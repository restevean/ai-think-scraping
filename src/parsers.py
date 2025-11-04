"""HTML parsers for different platforms."""

import logging
from abc import abstractmethod
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from src.abstractions import IParser
from src.models import Message

logger = logging.getLogger(__name__)


class BaseParser(IParser):
    """Base parser class with common parsing logic."""

    def parse(self, html_content: str) -> list[Message]:
        """
        Parse HTML content and extract messages.

        Args:
            html_content: Raw HTML content

        Returns:
            List of extracted Message objects

        Raises:
            ValueError: If parsing fails
        """
        if not html_content or not isinstance(html_content, str):
            raise ValueError("HTML content must be a non-empty string")

        try:
            soup = BeautifulSoup(html_content, "lxml")

            if not soup or not soup.body:
                raise ValueError("Failed to parse HTML: empty or invalid structure")

            messages = self._extract_messages(soup)

            if not messages:
                logger.warning("No messages extracted from HTML")

            return messages

        except Exception as e:
            logger.error(f"Parsing error: {str(e)}")
            raise ValueError(f"Failed to parse HTML: {str(e)}") from e

    @abstractmethod
    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """
        Extract messages from parsed HTML.

        Args:
            soup: BeautifulSoup object with parsed HTML

        Returns:
            List of Message objects

        Note:
            Subclasses implement platform-specific extraction
        """
        pass

    @staticmethod
    def _clean_text(text: Optional[str]) -> str:
        """
        Clean and normalize text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        cleaned = " ".join(text.split())
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    @staticmethod
    def _get_initials(username: Optional[str]) -> Optional[str]:
        """
        Extract initials from username.

        Args:
            username: Username to extract initials from

        Returns:
            Initials or None if username is empty
        """
        if not username or not isinstance(username, str):
            return None

        cleaned = username.strip()
        if not cleaned:
            return None

        words = cleaned.split()
        if len(words) == 1:
            return cleaned[0].upper() if cleaned else None

        initials = "".join(word[0].upper() for word in words if word)
        return initials if initials else None


class RedditParser(BaseParser):
    """Parser for Reddit HTML content."""

    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """
        Extract messages from Reddit HTML.

        Args:
            soup: BeautifulSoup object with parsed HTML

        Returns:
            List of Message objects
        """
        messages = []

        # Reddit comment selectors (these are examples - adjust based on actual structure)
        comment_elements = soup.find_all("div", class_="md") or soup.find_all(
            "div", {"data-type": "comment"}
        )

        for element in comment_elements[:100]:  # Limit to 100 messages
            try:
                content = self._clean_text(element.get_text())

                if not content:
                    continue

                # Try to find author
                author = element.find_previous(class_="author")
                author_initials = None

                if author:
                    author_text = self._clean_text(author.get_text())
                    author_initials = self._get_initials(author_text)

                message = Message(
                    content=content,
                    author_initials=author_initials,
                    platform="reddit",
                    url="https://reddit.com",  # Placeholder
                )

                messages.append(message)

            except Exception as e:
                logger.debug(f"Error extracting Reddit message: {str(e)}")
                continue

        return messages


class StackOverflowParser(BaseParser):
    """Parser for Stack Overflow HTML content."""

    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """
        Extract messages from Stack Overflow HTML.

        Args:
            soup: BeautifulSoup object with parsed HTML

        Returns:
            List of Message objects
        """
        messages = []

        # Stack Overflow post/answer selectors
        post_elements = soup.find_all("div", class_="s-prose") or soup.find_all(
            "div", class_="post-text"
        )

        for element in post_elements[:100]:  # Limit to 100 messages
            try:
                content = self._clean_text(element.get_text())

                if not content:
                    continue

                # Try to find author
                author_elem = element.find_previous(class_="user-details")
                author_initials = None

                if author_elem:
                    author_link = author_elem.find("a")
                    if author_link:
                        author_text = self._clean_text(author_link.get_text())
                        author_initials = self._get_initials(author_text)

                message = Message(
                    content=content,
                    author_initials=author_initials,
                    platform="stackoverflow",
                    url="https://stackoverflow.com",  # Placeholder
                )

                messages.append(message)

            except Exception as e:
                logger.debug(f"Error extracting Stack Overflow message: {str(e)}")
                continue

        return messages


class MediumParser(BaseParser):
    """Parser for Medium HTML content."""

    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """
        Extract messages from Medium HTML.

        Args:
            soup: BeautifulSoup object with parsed HTML

        Returns:
            List of Message objects
        """
        messages = []

        # Medium article/story selectors
        article_elements = soup.find_all("article") or soup.find_all(
            "div", class_="article-content"
        )

        for element in article_elements[:100]:  # Limit to 100 messages
            try:
                content = self._clean_text(element.get_text())

                if not content:
                    continue

                # Try to find author
                author_elem = element.find_previous(class_="author-name")
                author_initials = None

                if author_elem:
                    author_text = self._clean_text(author_elem.get_text())
                    author_initials = self._get_initials(author_text)

                message = Message(
                    content=content,
                    author_initials=author_initials,
                    platform="medium",
                    url="https://medium.com",  # Placeholder
                )

                messages.append(message)

            except Exception as e:
                logger.debug(f"Error extracting Medium message: {str(e)}")
                continue

        return messages


class DevToParser(BaseParser):
    """Parser for Dev.to HTML content."""

    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        """
        Extract messages from Dev.to HTML.

        Args:
            soup: BeautifulSoup object with parsed HTML

        Returns:
            List of Message objects
        """
        messages = []

        # Dev.to article/comment selectors
        content_elements = soup.find_all("div", class_="body") or soup.find_all(
            "div", class_="comment__body"
        )

        for element in content_elements[:100]:  # Limit to 100 messages
            try:
                content = self._clean_text(element.get_text())

                if not content:
                    continue

                # Try to find author
                author_elem = element.find_previous(class_="user-profile")
                author_initials = None

                if author_elem:
                    author_text = self._clean_text(author_elem.get_text())
                    author_initials = self._get_initials(author_text)

                message = Message(
                    content=content,
                    author_initials=author_initials,
                    platform="devto",
                    url="https://dev.to",  # Placeholder
                )

                messages.append(message)

            except Exception as e:
                logger.debug(f"Error extracting Dev.to message: {str(e)}")
                continue

        return messages
