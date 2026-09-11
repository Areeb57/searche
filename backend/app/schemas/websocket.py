import time
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class WebSocketEventType(str, Enum):
    """Event types broadcast over WebSocket."""
    RESEARCH_STARTED = "research_started"
    QUERIES_GENERATED = "queries_generated"
    SEARCH_STARTED = "search_started"
    SEARCH_RESULT = "search_result"
    SOURCES_SELECTED = "sources_selected"
    DUPLICATE_REMOVED = "duplicate_removed"
    CRAWL_STARTED = "crawl_started"
    PAGE_FETCHED = "page_fetched"
    PAGE_FAILED = "page_failed"
    ARTICLE_EXTRACTED = "article_extracted"
    LINK_DISCOVERED = "link_discovered"
    LINK_QUEUED = "link_queued"
    ARTICLE_ANALYZED = "article_analyzed"
    KNOWLEDGE_CREATED = "knowledge_created"
    KNOWLEDGE_MERGED = "knowledge_merged"
    CONTRADICTION_DETECTED = "contradiction_detected"
    ANSWER_GENERATED = "answer_generated"
    COMPLETED = "completed"
    ERROR = "error"


class WebSocketEvent(BaseModel):
    """Standardized event packet broadcast to frontend WebSocket subscribers."""
    type: str
    session_id: str
    stage: str
    message: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)
