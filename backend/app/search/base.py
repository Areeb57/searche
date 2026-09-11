from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse
from app.schemas.search import SearchResult


class SearchEngine(ABC):
    """Abstract interface for all search engine providers."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Perform search and return normalized SearchResult objects."""
        pass

    @staticmethod
    def extract_domain(url: str) -> str:
        """Helper to extract clean domain name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain or "unknown"
        except Exception:
            return "unknown"
