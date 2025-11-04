"""Tests for Orchestrator."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.models import ScrapingResult
from src.orchestrator import Orchestrator
from src.scraper_factory import ScraperFactory


class TestOrchestratorInitialization:
    """Test cases for Orchestrator initialization."""

    def test_initialization_with_defaults(self) -> None:
        """Test Orchestrator initialization with default factory and storage."""
        orchestrator = Orchestrator()

        assert orchestrator.factory is not None
        assert orchestrator.storage is not None
        assert orchestrator.results == []
        assert orchestrator.conversations == []

    def test_initialization_with_custom_factory(self) -> None:
        """Test Orchestrator initialization with custom factory."""
        factory = ScraperFactory()
        orchestrator = Orchestrator(factory=factory)

        assert orchestrator.factory is factory

    def test_initialization_with_custom_storage(self) -> None:
        """Test Orchestrator initialization with custom storage."""
        from src.json_storage import JsonStorage

        storage = JsonStorage()
        orchestrator = Orchestrator(storage=storage)

        assert orchestrator.storage is storage


class TestScrapeUrl:
    """Test cases for scrape_url method."""

    def test_scrape_url_with_empty_url(self) -> None:
        """Test scraping with empty URL."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="non-empty string"):
            orchestrator.scrape_url("")

    def test_scrape_url_with_none(self) -> None:
        """Test scraping with None URL."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="non-empty string"):
            orchestrator.scrape_url(None)  # type: ignore

    def test_scrape_url_with_unsupported_platform(self) -> None:
        """Test scraping URL from unsupported platform."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="No scraper supports URL"):
            orchestrator.scrape_url("https://unsupported.com/page")

    def test_scrape_url_adds_result(self) -> None:
        """Test that scrape_url adds result to results list."""
        from src.abstractions import IScraper
        from src.models import Message

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url, messages_count=5)

            def can_handle(self, url: str) -> bool:
                return "mock" in url

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        orchestrator = Orchestrator(factory=factory)
        result = orchestrator.scrape_url("https://mock.com/page")

        assert len(orchestrator.results) == 1
        assert orchestrator.results[0].url == "https://mock.com/page"
        assert orchestrator.results[0].success is True

    @patch("src.base_scraper.HttpClient.get")
    def test_scrape_url_successful_logging(self, mock_get) -> None:
        """Test successful scraping logs correctly."""
        mock_get.return_value = "<html><body></body></html>"

        from src.scrapers import RedditScraper

        factory = ScraperFactory()
        factory.register_scraper("reddit", RedditScraper)

        orchestrator = Orchestrator(factory=factory)
        result = orchestrator.scrape_url("https://reddit.com/r/python")

        assert result.url == "https://reddit.com/r/python"


class TestScrapeUrls:
    """Test cases for scrape_urls method."""

    def test_scrape_urls_with_empty_list(self) -> None:
        """Test scraping with empty URLs list."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="cannot be empty"):
            orchestrator.scrape_urls([])

    def test_scrape_urls_with_non_list(self) -> None:
        """Test scraping with non-list input."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="must be a list"):
            orchestrator.scrape_urls("https://example.com")  # type: ignore

    def test_scrape_urls_multiple(self) -> None:
        """Test scraping multiple URLs."""
        from src.abstractions import IScraper

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url, messages_count=1)

            def can_handle(self, url: str) -> bool:
                return "mock" in url

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        orchestrator = Orchestrator(factory=factory)
        urls = [
            "https://mock.com/page1",
            "https://mock.com/page2",
            "https://mock.com/page3",
        ]

        results = orchestrator.scrape_urls(urls)

        assert len(results) == 3
        assert all(r.success for r in results)
        assert len(orchestrator.results) == 3

    def test_scrape_urls_with_mixed_results(self) -> None:
        """Test scraping URLs with mixed success/failure."""
        from src.abstractions import IScraper

        call_count = [0]  # Use list to track calls (closure workaround)

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                call_count[0] += 1
                # Make every other call fail
                success = call_count[0] % 2 != 0
                return ScrapingResult(
                    success=success,
                    url=url,
                    messages_count=1 if success else 0,
                    error=None if success else "Simulated failure",
                )

            def can_handle(self, url: str) -> bool:
                return "mock" in url

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        orchestrator = Orchestrator(factory=factory)
        urls = [
            "https://mock.com/url1",
            "https://mock.com/url2",
            "https://mock.com/url3",
        ]

        results = orchestrator.scrape_urls(urls)

        assert len(results) == 3
        assert sum(1 for r in results if r.success) == 2
        assert sum(1 for r in results if not r.success) == 1


