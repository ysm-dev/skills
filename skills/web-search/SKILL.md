---
name: web-search
description: "DuckDuckGo web search from the command line using ddgr. Use this skill whenever you need to search the web for information -- looking up documentation, researching error messages, finding API references, checking current facts, comparing libraries, or answering questions that require up-to-date information. Trigger this proactively whenever a task would benefit from a web search, even if the user didn't explicitly ask you to search. Also use this when the user asks you to install or set up ddgr."
---

# web-search -- DuckDuckGo Search via ddgr

ddgr is a command-line utility that searches DuckDuckGo from the terminal. It's privacy-aware (no user data collection, Do Not Track enabled by default) and requires only Python 3.8+.

## Installation

If ddgr is not found on the system, install it before searching.

**macOS (Homebrew):**
```bash
brew install ddgr
```

**pip (cross-platform):**
```bash
pip3 install ddgr
```

To check if it's installed:
```bash
which ddgr
```

## Searching

Always use these flags on every search:

- `--np` -- perform search and exit (no interactive prompt)
- `--noua` -- disable user agent (reduces chance of being blocked)
- `--colorize=never` -- clean output without ANSI escape codes
- `-x` -- show complete URLs (needed for follow-up fetching)

Basic search:

```bash
ddgr --np --noua --colorize=never -x "your search query"
```

This returns numbered plain text results with full URLs:

```
 1.  Page Title
     https://example.com/page
Description text from search results.

 2.  Another Result
     https://another.com/article
More description text.
```

### Controlling result count

By default ddgr returns 10 results. Use `-n` to adjust:

```bash
ddgr --np --noua --colorize=never -x -n 5 "your query"
```

For quick lookups, 3-5 results is usually enough. For broader research, use up to 10.

### Site-specific search

Search within a specific website using `-w`:

```bash
ddgr --np --noua --colorize=never -x -w stackoverflow.com "python async await"
```

### Time-limited search

Restrict results to a time period using `-t`:

- `-t d` -- past day
- `-t w` -- past week
- `-t m` -- past month
- `-t y` -- past year

```bash
ddgr --np --noua --colorize=never -x -t m "react 19 new features"
```

### Region-specific search

Use `-r` for region-specific results:

```bash
ddgr --np --noua --colorize=never -x -r us-en "local news"
```

### DuckDuckGo Bangs

ddgr supports DuckDuckGo Bangs for searching specific sites directly:

```bash
ddgr --np --noua --colorize=never -x '!w artificial intelligence'   # Wikipedia
ddgr --np --noua --colorize=never -x '!gh opencode'                 # GitHub
ddgr --np --noua --colorize=never -x '!so python decorators'        # Stack Overflow
ddgr --np --noua --colorize=never -x '!mdn fetch api'               # MDN Web Docs
```

Note: in bash/zsh, escape `!` with a backslash (`\!w`) or use single quotes.

## When and How to Search

Use ddgr proactively whenever a task could benefit from current web information:

- **Error messages**: Search the error text to find solutions
- **Library/API docs**: Look up current documentation, especially for version-specific features
- **Facts and dates**: Verify claims that could be outdated
- **Comparisons**: Research alternatives when helping the user choose between tools
- **"How to" questions**: Find current best practices or tutorials
- **Unfamiliar topics**: When the user asks about something you're not confident about

### Search Strategy

Every search follows two steps: **search** with ddgr, then **fetch** the best result with WebFetch.

1. **Search first.** Run ddgr with a well-crafted query. The `-x` flag gives you full URLs in the output, which you'll need for the next step.

2. **Pick the best result and fetch it.** Scan the titles and descriptions, then use WebFetch on the most relevant URL to get the full page content. The snippets from ddgr are short -- the real value comes from reading the actual page.

3. **Search iteratively.** If the first search doesn't give good results, refine the query and try again -- just like a human would.

### Example Workflow

User asks: "What's the recommended way to handle authentication in Next.js 15?"

```bash
# Step 1: Search
ddgr --np --noua --colorize=never -x -n 5 "Next.js 15 authentication best practices 2025"
```

Output includes full URLs:
```
 1.  Authentication | Next.js
     https://nextjs.org/docs/app/building-your-application/authentication
Learn how to implement authentication in Next.js...
```

```bash
# Step 2: Fetch the most relevant result
# Use WebFetch on the URL from step 1 to get full page content
```

Synthesize the information from the fetched page and present it to the user with the source URL.

## Options Reference

### Always-on flags

| Flag | Description |
|---|---|
| `--np` | No prompt -- search and exit |
| `--noua` | Disable user agent |
| `--colorize=never` | No ANSI color codes |
| `-x` | Show complete URLs for WebFetch follow-up |

### Optional flags

| Option | Description |
|---|---|
| `-n N` | Show N results (0-25, default 10) |
| `-r REG` | Region (e.g. `us-en`, `in-en`) |
| `-t SPAN` | Time limit: `d`, `w`, `m`, `y` |
| `-w SITE` | Site-specific search |
| `-p URI` | HTTPS proxy |
| `--unsafe` | Disable safe search |

## Troubleshooting

- **ddgr not found**: Install with `brew install ddgr` (macOS) or `pip3 install ddgr`
- **No results / blocked**: Try without `--noua` temporarily, or use a proxy with `-p`
- **Garbled output**: Ensure `--colorize=never` is set
