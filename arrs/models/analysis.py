"""Data models for analysis sessions."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Analysis:
    """Analysis session model."""
    id: str
    url: str
    created_at: datetime
    status: AnalysisStatus
    composite_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "composite_score": self.composite_score,
            "metadata": self.metadata,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Analysis':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            url=data["url"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=AnalysisStatus(data["status"]),
            composite_score=data.get("composite_score"),
            metadata=data.get("metadata", {}),
            error_message=data.get("error_message")
        )
