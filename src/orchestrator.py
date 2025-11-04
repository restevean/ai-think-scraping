"""Orchestrator for coordinating multiple scrapers."""

import logging
from typing import Optional

from src.abstractions import IScraperFactory, IStorage
from src.json_storage import JsonStorage
from src.models import ConversationThread, Message, ScrapingResult
from src.scraper_factory import ScraperFactory

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates scraping operations across multiple URLs and platforms."""

    def __init__(
        self,
        factory: Optional[IScraperFactory] = None,
        storage: Optional[IStorage] = None,
    ) -> None:
        """
        Initialize orchestrator.

        Args:
            factory: Scraper factory (creates default if None)
            storage: Storage instance (creates default if None)
        """
        self.factory = factory or ScraperFactory()
        self.storage = storage or JsonStorage()
        self.results: list[ScrapingResult] = []
        self.conversations: list[ConversationThread] = []

        logger.info("Orchestrator initialized")

    def scrape_url(self, url: str) -> ScrapingResult:
        """
        Scrape a single URL with appropriate scraper.

        Args:
            url: URL to scrape

        Returns:
            ScrapingResult with extraction details

        Raises:
            ValueError: If no scraper supports the URL
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        logger.info(f"Starting scrape for single URL: {url}")

        # Find scraper that can handle this URL
        scraper = None
        for platform in self.factory.supported_platforms:
            try:
                candidate = self.factory.create_scraper(platform)
                if candidate.can_handle(url):
                    scraper = candidate
                    logger.debug(f"Found scraper for {url}: {candidate.platform_name}")
                    break
            except Exception as e:
                logger.debug(f"Scraper {platform} error: {str(e)}")
                continue

        if scraper is None:
            error_msg = f"No scraper supports URL: {url}"
            logger.error(error_msg)
            result = ScrapingResult(success=False, url=url, error=error_msg)
            self.results.append(result)
            raise ValueError(error_msg)

        # Execute scraping
        result = scraper.scrape(url)
        self.results.append(result)

        if result.success:
            logger.info(f"Successfully scraped {result.messages_count} messages from {url}")
        else:
            logger.warning(f"Scraping failed for {url}: {result.error}")

        return result

    def scrape_urls(self, urls: list[str]) -> list[ScrapingResult]:
        """
        Scrape multiple URLs sequentially.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of ScrapingResult objects

        Raises:
            ValueError: If urls list is empty
        """
        if not urls:
            raise ValueError("URLs list cannot be empty")

        if not isinstance(urls, list):
            raise ValueError("URLs must be a list")

        logger.info(f"Starting scrape for {len(urls)} URLs")

        results = []

        for idx, url in enumerate(urls, 1):
            try:
                logger.debug(f"Scraping URL {idx}/{len(urls)}: {url}")
                result = self.scrape_url(url)
                results.append(result)

            except ValueError as e:
                logger.warning(f"Failed to scrape {url}: {str(e)}")
                results.append(ScrapingResult(success=False, url=url, error=str(e)))

            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {str(e)}")
                results.append(ScrapingResult(success=False, url=url, error=str(e)))

        logger.info(
            f"Completed scraping {len(urls)} URLs. "
            f"Successful: {sum(1 for r in results if r.success)}, "
            f"Failed: {sum(1 for r in results if not r.success)}"
        )

        return results

    def scrape_platform(self, platform: str, urls: list[str]) -> list[ScrapingResult]:
        """
        Scrape multiple URLs using a specific platform scraper.

        Args:
            platform: Platform name (e.g., 'reddit', 'stackoverflow')
            urls: List of URLs for that platform

        Returns:
            List of ScrapingResult objects

        Raises:
            ValueError: If platform is not supported or urls list is empty
        """
        if not platform or not isinstance(platform, str):
            raise ValueError("Platform must be a non-empty string")

        if not urls:
            raise ValueError("URLs list cannot be empty")

        if not self.factory.is_platform_supported(platform):
            supported = ", ".join(self.factory.supported_platforms)
            raise ValueError(f"Platform '{platform}' not supported. " f"Supported: {supported}")

        logger.info(f"Starting scrape for platform '{platform}' with {len(urls)} URLs")

        results = []

        for idx, url in enumerate(urls, 1):
            try:
                logger.debug(f"Scraping {platform} URL {idx}/{len(urls)}: {url}")
                result = self.scrape_url(url)
                results.append(result)

            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                results.append(ScrapingResult(success=False, url=url, error=str(e)))

        logger.info(f"Completed scraping {platform}: {len(results)} URLs processed")

        return results

    def get_results_summary(self) -> dict:
        """
        Get summary of all scraping results.

        Returns:
            Dictionary with summary statistics
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        total_messages = sum(r.messages_count for r in self.results if r.success)

        return {
            "total_urls": total,
            "successful": successful,
            "failed": failed,
            "total_messages": total_messages,
            "success_rate": (successful / total * 100) if total > 0 else 0,
        }

    def export_results(self, filename: str) -> str:
        """
        Export results to JSON file.

        Args:
            filename: Name of file to save results to

        Returns:
            Path to saved file

        Raises:
            IOError: If export fails
        """
        if not self.results:
            raise ValueError("No results to export")

        logger.info(f"Exporting {len(self.results)} results to {filename}")

        # Create a data structure with all results
        export_data = {
            "results": [r.model_dump(mode="json") for r in self.results],
            "summary": self.get_results_summary(),
        }

        # Save to JSON (convert to dict first since it's not a Pydantic model)
        try:
            import json
            from pathlib import Path

            filepath = Path(filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Results exported to: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to export results: {str(e)}")
            raise IOError(f"Failed to export results: {str(e)}") from e

    def reset(self) -> None:
        """Reset results and conversations."""
        self.results = []
        self.conversations = []
        logger.info("Orchestrator reset")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Orchestrator(results={len(self.results)}, "
            f"platforms={len(self.factory.supported_platforms)})"
        )
