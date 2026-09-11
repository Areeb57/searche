import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import (
    ResearchSessionModel,
    ResearchQueryModel,
    SearchResultModel,
    SourceModel,
    DocumentModel,
    DocumentLinkModel,
    ClaimModel,
    EntityModel,
    RelationshipModel,
    UnifiedClaimModel,
    ClaimSourceModel,
    ContradictionModel,
    KnowledgeNodeModel,
    KnowledgeEdgeModel,
    KnowledgeEmbeddingModel,
    ResearchAnswerModel,
)

logger = logging.getLogger(__name__)


class ResearchRepository:
    """Encapsulates database operations for the multi-stage research agent."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Session Management ---
    async def create_session(self, session_id: str, query: str, config: Dict[str, Any]) -> ResearchSessionModel:
        model = ResearchSessionModel(
            id=session_id,
            original_query=query,
            status="created",
            configuration=config,
            stats={"sources_crawled": 0, "claims_extracted": 0, "contradictions_found": 0},
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_session(self, session_id: str) -> Optional[ResearchSessionModel]:
        stmt = select(ResearchSessionModel).where(ResearchSessionModel.id == session_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        session_id: str,
        status: str,
        error_message: Optional[str] = None,
        final_answer: Optional[str] = None,
        stats_update: Optional[Dict[str, Any]] = None,
    ) -> None:
        db_session = await self.get_session(session_id)
        if not db_session:
            return
        db_session.status = status
        if error_message:
            db_session.error_message = error_message
        if final_answer:
            db_session.final_answer = final_answer
        if stats_update:
            current_stats = dict(db_session.stats or {})
            current_stats.update(stats_update)
            db_session.stats = current_stats
        await self.session.commit()

    # --- Queries & Search Results ---
    async def add_queries(self, session_id: str, queries: List[str]) -> None:
        for rank, q in enumerate(queries, start=1):
            model = ResearchQueryModel(session_id=session_id, query_text=q, rank=rank)
            self.session.add(model)
        await self.session.commit()

    async def add_search_results(self, session_id: str, results: List[Dict[str, Any]]) -> None:
        for r in results:
            model = SearchResultModel(
                session_id=session_id,
                query_text=r.get("query", ""),
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
                domain=r.get("domain", ""),
                rank=r.get("rank", 1),
                relevance_score=r.get("relevance_score", 0.0),
            )
            self.session.add(model)
        await self.session.commit()

    # --- Sources & Documents ---
    async def add_source(
        self,
        source_id: str,
        session_id: str,
        url: str,
        domain: str,
        title: Optional[str] = None,
        relevance_score: float = 0.0,
        depth: int = 0,
        parent_source_id: Optional[str] = None,
    ) -> SourceModel:
        model = SourceModel(
            id=source_id,
            session_id=session_id,
            url=url,
            domain=domain,
            title=title,
            relevance_score=relevance_score,
            depth=depth,
            parent_source_id=parent_source_id,
        )
        self.session.add(model)
        await self.session.commit()
        return model

    async def get_sources_by_session(self, session_id: str) -> List[SourceModel]:
        stmt = select(SourceModel).where(SourceModel.session_id == session_id).order_by(desc(SourceModel.relevance_score))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_document(
        self,
        doc_id: str,
        source_id: str,
        session_id: str,
        url: str,
        cleaned_text: str,
        content_hash: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        published_date: Optional[str] = None,
        raw_html: Optional[str] = None,
    ) -> DocumentModel:
        model = DocumentModel(
            id=doc_id,
            source_id=source_id,
            session_id=session_id,
            url=url,
            cleaned_text=cleaned_text,
            content_hash=content_hash,
            title=title,
            author=author,
            published_date=published_date,
            raw_html=raw_html,
        )
        self.session.add(model)
        await self.session.commit()
        return model

    async def get_documents_by_session(self, session_id: str) -> List[DocumentModel]:
        stmt = select(DocumentModel).where(DocumentModel.session_id == session_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_document_links(self, doc_id: str, session_id: str, links: List[Dict[str, Any]]) -> None:
        for link in links:
            model = DocumentLinkModel(
                document_id=doc_id,
                session_id=session_id,
                url=link["url"],
                text=link.get("text"),
                relevance_score=link.get("relevance_score", 0.0),
                is_queued=link.get("is_queued", False),
            )
            self.session.add(model)
        await self.session.commit()

    # --- Structured Knowledge: Claims, Entities, Relationships ---
    async def add_claims(self, claims: List[Dict[str, Any]]) -> None:
        for c in claims:
            model = ClaimModel(
                id=c["id"],
                document_id=c["document_id"],
                source_id=c["source_id"],
                session_id=c["session_id"],
                claim_text=c["text"],
                importance=c.get("importance", 0.8),
            )
            self.session.add(model)
        await self.session.commit()

    async def get_claims_by_session(self, session_id: str) -> List[ClaimModel]:
        stmt = select(ClaimModel).where(ClaimModel.session_id == session_id).order_by(desc(ClaimModel.importance))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_entities(self, entities: List[Dict[str, Any]]) -> None:
        for e in entities:
            model = EntityModel(
                session_id=e["session_id"],
                document_id=e.get("document_id"),
                source_id=e.get("source_id"),
                name=e["name"],
                entity_type=e["type"],
                description=e.get("description"),
            )
            self.session.add(model)
        await self.session.commit()

    async def add_relationships(self, relationships: List[Dict[str, Any]]) -> None:
        for r in relationships:
            model = RelationshipModel(
                session_id=r["session_id"],
                source_entity=r["source_entity"],
                target_entity=r["target_entity"],
                relation_type=r["relation_type"],
                description=r.get("description"),
                document_id=r.get("document_id"),
            )
            self.session.add(model)
        await self.session.commit()

    # --- Unified Knowledge & Provenance ---
    async def add_unified_claim(
        self,
        unified_claim_id: str,
        session_id: str,
        text: str,
        confidence: float,
        sources: List[Dict[str, Any]],
        original_claim_ids: List[str],
    ) -> None:
        u_model = UnifiedClaimModel(
            id=unified_claim_id,
            session_id=session_id,
            claim_text=text,
            confidence=confidence,
        )
        self.session.add(u_model)
        await self.session.flush()

        for s in sources:
            source_link = ClaimSourceModel(
                unified_claim_id=unified_claim_id,
                claim_id=s.get("claim_id", original_claim_ids[0] if original_claim_ids else "clm_unknown"),
                source_id=s["source_id"],
                document_id=s["document_id"],
                support_type=s.get("support", "direct"),
            )
            self.session.add(source_link)
        await self.session.commit()

    async def get_unified_claims_with_sources(self, session_id: str) -> List[Dict[str, Any]]:
        stmt = select(UnifiedClaimModel).where(UnifiedClaimModel.session_id == session_id)
        result = await self.session.execute(stmt)
        u_claims = result.scalars().all()

        output = []
        for uc in u_claims:
            stmt_sources = select(ClaimSourceModel).where(ClaimSourceModel.unified_claim_id == uc.id)
            res_sources = await self.session.execute(stmt_sources)
            src_links = res_sources.scalars().all()

            sources_data = [
                {
                    "source_id": sl.source_id,
                    "document_id": sl.document_id,
                    "claim_id": sl.claim_id,
                    "support": sl.support_type,
                }
                for sl in src_links
            ]
            output.append({
                "id": uc.id,
                "text": uc.claim_text,
                "confidence": uc.confidence,
                "sources": sources_data,
            })
        return output

    # --- Contradictions ---
    async def add_contradiction(
        self,
        contradiction_id: str,
        session_id: str,
        topic: str,
        claims_json: List[Dict[str, Any]],
        relationship: str,
        explanation: str,
    ) -> None:
        model = ContradictionModel(
            id=contradiction_id,
            session_id=session_id,
            topic=topic,
            claims_json=claims_json,
            relationship=relationship,
            explanation=explanation,
        )
        self.session.add(model)
        await self.session.commit()

    async def get_contradictions(self, session_id: str) -> List[ContradictionModel]:
        stmt = select(ContradictionModel).where(ContradictionModel.session_id == session_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Knowledge Graph Nodes and Edges ---
    async def save_graph(
        self,
        session_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> None:
        # Delete old graph for this session if re-generating
        await self.session.execute(delete(KnowledgeEdgeModel).where(KnowledgeEdgeModel.session_id == session_id))
        await self.session.execute(delete(KnowledgeNodeModel).where(KnowledgeNodeModel.session_id == session_id))

        for n in nodes:
            node_model = KnowledgeNodeModel(
                id=n["id"],
                session_id=session_id,
                node_type=n["type"],
                label=n["label"],
                data_json=n.get("data", {}),
                pos_x=n.get("position", {}).get("x", 0.0),
                pos_y=n.get("position", {}).get("y", 0.0),
            )
            self.session.add(node_model)

        for e in edges:
            edge_model = KnowledgeEdgeModel(
                id=e["id"],
                session_id=session_id,
                source_node_id=e["source"],
                target_node_id=e["target"],
                relationship=e.get("relationship", "relates_to"),
                label=e.get("label"),
                data_json=e.get("data", {}),
            )
            self.session.add(edge_model)
        await self.session.commit()

    async def get_graph(self, session_id: str) -> Tuple[List[KnowledgeNodeModel], List[KnowledgeEdgeModel]]:
        stmt_nodes = select(KnowledgeNodeModel).where(KnowledgeNodeModel.session_id == session_id)
        stmt_edges = select(KnowledgeEdgeModel).where(KnowledgeEdgeModel.session_id == session_id)
        nodes_res = await self.session.execute(stmt_nodes)
        edges_res = await self.session.execute(stmt_edges)
        return list(nodes_res.scalars().all()), list(edges_res.scalars().all())

    # --- Vector Embeddings & Similarity Search ---
    async def store_embedding(
        self,
        session_id: str,
        item_type: str,
        item_id: str,
        text_content: str,
        embedding: List[float],
    ) -> None:
        model = KnowledgeEmbeddingModel(
            session_id=session_id,
            item_type=item_type,
            item_id=item_id,
            text_content=text_content,
            embedding=embedding,
        )
        self.session.add(model)
        await self.session.commit()

    async def search_similar_embeddings(
        self,
        session_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search knowledge embeddings scoped strictly to the current session."""
        stmt = select(KnowledgeEmbeddingModel).where(KnowledgeEmbeddingModel.session_id == session_id)
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        if not records:
            return []

        # Cosine similarity calculation (pure Python / numpy compatible)
        import numpy as np
        q_vec = np.array(query_embedding, dtype=np.float32)
        norm_q = np.linalg.norm(q_vec)
        if norm_q == 0:
            return []

        scored = []
        for rec in records:
            emb = rec.embedding
            if not emb:
                continue
            r_vec = np.array(emb, dtype=np.float32)
            norm_r = np.linalg.norm(r_vec)
            if norm_r == 0:
                continue
            sim = float(np.dot(q_vec, r_vec) / (norm_q * norm_r))
            if sim >= threshold:
                scored.append({
                    "item_type": rec.item_type,
                    "item_id": rec.item_id,
                    "text_content": rec.text_content,
                    "similarity": sim,
                })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    # --- Research Answers ---
    async def save_answer(
        self,
        session_id: str,
        answer_text: str,
        key_findings: List[str],
        sources_summary: List[Dict[str, Any]],
        contradictions_summary: Optional[str] = None,
    ) -> ResearchAnswerModel:
        model = ResearchAnswerModel(
            session_id=session_id,
            answer_text=answer_text,
            key_findings=key_findings,
            sources_summary=sources_summary,
            contradictions_summary=contradictions_summary,
        )
        self.session.add(model)
        await self.session.commit()
        return model
