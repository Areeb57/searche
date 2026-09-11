import asyncio
import logging
from typing import List
from app.search.base import SearchEngine
from app.schemas.search import SearchResult
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class SearchManager:
    """Coordinates concurrent search execution across queries and normalizes results."""

    def __init__(self, search_engine: SearchEngine, repository: ResearchRepository):
        self.search_engine = search_engine
        self.repository = repository

    async def search_query(self, query: str, limit_per_query: int = 8) -> List[SearchResult]:
        try:
            logger.info(f"Executing search for query: '{query}'")
            results = await self.search_engine.search(query=query, limit=limit_per_query)
            logger.info(f"Retrieved {len(results)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []

    async def search_all_queries(
        self,
        session_id: str,
        queries: List[str],
        limit_per_query: int = 8,
    ) -> List[SearchResult]:
        """Execute searches concurrently with concurrency throttling."""
        semaphore = asyncio.Semaphore(3)

        async def _bounded_search(q: str):
            async with semaphore:
                return await self.search_query(q, limit_per_query=limit_per_query)

        tasks = [_bounded_search(q) for q in queries]
        nested_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results: List[SearchResult] = []
        for res in nested_results:
            if isinstance(res, list):
                all_results.extend(res)
            elif isinstance(res, Exception):
                logger.warning(f"A search query task failed with exception: {res}")

        # Persist to database
        db_records = [
            {
                "query": r.query,
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "domain": r.domain,
                "rank": r.rank,
                "relevance_score": r.relevance_score,
            }
            for r in all_results
        ]
        await self.repository.add_search_results(session_id=session_id, results=db_records)

        return all_results
