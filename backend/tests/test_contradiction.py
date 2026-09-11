import pytest
from app.knowledge.contradiction import ContradictionDetector
from app.schemas.knowledge import Claim


class MockContradictionLLM:
    """Specialized mock LLM that flags opposing assertions."""
    async def generate_structured(self, prompt, schema, system_prompt=None):
        return schema(
            has_conflict=True,
            relationship="contradicts",
            topic="Daily Caloric Surplus Targets",
            explanation="Source A advocates 300 kcal/day whereas Source B recommends over 1000 kcal/day.",
        )


@pytest.mark.asyncio
async def test_contradiction_detection():
    llm = MockContradictionLLM()
    detector = ContradictionDetector(llm=llm)

    claims = [
        Claim(
            id="clm_1",
            text="Maintain a modest surplus of 300 calories daily to prevent excess adiposity.",
            importance=0.9,
            source_document_id="doc_1",
            source_id="src_1",
        ),
        Claim(
            id="clm_2",
            text="Consume an aggressive surplus of 1000+ calories daily for rapid bulk gains.",
            importance=0.8,
            source_document_id="doc_2",
            source_id="src_2",
        ),
    ]

    contradictions = await detector.detect_contradictions(claims)
    assert len(contradictions) == 1
    cntr = contradictions[0]
    assert cntr.relationship == "contradicts"
    assert "Daily Caloric Surplus Targets" in cntr.topic
    assert len(cntr.claims) == 2
