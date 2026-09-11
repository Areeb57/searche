import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.llm.base import LLMProvider
from app.schemas.source import Source
from app.schemas.knowledge import UnifiedClaim, Contradiction
from app.schemas.answer import ResearchAnswer
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)

ANSWER_SYSTEM_PROMPT = """You are an expert research synthesizer.
Your task is to write a concise, authoritative, directly relevant answer to the user's research question, grounded strictly in the unified research findings provided.

GUIDELINES:
1. Be concise, direct, and easy to understand.
2. Directly answer the core question in the opening paragraph.
3. Cite sources using [Domain] notation where appropriate (e.g. [healthline.com], [nih.gov]).
4. Explicitly acknowledge notable contradictions or qualifying conditions between sources if present.
5. Do NOT provide lengthy repetitive summaries of individual websites. Focus on consolidated facts and actionable takeaways.
6. Return structured output with the synthesized answer and key findings.
"""


class SynthesizedAnswerSchema(BaseModel):
    answer: str = Field(..., description="The direct, concise, source-aware research answer in Markdown format")
    key_findings: List[str] = Field(default_factory=list, description="Top 3-5 concise bullet-point takeaways")


class AnswerGenerator:
    """Produces a concise, source-aware answer to the research query grounded in unified knowledge."""

    def __init__(self, llm: LLMProvider, repository: ResearchRepository):
        self.llm = llm
        self.repository = repository

    async def generate_answer(
        self,
        session_id: str,
        original_query: str,
        unified_claims: List[UnifiedClaim],
        contradictions: List[Contradiction],
        sources: List[Source],
    ) -> ResearchAnswer:
        # Prepare context
        claims_text = "\n".join([f"- {uc.text} (Supported by {len(uc.sources)} sources)" for uc in unified_claims[:12]])

        contradictions_text = "None noted."
        if contradictions:
            contradictions_text = "\n".join(
                [f"- Disagreement on {c.topic}: {c.explanation}" for c in contradictions[:4]]
            )

        sources_summary = [
            {"source_id": s.id, "domain": s.domain, "url": s.url, "title": s.title}
            for s in sources[:8]
        ]
        sources_text = ", ".join([s["domain"] for s in sources_summary])

        prompt = (
            f"ORIGINAL QUERY: \"{original_query}\"\n\n"
            f"AVAILABLE SOURCES: {sources_text}\n\n"
            f"CONSOLIDATED CLAIMS:\n{claims_text}\n\n"
            f"IDENTIFIED CONTRADICTIONS / NUANCES:\n{contradictions_text}\n\n"
            f"Synthesize an authoritative, concise, source-aware answer."
        )

        try:
            result: SynthesizedAnswerSchema = await self.llm.generate_structured(
                prompt=prompt,
                schema=SynthesizedAnswerSchema,
                system_prompt=ANSWER_SYSTEM_PROMPT,
            )
            answer_text = result.answer
            key_findings = result.key_findings
        except Exception as e:
            logger.warning(f"Structured answer generation failed ({e}), falling back to text generation.")
            answer_text = await self.llm.generate_text(prompt, system_prompt=ANSWER_SYSTEM_PROMPT)
            key_findings = [uc.text for uc in unified_claims[:4]]

        contradictions_summary = contradictions[0].explanation if contradictions else None

        # Persist answer in DB
        await self.repository.save_answer(
            session_id=session_id,
            answer_text=answer_text,
            key_findings=key_findings,
            sources_summary=sources_summary,
            contradictions_summary=contradictions_summary,
        )

        # Store embedding of the answer for follow-up questions
        try:
            emb = await self.llm.generate_embedding(answer_text)
            await self.repository.store_embedding(
                session_id=session_id,
                item_type="answer",
                item_id="final_answer",
                text_content=answer_text,
                embedding=emb,
            )
        except Exception as e:
            logger.debug(f"Could not store answer embedding: {e}")

        return ResearchAnswer(
            session_id=session_id,
            answer=answer_text,
            key_findings=key_findings,
            sources_used=sources_summary,
            contradictions_summary=contradictions_summary,
        )
