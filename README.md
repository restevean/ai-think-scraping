# ThinkScraper

Web scraper for collecting opinions, messages and conversations from multiple platforms about software development.

## Requirements

- Python 3.12+
- UV for environment and dependency management

## Installation

```bash
# Clone the repository
git clone <repo>
cd ai-think-scrapping

# Create virtual environment with UV
uv venv

# Activate environment
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev]"
```

## Quick Start

```bash
# List supported platforms
thinkscraper list-platforms

# Scrape a URL
thinkscraper scrape-url https://reddit.com/r/Python

# Scrape multiple URLs
thinkscraper scrape-urls urls.txt --output results.json

# View results summary
thinkscraper show-summary results.json

# Export to CSV
thinkscraper export-results results.json report.csv --format csv
```

## Supported Platforms

- Reddit
- Stack Overflow
- Medium
- Dev.to

## Project Structure

```
ai-think-scrapping/
├── src/
│   ├── abstractions.py      # Interfaces (IScraper, IHttpClient, etc.)
│   ├── base_scraper.py      # Template Method pattern
│   ├── cli.py               # Click CLI interface
│   ├── config.py            # Centralised configuration
│   ├── http_client.py       # HTTP client with retries
│   ├── json_storage.py      # JSON storage
│   ├── models.py            # Pydantic models (Message, ScrapingResult)
│   ├── orchestrator.py      # Scrapers coordinator
│   ├── parsers.py           # Platform-specific parsers
│   ├── scraper_factory.py   # Factory Pattern
│   └── scrapers.py          # Platform scrapers
├── tests/
│   ├── test_abstractions.py
│   ├── test_cli.py
│   ├── test_implementations.py
│   ├── test_models.py
│   ├── test_orchestrator.py
│   └── test_scrapers.py
├── docs/
│   ├── ARCHITECTURE.md      # Technical architecture and design
│   ├── EXAMPLES.md          # Use cases and examples
│   └── README.md            # Documentation index
└── data/                    # JSON results
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Specific tests
pytest tests/test_cli.py -v
```

## Features

✅ Multi-platform scraping
✅ Professional CLI with Click
✅ SOLID architecture
✅ Comprehensive tests with TDD
✅ Robust error handling
✅ Automatic rate limiting and retries
✅ Export to JSON and CSV
✅ Type hints and validation with Pydantic
✅ Code coverage >95%

## Documentation

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Technical architecture, design patterns and SOLID principles
- [EXAMPLES.md](./docs/EXAMPLES.md) - Use cases, CLI and programmatic examples
- [docs/README.md](./docs/README.md) - Documentation index

## Licence

MIT

# Detailed Explanation of ThinkScraper Command

## Level 1: General Structure

ThinkScraper is a **CLI (Command Line Interface) tool** that works with the structure:

```bash
thinkscraper [COMMAND] [ARGUMENTS] [OPTIONS]
```

It has **7 main commands**.

---

## Level 2: Available Commands

### 1️⃣ `list-platforms` (The simplest)

```bash
thinkscraper list-platforms
```

**What it does:** Shows the platforms that ThinkScraper supports.

**Output:**
```
📋 Supported Platforms:
  • devto
  • medium
  • reddit
  • stackoverflow
```

---

### 2️⃣ `scrape-url` (Single URL, simple)

```bash
thinkscraper scrape-url "https://reddit.com/r/Python"
```

**What it does:** Scrapes a single URL by automatically detecting its platform.

**With output option:**
```bash
thinkscraper scrape-url "https://reddit.com/r/Python" --output result.json
```

**Output:**
```
🔍 Scraping: https://reddit.com/r/Python
✅ Success! Extracted 15 messages
📁 Results saved to: result.json
```

---

### 3️⃣ `scrape-urls` (Multiple URLs from file)

First, create a text file:

```bash
cat > urls.txt << EOF
https://reddit.com/r/Python
https://stackoverflow.com/questions/123
https://medium.com/@author/article
EOF
```

Then scrape it:

```bash
thinkscraper scrape-urls urls.txt --output results.json
```

**What it does:**
- Reads ALL URLs from the `urls.txt` file (one per line)
- Scrapes each one by automatically detecting its platform
- Saves combined results to `results.json`
- Generates a statistical summary

**Output:**
```
🔍 Scraping 3 URLs from urls.txt
✅ Completed: 3/3 successful
   Total messages extracted: 120
   Success rate: 100.0%
📁 Results saved to: results.json
```

**Important option:**
```bash
thinkscraper scrape-urls urls.txt --output results.json --skip-errors
```

The `--skip-errors` option makes it continue even if some URLs fail. Without it, if one URL fails, EVERYTHING stops.

---

### 4️⃣ `scrape-platform` (Multiple URLs from ONE platform)

```bash
thinkscraper scrape-platform reddit \
  https://reddit.com/r/Python \
  https://reddit.com/r/JavaScript \
  https://reddit.com/golang
```

