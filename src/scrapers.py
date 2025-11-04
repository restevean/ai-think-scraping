"""Platform-specific scraper implementations."""

import logging

from src.abstractions import IHttpClient, IParser
from src.base_scraper import BaseScraper
from src.parsers import DevToParser, MediumParser, RedditParser, StackOverflowParser

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Scraper for Reddit content."""

    def _get_parser(self) -> IParser:
        """Get Reddit parser."""
        return RedditParser()

    def _get_supported_domains(self) -> list[str]:
        """Get supported domains for Reddit."""
        return ["reddit.com", "old.reddit.com", "www.reddit.com"]

    @property
    def platform_name(self) -> str:
        """Get platform name."""
        return "reddit"


class StackOverflowScraper(BaseScraper):
    """Scraper for Stack Overflow content."""

    def _get_parser(self) -> IParser:
        """Get Stack Overflow parser."""
        return StackOverflowParser()

    def _get_supported_domains(self) -> list[str]:
        """Get supported domains for Stack Overflow."""
        return ["stackoverflow.com", "www.stackoverflow.com"]

    @property
    def platform_name(self) -> str:
        """Get platform name."""
        return "stackoverflow"


class MediumScraper(BaseScraper):
    """Scraper for Medium content."""

    def _get_parser(self) -> IParser:
        """Get Medium parser."""
        return MediumParser()

    def _get_supported_domains(self) -> list[str]:
        """Get supported domains for Medium."""
        return ["medium.com", "www.medium.com"]

    @property
    def platform_name(self) -> str:
        """Get platform name."""
        return "medium"


class DevToScraper(BaseScraper):
    """Scraper for Dev.to content."""

    def _get_parser(self) -> IParser:
        """Get Dev.to parser."""
        return DevToParser()

    def _get_supported_domains(self) -> list[str]:
        """Get supported domains for Dev.to."""
        return ["dev.to", "www.dev.to"]

    @property
    def platform_name(self) -> str:
        """Get platform name."""
        return "devto"