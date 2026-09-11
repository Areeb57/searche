import re
from typing import Optional, Set
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, urljoin

TRACKING_PARAMS: Set[str] = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "ref",
    "fbclid",
    "gclid",
    "gclsrc",
    "msclkid",
    "yclid",
    "mc_eid",
    "_ga",
    "_gl",
    "trk",
    "source",
    "src",
}


class URLNormalizer:
    """Normalizes and canonicalizes web URLs for crawler deduplication."""

    @classmethod
    def normalize(cls, raw_url: str, base_url: Optional[str] = None) -> Optional[str]:
        """Normalize URL into a canonical, deduplicated representation."""
        if not raw_url or not isinstance(raw_url, str):
            return None

        clean_url = raw_url.strip()
        if not clean_url:
            return None

        # Resolve relative URLs
        if base_url:
            try:
                clean_url = urljoin(base_url, clean_url)
            except Exception:
                pass

        try:
            parsed = urlparse(clean_url)
        except Exception:
            return None

        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            return None

        netloc = parsed.netloc.lower()
        # Strip default ports
        if netloc.endswith(":80") and scheme == "http":
            netloc = netloc[:-3]
        elif netloc.endswith(":443") and scheme == "https":
            netloc = netloc[:-4]

        # Normalize www. if desired, but retain standard domain
        # Strip redundant trailing dots in netloc
        netloc = netloc.rstrip(".")

        # Clean path: normalize multiple slashes
        path = parsed.path
        path = re.sub(r"/+", "/", path)
        if not path:
            path = "/"
        elif len(path) > 1 and path.endswith("/"):
            # Strip trailing slash for consistency (unless root path)
            path = path.rstrip("/")

        # Filter query params
        query_params = []
        if parsed.query:
            for k, v in parse_qsl(parsed.query, keep_blank_values=False):
                if k.lower() not in TRACKING_PARAMS:
                    query_params.append((k, v))
            query_params.sort(key=lambda x: x[0])  # Sort query params for deterministic canonical URL

        clean_query = urlencode(query_params) if query_params else ""

        # Remove fragment entirely
        fragment = ""

        canonical = urlunparse((scheme, netloc, path, "", clean_query, fragment))
        return canonical

    @classmethod
    def extract_domain(cls, url: str) -> str:
        """Extract domain without www prefix."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain or "unknown"
        except Exception:
            return "unknown"
