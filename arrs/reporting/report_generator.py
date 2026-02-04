"""Report generation for ARRS analysis results."""
from typing import Dict, Any, List
from datetime import datetime
from arrs.storage.repository import Repository
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """Generate comprehensive analysis reports."""

    def __init__(self, repository: Repository):
        """
        Initialize report generator.

        Args:
            repository: Data repository
        """
        self.repository = repository

    async def generate_report(self, analysis_id: str) -> Dict[str, Any]:
        """
        Generate complete analysis report.

        Args:
            analysis_id: Analysis ID

        Returns:
            Complete report dictionary
        """
        logger.info("Generating report", extra={"analysis_id": analysis_id})

        # Get all data
        analysis = await self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        engine_scores = await self.repository.get_engine_scores(analysis_id)
        gaps = await self.repository.get_gaps(analysis_id)
        simulation = await self.repository.get_simulation_result(analysis_id)

        # Build report
        report = {
            "analysis_id": analysis.id,
            "url": analysis.url,
            "timestamp": datetime.now().isoformat(),
            "status": analysis.status.value,
            "composite_score": analysis.composite_score,
            "grade": self._score_to_grade(analysis.composite_score or 0),
            "engine_scores": self._format_engine_scores(engine_scores),
            "gaps": self._format_gaps(gaps),
            "summary": self._generate_summary(analysis, engine_scores, gaps, simulation),
            "simulation_results": self._format_simulation(simulation) if simulation else None,
            "recommendations": self._prioritize_recommendations(gaps)
        }

        logger.info("Report generated", extra={"analysis_id": analysis_id})

        return report

    def _format_engine_scores(self, scores: List) -> Dict[str, Any]:
        """Format engine scores for report."""
        formatted = {}

        for score in scores:
            formatted[score.engine_name] = {
                "score": round(score.score, 2),
                "weight": score.weight,
                "grade": self._score_to_grade(score.score),
                "details": score.details
            }

        return formatted

    def _format_gaps(self, gaps: List) -> List[Dict[str, Any]]:
        """Format gaps for report."""
        return [
            {
                "type": gap.gap_type,
                "severity": gap.severity,
                "description": gap.description,
                "recommendation": gap.recommendation,
                "engine_source": gap.engine_source
            }
            for gap in gaps
        ]

    def _format_simulation(self, simulation) -> Dict[str, Any]:
        """Format simulation results."""
        return {
            "brand_cited": simulation.brand_cited,
            "citation_count": simulation.citation_count,
            "missing_signals": simulation.missing_signals,
            "prompt": simulation.prompt,
            "response": simulation.response,
            "metadata": simulation.metadata
        }

    def _generate_summary(
        self,
        analysis,
        scores: List,
        gaps: List,
        simulation
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        composite_score = analysis.composite_score or 0

        # Count gaps by severity
        gap_counts = {
            "critical": sum(1 for g in gaps if g.severity == "critical"),
            "high": sum(1 for g in gaps if g.severity == "high"),
            "medium": sum(1 for g in gaps if g.severity == "medium"),
            "low": sum(1 for g in gaps if g.severity == "low")
        }

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        for score in scores:
            if score.score >= 75:
                strengths.append(score.engine_name)
            elif score.score < 50:
                weaknesses.append(score.engine_name)

        return {
            "composite_score": composite_score,
            "grade": self._score_to_grade(composite_score),
            "interpretation": self._interpret_score(composite_score),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "total_gaps": len(gaps),
            "gaps_by_severity": gap_counts,
            "ai_citation_status": "cited" if (simulation and simulation.brand_cited) else "not_cited" if simulation else "not_tested",
            "readiness_for_ai_commerce": self._assess_ai_readiness(composite_score, simulation)
        }

    def _prioritize_recommendations(self, gaps: List) -> List[Dict[str, Any]]:
        """Prioritize recommendations by impact."""
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        sorted_gaps = sorted(
            gaps,
            key=lambda g: severity_order.get(g.severity, 99)
        )

        # Return top 10 prioritized recommendations
        return [
            {
                "priority": idx + 1,
                "severity": gap.severity,
                "issue": gap.description,
                "action": gap.recommendation,
                "impact": "High" if gap.severity in ["critical", "high"] else "Medium"
            }
            for idx, gap in enumerate(sorted_gaps[:10])
        ]

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _interpret_score(self, score: float) -> str:
        """Interpret composite score."""
        if score >= 90:
            return "Excellent - Highly optimized for AI recommendations"
        elif score >= 80:
            return "Very Good - Well-positioned for AI citations"
        elif score >= 70:
            return "Good - Decent AI readability with room for improvement"
        elif score >= 60:
            return "Fair - Moderate AI understanding, needs optimization"
        elif score >= 50:
            return "Poor - Limited AI comprehension, significant gaps"
        else:
            return "Critical - Major barriers to AI recommendations"

    def _assess_ai_readiness(self, score: float, simulation) -> str:
        """Assess readiness for agentic commerce."""
        if not simulation:
            return "Not tested"

        if score >= 80 and simulation.brand_cited:
            return "Ready - High confidence for AI-led transactions"
        elif score >= 70 and simulation.brand_cited:
            return "Mostly Ready - Good foundation with minor improvements needed"
        elif score >= 60:
            return "Partially Ready - Needs optimization for reliable AI recommendations"
        else:
            return "Not Ready - Significant improvements required"

    async def export_json(self, analysis_id: str, filepath: str):
        """
        Export report to JSON file.

        Args:
            analysis_id: Analysis ID
            filepath: Output file path
        """
        import json

        report = await self.generate_report(analysis_id)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("Report exported", extra={"analysis_id": analysis_id, "filepath": filepath})
