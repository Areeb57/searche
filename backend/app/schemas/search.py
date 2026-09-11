from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GeneratedQueries(BaseModel):
    """Output from the query generator stage."""
    original_query: str
    queries: List[str] = Field(
        ...,
        min_length=1,
        description="List of complementary research queries exploring distinct angles",
    )


class SearchResult(BaseModel):
    """Normalized search result across all search engine providers."""
    title: str
    url: str
    snippet: str
    domain: str
    query: str
    rank: int = 1
    relevance_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
