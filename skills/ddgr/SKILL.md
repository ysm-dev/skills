---
name: ddgr
description: Search the web using ddgr (DuckDuckGo from the terminal) to find current information, documentation, error solutions, package versions, API references, or any real-world data. Use this skill whenever the user asks to look something up online, search the web, find recent information, check documentation, research a topic, troubleshoot an error message, or needs any data that might not be in your training set. Also use it when you need to verify facts, find URLs, or when a task would clearly benefit from current web information even if the user didn't explicitly ask you to search. Trigger on phrases like "search for", "look up", "what's the latest", "find me", "google", "how do I fix this error", or any request for up-to-date information.
---

# ddgr -- Web Search via DuckDuckGo

Search the web from the terminal using ddgr and parse structured JSON results. This gives you access to current information beyond your training data.

## Check and install ddgr

Before running any search, verify ddgr is available. If it isn't installed, install it automatically -- the user asked you to search the web, so getting the tool in place is part of fulfilling that request.

```bash
command -v ddgr >/dev/null 2>&1 && echo "ddgr is installed" || echo "ddgr not found"
```

If ddgr is not found, detect the platform and install. Try the platform-native package manager first because it handles dependencies and updates automatically. Fall back to pip only if the native method is unavailable or fails.

**macOS:**
```bash
brew install ddgr
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update && sudo apt-get install -y ddgr
```

**Windows / any platform (pip -- requires Python 3.8+):**
```bash
pip3 install ddgr
```

After installation, verify it works:
```bash
ddgr --version
```

## Running searches

Use `--json`, `--np`, and `--noua` flags on every search. `--json` gives you structured output you can parse reliably instead of terminal-formatted text. `--np` (no prompt) makes ddgr exit after printing results instead of entering interactive mode, which would hang the terminal. `--noua` disables the user agent string, which prevents DuckDuckGo from rejecting requests with HTTP 202 errors.

### Basic search

```bash
ddgr --json --np --noua "your search query"
```

### Control result count

Default is 10 results. Use `-n` to adjust. For quick lookups, 3-5 results is usually enough. For research tasks, request more.

```bash
ddgr --json --np --noua -n 5 "your search query"
```

### Site-specific search

Use `-w` to restrict results to a specific domain. Valuable for searching documentation sites, Stack Overflow, GitHub, etc.

```bash
ddgr --json --np --noua -w stackoverflow.com "python async timeout"
ddgr --json --np --noua -w docs.python.org "pathlib glob"
```

### Time-filtered search

Use `-t` to limit results by recency. Useful when the user needs recent information.

- `d` -- past day
- `w` -- past week
- `m` -- past month
- `y` -- past year

```bash
ddgr --json --np --noua -t w "next.js 15 breaking changes"
```

### Region-specific search

Use `-r` for localized results. Format is `xx-xx` (e.g., `us-en`, `uk-en`, `de-de`).

```bash
ddgr --json --np --noua -r us-en "local election results"
```

### Bangs (shortcut searches)

ddgr supports DuckDuckGo bangs:

```bash
ddgr --json --np --noua "!w artificial intelligence"   # Wikipedia
ddgr --json --np --noua "!gh react hooks"               # GitHub
ddgr --json --np --noua "!so python decorators"         # Stack Overflow
ddgr --json --np --noua "!mdn fetch api"                # MDN Web Docs
```

Note: bangs redirect through DuckDuckGo and may not always return JSON results. Prefer `-w` for programmatic use.

### Combining flags

Flags compose naturally:

```bash
ddgr --json --np --noua -n 5 -t m -w reddit.com "best rust web framework"
```

## Parsing JSON output

ddgr's `--json` output is a JSON array of result objects:

```json
[
  {
    "abstract": "A brief description or snippet from the page",
    "title": "Page Title",
    "url": "https://example.com/page"
  }
]
```

Each result has three fields: `title`, `url`, and `abstract`. You can read this JSON directly from the command output.

## When to use which pattern

**Quick fact lookup** -- Use `-n 3` to keep results concise:
```bash
ddgr --json --np --noua -n 3 "current python latest version"
```

**Error troubleshooting** -- Include the error message and optionally restrict to Stack Overflow:
```bash
ddgr --json --np --noua -n 5 "ModuleNotFoundError: No module named 'cv2'"
ddgr --json --np --noua -n 5 -w stackoverflow.com "ECONNREFUSED 127.0.0.1:5432"
```

**Documentation lookup** -- Search against official docs:
```bash
ddgr --json --np --noua -w docs.djangoproject.com "queryset annotate"
```

**Research and comparison** -- More results, time-filtered for recency:
```bash
ddgr --json --np --noua -n 10 -t y "comparing bun vs deno vs node performance"
```

**Finding a specific page or URL:**
```bash
ddgr --json --np --noua -n 3 "github anthropic claude code repository"
```

## Error handling

**No results (empty array `[]`):** Rephrase the query. Remove overly specific terms or quotes. Broaden the search.

**ddgr hangs:** This means `--np` was omitted and ddgr entered interactive mode. Always include `--np`.

**Non-JSON output:** If ddgr prints an error instead of JSON, the output won't parse. Common causes: no internet connection, DuckDuckGo rate limiting (rare), or a very old ddgr version. Check stderr and the exit code.

**Rate limiting:** DuckDuckGo rarely rate-limits, but if you get empty responses on rapid repeated queries, add a brief pause between searches.

## Tips

- Quote multi-word queries to keep them as a single search phrase.
- For programming questions, include the language name and version for more relevant results.
- When debugging errors, search for the most distinctive part of the error message -- the error class and a few key words, not the full traceback.
- After getting search results, you can use WebFetch (if available) to read the full content of promising URLs for deeper information.
- If the user's question needs current data (prices, dates, version numbers, recent events), search proactively rather than guessing from training data.
