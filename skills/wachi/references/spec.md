# wachi Detailed Behavior

## Table of Contents

- [Architecture](#architecture)
- [CLI Output Formats](#cli-output-formats)
- [Configuration](#configuration)
- [Change Detection](#change-detection)
- [Notification Delivery](#notification-delivery)
- [Summary Feature](#summary-feature)
- [Error Handling](#error-handling)
- [Auto-Update](#auto-update)

## Architecture

```
wachi sub <apprise-url> <url>
       |
       v
  Validate apprise-url format (contains "://")
  Normalize URL (prepend https:// if missing, strip trailing slash)
  Validate URL is reachable (HTTP fetch)
       |
       v
  Is it an RSS URL directly?  ------yes-----> Store as RSS subscription
       |no
       v
  Fetch HTML, auto-discover RSS
  (1. <link rel="alternate"> tags
   2. Common paths: /rss, /rss.xml, /feed, /feed.xml, /atom, /atom.xml)
       |
  RSS found? ------yes-----> Store original URL + discovered RSS URL
       |no
       v
  Validate LLM config exists (error if missing)
  Auto-install agent-browser if missing
  Launch agent-browser -> a11y tree -> LLM identifies refs
  Derive CSS selectors from DOM (deterministic)
  Validate selectors against raw HTTP
  Store URL + CSS selectors + baseline items
```

### Ongoing checks (`wachi check`)

1. Auto-update check (24h cooldown, non-blocking)
2. Cleanup old dedup records (TTL 90 days + cap 50k)
3. For each subscription (concurrent, rate-limited per domain):
   - RSS: Fetch (with ETag/If-Modified-Since) -> Parse -> Extract items
   - CSS: HTTP fetch -> Apply selector with cheerio -> Extract items
   - For each item: compute dedup key `sha256(link + title + channel_apprise_url)`, INSERT OR IGNORE
   - If inserted (new): send notification via apprise
4. Print summary: "3 new, 47 unchanged, 0 errors"

### Dedup Model

Items identified by `sha256(link + title + channel_apprise_url)`. If hash exists, already sent. On first subscribe, all current items pre-seeded (baseline). Use `--send-existing` to skip baseline.

Same URL, multiple channels: allowed. Each channel has its own dedup space.

### Dedup Cleanup

At start of every `wachi check`:
- **TTL**: Delete records older than 90 days
- **Count cap**: If >50,000 records, delete oldest until 50,000

Configurable:
```yaml
cleanup:
  ttl_days: 90
  max_records: 50000
```

## CLI Output Formats

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Fatal error |
| 2 | Partial success (some failed, some succeeded) |

### JSON Envelope (`--json`)

```json
{"ok": true, "data": { ... }}
{"ok": false, "error": {"what": "...", "why": "...", "fix": "..."}}
```

### Command Output Examples

**`wachi sub` (RSS):**
```
Subscribed (RSS): https://blog.example.com
Feed: https://blog.example.com/feed.xml
Baseline: 42 items seeded
```

**`wachi sub` (CSS):**
```
Subscribed (CSS): https://news.ycombinator.com
Selector: tr.athing
Baseline: 30 items seeded
```

**`wachi sub` (idempotent):**
```
Already subscribed: https://blog.example.com -> slack://xoxb-.../channel
```

**`wachi ls`:**
```
slack://xoxb-.../channel
  https://blog.example.com (RSS)
  https://news.ycombinator.com (CSS) [3 failures]

discord://webhook-id/token
  https://youtube.com/@channel (RSS)
```

**`wachi check`:**
```
sent: Show HN: My Project -> slack://xoxb-.../channel
sent: New Blog Post Title -> slack://xoxb-.../channel
3 new, 47 unchanged, 0 errors
```

**`wachi check --dry-run`:**
```
[dry-run] would send: Show HN: My Project -> slack://xoxb-.../channel
[dry-run] 2 items would be sent
```

## Configuration

Config at `~/.config/wachi/config.yml` (XDG). Created with `0600` permissions on first `wachi sub`.

Subscription type inferred from fields:
- Has `rss_url` -> RSS
- Has `item_selector` -> CSS

Full config example:
```yaml
llm:
  base_url: "https://api.openai.com/v1"
  api_key: "sk-..."
  model: "gpt-4.1-mini"

summary:
  enabled: true
  prompt: "Summarize focusing on actionable insights"
  language: "en"
  min_reading_time: 3

cleanup:
  ttl_days: 90
  max_records: 50000

channels:
  - apprise_url: "slack://xoxb-token/channel"
    subscriptions:
      - url: "https://blog.example.com"
        rss_url: "https://blog.example.com/feed.xml"
      - url: "https://news.ycombinator.com"
        item_selector: "tr.athing"
        title_selector: ".titleline > a"
        link_selector: ".titleline > a"
```

All top-level fields optional. Empty config is valid.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `WACHI_LLM_BASE_URL` | LLM API base URL (default: `https://api.openai.com/v1`) |
| `WACHI_LLM_API_KEY` | LLM API key |
| `WACHI_LLM_MODEL` | LLM model name |
| `WACHI_APPRISE_URL` | Override notification destination for ALL channels |
| `WACHI_CONFIG_PATH` | Custom config file path |
| `WACHI_DB_PATH` | Custom database path |
| `WACHI_NO_AUTO_UPDATE` | Set to `1` to disable auto-update |

### Data Storage

- **Config**: `~/.config/wachi/config.yml`
- **Database**: `~/.local/share/wachi/wachi.db` (SQLite, WAL mode)
- **Cache**: `~/.cache/wachi/` (pending updates)

Database auto-recovers from corruption: deletes and recreates with a warning.

## Change Detection

### RSS Discovery

1. Check if URL is directly an RSS feed (Content-Type contains `xml`/`rss`)
2. Parse `<link rel="alternate">` tags
3. Probe common paths: `/rss`, `/rss.xml`, `/feed`, `/feed.xml`, `/atom`, `/atom.xml`, `/feed/rss`, `/feed/atom`
4. Prefer first `<link>` tag match

Uses ETag/If-Modified-Since for bandwidth efficiency on subsequent fetches.

### LLM-Based CSS Selector Identification

When no RSS found:

1. Get a11y tree via `agent-browser snapshot --json`
2. LLM identifies main list item refs from a11y tree
3. Derive CSS selectors from DOM using `css-selector-generator` (deterministic)
4. Validate selectors against raw HTTP (no browser) -- warn if mismatch (JS-rendered site)

Requires LLM config (`WACHI_LLM_API_KEY` + `WACHI_LLM_MODEL`).

### Selector Staleness Recovery

After 3 consecutive failures (0 items): auto re-identify selectors. If fails, notify user.

### Baseline Behavior

Default: pre-seed all current items into dedup (no notifications on first check). With `--send-existing` / `-e`: skip seeding, send all on next check.

## Notification Delivery

### Message Format

```
<link>

<title>
```

With summary:
```
<link>

<title>

<summary>
```

### Behavior

- 1 item = 1 message
- Same channel: sequential (preserves chronological order)
- Different channels: parallel
- Within channel: oldest first
- 30s timeout per notification
- Failed notification: item NOT recorded in dedup (retried next check)
- Auto-installs `uv` if `uvx` not available

### Test Notification

`wachi test <apprise-url>` sends: "wachi test notification -- if you see this, your notification channel is working."

## Summary Feature

```yaml
summary:
  enabled: true
  prompt: "Summarize focusing on actionable insights"
  language: "ko"
  min_reading_time: 3
```

| Field | Default | Description |
|-------|---------|-------------|
| `enabled` | `false` | Must be explicitly enabled |
| `prompt` | `"Summarize this article concisely."` | System prompt for LLM |
| `language` | `"en"` | ISO 639-1 language code |
| `min_reading_time` | `0` | Minutes; 0 = always summarize |

Flow: fetch article -> convert to markdown -> check reading time -> LLM summarize if above threshold -> append to notification. Best-effort (failure = send without summary).

## Error Handling

All errors follow **What / Why / Fix** pattern:

```
Error: <what happened>

<why it happened>

<how to fix it>
```

Examples:

```
Error: LLM configuration required for non-RSS subscriptions.

https://news.ycombinator.com has no RSS feed. wachi needs an LLM to identify content selectors.

Set environment variables:
  export WACHI_LLM_API_KEY="sk-..."
  export WACHI_LLM_MODEL="gpt-4.1-mini"

Or add to ~/.config/wachi/config.yml:
  llm:
    api_key: "sk-..."
    model: "gpt-4.1-mini"
```

### Consecutive Failure Tracking

| Failures | Action |
|----------|--------|
| 1-2 | Silent, logged internally |
| 3 | Notify user + auto re-identify CSS selectors |
| 10+ | Notify user to consider `wachi unsub` |

Counter resets to 0 on any successful check.

## Auto-Update

Two-phase: download in background on current run, replace binary on next invocation. 24h cooldown. Disabled with `WACHI_NO_AUTO_UPDATE=1`.

`wachi upgrade`: manual update. Detects install method:
- npm/bun -> `npm update -g wachi` / `bun update -g wachi`
- Homebrew -> `brew upgrade wachi`
- Standalone -> download from GitHub Releases
