"""Tests for data models."""

from datetime import datetime

import pytest

from src.models import ConversationThread, Message, ScrapingResult


class TestMessage:
    """Test cases for Message model."""

    def test_message_creation_with_all_fields(self) -> None:
        """Test creating a message with all fields."""
        msg = Message(
            content="Great discussion!",
            author_initials="JD",
            date=datetime(2024, 1, 1, 10, 30),
            platform="reddit",
            url="https://reddit.com/r/test",
        )

        assert msg.content == "Great discussion!"
        assert msg.author_initials == "JD"
        assert msg.platform == "reddit"
        assert msg.url == "https://reddit.com/r/test"

    def test_message_creation_without_optional_fields(self) -> None:
        """Test creating a message with only required fields."""
        msg = Message(
            content="Minimal message",
            platform="stackoverflow",
            url="https://stackoverflow.com/q/test",
        )

        assert msg.content == "Minimal message"
        assert msg.author_initials is None
        assert msg.date is None

    def test_message_requires_content(self) -> None:
        """Test that content is required."""
        with pytest.raises(ValueError):
            Message(  # type: ignore
                platform="reddit", url="https://reddit.com/r/test"
            )

    def test_message_requires_platform(self) -> None:
        """Test that platform is required."""
        with pytest.raises(ValueError):
            Message(content="Test", url="https://example.com")  # type: ignore


class TestConversationThread:
    """Test cases for ConversationThread model."""

    def test_thread_creation_empty_messages(self) -> None:
        """Test creating a thread without messages."""
        thread = ConversationThread(
            title="Test Discussion",
            url="https://reddit.com/r/test/12345",
            platform="reddit",
        )

        assert thread.title == "Test Discussion"
        assert thread.messages == []
        assert len(thread.messages) == 0

    def test_thread_creation_with_messages(self) -> None:
        """Test creating a thread with messages."""
        msg1 = Message(
            content="First message",
            author_initials="A",
            platform="reddit",
            url="https://reddit.com/r/test",
        )
        msg2 = Message(
            content="Second message",
            author_initials="B",
            platform="reddit",
            url="https://reddit.com/r/test",
        )

        thread = ConversationThread(
            title="Discussion",
            url="https://reddit.com/r/test/12345",
            platform="reddit",
            messages=[msg1, msg2],
        )

        assert len(thread.messages) == 2
        assert thread.messages[0].content == "First message"

    def test_thread_scraped_at_default(self) -> None:
        """Test that scraped_at is set to current time."""
        thread = ConversationThread(
            title="Test",
            url="https://reddit.com/r/test/12345",
            platform="reddit",
        )

        assert thread.scraped_at is not None
        assert isinstance(thread.scraped_at, datetime)


class TestScrapingResult:
    """Test cases for ScrapingResult model."""

    def test_successful_scraping_result(self) -> None:
        """Test creating a successful scraping result."""
        result = ScrapingResult(
            success=True,
            url="https://reddit.com/r/test",
            messages_count=5,
        )

        assert result.success is True
        assert result.messages_count == 5
        assert result.error is None

    def test_failed_scraping_result(self) -> None:
        """Test creating a failed scraping result."""
        result = ScrapingResult(
            success=False,
            url="https://reddit.com/r/test",
            error="Connection timeout",
        )

        assert result.success is False
        assert result.error == "Connection timeout"
        assert result.messages_count == 0

    def test_scraping_result_timestamp(self) -> None:
        """Test that timestamp is set automatically."""
        result = ScrapingResult(
            success=True,
            url="https://example.com",
        )

        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)