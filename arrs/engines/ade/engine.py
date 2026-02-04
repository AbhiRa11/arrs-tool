"""Attribute Density Engine (ADE) - 30% weight.

Measures how richly and clearly product attributes are defined.
"""
from typing import Dict, List, Any
from arrs.engines.base.engine import BaseEngine
from arrs.engines.base.scoring_utils import calculate_completeness_score, calculate_richness_score
from arrs.models.score_result import EngineScore, Gap
from arrs.models.crawled_content import CrawledContent
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class ADEEngine(BaseEngine):
    """Attribute Density Engine."""

    async def analyze(self, content: CrawledContent, parsed_data: Dict[str, Any]) -> EngineScore:
        """
        Analyze attribute density.

        Scoring breakdown:
        - Schema.org Product completeness: 40 points
        - Attribute richness (description length): 30 points
        - Image quality indicators: 20 points
        - Technical specs depth: 10 points
        Total: 100 points

        Args:
            content: Crawled content
            parsed_data: Parsed data

        Returns:
            Engine score
        """
        logger.info(f"Running ADE analysis", extra={"analysis_id": content.analysis_id})

        schema_data = parsed_data.get('schema', {})
        html_data = parsed_data.get('html', {})

        # 1. Schema completeness (40 points)
        schema_score = self._score_schema_completeness(schema_data)

        # 2. Attribute richness (30 points)
        richness_score = self._score_attribute_richness(schema_data, html_data)

        # 3. Image quality (20 points)
        image_score = self._score_image_quality(schema_data, html_data)

        # 4. Technical specs (10 points)
        specs_score = self._score_technical_specs(html_data)

        # Calculate total score
        total_score = schema_score + richness_score + image_score + specs_score

        details = {
            "schema_completeness_score": schema_score,
            "attribute_richness_score": richness_score,
            "image_quality_score": image_score,
            "technical_specs_score": specs_score,
            "product_schema_present": schema_data.get('product_validation', {}).get('present', False),
            "schema_field_count": schema_data.get('product_validation', {}).get('field_count', 0),
            "description_length": len(schema_data.get('product', {}).get('description', '')),
            "image_count": len(html_data.get('images', []))
        }

        logger.info(f"ADE analysis complete", extra={
            "analysis_id": content.analysis_id,
            "score": total_score
        })

        return self.create_score(content.analysis_id, total_score, details)

    def _score_schema_completeness(self, schema_data: Dict[str, Any]) -> float:
        """Score Product schema completeness (40 points max)."""
        validation = schema_data.get('product_validation', {})

        if not validation.get('present', False):
            return 0.0

        completeness = validation.get('completeness', 0.0)
        return completeness * 40.0

    def _score_attribute_richness(self, schema_data: Dict[str, Any], html_data: Dict[str, Any]) -> float:
        """Score attribute richness (30 points max)."""
        product = schema_data.get('product', {})

        # Check description length
        description = product.get('description', '') or html_data.get('meta_description', '')
        desc_score = calculate_richness_score(description, benchmark_chars=300, max_points=15.0)

        # Check for detailed attributes
        has_brand = bool(schema_data.get('brand'))
        has_sku = bool(product.get('sku') or product.get('gtin') or product.get('mpn'))

        attribute_score = 0.0
        if has_brand:
            attribute_score += 7.5
        if has_sku:
            attribute_score += 7.5

        return desc_score + attribute_score

    def _score_image_quality(self, schema_data: Dict[str, Any], html_data: Dict[str, Any]) -> float:
        """Score image quality indicators (20 points max)."""
        images = html_data.get('images', [])
        product = schema_data.get('product', {})

        if not images:
            return 0.0

        # Image count (10 points)
        image_count_score = min(10.0, len(images) * 2.5)  # Max at 4 images

        # Alt text presence (10 points)
        images_with_alt = sum(1 for img in images if img.get('alt'))
        alt_ratio = images_with_alt / len(images) if images else 0
        alt_score = alt_ratio * 10.0

        return image_count_score + alt_score

    def _score_technical_specs(self, html_data: Dict[str, Any]) -> float:
        """Score technical specification depth (10 points max)."""
        text = html_data.get('text_content', '').lower()

        # Look for spec indicators
        spec_keywords = [
            'specification', 'dimensions', 'weight', 'material',
            'features', 'technical', 'details', 'capacity', 'size'
        ]

        spec_mentions = sum(1 for keyword in spec_keywords if keyword in text)

        # Max score at 5 or more spec mentions
        return min(10.0, spec_mentions * 2.0)

    async def identify_gaps(self, score: EngineScore, parsed_data: Dict[str, Any]) -> List[Gap]:
        """Identify attribute density gaps."""
        gaps = []
        analysis_id = score.analysis_id

        schema_data = parsed_data.get('schema', {})
        html_data = parsed_data.get('html', {})

        # Check for missing Product schema
        if not schema_data.get('product_validation', {}).get('present'):
            gaps.append(self.create_gap(
                analysis_id,
                "missing_schema",
                "critical",
                "Product schema.org markup is missing",
                "Add Product schema.org markup using JSON-LD format to help AI understand product attributes"
            ))

        # Check for missing fields
        missing_fields = schema_data.get('product_validation', {}).get('missing_fields', [])
        critical_fields = ['name', 'description', 'image', 'offers']

        for field in critical_fields:
            if field in missing_fields:
                gaps.append(self.create_gap(
                    analysis_id,
                    f"missing_field_{field}",
                    "high",
                    f"Product schema missing '{field}' field",
                    f"Add '{field}' to Product schema for better AI attribute extraction"
                ))

        # Check for short description
        desc_length = score.details.get('description_length', 0)
        if desc_length < 100:
            gaps.append(self.create_gap(
                analysis_id,
                "short_description",
                "medium",
                f"Product description is too short ({desc_length} characters)",
                "Expand product description to at least 300 characters with detailed attributes and benefits"
            ))

        # Check for missing images
        image_count = score.details.get('image_count', 0)
        if image_count == 0:
            gaps.append(self.create_gap(
                analysis_id,
                "no_images",
                "high",
                "No product images found",
                "Add product images with descriptive alt text"
            ))

        return gaps
