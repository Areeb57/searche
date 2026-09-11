import asyncio
import ipaddress
import logging
import socket
from typing import Any, Dict, Optional
from urllib.parse import urlparse
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

PRIVATE_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


class WebFetcher:
    """Asynchronous HTTP web fetcher with SSRF defense, retries, and size guards."""

    def __init__(
        self,
        timeout: int = settings.CRAWL_TIMEOUT_SECONDS,
        max_size: int = settings.MAX_PAGE_SIZE_BYTES,
    ):
        self.timeout = timeout
        self.max_size = max_size
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }

    @staticmethod
    def is_safe_url(url: str) -> bool:
        """Validate URL to prevent SSRF against internal/private infrastructure."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Block localhost and local development hostnames
            lower_host = hostname.lower()
            if lower_host in ("localhost", "127.0.0.1", "::1") or lower_host.endswith((".local", ".internal", ".localhost")):
                return False

            # Check if hostname is an IP literal
            try:
                ip = ipaddress.ip_address(hostname)
                for net in PRIVATE_NETWORKS:
                    if ip in net:
                        logger.warning(f"SSRF blocked private IP {ip} in URL: {url}")
                        return False
                return True
            except ValueError:
                # Hostname is a domain name, verify resolved IPs if resolvable
                try:
                    resolved_ips = socket.gethostbyname_ex(hostname)[2]
                    for ip_str in resolved_ips:
                        ip = ipaddress.ip_address(ip_str)
                        for net in PRIVATE_NETWORKS:
                            if ip in net:
                                logger.warning(f"SSRF blocked domain {hostname} resolving to {ip}")
                                return False
                except (socket.gaierror, socket.herror):
                    # Unresolvable DNS; permit through so httpx handles HTTP request error
                    pass

            return True
        except Exception as e:
            logger.debug(f"URL safety check failed for {url}: {e}")
            return False

    async def fetch(self, url: str, max_retries: int = 2) -> Dict[str, Any]:
        """Fetch webpage HTML asynchronously with exponential backoff."""
        if not self.is_safe_url(url):
            return {
                "url": url,
                "status_code": 400,
                "content_type": "",
                "html": "",
                "error": "URL failed SSRF safety checks",
            }

        backoff = 1.0
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=False,  # Allow self-signed or legacy certs for research
                ) as client:
                    async with client.stream("GET", url) as response:
                        content_type = response.headers.get("content-type", "").lower()
                        # Verify text or html
                        if not any(t in content_type for t in ["text/html", "application/xhtml", "text/plain", "xml"]):
                            return {
                                "url": str(response.url),
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "html": "",
                                "error": f"Unsupported content-type: {content_type}",
                            }

                        body_chunks = []
                        total_bytes = 0
                        async for chunk in response.aiter_bytes():
                            total_bytes += len(chunk)
                            if total_bytes > self.max_size:
                                logger.warning(f"Response exceeded size cap ({self.max_size} bytes): {url}")
                                break
                            body_chunks.append(chunk)

                        raw_bytes = b"".join(body_chunks)
                        encoding = response.encoding or "utf-8"
                        try:
                            html_text = raw_bytes.decode(encoding, errors="replace")
                        except Exception:
                            html_text = raw_bytes.decode("utf-8", errors="replace")

                        return {
                            "url": str(response.url),
                            "status_code": response.status_code,
                            "content_type": content_type,
                            "html": html_text,
                            "headers": dict(response.headers),
                            "error": None if response.status_code < 400 else f"HTTP {response.status_code}",
                        }

            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt < max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                else:
                    return {
                        "url": url,
                        "status_code": 0,
                        "content_type": "",
                        "html": "",
                        "error": str(e),
                    }
            except Exception as e:
                return {
                    "url": url,
                    "status_code": 0,
                    "content_type": "",
                    "html": "",
                    "error": f"Unexpected fetch error: {str(e)}",
                }

        return {
            "url": url,
            "status_code": 0,
            "content_type": "",
            "html": "",
            "error": "Failed after max retries",
        }
