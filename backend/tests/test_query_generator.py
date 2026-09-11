import pytest
from app.agent.query_generator import QueryGenerator
from app.llm.mock import MockLLMProvider
from app.schemas.search import GeneratedQueries


@pytest.mark.asyncio
async def test_query_generator_execution(mock_llm):
    generator = QueryGenerator(llm=mock_llm)
    original_query = "best foods for healthy weight gain"
    queries = await generator.generate_queries(original_query, number_of_queries=4)

    assert len(queries) <= 4
    assert len(queries) >= 2
    assert any(original_query.lower() in q.lower() for q in queries)


def test_generated_queries_schema():
    data = {
        "original_query": "how to learn python",
        "queries": [
            "how to learn python",
            "python learning roadmap beginners",
            "effective python study methods",
        ],
    }
    model = GeneratedQueries.model_validate(data)
    assert model.original_query == "how to learn python"
    assert len(model.queries) == 3
