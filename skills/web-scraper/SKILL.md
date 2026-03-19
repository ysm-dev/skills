---
name: web-scraper
description: "Use when the user wants to scrape, crawl, or extract data from a website or URL. Triggers on: 'scrape this site', 'get data from this URL', 'crawl this page', 'extract data from the web', 'pull data from this link', 'download data from this website', 'I need data from [URL]', or any request involving collecting structured data from a web page. Also triggers when the user provides a URL and asks for its data in CSV, JSON, or other tabular formats. Always load the agent-browser skill alongside this one."
---

# Web Scraper — API-First Approach via HAR Capture

This skill extracts structured data from websites by capturing network traffic rather than parsing HTML. The core idea: every dynamic web page fetches its data from backend APIs. By recording the browser's network activity, you can discover those APIs and call them directly — producing scraping code that is faster, more reliable, and less likely to break when the page redesign happens.

**Always use the `agent-browser` skill for all browser operations.** Do not use `curl`, `fetch`, `wget`, or similar tools to load pages. The browser handles JavaScript rendering, authentication cookies, and dynamic content that simple HTTP clients miss.

## Workflow Overview

```
1. Set up temp workspace
2. Open URL in headed browser + start HAR recording
3. Handle authentication if needed (user logs in manually)
4. Wait for page to fully load, interact if needed to trigger data requests
5. Stop HAR recording → save .har to temp workspace
6. Analyze .har to identify data-serving API endpoints
7. Write Python scraping code that calls those APIs
8. Run the code → save results to current directory
```

## Step 1: Set Up Temp Workspace

Create an isolated temp directory for all intermediate files. Only the final output belongs in the user's current directory.

```bash
SCRAPE_TMP="/tmp/web-scraper-$(echo '<domain>' | tr '/:' '-')-$(date +%s)"
mkdir -p "$SCRAPE_TMP"
```

All intermediate files go here: `.har` files, analysis notes, scraping scripts, debug logs.

## Step 2: Open the Target URL and Start HAR Recording

Open the browser in **headed mode** so the user can see what's happening (and manually authenticate if needed). Start HAR recording before navigating so you capture every request the page makes.

```bash
agent-browser --headed network har start
agent-browser --headed open <target-url>
agent-browser wait --load networkidle
```

The `--headed` flag is important — it lets the user visually confirm the page loaded correctly and intervene for login flows.

## Step 3: Handle Authentication

If the target page requires login, the browser will show the login page. Ask the user to log in manually in the headed browser window. Guide them:

> "The browser is open. Please log in if the site requires authentication. Let me know when you're on the page with the data you want to scrape."

After the user confirms they've logged in and navigated to the data page, proceed. If additional interaction is needed to reveal the data (clicking tabs, expanding sections, scrolling to trigger lazy loading), do it via `agent-browser` commands or ask the user to do it in the headed window.

For pages that load data progressively or via infinite scroll:

```bash
agent-browser scroll down 3000
agent-browser wait --load networkidle
```

Repeat scrolling if the page uses infinite scroll and the user wants more data. Each scroll may trigger new API calls that the HAR will capture.

## Step 4: Capture the HAR File

Once the data is visible on the page, stop the HAR recording:

```bash
agent-browser network har stop "$SCRAPE_TMP/capture.har"
```

Close the browser session when done:

```bash
agent-browser close
```

## Step 5: Analyze the HAR File

This is the most important analytical step. Read and parse the `.har` file to find the API endpoints that serve the actual data.

What to look for:

1. **JSON/XML API responses** — Requests returning `application/json` or `application/xml` with structured data in the response body. These are the primary targets.
2. **GraphQL endpoints** — POST requests to paths like `/graphql` or `/api/graphql` with query payloads.
3. **Paginated APIs** — Look for query parameters like `page`, `offset`, `limit`, `cursor`, `after`, `pageToken` in the URLs or request bodies.
4. **Authentication headers** — Note any `Authorization`, `Cookie`, `X-API-Key`, or custom auth headers that the API requests carry. The scraping code needs to replicate these.
5. **Request patterns** — Identify which requests are for the actual data vs. static assets (JS, CSS, images, fonts, analytics/tracking). Filter out noise.

Write a Python script to parse the HAR and extract relevant requests:

```python
import json

with open("capture.har") as f:
    har = json.load(f)

for entry in har["log"]["entries"]:
    url = entry["request"]["url"]
    method = entry["request"]["method"]
    status = entry["response"]["status"]
    mime = entry["response"]["content"].get("mimeType", "")

    # Focus on API responses with data
    if "json" in mime or "xml" in mime:
        print(f"{method} {status} {url}")
        # Check response size to gauge data volume
        size = entry["response"]["content"].get("size", 0)
        print(f"  Size: {size} bytes")
```

