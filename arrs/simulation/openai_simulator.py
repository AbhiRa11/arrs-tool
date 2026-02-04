"""OpenAI API integration for AI simulation."""
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

from arrs.simulation.citation_analyzer import CitationAnalyzer
from arrs.simulation.prompt_templates import get_recommendation_prompt
from arrs.storage.repository import Repository

logger = logging.getLogger(__name__)


class OpenAISimulator:
    """Simulates AI recommendations using OpenAI's GPT models."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        repository: Optional[Repository] = None
    ):
        """
        Initialize OpenAI simulator.

        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            repository: Repository for data persistence
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.repository = repository
        self.citation_analyzer = CitationAnalyzer()
        logger.info(f"OpenAI simulator initialized with model: {model}")

    async def simulate_recommendation(
        self,
        analysis_id: str,
        brand: Optional[str] = None,
        product_category: Optional[str] = None,
        use_case: Optional[str] = None,
        parsed_content: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate AI recommendation using OpenAI's API.

        Args:
            analysis_id: ID of the analysis
            brand: Brand name to test
            product_category: Product category
            use_case: Use case description
            parsed_content: Parsed content from the website

        Returns:
            Dict with simulation results
        """
        if not brand or not product_category or not use_case:
            logger.warning("Missing required fields for simulation")
            return {
                "brand_cited": False,
                "citation_count": 0,
                "missing_signals": [],
                "prompt": "",
                "response": "Simulation skipped - missing brand, category, or use case"
            }

        try:
            # Generate prompt
            prompt = get_recommendation_prompt(
                product_category=product_category,
                use_case=use_case
            )

            logger.info(f"Querying OpenAI {self.model} for recommendations...")

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful shopping assistant that recommends products based on user needs. Provide specific brand and product recommendations with detailed reasoning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Extract response text
            response_text = response.choices[0].message.content

            logger.info(f"OpenAI response received ({len(response_text)} chars)")

            # Analyze citation
            citation_analysis = self.citation_analyzer.analyze_citation(
                response_text,
                brand
            )

            # Identify missing signals
            missing_signals = self._identify_missing_signals(
                response_text,
                parsed_content or {}
            )

            result = {
                "brand_cited": citation_analysis["cited"],
                "citation_count": citation_analysis["count"],
                "missing_signals": missing_signals,
                "prompt": prompt,
                "response": response_text,
                "model": self.model
            }

            # Save to repository if available
            if self.repository:
                await self.repository.save_simulation_result(
                    analysis_id=analysis_id,
                    prompt=prompt,
                    response=response_text,
                    brand_cited=citation_analysis["cited"],
                    citation_count=citation_analysis["count"],
                    missing_signals=missing_signals
                )

            return result

        except Exception as e:
            logger.error(f"OpenAI simulation failed: {e}")
            return {
                "brand_cited": False,
                "citation_count": 0,
                "missing_signals": [],
                "prompt": prompt if 'prompt' in locals() else "",
                "response": f"Error: {str(e)}",
                "error": str(e)
            }

    def _identify_missing_signals(
        self,
        response: str,
        parsed_content: Dict[str, Any]
    ) -> list:
        """
        Identify signals mentioned by AI but missing from content.

        Args:
            response: AI response text
            parsed_content: Parsed website content

        Returns:
            List of missing signal descriptions
        """
        missing = []

        # Common signals to check
        signals = {
            "warranty": ["warranty", "guarantee"],
            "return_policy": ["return policy", "returns", "refund"],
            "reviews": ["reviews", "ratings", "customer feedback"],
            "specifications": ["specs", "specifications", "technical details"],
            "size_guide": ["size guide", "sizing", "fit guide"],
            "shipping": ["shipping", "delivery", "freight"],
            "price": ["price", "cost", "$"],
            "availability": ["in stock", "available", "availability"]
        }

        # Check which signals are mentioned in response but missing in content
        for signal_name, keywords in signals.items():
            mentioned_in_response = any(
                keyword.lower() in response.lower()
                for keyword in keywords
            )

            if mentioned_in_response:
                # Check if present in parsed content
                content_str = str(parsed_content).lower()
                found_in_content = any(
                    keyword.lower() in content_str
                    for keyword in keywords
                )

                if not found_in_content:
                    missing.append(signal_name.replace("_", " ").title())

        return missing
