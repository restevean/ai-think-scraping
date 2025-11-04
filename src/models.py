"""Data models for AI THINK Scrapping."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents a single message or conversation entry."""

    content: str = Field(..., description="Message content")
    author_initials: Optional[str] = Field(default=None, description="Author initials if available")
    date: Optional[datetime] = Field(default=None, description="Message date/timestamp")
    platform: str = Field(..., description="Source platform (reddit, stackoverflow, etc)")
    url: str = Field(..., description="URL where message was found")


class ConversationThread(BaseModel):
    """Represents a conversation thread with multiple messages."""

    title: str = Field(..., description="Thread title")
    url: str = Field(..., description="Thread URL")
    platform: str = Field(..., description="Source platform")
    messages: list[Message] = Field(default_factory=list, description="List of messages in thread")
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the thread was scraped",
    )


class ScrapingResult(BaseModel):
    """Result of a scraping operation."""

    success: bool = Field(..., description="Whether scraping was successful")
    url: str = Field(..., description="URL that was scraped")
    messages_count: int = Field(default=0, description="Number of messages extracted")
    error: Optional[str] = Field(default=None, description="Error message if scraping failed")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When scraping occurred"
    )
