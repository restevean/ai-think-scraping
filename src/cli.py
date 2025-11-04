"""Command-line interface for AI THINK Scrapping."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from src.json_storage import JsonStorage
from src.orchestrator import Orchestrator
from src.scraper_factory import ScraperFactory
from src.scrapers import DevToScraper, MediumScraper, RedditScraper, StackOverflowScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_factory() -> ScraperFactory:
    """Create and configure scraper factory with all scrapers."""
    factory = ScraperFactory()
    factory.register_scraper("reddit", RedditScraper)
    factory.register_scraper("stackoverflow", StackOverflowScraper)
    factory.register_scraper("medium", MediumScraper)
    factory.register_scraper("devto", DevToScraper)
    return factory


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """ThinkScraper - Web scraper for conversations and opinions."""
    pass


@cli.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for results (JSON)",
)
def scrape_url(url: str, output: Optional[str]) -> None:
    """Scrape a single URL."""
    try:
        click.echo(f"🔍 Scraping: {url}")

        factory = setup_factory()
        orchestrator = Orchestrator(factory=factory)

        result = orchestrator.scrape_url(url)

        if result.success:
            click.echo(
                click.style(
                    f"✅ Success! Extracted {result.messages_count} messages",
                    fg="green",
                )
            )
        else:
            click.echo(
                click.style(
                    f"❌ Failed: {result.error}",
                    fg="red",
                )
            )

        if output:
            filepath = orchestrator.export_results(output)
            click.echo(f"📁 Results saved to: {filepath}")

    except ValueError as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {str(e)}", fg="red"), err=True)
        logger.exception("Unexpected error in scrape_url")
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.File("r"))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output file path for results (JSON)",
)
@click.option(
    "--skip-errors",
    is_flag=True,
    help="Continue scraping even if some URLs fail",
)
def scrape_urls(input_file, output: str, skip_errors: bool) -> None:
    """Scrape multiple URLs from a file.

    INPUT_FILE should contain one URL per line.
    """
    try:
        # Read URLs from file
        urls = [line.strip() for line in input_file if line.strip()]

        if not urls:
            click.echo(click.style("❌ No URLs found in input file", fg="red"), err=True)
            sys.exit(1)

        click.echo(f"🔍 Scraping {len(urls)} URLs from {input_file.name}")

        factory = setup_factory()
        orchestrator = Orchestrator(factory=factory)

        results = orchestrator.scrape_urls(urls)

        summary = orchestrator.get_results_summary()

        click.echo(
            click.style(
                f"\n✅ Completed: {summary['successful']}/{summary['total_urls']} successful",
                fg="green",
            )
        )
        click.echo(f"   Total messages extracted: {summary['total_messages']}")
        click.echo(f"   Success rate: {summary['success_rate']:.1f}%")

        if output:
            filepath = orchestrator.export_results(output)
            click.echo(f"📁 Results saved to: {filepath}")

    except FileNotFoundError:
        click.echo(
            click.style(f"❌ Input file not found: {input_file.name}", fg="red"),
            err=True,
        )
        sys.exit(1)
    except ValueError as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {str(e)}", fg="red"), err=True)
        logger.exception("Unexpected error in scrape_urls")
        sys.exit(1)


@cli.command()
@click.argument("platform")
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for results (JSON)",
)
def scrape_platform(platform: str, urls, output: Optional[str]) -> None:
    """Scrape multiple URLs from a specific platform.

    PLATFORM: Platform name (reddit, stackoverflow, medium, devto)
    URLS: One or more URLs to scrape
    """
    try:
        if not urls:
            click.echo(click.style("❌ At least one URL is required", fg="red"), err=True)
            sys.exit(1)

        click.echo(f"🔍 Scraping {len(urls)} URLs from {platform}")

        factory = setup_factory()
        orchestrator = Orchestrator(factory=factory)

        results = orchestrator.scrape_platform(platform, list(urls))

        summary = orchestrator.get_results_summary()

        click.echo(
            click.style(
                f"\n✅ Completed: {summary['successful']}/{summary['total_urls']} successful",
                fg="green",
            )
        )
        click.echo(f"   Total messages extracted: {summary['total_messages']}")
        click.echo(f"   Success rate: {summary['success_rate']:.1f}%")

        if output:
            filepath = orchestrator.export_results(output)
            click.echo(f"📁 Results saved to: {filepath}")

    except ValueError as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {str(e)}", fg="red"), err=True)
        logger.exception("Unexpected error in scrape_platform")
        sys.exit(1)


@cli.command()
def list_platforms() -> None:
    """List all supported platforms."""
    factory = setup_factory()
    platforms = factory.supported_platforms

    click.echo(click.style("📋 Supported Platforms:", fg="blue", bold=True))
    click.echo()

    for platform in platforms:
        click.echo(f"  • {platform}")

    click.echo()
    click.echo("Usage examples:")
    click.echo("  thinkscraper scrape-url https://reddit.com/r/python")
    click.echo("  thinkscraper scrape-platform reddit url1 url2 url3")


@cli.command()
@click.argument("input_file", type=click.File("r"))
@click.argument("output_file", type=click.Path())
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format (default: json)",
)
def export_results(input_file, output_file: str, output_format: str) -> None:
    """Export results from a JSON file to different formats.

    INPUT_FILE: Results JSON file from scraping
    OUTPUT_FILE: Path for exported results
    """
    try:
        data = json.load(input_file)

        if output_format == "json":
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            click.echo(click.style(f"✅ Exported to JSON: {output_file}", fg="green"))

        elif output_format == "csv":
            import csv

            if "results" not in data:
                click.echo(
                    click.style("❌ Invalid results format", fg="red"),
                    err=True,
                )
                sys.exit(1)

            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["url", "success", "messages_count", "error"]
                )
                writer.writeheader()

                for result in data["results"]:
                    writer.writerow(
                        {
                            "url": result.get("url", ""),
                            "success": result.get("success", False),
                            "messages_count": result.get("messages_count", 0),
                            "error": result.get("error", ""),
                        }
                    )

            click.echo(click.style(f"✅ Exported to CSV: {output_file}", fg="green"))

    except json.JSONDecodeError:
        click.echo(
            click.style("❌ Invalid JSON input file", fg="red"),
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(
            click.style(f"❌ Export error: {str(e)}", fg="red"),
            err=True,
        )
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.File("r"))
def show_summary(input_file) -> None:
    """Show summary of a results file.

    INPUT_FILE: Results JSON file from scraping
    """
    try:
        data = json.load(input_file)

        if "summary" not in data:
            click.echo(
                click.style("❌ Invalid results file format", fg="red"),
                err=True,
            )
            sys.exit(1)

        summary = data["summary"]

        click.echo(click.style("📊 Scraping Summary:", fg="blue", bold=True))
        click.echo()
        click.echo(f"  Total URLs:        {summary['total_urls']}")
        click.echo(
            click.style(
                f"  Successful:        {summary['successful']}",
                fg="green",
            )
        )
        click.echo(
            click.style(
                f"  Failed:            {summary['failed']}",
                fg="red" if summary["failed"] > 0 else "green",
            )
        )
        click.echo(f"  Total Messages:    {summary['total_messages']}")
        click.echo(
            f"  Success Rate:      {summary['success_rate']:.1f}%"
        )

    except json.JSONDecodeError:
        click.echo(
            click.style("❌ Invalid JSON file", fg="red"),
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(
            click.style(f"❌ Error: {str(e)}", fg="red"),
            err=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    cli()