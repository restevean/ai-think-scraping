"""Tests for scrapers and parsers."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.abstractions import IParser
from src.models import Message, ScrapingResult
from src.parsers import BaseParser, DevToParser, MediumParser, RedditParser, StackOverflowParser
from src.scrapers import DevToScraper, MediumScraper, RedditScraper, StackOverflowScraper


class TestBaseParser:
    """Test cases for BaseParser."""

    def test_parse_empty_html_raises_error(self) -> None:
        """Test that empty HTML raises error."""

        class TestParser(BaseParser):
            def _extract_messages(self, soup):
                return []

        parser = TestParser()

        with pytest.raises(ValueError, match="non-empty string"):
            parser.parse("")

    def test_parse_invalid_html_with_error_in_extract(self) -> None:
        """Test that parsing error in _extract_messages is handled."""

        class FailingParser(BaseParser):
            def _extract_messages(self, soup):
                raise ValueError("Extraction failed")

        parser = FailingParser()

        with pytest.raises(ValueError, match="Failed to parse HTML"):
            parser.parse("<html><body>Test</body></html>")

    def test_clean_text_removes_whitespace(self) -> None:
        """Test that clean_text removes extra whitespace."""
        result = BaseParser._clean_text("  hello   world  \n  test  ")

        assert result == "hello world test"

    def test_clean_text_with_empty_string(self) -> None:
        """Test that clean_text handles empty string."""
        result = BaseParser._clean_text("")

        assert result == ""

    def test_clean_text_with_none(self) -> None:
        """Test that clean_text handles None."""
        result = BaseParser._clean_text(None)

        assert result == ""

    def test_get_initials_from_single_word(self) -> None:
        """Test extracting initials from single word."""
        result = BaseParser._get_initials("john")

        assert result == "J"

    def test_get_initials_from_multiple_words(self) -> None:
        """Test extracting initials from multiple words."""
        result = BaseParser._get_initials("john doe smith")

        assert result == "JDS"

    def test_get_initials_with_none(self) -> None:
        """Test get_initials with None."""
        result = BaseParser._get_initials(None)

        assert result is None

    def test_get_initials_with_empty_string(self) -> None:
        """Test get_initials with empty string."""
        result = BaseParser._get_initials("")

        assert result is None


class TestRedditParser:
    """Test cases for RedditParser."""

    def test_parser_is_parser_implementation(self) -> None:
        """Test that RedditParser implements IParser."""
        parser = RedditParser()

        assert isinstance(parser, IParser)

    def test_extract_messages_with_empty_content(self) -> None:
        """Test extracting from HTML with no comments."""
        parser = RedditParser()
        html = "<html><body></body></html>"

        messages = parser.parse(html)

        assert isinstance(messages, list)
        assert len(messages) == 0


class TestStackOverflowParser:
    """Test cases for StackOverflowParser."""

    def test_parser_is_parser_implementation(self) -> None:
        """Test that StackOverflowParser implements IParser."""
        parser = StackOverflowParser()

        assert isinstance(parser, IParser)

    def test_extract_messages_with_empty_content(self) -> None:
        """Test extracting from HTML with no posts."""
        parser = StackOverflowParser()
        html = "<html><body></body></html>"

        messages = parser.parse(html)

        assert isinstance(messages, list)
        assert len(messages) == 0


class TestMediumParser:
    """Test cases for MediumParser."""

    def test_parser_is_parser_implementation(self) -> None:
        """Test that MediumParser implements IParser."""
        parser = MediumParser()

        assert isinstance(parser, IParser)

    def test_extract_messages_with_empty_content(self) -> None:
        """Test extracting from HTML with no articles."""
        parser = MediumParser()
        html = "<html><body></body></html>"

        messages = parser.parse(html)

        assert isinstance(messages, list)
        assert len(messages) == 0


class TestDevToParser:
    """Test cases for DevToParser."""

    def test_parser_is_parser_implementation(self) -> None:
        """Test that DevToParser implements IParser."""
        parser = DevToParser()

        assert isinstance(parser, IParser)

    def test_extract_messages_with_empty_content(self) -> None:
        """Test extracting from HTML with no content."""
        parser = DevToParser()
        html = "<html><body></body></html>"

        messages = parser.parse(html)

        assert isinstance(messages, list)
        assert len(messages) == 0


class TestRedditScraper:
    """Test cases for RedditScraper."""

    def test_scraper_is_scraper(self) -> None:
        """Test that RedditScraper is a scraper."""
        scraper = RedditScraper()

        assert scraper.platform_name == "reddit"

    def test_can_handle_reddit_urls(self) -> None:
        """Test that RedditScraper handles Reddit URLs."""
        scraper = RedditScraper()

        assert scraper.can_handle("https://reddit.com/r/test")
        assert scraper.can_handle("https://old.reddit.com/r/test")
        assert scraper.can_handle("https://www.reddit.com/r/test")

    def test_cannot_handle_other_urls(self) -> None:
        """Test that RedditScraper doesn't handle other URLs."""
        scraper = RedditScraper()

        assert scraper.can_handle("https://stackoverflow.com/q/test") is False
        assert scraper.can_handle("https://medium.com/story") is False

    def test_cannot_handle_invalid_urls(self) -> None:
        """Test that RedditScraper rejects invalid URLs."""
        scraper = RedditScraper()

        assert scraper.can_handle("") is False
        assert scraper.can_handle(None) is False  # type: ignore

    @patch("src.base_scraper.HttpClient.get")
    def test_scrape_successful(self, mock_get) -> None:
        """Test successful scraping."""
        mock_get.return_value = "<html><body><div class='md'>Test comment</div></body></html>"

        scraper = RedditScraper()
        result = scraper.scrape("https://reddit.com/r/test")

        assert isinstance(result, ScrapingResult)
        assert result.success is True
        assert result.url == "https://reddit.com/r/test"

    def test_scrape_invalid_url_returns_failure(self) -> None:
        """Test scraping with invalid URL."""
        scraper = RedditScraper()
        result = scraper.scrape("https://stackoverflow.com/q/test")

        assert result.success is False
        assert result.error is not None


