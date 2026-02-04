"""Content cleaning and normalization utilities."""
import re
from bs4 import BeautifulSoup
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentCleaner:
    """Clean and normalize HTML content."""

    @staticmethod
    def remove_scripts_and_styles(html: str) -> str:
        """
        Remove script and style tags from HTML.

        Args:
            html: Raw HTML

        Returns:
            Cleaned HTML
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for element in soup(['script', 'style', 'noscript']):
            element.decompose()

        return str(soup)

    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extract clean text from HTML.

        Args:
            html: Raw HTML

        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
            element.decompose()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def extract_main_content(html: str) -> str:
        """
        Extract main content area from HTML.

        Args:
            html: Raw HTML

        Returns:
            Main content HTML
        """
        soup = BeautifulSoup(html, 'lxml')

        # Try to find main content area
        main_content = None

        # Look for semantic HTML5 elements
        for tag in ['main', 'article', '[role="main"]']:
            main_content = soup.select_one(tag)
            if main_content:
                break

        # Fallback: Look for content-indicating IDs/classes
        if not main_content:
            for selector in ['#main', '#content', '.main-content', '.content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break

        # If still not found, use body
        if not main_content:
            main_content = soup.body

        return str(main_content) if main_content else html

    @staticmethod
    def remove_html_comments(html: str) -> str:
        """
        Remove HTML comments.

        Args:
            html: Raw HTML

        Returns:
            HTML without comments
        """
        return re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
