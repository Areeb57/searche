from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.schemas.research import ResearchConfig, SessionStatusEnum
from app.schemas.search import SearchResult
from app.schemas.source import Source, Document, CrawlQueueItem
from app.schemas.knowledge import (
    Claim,
    Entity,
    Relationship,
    SourceKnowledge,
    UnifiedClaim,
    Contradiction,
    KnowledgeNode,
    KnowledgeEdge,
)


@dataclass
class ResearchState:
    """Central state object passed cleanly across multi-stage research components."""

    session_id: str
    original_query: str
    config: ResearchConfig

    status: SessionStatusEnum = SessionStatusEnum.CREATED
    generated_queries: List[str] = field(default_factory=list)
    search_results: List[SearchResult] = field(default_factory=list)
    selected_sources: List[Source] = field(default_factory=list)

    crawl_queue: List[CrawlQueueItem] = field(default_factory=list)
    crawled_pages: List[Dict[str, Any]] = field(default_factory=list)
    extracted_documents: List[Document] = field(default_factory=list)

    raw_claims: List[Claim] = field(default_factory=list)
    raw_entities: List[Entity] = field(default_factory=list)
    raw_relationships: List[Relationship] = field(default_factory=list)

    source_knowledge: List[SourceKnowledge] = field(default_factory=list)
    unified_claims: List[UnifiedClaim] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)

    graph_nodes: List[KnowledgeNode] = field(default_factory=list)
    graph_edges: List[KnowledgeEdge] = field(default_factory=list)

    final_answer: Optional[str] = None
    key_findings: List[str] = field(default_factory=list)

    stats: Dict[str, Any] = field(
        default_factory=lambda: {
            "queries_generated": 0,
            "search_results_found": 0,
            "sources_selected": 0,
            "pages_crawled": 0,
            "pages_failed": 0,
            "claims_extracted": 0,
            "unified_claims": 0,
            "contradictions_found": 0,
        }
    )
    errors: List[Dict[str, Any]] = field(default_factory=list)
