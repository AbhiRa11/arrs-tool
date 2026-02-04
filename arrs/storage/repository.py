"""Repository layer for data access."""
import uuid
from datetime import datetime
from typing import List, Optional
from arrs.models.analysis import Analysis, AnalysisStatus
from arrs.models.crawled_content import CrawledContent
from arrs.models.score_result import EngineScore, Gap
from arrs.models.simulation_result import SimulationResult
from arrs.storage.database import Database, serialize_json_field, deserialize_json_field
from arrs.storage.json_store import JSONStore
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class Repository:
    """Data access repository combining database and JSON storage."""

    def __init__(self, database: Database, json_store: JSONStore):
        """
        Initialize repository.

        Args:
            database: Database instance
            json_store: JSON store instance
        """
        self.db = database
        self.json_store = json_store

    # Analysis operations
    async def create_analysis(self, url: str) -> Analysis:
        """
        Create a new analysis.

        Args:
            url: URL to analyze

        Returns:
            Created analysis
        """
        analysis = Analysis(
            id=str(uuid.uuid4()),
            url=url,
            created_at=datetime.now(),
            status=AnalysisStatus.PENDING
        )

        await self.db.execute(
            """INSERT INTO analyses (id, url, created_at, status, composite_score, metadata, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                analysis.id,
                analysis.url,
                analysis.created_at.isoformat(),
                analysis.status.value,
                analysis.composite_score,
                serialize_json_field(analysis.metadata),
                analysis.error_message
            )
        )

        logger.info("Created analysis", extra={"analysis_id": analysis.id, "url": url})
        return analysis

    async def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        """
        Get analysis by ID.

        Args:
            analysis_id: Analysis ID

        Returns:
            Analysis or None
        """
        row = await self.db.fetch_one(
            "SELECT * FROM analyses WHERE id = ?",
            (analysis_id,)
        )

        if not row:
            return None

        return Analysis(
            id=row["id"],
            url=row["url"],
            created_at=datetime.fromisoformat(row["created_at"]),
            status=AnalysisStatus(row["status"]),
            composite_score=row["composite_score"],
            metadata=deserialize_json_field(row["metadata"]),
            error_message=row["error_message"]
        )

    async def update_analysis_status(self, analysis_id: str, status: AnalysisStatus, error_message: Optional[str] = None):
        """Update analysis status."""
        await self.db.execute(
            "UPDATE analyses SET status = ?, error_message = ? WHERE id = ?",
            (status.value, error_message, analysis_id)
        )
        logger.info("Updated analysis status", extra={"analysis_id": analysis_id, "status": status.value})

    async def update_composite_score(self, analysis_id: str, score: float):
        """Update composite score."""
        await self.db.execute(
            "UPDATE analyses SET composite_score = ? WHERE id = ?",
            (score, analysis_id)
        )
        logger.info("Updated composite score", extra={"analysis_id": analysis_id, "score": score})

    # Crawled content operations
    async def save_crawled_content(self, content: CrawledContent):
        """Save crawled content."""
        await self.db.execute(
            """INSERT INTO crawled_pages (id, analysis_id, url, html_content, crawled_at, crawl_method, status_code)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                content.id,
                content.analysis_id,
                content.url,
                content.html_content[:50000],  # Store first 50KB in DB
                content.crawled_at.isoformat(),
                content.crawl_method,
                content.status_code
            )
        )

        # Save full HTML to JSON
        self.json_store.save_raw_content(content.analysis_id, f"{content.id}.html", content.html_content)

        logger.info("Saved crawled content", extra={"analysis_id": content.analysis_id, "url": content.url})

    async def get_crawled_content(self, analysis_id: str) -> Optional[CrawledContent]:
        """Get crawled content for analysis."""
        row = await self.db.fetch_one(
            "SELECT * FROM crawled_pages WHERE analysis_id = ? LIMIT 1",
            (analysis_id,)
        )

        if not row:
            return None

        # Load full HTML from JSON
        full_html = self.json_store.load_raw_content(analysis_id, f"{row['id']}.html")

        return CrawledContent(
            id=row["id"],
            analysis_id=row["analysis_id"],
            url=row["url"],
            html_content=full_html or row["html_content"],
            crawled_at=datetime.fromisoformat(row["crawled_at"]),
            crawl_method=row["crawl_method"],
            status_code=row["status_code"]
        )

    # Engine score operations
    async def save_engine_score(self, score: EngineScore):
        """Save engine score."""
        await self.db.execute(
            """INSERT INTO engine_scores (id, analysis_id, engine_name, score, weight, details, calculated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                score.id,
                score.analysis_id,
                score.engine_name,
                score.score,
                score.weight,
                serialize_json_field(score.details),
                score.calculated_at.isoformat()
            )
        )

        logger.info("Saved engine score", extra={
            "analysis_id": score.analysis_id,
            "engine": score.engine_name,
            "score": score.score
        })

    async def get_engine_scores(self, analysis_id: str) -> List[EngineScore]:
        """Get all engine scores for analysis."""
        rows = await self.db.fetch_all(
            "SELECT * FROM engine_scores WHERE analysis_id = ?",
            (analysis_id,)
        )

        return [
            EngineScore(
                id=row["id"],
                analysis_id=row["analysis_id"],
                engine_name=row["engine_name"],
                score=row["score"],
                weight=row["weight"],
                details=deserialize_json_field(row["details"]),
                calculated_at=datetime.fromisoformat(row["calculated_at"])
            )
            for row in rows
        ]

    # Simulation operations
    async def save_simulation_result(self, result: SimulationResult):
        """Save simulation result."""
        await self.db.execute(
            """INSERT INTO simulation_results
               (id, analysis_id, prompt, response, brand_cited, citation_count, missing_signals, simulated_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result.id,
                result.analysis_id,
                result.prompt,
                result.response,
                1 if result.brand_cited else 0,
                result.citation_count,
                serialize_json_field(result.missing_signals),
                result.simulated_at.isoformat(),
                serialize_json_field(result.metadata)
            )
        )

        # Also save to JSON
        self.json_store.save_simulation_data(result.analysis_id, result.to_dict())

        logger.info("Saved simulation result", extra={
            "analysis_id": result.analysis_id,
            "brand_cited": result.brand_cited
        })

    async def get_simulation_result(self, analysis_id: str) -> Optional[SimulationResult]:
        """Get simulation result for analysis."""
        row = await self.db.fetch_one(
            "SELECT * FROM simulation_results WHERE analysis_id = ? LIMIT 1",
            (analysis_id,)
        )

        if not row:
            return None

        return SimulationResult(
            id=row["id"],
            analysis_id=row["analysis_id"],
            prompt=row["prompt"],
            response=row["response"],
            brand_cited=bool(row["brand_cited"]),
            citation_count=row["citation_count"],
            missing_signals=deserialize_json_field(row["missing_signals"]),
            simulated_at=datetime.fromisoformat(row["simulated_at"]),
            metadata=deserialize_json_field(row["metadata"])
        )

    # Gap operations
    async def save_gap(self, gap: Gap):
        """Save identified gap."""
        await self.db.execute(
            """INSERT INTO gaps (id, analysis_id, gap_type, severity, description, recommendation, engine_source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                gap.id,
                gap.analysis_id,
                gap.gap_type,
                gap.severity,
                gap.description,
                gap.recommendation,
                gap.engine_source
            )
        )

    async def save_gaps(self, gaps: List[Gap]):
        """Save multiple gaps."""
        if not gaps:
            return

        await self.db.executemany(
            """INSERT INTO gaps (id, analysis_id, gap_type, severity, description, recommendation, engine_source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (g.id, g.analysis_id, g.gap_type, g.severity, g.description, g.recommendation, g.engine_source)
                for g in gaps
            ]
        )

        logger.info("Saved gaps", extra={"count": len(gaps)})

    async def get_gaps(self, analysis_id: str) -> List[Gap]:
        """Get all gaps for analysis."""
        rows = await self.db.fetch_all(
            "SELECT * FROM gaps WHERE analysis_id = ? ORDER BY severity",
            (analysis_id,)
        )

        return [
            Gap(
                id=row["id"],
                analysis_id=row["analysis_id"],
                gap_type=row["gap_type"],
                severity=row["severity"],
                description=row["description"],
                recommendation=row["recommendation"],
                engine_source=row["engine_source"]
            )
            for row in rows
        ]
