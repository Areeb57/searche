import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    TypeDecorator,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship as sa_relationship

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

Base = declarative_base()


class VectorType(TypeDecorator):
    """Universal Vector type handling PostgreSQL pgvector or SQLite JSON array fallback."""
    impl = JSON
    cache_ok = True

    def __init__(self, dim: int = 1536):
        super().__init__()
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR:
            return value
        if isinstance(value, (list, tuple)):
            return list(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return list(value)


class ResearchSessionModel(Base):
    __tablename__ = "research_sessions"

    id = Column(String(64), primary_key=True)  # rs_...
    original_query = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="created", index=True)
    configuration = Column(JSON, nullable=False, default=dict)
    final_answer = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    stats = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    queries = sa_relationship("ResearchQueryModel", back_populates="session", cascade="all, delete-orphan")
    search_results = sa_relationship("SearchResultModel", back_populates="session", cascade="all, delete-orphan")
    sources = sa_relationship("SourceModel", back_populates="session", cascade="all, delete-orphan")
    documents = sa_relationship("DocumentModel", back_populates="session", cascade="all, delete-orphan")
    claims = sa_relationship("ClaimModel", back_populates="session", cascade="all, delete-orphan")
    unified_claims = sa_relationship("UnifiedClaimModel", back_populates="session", cascade="all, delete-orphan")
    contradictions = sa_relationship("ContradictionModel", back_populates="session", cascade="all, delete-orphan")
    nodes = sa_relationship("KnowledgeNodeModel", back_populates="session", cascade="all, delete-orphan")
    edges = sa_relationship("KnowledgeEdgeModel", back_populates="session", cascade="all, delete-orphan")
    embeddings = sa_relationship("KnowledgeEmbeddingModel", back_populates="session", cascade="all, delete-orphan")
    answers = sa_relationship("ResearchAnswerModel", back_populates="session", cascade="all, delete-orphan")


class ResearchQueryModel(Base):
    __tablename__ = "research_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    rank = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="queries")


class SearchResultModel(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)
    domain = Column(String(255), nullable=False, index=True)
    rank = Column(Integer, default=1)
    relevance_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="search_results")


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True)  # src_...
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    title = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    depth = Column(Integer, default=0)
    parent_source_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="sources")
    documents = sa_relationship("DocumentModel", back_populates="source", cascade="all, delete-orphan")
    claims = sa_relationship("ClaimModel", back_populates="source", cascade="all, delete-orphan")


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True)  # doc_...
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    published_date = Column(String(64), nullable=True)
    raw_html = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="documents")
    source = sa_relationship("SourceModel", back_populates="documents")
    claims = sa_relationship("ClaimModel", back_populates="document", cascade="all, delete-orphan")
    links = sa_relationship("DocumentLinkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentLinkModel(Base):
    __tablename__ = "document_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    text = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    is_queued = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = sa_relationship("DocumentModel", back_populates="links")


class SourceKnowledgeModel(Base):
    __tablename__ = "source_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ClaimModel(Base):
    __tablename__ = "claims"

    id = Column(String(64), primary_key=True)  # clm_...
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    importance = Column(Float, default=0.8)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="claims")
    document = sa_relationship("DocumentModel", back_populates="claims")
    source = sa_relationship("SourceModel", back_populates="claims")
    provenance_links = sa_relationship("ClaimSourceModel", back_populates="claim", cascade="all, delete-orphan")


class EntityModel(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)


class RelationshipModel(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    source_entity = Column(String(255), nullable=False)
    target_entity = Column(String(255), nullable=False)
    relation_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    document_id = Column(String(64), nullable=True)


class UnifiedClaimModel(Base):
    __tablename__ = "unified_claims"

    id = Column(String(64), primary_key=True)  # uclm_...
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="unified_claims")
    sources = sa_relationship("ClaimSourceModel", back_populates="unified_claim", cascade="all, delete-orphan")


class ClaimSourceModel(Base):
    __tablename__ = "claim_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unified_claim_id = Column(String(64), ForeignKey("unified_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String(64), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(64), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    support_type = Column(String(32), default="direct")  # direct | partial | qualifies
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    unified_claim = sa_relationship("UnifiedClaimModel", back_populates="sources")
    claim = sa_relationship("ClaimModel", back_populates="provenance_links")


class ContradictionModel(Base):
    __tablename__ = "contradictions"

    id = Column(String(64), primary_key=True)  # cntr_...
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(Text, nullable=False)
    claims_json = Column(JSON, nullable=False)
    relationship = Column(String(64), default="contradiction")
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="contradictions")


class KnowledgeNodeModel(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(String(128), primary_key=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type = Column(String(32), nullable=False)  # topic, concept, claim, entity, contradiction, source
    label = Column(Text, nullable=False)
    data_json = Column(JSON, nullable=False, default=dict)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)

    session = sa_relationship("ResearchSessionModel", back_populates="nodes")


class KnowledgeEdgeModel(Base):
    __tablename__ = "knowledge_edges"

    id = Column(String(128), primary_key=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id = Column(String(128), nullable=False, index=True)
    target_node_id = Column(String(128), nullable=False, index=True)
    relationship = Column(String(64), nullable=False, default="relates_to")
    label = Column(String(128), nullable=True)
    data_json = Column(JSON, nullable=False, default=dict)

    session = sa_relationship("ResearchSessionModel", back_populates="edges")


class KnowledgeEmbeddingModel(Base):
    __tablename__ = "knowledge_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(32), nullable=False, index=True)  # claim, unified_claim, document, answer
    item_id = Column(String(64), nullable=False, index=True)
    text_content = Column(Text, nullable=False)
    embedding = Column(VectorType(1536), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="embeddings")


class ResearchAnswerModel(Base):
    __tablename__ = "research_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=False, default=list)
    sources_summary = Column(JSON, nullable=False, default=list)
    contradictions_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = sa_relationship("ResearchSessionModel", back_populates="answers")
