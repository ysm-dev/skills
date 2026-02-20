---
name: wachi
description: "Install, configure, and use the wachi CLI to monitor any URL for new content and get notifications via 90+ services (Slack, Discord, Telegram, email, etc.). Use when the user wants to: (1) subscribe to web pages, blogs, YouTube channels, or RSS feeds for change notifications, (2) set up URL monitoring with wachi sub/check/ls commands, (3) configure notification channels via apprise URLs, (4) schedule periodic checks with cron, (5) troubleshoot wachi errors or configuration, or (6) understand how wachi detects changes (RSS auto-discovery, LLM-based CSS selectors)."
---

# wachi

Subscribe any link and get notified on change. Monitors URLs for new content, pushes notifications to 90+ services via apprise.

## Install

```bash
# npm / bun (no install needed)
npx wachi --help
bunx wachi --help

# global install
npm i -g wachi
bun i -g wachi

# shell script
curl -fsSL https://raw.githubusercontent.com/ysm-dev/wachi/main/install.sh | sh

# homebrew
brew tap ysm-dev/tap && brew install wachi
```

## Quick Start

```bash
# 1. Subscribe to any URL (auto-discovers RSS)
wachi sub "slack://xoxb-token/channel" "https://blog.example.com"

# 2. Check for new content (run on a schedule)
wachi check

# New posts get pushed to Slack. That's it.
```

## Commands

```
wachi sub <apprise-url> <url>     Subscribe URL to notification channel
  -e, --send-existing             Send all current items on next check (skip baseline)

wachi unsub <apprise-url> [url]   Unsubscribe URL or remove entire channel

wachi ls                          List all channels and subscriptions

wachi check                       Check all subscriptions for changes
  -c, --channel <apprise-url>     Check specific channel only
  -n, --concurrency <number>      Max concurrent checks (default: 10)
  -d, --dry-run                   Preview without sending or recording

wachi test <apprise-url>          Send test notification

wachi upgrade                     Update wachi to latest version
```

**Global flags:** `--json` / `-j` for machine-readable output, `--verbose` / `-V` for detailed logs, `--config` / `-C` for custom config path.

## How It Works

1. `wachi sub` checks if the URL has an RSS feed (auto-discovery via `<link>` tags and common paths)
2. If RSS found: store and use RSS for ongoing checks
3. If no RSS: use LLM + agent-browser to identify CSS selectors via accessibility tree analysis
4. `wachi check` fetches each subscription, compares against dedup table (SHA-256 hash), sends new items via apprise

## Configuration

Config at `~/.config/wachi/config.yml` (auto-created on first `wachi sub`).

```yaml
# LLM config (only needed for non-RSS sites)
# Also settable via WACHI_LLM_API_KEY, WACHI_LLM_MODEL env vars
llm:
  api_key: "sk-..."
  model: "gpt-4.1-mini"

# Optional: summarize articles before sending
summary:
  enabled: true
  language: "en"
  min_reading_time: 3  # minutes

# Channels managed by wachi sub/unsub
channels:
  - apprise_url: "slack://xoxb-token/channel"
    subscriptions:
      - url: "https://blog.example.com"
        rss_url: "https://blog.example.com/feed.xml"
```

All fields optional with sensible defaults. Empty config is valid.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `WACHI_LLM_API_KEY` | LLM API key |
| `WACHI_LLM_MODEL` | LLM model name |
| `WACHI_LLM_BASE_URL` | LLM API base URL (default: OpenAI) |
| `WACHI_NO_AUTO_UPDATE` | Set to `1` to disable auto-update |

## Notification Channels

Uses [apprise](https://github.com/caronc/apprise) URL format. Examples:

```bash
# Slack
wachi sub "slack://xoxb-token/channel" "https://example.com"

# Discord
wachi sub "discord://webhook-id/token" "https://example.com"

# Telegram
wachi sub "tgram://bot-token/chat-id" "https://example.com"

# Test channel works
wachi test "slack://xoxb-token/channel"
```

Full list: https://github.com/caronc/apprise/wiki

## Scheduling

`wachi check` is stateless and one-shot. Use any scheduler:

```bash
# crnd (recommended)
crnd "*/5 * * * *" wachi check

# system cron
crontab -e
# */5 * * * * wachi check
```

## Examples

```bash
# Blog (auto-discovers RSS)
wachi sub "slack://xoxb-token/channel" "https://blog.example.com"

# Hacker News (LLM identifies selectors)
wachi sub "discord://webhook-id/token" "https://news.ycombinator.com"

# YouTube channel
wachi sub "tgram://bot-token/chat-id" "https://youtube.com/@channel"

# URL without https:// (auto-prepended)
wachi sub "slack://token/channel" "blog.example.com"

# Send existing items on next check
wachi sub -e "discord://webhook-id/token" "https://news.ycombinator.com"

# Dry-run check
wachi check -d

# Check specific channel
wachi check -c "slack://xoxb-token/channel"
```

For detailed behavior (dedup model, error patterns, notification format, config schema), see [references/spec.md](references/spec.md).
