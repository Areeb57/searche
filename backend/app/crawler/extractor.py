import logging
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import trafilatura
from app.crawler.url_normalizer import URLNormalizer

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extracts article title, author, date, main text, and outgoing links from HTML."""

    @classmethod
    def extract(cls, html: str, base_url: str) -> Dict[str, Any]:
        if not html or not html.strip():
            return {
                "title": "",
                "author": None,
                "published_date": None,
                "main_content": "",
                "links": [],
            }

        # 1. Primary extraction with Trafilatura
        trafilatura_content = None
        trafilatura_meta = None
        try:
            trafilatura_content = trafilatura.extract(
                html,
                url=base_url,
                include_comments=False,
                include_tables=True,
                include_links=False,
                output_format="txt",
            )
            trafilatura_meta = trafilatura.extract_metadata(html, default_url=base_url)
        except Exception as e:
            logger.debug(f"Trafilatura extraction exception on {base_url}: {e}")

        # 2. Parse DOM with BeautifulSoup for links, fallback text, and metadata
        soup = BeautifulSoup(html, "html.parser")

        # Strip scripts, styles, forms, nav, footer, iframes, ads
        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "iframe",
                "header",
                "footer",
                "nav",
                "aside",
                "form",
                "svg",
                "button",
            ]
        ):
            tag.decompose()

        # Remove elements with typical noise classes or IDs
        noise_keywords = ["cookie", "ad-", "banner", "sidebar", "social", "share", "comment", "popup"]
        for element in soup.find_all(attrs={"class": True}):
            cls_str = " ".join(element.get("class", [])).lower()
            if any(kw in cls_str for kw in noise_keywords):
                element.decompose()

        # Extract title
        title = ""
        if trafilatura_meta and trafilatura_meta.title:
            title = trafilatura_meta.title.strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Extract author
        author = None
        if trafilatura_meta and trafilatura_meta.author:
            author = trafilatura_meta.author.strip()
        else:
            author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
            if author_meta and author_meta.get("content"):
                author = author_meta["content"].strip()

        # Extract date
        published_date = None
        if trafilatura_meta and trafilatura_meta.date:
            published_date = str(trafilatura_meta.date).strip()
        else:
            date_meta = (
                soup.find("meta", attrs={"property": "article:published_time"})
                or soup.find("meta", attrs={"name": "date"})
                or soup.find("time")
            )
            if date_meta:
                published_date = date_meta.get("content") or date_meta.get_text(strip=True)

        # Main content determination: prioritize Trafilatura, fallback to BeautifulSoup text
        main_content = ""
        if trafilatura_content and len(trafilatura_content.strip()) > 100:
            main_content = trafilatura_content.strip()
        else:
            # Fallback to main/article tags or body
            main_tag = soup.find("main") or soup.find("article") or soup.find("body")
            if main_tag:
                paragraphs = [p.get_text(strip=True) for p in main_tag.find_all(["p", "h1", "h2", "h3", "li", "tr"])]
                main_content = "\n\n".join(p for p in paragraphs if len(p) > 20)

        # Extract outgoing links
        links: List[Dict[str, str]] = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            norm_url = URLNormalizer.normalize(href, base_url=base_url)
            link_text = a_tag.get_text(strip=True)
            if norm_url and norm_url != base_url:
                links.append({"url": norm_url, "text": link_text})

        return {
            "title": title,
            "author": author,
            "published_date": published_date,
            "main_content": main_content,
            "links": links,
        }
