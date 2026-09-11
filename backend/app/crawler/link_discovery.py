import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from app.crawler.url_normalizer import URLNormalizer
from app.schemas.source import DiscoveredLink

IRRELEVANT_DOMAINS = {
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "linkedin.com",
    "pinterest.com",
    "youtube.com",
    "tiktok.com",
    "reddit.com",
    "github.com",
}

IRRELEVANT_PATH_PATTERNS = [
    re.compile(r"(?i)\b(login|signin|signup|register|auth|cart|checkout|account)\b"),
    re.compile(r"(?i)\b(privacy-policy|terms-of-service|terms-of-use|disclaimer|copyright)\b"),
    re.compile(r"(?i)\b(contact-us|about-us|careers|jobs|advertise|press|media-kit)\b"),
]


class LinkDiscovery:
    """Discovers, filters, and evaluates relevance of outgoing links within extracted webpages."""

    @classmethod
    def is_valid_link(cls, url: str) -> bool:
        """Filter out social media, non-http, and navigational junk."""
        if not url:
            return False

        lower_url = url.lower()
        if lower_url.startswith(("mailto:", "javascript:", "tel:", "#", "ftp:")):
            return False

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        if any(bad_d in domain for bad_d in IRRELEVANT_DOMAINS):
            return False

        if any(p.search(parsed.path) for p in IRRELEVANT_PATH_PATTERNS):
            return False

        # Ignore static assets
        if re.search(r"\.(pdf|jpg|jpeg|png|gif|svg|zip|tar|gz|mp4|mp3|exe|css|js)$", parsed.path, re.I):
            return False

        return True

    @classmethod
    def score_relevance(cls, link_url: str, link_text: Optional[str], query: str) -> float:
        """Calculate heuristic relevance score for a link given the research topic."""
        query_words = set(re.findall(r"\w+", query.lower()))
        # Filter out common stop words
        stop_words = {"the", "a", "an", "for", "and", "in", "of", "to", "best", "what", "is", "how"}
        meaningful_words = query_words - stop_words
        if not meaningful_words:
            meaningful_words = query_words

        target_text = f"{link_url} {link_text or ''}".lower()
        match_count = sum(1 for w in meaningful_words if w in target_text)

        score = min(1.0, match_count / max(1, len(meaningful_words)))
        # Slight bonus if keywords appear in anchor text
        if link_text and any(w in link_text.lower() for w in meaningful_words):
            score = min(1.0, score + 0.15)

        return round(score, 3)

    @classmethod
    def discover_links(
        cls,
        raw_links: List[Dict[str, str]],
        query: str,
        threshold: float = 0.4,
        max_candidates: int = 5,
    ) -> List[DiscoveredLink]:
        """Filter and select top relevant candidate links for further crawl exploration."""
        discovered: List[DiscoveredLink] = []
        seen_urls = set()

        for item in raw_links:
            url = item.get("url", "")
            text = item.get("text", "")
            if not cls.is_valid_link(url):
                continue

            norm_url = URLNormalizer.normalize(url)
            if not norm_url or norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)

            score = cls.score_relevance(norm_url, text, query)
            if score >= threshold:
                discovered.append(
                    DiscoveredLink(
                        url=norm_url,
                        text=text,
                        relevance_score=score,
                        reason=f"Matched relevant query terms with score {score}",
                    )
                )

        discovered.sort(key=lambda x: x.relevance_score, reverse=True)
        return discovered[:max_candidates]
