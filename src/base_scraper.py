"""Base scraper with common functionality."""

import logging
from abc import abstractmethod
from typing import Optional

from src.abstractions import IHttpClient, IParser, IScraper
from src.http_client import HttpClient
from src.models import Message, ScrapingResult

logger = logging.getLogger(__name__)


class BaseScraper(IScraper):
    """Base class for all scrapers with common functionality."""

    def __init__(
        self,
        http_client: Optional[IHttpClient] = None,
        parser: Optional[IParser] = None,
    ) -> None:
        """
        Initialize base scraper.

        Args:
            http_client: HTTP client instance (uses default if None)
            parser: HTML parser instance (must be implemented by subclass)
        """
        self.http_client = http_client or HttpClient()
        self.parser = parser
        logger.debug(f"Initializing {self.__class__.__name__}")

    @abstractmethod
    def _get_parser(self) -> IParser:
        """
        Get parser instance for this scraper.

        Returns:
            Parser instance implementing IParser

        Note:
            Subclasses must implement this to provide their specific parser
        """
        pass

    def _ensure_parser(self) -> None:
        """Ensure parser is initialized."""
        if self.parser is None:
            self.parser = self._get_parser()

    def scrape(self, url: str) -> ScrapingResult:
        """
        Scrape content from URL.

        Args:
            url: URL to scrape

        Returns:
            ScrapingResult with extraction details

        Raises:
            ValueError: If URL is invalid or scraping fails
        """
        if not url or not isinstance(url, str):
            return ScrapingResult(
                success=False,
                url=url or "unknown",
                error="URL must be a non-empty string",
            )

        if not self.can_handle(url):
            return ScrapingResult(
                success=False,
                url=url,
                error=f"This scraper does not support URL: {url}",
            )

        try:
            logger.info(f"Starting scrape for URL: {url}")
            self._ensure_parser()

            # Fetch HTML content
            html_content = self.http_client.get(url)

            if not html_content:
                return ScrapingResult(
                    success=False,
                    url=url,
                    error="No content retrieved from URL",
                )

            # Parse HTML and extract messages
            messages = self.parser.parse(html_content)

            logger.info(f"Successfully scraped {len(messages)} messages from {url}")

            return ScrapingResult(
                success=True,
                url=url,
                messages_count=len(messages),
            )

        except TimeoutError as e:
            logger.error(f"Timeout error while scraping {url}: {str(e)}")
            return ScrapingResult(
                success=False,
                url=url,
                error=f"Request timeout: {str(e)}",
            )

        except ConnectionError as e:
            logger.error(f"Connection error while scraping {url}: {str(e)}")
            return ScrapingResult(
                success=False,
                url=url,
                error=f"Connection failed: {str(e)}",
            )

        except ValueError as e:
            logger.error(f"Parsing error for {url}: {str(e)}")
            return ScrapingResult(
                success=False,
                url=url,
                error=f"Parsing failed: {str(e)}",
            )

        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return ScrapingResult(
                success=False,
                url=url,
                error=f"Unexpected error: {str(e)}",
            )

    def can_handle(self, url: str) -> bool:
        """
        Check if this scraper can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this scraper supports the URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        domain = self._extract_domain(url)
        supported_domains = self._get_supported_domains()

        return domain in supported_domains

    @staticmethod
    def _extract_domain(url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: URL to extract domain from

        Returns:
            Domain name (e.g., 'reddit.com', 'stackoverflow.com')
        """
        try:
            # Remove protocol
            domain = url.replace("https://", "").replace("http://", "")
            # Remove path
            domain = domain.split("/")[0]
            # Remove www
            domain = domain.replace("www.", "")
            return domain.lower()
        except Exception:
            return ""

    @abstractmethod
    def _get_supported_domains(self) -> list[str]:
        """
        Get list of supported domains for this scraper.

        Returns:
            List of domain names (e.g., ['reddit.com', 'old.reddit.com'])

        Note:
            Subclasses must implement this
        """
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:

        pass

    def __repr__(self) -> str:
        """String representation of scraper."""
        return f"{self.__class__.__name__}(platform='{self.platform_name}')"
