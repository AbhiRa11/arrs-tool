"""Data models for AI simulation results."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class SimulationResult:
    """AI simulation result model."""
    id: str
    analysis_id: str
    prompt: str
    response: str
    brand_cited: bool
    citation_count: int
    missing_signals: List[str] = field(default_factory=list)
    simulated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "prompt": self.prompt,
            "response": self.response,
            "brand_cited": self.brand_cited,
            "citation_count": self.citation_count,
            "missing_signals": self.missing_signals,
            "simulated_at": self.simulated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationResult':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            analysis_id=data["analysis_id"],
            prompt=data["prompt"],
            response=data["response"],
            brand_cited=data["brand_cited"],
            citation_count=data["citation_count"],
            missing_signals=data.get("missing_signals", []),
            simulated_at=datetime.fromisoformat(data["simulated_at"]),
            metadata=data.get("metadata", {})
        )
