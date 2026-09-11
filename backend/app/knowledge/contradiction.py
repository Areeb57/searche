import json
import logging
import uuid
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.llm.base import LLMProvider
from app.schemas.knowledge import Claim, Contradiction

logger = logging.getLogger(__name__)


class ContradictionLLMResult(BaseModel):
    has_conflict: bool
    relationship: str = Field(default="contradiction", description="contradiction | qualifies | different_context")
    topic: str
    explanation: str


CONTRADICTION_PROMPT = """Analyze these two claims from different research sources regarding the same general topic.
Determine if they contradict each other, qualify each other (e.g. valid under different conditions), or merely apply to different contexts.

Claim A (Source {source_a}): "{claim_a}"
Claim B (Source {source_b}): "{claim_b}"

Answer in JSON according to the schema."""


class ContradictionDetector:
    """Detects opposing, contradictory, or qualifying assertions across distinct sources."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def detect_contradictions(self, claims: List[Claim]) -> List[Contradiction]:
        """Pairwise evaluation of claims originating from different sources."""
        contradictions: List[Contradiction] = []
        if len(claims) < 2:
            return contradictions

        # Compare claims across different sources
        # Limit pairs checked to avoid combinatorial explosion
        evaluated_pairs = 0
        max_evaluations = 25

        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                c1 = claims[i]
                c2 = claims[j]

                # Only compare claims from different sources
                if c1.source_id and c2.source_id and c1.source_id == c2.source_id:
                    continue

                evaluated_pairs += 1
                if evaluated_pairs > max_evaluations:
                    break

                prompt = CONTRADICTION_PROMPT.format(
                    source_a=c1.source_id or "Source A",
                    claim_a=c1.text,
                    source_b=c2.source_id or "Source B",
                    claim_b=c2.text,
                )

                try:
                    res: ContradictionLLMResult = await self.llm.generate_structured(
                        prompt=prompt,
                        schema=ContradictionLLMResult,
                    )

                    if res.has_conflict:
                        cntr_id = f"cntr_{uuid.uuid4().hex[:8]}"
                        contradictions.append(
                            Contradiction(
                                id=cntr_id,
                                topic=res.topic or "Topic Discrepancy",
                                claims=[
                                    {"claim_id": c1.id, "text": c1.text, "source_id": c1.source_id},
                                    {"claim_id": c2.id, "text": c2.text, "source_id": c2.source_id},
                                ],
                                relationship=res.relationship,
                                explanation=res.explanation,
                            )
                        )
                except Exception as e:
                    logger.debug(f"Contradiction detection check error between claims {c1.id} and {c2.id}: {e}")

            if evaluated_pairs > max_evaluations:
                break

        return contradictions
