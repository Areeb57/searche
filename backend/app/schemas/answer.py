from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchAnswer(BaseModel):
    """Synthesized initial answer grounded in researched sources."""
    session_id: str
    answer: str = Field(..., description="Concise, source-aware research answer")
    key_findings: List[str] = Field(default_factory=list)
    sources_used: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions_summary: Optional[str] = None


class FollowUpRequest(BaseModel):
    """Question posed against stored research memory."""
    question: str = Field(..., min_length=2, max_length=1000, description="Follow-up question")


class FollowUpResponse(BaseModel):
    """Answer formulated exclusively from the session's stored research memory."""
    session_id: str
    question: str
    answer: str
    cited_sources: List[Dict[str, Any]] = Field(default_factory=list)
    relevant_claims: List[str] = Field(default_factory=list)
    disagreements_or_nuances: Optional[str] = None
