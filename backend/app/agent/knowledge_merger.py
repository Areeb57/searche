import logging
from typing import Any, Dict, List, Tuple
from app.llm.base import LLMProvider
from app.schemas.source import Source
from app.schemas.knowledge import (
    Claim,
    Entity,
    Relationship,
    UnifiedClaim,
    Contradiction,
    KnowledgeNode,
    KnowledgeEdge,
    KnowledgeGraphResponse,
)
from app.knowledge.deduplication import ClaimDeduplicator
from app.knowledge.contradiction import ContradictionDetector
from app.knowledge.provenance import ProvenanceTracker
from app.knowledge.graph import KnowledgeGraphBuilder
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class KnowledgeMerger:
    """Merges disparate source-level knowledge into unified claims, detects contradictions, and compiles graph."""

    def __init__(
        self,
        llm: LLMProvider,
        repository: ResearchRepository,
        provenance: ProvenanceTracker,
    ):
        self.llm = llm
        self.repository = repository
        self.provenance = provenance
        self.claim_deduplicator = ClaimDeduplicator(llm=llm, provenance=provenance)
        self.contradiction_detector = ContradictionDetector(llm=llm)

    async def merge_knowledge(
        self,
        session_id: str,
        topic: str,
        sources: List[Source],
        raw_claims: List[Claim],
        raw_entities: List[Entity],
        raw_relationships: List[Relationship],
    ) -> Tuple[List[UnifiedClaim], List[Contradiction], KnowledgeGraphResponse]:
        """Perform semantic claim deduplication, contradiction detection, and knowledge graph construction."""
        logger.info(f"Merging knowledge across {len(raw_claims)} raw claims from {len(sources)} sources...")

        # 1. Semantic Claim Deduplication & Provenance Preservation
        unified_claims = await self.claim_deduplicator.deduplicate_claims(raw_claims)
        logger.info(f"Synthesized {len(unified_claims)} unified claims.")

        # Persist unified claims with provenance junction records
        for uc in unified_claims:
            sources_dicts = [
                {
                    "source_id": s.source_id,
                    "document_id": s.document_id,
                    "support": s.support,
                }
                for s in uc.sources
            ]
            await self.repository.add_unified_claim(
                unified_claim_id=uc.id,
                session_id=session_id,
                text=uc.text,
                confidence=uc.confidence,
                sources=sources_dicts,
                original_claim_ids=uc.original_claim_ids,
            )

            # Store dense embedding for unified claim
            try:
                emb = await self.llm.generate_embedding(uc.text)
                await self.repository.store_embedding(
                    session_id=session_id,
                    item_type="unified_claim",
                    item_id=uc.id,
                    text_content=uc.text,
                    embedding=emb,
                )
            except Exception as e:
                logger.debug(f"Could not store embedding for unified claim {uc.id}: {e}")

        # 2. Contradiction Detection
        contradictions = await self.contradiction_detector.detect_contradictions(raw_claims)
        logger.info(f"Identified {len(contradictions)} cross-source contradictions/nuances.")

        # Persist contradictions
        for cntr in contradictions:
            await self.repository.add_contradiction(
                contradiction_id=cntr.id,
                session_id=session_id,
                topic=cntr.topic,
                claims_json=cntr.claims,
                relationship=cntr.relationship,
                explanation=cntr.explanation,
            )
            # Store embedding for contradiction
            try:
                c_text = f"Contradiction on {cntr.topic}: {cntr.explanation}"
                emb = await self.llm.generate_embedding(c_text)
                await self.repository.store_embedding(
                    session_id=session_id,
                    item_type="contradiction",
                    item_id=cntr.id,
                    text_content=c_text,
                    embedding=emb,
                )
            except Exception as e:
                logger.debug(f"Could not store embedding for contradiction {cntr.id}: {e}")

        # 3. Build Knowledge Graph (React Flow format)
        graph_response = KnowledgeGraphBuilder.build_graph(
            topic=topic,
            sources=sources,
            unified_claims=unified_claims,
            contradictions=contradictions,
            entities=raw_entities,
            relationships=raw_relationships,
            session_id=session_id,
        )

        # Persist graph nodes & edges
        nodes_data = [n.model_dump() for n in graph_response.nodes]
        edges_data = [e.model_dump() for e in graph_response.edges]
        await self.repository.save_graph(session_id=session_id, nodes=nodes_data, edges=edges_data)

        return unified_claims, contradictions, graph_response
