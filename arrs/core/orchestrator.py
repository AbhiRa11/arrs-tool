"""Orchestrator for coordinating the ARRS analysis pipeline."""
from typing import Dict, List, Any, Optional
from arrs.models.analysis import Analysis, AnalysisStatus
from arrs.models.crawled_content import CrawledContent
from arrs.crawlers.beautifulsoup_crawler import BeautifulSoupCrawler
from arrs.crawlers.playwright_crawler import PlaywrightCrawler
from arrs.parsers.html_parser import HTMLParser
from arrs.parsers.schema_parser import SchemaParser
from arrs.engines.ade.engine import ADEEngine
from arrs.engines.arce.engine import ARCEEngine
from arrs.engines.tre.engine import TREEngine
from arrs.simulation.simulator import ClaudeSimulator
from arrs.simulation.ollama_simulator import OllamaSimulator
from arrs.simulation.openai_simulator import OpenAISimulator
from arrs.storage.repository import Repository
from arrs.core.exceptions import CrawlerException, EngineException, SimulationException
from arrs.utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class AnalysisOrchestrator:
    """Orchestrates the complete ARRS analysis pipeline."""

    def __init__(self, repository: Repository):
        """
        Initialize orchestrator.

        Args:
            repository: Data repository
        """
        self.repository = repository

        # Initialize components
        self.crawler = BeautifulSoupCrawler(
            timeout=settings.crawler_timeout,
            user_agent=settings.crawler_user_agent
        )

        # Initialize engines
        self.engines = {
            "ADE": ADEEngine(weight=settings.weight_ade),
            "ARCE": ARCEEngine(weight=settings.weight_arce),
            "TRE": TREEngine(weight=settings.weight_tre)
        }

        # Initialize LLM simulator based on configuration
        if settings.llm_provider == "openai" and settings.openai_api_key:
            self.simulator = OpenAISimulator(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                repository=repository
            )
            logger.info(f"Using OpenAI ({settings.openai_model}) for AI simulation")
        elif settings.llm_provider == "claude" and settings.anthropic_api_key:
            self.simulator = ClaudeSimulator(api_key=settings.anthropic_api_key)
            logger.info("Using Claude API for AI simulation")
        elif settings.llm_provider == "ollama":
            self.simulator = OllamaSimulator(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model
            )
            logger.info(f"Using Ollama ({settings.ollama_model}) for AI simulation")
        else:
            self.simulator = None
            logger.warning("No LLM provider configured - AI simulation will be skipped")

        logger.info("Orchestrator initialized", extra={
            "engines": list(self.engines.keys()),
            "weights": {name: engine.weight for name, engine in self.engines.items()},
            "llm_provider": settings.llm_provider
        })

    async def analyze_url(
        self,
        url: str,
        brand: Optional[str] = None,
        product_category: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> str:
        """
        Run complete analysis pipeline on a URL.

        Args:
            url: URL to analyze
            brand: Brand name (extracted if not provided)
            product_category: Product category for simulation
            use_case: Use case for simulation

        Returns:
            Analysis ID

        Raises:
            Exception: If analysis fails
        """
        logger.info("Starting analysis", extra={"url": url})

        # 1. Create analysis record
        analysis = await self.repository.create_analysis(url)

        try:
            # 2. Update status to processing
            await self.repository.update_analysis_status(
                analysis.id,
                AnalysisStatus.PROCESSING
            )

            # 3. Crawl URL
            logger.info("Crawling URL", extra={"analysis_id": analysis.id})
            crawled_content = await self._crawl_url(url, analysis.id)
            await self.repository.save_crawled_content(crawled_content)

            # 4. Parse content
            logger.info("Parsing content", extra={"analysis_id": analysis.id})
            parsed_data = await self._parse_content(crawled_content)

            # 5. Run scoring engines
            logger.info("Running scoring engines", extra={"analysis_id": analysis.id})
            engine_scores = await self._run_engines(crawled_content, parsed_data)

            # Save scores
            for score in engine_scores:
                await self.repository.save_engine_score(score)

            # 6. Calculate composite score
            composite_score = self._calculate_composite_score(engine_scores)
            await self.repository.update_composite_score(analysis.id, composite_score)

            logger.info("Composite score calculated", extra={
                "analysis_id": analysis.id,
                "composite_score": composite_score
            })

            # 7. Identify gaps from engines
            all_gaps = []
            for score in engine_scores:
                engine_name = score.engine_name
                engine = self.engines.get(engine_name)
                if engine:
                    gaps = await engine.identify_gaps(score, parsed_data)
                    all_gaps.extend(gaps)

            # 8. Run AI simulation (if simulator available and brand/category provided)
            if self.simulator and brand and product_category and use_case:
                logger.info("Running AI simulation", extra={"analysis_id": analysis.id})
                try:
                    simulation_result = await self._run_simulation(
                        analysis.id,
                        brand,
                        product_category,
                        use_case
                    )
                    await self.repository.save_simulation_result(simulation_result)

                    # Add simulation-based gaps
                    simulation_gaps = self._extract_simulation_gaps(
                        analysis.id,
                        simulation_result,
                        parsed_data
                    )
                    all_gaps.extend(simulation_gaps)
                except Exception as e:
                    logger.warning(f"AI simulation failed: {e}. Continuing without simulation.")
            elif not self.simulator:
                logger.info("AI simulation skipped - no LLM provider configured")

            # 9. Save all gaps
            await self.repository.save_gaps(all_gaps)

            # 10. Mark analysis complete
            await self.repository.update_analysis_status(
                analysis.id,
                AnalysisStatus.COMPLETED
            )

            logger.info("Analysis completed", extra={
                "analysis_id": analysis.id,
                "composite_score": composite_score,
                "gap_count": len(all_gaps)
            })

            return analysis.id

        except Exception as e:
            logger.error("Analysis failed", extra={
                "analysis_id": analysis.id,
                "error": str(e)
            })

            await self.repository.update_analysis_status(
                analysis.id,
                AnalysisStatus.FAILED,
                error_message=str(e)
            )

            raise

    async def _crawl_url(self, url: str, analysis_id: str) -> CrawledContent:
        """Crawl URL with BeautifulSoup first, fallback to Playwright if needed."""
        # Try BeautifulSoup first (faster)
        try:
            logger.info("Trying BeautifulSoup crawler")
            return await self.crawler.crawl(url, analysis_id)
        except Exception as e:
            logger.warning(f"BeautifulSoup failed: {e}. Trying Playwright fallback...")

            # Fallback to Playwright for protected sites
            try:
                playwright_crawler = PlaywrightCrawler(
                    timeout=settings.crawler_timeout,
                    user_agent=settings.crawler_user_agent
                )
                logger.info("Using Playwright crawler for anti-bot protection")
                return await playwright_crawler.crawl(url, analysis_id)
            except Exception as playwright_error:
                logger.error(f"Both crawlers failed. Playwright error: {playwright_error}")
                raise CrawlerException(f"Failed to crawl {url}: {playwright_error}")

    async def _parse_content(self, content: CrawledContent) -> Dict[str, Any]:
        """Parse HTML and extract structured data."""
        # Parse HTML
        html_parser = HTMLParser(content.html_content, content.url)
        html_data = html_parser.parse()
        html_data["heading_validation"] = html_parser.validate_heading_hierarchy()

        # Parse schema
        schema_parser = SchemaParser(content.html_content, content.url)
        schema_data = {
            "all_schemas": schema_parser.extract_all_schemas(),
            "product": schema_parser.find_product_schema(),
            "organization": schema_parser.find_organization_schema(),
            "product_validation": schema_parser.validate_product_schema(),
            "offers": schema_parser.extract_offers(),
            "reviews": schema_parser.extract_reviews(),
            "brand": schema_parser.extract_brand_info()
        }

        return {
            "html": html_data,
            "schema": schema_data
        }

    async def _run_engines(
        self,
        content: CrawledContent,
        parsed_data: Dict[str, Any]
    ) -> List:
        """Run all scoring engines."""
        scores = []

        for engine_name, engine in self.engines.items():
            try:
                logger.info(f"Running {engine_name} engine")
                score = await engine.analyze(content, parsed_data)
                scores.append(score)
            except Exception as e:
                logger.error(f"{engine_name} engine failed: {e}")
                # Continue with other engines
                # Could optionally create a zero-score result here

        return scores

    def _calculate_composite_score(self, engine_scores: List) -> float:
        """Calculate weighted composite score."""
        total_weight = sum(score.weight for score in engine_scores)

        if total_weight == 0:
            return 0.0

        weighted_sum = sum(score.score * score.weight for score in engine_scores)

        # Normalize to 0-100 range
        composite = weighted_sum / total_weight

        return round(composite, 2)

    async def _run_simulation(
        self,
        analysis_id: str,
        brand: str,
        product_category: str,
        use_case: str
    ):
        """Run AI simulation."""
        try:
            return await self.simulator.simulate_recommendation(
                analysis_id,
                brand,
                product_category,
                use_case
            )
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise SimulationException(f"AI simulation failed: {e}")

    def _extract_simulation_gaps(
        self,
        analysis_id: str,
        simulation_result,
        parsed_data: Dict[str, Any]
    ) -> List:
        """Extract gaps from simulation results."""
        gaps = []

        # If brand not cited, it's a critical gap
        if not simulation_result.brand_cited:
            from arrs.models.score_result import Gap
            import uuid

            gaps.append(Gap(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                gap_type="not_cited_by_ai",
                severity="critical",
                description="Brand was not mentioned in AI recommendation",
                recommendation="Improve product attributes, trust signals, and content clarity to increase AI citation likelihood",
                engine_source="AI_SIMULATION"
            ))

        # Add gaps for missing signals
        for signal in simulation_result.missing_signals:
            from arrs.models.score_result import Gap
            import uuid

            gaps.append(Gap(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                gap_type="missing_attribute",
                severity="medium",
                description=f"AI values this attribute but it may be missing: {signal}",
                recommendation=f"Add or enhance information about: {signal}",
                engine_source="AI_SIMULATION"
            ))

        return gaps

    async def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get complete analysis summary.

        Args:
            analysis_id: Analysis ID

        Returns:
            Analysis summary dictionary
        """
        analysis = await self.repository.get_analysis(analysis_id)
        if not analysis:
            return None

        engine_scores = await self.repository.get_engine_scores(analysis_id)
        gaps = await self.repository.get_gaps(analysis_id)
        simulation = await self.repository.get_simulation_result(analysis_id)

        return {
            "analysis_id": analysis.id,
            "url": analysis.url,
            "status": analysis.status.value,
            "composite_score": analysis.composite_score,
            "created_at": analysis.created_at.isoformat(),
            "engine_scores": {
                score.engine_name: {
                    "score": score.score,
                    "weight": score.weight,
                    "details": score.details
                }
                for score in engine_scores
            },
            "gaps": [
                {
                    "type": gap.gap_type,
                    "severity": gap.severity,
                    "description": gap.description,
                    "recommendation": gap.recommendation,
                    "source": gap.engine_source
                }
                for gap in gaps
            ],
            "simulation": {
                "brand_cited": simulation.brand_cited if simulation else None,
                "citation_count": simulation.citation_count if simulation else 0,
                "response_preview": simulation.response[:200] + "..." if simulation and simulation.response else None
            } if simulation else None
        }
