import logging
import uuid
from collections import defaultdict
from typing import Dict, List
from app.crawler.url_normalizer import URLNormalizer
from app.schemas.search import SearchResult
from app.schemas.source import Source
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class SourceSelector:
    """Selects and ranks candidate sources using multi-criteria cross-query scoring."""

    def __init__(self, repository: ResearchRepository):
        self.repository = repository

    async def select_sources(
        self,
        session_id: str,
        search_results: List[SearchResult],
        initial_sources_count: int = 8,
    ) -> List[Source]:
        """Rank and select high-quality unique sources across all query results."""
        if not search_results:
            return []

        # Group results by canonical URL
        grouped: Dict[str, List[SearchResult]] = defaultdict(list)
        for r in search_results:
            norm_url = URLNormalizer.normalize(r.url)
            if norm_url:
                grouped[norm_url].append(r)

        scored_candidates = []
        domain_counts: Dict[str, int] = defaultdict(int)

        for norm_url, result_list in grouped.items():
            first = result_list[0]
            domain = URLNormalizer.extract_domain(norm_url)

            # Frequency bonus: appeared across multiple distinct generated queries
            distinct_queries = len(set(r.query for r in result_list))
            query_frequency_bonus = (distinct_queries - 1) * 0.15

            # Search rank score (average rank)
            avg_rank = sum(r.rank for r in result_list) / len(result_list)
            rank_score = max(0.2, 1.0 - (avg_rank * 0.08))

            # Domain diversity penalty if same domain appears many times
            domain_penalty = domain_counts[domain] * 0.1
            domain_counts[domain] += 1

            # Combined heuristic relevance score
            final_score = min(1.0, max(0.1, rank_score + query_frequency_bonus - domain_penalty))

            scored_candidates.append(
                {
                    "url": norm_url,
                    "domain": domain,
                    "title": first.title,
                    "relevance_score": round(final_score, 3),
                }
            )

        # Sort descending by relevance score
        scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
        selected_candidates = scored_candidates[:initial_sources_count]

        # Convert to Source models and persist
        selected_sources: List[Source] = []
        for c in selected_candidates:
            source_id = f"src_{uuid.uuid4().hex[:8]}"
            src = Source(
                id=source_id,
                session_id=session_id,
                url=c["url"],
                domain=c["domain"],
                title=c["title"],
                relevance_score=c["relevance_score"],
                depth=0,
                parent_source_id=None,
            )
            await self.repository.add_source(
                source_id=source_id,
                session_id=session_id,
                url=src.url,
                domain=src.domain,
                title=src.title,
                relevance_score=src.relevance_score,
                depth=src.depth,
                parent_source_id=None,
            )
            selected_sources.append(src)

        logger.info(f"Selected {len(selected_sources)} initial sources for session {session_id}")
        return selected_sources
