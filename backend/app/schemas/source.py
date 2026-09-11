from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CrawlStatus(str, Enum):
    """Status of an individual URL in the crawl pipeline."""
    QUEUED = "queued"
    FETCHING = "fetching"
    FETCHED = "fetched"
    FAILED = "failed"
    SKIPPED = "skipped"
    ANALYZED = "analyzed"


class Source(BaseModel):
    """Source website or domain identified for research."""
    id: str
    session_id: str
    url: str
    domain: str
    title: Optional[str] = None
    relevance_score: float = 0.0
    depth: int = 0
    parent_source_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Document(BaseModel):
    """Cleaned article document extracted from a source page."""
    id: str
    source_id: str
    session_id: str
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    cleaned_text: str
    content_hash: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CrawlQueueItem(BaseModel):
    """Item in the asynchronous crawl manager queue."""
    url: str
    depth: int = 0
    parent_url: Optional[str] = None
    parent_source_id: Optional[str] = None
    domain: str
    status: CrawlStatus = CrawlStatus.QUEUED
    error_message: Optional[str] = None


class DiscoveredLink(BaseModel):
    """Candidate link discovered within an extracted webpage."""
    url: str
    text: Optional[str] = None
    relevance_score: float = 0.0
    reason: Optional[str] = None
