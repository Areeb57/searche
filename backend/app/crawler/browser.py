import logging
from typing import Any, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class PlaywrightBrowser:
    """Optional Playwright browser renderer for JavaScript-heavy dynamic pages."""

    def __init__(self):
        self.available = False
        try:
            import playwright
            self.available = True
        except ImportError:
            logger.debug("Playwright not installed; dynamic browser rendering disabled.")

    async def fetch_rendered_html(self, url: str) -> Optional[Dict[str, Any]]:
        if not self.available or not settings.ENABLE_PLAYWRIGHT_FALLBACK:
            return None

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent=settings.USER_AGENT)
                await page.goto(url, timeout=settings.CRAWL_TIMEOUT_SECONDS * 1000, wait_until="domcontentloaded")
                # Brief wait for client-side hydration
                await page.wait_for_timeout(1500)
                html = await page.content()
                await browser.close()

                return {
                    "url": url,
                    "status_code": 200,
                    "content_type": "text/html",
                    "html": html,
                    "headers": {},
                    "error": None,
                }
        except Exception as e:
            logger.warning(f"Playwright rendering failed for {url}: {e}")
            return None