Save this analysis script to the temp workspace and run it. Review the output to identify which endpoint(s) serve the data the user wants.

## Step 6: Write the Scraping Code

Based on the HAR analysis, write a Python script using `requests` (or `httpx`) that:

1. **Calls the discovered API endpoint(s) directly** — replicate the exact headers, cookies, and parameters from the HAR
2. **Handles pagination** — if the API uses pagination, loop through all pages
3. **Extracts and flattens the data** — navigate the JSON response structure to pull out the fields the user wants
4. **Outputs to the requested format** — CSV by default, or JSON/TSV if specified

### Pagination Strategies

If the HAR reveals pagination parameters, implement the appropriate strategy:

- **Offset-based** (`offset=0&limit=50`): Increment offset by limit each iteration until empty response
- **Page-based** (`page=1`): Increment page number until empty or past total pages
- **Cursor-based** (`cursor=abc123` or `after=xyz`): Use the cursor from each response to fetch the next page
- **Token-based** (`pageToken=...`): Similar to cursor, use `nextPageToken` from response

### Template Structure

```python
import requests
import csv
import json
import sys

# --- Configuration ---
BASE_URL = "<api-endpoint-from-har>"
HEADERS = {
    # Replicate relevant headers from HAR
}
COOKIES = {
    # Replicate session cookies from HAR if needed
}
PARAMS = {
    # Base query parameters from HAR
}
OUTPUT_FORMAT = "csv"  # or "json", "tsv"

def fetch_page(page_param):
    """Fetch a single page of data."""
    params = {**PARAMS, **page_param}
    resp = requests.get(BASE_URL, headers=HEADERS, cookies=COOKIES, params=params)
    resp.raise_for_status()
    return resp.json()

def extract_records(data):
    """Extract the list of records from the API response.
    Adjust the key path based on the actual response structure."""
    # e.g., return data["results"] or data["data"]["items"]
    pass

def scrape_all():
    """Fetch all pages and collect records."""
    all_records = []
    # Implement pagination loop based on detected strategy
    # ...
    return all_records

def save_csv(records, output_path):
    if not records:
        print("No records found.")
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {output_path}")

def save_json(records, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(records)} records to {output_path}")

def save_tsv(records, output_path):
    if not records:
        print("No records found.")
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {output_path}")

if __name__ == "__main__":
    records = scrape_all()
    output_path = sys.argv[1] if len(sys.argv) > 1 else "output.csv"
    if OUTPUT_FORMAT == "json":
        save_json(records, output_path)
    elif OUTPUT_FORMAT == "tsv":
        save_tsv(records, output_path)
    else:
        save_csv(records, output_path)
```

Save the scraping script to `$SCRAPE_TMP/scraper.py`.

## Step 7: Run and Deliver Results

Run the scraping script and save the output to the user's **current working directory**:

```bash
python "$SCRAPE_TMP/scraper.py" "./output.csv"
```

After successful execution:
- Confirm the output file location and record count to the user
- Offer a preview of the first few rows
- If the user wants a different format, re-run with the appropriate format flag

## File Organization Rules

| File | Location |
|------|----------|
| Final output (`.csv`, `.json`, `.tsv`) | Current working directory (`./`) |
| HAR capture file | `$SCRAPE_TMP/capture.har` |
| HAR analysis script | `$SCRAPE_TMP/analyze_har.py` |
| Scraping script | `$SCRAPE_TMP/scraper.py` |
| Debug logs | `$SCRAPE_TMP/` |

Tell the user where the temp files are in case they want to inspect them, but don't clutter their project directory with intermediates.

## Troubleshooting

**No useful API endpoints found in HAR:**
Some pages render data server-side (SSR) without separate API calls. In this case, fall back to extracting data from the HTML response in the HAR, or use `agent-browser` to extract text from the rendered page via `snapshot` or `get text` commands. This is a last resort — the API-first approach should be tried first.

**Authentication tokens expire quickly:**
If captured cookies/tokens are short-lived, note this to the user. The scraping script may need to be run promptly after HAR capture, or you may need to implement a token refresh mechanism.

**Rate limiting or blocking:**
If the API returns 429 or 403 errors, add delays between requests (`time.sleep()`) and respect `Retry-After` headers. Inform the user about rate limits.

**CORS or origin checks:**
Some APIs validate the `Origin` or `Referer` header. Make sure to replicate these headers from the HAR in the scraping code.
