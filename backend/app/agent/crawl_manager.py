import asyncio
import logging
import uuid
from typing import Any, Callable, Coroutine, Dict, List, Optional
from app.config import settings
from app.crawler.url_normalizer import URLNormalizer
from app.crawler.deduplication import DeduplicationManager
from app.crawler.fetcher import WebFetcher
from app.crawler.extractor import ContentExtractor
from app.crawler.cleaner import ContentCleaner
from app.crawler.link_discovery import LinkDiscovery
from app.schemas.source import Source, Document, CrawlQueueItem, CrawlStatus
from app.database.repositories import ResearchRepository

logger = logging.getLogger(__name__)


class CrawlManager:
    """Manages asynchronous queued webpage crawling, rate limiting, and recursive link exploration."""

    def __init__(
        self,
        repository: ResearchRepository,
        fetcher: Optional[WebFetcher] = None,
        max_concurrent: int = settings.MAX_CONCURRENT_REQUESTS,
    ):
        self.repository = repository
        self.fetcher = fetcher or WebFetcher()
        self.dedup = DeduplicationManager()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def crawl_sources(
        self,
        session_id: str,
        initial_sources: List[Source],
        query: str,
        max_pages: int = 20,
        max_depth: int = 1,
        max_pages_per_domain: int = 3,
        progress_callback: Optional[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = None,
    ) -> List[Document]:
        """Crawl initial sources and discover relevant links up to max_pages and max_depth."""
        queue: List[CrawlQueueItem] = []
        crawled_documents: List[Document] = []
        pages_crawled_count = 0

        # Initialize queue with initial sources (depth 0)
        for src in initial_sources:
            norm_url = URLNormalizer.normalize(src.url)
            if not norm_url or self.dedup.is_url_seen(norm_url):
                continue

            queue.append(
                CrawlQueueItem(
                    url=norm_url,
                    depth=src.depth,
                    parent_url=None,
                    parent_source_id=src.id,
                    domain=src.domain,
                    status=CrawlStatus.QUEUED,
                )
            )

        logger.info(f"CrawlManager initialized with {len(queue)} items in queue for session {session_id}")

        while queue and pages_crawled_count < max_pages:
            item = queue.pop(0)

            # Check domain quota
            if not self.dedup.can_crawl_domain(item.domain, max_pages_per_domain):
                logger.debug(f"Skipping {item.url}: domain cap reached for {item.domain}")
                continue

            # Mark URL visited
            canonical_url = self.dedup.mark_url_seen(item.url)
            if not canonical_url:
                continue

            # Notify progress
            if progress_callback:
                await progress_callback({
                    "event": "page_fetching",
                    "url": canonical_url,
                    "depth": item.depth,
                    "completed": pages_crawled_count,
                    "total": min(max_pages, pages_crawled_count + len(queue) + 1),
                })

            # Fetch page under concurrency semaphore
            fetch_result = None
            async with self.semaphore:
                fetch_result = await self.fetcher.fetch(canonical_url)

            if fetch_result.get("error") or not fetch_result.get("html"):
                logger.warning(f"Failed fetching {canonical_url}: {fetch_result.get('error')}")
                if progress_callback:
                    await progress_callback({"event": "page_failed", "url": canonical_url, "error": fetch_result.get("error")})
                continue

            pages_crawled_count += 1

            # Extract content
            extracted = ContentExtractor.extract(fetch_result["html"], base_url=canonical_url)
            cleaned_text = ContentCleaner.clean(extracted["main_content"])

            if not cleaned_text or len(cleaned_text.strip()) < 100:
                logger.info(f"Insufficient text in {canonical_url}, skipping.")
                continue

            # Deduplicate content
            if self.dedup.is_content_duplicate(cleaned_text):
                logger.info(f"Duplicate content detected for {canonical_url}, skipping.")
                continue

            content_hash = self.dedup.compute_content_hash(cleaned_text)
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"

            # Ensure source exists in DB for this document
            source_id = item.parent_source_id
            if not source_id:
                source_id = f"src_{uuid.uuid4().hex[:8]}"
                await self.repository.add_source(
                    source_id=source_id,
                    session_id=session_id,
                    url=canonical_url,
                    domain=item.domain,
                    title=extracted.get("title"),
                    relevance_score=0.8,
                    depth=item.depth,
                    parent_source_id=None,
                )

            # Persist Document to database
            doc_model = await self.repository.add_document(
                doc_id=doc_id,
                source_id=source_id,
                session_id=session_id,
                url=canonical_url,
                cleaned_text=cleaned_text,
                content_hash=content_hash,
                title=extracted.get("title"),
                author=extracted.get("author"),
                published_date=extracted.get("published_date"),
                raw_html=None,  # Keep DB light, raw_html can be omitted or truncated
            )

            document = Document(
                id=doc_id,
                source_id=source_id,
                session_id=session_id,
                url=canonical_url,
                title=extracted.get("title"),
                author=extracted.get("author"),
                published_date=extracted.get("published_date"),
                cleaned_text=cleaned_text,
                content_hash=content_hash,
            )
            crawled_documents.append(document)

            if progress_callback:
                await progress_callback({
                    "event": "article_extracted",
                    "url": canonical_url,
                    "title": document.title,
                    "doc_id": doc_id,
                    "completed": pages_crawled_count,
                })

            # Discover outgoing links if depth allows
            if item.depth < max_depth:
                candidate_links = LinkDiscovery.discover_links(
                    raw_links=extracted["links"],
                    query=query,
                    threshold=0.4,
                    max_candidates=4,
                )

                # Persist discovered links
                db_links = [
                    {
                        "url": cl.url,
                        "text": cl.text,
                        "relevance_score": cl.relevance_score,
                        "is_queued": True,
                    }
                    for cl in candidate_links
                ]
                await self.repository.add_document_links(doc_id=doc_id, session_id=session_id, links=db_links)

                for cl in candidate_links:
                    c_domain = URLNormalizer.extract_domain(cl.url)
                    if not self.dedup.is_url_seen(cl.url) and self.dedup.can_crawl_domain(c_domain, max_pages_per_domain):
                        # Register child source
                        child_source_id = f"src_{uuid.uuid4().hex[:8]}"
                        await self.repository.add_source(
                            source_id=child_source_id,
                            session_id=session_id,
                            url=cl.url,
                            domain=c_domain,
                            title=cl.text,
                            relevance_score=cl.relevance_score,
                            depth=item.depth + 1,
                            parent_source_id=source_id,
                        )

                        queue.append(
                            CrawlQueueItem(
                                url=cl.url,
                                depth=item.depth + 1,
                                parent_url=canonical_url,
                                parent_source_id=child_source_id,
                                domain=c_domain,
                                status=CrawlStatus.QUEUED,
                            )
                        )

        logger.info(f"Crawl completed. Crawled {len(crawled_documents)} valid documents.")
        return crawled_documents
