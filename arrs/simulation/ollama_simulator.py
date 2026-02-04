"""Ollama (local LLM) simulator for testing recommendation behavior.

Alternative to Claude API that runs locally without API keys.
Install Ollama from: https://ollama.ai
"""
import uuid
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from arrs.models.simulation_result import SimulationResult
from arrs.simulation.prompt_templates import (
    get_recommendation_prompt,
    get_attribute_extraction_prompt
)
from arrs.simulation.citation_analyzer import CitationAnalyzer
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)


class OllamaSimulator:
    """Local LLM simulator using Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama simulator.

        Args:
            base_url: Ollama API base URL (default: localhost)
            model: Model name (llama2, mistral, phi, etc.)
        """
        self.base_url = base_url
        self.model = model
        self.citation_analyzer = CitationAnalyzer()
        logger.info(f"Initialized Ollama simulator with model: {model}")

    async def simulate_recommendation(
        self,
        analysis_id: str,
        brand: str,
        product_category: str,
        use_case: str
    ) -> SimulationResult:
        """
        Simulate AI recommendation using local LLM.

        Args:
            analysis_id: Analysis ID
            brand: Brand name to check for
            product_category: Product category
            use_case: Use case scenario

        Returns:
            Simulation result
        """
        logger.info("Starting Ollama recommendation simulation", extra={
            "analysis_id": analysis_id,
            "brand": brand,
            "category": product_category,
            "model": self.model
        })

        # Generate prompt
        prompt = get_recommendation_prompt(product_category, use_case)

        # Query Ollama
        try:
            response = await self._query_ollama(prompt)
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            # Return empty result if Ollama is not available
            return self._create_fallback_result(analysis_id, brand, prompt, str(e))

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
                "citation_context": citation_analysis.get("contexts", []),
                "llm_provider": "ollama",
                "model": self.model
            }
        )

        logger.info("Ollama simulation complete", extra={
            "analysis_id": analysis_id,
            "brand_cited": result.brand_cited,
            "citation_count": result.citation_count
        })

        return result

    async def _query_ollama(self, prompt: str) -> str:
        """
        Query Ollama API.

        Args:
            prompt: Prompt text

        Returns:
            LLM response

        Raises:
            Exception: If Ollama is not available or query fails
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                return data.get("response", "")

            except httpx.ConnectError:
                raise Exception(
                    "Cannot connect to Ollama. Is it running? Install from https://ollama.ai and run 'ollama serve'"
                )
            except Exception as e:
                raise Exception(f"Ollama query failed: {e}")

    async def _identify_missing_signals(
        self,
        brand: str,
        product_category: str,
        recommendation_response: str
    ) -> list:
        """
        Identify what attributes the LLM wanted but might be missing.

        Args:
            brand: Brand name
            product_category: Product category
            recommendation_response: LLM's recommendation response

        Returns:
            List of missing signals/attributes
        """
        # Ask LLM what attributes it values
        prompt = get_attribute_extraction_prompt(brand, product_category)

        try:
            response = await self._query_ollama(prompt)
            missing_signals = self.citation_analyzer.extract_important_attributes(response)
            return missing_signals

        except Exception as e:
            logger.warning(f"Failed to identify missing signals: {e}")
            return []

    def _create_fallback_result(
        self,
        analysis_id: str,
        brand: str,
        prompt: str,
        error: str
    ) -> SimulationResult:
        """Create a fallback result when Ollama is not available."""
        return SimulationResult(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            prompt=prompt,
            response=f"[Ollama not available: {error}]",
            brand_cited=False,
            citation_count=0,
            missing_signals=[],
            simulated_at=datetime.now(),
            metadata={
                "llm_provider": "ollama",
                "model": self.model,
                "error": error,
                "simulation_skipped": True
            }
        )

    async def check_availability(self) -> bool:
        """
        Check if Ollama is available.

        Returns:
            True if Ollama is running and accessible
        """
        url = f"{self.base_url}/api/tags"

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                return response.status_code == 200
            except Exception:
                return False
