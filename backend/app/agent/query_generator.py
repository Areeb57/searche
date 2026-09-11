import logging
from typing import List
from app.llm.base import LLMProvider
from app.schemas.search import GeneratedQueries

logger = logging.getLogger(__name__)

QUERY_GEN_SYSTEM_PROMPT = """You are a senior search intelligence researcher.
Your task is to generate distinct, complementary search queries that explore different critical facets of the user's research topic.

RULES:
1. Always include the user's original query as the first query.
2. Formulate complementary research angles:
   - Foundational mechanics and scientific definitions
   - Practical recommendations and actionable strategies
   - Potential risks, edge cases, limitations, or dissenting perspectives
   - Comparative effectiveness or evidence-based benchmarks
3. NEVER generate trivial variations that only reorder words or change synonyms.
4. Keep queries keyword-rich and optimal for modern search engines.
"""


class QueryGenerator:
    """Generates multifaceted search queries to uncover comprehensive research angles."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def generate_queries(self, original_query: str, number_of_queries: int = 4) -> List[str]:
        prompt = (
            f"Original Query: \"{original_query}\"\n"
            f"Total Queries Needed: {number_of_queries}\n\n"
            f"Generate a list of exactly {number_of_queries} diverse, complementary research queries."
        )

        try:
            result: GeneratedQueries = await self.llm.generate_structured(
                prompt=prompt,
                schema=GeneratedQueries,
                system_prompt=QUERY_GEN_SYSTEM_PROMPT,
            )

            queries = result.queries
            # Ensure original query is present
            if original_query not in queries:
                queries.insert(0, original_query)

            # Deduplicate and trim to requested count
            seen = set()
            unique_queries = []
            for q in queries:
                q_clean = q.strip()
                if q_clean and q_clean.lower() not in seen:
                    unique_queries.append(q_clean)
                    seen.add(q_clean.lower())

            return unique_queries[:number_of_queries]
        except Exception as e:
            logger.error(f"Error generating queries with LLM: {e}")
            # Fallback diverse heuristics
            return [
                original_query,
                f"best evidence based guide {original_query}",
                f"mechanisms and nutrition science {original_query}",
                f"risks and considerations {original_query}",
            ][:number_of_queries]
