"""Abstract interfaces for AI THINK Scrapping."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from src.models import ConversationThread, Message, ScrapingResult


class IHttpClient(ABC):
    """Interface for HTTP client operations."""

    @abstractmethod
    def get(self, url: str, timeout: Optional[int] = None) -> str:
        """
        Perform a GET request.

        Args:
            url: URL to request
            timeout: Request timeout in seconds

        Returns:
            Response content as string

        Raises:
            ConnectionError: If request fails after retries
            TimeoutError: If request exceeds timeout
        """
        pass

    @abstractmethod
    def head(self, url: str, timeout: Optional[int] = None) -> dict:
        """
        Perform a HEAD request to check URL availability.

        Args:
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            Response headers as dictionary

        Raises:
            ConnectionError: If request fails
        """
        pass


class IParser(ABC):
    """Interface for HTML parsing and content extraction."""

    @abstractmethod
    def parse(self, html_content: str) -> list[Message]:
        """
        Parse HTML content and extract messages.

        Args:
            html_content: Raw HTML content to parse

        Returns:
            List of extracted Message objects

        Raises:
            ValueError: If HTML parsing fails
        """
        pass


class IScraper(ABC):
    """Interface for web scrapers."""

    @abstractmethod
    def scrape(self, url: str) -> ScrapingResult:
        """
        Scrape content from a URL.

        Args:
            url: URL to scrape

        Returns:
            ScrapingResult with extraction details

        Raises:
            ValueError: If URL is invalid or scraping fails
        """
        pass

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this scraper can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this scraper supports the URL, False otherwise
        """
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Get the platform name (e.g., 'reddit', 'stackoverflow')."""
        pass


class IStorage(ABC):
    """Interface for data storage operations."""

    @abstractmethod
    def save(self, data: BaseModel, filename: str) -> str:
        """
        Save data to storage.

        Args:
            data: Data object to save (Pydantic model)
            filename: Name of the file to save (without extension)

        Returns:
            Path to saved file

        Raises:
            IOError: If save operation fails
        """
        pass

    @abstractmethod
    def load(self, filename: str) -> dict:
        """
        Load data from storage.

        Args:
            filename: Name of the file to load (without extension)

        Returns:
            Loaded data as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass

    @abstractmethod
    def exists(self, filename: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            filename: Name of the file (without extension)

        Returns:
            True if file exists, False otherwise
        """
        pass


class IScraperFactory(ABC):
    """Interface for scraper factory pattern."""

    @abstractmethod
    def create_scraper(self, platform: str) -> IScraper:
        """
        Create a scraper for the given platform.

        Args:
            platform: Platform name (e.g., 'reddit', 'stackoverflow')

        Returns:
            Scraper instance for the platform

        Raises:
            ValueError: If platform is not supported
        """
        pass

    @abstractmethod
    def register_scraper(self, platform: str, scraper_class: type[IScraper]) -> None:
        """
        Register a new scraper class for a platform.

        Args:
            platform: Platform name
            scraper_class: Class implementing IScraper
        """
        pass

    @property
    @abstractmethod
    def supported_platforms(self) -> list[str]:
        """Get list of supported platforms."""
        pass