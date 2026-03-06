---
name: web-scraper
description: Bulk web scraping via HAR-based API discovery. Use when the user asks to scrape, download, or export bulk data from a website (e.g., "download all Hacker News posts from Dec 2025", "scrape all jobs from YC job board", "export all products from this catalog", "get all comments from this thread"). Triggers on requests involving collecting many records/pages from a web source and saving as CSV, JSON, or other structured formats.
---

# Web Scraper

Bulk-scrape structured data from websites by discovering APIs through HAR capture, then generating and running scraping code.

When this `web-scraper` skill is used, always load the `agent-browser` skill together with it for browser automation steps.

## Temp Directory

At the start of every scrape session, create a unique working directory under `/tmp`:

```
/tmp/scrape-<slug>/
```

Derive `<slug>` from the task (e.g., `scrape-hn-dec2025`, `scrape-yc-jobs-2026`). Keep it short, lowercase, hyphenated. All intermediate files (HAR, scripts, logs) go here. This prevents collisions between sessions.

## Workflow

### 1. Clarify Requirements

Before starting, confirm:

- **Target URL** and what data to collect (e.g., "all posts", "all job listings")
- **Output format**: CSV (default), JSON, or other format the user specifies
- **Scope/filters**: date range, categories, search terms, pagination limits

### 2. Open Site and Capture HAR

Open the target page with `agent-browser`, start HAR capture, then interact with the page to trigger API calls (scroll, paginate, click "load more", apply filters).

```bash
agent-browser open <target-url>
agent-browser har start
agent-browser snapshot -i
# Interact: scroll, click pagination, expand sections to trigger API calls
agent-browser scroll down 3000
agent-browser wait --load networkidle
# If there is pagination or "load more", click it
agent-browser click @e<next-page-ref>
agent-browser wait --load networkidle
agent-browser har stop /tmp/scrape-<slug>/capture.har
```

Key: trigger as many data-fetching requests as possible -- paginate, scroll, filter, search -- so the HAR captures the underlying API endpoints and their parameters.

### 3. Analyze HAR

Read `/tmp/scrape-<slug>/capture.har` and identify:

- **API endpoints** returning structured data (JSON responses with arrays of records)
- **Request patterns**: URL structure, query parameters for pagination (`page`, `offset`, `cursor`, `limit`), auth headers, cookies
- **Response structure**: field names, nesting, total count / `hasMore` flags
- **Pagination mechanism**: page numbers, cursor-based, offset-based, or infinite scroll

Prioritize XHR/fetch requests returning JSON over HTML page loads. Look for endpoints with large arrays of items -- these are the data APIs.

Ignore static assets (images, CSS, JS bundles, fonts), tracking/analytics calls, and ad network requests.

### 4. Write Scraping Code

Write a Python script to `/tmp/scrape-<slug>/scraper.py` that:

- Hits the discovered API endpoint(s) directly (no browser needed)
- Handles pagination by iterating through all pages/cursors
- Copies necessary headers/cookies from the HAR (auth tokens, session cookies, user-agent)
- Includes rate limiting (`time.sleep`) to be respectful -- 0.5-1s between requests
- Collects all records into a list
- Handles errors gracefully (retries on 429/5xx, logs failures)
- Saves results in the user's requested format to the **current working directory**

Use only Python standard library (`urllib.request`, `json`, `csv`, `time`) unless the user has specific library preferences. This avoids dependency issues.

If direct API access is not possible (no JSON API found, heavy anti-bot protection, data only in rendered HTML), fall back to browser-based scraping:

- Write a script that uses `agent-browser` commands via `subprocess` to navigate and extract data page by page
- Use `agent-browser eval` or `agent-browser get text` to pull data from the DOM

### 5. Run and Verify

```bash
python3 /tmp/scrape-<slug>/scraper.py
```

After running:

- Check the output file exists in the current directory and has the expected number of records
- Show the user a preview: first 5 rows for CSV, first 2 records for JSON
- Report total record count

If the script fails (auth expired, rate limited, structure changed), diagnose and fix `/tmp/scrape-<slug>/scraper.py` then re-run.

### 6. Clean Up

Report to the user:

- Output file path and record count
- Any records that were skipped or errored

The temp directory (`/tmp/scrape-<slug>/`) is left for debugging. Only the final data file lives in the current working directory.

## File Placement Rules

| File                        | Location                         | Reason                                |
| --------------------------- | -------------------------------- | ------------------------------------- |
| Temp directory              | `/tmp/scrape-<slug>/`            | Unique per session, avoids collisions |
| HAR capture                 | `/tmp/scrape-<slug>/capture.har` | Temporary debug artifact              |
| Scraper script              | `/tmp/scrape-<slug>/scraper.py`  | Temporary tool, not project code      |
| Output data (CSV/JSON/etc.) | `./` (current directory)         | User's requested deliverable          |

## Pagination Patterns Cheat Sheet

| Pattern      | Signal in HAR                    | How to iterate                                        |
| ------------ | -------------------------------- | ----------------------------------------------------- |
| Page number  | `?page=1`, `?p=2`                | Increment page param until empty response             |
| Offset/limit | `?offset=0&limit=25`             | Increment offset by limit until count reached         |
| Cursor       | `?cursor=abc123`, `?after=xyz`   | Use `nextCursor`/`endCursor` from response until null |
| Link header  | `Link: <...?page=3>; rel="next"` | Follow `next` link until absent                       |
| Total count  | `"total": 500` in response       | Calculate total pages from total and page size        |
| hasMore flag | `"hasMore": true`                | Continue until `hasMore` is false                     |

## Anti-Pattern Awareness

- **Always check for APIs first.** JSON APIs are more reliable and efficient than HTML scraping. But if no API exists (server-rendered pages, no XHR/fetch calls in HAR), HTML scraping is perfectly valid -- use `agent-browser eval` or `agent-browser get text` to extract data from the DOM.
- **Never dump all data to /tmp.** Only intermediate/debug files go to /tmp; the user's data goes to current directory.
- **Never skip pagination.** Always verify total records match expectations. If the site says "500 results" but you only got 25, pagination is incomplete.
- **Never ignore rate limits.** If you get 429 responses, increase sleep time. Be respectful.
