"""BeautifulSoup-based crawler for static websites."""
import uuid
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
from arrs.crawlers.base import BaseCrawler
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class BeautifulSoupCrawler(BaseCrawler):
    """Crawler using BeautifulSoup for static content."""

    async def crawl(self, url: str, analysis_id: str) -> CrawledContent:
        """
        Crawl URL using BeautifulSoup.

        Args:
            url: URL to crawl
            analysis_id: Analysis ID

        Returns:
            Crawled content

        Raises:
            httpx.HTTPError: If request fails
        """
        logger.info("Starting crawl with BeautifulSoup", extra={"url": url})

        # Use realistic browser headers to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                content = CrawledContent(
                    id=str(uuid.uuid4()),
                    analysis_id=analysis_id,
                    url=str(response.url),  # Final URL after redirects
                    html_content=response.text,
                    crawled_at=datetime.now(),
                    crawl_method="beautifulsoup",
                    status_code=response.status_code
                )

                logger.info("Crawl successful", extra={
                    "url": url,
                    "status_code": response.status_code,
                    "content_length": len(response.text)
                })

                return content

            except httpx.HTTPError as e:
                logger.error("Crawl failed", extra={"url": url, "error": str(e)})
                raise
