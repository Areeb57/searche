import logging
from typing import Optional
from app.config import settings
from app.search.base import SearchEngine
from app.search.tavily import TavilySearch
from app.search.brave import BraveSearch
from app.search.serper import SerperSearch
from app.search.duckduckgo import DuckDuckGoSearch
from app.search.mock import MockSearch

logger = logging.getLogger(__name__)


def get_search_engine(override_name: Optional[str] = None) -> SearchEngine:
    """Factory function to resolve and instantiate the active SearchEngine provider."""
    provider_name = (override_name or settings.SEARCH_PROVIDER).lower()

    if provider_name == "tavily":
        if settings.TAVILY_API_KEY:
            return TavilySearch()
        logger.warning("TAVILY_API_KEY not found. Falling back to DuckDuckGoSearch.")
        return DuckDuckGoSearch()

    elif provider_name == "brave":
        if settings.BRAVE_API_KEY:
            return BraveSearch()
        logger.warning("BRAVE_API_KEY not found. Falling back to DuckDuckGoSearch.")
        return DuckDuckGoSearch()

    elif provider_name == "serper":
        if settings.SERPER_API_KEY:
            return SerperSearch()
        logger.warning("SERPER_API_KEY not found. Falling back to DuckDuckGoSearch.")
        return DuckDuckGoSearch()

    elif provider_name == "duckduckgo":
        return DuckDuckGoSearch()

    elif provider_name == "mock":
        return MockSearch()

    else:
        logger.warning(f"Unknown search provider '{provider_name}'. Falling back to DuckDuckGoSearch.")
        return DuckDuckGoSearch()
