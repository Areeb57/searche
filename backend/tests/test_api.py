import pytest
from app.schemas.research import ResearchConfig


@pytest.mark.asyncio
async def test_health_check(async_client):
    resp = await async_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_start_research_endpoint(async_client):
    payload = {
        "query": "best foods for healthy weight gain",
        "config": {
            "number_of_queries": 3,
            "initial_sources": 5,
            "max_pages": 10,
            "max_depth": 1,
            "max_pages_per_domain": 2,
            "llm_provider": "mock",
            "search_provider": "mock",
        },
    }
    resp = await async_client.post("/api/research", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "session_id" in data
    assert data["status"] == "created"

    session_id = data["session_id"]
    # Check session endpoint
    resp_get = await async_client.get(f"/api/research/{session_id}")
    assert resp_get.status_code == 200
    s_data = resp_get.json()
    assert s_data["session_id"] == session_id
    assert s_data["original_query"] == payload["query"]


@pytest.mark.asyncio
async def test_validation_limits(async_client):
    # Query too short (< 3 chars)
    resp = await async_client.post("/api/research", json={"query": "ab"})
    assert resp.status_code == 422

    # number_of_queries out of bounds (> 10)
    resp = await async_client.post(
        "/api/research",
        json={"query": "healthy weight gain", "config": {"number_of_queries": 20}},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sources_and_graph_endpoints(async_client, test_repo):
    session_id = "rs_test_endpoints"
    await test_repo.create_session(session_id, "test topic", {})
    await test_repo.add_source(
        source_id="src_1",
        session_id=session_id,
        url="https://healthline.com/test",
        domain="healthline.com",
        title="Test Article",
        relevance_score=0.9,
    )
    await test_repo.add_unified_claim(
        unified_claim_id="uclm_1",
        session_id=session_id,
        text="Protein promotes muscle synthesis.",
        confidence=0.95,
        sources=[{"source_id": "src_1", "document_id": "doc_1", "support": "direct"}],
        original_claim_ids=["clm_1"],
    )

    # Test sources endpoint
    resp = await async_client.get(f"/api/research/{session_id}/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sources"]) == 1

    # Test knowledge endpoint
    resp = await async_client.get(f"/api/research/{session_id}/knowledge")
    assert resp.status_code == 200
    k_data = resp.json()
    assert len(k_data["unified_claims"]) == 1

    # Test follow-up question endpoint
    resp_q = await async_client.post(
        f"/api/research/{session_id}/questions",
        json={"question": "What protein intake is recommended?"},
    )
    assert resp_q.status_code == 200
    q_data = resp_q.json()
    assert q_data["session_id"] == session_id
    assert q_data["answer"]
