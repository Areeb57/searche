import logging
from typing import List, Optional
import httpx
from app.config import settings
from app.schemas.search import SearchResult
from app.search.base import SearchEngine

logger = logging.getLogger(__name__)


class BraveSearch(SearchEngine):
    """Brave Search API provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.BRAVE_API_KEY
        self.url = "https://api.search.brave.com/res/v1/web/search"
        if not self.api_key:
            logger.warning("BraveSearch initialized without BRAVE_API_KEY.")

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY is not configured.")

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": min(limit, 20),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self.url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            results = []
            web_results = data.get("web", {}).get("results", [])
            for rank, item in enumerate(web_results, start=1):
                url = item.get("url", "")
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("description", ""),
                        domain=self.extract_domain(url),
                        query=query,
                        rank=rank,
                        relevance_score=1.0 - (rank * 0.05),
                    )
                )
            return results
