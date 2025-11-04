"""Tests for abstract interfaces."""

from abc import ABC
from unittest.mock import MagicMock, patch

import pytest

from src.abstractions import IHttpClient, IParser, IScraper, IScraperFactory, IStorage
from src.models import Message, ScrapingResult


class TestIHttpClient:
    """Test cases for IHttpClient interface."""

    def test_http_client_is_abstract(self) -> None:
        """Test that IHttpClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IHttpClient()  # type: ignore

    def test_http_client_requires_get_method(self) -> None:
        """Test that IHttpClient requires get method implementation."""

        class IncompleteHttpClient(IHttpClient):
            def head(self, url: str, timeout=None) -> dict:
                return {}

        with pytest.raises(TypeError):
            IncompleteHttpClient()  # type: ignore

    def test_http_client_requires_head_method(self) -> None:
        """Test that IHttpClient requires head method implementation."""

        class IncompleteHttpClient(IHttpClient):
            def get(self, url: str, timeout=None) -> str:
                return ""

        with pytest.raises(TypeError):
            IncompleteHttpClient()  # type: ignore


class TestIParser:
    """Test cases for IParser interface."""

    def test_parser_is_abstract(self) -> None:
        """Test that IParser cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IParser()  # type: ignore

    def test_parser_requires_parse_method(self) -> None:
        """Test that IParser requires parse method implementation."""

        class IncompleteParser(IParser):
            pass

        with pytest.raises(TypeError):
            IncompleteParser()  # type: ignore


class TestIScraper:
    """Test cases for IScraper interface."""

    def test_scraper_is_abstract(self) -> None:
        """Test that IScraper cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IScraper()  # type: ignore

    def test_scraper_requires_scrape_method(self) -> None:
        """Test that IScraper requires scrape method."""

        class IncompleteScraper(IScraper):
            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "test"

        with pytest.raises(TypeError):
            IncompleteScraper()  # type: ignore

    def test_scraper_requires_can_handle_method(self) -> None:
        """Test that IScraper requires can_handle method."""

        class IncompleteScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            @property
            def platform_name(self) -> str:
                return "test"

        with pytest.raises(TypeError):
            IncompleteScraper()  # type: ignore

    def test_scraper_requires_platform_name_property(self) -> None:
        """Test that IScraper requires platform_name property."""

        class IncompleteScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteScraper()  # type: ignore


class TestIStorage:
    """Test cases for IStorage interface."""

    def test_storage_is_abstract(self) -> None:
        """Test that IStorage cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IStorage()  # type: ignore

    def test_storage_requires_save_method(self) -> None:
        """Test that IStorage requires save method."""

        class IncompleteStorage(IStorage):
            def load(self, filename: str) -> dict:
                return {}

            def exists(self, filename: str) -> bool:
                return False

        with pytest.raises(TypeError):
            IncompleteStorage()  # type: ignore

    def test_storage_requires_load_method(self) -> None:
        """Test that IStorage requires load method."""

        class IncompleteStorage(IStorage):
            def save(self, data, filename: str) -> str:
                return filename

            def exists(self, filename: str) -> bool:
                return False

        with pytest.raises(TypeError):
            IncompleteStorage()  # type: ignore

    def test_storage_requires_exists_method(self) -> None:
        """Test that IStorage requires exists method."""

        class IncompleteStorage(IStorage):
            def save(self, data, filename: str) -> str:
                return filename

            def load(self, filename: str) -> dict:
                return {}

        with pytest.raises(TypeError):
            IncompleteStorage()  # type: ignore


class TestIScraperFactory:
    """Test cases for IScraperFactory interface."""

    def test_factory_is_abstract(self) -> None:
        """Test that IScraperFactory cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IScraperFactory()  # type: ignore

    def test_factory_requires_create_scraper_method(self) -> None:
        """Test that factory requires create_scraper method."""

        class IncompleteFactory(IScraperFactory):
            def register_scraper(self, platform: str, scraper_class) -> None:
                pass

            @property
            def supported_platforms(self) -> list[str]:
                return []

        with pytest.raises(TypeError):
            IncompleteFactory()  # type: ignore

    def test_factory_requires_register_scraper_method(self) -> None:
        """Test that factory requires register_scraper method."""

        class IncompleteFactory(IScraperFactory):
            def create_scraper(self, platform: str) -> IScraper:
                raise NotImplementedError()

            @property
            def supported_platforms(self) -> list[str]:
                return []

        with pytest.raises(TypeError):
            IncompleteFactory()  # type: ignore

    def test_factory_requires_supported_platforms_property(self) -> None:
        """Test that factory requires supported_platforms property."""

        class IncompleteFactory(IScraperFactory):
            def create_scraper(self, platform: str) -> IScraper:
                raise NotImplementedError()

            def register_scraper(self, platform: str, scraper_class) -> None:
                pass

        with pytest.raises(TypeError):
            IncompleteFactory()  # type: ignore


class TestInterfaceCompliance:
    """Test that implementations correctly follow interfaces."""

    def test_valid_http_client_implementation(self) -> None:
        """Test a valid IHttpClient implementation."""

        class ValidHttpClient(IHttpClient):
            def get(self, url: str, timeout=None) -> str:
                return "<html></html>"

            def head(self, url: str, timeout=None) -> dict:
                return {"Content-Type": "text/html"}

        client = ValidHttpClient()
        assert client.get("http://example.com") == "<html></html>"
        assert client.head("http://example.com")["Content-Type"] == "text/html"

    def test_valid_scraper_implementation(self) -> None:
        """Test a valid IScraper implementation."""

        class ValidScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url, messages_count=0)

            def can_handle(self, url: str) -> bool:
                return "example.com" in url

            @property
            def platform_name(self) -> str:
                return "example"

        scraper = ValidScraper()
        assert scraper.can_handle("http://example.com/page")
        assert scraper.platform_name == "example"
        result = scraper.scrape("http://example.com/page")
        assert result.success is True