class TestStackOverflowScraper:
    """Test cases for StackOverflowScraper."""

    def test_scraper_is_scraper(self) -> None:
        """Test that StackOverflowScraper is a scraper."""
        scraper = StackOverflowScraper()

        assert scraper.platform_name == "stackoverflow"

    def test_can_handle_stackoverflow_urls(self) -> None:
        """Test that StackOverflowScraper handles Stack Overflow URLs."""
        scraper = StackOverflowScraper()

        assert scraper.can_handle("https://stackoverflow.com/q/123")
        assert scraper.can_handle("https://www.stackoverflow.com/q/123")

    def test_cannot_handle_other_urls(self) -> None:
        """Test that StackOverflowScraper doesn't handle other URLs."""
        scraper = StackOverflowScraper()

        assert scraper.can_handle("https://reddit.com/r/test") is False


class TestMediumScraper:
    """Test cases for MediumScraper."""

    def test_scraper_is_scraper(self) -> None:
        """Test that MediumScraper is a scraper."""
        scraper = MediumScraper()

        assert scraper.platform_name == "medium"

    def test_can_handle_medium_urls(self) -> None:
        """Test that MediumScraper handles Medium URLs."""
        scraper = MediumScraper()

        assert scraper.can_handle("https://medium.com/@user/story")
        assert scraper.can_handle("https://www.medium.com/@user/story")

    def test_cannot_handle_other_urls(self) -> None:
        """Test that MediumScraper doesn't handle other URLs."""
        scraper = MediumScraper()

        assert scraper.can_handle("https://dev.to/user/story") is False


class TestDevToScraper:
    """Test cases for DevToScraper."""

    def test_scraper_is_scraper(self) -> None:
        """Test that DevToScraper is a scraper."""
        scraper = DevToScraper()

        assert scraper.platform_name == "devto"

    def test_can_handle_devto_urls(self) -> None:
        """Test that DevToScraper handles Dev.to URLs."""
        scraper = DevToScraper()

        assert scraper.can_handle("https://dev.to/user/story")
        assert scraper.can_handle("https://www.dev.to/user/story")

    def test_cannot_handle_other_urls(self) -> None:
        """Test that DevToScraper doesn't handle other URLs."""
        scraper = DevToScraper()

        assert scraper.can_handle("https://medium.com/@user/story") is False


class TestScraperIntegration:
    """Integration tests for scrapers."""

    def test_all_scrapers_are_different_platforms(self) -> None:
        """Test that all scrapers represent different platforms."""
        scrapers = [
            RedditScraper(),
            StackOverflowScraper(),
            MediumScraper(),
            DevToScraper(),
        ]

        platforms = {scraper.platform_name for scraper in scrapers}

        assert len(platforms) == 4
        assert "reddit" in platforms
        assert "stackoverflow" in platforms
        assert "medium" in platforms
        assert "devto" in platforms