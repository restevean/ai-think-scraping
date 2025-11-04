"""Tests for CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.cli import cli, scrape_platform, scrape_url, scrape_urls


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self) -> None:
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "ThinkScraper" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestScrapeUrlCommand:
    """Test scrape-url command."""

    def test_scrape_url_help(self) -> None:
        """Test scrape-url help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-url", "--help"])

        assert result.exit_code == 0
        assert "Scrape a single URL" in result.output

    def test_scrape_url_requires_url(self) -> None:
        """Test that scrape-url requires URL argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-url"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output

    @patch("src.orchestrator.Orchestrator.scrape_url")
    def test_scrape_url_success(self, mock_scrape) -> None:
        """Test successful scrape-url command."""
        from src.models import ScrapingResult

        mock_scrape.return_value = ScrapingResult(
            success=True, url="https://reddit.com/r/test", messages_count=5
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-url", "https://reddit.com/r/test"])

        assert result.exit_code == 0
        assert "✅" in result.output or "Success" in result.output

    @patch("src.orchestrator.Orchestrator.scrape_url")
    def test_scrape_url_failure(self, mock_scrape) -> None:
        """Test failed scrape-url command."""
        from src.models import ScrapingResult

        mock_scrape.return_value = ScrapingResult(
            success=False,
            url="https://invalid.com",
            error="URL not supported",
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-url", "https://invalid.com"])

        assert "❌" in result.output or "Failed" in result.output

    @patch("src.orchestrator.Orchestrator.scrape_url")
    @patch("src.orchestrator.Orchestrator.export_results")
    def test_scrape_url_with_output(self, mock_export, mock_scrape) -> None:
        """Test scrape-url with output file."""
        from src.models import ScrapingResult

        mock_scrape.return_value = ScrapingResult(
            success=True, url="https://reddit.com/r/test", messages_count=5
        )
        mock_export.return_value = "/tmp/results.json"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scrape-url", "https://reddit.com/r/test", "--output", "/tmp/results.json"],
        )

        assert result.exit_code == 0
        assert "📁" in result.output or "Results saved" in result.output


class TestScrapeUrlsCommand:
    """Test scrape-urls command."""

    def test_scrape_urls_help(self) -> None:
        """Test scrape-urls help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-urls", "--help"])

        assert result.exit_code == 0
        assert "multiple URLs" in result.output

    def test_scrape_urls_requires_input_and_output(self) -> None:
        """Test that scrape-urls requires input and output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-urls"])

        assert result.exit_code != 0

    def test_scrape_urls_input_file_not_found(self) -> None:
        """Test scrape-urls with non-existent input file."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scrape-urls", "/nonexistent/file.txt", "--output", "/tmp/output.json"],
        )

        assert result.exit_code != 0
        assert "no such file" in result.output.lower() or "not found" in result.output.lower()

    def test_scrape_urls_empty_input_file(self) -> None:
        """Test scrape-urls with empty input file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("urls.txt", "w") as f:
                f.write("")

            result = runner.invoke(
                cli,
                ["scrape-urls", "urls.txt", "--output", "output.json"],
            )

            assert result.exit_code != 0
            assert "No URLs found" in result.output

    @patch("src.orchestrator.Orchestrator.scrape_urls")
    @patch("src.orchestrator.Orchestrator.get_results_summary")
    @patch("src.orchestrator.Orchestrator.export_results")
    def test_scrape_urls_success(self, mock_export, mock_summary, mock_scrape) -> None:
        """Test successful scrape-urls command."""
        from src.models import ScrapingResult

        mock_scrape.return_value = [
            ScrapingResult(success=True, url="url1", messages_count=5),
            ScrapingResult(success=True, url="url2", messages_count=3),
        ]
        mock_summary.return_value = {
            "total_urls": 2,
            "successful": 2,
            "failed": 0,
            "total_messages": 8,
            "success_rate": 100.0,
        }
        mock_export.return_value = "output.json"

        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("urls.txt", "w") as f:
                f.write("https://example.com/url1\n")
                f.write("https://example.com/url2\n")

            result = runner.invoke(
                cli,
                ["scrape-urls", "urls.txt", "--output", "output.json"],
            )

            assert result.exit_code == 0
            assert "Completed" in result.output


class TestScrapePlatformCommand:
    """Test scrape-platform command."""

    def test_scrape_platform_help(self) -> None:
        """Test scrape-platform help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-platform", "--help"])

        assert result.exit_code == 0
        assert "specific platform" in result.output

    def test_scrape_platform_requires_arguments(self) -> None:
        """Test that scrape-platform requires platform and URLs."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape-platform"])

        assert result.exit_code != 0

    @patch("src.orchestrator.Orchestrator.scrape_platform")
    @patch("src.orchestrator.Orchestrator.get_results_summary")
    def test_scrape_platform_success(self, mock_summary, mock_scrape) -> None:
        """Test successful scrape-platform command."""
        from src.models import ScrapingResult

        mock_scrape.return_value = [
            ScrapingResult(success=True, url="https://reddit.com/r/test", messages_count=5),
        ]
        mock_summary.return_value = {
            "total_urls": 1,
            "successful": 1,
            "failed": 0,
            "total_messages": 5,
            "success_rate": 100.0,
        }

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scrape-platform", "reddit", "https://reddit.com/r/test"],
        )

        assert result.exit_code == 0
        assert "Completed" in result.output


class TestListPlatformsCommand:
    """Test list-platforms command."""

    def test_list_platforms(self) -> None:
        """Test list-platforms command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-platforms"])

        assert result.exit_code == 0
        assert "Supported Platforms" in result.output
        assert "reddit" in result.output
        assert "stackoverflow" in result.output


