import pytest
from app.knowledge.graph import KnowledgeGraphBuilder
from app.schemas.source import Source
from app.schemas.knowledge import UnifiedClaim, ClaimProvenance, Contradiction, Entity, Relationship


def test_knowledge_graph_builder():
    sources = [
        Source(
            id="src_1",
            session_id="rs_test",
            url="https://healthline.example.com",
            domain="healthline.example.com",
            title="Foods to Gain Weight",
            relevance_score=0.9,
            depth=0,
        )
    ]
    unified_claims = [
        UnifiedClaim(
            id="uclm_1",
            text="Protein intake of 1.6-2.2 g/kg maximizes hypertrophic stimulus.",
            confidence=0.95,
            sources=[ClaimProvenance(source_id="src_1", document_id="doc_1", support="direct")],
        )
    ]
    contradictions = [
        Contradiction(
            id="cntr_1",
            topic="Surplus size",
            claims=[],
            relationship="contradiction",
            explanation="Different recommended surpluses",
        )
    ]
    entities = [Entity(name="Protein", type="nutrient", description="Essential macronutrient")]
    relationships = [Relationship(source_entity="Protein", target_entity="Muscle", relation_type="builds")]

    graph = KnowledgeGraphBuilder.build_graph(
        topic="Weight Gain",
        sources=sources,
        unified_claims=unified_claims,
        contradictions=contradictions,
        entities=entities,
        relationships=relationships,
    )

    assert len(graph.nodes) >= 4  # root, source, claim, contradiction, entity
    assert len(graph.edges) >= 2

    # Verify React Flow compatibility
    for node in graph.nodes:
        assert "x" in node.position
        assert "y" in node.position
        assert node.id
        assert node.type in ["topic", "source", "claim", "entity", "contradiction", "concept", "fact"]

    for edge in graph.edges:
        assert edge.id
        assert edge.source
        assert edge.target
