from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class SessionStatusEnum(str, Enum):
    """Execution status of a research session."""
    CREATED = "created"
    GENERATING_QUERIES = "generating_queries"
    SEARCHING = "searching"
    SELECTING_SOURCES = "selecting_sources"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    BUILDING_KNOWLEDGE = "building_knowledge"
    MERGING_KNOWLEDGE = "merging_knowledge"
    GENERATING_ANSWER = "generating_answer"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchConfig(BaseModel):
    """User-configurable research parameters with boundary validation."""
    number_of_queries: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of diverse search queries to generate (1-10)",
    )
    initial_sources: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Number of initial sources to select from search results (1-30)",
    )
    max_pages: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Total maximum pages to fetch/crawl across the session (1-100)",
    )
    max_depth: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Maximum crawl depth from initial sources (0-3)",
    )
    max_pages_per_domain: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum pages to fetch from any single domain (1-10)",
    )
    llm_provider: Optional[str] = Field(
        default=None,
        description="Override LLM provider ('openai', 'gemini', 'claude', 'mock')",
    )
    search_provider: Optional[str] = Field(
        default=None,
        description="Override Search provider ('tavily', 'brave', 'serper', 'duckduckgo', 'mock')",
    )


class ResearchRequest(BaseModel):
    """Payload to initiate a new research session."""
    query: str = Field(..., min_length=3, max_length=500, description="The user's research topic or question")
    config: Optional[ResearchConfig] = Field(
        default_factory=ResearchConfig,
        description="Optional execution configuration overrides",
    )


class ResearchSessionResponse(BaseModel):
    """High-level summary of a research session."""
    session_id: str
    original_query: str
    status: SessionStatusEnum
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    final_answer: Optional[str] = None
    error_message: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
