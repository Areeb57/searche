import pytest
from app.crawler.url_normalizer import URLNormalizer
from app.crawler.deduplication import DeduplicationManager


def test_url_normalization_tracking_params():
    url = "https://example.com/article?utm_source=test&utm_medium=email&utm_campaign=spring&id=123"
    normalized = URLNormalizer.normalize(url)
    assert normalized == "https://example.com/article?id=123"


def test_url_normalization_trailing_slash_and_fragment():
    url = "https://www.example.com/article/#section-1"
    normalized = URLNormalizer.normalize(url)
    assert normalized == "https://www.example.com/article"


def test_url_normalization_case_and_port():
    url = "HTTP://EXAMPLE.COM:80/path/to/page/"
    normalized = URLNormalizer.normalize(url)
    assert normalized == "http://example.com/path/to/page"


def test_url_normalization_relative():
    base = "https://example.com/docs/guide/"
    relative = "../faq"
    normalized = URLNormalizer.normalize(relative, base_url=base)
    assert normalized == "https://example.com/docs/faq"


def test_domain_extraction():
    assert URLNormalizer.extract_domain("https://www.healthline.com/nutrition/foods") == "healthline.com"
    assert URLNormalizer.extract_domain("https://sub.domain.co.uk/page") == "sub.domain.co.uk"


def test_deduplication_manager():
    dedup = DeduplicationManager()
    url1 = "https://example.com/article"
    url2 = "https://example.com/article/?utm_source=twitter"

    assert not dedup.is_url_seen(url1)
    dedup.mark_url_seen(url1)
    assert dedup.is_url_seen(url1)
    # url2 normalizes to same as url1
    assert dedup.is_url_seen(url2)

    # Content duplicate detection
    content_a = "Consuming a moderate caloric surplus promotes lean muscle growth."
    content_b = "  consuming a moderate caloric surplus promotes lean muscle growth.  \n\n"
    assert not dedup.is_content_duplicate(content_a)
    assert dedup.is_content_duplicate(content_b)
