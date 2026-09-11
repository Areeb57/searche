import math
from typing import Any, Dict, List, Optional
from app.schemas.knowledge import (
    KnowledgeNode,
    KnowledgeEdge,
    KnowledgeGraphResponse,
    UnifiedClaim,
    Contradiction,
    Entity,
    Relationship,
)
from app.schemas.source import Source


class KnowledgeGraphBuilder:
    """Builds a generic, extensible Knowledge Graph formatted for React Flow rendering."""

    @classmethod
    def build_graph(
        cls,
        topic: str,
        sources: List[Source],
        unified_claims: List[UnifiedClaim],
        contradictions: List[Contradiction],
        entities: List[Entity],
        relationships: List[Relationship],
        session_id: str = "sess",
    ) -> KnowledgeGraphResponse:
        nodes: List[KnowledgeNode] = []
        edges: List[KnowledgeEdge] = []
        seen_node_ids = set()

        prefix = f"{session_id}_" if session_id else ""

        # 1. Central Topic Node (Column 0 / Center)
        topic_node_id = f"{prefix}node_topic_root"
        nodes.append(
            KnowledgeNode(
                id=topic_node_id,
                type="topic",
                label=topic,
                data={"title": topic, "category": "Root Topic"},
                position={"x": 500.0, "y": 50.0},
            )
        )
        seen_node_ids.add(topic_node_id)

        # 2. Source Nodes (Left column, x = 100)
        source_y = 150.0
        for i, src in enumerate(sources[:8]):
            src_node_id = f"{prefix}node_src_{src.id}"
            nodes.append(
                KnowledgeNode(
                    id=src_node_id,
                    type="source",
                    label=src.domain or "Source",
                    data={
                        "url": src.url,
                        "domain": src.domain,
                        "title": src.title,
                        "relevance": src.relevance_score,
                    },
                    position={"x": 100.0, "y": source_y + (i * 120.0)},
                )
            )
            seen_node_ids.add(src_node_id)

        # 3. Unified Claim Nodes (Center-Right column, x = 500)
        claim_y = 180.0
        for i, u_claim in enumerate(unified_claims[:10]):
            claim_node_id = f"{prefix}node_uclm_{u_claim.id}"
            nodes.append(
                KnowledgeNode(
                    id=claim_node_id,
                    type="claim",
                    label=u_claim.text[:60] + ("..." if len(u_claim.text) > 60 else ""),
                    data={
                        "full_text": u_claim.text,
                        "confidence": u_claim.confidence,
                        "sources_count": len(u_claim.sources),
                    },
                    position={"x": 500.0, "y": claim_y + (i * 140.0)},
                )
            )
            seen_node_ids.add(claim_node_id)

            # Connect Root Topic -> Claim
            edges.append(
                KnowledgeEdge(
                    id=f"{prefix}edge_topic_{u_claim.id}",
                    source=topic_node_id,
                    target=claim_node_id,
                    relationship="asserts",
                    label="asserts",
                )
            )

            # Connect Sources -> Claim (Provenance edges)
            for prov in u_claim.sources:
                src_node_id = f"{prefix}node_src_{prov.source_id}"
                if src_node_id in seen_node_ids:
                    edges.append(
                        KnowledgeEdge(
                            id=f"{prefix}edge_{prov.source_id}_{u_claim.id}",
                            source=src_node_id,
                            target=claim_node_id,
                            relationship="cites",
                            label="cites",
                            data={"support": prov.support},
                        )
                    )

        # 4. Entity Nodes (Far-right column, x = 900)
        entity_y = 150.0
        for i, ent in enumerate(entities[:12]):
            ent_node_id = f"{prefix}node_ent_{i+1}"
            nodes.append(
                KnowledgeNode(
                    id=ent_node_id,
                    type="entity",
                    label=ent.name,
                    data={
                        "entity_type": ent.type,
                        "description": ent.description,
                    },
                    position={"x": 900.0, "y": entity_y + (i * 100.0)},
                )
            )
            seen_node_ids.add(ent_node_id)

        # 5. Contradiction Nodes (Bottom area, x = 500)
        cntr_y = claim_y + (len(unified_claims[:10]) * 140.0) + 50.0
        for i, cntr in enumerate(contradictions[:5]):
            cntr_node_id = f"{prefix}node_cntr_{cntr.id}"
            nodes.append(
                KnowledgeNode(
                    id=cntr_node_id,
                    type="contradiction",
                    label=f"Conflict: {cntr.topic}",
                    data={
                        "explanation": cntr.explanation,
                        "relationship": cntr.relationship,
                        "claims": cntr.claims,
                    },
                    position={"x": 500.0, "y": cntr_y + (i * 130.0)},
                )
            )
            seen_node_ids.add(cntr_node_id)

            # Connect contradictory claims to contradiction node
            for claim_item in cntr.claims:
                claim_id = claim_item.get("claim_id")
                edges.append(
                    KnowledgeEdge(
                        id=f"{prefix}edge_cntr_{cntr.id}_{claim_id}",
                        source=topic_node_id,
                        target=cntr_node_id,
                        relationship="contradicts",
                        label="contradicts",
                    )
                )

        return KnowledgeGraphResponse(nodes=nodes, edges=edges)
