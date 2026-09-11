import hashlib
from collections import defaultdict
from typing import Dict, Optional, Set
from app.crawler.url_normalizer import URLNormalizer


class DeduplicationManager:
    """Tracks crawled URLs, content hashes, and per-domain quotas to prevent duplication."""

    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.domain_visit_counts: Dict[str, int] = defaultdict(int)

    def is_url_seen(self, raw_url: str) -> bool:
        normalized = URLNormalizer.normalize(raw_url)
        if not normalized:
            return True
        return normalized in self.seen_urls

    def mark_url_seen(self, raw_url: str) -> Optional[str]:
        normalized = URLNormalizer.normalize(raw_url)
        if normalized:
            self.seen_urls.add(normalized)
            domain = URLNormalizer.extract_domain(normalized)
            self.domain_visit_counts[domain] += 1
            return normalized
        return None

    def compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of normalized text."""
        normalized_text = " ".join(content.split()).lower()
        return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    def is_content_duplicate(self, content: str) -> bool:
        """Check if content has already been extracted from another URL."""
        if not content or len(content.strip()) < 50:
            return False
        h = self.compute_content_hash(content)
        if h in self.seen_content_hashes:
            return True
        self.seen_content_hashes.add(h)
        return False

    def can_crawl_domain(self, domain: str, max_per_domain: int) -> bool:
        """Enforce domain visit caps."""
        clean_domain = domain.lower()
        if clean_domain.startswith("www."):
            clean_domain = clean_domain[4:]
        return self.domain_visit_counts[clean_domain] < max_per_domain

    def get_domain_count(self, domain: str) -> int:
        clean_domain = domain.lower()
        if clean_domain.startswith("www."):
            clean_domain = clean_domain[4:]
        return self.domain_visit_counts[clean_domain]