class TestScrapePlatform:
    """Test cases for scrape_platform method."""

    def test_scrape_platform_with_empty_platform(self) -> None:
        """Test scraping with empty platform."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="non-empty string"):
            orchestrator.scrape_platform("", ["https://example.com"])

    def test_scrape_platform_with_empty_urls(self) -> None:
        """Test scraping with empty URLs list."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="cannot be empty"):
            orchestrator.scrape_platform("reddit", [])

    def test_scrape_platform_unsupported(self) -> None:
        """Test scraping unsupported platform."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="not supported"):
            orchestrator.scrape_platform("unknown", ["https://example.com"])

    def test_scrape_platform_supported(self) -> None:
        """Test scraping with supported platform."""
        from src.abstractions import IScraper

        class MockScraper(IScraper):
            def scrape(self, url: str) -> ScrapingResult:
                return ScrapingResult(success=True, url=url, messages_count=1)

            def can_handle(self, url: str) -> bool:
                return "mock" in url

            @property
            def platform_name(self) -> str:
                return "mock"

        factory = ScraperFactory()
        factory.register_scraper("mock", MockScraper)

        orchestrator = Orchestrator(factory=factory)
        results = orchestrator.scrape_platform("mock", ["https://mock.com/page"])

        assert len(results) == 1
        assert results[0].success is True


class TestResultsSummary:
    """Test cases for results summary."""

    def test_get_results_summary_empty(self) -> None:
        """Test summary with no results."""
        orchestrator = Orchestrator()

        summary = orchestrator.get_results_summary()

        assert summary["total_urls"] == 0
        assert summary["successful"] == 0
        assert summary["failed"] == 0
        assert summary["total_messages"] == 0
        assert summary["success_rate"] == 0

    def test_get_results_summary_with_results(self) -> None:
        """Test summary with mixed results."""
        orchestrator = Orchestrator()

        orchestrator.results = [
            ScrapingResult(success=True, url="url1", messages_count=10),
            ScrapingResult(success=True, url="url2", messages_count=5),
            ScrapingResult(success=False, url="url3", error="Failed"),
        ]

        summary = orchestrator.get_results_summary()

        assert summary["total_urls"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["total_messages"] == 15
        assert summary["success_rate"] == pytest.approx(66.66, rel=1)


class TestExportResults:
    """Test cases for exporting results."""

    def test_export_results_empty_raises_error(self) -> None:
        """Test exporting with no results."""
        orchestrator = Orchestrator()

        with pytest.raises(ValueError, match="No results to export"):
            orchestrator.export_results("output.json")

    def test_export_results_creates_file(self) -> None:
        """Test that export creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator()
            orchestrator.results = [
                ScrapingResult(success=True, url="url1", messages_count=5),
                ScrapingResult(success=False, url="url2", error="Failed"),
            ]

            filepath = Path(tmpdir) / "results.json"
            result_path = orchestrator.export_results(str(filepath))

            assert Path(result_path).exists()

    def test_export_results_contains_summary(self) -> None:
        """Test that exported file contains summary."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = Orchestrator()
            orchestrator.results = [
                ScrapingResult(success=True, url="url1", messages_count=5),
            ]

            filepath = Path(tmpdir) / "results.json"
            orchestrator.export_results(str(filepath))

            with open(filepath, "r") as f:
                data = json.load(f)

            assert "results" in data
            assert "summary" in data
            assert data["summary"]["total_urls"] == 1
            assert data["summary"]["successful"] == 1


class TestReset:
    """Test cases for reset method."""

    def test_reset_clears_results(self) -> None:
        """Test that reset clears results."""
        orchestrator = Orchestrator()
        orchestrator.results = [
            ScrapingResult(success=True, url="url1", messages_count=5),
        ]

        orchestrator.reset()

        assert orchestrator.results == []
        assert orchestrator.conversations == []


class TestRepr:
    """Test cases for string representation."""

    def test_repr_format(self) -> None:
        """Test __repr__ format."""
        orchestrator = Orchestrator()

        repr_str = repr(orchestrator)

        assert "Orchestrator" in repr_str
        assert "results" in repr_str
        assert "platforms" in repr_str