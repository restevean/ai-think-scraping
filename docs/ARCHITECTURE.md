# Architecture Guide

## Overview

ThinkScraper is built on **SOLID principles** and modern Python best practices. This guide explains the architecture and design decisions.

## Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│               CLI (Click)                        │
│       User-facing command interface              │
└────────────────────┬─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│              Orchestrator                        │
│       Coordinates multiple scrapers              │
│  • scrape_url()                                  │
│  • scrape_urls()                                 │
│  • scrape_platform()                             │
│  • export_results()                              │
└────────────────────┬─────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌─────────▼─────────┐
│ ScraperFactory   │    │  JsonStorage      │
│                  │    │                   │
│ Creates scrapers │    │ Saves/loads data  │
│ Registers        │    │ in JSON format    │
│ platforms        │    │                   │
└────────┬─────────┘    └───────────────────┘
         │
    ┌────┴────────────────────────────────────┐
    │                                         │
┌───▼──────┐  ┌───▼──────┐  ┌───▼──────┐  ┌───▼──────┐
│  Reddit  │  │  Stack   │  │  Medium  │  │  Dev.to  │
│ Scraper  │  │ Overflow │  │ Scraper  │  │ Scraper  │
│          │  │ Scraper  │  │          │  │          │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────┬───┴───────┬─────┴─────────────┘             
               │           │                   
        ┌──────▼─────┐  ┌──▼──────────┐
        │ HttpClient │  │   Parser    │
        │            │  │             │
        │ • Retry    │  │ Parse HTML  │
        │ • Rate     │  │ & extract   │
        │   limit    │  │ messages    │
        │ • Timeout  │  │             │
        └────────────┘  └─────────────┘
```

## Core Components

### 1. Models (`src/models.py`)

**Pydantic models** for type-safe data structures.

```python
class Message(BaseModel):
    """Single message extracted from a platform"""
    content: str
    author_initials: Optional[str]
    date: Optional[datetime]
    platform: str
    url: str

class ScrapingResult(BaseModel):
    """Result of a scraping operation"""
    success: bool
    url: str
    messages_count: int
    error: Optional[str]
    timestamp: datetime
```

**Why Pydantic:**
- Automatic validation
- Type safety
- Easy JSON serialization
- IDE autocomplete

### 2. Abstractions (`src/abstractions.py`)

**Interfaces** defining contracts between components.

```python
class IHttpClient(ABC):
    """HTTP client interface"""
    @abstractmethod
    def get(self, url: str, timeout: Optional[int] = None) -> str:
        pass
    
    @abstractmethod
    def head(self, url: str, timeout: Optional[int] = None) -> dict:
        pass

class IScraper(ABC):
    """Scraper interface"""
    @abstractmethod
    def scrape(self, url: str) -> ScrapingResult:
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass
```

**Why Abstractions:**
- Loose coupling
- Easy to mock in tests
- Multiple implementations
- Clear contracts

### 3. HttpClient (`src/http_client.py`)

**HTTP client with retry logic and rate limiting**.

Features:
- ✓ Automatic retries with exponential backoff
- ✓ Rate limiting (1 second between requests)
- ✓ Configurable timeouts
- ✓ User agent spoofing
- ✓ Context manager support

```python
with HttpClient() as client:
    content = client.get("https://example.com")
```

### 4. Storage (`src/json_storage.py`)

**JSON file storage** for scraping results.

```python
storage = JsonStorage()
storage.save(result, "my_results")  # Saves to data/my_results.json
data = storage.load("my_results")
```

### 5. ScraperFactory (`src/scraper_factory.py`)

**Factory Pattern** for creating scrapers.

```python
factory = ScraperFactory()
factory.register_scraper("reddit", RedditScraper)
factory.register_scraper("stackoverflow", StackOverflowScraper)

scraper = factory.create_scraper("reddit")
```

**Why Factory Pattern:**
- Centralized object creation
- Easy to add new platforms
- Runtime platform selection
- Extensible without modification

### 6. BaseScraper (`src/base_scraper.py`)

**Template Method Pattern** with common scraping logic.

```python
class BaseScraper(IScraper):
    def scrape(self, url: str) -> ScrapingResult:
        # Common logic:
        # 1. Validate URL
        # 2. Check if can handle
        # 3. Fetch HTML
        # 4. Parse content
        # 5. Return result
        
    @abstractmethod
    def _get_parser(self) -> IParser:
        """Subclasses implement this"""
        pass
```

**Why Template Method:**
- DRY (Don't Repeat Yourself)
- Consistent behavior
- Easy to extend

### 7. Parsers (`src/parsers.py`)

**HTML parsing** specific to each platform.

```python
class RedditParser(BaseParser):
    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        # Reddit-specific parsing logic
        pass

class StackOverflowParser(BaseParser):
    def _extract_messages(self, soup: BeautifulSoup) -> list[Message]:
        # Stack Overflow-specific parsing logic
        pass
```

### 8. Platform Scrapers (`src/scrapers.py`)

**Minimal implementations** for each platform.

```python
class RedditScraper(BaseScraper):
    def _get_parser(self) -> IParser:
        return RedditParser()
    
    def _get_supported_domains(self) -> list[str]:
        return ["reddit.com", "old.reddit.com"]
    
    @property
    def platform_name(self) -> str:
        return "reddit"
```

### 9. Orchestrator (`src/orchestrator.py`)

**Coordinator** managing multiple scrapers.

```python
orchestrator = Orchestrator(factory, storage)

# Single URL
result = orchestrator.scrape_url("https://reddit.com/r/python")

# Multiple URLs
results = orchestrator.scrape_urls([url1, url2, url3])

# Specific platform
results = orchestrator.scrape_platform("reddit", [url1, url2])

