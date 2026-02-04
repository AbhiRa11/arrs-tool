"""Base engine interface for all scoring engines."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import uuid
from datetime import datetime
from arrs.models.score_result import EngineScore, Gap
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseEngine(ABC):
    """Abstract base class for all scoring engines."""

    def __init__(self, weight: float):
        """
        Initialize engine.

        Args:
            weight: Engine weight in composite score (0.0-1.0)
        """
        self.name = self.__class__.__name__.replace("Engine", "")
        self.weight = weight
        logger.info(f"Initialized {self.name} engine", extra={"weight": weight})

    @abstractmethod
    async def analyze(self, content: CrawledContent, parsed_data: Dict[str, Any]) -> EngineScore:
        """
        Analyze content and generate score.

        Args:
            content: Crawled content
            parsed_data: Parsed HTML and schema data

        Returns:
            Engine score result

        Raises:
            Exception: If analysis fails
        """
        pass

    @abstractmethod
    async def identify_gaps(self, score: EngineScore, parsed_data: Dict[str, Any]) -> List[Gap]:
        """
        Identify gaps and generate recommendations.

        Args:
            score: Engine score
            parsed_data: Parsed data

        Returns:
            List of identified gaps
        """
        pass

    def normalize_score(self, raw_score: float, max_score: float) -> float:
        """
        Normalize score to 0-100 range.

        Args:
            raw_score: Raw score value
            max_score: Maximum possible score

        Returns:
            Normalized score (0-100)
        """
        if max_score == 0:
            return 0.0

        normalized = (raw_score / max_score) * 100
        return min(100.0, max(0.0, normalized))

    def create_score(self, analysis_id: str, score: float, details: Dict[str, Any]) -> EngineScore:
        """
        Create an EngineScore object.

        Args:
            analysis_id: Analysis ID
            score: Calculated score (0-100)
            details: Detailed metrics

        Returns:
            EngineScore object
        """
        return EngineScore(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            engine_name=self.name,
            score=score,
            weight=self.weight,
            details=details,
            calculated_at=datetime.now()
        )

    def create_gap(
        self,
        analysis_id: str,
        gap_type: str,
        severity: str,
        description: str,
        recommendation: str
    ) -> Gap:
        """
        Create a Gap object.

        Args:
            analysis_id: Analysis ID
            gap_type: Type of gap
            severity: Severity level (critical, high, medium, low)
            description: Gap description
            recommendation: Recommended action

        Returns:
            Gap object
        """
        return Gap(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            gap_type=gap_type,
            severity=severity,
            description=description,
            recommendation=recommendation,
            engine_source=self.name
        )
