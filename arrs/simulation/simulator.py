"""Claude AI simulator for testing recommendation behavior."""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from anthropic import Anthropic
from arrs.models.simulation_result import SimulationResult
from arrs.simulation.prompt_templates import (
    get_recommendation_prompt,
    get_attribute_extraction_prompt
)
from arrs.simulation.citation_analyzer import CitationAnalyzer
from arrs.utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class ClaudeSimulator:
    """Claude AI simulator for recommendation testing."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude simulator.

        Args:
            api_key: Anthropic API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.citation_analyzer = CitationAnalyzer()

    async def simulate_recommendation(
        self,
        analysis_id: str,
        brand: str,
        product_category: str,
        use_case: str
    ) -> SimulationResult:
        """
        Simulate AI recommendation and check for brand citation.

        Args:
            analysis_id: Analysis ID
            brand: Brand name to check for
            product_category: Product category
            use_case: Use case scenario

        Returns:
            Simulation result
        """
        logger.info("Starting recommendation simulation", extra={
            "analysis_id": analysis_id,
            "brand": brand,
            "category": product_category
        })

        # Generate prompt
        prompt = get_recommendation_prompt(product_category, use_case)

        # Query Claude
        response = await self._query_claude(prompt)

        # Analyze citation
        citation_analysis = self.citation_analyzer.analyze_citation(response, brand)

        # Identify missing signals
        missing_signals = await self._identify_missing_signals(brand, product_category, response)

        result = SimulationResult(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            prompt=prompt,
            response=response,
            brand_cited=citation_analysis["cited"],
            citation_count=citation_analysis["count"],
            missing_signals=missing_signals,
            simulated_at=datetime.now(),
            metadata={
                "product_category": product_category,
                "use_case": use_case,
                "brand": brand,
                "citation_context": citation_analysis.get("contexts", [])
            }
        )

        logger.info("Simulation complete", extra={
            "analysis_id": analysis_id,
            "brand_cited": result.brand_cited,
            "citation_count": result.citation_count
        })

        return result

    async def _query_claude(self, prompt: str) -> str:
        """
        Query Claude API.

        Args:
            prompt: Prompt text

        Returns:
            Claude's response
        """
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            return response_text

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def _identify_missing_signals(
        self,
        brand: str,
        product_category: str,
        recommendation_response: str
    ) -> list:
        """
        Identify what attributes Claude wanted but might be missing.

        Args:
            brand: Brand name
            product_category: Product category
            recommendation_response: Claude's recommendation response

        Returns:
            List of missing signals/attributes
        """
        # Ask Claude what attributes it values
        prompt = get_attribute_extraction_prompt(brand, product_category)

        try:
            response = await self._query_claude(prompt)

            # Extract key attributes mentioned
            missing_signals = self.citation_analyzer.extract_important_attributes(response)

            return missing_signals

        except Exception as e:
            logger.warning(f"Failed to identify missing signals: {e}")
            return []

    async def test_with_context(
        self,
        analysis_id: str,
        brand: str,
        product_category: str,
        use_case: str,
        site_content: str
    ) -> SimulationResult:
        """
        Test recommendation with site content as context.

        Args:
            analysis_id: Analysis ID
            brand: Brand name
            product_category: Product category
            use_case: Use case
            site_content: Site content to provide as context

        Returns:
            Simulation result
        """
        # Enhanced prompt with context
        prompt = f"""You are helping a customer find the best {product_category} for {use_case}.

Here is information about {brand}:
{site_content[:2000]}  # Limit context to avoid token limits

Based on this information and your knowledge, would you recommend {brand}'s {product_category}
for {use_case}? Why or why not?

Also provide 2-3 alternative recommendations with reasoning."""

        response = await self._query_claude(prompt)

        citation_analysis = self.citation_analyzer.analyze_citation(response, brand)

        return SimulationResult(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            prompt=prompt,
            response=response,
            brand_cited=citation_analysis["cited"],
            citation_count=citation_analysis["count"],
            missing_signals=[],
            simulated_at=datetime.now(),
            metadata={
                "simulation_type": "with_context",
                "product_category": product_category,
                "use_case": use_case,
                "brand": brand
            }
        )
