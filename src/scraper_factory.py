"""Scraper factory implementation."""

import logging
from typing import Dict, Type

from src.abstractions import IScraper, IScraperFactory

logger = logging.getLogger(__name__)


class ScraperFactory(IScraperFactory):
    """Factory for creating scraper instances."""

    def __init__(self) -> None:
        """Initialize the scraper factory."""
        self._scrapers: Dict[str, Type[IScraper]] = {}
        logger.debug("ScraperFactory initialized")

    def register_scraper(self, platform: str, scraper_class: Type[IScraper]) -> None:
        """
        Register a new scraper class for a platform.

        Args:
            platform: Platform name (e.g., 'reddit', 'stackoverflow')
            scraper_class: Class implementing IScraper

        Raises:
            ValueError: If platform is empty or scraper_class doesn't implement IScraper
            TypeError: If scraper_class doesn't have required IScraper methods
        """
        if not platform or not isinstance(platform, str):
            raise ValueError("Platform must be a non-empty string")

        if not issubclass(scraper_class, IScraper):
            raise TypeError(
                f"{scraper_class.__name__} must implement IScraper interface"
            )

        platform_lower = platform.lower().strip()
        self._scrapers[platform_lower] = scraper_class

        logger.info(f"Scraper registered for platform: {platform_lower}")

    def create_scraper(self, platform: str) -> IScraper:
        """
        Create a scraper instance for the given platform.

        Args:
            platform: Platform name (e.g., 'reddit', 'stackoverflow')

        Returns:
            Scraper instance for the platform

        Raises:
            ValueError: If platform is not supported or empty
        """
        if not platform or not isinstance(platform, str):
            raise ValueError("Platform must be a non-empty string")

        platform_lower = platform.lower().strip()

        if platform_lower not in self._scrapers:
            supported = ", ".join(self._scrapers.keys())
            raise ValueError(
                f"Unsupported platform: '{platform}'. "
                f"Supported platforms: {supported}"
            )

        scraper_class = self._scrapers[platform_lower]

        try:
            scraper = scraper_class()
            logger.debug(f"Scraper created for platform: {platform_lower}")
            return scraper

        except Exception as e:
            logger.error(f"Failed to instantiate scraper for {platform_lower}: {str(e)}")
            raise ValueError(
                f"Failed to create scraper for {platform_lower}: {str(e)}"
            ) from e

    @property
    def supported_platforms(self) -> list[str]:
        """
        Get list of supported platforms.

        Returns:
            List of registered platform names sorted alphabetically
        """
        platforms = sorted(self._scrapers.keys())
        logger.debug(f"Supported platforms: {platforms}")
        return platforms

    def is_platform_supported(self, platform: str) -> bool:
        """
        Check if a platform is supported.

        Args:
            platform: Platform name to check

        Returns:
            True if platform is supported, False otherwise
        """
        if not platform or not isinstance(platform, str):
            return False

        return platform.lower().strip() in self._scrapers

    def unregister_scraper(self, platform: str) -> None:
        """
        Unregister a scraper from a platform.

        Args:
            platform: Platform name to unregister

        Raises:
            ValueError: If platform is not registered
        """
        if not platform or not isinstance(platform, str):
            raise ValueError("Platform must be a non-empty string")

        platform_lower = platform.lower().strip()

        if platform_lower not in self._scrapers:
            raise ValueError(f"Platform '{platform}' is not registered")

        del self._scrapers[platform_lower]
        logger.info(f"Scraper unregistered for platform: {platform_lower}")