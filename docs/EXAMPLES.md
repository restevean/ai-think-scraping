# Usage Examples

Comprehensive examples for using ThinkScraper in different scenarios.

## Table of Contents

1. [CLI Examples](#cli-examples)
2. [Programmatic Examples](#programmatic-examples)
3. [Advanced Scenarios](#advanced-scenarios)
4. [Troubleshooting](#troubleshooting)

---

## CLI Examples

### Example 1: Simple Single URL Scraping

Scrape a single Reddit URL:

```bash
$ thinkscraper scrape-url https://reddit.com/r/Python

🔍 Scraping: https://reddit.com/r/Python
✅ Success! Extracted 15 messages
```

### Example 2: Single URL with Output File

Scrape and save results:

```bash
$ thinkscraper scrape-url https://reddit.com/r/Python --output results.json

🔍 Scraping: https://reddit.com/r/Python
✅ Success! Extracted 15 messages
📁 Results saved to: results.json
```

**Output file (`results.json`):**

```json
{
  "results": [
    {
      "success": true,
      "url": "https://reddit.com/r/Python",
      "messages_count": 15,
      "error": null,
      "timestamp": "2024-11-04T10:30:00"
    }
  ],
  "summary": {
    "total_urls": 1,
    "successful": 1,
    "failed": 0,
    "total_messages": 15,
    "success_rate": 100.0
  }
}
```

### Example 3: Multiple URLs from File

Create a file with URLs:

```bash
$ cat > urls.txt << EOF
https://reddit.com/r/Python
https://reddit.com/r/JavaScript
https://stackoverflow.com/q/12345
https://medium.com/@author/story
EOF
```

Scrape all URLs:

```bash
$ thinkscraper scrape-urls urls.txt --output results.json

🔍 Scraping 4 URLs from urls.txt
✅ Completed: 3/4 successful
   Total messages extracted: 120
   Success rate: 75.0%
📁 Results saved to: results.json
```

### Example 4: Scraping Specific Platform

Scrape multiple URLs from same platform:

```bash
$ thinkscraper scrape-platform reddit \
    https://reddit.com/r/Python \
    https://reddit.com/r/JavaScript \
    https://reddit.com/r/golang

🔍 Scraping 3 URLs from reddit
✅ Completed: 3/3 successful
   Total messages extracted: 200
   Success rate: 100.0%
```

### Example 5: View Results Summary

Check results without opening file:

```bash
$ thinkscraper show-summary results.json

📊 Scraping Summary:

  Total URLs:        10
  Successful:        8
  Failed:            2
  Total Messages:    245
  Success Rate:      80.0%
```

### Example 6: Export to CSV

Convert JSON results to CSV:

```bash
$ thinkscraper export-results results.json report.csv --format csv

✅ Exported to CSV: report.csv
```

**CSV output (`report.csv`):**

```csv
url,success,messages_count,error
https://reddit.com/r/Python,True,15,
https://stackoverflow.com/q/123,True,8,
https://invalid.com,False,0,No scraper supports URL
```

### Example 7: List Supported Platforms

See all available platforms:

```bash
$ thinkscraper list-platforms

📋 Supported Platforms:

  • devto
  • medium
  • reddit
  • stackoverflow

Usage examples:
  thinkscraper scrape-url https://reddit.com/r/python
  thinkscraper scrape-platform reddit url1 url2 url3
```

---

## Programmatic Examples

### Example 1: Basic Scraping

```python
from src.scrapers import RedditScraper

scraper = RedditScraper()
result = scraper.scrape("https://reddit.com/r/Python")

if result.success:
    print(f"Extracted {result.messages_count} messages")
else:
    print(f"Error: {result.error}")
```

### Example 2: Using Factory

```python
from src.scraper_factory import ScraperFactory

factory = ScraperFactory()
factory.register_scraper("reddit", RedditScraper)

scraper = factory.create_scraper("reddit")
result = scraper.scrape("https://reddit.com/r/Python")
```

### Example 3: Orchestrator - Single URL

```python
from src.orchestrator import Orchestrator
from src.scraper_factory import ScraperFactory

factory = ScraperFactory()
# Register scrapers...

orchestrator = Orchestrator(factory=factory)
result = orchestrator.scrape_url("https://reddit.com/r/Python")
```

### Example 4: Orchestrator - Multiple URLs

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()
# (Uses default factory with all platforms)

urls = [
    "https://reddit.com/r/Python",
    "https://stackoverflow.com/q/123",
    "https://medium.com/@user/story"
]

results = orchestrator.scrape_urls(urls)

# Get summary
summary = orchestrator.get_results_summary()
print(f"Successful: {summary['successful']}/{summary['total_urls']}")
print(f"Total messages: {summary['total_messages']}")
```

### Example 5: Orchestrator - By Platform

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()

urls = [
    "https://reddit.com/r/Python",
    "https://reddit.com/r/JavaScript"
]

results = orchestrator.scrape_platform("reddit", urls)
```

### Example 6: Storage Operations

```python
from src.json_storage import JsonStorage
from src.models import Message

storage = JsonStorage()

# Save
msg = Message(
    content="Great discussion!",
    author_initials="JD",
    platform="reddit",
    url="https://reddit.com/r/test"
)
filepath = storage.save(msg, "my_message")
print(f"Saved to: {filepath}")

# Load
data = storage.load("my_message")
print(data)

# Check existence
if storage.exists("my_message"):
    print("File exists!")

# List all files
files = storage.list_files()
print(f"Found {len(files)} files")

# Delete
storage.delete("my_message")
```

### Example 7: Export Results Programmatically

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()
urls = ["https://reddit.com/r/Python"]

results = orchestrator.scrape_urls(urls)
filepath = orchestrator.export_results("my_results.json")
print(f"Results exported to: {filepath}")
```

### Example 8: Custom Scraping Flow

```python
from src.http_client import HttpClient
from src.scrapers import RedditScraper
from src.models import ScrapingResult

# Create scraper
scraper = RedditScraper()

# Check if URL is supported
url = "https://reddit.com/r/Python"
if scraper.can_handle(url):
    # Scrape
    result = scraper.scrape(url)

    if result.success:
        print(f"Platform: {scraper.platform_name}")
        print(f"Messages: {result.messages_count}")
else:
    print("URL not supported by this scraper")
```

---

## Advanced Scenarios

### Scenario 1: Batch Processing

Process multiple files of URLs:

```bash
#!/bin/bash

for file in urls_*.txt; do
    output="results_${file%.txt}.json"
    echo "Processing $file -> $output"
    thinkscraper scrape-urls "$file" --output "$output"
done

# Generate reports
for result in results_*.json; do
    echo "\n=== Summary for $result ==="
    thinkscraper show-summary "$result"
done

# Combine all to CSV
thinkscraper export-results results_all.json combined_report.csv --format csv
```

### Scenario 2: Custom Factory Setup

```python
from src.scraper_factory import ScraperFactory
from src.scrapers import (
    RedditScraper,
    StackOverflowScraper,
    MediumScraper,
    DevToScraper
)

# Create factory with specific platforms
factory = ScraperFactory()
factory.register_scraper("reddit", RedditScraper)
factory.register_scraper("stackoverflow", StackOverflowScraper)
factory.register_scraper("medium", MediumScraper)
factory.register_scraper("devto", DevToScraper)

# Use factory
orchestrator = Orchestrator(factory=factory)
```

### Scenario 3: Error Handling

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()

urls = [
    "https://reddit.com/r/Python",      # Valid
    "https://invalid.com/page",         # Invalid
    "https://stackoverflow.com/q/123",  # Valid
]

results = orchestrator.scrape_urls(urls)

# Process results
for result in results:
    if result.success:
        print(f"✓ {result.url}: {result.messages_count} messages")
    else:
        print(f"✗ {result.url}: {result.error}")

# Get statistics
summary = orchestrator.get_results_summary()
print(f"\nSummary: {summary['successful']}/{summary['total_urls']} successful")
```

### Scenario 4: Selective Scraping

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Only scrape specific platforms
for platform in ["reddit", "stackoverflow"]:
    urls = [
        f"https://{platform}.com/page1",
        f"https://{platform}.com/page2"
    ]

    print(f"\nScraping {platform}...")
    results = orchestrator.scrape_platform(platform, urls)

    for result in results:
        print(f"  {result.url}: {result.messages_count} messages")
```

### Scenario 5: Results Aggregation

```python
from src.orchestrator import Orchestrator
import json

# Scrape from multiple sources
orchestrator = Orchestrator()

all_results = {
    "reddit": [],
    "stackoverflow": [],
    "medium": [],
    "devto": []
}

for platform in all_results.keys():
    # Get some URLs for each platform (example)
    urls = [f"https://{platform}.com/page"]
    results = orchestrator.scrape_platform(platform, urls)
    all_results[platform] = [r.model_dump() for r in results]

# Save aggregated results
with open("aggregated_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

### Scenario 6: Monitoring and Logging

```python
import logging
from src.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Scrape with logging
orchestrator = Orchestrator()
urls = ["https://reddit.com/r/Python"]

try:
    results = orchestrator.scrape_urls(urls)
    summary = orchestrator.get_results_summary()

    logger.info(f"Scraping completed: {summary['successful']}/{summary['total_urls']}")

except Exception as e:
    logger.error(f"Scraping failed: {str(e)}")
```

### Scenario 7: Custom HTTP Configuration

```python
from src.http_client import HttpClient
from src.orchestrator import Orchestrator

# Create custom HTTP client
http_client = HttpClient(
    timeout=20,        # Longer timeout
    max_retries=5,     # More retries
    retry_delay=3,     # Longer delay
    request_delay=2    # More rate limiting
)

# Use with orchestrator
# (Note: Orchestrator creates its own HttpClient by default)
# This is just to show HttpClient configuration
```

---

## Troubleshooting

### Problem: "No scraper supports URL"

**Cause:** URL is from unsupported platform

**Solution:** Use `list-platforms` to check supported platforms

```bash
$ thinkscraper list-platforms
```

### Problem: "Connection timeout"

**Cause:** Network issue or server too slow

**Solution:** Check internet, wait, or retry

```bash
# Retry with more time
thinkscraper scrape-url <URL> --output results.json
```

### Problem: "File not found"

**Cause:** Input file doesn't exist

**Solution:** Verify file path

```bash
$ ls -la urls.txt
$ thinkscraper scrape-urls urls.txt --output results.json
```

### Problem: "Invalid JSON"

**Cause:** Results file is corrupted

**Solution:** Regenerate results

```bash
$ rm results.json
$ thinkscraper scrape-urls urls.txt --output results.json
```

### Problem: Low success rate

**Cause:**
- Invalid URLs
- Website structure changed
- Being rate-limited

**Solution:**
- Verify URLs
- Check if website has changed
- Wait and retry

```bash
$ thinkscraper scrape-urls urls.txt --output results.json
$ thinkscraper show-summary results.json
```

---

## Performance Tips

1. **Batch multiple URLs** instead of one at a time
   ```bash
   # Good: Process all at once
   thinkscraper scrape-urls urls.txt --output results.json

   # Avoid: One by one
   for url in $(cat urls.txt); do
       thinkscraper scrape-url "$url"
   done
   ```

2. **Use platform-specific scraping** when possible
   ```bash
   # Faster: One scraper initialization
   thinkscraper scrape-platform reddit url1 url2 url3

   # Slower: Factory finds scraper each time
   thinkscraper scrape-urls urls.txt
   ```

3. **Export results once**
   ```bash
   # Good: Single export
   thinkscraper export-results results.json export.csv --format csv

   # Avoid: Multiple exports
   thinkscraper show-summary results.json
   thinkscraper export-results results.json report1.csv
   thinkscraper export-results results.json report2.json
   ```

---

## Complete Workflow Example

```bash
# 1. Create URLs file
cat > urls.txt << EOF
https://reddit.com/r/Python
https://reddit.com/r/JavaScript
https://stackoverflow.com/q/12345
https://medium.com/@author/story
https://dev.to/user/article
EOF

# 2. Scrape all URLs
echo "Starting scraping..."
thinkscraper scrape-urls urls.txt --output results.json

# 3. Check results
echo "\nResults:"
thinkscraper show-summary results.json

# 4. Export to CSV
thinkscraper export-results results.json report.csv --format csv

# 5. Verify output
echo "\nExported files:"
ls -lh results.json report.csv

# 6. View first few lines of CSV
echo "\nCSV Preview:"
head -5 report.csv
```

**Output:**

```
Starting scraping...
🔍 Scraping 5 URLs from urls.txt
✅ Completed: 4/5 successful
   Total messages extracted: 150
   Success rate: 80.0%
📁 Results saved to: results.json

Results:
📊 Scraping Summary:

  Total URLs:        5
  Successful:        4
  Failed:            1
  Total Messages:    150
  Success Rate:      80.0%

Exported files:
-rw-r--r--  1 user  staff  2.5K Nov  4 10:30 results.json
-rw-r--r--  1 user  staff  1.2K Nov  4 10:31 report.csv

CSV Preview:
url,success,messages_count,error
https://reddit.com/r/Python,True,35,
https://reddit.com/r/JavaScript,True,42,
...
```

---

**See also:** [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details