# Export
orchestrator.export_results("results.json")
```

### 10. CLI (`src/cli.py`)

**User interface** using Click framework.

```bash
thinkscraper scrape-url <URL>
thinkscraper scrape-urls <FILE>
thinkscraper scrape-platform <PLATFORM> <URLs>
thinkscraper list-platforms
thinkscraper export-results <FILE>
thinkscraper show-summary <FILE>
```

## Design Patterns Used

### 1. Factory Pattern
**File:** `src/scraper_factory.py`

Creates scrapers based on platform name. Allows adding new platforms without modifying existing code.

```python
factory = ScraperFactory()
factory.register_scraper("reddit", RedditScraper)
scraper = factory.create_scraper("reddit")
```

### 2. Template Method Pattern
**File:** `src/base_scraper.py`

Defines algorithm structure in base class, lets subclasses implement specific steps.

```python
class BaseScraper(IScraper):
    def scrape(self, url: str):
        # Template: validate → fetch → parse → return
        pass
```

### 3. Strategy Pattern
**File:** `src/parsers.py`

Different parsing strategies for different platforms.

```python
class RedditParser(BaseParser): ...
class StackOverflowParser(BaseParser): ...
```

### 4. Dependency Injection
**File:** `src/orchestrator.py`, `src/base_scraper.py`

Dependencies passed to constructors, not created inside.

```python
orchestrator = Orchestrator(
    factory=my_factory,
    storage=my_storage
)
```

## SOLID Principles Applied

### Single Responsibility
- `HttpClient`: Only HTTP operations
- `JsonStorage`: Only file I/O
- `RedditScraper`: Only Reddit scraping

### Open/Closed
- `ScraperFactory`: Open for new platforms, closed for modification
- `IScraper`: New scrapers extend without changing interface

### Liskov Substitution
- Any `IScraper` implementation can replace another
- `HttpClient` and mocked client are interchangeable

### Interface Segregation
- `IHttpClient`: Only HTTP methods
- `IStorage`: Only storage methods
- `IScraper`: Only scraping methods

### Dependency Inversion
- Classes depend on `IScraper`, not concrete scrapers
- Factory handles creation, not caller

## Data Flow

### Scraping Flow

```
User Input (CLI)
    ↓
Orchestrator.scrape_url(url)
    ↓
Find appropriate scraper via Factory
    ↓
HttpClient.get(url)
    ↓
Parser.parse(html)
    ↓
List[Message] extracted
    ↓
ScrapingResult created
    ↓
Results stored in list
    ↓
Results exported to JSON
```

### Error Handling Flow

```
Operation fails
    ↓
Caught as specific exception
    ↓
Logged at appropriate level
    ↓
Wrapped in ScrapingResult with error
    ↓
Returned to caller (not raised)
    ↓
Orchestrator continues with next URL
```

## Configuration

**File:** `src/config.py`

Centralized configuration:

```python
SCRAPER_CONFIG = {
    "timeout": 10,           # seconds
    "max_retries": 3,        # attempts
    "retry_delay": 2,        # seconds
    "request_delay": 1,      # seconds (rate limiting)
    "user_agent": "...",     # Mozilla compatible
}
```

## Testing Architecture

### Unit Tests
- Test individual components
- Mock external dependencies
- Fast execution

### Integration Tests
- Test component interactions
- Smaller scope than end-to-end
- Moderate execution time

### Test Organization

```
tests/
├── test_models.py          # Pydantic models
├── test_abstractions.py    # Interfaces
├── test_implementations.py # HttpClient, Storage, Factory
├── test_scrapers.py        # Parsers & Scrapers
├── test_orchestrator.py    # Orchestrator
└── test_cli.py             # CLI commands
```

## Extending the System

### Add New Platform

1. **Create Parser:**
```python
class NewPlatformParser(BaseParser):
    def _extract_messages(self, soup):
        # Extract messages specific to platform
        pass
```

2. **Create Scraper:**
```python
class NewPlatformScraper(BaseScraper):
    def _get_parser(self):
        return NewPlatformParser()
    
    def _get_supported_domains(self):
        return ["newplatform.com"]
    
    @property
    def platform_name(self):
        return "newplatform"
```

3. **Register in Factory:**
```python
factory.register_scraper("newplatform", NewPlatformScraper)
```

No modification to existing code! **Open/Closed Principle**.

## Performance Considerations

### Rate Limiting
- 1 second delay between requests
- Prevents server overload
- Respects robots.txt

### Retry Logic
- Exponential backoff
- Handles transient failures
- Configurable attempts

### Error Handling
- Partial failures don't stop execution
- Errors logged, not raised
- Resilient to network issues

## Thread Safety

Currently **not thread-safe**:
- HttpClient maintains state (`_last_request_time`)
- Use separate instances per thread

**Future:** Make thread-safe with locks or asyncio

## Dependencies

**Production:**
- `requests`: HTTP operations
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast parsing
- `pydantic`: Data validation
- `click`: CLI framework

**Development:**
- `pytest`: Testing
- `black`: Code formatting
- `ruff`: Linting
- `mypy`: Type checking

## Deployment Considerations

### Configuration
- Centralized in `config.py`
- Environment-specific overrides
- No hardcoded values

### Logging
- Structured logging to file
- Configurable levels
- Searchable logs

### Error Recovery
- Graceful degradation
- Partial success handling
- Clear error messages

## Future Enhancements

1. **Async/Await**
   - Parallel scraping
   - Better performance

2. **Database**
   - Cache results
   - Historical data
   - Better queries

3. **API**
   - REST API wrapper
   - Real-time scraping
   - Cloud deployment

4. **Monitoring**
   - Metrics collection
   - Health checks
   - Alerting

---

**See also:** [EXAMPLES.md](./EXAMPLES.md) for usage examples