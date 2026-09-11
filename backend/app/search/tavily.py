import logging
from typing import List, Optional
import httpx
from app.config import settings
from app.schemas.search import SearchResult
from app.search.base import SearchEngine

logger = logging.getLogger(__name__)


class TavilySearch(SearchEngine):
    """Tavily AI Search API provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.url = "https://api.tavily.com/search"
        if not self.api_key:
            logger.warning("TavilySearch initialized without TAVILY_API_KEY.")

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not configured.")

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": limit,
            "search_depth": "advanced",
            "include_raw_content": False,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for rank, item in enumerate(data.get("results", []), start=1):
                url = item.get("url", "")
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("content", ""),
                        domain=self.extract_domain(url),
                        query=query,
                        rank=rank,
                        relevance_score=item.get("score", 1.0 - (rank * 0.05)),
                    )
                )
            return results
