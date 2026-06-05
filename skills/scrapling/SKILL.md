---
name: scrapling
description: "Adaptive web scraping framework with anti-bot bypass and spider crawling. Use when asked to scrape, crawl, or extract data from websites; web_fetch fails; the site has anti-bot protections; write Python code to scrape/crawl; or write spiders. Requires Python 3.10+."
version: "0.4.8"
metadata:
  {"tags":["web-scraping", "crawling", "research", "automation", "anti-bot", "cloudflare"]}
---

# Scrapling

Scrapling is an adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl.

Its parser learns from website changes and automatically relocates your elements when pages update. Its fetchers bypass anti-bot systems like Cloudflare Turnstile out of the box. And its spider framework lets you scale up to concurrent, multi-session crawls with pause/resume and automatic proxy rotation - all in a few lines of Python. One library, zero compromises.

**Requires: Python 3.10+**

## Setup (once)

Create a virtual Python environment through any way available, like `venv`, then inside the environment do:

`pip install "scrapling[all]>=0.4.8"`

Then do this to download all the browsers' dependencies:

```bash
scrapling install --force
```

## CLI Usage

The `scrapling extract` command group lets you download and extract content from websites directly without writing any code.

```bash
Usage: scrapling extract [OPTIONS] COMMAND [ARGS]...

Commands:
  get             Perform a GET request and save the content to a file.
  post            Perform a POST request and save the content to a file.
  put             Perform a PUT request and save the content to a file.
  delete          Perform a DELETE request and save the content to a file.
  fetch           Use a browser to fetch content with browser automation and flexible options.
  stealthy-fetch  Use a stealthy browser to fetch content with advanced stealth features.
```

### Usage pattern

- Choose your output format by changing the file extension:
  - `.md` - Convert HTML to Markdown (great for documentation)
  - `.html` - Save HTML content as-is
  - `.txt` - Save clean text content

Which command to use generally:
- Use **`get`** with simple websites, blogs, or news articles.
- Use **`fetch`** with modern web apps, or sites with dynamic content.
- Use **`stealthy-fetch`** with protected sites, Cloudflare, or anti-bot systems.

> When unsure, start with `get`. If it fails or returns empty content, escalate to `fetch`, then `stealthy-fetch`.

### Key options

| Option | Description |
|--------|-------------|
| `-s, --css-selector` | Extract specific content using CSS selectors |
| `--ai-targeted` | Extract only main content and sanitize for AI consumption |
| `--headless / --no-headless` | Run browser in headless mode (default: True) |
| `--network-idle` | Wait for network idle |
| `--stealthy-headers` | Use stealthy browser headers (default: True) |
| `--solve-cloudflare` | Solve Cloudflare challenges |
| `--proxy` | Proxy URL in format "http://username:password@host:port" |
| `--impersonate` | Browser to impersonate (Chrome, Firefox, Safari) |

### Examples

```bash
# Basic download
scrapling extract get "https://news.site.com" news.md

# Extract specific content using CSS selectors
scrapling extract get "https://blog.example.com" articles.md --css-selector "article"

# Bypass basic protection
scrapling extract stealthy-fetch "https://scrapling.requestcatcher.com" content.md

# Solve Cloudflare challenges
scrapling extract stealthy-fetch "https://nopecha.com/demo/cloudflare" data.txt --solve-cloudflare --css-selector "#padded_content a"
```

## Code Overview

### Basic Usage

```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()

# Or use one-off requests
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```

### Advanced stealth mode

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()
```

### Full browser automation

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.css('.quote .text::text').getall()
```

### Spiders

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    robots_txt_obey = True
    
    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }
            
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = QuotesSpider().start()
print(f"Scraped {len(result.items)} quotes")
result.items.to_json("quotes.json")
```

## Guardrails (Always)

- Only scrape content you're authorized to access.
- Respect robots.txt and ToS. Use `robots_txt_obey = True` on spiders.
- Add delays (`download_delay`) for large crawls.
- Don't bypass paywalls or authentication without permission.
- Never scrape personal/sensitive data.