import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database.connection import get_db, AsyncSessionLocal
from app.database.repositories import ResearchRepository
from app.schemas.research import ResearchRequest, ResearchConfig, ResearchSessionResponse
from app.schemas.knowledge import KnowledgeGraphResponse, KnowledgeNode, KnowledgeEdge
from app.schemas.answer import FollowUpRequest, FollowUpResponse
from app.agent.research_agent import ResearchAgent
from app.agent.follow_up_service import FollowUpService
from app.llm.factory import get_llm_provider
from app.search.factory import get_search_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research"])


async def _run_research_background(session_id: str, query: str, config: ResearchConfig) -> None:
    """Independent background worker for long-running research pipeline execution."""
    async with AsyncSessionLocal() as session:
        try:
            repo = ResearchRepository(session)
            llm = get_llm_provider(config.llm_provider)
            search_engine = get_search_engine(config.search_provider)
            agent = ResearchAgent(repository=repo, llm=llm, search_engine=search_engine)
            await agent.execute_research(session_id=session_id, query=query, config=config)
        except Exception as e:
            logger.error(f"Background task failed for session {session_id}: {e}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_research(
    payload: ResearchRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Initiate a multi-stage deep research session in the background."""
    session_id = f"rs_{uuid.uuid4().hex[:10]}"
    config = payload.config or ResearchConfig()

    repo = ResearchRepository(db)
    await repo.create_session(
        session_id=session_id,
        query=payload.query,
        config=config.model_dump(),
    )

    # Launch non-blocking background processing
    asyncio.create_task(_run_research_background(session_id, payload.query, config))

    return {
        "session_id": session_id,
        "status": "created",
    }


@router.get("/{session_id}", response_model=ResearchSessionResponse)
async def get_research_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResearchSessionResponse:
    """Retrieve high-level session status, metrics, and final synthesized answer."""
    repo = ResearchRepository(db)
    session = await repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{session_id}' not found.")

    return ResearchSessionResponse(
        session_id=session.id,
        original_query=session.original_query,
        status=session.status,
        configuration=session.configuration,
        created_at=session.created_at,
        updated_at=session.updated_at,
        final_answer=session.final_answer,
        error_message=session.error_message,
        stats=session.stats,
    )


@router.get("/{session_id}/sources")
async def get_research_sources(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve all identified sources and crawled documents with relevance scores."""
    repo = ResearchRepository(db)
    sources = await repo.get_sources_by_session(session_id)
    documents = await repo.get_documents_by_session(session_id)

    return {
        "session_id": session_id,
        "sources": [
            {
                "id": s.id,
                "domain": s.domain,
                "url": s.url,
                "title": s.title,
                "relevance_score": s.relevance_score,
                "depth": s.depth,
                "parent_source_id": s.parent_source_id,
            }
            for s in sources
        ],
        "documents": [
            {
                "id": d.id,
                "source_id": d.source_id,
                "title": d.title,
                "author": d.author,
                "published_date": d.published_date,
                "url": d.url,
                "content_preview": d.cleaned_text[:250] if d.cleaned_text else "",
            }
            for d in documents
        ],
    }


@router.get("/{session_id}/knowledge")
async def get_unified_knowledge(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve unified claims, source provenance lineage, and contradictions."""
    repo = ResearchRepository(db)
    unified_claims = await repo.get_unified_claims_with_sources(session_id)
    contradictions = await repo.get_contradictions(session_id)

    return {
        "session_id": session_id,
        "unified_claims": unified_claims,
        "contradictions": [
            {
                "id": c.id,
                "topic": c.topic,
                "claims": c.claims_json,
                "relationship": c.relationship,
                "explanation": c.explanation,
            }
            for c in contradictions
        ],
    }


@router.get("/{session_id}/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeGraphResponse:
    """Return nodes and edges formatted for React Flow graph visualization."""
    repo = ResearchRepository(db)
    nodes_models, edges_models = await repo.get_graph(session_id)

    nodes = [
        KnowledgeNode(
            id=n.id,
            type=n.node_type,
            label=n.label,
            data=n.data_json or {},
            position={"x": n.pos_x, "y": n.pos_y},
        )
        for n in nodes_models
    ]

    edges = [
        KnowledgeEdge(
            id=e.id,
            source=e.source_node_id,
            target=e.target_node_id,
            relationship=e.relationship,
            label=e.label,
            data=e.data_json or {},
        )
        for e in edges_models
    ]

    return KnowledgeGraphResponse(nodes=nodes, edges=edges)


@router.post("/{session_id}/questions", response_model=FollowUpResponse)
async def answer_follow_up_question(
    session_id: str,
    payload: FollowUpRequest,
    db: AsyncSession = Depends(get_db),
) -> FollowUpResponse:
    """Answer follow-up questions exclusively using the session's stored research memory."""
    repo = ResearchRepository(db)
    llm = get_llm_provider()
    service = FollowUpService(llm=llm, repository=repo)

    try:
        response = await service.answer_follow_up(session_id=session_id, question=payload.question)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error answering follow-up question for {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed generating follow-up answer from research memory.")


@router.get("/{session_id}/contradictions")
async def get_contradictions(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve identified conflicting assertions between sources."""
    repo = ResearchRepository(db)
    contradictions = await repo.get_contradictions(session_id)
    return {
        "session_id": session_id,
        "contradictions": [
            {
                "id": c.id,
                "topic": c.topic,
                "claims": c.claims_json,
                "relationship": c.relationship,
                "explanation": c.explanation,
            }
            for c in contradictions
        ],
    }
