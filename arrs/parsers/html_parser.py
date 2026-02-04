"""HTML parsing utilities."""
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class HTMLParser:
    """Parse HTML structure and extract metadata."""

    def __init__(self, html: str, base_url: str):
        """
        Initialize parser.

        Args:
            html: Raw HTML content
            base_url: Base URL for resolving relative links
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'lxml')

    def parse(self) -> Dict[str, Any]:
        """
        Parse HTML and extract all metadata.

        Returns:
            Dictionary of parsed data
        """
        return {
            "title": self.extract_title(),
            "meta_description": self.extract_meta_description(),
            "headings": self.extract_headings(),
            "images": self.extract_images(),
            "links": self.extract_links(),
            "text_content": self.extract_text(),
            "word_count": self.count_words(),
            "has_structured_data": self.has_structured_data(),
            "semantic_elements": self.count_semantic_elements(),
            "metadata": self.extract_metadata()
        }

    def extract_title(self) -> str:
        """Extract page title."""
        title_tag = self.soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""

    def extract_meta_description(self) -> str:
        """Extract meta description."""
        meta = self.soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ""

    def extract_headings(self) -> List[Dict[str, str]]:
        """
        Extract all headings (h1-h6).

        Returns:
            List of heading dictionaries
        """
        headings = []
        for level in range(1, 7):
            for heading in self.soup.find_all(f'h{level}'):
                headings.append({
                    "level": f"h{level}",
                    "text": heading.get_text(strip=True)
                })
        return headings

    def extract_images(self) -> List[Dict[str, str]]:
        """
        Extract image information.

        Returns:
            List of image dictionaries
        """
        images = []
        for img in self.soup.find_all('img'):
            images.append({
                "src": urljoin(self.base_url, img.get('src', '')),
                "alt": img.get('alt', ''),
                "title": img.get('title', ''),
                "width": img.get('width', ''),
                "height": img.get('height', '')
            })
        return images

    def extract_links(self) -> List[str]:
        """
        Extract all links.

        Returns:
            List of URLs
        """
        links = []
        for link in self.soup.find_all('a', href=True):
            url = urljoin(self.base_url, link['href'])
            links.append(url)
        return links

    def extract_text(self) -> str:
        """
        Extract clean text content.

        Returns:
            Clean text
        """
        # Remove scripts and styles
        for element in self.soup(['script', 'style', 'noscript']):
            element.decompose()

        text = self.soup.get_text(separator=' ', strip=True)
        return ' '.join(text.split())  # Normalize whitespace

    def count_words(self) -> int:
        """Count words in text content."""
        text = self.extract_text()
        return len(text.split())

    def has_structured_data(self) -> bool:
        """Check if page has structured data."""
        # Check for JSON-LD
        json_ld = self.soup.find('script', type='application/ld+json')
        if json_ld:
            return True

        # Check for microdata
        microdata = self.soup.find(attrs={'itemscope': True})
        if microdata:
            return True

        # Check for Open Graph
        og = self.soup.find('meta', property=lambda x: x and x.startswith('og:'))
        if og:
            return True

        return False

    def count_semantic_elements(self) -> Dict[str, int]:
        """
        Count semantic HTML5 elements.

        Returns:
            Dictionary of element counts
        """
        semantic_tags = [
            'article', 'section', 'nav', 'aside', 'header', 'footer',
            'main', 'figure', 'figcaption', 'mark', 'time'
        ]

        counts = {}
        for tag in semantic_tags:
            counts[tag] = len(self.soup.find_all(tag))

        return counts

    def extract_metadata(self) -> Dict[str, str]:
        """
        Extract various metadata.

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Open Graph
        for og_tag in self.soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            key = og_tag.get('property', '').replace('og:', '')
            metadata[f"og_{key}"] = og_tag.get('content', '')

        # Twitter Cards
        for twitter_tag in self.soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            key = twitter_tag.get('name', '').replace('twitter:', '')
            metadata[f"twitter_{key}"] = twitter_tag.get('content', '')

        # Canonical URL
        canonical = self.soup.find('link', rel='canonical')
        if canonical:
            metadata['canonical_url'] = canonical.get('href', '')

        return metadata

    def validate_heading_hierarchy(self) -> Dict[str, Any]:
        """
        Validate heading hierarchy.

        Returns:
            Validation results
        """
        headings = [h["level"] for h in self.extract_headings()]

        # Check for h1
        has_h1 = 'h1' in headings
        h1_count = headings.count('h1')

        # Check for skipped levels
        levels = [int(h[1]) for h in headings]
        skipped_levels = []
        if levels:
            for i in range(len(levels) - 1):
                diff = levels[i + 1] - levels[i]
                if diff > 1:
                    skipped_levels.append((levels[i], levels[i + 1]))

        return {
            "has_h1": has_h1,
            "h1_count": h1_count,
            "multiple_h1": h1_count > 1,
            "skipped_levels": skipped_levels,
            "valid_hierarchy": has_h1 and h1_count == 1 and not skipped_levels
        }
