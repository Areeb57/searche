import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional
from app.llm.base import LLMProvider
from app.schemas.source import Document
from app.schemas.knowledge import ExtractedArticleKnowledge, Claim, Entity, Relationship
from app.knowledge.extraction import ArticleKnowledgeExtractor
from app.knowledge.provenance import ProvenanceTracker
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class ArticleAnalyzer:
    """Analyzes crawled article documents and extracts fine-grained structured knowledge."""

    def __init__(
        self,
        llm: LLMProvider,
        repository: ResearchRepository,
        provenance: ProvenanceTracker,
    ):
        self.llm = llm
        self.repository = repository
        self.provenance = provenance

    async def analyze_document(
        self,
        session_id: str,
        doc: Document,
    ) -> ExtractedArticleKnowledge:
        """Extract multi-dimensional knowledge for a single document."""
        knowledge = await ArticleKnowledgeExtractor.extract_knowledge(
            llm=self.llm,
            text=doc.cleaned_text,
            title=doc.title,
            url=doc.url,
            doc_id=doc.id,
            source_id=doc.source_id,
        )

        # Register in Provenance Tracker
        self.provenance.register_document(doc_id=doc.id, source_id=doc.source_id, url=doc.url, title=doc.title)

        # Register and persist claims
        claims_to_persist = []
        for c in knowledge.claims:
            self.provenance.register_claim(
                claim_id=c.id,
                text=c.text,
                doc_id=doc.id,
                source_id=doc.source_id,
                importance=c.importance,
            )
            claims_to_persist.append({
                "id": c.id,
                "document_id": doc.id,
                "source_id": doc.source_id,
                "session_id": session_id,
                "text": c.text,
                "importance": c.importance,
            })

        if claims_to_persist:
            await self.repository.add_claims(claims_to_persist)

        # Persist entities
        entities_to_persist = [
            {
                "session_id": session_id,
                "document_id": doc.id,
                "source_id": doc.source_id,
                "name": e.name,
                "type": e.type,
                "description": e.description,
            }
            for e in knowledge.entities
        ]
        if entities_to_persist:
            await self.repository.add_entities(entities_to_persist)

        # Persist relationships
        relationships_to_persist = [
            {
                "session_id": session_id,
                "source_entity": r.source_entity,
                "target_entity": r.target_entity,
                "relation_type": r.relation_type,
                "description": r.description,
                "document_id": doc.id,
            }
            for r in knowledge.relationships
        ]
        if relationships_to_persist:
            await self.repository.add_relationships(relationships_to_persist)

        return knowledge

    async def analyze_all_documents(
        self,
        session_id: str,
        documents: List[Document],
        progress_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None,
    ) -> List[ExtractedArticleKnowledge]:
        """Analyze all extracted documents sequentially or with controlled concurrency."""
        results: List[ExtractedArticleKnowledge] = []
        for i, doc in enumerate(documents, start=1):
            if progress_callback:
                await progress_callback({
                    "event": "analyzing_article",
                    "doc_id": doc.id,
                    "title": doc.title,
                    "completed": i,
                    "total": len(documents),
                })

            extracted = await self.analyze_document(session_id, doc)
            results.append(extracted)

        return results
