---
name: findweb
description: "Google search from the command line using findweb. Use this skill whenever you need to search the web for information — looking up documentation, researching error messages, finding API references, checking current facts, comparing libraries, or answering questions that require up-to-date information. Trigger this proactively whenever a task would benefit from a web search, even if the user didn't explicitly ask you to search. Also use this when the user asks you to install or set up findweb."
---

# findweb — Google Search CLI

findweb is a Google search CLI powered by the system Chrome browser. It lets you search Google and get results directly from the terminal, with no API key required.

## Installation

```bash
bun install -g findweb
```

Or run without installing:

```bash
bunx findweb "search query"
```

Requires: macOS, system Chrome (`/Applications/Google Chrome.app`), and [Bun](https://bun.sh) >= 1.3.11.

## First Run — Google Login

The first time findweb runs on a fresh profile, it opens a Chrome window for Google sign-in. This is normal and only happens once — it reduces rate limiting from Google.

If the user hasn't logged in yet, run `findweb login` first to trigger the interactive sign-in flow. After sign-in, searches work headlessly from then on.

If the user reports issues with rate limiting or CAPTCHAs, suggest running `findweb login` to re-authenticate.

## Searching

The simplest way to search:

```bash
findweb "your search query"
```

This returns numbered plain text results:

```
1. Page Title
https://example.com
Description text from search results.

2. Another Result
https://another.com
More description text.
```

This format is concise, readable, and works well for most use cases — showing results to the user, scanning for relevant links, or quickly finding an answer.

### JSON Output

When you need to programmatically parse results (e.g., extracting URLs to fetch, filtering by domain, or building a list), use `--json`:

```bash
findweb --json "your search query"
```

Returns a JSON array:

```json
[
  {
    "title": "Page Title",
    "url": "https://example.com",
    "snippet": "Description text from search results."
  }
]
```

### Getting More Results

By default findweb returns 3 results. Use `-n` for more:

```bash
findweb -n 10 "react useEffect cleanup"
```

### Region and Language

Target specific regions or languages when relevant:

```bash
# Korean results
findweb --gl kr --lang ko "startup"

# Japanese results
findweb --gl jp --lang ja "query"
```

### Batch Search

Search multiple queries at once — each runs in a separate Chrome tab:

```bash
findweb "query one" "query two" "query three" --parallel 3
```

This is much faster than running searches sequentially. Use it when you need to research multiple topics at once.

## When and How to Search

Use findweb proactively whenever a task could benefit from current web information. Some examples of when to search:

- **Error messages**: Search the error text to find solutions
- **Library/API docs**: Look up current documentation, especially for version-specific features
- **Facts and dates**: Verify claims that could be outdated
- **Comparisons**: Research alternatives when helping the user choose between tools
- **"How to" questions**: Find current best practices or tutorials
- **Unfamiliar topics**: When the user asks about something you're not confident about

### Search Strategy

1. **Formulate a good query.** Think about what a human would type into Google. Be specific — include library names, version numbers, error codes.

2. **Read the results.** The default plain text output is usually enough to identify relevant results. Use `--json` if you need to extract URLs or process results programmatically.

3. **Follow up with WebFetch if needed.** findweb gives you titles, URLs, and snippets. If you need the full content of a page, use WebFetch on the URL from the results.

4. **Batch related searches.** If you need to look up 3 things, run them as one batch command instead of 3 separate searches.

5. **Search iteratively.** If the first search doesn't give good results, refine the query and try again — just like a human would.

### Example Workflow

User asks: "How do I set up server-side rendering with the latest version of Remix?"

```bash
# Step 1: Search for current docs
findweb -n 5 "remix server side rendering setup 2025"
```

Scan the results for the most relevant link, then read it:

```bash
# Step 2: Read the most relevant result using WebFetch
```

Synthesize the information and present it to the user with sources.

## Options Reference

| Option             | Default       | Description                          |
| ------------------ | ------------- | ------------------------------------ |
| `--gl <country>`   | `us`          | Google region hint                   |
| `-l, --lang`       | `en`          | Google UI language                   |
| `-n, --num`        | `3`           | Results per query                    |
| `--parallel`       | `4`           | Batch tab concurrency                |
| `--userDataDir`    | auto-detected | Chrome profile directory             |
| `--headed`         | `false`       | Show the Chrome window               |
| `--json`           | `false`       | Print output as JSON                 |

## Troubleshooting

- **"Chrome not found"**: findweb looks for `/Applications/Google Chrome.app`. Make sure Chrome is installed at the default path.
- **Rate limiting / CAPTCHAs**: Run `findweb login` to sign in with a Google account.
- **Bun not installed**: Install with `curl -fsSL https://bun.sh/install | bash`.
- **Stale results**: Google caches results. Try a slightly different query or add a date to the search terms.