**What it does:**
- Scrapes multiple URLs from the SAME platform
- It's more efficient than `scrape-urls` because **it doesn't need to detect the platform for each URL**
- Uses the same scraper for all (faster)

**Performance advantage:**
```
scrape-urls     → Detects platform 3 times (slow)
scrape-platform → Uses the same scraper 3 times (fast)
```

---

### 5️⃣ `show-summary` (View results summary)

```bash
thinkscraper show-summary results.json
```

**What it does:** Shows a summary of extracted data without opening the JSON file.

**Output:**
```
📊 Scraping Summary:

  Total URLs:        5
  Successful:        4
  Failed:            1
  Total Messages:    245
  Success Rate:      80.0%
```

---

### 6️⃣ `export-results` (Convert JSON to another format)

```bash
thinkscraper export-results results.json report.csv --format csv
```

**What it does:** Converts the JSON results to CSV (or keeps JSON).

**Available formats:**
- `--format json` → Keeps JSON format
- `--format csv` → Converts to CSV

**Resulting CSV:**
```csv
url,success,messages_count,error
https://reddit.com/r/Python,True,15,
https://stackoverflow.com/q/123,True,8,
https://invalid.com,False,0,No scraper supports URL
```

---

## Level 3: Output JSON Structure

When you scrape and use `--output`, you get something like:

```json
{
  "results": [
    {
      "success": true,
      "url": "https://reddit.com/r/Python",
      "messages_count": 15,
      "error": null,
      "timestamp": "2024-11-04T10:30:00"
    },
    {
      "success": false,
      "url": "https://invalid.com",
      "messages_count": 0,
      "error": "No scraper supports URL",
      "timestamp": "2024-11-04T10:31:00"
    }
  ],
  "summary": {
    "total_urls": 2,
    "successful": 1,
    "failed": 1,
    "total_messages": 15,
    "success_rate": 50.0
  }
}
```

---

## Level 4: Complete Flow (How to use them together)

**Step 1:** Create file with URLs
```bash
cat > my_urls.txt << EOF
https://reddit.com/r/Python
https://stackoverflow.com/questions/12345
https://medium.com/@author/article
EOF
```

**Step 2:** Scrape all
```bash
thinkscraper scrape-urls my_urls.txt --output results.json
```

**Step 3:** View summary
```bash
thinkscraper show-summary results.json
```

**Step 4:** Export to CSV for analysis
```bash
thinkscraper export-results results.json report.csv --format csv
```

**Final result:** `report.csv` ready to open in Excel.

---

## Level 5: Available Options per Command

### `thinkscraper scrape-url`
- `--output, -o` → Output file (JSON)
- `--help` → Show help

### `thinkscraper scrape-urls`
- `--output, -o` → Output file (JSON) [REQUIRED]
- `--skip-errors` → Continue if there are errors
- `--help` → Show help

### `thinkscraper scrape-platform`
- `--output, -o` → Output file (JSON)
- `--help` → Show help

### `thinkscraper export-results`
- `--format` → Output format (json, csv) [default: json]
- `--help` → Show help

---

## Visual Summary of All Commands

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `list-platforms` | View supported platforms | None | Terminal |
| `scrape-url` | Scrape 1 URL | URL in terminal | JSON (optional) |
| `scrape-urls` | Scrape N URLs | .txt file | JSON with summary |
| `scrape-platform` | Scrape N URLs same platform | Platform + URLs | JSON with summary |
| `show-summary` | View results summary | Previous JSON | Terminal |
| `export-results` | Convert JSON format to CSV | Previous JSON | CSV or JSON |

---

## Common Use Cases

### Case 1: Simple scraping of a Reddit URL
```bash
thinkscraper scrape-url https://reddit.com/r/Python
```

### Case 2: Scraping multiple URLs with report
```bash
thinkscraper scrape-urls urls.txt --output results.json
thinkscraper show-summary results.json
thinkscraper export-results results.json report.csv --format csv
```

### Case 3: Scraping by platform
```bash
thinkscraper scrape-platform stackoverflow \
  https://stackoverflow.com/q/1 \
  https://stackoverflow.com/q/2 \
  https://stackoverflow.com/q/3 \
  --output so_results.json
```

### Case 4: Complete workflow
```bash
cat > urls.txt << EOF
https://reddit.com/r/python
https://stackoverflow.com/q/123
https://medium.com/@user/story
EOF

thinkscraper scrape-urls urls.txt --output results.json
thinkscraper show-summary results.json
thinkscraper export-results results.json export.csv --format csv
```

---

## Troubleshooting

### Error: "command not found: thinkscraper"
**Solution:** Run:
```bash
uv pip install -e .
```

### Error: "No scraper supports URL"
**Solution:** Verify that the URL is from a supported platform. Use `list-platforms` to see the available ones.

### One URL fails and everything stops
**Solution:** Use the `--skip-errors` option:
```bash
thinkscraper scrape-urls urls.txt --output results.json --skip-errors
```