class TestExportResultsCommand:
    """Test export-results command."""

    def test_export_results_help(self) -> None:
        """Test export-results help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["export-results", "--help"])

        assert result.exit_code == 0
        assert "Export results" in result.output

    def test_export_results_json_to_json(self) -> None:
        """Test exporting JSON to JSON."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create input file
            input_data = {
                "results": [
                    {"url": "url1", "success": True, "messages_count": 5, "error": None}
                ],
                "summary": {
                    "total_urls": 1,
                    "successful": 1,
                    "failed": 0,
                    "total_messages": 5,
                    "success_rate": 100.0,
                },
            }

            with open("input.json", "w") as f:
                json.dump(input_data, f)

            result = runner.invoke(
                cli,
                ["export-results", "input.json", "output.json"],
            )

            assert result.exit_code == 0
            assert Path("output.json").exists()

    def test_export_results_json_to_csv(self) -> None:
        """Test exporting JSON to CSV."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create input file
            input_data = {
                "results": [
                    {"url": "url1", "success": True, "messages_count": 5, "error": None}
                ],
                "summary": {
                    "total_urls": 1,
                    "successful": 1,
                    "failed": 0,
                    "total_messages": 5,
                    "success_rate": 100.0,
                },
            }

            with open("input.json", "w") as f:
                json.dump(input_data, f)

            result = runner.invoke(
                cli,
                ["export-results", "input.json", "output.csv", "--format", "csv"],
            )

            assert result.exit_code == 0
            assert Path("output.csv").exists()

    def test_export_results_invalid_input(self) -> None:
        """Test export with invalid input file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("invalid.json", "w") as f:
                f.write("not valid json")

            result = runner.invoke(
                cli,
                ["export-results", "invalid.json", "output.json"],
            )

            assert result.exit_code != 0
            assert "Invalid JSON" in result.output


class TestShowSummaryCommand:
    """Test show-summary command."""

    def test_show_summary_success(self) -> None:
        """Test show-summary with valid results file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            data = {
                "results": [],
                "summary": {
                    "total_urls": 10,
                    "successful": 8,
                    "failed": 2,
                    "total_messages": 100,
                    "success_rate": 80.0,
                },
            }

            with open("results.json", "w") as f:
                json.dump(data, f)

            result = runner.invoke(cli, ["show-summary", "results.json"])

            assert result.exit_code == 0
            assert "Scraping Summary" in result.output
            assert "Total URLs:" in result.output

    def test_show_summary_invalid_file(self) -> None:
        """Test show-summary with invalid file."""
        runner = CliRunner()

        result = runner.invoke(cli, ["show-summary", "/nonexistent/file.json"])

        assert result.exit_code != 0