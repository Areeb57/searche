from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Claim(BaseModel):
    """An individual assertion or claim extracted from a document with full provenance."""
    id: str = Field(..., description="Unique claim identifier, e.g. claim_123")
    text: str = Field(..., description="The factual claim text")
    importance: float = Field(default=0.8, ge=0.0, le=1.0, description="Significance score (0-1)")
    source_document_id: str = Field(..., description="ID of the document containing this claim")
    source_id: Optional[str] = Field(default=None, description="ID of the parent source website")

    model_config = ConfigDict(from_attributes=True)


class Entity(BaseModel):
    """Named entity or key concept identified in the text."""
    name: str
    type: str = Field(..., description="Entity category (e.g. concept, food, nutrient, person, tool)")
    description: Optional[str] = None


class Fact(BaseModel):
    """Specific factual piece of data."""
    text: str
    confidence: float = 1.0


class Recommendation(BaseModel):
    """Actionable advice or recommendation extracted from content."""
    text: str
    priority: str = "medium"


class Statistic(BaseModel):
    """Empirical or numerical figure mentioned in content."""
    metric: str
    value: str
    context: Optional[str] = None


class Evidence(BaseModel):
    """Evidence or clinical/observational backing for a claim."""
    claim: str
    finding: str


class Limitation(BaseModel):
    """Caveat, limitation, or risk noted in source material."""
    text: str


class Definition(BaseModel):
    """Definition of a term or concept."""
    term: str
    definition: str


class Relationship(BaseModel):
    """Directional relationship between two concepts/entities."""
    source_entity: str
    target_entity: str
    relation_type: str = Field(..., description="Relationship verb (e.g. requires, causes, enhances, opposes)")
    description: Optional[str] = None


class ExtractedArticleKnowledge(BaseModel):
    """Structured knowledge extracted from a single article by the LLM."""
    topic: str
    summary: Optional[str] = None
    claims: List[Claim] = Field(default_factory=list)
    facts: List[Fact] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    statistics: List[Statistic] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    limitations: List[Limitation] = Field(default_factory=list)
    definitions: List[Definition] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)


class SourceKnowledge(BaseModel):
    """Independent source-level structured knowledge representation."""
    source_id: str
    source_url: str
    topic: str
    entities: List[Entity] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    facts: List[Fact] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    statistics: List[Statistic] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)


class ClaimProvenance(BaseModel):
    """Traceable provenance link to an original source and document."""
    source_id: str
    document_id: str
    source_url: Optional[str] = None
    support: str = Field(default="direct", description="direct | partial | qualifies")


class UnifiedClaim(BaseModel):
    """Consolidated claim aggregated from one or more distinct sources."""
    id: str
    text: str
    confidence: float = 1.0
    sources: List[ClaimProvenance] = Field(default_factory=list)
    original_claim_ids: List[str] = Field(default_factory=list)


class Contradiction(BaseModel):
    """Detected conflict or discrepancy between two or more claims."""
    id: str
    topic: str
    claims: List[Dict[str, Any]] = Field(
        ...,
        description="Conflicting claims paired with their source IDs and texts",
    )
    relationship: str = Field(
        default="contradiction",
        description="supports | contradicts | partially_supports | qualifies | same_meaning | different_context",
    )
    explanation: str


class KnowledgeNode(BaseModel):
    """Generic graph node formatted for React Flow or graph visualizers."""
    id: str
    type: str = Field(..., description="topic | concept | claim | entity | fact | contradiction | source")
    label: str
    data: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})


class KnowledgeEdge(BaseModel):
    """Generic directed graph edge formatted for React Flow."""
    id: str
    source: str
    target: str
    relationship: str = "relates_to"
    label: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphResponse(BaseModel):
    """Complete graph structure suitable for React Flow."""
    nodes: List[KnowledgeNode] = Field(default_factory=list)
    edges: List[KnowledgeEdge] = Field(default_factory=list)


class UnifiedKnowledge(BaseModel):
    """Aggregated knowledge repository for the completed session."""
    session_id: str
    topic: str
    unified_claims: List[UnifiedClaim] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 1.0
