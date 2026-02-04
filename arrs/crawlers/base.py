"""Base crawler interface."""
from abc import ABC, abstractmethod
from arrs.models.crawled_content import CrawledContent


class BaseCrawler(ABC):
    """Abstract base class for web crawlers."""

    def __init__(self, timeout: int = 30, user_agent: str = "ARRS-Bot/1.0"):
        """
        Initialize crawler.

        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent

    @abstractmethod
    async def crawl(self, url: str, analysis_id: str) -> CrawledContent:
        """
        Crawl a URL and return content.

        Args:
            url: URL to crawl
            analysis_id: Analysis ID for tracking

        Returns:
            Crawled content

        Raises:
            Exception: If crawling fails
        """
        pass

    def _should_use_playwright(self, url: str) -> bool:
        """
        Determine if Playwright should be used for this URL.

        Args:
            url: URL to check

        Returns:
            True if Playwright should be used
        """
        # Heuristic: Use Playwright for known SPA frameworks
        spa_indicators = [
            'app.', 'www.app.', 'my.', 'account.',
            'react', 'vue', 'angular'
        ]
        return any(indicator in url.lower() for indicator in spa_indicators)
