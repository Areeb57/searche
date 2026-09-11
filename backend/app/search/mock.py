import logging
from typing import List
from app.schemas.search import SearchResult
from app.search.base import SearchEngine

logger = logging.getLogger(__name__)


class MockSearch(SearchEngine):
    """Deterministic Mock Search Engine for testing without network requests."""

    def __init__(self):
        logger.info("MockSearch initialized.")

    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        slug = query.lower().replace(" ", "-")[:20]
        results = [
            SearchResult(
                title=f"Clinical Guidelines and Principles for {query.title()}",
                url=f"https://healthline.example.com/nutrition/{slug}-guide",
                snippet=f"Comprehensive review detailing foundational mechanics, macronutrient intake, and protocols for {query}.",
                domain="healthline.example.com",
                query=query,
                rank=1,
                relevance_score=0.96,
            ),
            SearchResult(
                title=f"Evidence-Based Strategy for {query.title()} - Medical News",
                url=f"https://medicalnews.example.org/articles/{slug}-strategy",
                snippet=f"Meta-analysis and scientific findings covering efficacy and dietary variations for {query}.",
                domain="medicalnews.example.org",
                query=query,
                rank=2,
                relevance_score=0.91,
            ),
            SearchResult(
                title=f"Nutritional Approaches to {query.title()}",
                url=f"https://academichealth.example.edu/research/{slug}",
                snippet=f"Peer-reviewed studies detailing comparative outcomes and caloric surpluses in {query}.",
                domain="academichealth.example.edu",
                query=query,
                rank=3,
                relevance_score=0.85,
            ),
            SearchResult(
                title=f"Common Pitfalls and Limitations in {query.title()}",
                url=f"https://nutritionjournal.example.org/review/{slug}-risks",
                snippet=f"Critical analysis exploring counter-indications, fat accretion risks, and misconceptions regarding {query}.",
                domain="nutritionjournal.example.org",
                query=query,
                rank=4,
                relevance_score=0.80,
            ),
        ]
        return results[:limit]
