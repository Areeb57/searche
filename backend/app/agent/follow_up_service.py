import logging
from typing import Any, Dict, List, Optional
from app.llm.base import LLMProvider
from app.database.repositories import ResearchRepository
from app.schemas.answer import FollowUpResponse

logger = logging.getLogger(__name__)

FOLLOW_UP_SYSTEM_PROMPT = """You are an advanced scientific research Q&A assistant.
Your task is to answer the user's follow-up question strictly using the stored research memory, claims, source provenance, and contradictions retrieved from their specific research session.

CRITICAL RULES:
1. Ground your answer EXCLUSIVELY in the provided session context.
2. If the user asks about source disagreements, consensus, or specific citations, reference the exact sources from the context (e.g. "According to Source A (example.com)... whereas Source B argued...").
3. If the stored research does not contain the answer, explicitly state that this information was not discovered in the collected sources, rather than inventing facts.
4. Keep the answer clear, authoritative, and direct.
"""


class FollowUpService:
    """Answers follow-up questions using vector similarity retrieval and stored session research memory."""

    def __init__(self, llm: LLMProvider, repository: ResearchRepository):
        self.llm = llm
        self.repository = repository

    async def answer_follow_up(self, session_id: str, question: str) -> FollowUpResponse:
        # Verify session exists
        session_obj = await self.repository.get_session(session_id)
        if not session_obj:
            raise ValueError(f"Research session '{session_id}' not found.")

        # 1. Compute question embedding
        question_embedding = await self.llm.generate_embedding(question)

        # 2. Vector search across session embeddings
        similar_items = await self.repository.search_similar_embeddings(
            session_id=session_id,
            query_embedding=question_embedding,
            top_k=8,
            threshold=0.35,
        )

        # 3. Retrieve session context: unified claims, contradictions, sources
        unified_claims = await self.repository.get_unified_claims_with_sources(session_id)
        contradictions = await self.repository.get_contradictions(session_id)
        sources = await self.repository.get_sources_by_session(session_id)

        source_map = {s.id: s.domain for s in sources}

        # Format context for LLM
        retrieved_texts = [f"• {item['text_content']}" for item in similar_items]

        claims_context = []
        for uc in unified_claims[:8]:
            src_domains = [source_map.get(s["source_id"], s["source_id"]) for s in uc.get("sources", [])]
            claims_context.append(f"- Claim: \"{uc['text']}\" [Sources: {', '.join(src_domains)}]")

        contradictions_context = []
        for cntr in contradictions:
            contradictions_context.append(f"- Conflict on {cntr.topic}: {cntr.explanation}")

        sources_summary = [
            {"source_id": s.id, "domain": s.domain, "url": s.url, "title": s.title}
            for s in sources[:8]
        ]

        prompt = (
            f"ORIGINAL RESEARCH QUERY: \"{session_obj.original_query}\"\n\n"
            f"FOLLOW-UP QUESTION: \"{question}\"\n\n"
            f"MOST RELEVANT VECTOR-RETRIEVED ITEMS:\n"
            f"{chr(10).join(retrieved_texts) if retrieved_texts else 'No direct vector matches.'}\n\n"
            f"STORED SESSION CLAIMS WITH SOURCES:\n"
            f"{chr(10).join(claims_context) if claims_context else 'None'}\n\n"
            f"IDENTIFIED CONTRADICTIONS IN RESEARCH:\n"
            f"{chr(10).join(contradictions_context) if contradictions_context else 'No contradictions recorded.'}\n\n"
            f"Answer the follow-up question based strictly on this research memory."
        )

        answer = await self.llm.generate_text(prompt, system_prompt=FOLLOW_UP_SYSTEM_PROMPT)

        return FollowUpResponse(
            session_id=session_id,
            question=question,
            answer=answer,
            cited_sources=sources_summary,
            relevant_claims=[item["text_content"] for item in similar_items[:5]],
            disagreements_or_nuances=contradictions[0].explanation if contradictions else None,
        )
