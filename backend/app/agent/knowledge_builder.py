import logging
from collections import defaultdict
from typing import Dict, List
from app.schemas.source import Source, Document
from app.schemas.knowledge import ExtractedArticleKnowledge, SourceKnowledge
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class KnowledgeBuilder:
    """Aggregates document-level extractions into independent source-level structured knowledge representations."""

    def __init__(self, repository: ResearchRepository):
        self.repository = repository

    async def build_source_knowledge(
        self,
        session_id: str,
        sources: List[Source],
        documents: List[Document],
        extractions: List[ExtractedArticleKnowledge],
    ) -> List[SourceKnowledge]:
        # Group extractions by source_id
        doc_to_source: Dict[str, str] = {doc.id: doc.source_id for doc in documents}
        source_map: Dict[str, Source] = {src.id: src for src in sources}

        source_groups: Dict[str, List[ExtractedArticleKnowledge]] = defaultdict(list)
        for doc, ext in zip(documents, extractions):
            s_id = doc_to_source.get(doc.id)
            if s_id:
                source_groups[s_id].append(ext)

        source_knowledge_list: List[SourceKnowledge] = []

        for s_id, ext_list in source_groups.items():
            src_obj = source_map.get(s_id)
            source_url = src_obj.url if src_obj else "unknown"

            combined_topic = ext_list[0].topic if ext_list else "Research Topic"
            combined_claims = []
            combined_facts = []
            combined_entities = []
            combined_recs = []
            combined_stats = []
            combined_rels = []

            for ext in ext_list:
                combined_claims.extend(ext.claims)
                combined_facts.extend(ext.facts)
                combined_entities.extend(ext.entities)
                combined_recs.extend(ext.recommendations)
                combined_stats.extend(ext.statistics)
                combined_rels.extend(ext.relationships)

            sk = SourceKnowledge(
                source_id=s_id,
                source_url=source_url,
                topic=combined_topic,
                entities=combined_entities,
                claims=combined_claims,
                facts=combined_facts,
                recommendations=combined_recs,
                statistics=combined_stats,
                relationships=combined_rels,
            )
            source_knowledge_list.append(sk)

        logger.info(f"Constructed {len(source_knowledge_list)} independent source-level knowledge models.")
        return source_knowledge_list
