import logging
import traceback
from typing import Optional
from app.config import settings
from app.schemas.research import ResearchConfig, SessionStatusEnum
from app.schemas.websocket import WebSocketEvent, WebSocketEventType
from app.agent.research_state import ResearchState
from app.agent.query_generator import QueryGenerator
from app.agent.search_manager import SearchManager
from app.agent.source_selector import SourceSelector
from app.agent.crawl_manager import CrawlManager
from app.agent.article_analyzer import ArticleAnalyzer
from app.agent.knowledge_builder import KnowledgeBuilder
from app.agent.knowledge_merger import KnowledgeMerger
from app.agent.answer_generator import AnswerGenerator
from app.knowledge.provenance import ProvenanceTracker
from app.llm.base import LLMProvider
from app.llm.factory import get_llm_provider
from app.search.base import SearchEngine
from app.search.factory import get_search_engine
from app.database.repositories import ResearchRepository
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Orchestrates the complete multi-stage asynchronous research pipeline."""

    def __init__(
        self,
        repository: ResearchRepository,
        llm: Optional[LLMProvider] = None,
        search_engine: Optional[SearchEngine] = None,
    ):
        self.repository = repository
        self.llm = llm or get_llm_provider()
        self.search_engine = search_engine or get_search_engine()
        self.provenance = ProvenanceTracker()

        # Modular components
        self.query_generator = QueryGenerator(llm=self.llm)
        self.search_manager = SearchManager(search_engine=self.search_engine, repository=self.repository)
        self.source_selector = SourceSelector(repository=self.repository)
        self.crawl_manager = CrawlManager(repository=self.repository)
        self.article_analyzer = ArticleAnalyzer(llm=self.llm, repository=self.repository, provenance=self.provenance)
        self.knowledge_builder = KnowledgeBuilder(repository=self.repository)
        self.knowledge_merger = KnowledgeMerger(llm=self.llm, repository=self.repository, provenance=self.provenance)
        self.answer_generator = AnswerGenerator(llm=self.llm, repository=self.repository)

    async def _emit_event(
        self,
        session_id: str,
        event_type: WebSocketEventType,
        stage: str,
        message: str,
        payload: Optional[dict] = None,
    ) -> None:
        """Helper to broadcast real-time status updates via WebSocket."""
        event = WebSocketEvent(
            type=event_type.value,
            session_id=session_id,
            stage=stage,
            message=message,
            payload=payload or {},
        )
        await ws_manager.broadcast(event)

    async def execute_research(self, session_id: str, query: str, config: ResearchConfig) -> ResearchState:
        """Run the end-to-end multi-stage research pipeline."""
        state = ResearchState(
            session_id=session_id,
            original_query=query,
            config=config,
            status=SessionStatusEnum.CREATED,
        )

        try:
            logger.info(f"[{session_id}] RESEARCH INITIATED: '{query}'")
            await self._emit_event(
                session_id,
                WebSocketEventType.RESEARCH_STARTED,
                stage="created",
                message=f"Research started for: {query}",
                payload={"query": query, "config": config.model_dump()},
            )

            # STAGE 1: Generate Additional Queries
            state.status = SessionStatusEnum.GENERATING_QUERIES
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.QUERIES_GENERATED,
                stage="generating_queries",
                message="Generating multifaceted search angles...",
            )

            state.generated_queries = await self.query_generator.generate_queries(
                original_query=query,
                number_of_queries=config.number_of_queries,
            )
            state.stats["queries_generated"] = len(state.generated_queries)
            logger.info(f"[{session_id}] Generated queries: {state.generated_queries}")

            # STAGE 2: Search All Queries Concurrently
            state.status = SessionStatusEnum.SEARCHING
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.SEARCH_STARTED,
                stage="searching",
                message=f"Searching web across {len(state.generated_queries)} queries concurrently...",
                payload={"queries": state.generated_queries},
            )

            state.search_results = await self.search_manager.search_all_queries(
                session_id=session_id,
                queries=state.generated_queries,
                limit_per_query=8,
            )
            state.stats["search_results_found"] = len(state.search_results)

            # STAGE 3: Select Initial Sources
            state.status = SessionStatusEnum.SELECTING_SOURCES
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.SOURCES_SELECTED,
                stage="selecting_sources",
                message="Scoring and selecting high-relevance sources...",
            )

            state.selected_sources = await self.source_selector.select_sources(
                session_id=session_id,
                search_results=state.search_results,
                initial_sources_count=config.initial_sources,
            )
            state.stats["sources_selected"] = len(state.selected_sources)

            # Register initial sources in ProvenanceTracker
            for s in state.selected_sources:
                self.provenance.register_source(source_id=s.id, url=s.url, domain=s.domain, title=s.title)

            # STAGE 4: Crawl Webpages & Discover Links
            state.status = SessionStatusEnum.CRAWLING
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.CRAWL_STARTED,
                stage="crawling",
                message=f"Crawling {len(state.selected_sources)} initial sources with max depth {config.max_depth}...",
            )

            async def crawl_progress(data: dict):
                await self._emit_event(
                    session_id,
                    WebSocketEventType.PAGE_FETCHED if data.get("event") == "article_extracted" else WebSocketEventType.PAGE_FAILED,
                    stage="crawling",
                    message=f"Crawled: {data.get('url', '')}",
                    payload=data,
                )

            state.extracted_documents = await self.crawl_manager.crawl_sources(
                session_id=session_id,
                initial_sources=state.selected_sources,
                query=query,
                max_pages=config.max_pages,
                max_depth=config.max_depth,
                max_pages_per_domain=config.max_pages_per_domain,
                progress_callback=crawl_progress,
            )
            state.stats["pages_crawled"] = len(state.extracted_documents)

            # STAGE 5: Analyze Articles with LLM
            state.status = SessionStatusEnum.ANALYZING
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.ARTICLE_ANALYZED,
                stage="analyzing",
                message=f"Extracting structured claims and entities from {len(state.extracted_documents)} documents...",
            )

            article_extractions = await self.article_analyzer.analyze_all_documents(
                session_id=session_id,
                documents=state.extracted_documents,
            )

            for ext in article_extractions:
                state.raw_claims.extend(ext.claims)
                state.raw_entities.extend(ext.entities)
                state.raw_relationships.extend(ext.relationships)

            state.stats["claims_extracted"] = len(state.raw_claims)

            # STAGE 6: Build Source-Level Knowledge
            state.status = SessionStatusEnum.BUILDING_KNOWLEDGE
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.KNOWLEDGE_CREATED,
                stage="building_knowledge",
                message="Constructing independent source-level knowledge representations...",
            )

            state.source_knowledge = await self.knowledge_builder.build_source_knowledge(
                session_id=session_id,
                sources=state.selected_sources,
                documents=state.extracted_documents,
                extractions=article_extractions,
            )

            # STAGE 7: Merge Knowledge, Deduplicate Claims & Detect Contradictions
            state.status = SessionStatusEnum.MERGING_KNOWLEDGE
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.KNOWLEDGE_MERGED,
                stage="merging_knowledge",
                message="Synthesizing unified claims and detecting cross-source contradictions...",
            )

            unified_claims, contradictions, graph_resp = await self.knowledge_merger.merge_knowledge(
                session_id=session_id,
                topic=query,
                sources=state.selected_sources,
                raw_claims=state.raw_claims,
                raw_entities=state.raw_entities,
                raw_relationships=state.raw_relationships,
            )
            state.unified_claims = unified_claims
            state.contradictions = contradictions
            state.graph_nodes = graph_resp.nodes
            state.graph_edges = graph_resp.edges
            state.stats["unified_claims"] = len(unified_claims)
            state.stats["contradictions_found"] = len(contradictions)

            # STAGE 8: Generate Concise Final Answer
            state.status = SessionStatusEnum.GENERATING_ANSWER
            await self.repository.update_status(session_id, state.status.value)
            await self._emit_event(
                session_id,
                WebSocketEventType.ANSWER_GENERATED,
                stage="generating_answer",
                message="Generating concise, source-aware research answer...",
            )

            research_answer = await self.answer_generator.generate_answer(
                session_id=session_id,
                original_query=query,
                unified_claims=state.unified_claims,
                contradictions=state.contradictions,
                sources=state.selected_sources,
            )
            state.final_answer = research_answer.answer
            state.key_findings = research_answer.key_findings

            # STAGE 9: Complete Session
            state.status = SessionStatusEnum.COMPLETED
            await self.repository.update_status(
                session_id=session_id,
                status=state.status.value,
                final_answer=state.final_answer,
                stats_update=state.stats,
            )

            await self._emit_event(
                session_id,
                WebSocketEventType.COMPLETED,
                stage="completed",
                message="Research session completed successfully.",
                payload={
                    "session_id": session_id,
                    "final_answer": state.final_answer,
                    "key_findings": state.key_findings,
                    "stats": state.stats,
                },
            )
            logger.info(f"[{session_id}] RESEARCH COMPLETED SUCCESSFULLY.")
            return state

        except Exception as e:
            logger.error(f"[{session_id}] Critical failure in research pipeline: {e}\n{traceback.format_exc()}")
            state.status = SessionStatusEnum.FAILED
            err_msg = str(e)
            await self.repository.update_status(
                session_id=session_id,
                status=state.status.value,
                error_message=err_msg,
            )
            await self._emit_event(
                session_id,
                WebSocketEventType.ERROR,
                stage="failed",
                message=f"Research pipeline failed: {err_msg}",
                payload={"error": err_msg},
            )
            return state
