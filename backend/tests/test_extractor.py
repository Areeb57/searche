import pytest
from app.crawler.extractor import ContentExtractor
from app.crawler.cleaner import ContentCleaner
from app.crawler.link_discovery import LinkDiscovery

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>10 Best Foods for Healthy Weight Gain</title>
    <meta name="author" content="Dr. Jane Nutritionist">
</head>
<body>
    <nav class="navigation">
        <a href="/login">Login</a>
        <a href="/cart">Cart</a>
    </nav>
    <div class="cookie-banner">Please accept all tracking cookies.</div>
    <main>
        <h1>10 Best Foods for Healthy Weight Gain</h1>
        <p>Gaining weight in a healthy manner requires a consistent caloric surplus of nutrient-dense whole foods.</p>
        <p>Focus on energy-dense items like nut butters, whole eggs, avocados, and whole oats.</p>
        <a href="https://example.com/protein-study">Read our full study on protein requirements</a>
        <a href="https://twitter.com/share">Share on Twitter</a>
        <a href="mailto:contact@example.com">Email Us</a>
    </main>
    <footer>
        <p>All rights reserved. Terms of service apply.</p>
    </footer>
</body>
</html>
"""


def test_content_extraction():
    res = ContentExtractor.extract(SAMPLE_HTML, base_url="https://example.com/article")
    assert "10 Best Foods for Healthy Weight Gain" in res["title"]
    assert "Jane Nutritionist" in (res["author"] or "")
    assert "caloric surplus" in res["main_content"].lower()
    # Outgoing links should exclude javascript/mailto and contain valid http links
    urls = [link["url"] for link in res["links"]]
    assert "https://example.com/protein-study" in urls


def test_content_cleaner():
    raw_text = """
    10 Best Foods for Healthy Weight Gain
    
    All rights reserved. Terms of service apply.
    
    Gaining weight requires a caloric surplus.
    
    Sign up for our newsletter.
    """
    cleaned = ContentCleaner.clean(raw_text)
    assert "All rights reserved" not in cleaned
    assert "Sign up for our newsletter" not in cleaned
    assert "Gaining weight requires a caloric surplus." in cleaned


def test_link_discovery():
    links = [
        {"url": "https://example.com/protein-study", "text": "Clinical study on protein for weight gain"},
        {"url": "https://twitter.com/share", "text": "Tweet this"},
        {"url": "mailto:info@example.com", "text": "Contact"},
        {"url": "https://example.com/login", "text": "Login"},
    ]
    discovered = LinkDiscovery.discover_links(links, query="protein weight gain", threshold=0.3)
    assert len(discovered) == 1
    assert discovered[0].url == "https://example.com/protein-study"
    assert discovered[0].relevance_score > 0.3
