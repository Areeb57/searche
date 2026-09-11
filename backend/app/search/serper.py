import logging
from typing import List, Optional
import httpx
from app.config import settings
from app.schemas.search import SearchResult
from app.search.base import SearchEngine

logger = logging.getLogger(__name__)


class SerperSearch(SearchEngine):
    """Serper.dev Google Search API provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SERPER_API_KEY
        self.url = "https://google.serper.dev/search"
        if not self.api_key:
            logger.warning("SerperSearch initialized without SERPER_API_KEY.")

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("SERPER_API_KEY is not configured.")

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query,
            "num": limit,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

            results = []
            organic = data.get("organic", [])
            for rank, item in enumerate(organic, start=1):
                url = item.get("link", "")
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("snippet", ""),
                        domain=self.extract_domain(url),
                        query=query,
                        rank=rank,
                        relevance_score=1.0 - (rank * 0.05),
                    )
                )
            return results
