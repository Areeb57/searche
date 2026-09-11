import logging
import uuid
from typing import Any, Dict, Optional
from app.llm.base import LLMProvider
from app.schemas.knowledge import ExtractedArticleKnowledge, Claim

logger = logging.getLogger(__name__)

ARTICLE_ANALYSIS_SYSTEM_PROMPT = """You are an advanced scientific research intelligence analyst.
Your task is to analyze the provided article content and extract structured knowledge.

CRITICAL INSTRUCTIONS:
1. Do NOT just summarize the text. Extract distinct, actionable, high-quality knowledge objects.
2. Extract major CLAIMS: Each claim must be a distinct factual assertion made by the article. Assign an importance score (0.0 to 1.0).
3. Extract verified FACTS: Exact verifiable data points.
4. Extract ENTITIES: Key concepts, methodologies, tools, nutrients, foods, or persons mentioned. Categorize them accurately.
5. Extract RECOMMENDATIONS: Prescriptive advice or protocols suggested.
6. Extract STATISTICS: Quantitative figures, metrics, percentages with contextual framing.
7. Extract LIMITATIONS: Caveats, risks, side effects, or contraindications noted.
8. Extract RELATIONSHIPS: Directional semantic interactions between entities (e.g. Entity A causes/supports/inhibits Entity B).
9. Respond strictly in valid JSON matching the requested schema.
"""


class ArticleKnowledgeExtractor:
    """Invokes LLM to extract structured multi-dimensional knowledge from cleaned article text."""

    @classmethod
    async def extract_knowledge(
        cls,
        llm: LLMProvider,
        text: str,
        title: Optional[str],
        url: str,
        doc_id: str,
        source_id: str,
    ) -> ExtractedArticleKnowledge:
        truncated_text = text[:12000]  # Safe token window for article extraction

        prompt = (
            f"ARTICLE METADATA:\n"
            f"Title: {title or 'Untitled'}\n"
            f"Source URL: {url}\n\n"
            f"ARTICLE CONTENT:\n"
            f"{truncated_text}\n\n"
            f"Extract structured research knowledge from this article according to the schema."
        )

        try:
            extracted = await llm.generate_structured(
                prompt=prompt,
                schema=ExtractedArticleKnowledge,
                system_prompt=ARTICLE_ANALYSIS_SYSTEM_PROMPT,
            )

            # Ensure all claims have consistent IDs and trace back to source & doc
            for i, claim in enumerate(extracted.claims):
                if not claim.id or claim.id == "string":
                    claim.id = f"clm_{doc_id}_{i+1}_{uuid.uuid4().hex[:4]}"
                claim.source_document_id = doc_id
                claim.source_id = source_id

            return extracted
        except Exception as e:
            logger.error(f"Error extracting structured knowledge from {url}: {e}")
            # Fallback minimal extraction
            return ExtractedArticleKnowledge(
                topic=title or "General Topic",
                summary=text[:200] if text else "No content available.",
                claims=[
                    Claim(
                        id=f"clm_{doc_id}_fallback",
                        text=f"Information extracted from {title or url}",
                        importance=0.7,
                        source_document_id=doc_id,
                        source_id=source_id,
                    )
                ],
            )
