"""Data models for crawled content."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class CrawledContent:
    """Crawled page content model."""
    id: str
    analysis_id: str
    url: str
    html_content: str
    crawled_at: datetime
    crawl_method: str  # 'beautifulsoup' or 'playwright'
    status_code: int

    # Parsed content (populated by parsers)
    text_content: Optional[str] = None
    schema_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    headings: List[Dict[str, str]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "url": self.url,
            "html_content": self.html_content,
            "crawled_at": self.crawled_at.isoformat(),
            "crawl_method": self.crawl_method,
            "status_code": self.status_code,
            "text_content": self.text_content,
            "schema_data": self.schema_data,
            "metadata": self.metadata,
            "headings": self.headings,
            "links": self.links,
            "images": self.images
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawledContent':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            analysis_id=data["analysis_id"],
            url=data["url"],
            html_content=data["html_content"],
            crawled_at=datetime.fromisoformat(data["crawled_at"]),
            crawl_method=data["crawl_method"],
            status_code=data["status_code"],
            text_content=data.get("text_content"),
            schema_data=data.get("schema_data", {}),
            metadata=data.get("metadata", {}),
            headings=data.get("headings", []),
            links=data.get("links", []),
            images=data.get("images", [])
        )
