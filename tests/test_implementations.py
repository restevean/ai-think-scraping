"""Tests for concrete implementations."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.abstractions import IScraper
from src.http_client import HttpClient
from src.json_storage import JsonStorage
from src.models import Message, ScrapingResult
from src.scraper_factory import ScraperFactory


class TestHttpClient:
    """Test cases for HttpClient implementation."""

    def test_initialization_with_defaults(self) -> None:
        """Test HttpClient initialization with default values."""
        client = HttpClient()

        assert client.timeout == 10
        assert client.max_retries == 3
        assert client.request_delay == 1
        assert client.session is not None

    def test_initialization_with_custom_values(self) -> None:
        """Test HttpClient initialization with custom values."""
        client = HttpClient(
            timeout=20, max_retries=5, retry_delay=3, request_delay=2
        )

        assert client.timeout == 20
        assert client.max_retries == 5
        assert client.retry_delay == 3
        assert client.request_delay == 2

    def test_get_with_invalid_url(self) -> None:
        """Test GET request with invalid URL."""
        client = HttpClient()

        with pytest.raises(ValueError, match="Invalid URL"):
            client.get("not-a-valid-url")

    def test_get_with_empty_url(self) -> None:
        """Test GET request with empty URL."""
        client = HttpClient()

        with pytest.raises(ValueError, match="URL cannot be empty"):
            client.get("")

    def test_head_with_invalid_url(self) -> None:
        """Test HEAD request with invalid URL."""
        client = HttpClient()

        with pytest.raises(ValueError, match="Invalid URL"):
            client.head("invalid-url")

    def test_head_with_empty_url(self) -> None:
        """Test HEAD request with empty URL."""
        client = HttpClient()

        with pytest.raises(ValueError, match="URL cannot be empty"):
            client.head("")

    @patch("src.http_client.requests.Session.get")
    def test_get_successful_request(self, mock_get) -> None:
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = HttpClient()
        result = client.get("https://example.com")

        assert result == "<html>Test</html>"
        mock_get.assert_called_once()

    @patch("src.http_client.requests.Session.head")
    def test_head_successful_request(self, mock_head) -> None:
        """Test successful HEAD request."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        client = HttpClient()
        result = client.head("https://example.com")

        assert result["Content-Type"] == "text/html"
        mock_head.assert_called_once()

    def test_context_manager(self) -> None:
        """Test HttpClient as context manager."""
        with HttpClient() as client:
            assert client is not None
            assert client.session is not None


class TestJsonStorage:
    """Test cases for JsonStorage implementation."""

    def test_initialization_creates_directory(self) -> None:
        """Test that JsonStorage creates storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            assert storage.storage_dir.exists()

    def test_save_pydantic_model(self) -> None:
        """Test saving a Pydantic model to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test message",
                platform="reddit",
                url="https://reddit.com",
            )

            filepath = storage.save(msg, "test_message")

            assert Path(filepath).exists()
            assert filepath.endswith(".json")

    def test_save_with_json_extension(self) -> None:
        """Test saving with .json extension in filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test", platform="reddit", url="https://reddit.com"
            )

            filepath = storage.save(msg, "test.json")

            assert Path(filepath).exists()

    def test_save_non_pydantic_model_raises_error(self) -> None:
        """Test that saving non-Pydantic data raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))

            with pytest.raises(ValueError, match="Pydantic BaseModel"):
                storage.save({"not": "a model"}, "test")  # type: ignore

    def test_load_existing_file(self) -> None:
        """Test loading data from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test", platform="reddit", url="https://reddit.com"
            )
            storage.save(msg, "test_message")

            loaded = storage.load("test_message")

            assert loaded["content"] == "Test"
            assert loaded["platform"] == "reddit"

    def test_load_nonexistent_file_raises_error(self) -> None:
        """Test that loading nonexistent file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))

            with pytest.raises(FileNotFoundError):
                storage.load("nonexistent")

    def test_exists_returns_true_for_existing_file(self) -> None:
        """Test exists() returns True for existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test", platform="reddit", url="https://reddit.com"
            )
            storage.save(msg, "test_message")

            assert storage.exists("test_message") is True

    def test_exists_returns_false_for_nonexistent_file(self) -> None:
        """Test exists() returns False for nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))

            assert storage.exists("nonexistent") is False

    def test_delete_removes_file(self) -> None:
        """Test delete() removes file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test", platform="reddit", url="https://reddit.com"
            )
            storage.save(msg, "test_message")

            assert storage.exists("test_message") is True

            storage.delete("test_message")

            assert storage.exists("test_message") is False

    def test_delete_nonexistent_file_raises_error(self) -> None:
        """Test delete() raises error for nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))

            with pytest.raises(FileNotFoundError):
                storage.delete("nonexistent")

    def test_list_files(self) -> None:
        """Test list_files() returns all JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JsonStorage(storage_dir=Path(tmpdir))
            msg = Message(
                content="Test", platform="reddit", url="https://reddit.com"
            )

            storage.save(msg, "file1")
            storage.save(msg, "file2")
            storage.save(msg, "file3")

            files = storage.list_files()

            assert len(files) == 3
            assert "file1.json" in files
            assert "file2.json" in files
            assert "file3.json" in files


class TestScraperFactory:
    """Test cases for ScraperFactory implementation."""

    def test_initialization(self) -> None:
        """Test factory initialization."""
        factory = ScraperFactory()

        assert factory.supported_platforms == []

    def test_register_scraper(self) -> None:
        """Test registering a scraper."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        assert "mock" in factory.supported_platforms

    def test_register_with_empty_platform_raises_error(self) -> None:
        """Test that registering with empty platform raises error."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()

        with pytest.raises(ValueError, match="non-empty string"):
            factory.register_scraper("", MockScraper)

    def test_register_non_scraper_raises_error(self) -> None:
        """Test that registering non-IScraper class raises error."""

        class NotAScraper:
            pass

        factory = ScraperFactory()

        with pytest.raises(TypeError, match="must implement IScraper"):
            factory.register_scraper("invalid", NotAScraper)  # type: ignore

    def test_create_scraper(self) -> None:
        """Test creating a scraper instance."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        scraper = factory.create_scraper("mock")

        assert isinstance(scraper, IScraper)
        assert scraper.platform_name == "mock"

    def test_create_unsupported_platform_raises_error(self) -> None:
        """Test that creating unsupported platform raises error."""
        factory = ScraperFactory()

        with pytest.raises(ValueError, match="Unsupported platform"):
            factory.create_scraper("unsupported")

    def test_is_platform_supported(self) -> None:
        """Test is_platform_supported() method."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        assert factory.is_platform_supported("mock") is True
        assert factory.is_platform_supported("other") is False

    def test_platform_names_are_case_insensitive(self) -> None:
        """Test that platform names are case insensitive."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("REDDIT", MockScraper)

        scraper = factory.create_scraper("reddit")
        assert scraper is not None

        assert factory.is_platform_supported("REDDIT") is True
        assert factory.is_platform_supported("Reddit") is True

    def test_unregister_scraper(self) -> None:
        """Test unregistering a scraper."""

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url)

            def can_handle(self, url: str) -> bool:
                return True

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        assert "mock" in factory.supported_platforms

        factory.unregister_scraper("mock")

        assert "mock" not in factory.supported_platforms

    def test_unregister_nonexistent_platform_raises_error(self) -> None:
        """Test that unregistering nonexistent platform raises error."""
        factory = ScraperFactory()

        with pytest.raises(ValueError, match="not registered"):
            factory.unregister_scraper("nonexistent")