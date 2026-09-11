import pytest
from app.knowledge.deduplication import ClaimDeduplicator
from app.knowledge.provenance import ProvenanceTracker
from app.schemas.knowledge import Claim


@pytest.mark.asyncio
async def test_claim_deduplication(mock_llm):
    provenance = ProvenanceTracker()
    provenance.register_source("src_1", "https://source1.com", "source1.com")
    provenance.register_source("src_2", "https://source2.com", "source2.com")
    provenance.register_document("doc_1", "src_1", "https://source1.com/art1")
    provenance.register_document("doc_2", "src_2", "https://source2.com/art2")

    claims = [
        Claim(
            id="clm_1",
            text="Adequate dietary protein is essential for muscle hypertrophy and repair.",
            importance=0.9,
            source_document_id="doc_1",
            source_id="src_1",
        ),
        Claim(
            id="clm_2",
            text="Adequate dietary protein is essential for muscle hypertrophy and repair.",
            importance=0.85,
            source_document_id="doc_2",
            source_id="src_2",
        ),
    ]

    dedup = ClaimDeduplicator(llm=mock_llm, provenance=provenance, similarity_threshold=0.80)
    unified = await dedup.deduplicate_claims(claims)

    assert len(unified) == 1
    u = unified[0]
    assert len(u.sources) == 2
    source_ids = {s.source_id for s in u.sources}
    assert "src_1" in source_ids
    assert "src_2" in source_ids
