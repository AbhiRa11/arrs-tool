"""Playwright-based crawler for JavaScript-heavy websites and anti-bot protection."""
import uuid
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from arrs.crawlers.base import BaseCrawler
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class PlaywrightCrawler(BaseCrawler):
    """Crawler using Playwright headless browser for dynamic content."""

    async def crawl(self, url: str, analysis_id: str) -> CrawledContent:
        """
        Crawl URL using Playwright headless browser.

        Args:
            url: URL to crawl
            analysis_id: Analysis ID

        Returns:
            Crawled content

        Raises:
            Exception: If crawl fails
        """
        logger.info("Starting crawl with Playwright", extra={"url": url})

        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            try:
                # Create context with realistic browser fingerprint
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'Sec-Ch-Ua-Mobile': '?0',
                        'Sec-Ch-Ua-Platform': '"macOS"',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                    }
                )

                # Remove webdriver flag
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                page = await context.new_page()

                # Navigate to URL
                try:
                    response = await page.goto(
                        url,
                        wait_until='networkidle',
                        timeout=self.timeout * 1000  # Convert to milliseconds
                    )

                    # Wait for content to load
                    await page.wait_for_load_state('domcontentloaded')

                    # Get HTML content
                    html_content = await page.content()
                    status_code = response.status if response else 200
                    final_url = page.url

                    content = CrawledContent(
                        id=str(uuid.uuid4()),
                        analysis_id=analysis_id,
                        url=final_url,
                        html_content=html_content,
                        crawled_at=datetime.now(),
                        crawl_method="playwright",
                        status_code=status_code
                    )

                    logger.info("Playwright crawl successful", extra={
                        "url": url,
                        "final_url": final_url,
                        "status_code": status_code,
                        "content_length": len(html_content)
                    })

                    return content

                except PlaywrightTimeout as e:
                    logger.error("Playwright timeout", extra={"url": url, "error": str(e)})
                    raise Exception(f"Timeout while loading {url}: {str(e)}")

            finally:
                await browser.close()
