import pytest
from app.search.mock import MockSearch
from app.schemas.search import SearchResult


@pytest.mark.asyncio
async def test_search_results_normalization():
    engine = MockSearch()
    query = "healthy weight gain foods"
    results = await engine.search(query, limit=3)

    assert len(results) == 3
    for r in results:
        assert isinstance(r, SearchResult)
        assert r.title
        assert r.url.startswith("http")
        assert r.domain
        assert r.rank >= 1
        assert r.query == query


def test_search_result_validation():
    item = {
        "title": "Top Calorie Dense Foods",
        "url": "https://www.healthline.com/nutrition/18-foods-to-gain-weight",
        "snippet": "Nuts, seeds, avocados, and whole grains.",
        "domain": "healthline.com",
        "query": "weight gain foods",
        "rank": 1,
        "relevance_score": 0.95,
    }
    model = SearchResult.model_validate(item)
    assert model.domain == "healthline.com"
    assert model.rank == 1
