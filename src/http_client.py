"""HTTP client implementation with retry logic and rate limiting."""

import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.abstractions import IHttpClient
from src.config import SCRAPER_CONFIG

logger = logging.getLogger(__name__)


class HttpClient(IHttpClient):
    """HTTP client implementation with retry logic and rate limiting."""

    def __init__(
        self,
        timeout: int = SCRAPER_CONFIG["timeout"],
        max_retries: int = SCRAPER_CONFIG["max_retries"],
        retry_delay: float = SCRAPER_CONFIG["retry_delay"],
        request_delay: float = SCRAPER_CONFIG["request_delay"],
        user_agent: str = SCRAPER_CONFIG["user_agent"],
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            request_delay: Delay between requests in seconds (rate limiting)
            user_agent: User agent string
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_delay = request_delay
        self.user_agent = user_agent
        self._last_request_time: float = 0

        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({"User-Agent": self.user_agent})

        return session

    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            sleep_time = self.request_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def get(self, url: str, timeout: Optional[int] = None) -> str:
        """
        Perform a GET request with retry logic.

        Args:
            url: URL to request
            timeout: Request timeout in seconds (uses default if None)

        Returns:
            Response content as string

        Raises:
            ConnectionError: If request fails after retries
            TimeoutError: If request exceeds timeout
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError("URL cannot be empty")

        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

        timeout_val = timeout or self.timeout

        try:
            self._apply_rate_limit()

            logger.debug(f"GET request to: {url}")
            response = self.session.get(url, timeout=timeout_val)
            response.raise_for_status()

            logger.info(f"Successfully retrieved: {url} (status: {response.status_code})")
            return response.text

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error for {url}: {str(e)}")
            raise TimeoutError(f"Request to {url} timed out after {timeout_val}s") from e

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {url}: {str(e)}")
            raise ConnectionError(f"Failed to connect to {url}") from e

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP error {status_code} for {url}: {str(e)}")
            raise ConnectionError(f"HTTP {status_code} error for {url}") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise ConnectionError(f"Request failed for {url}: {str(e)}") from e

    def head(self, url: str, timeout: Optional[int] = None) -> dict:
        """
        Perform a HEAD request to check URL availability.

        Args:
            url: URL to check
            timeout: Request timeout in seconds (uses default if None)

        Returns:
            Response headers as dictionary

        Raises:
            ConnectionError: If request fails
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError("URL cannot be empty")

        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {url}")

        timeout_val = timeout or self.timeout

        try:
            self._apply_rate_limit()

            logger.debug(f"HEAD request to: {url}")
            response = self.session.head(url, timeout=timeout_val, allow_redirects=True)
            response.raise_for_status()

            logger.info(f"HEAD request successful for {url} (status: {response.status_code})")
            return dict(response.headers)

        except requests.exceptions.RequestException as e:
            logger.error(f"HEAD request error for {url}: {str(e)}")
            raise ConnectionError(f"HEAD request failed for {url}: {str(e)}") from e

    def close(self) -> None:
        """Close the session."""
        self.session.close()
        logger.debug("HTTP session closed")

    def __enter__(self) -> "HttpClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()