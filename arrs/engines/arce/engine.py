"""AI Readability & Composability Engine (ARCE) - 20% weight.

Measures how easily an LLM can extract, summarize, and reuse content.
"""
from typing import Dict, List, Any
import textstat
from arrs.engines.base.engine import BaseEngine
from arrs.engines.base.scoring_utils import calculate_ratio_score, count_semantic_html_tags
from arrs.models.score_result import EngineScore, Gap
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class ARCEEngine(BaseEngine):
    """AI Readability & Composability Engine."""

    async def analyze(self, content: CrawledContent, parsed_data: Dict[str, Any]) -> EngineScore:
        """
        Analyze AI readability and composability.

        Scoring breakdown:
        - Semantic HTML usage: 30 points
        - Flesch readability score: 25 points
        - Heading hierarchy quality: 25 points
        - Metadata completeness: 20 points
        Total: 100 points

        Args:
            content: Crawled content
            parsed_data: Parsed data

        Returns:
            Engine score
        """
        logger.info(f"Running ARCE analysis", extra={"analysis_id": content.analysis_id})

        html_data = parsed_data.get('html', {})

        # 1. Semantic HTML usage (30 points)
        semantic_score = self._score_semantic_html(html_data)

        # 2. Readability (25 points)
        readability_score = self._score_readability(html_data)

        # 3. Heading hierarchy (25 points)
        hierarchy_score = self._score_heading_hierarchy(html_data)

        # 4. Metadata completeness (20 points)
        metadata_score = self._score_metadata(html_data)

        # Calculate total score
        total_score = semantic_score + readability_score + hierarchy_score + metadata_score

        details = {
            "semantic_html_score": semantic_score,
            "readability_score": readability_score,
            "heading_hierarchy_score": hierarchy_score,
            "metadata_score": metadata_score,
            "semantic_element_count": count_semantic_html_tags(html_data),
            "flesch_reading_ease": self._calculate_flesch_score(html_data.get('text_content', '')),
            "has_valid_hierarchy": html_data.get('heading_validation', {}).get('valid_hierarchy', False),
            "word_count": html_data.get('word_count', 0)
        }

        logger.info(f"ARCE analysis complete", extra={
            "analysis_id": content.analysis_id,
            "score": total_score
        })

        return self.create_score(content.analysis_id, total_score, details)

    def _score_semantic_html(self, html_data: Dict[str, Any]) -> float:
        """Score semantic HTML usage (30 points max)."""
        semantic_count = count_semantic_html_tags(html_data)

        # Good semantic structure has at least 10 semantic elements
        score = min(30.0, semantic_count * 3.0)
        return score

    def _score_readability(self, html_data: Dict[str, Any]) -> float:
        """Score readability (25 points max)."""
        text = html_data.get('text_content', '')

        if not text or len(text) < 100:
            return 0.0

        flesch_score = self._calculate_flesch_score(text)

        # Flesch Reading Ease: 0-100 scale
        # 60-70 is ideal (plain English)
        # Normalize to 0-25 points
        if flesch_score >= 60:
            # Good readability
            return 25.0
        elif flesch_score >= 30:
            # Acceptable readability
            return (flesch_score / 60) * 25.0
        else:
            # Poor readability
            return (flesch_score / 30) * 12.5

    def _calculate_flesch_score(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""
        try:
            return textstat.flesch_reading_ease(text)
        except Exception:
            return 0.0

    def _score_heading_hierarchy(self, html_data: Dict[str, Any]) -> float:
        """Score heading hierarchy quality (25 points max)."""
        validation = html_data.get('heading_validation', {})

        score = 0.0

        # Has H1 (10 points)
        if validation.get('has_h1', False):
            score += 10.0

        # Single H1 (not multiple) (10 points)
        if not validation.get('multiple_h1', True):
            score += 10.0

        # No skipped levels (5 points)
        if not validation.get('skipped_levels', []):
            score += 5.0

        return score

    def _score_metadata(self, html_data: Dict[str, Any]) -> float:
        """Score metadata completeness (20 points max)."""
        metadata = html_data.get('metadata', {})

        score = 0.0

        # Title (5 points)
        if html_data.get('title'):
            score += 5.0

        # Meta description (5 points)
        if html_data.get('meta_description'):
            score += 5.0

        # Open Graph (5 points)
        og_tags = [k for k in metadata.keys() if k.startswith('og_')]
        if len(og_tags) >= 3:
            score += 5.0

        # Canonical URL (5 points)
        if metadata.get('canonical_url'):
            score += 5.0

        return score

    async def identify_gaps(self, score: EngineScore, parsed_data: Dict[str, Any]) -> List[Gap]:
        """Identify readability and composability gaps."""
        gaps = []
        analysis_id = score.analysis_id

        html_data = parsed_data.get('html', {})

        # Check semantic HTML usage
        semantic_count = count_semantic_html_tags(html_data)
        if semantic_count < 5:
            gaps.append(self.create_gap(
                analysis_id,
                "low_semantic_html",
                "medium",
                f"Only {semantic_count} semantic HTML elements found",
                "Use semantic HTML5 elements (article, section, header, main) to improve AI content understanding"
            ))

        # Check heading hierarchy
        validation = html_data.get('heading_validation', {})
        if not validation.get('has_h1'):
            gaps.append(self.create_gap(
                analysis_id,
                "missing_h1",
                "high",
                "Page missing H1 heading",
                "Add a clear H1 heading that describes the page content"
            ))

        if validation.get('multiple_h1'):
            gaps.append(self.create_gap(
                analysis_id,
                "multiple_h1",
                "medium",
                "Page has multiple H1 headings",
                "Use only one H1 heading per page for clear content hierarchy"
            ))

        # Check readability
        flesch_score = score.details.get('flesch_reading_ease', 0)
        if flesch_score < 30:
            gaps.append(self.create_gap(
                analysis_id,
                "poor_readability",
                "medium",
                f"Content has poor readability (Flesch score: {flesch_score:.1f})",
                "Simplify sentences and use clearer language to improve AI comprehension"
            ))

        # Check metadata
        if not html_data.get('meta_description'):
            gaps.append(self.create_gap(
                analysis_id,
                "missing_meta_description",
                "medium",
                "Meta description is missing",
                "Add a meta description (150-160 characters) summarizing the page content"
            ))

        return gaps
