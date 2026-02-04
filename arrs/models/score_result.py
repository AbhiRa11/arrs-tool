"""Data models for scoring results."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class EngineScore:
    """Individual engine score result."""
    id: str
    analysis_id: str
    engine_name: str
    score: float  # 0-100
    weight: float
    details: Dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "engine_name": self.engine_name,
            "score": self.score,
            "weight": self.weight,
            "details": self.details,
            "calculated_at": self.calculated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngineScore':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            analysis_id=data["analysis_id"],
            engine_name=data["engine_name"],
            score=data["score"],
            weight=data["weight"],
            details=data.get("details", {}),
            calculated_at=datetime.fromisoformat(data["calculated_at"])
        )


@dataclass
class Gap:
    """Identified gap/improvement recommendation."""
    id: str
    analysis_id: str
    gap_type: str
    severity: str  # critical, high, medium, low
    description: str
    recommendation: str
    engine_source: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "gap_type": self.gap_type,
            "severity": self.severity,
            "description": self.description,
            "recommendation": self.recommendation,
            "engine_source": self.engine_source
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gap':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            analysis_id=data["analysis_id"],
            gap_type=data["gap_type"],
            severity=data["severity"],
            description=data["description"],
            recommendation=data["recommendation"],
            engine_source=data["engine_source"]
        )
