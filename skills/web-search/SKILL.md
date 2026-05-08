---
name: web-search
description: Search the web from the command line using duckduckgo-cli. Use this skill whenever you need current information, latest news, recent events, fact-checking, research, documentation lookups, or any answer that may have changed since training. Trigger this even when the user doesn't say "search" — phrases like "what's the latest...", "find out...", "look up...", "is X still true?", "who is the current...", "compare prices/options", or any question about recent things should activate it.
---

# Web Search

This skill uses `duckduckgo-cli` — a command-line search tool that returns DuckDuckGo results as plain text or JSON. It's built for LLM agents: plain text output is compact (title, URL, snippet per result) and the flags let you control time, region, site, and count.

## When to reach for this

- The user asks about something recent ("latest", "today", "current", a year at or past your knowledge cutoff)
- A claim needs verification
- Documentation, references, or external context is needed
- The user asks to search, look up, find out, research, or check something
- You're answering a factual question and you're not sure your knowledge is current

Once you're already in a conversation, you don't need explicit permission — just search.

## Command

The CLI is invoked as `ddg` (a short alias for `duckduckgo-cli`).

```sh
ddg rust async tutorial             # plain text, default 10 results
ddg -n 5 "best Rust web framework 2026"
ddg --json -n 5 "topic"              # JSON envelope, for parsing
echo "tokio runtime overhead" | ddg  # query via stdin
```

Plain text is the default and the right choice for most uses — it's compact and you can quote URLs and snippets straight out of it.

## Flags worth knowing

**`-n <N>`** — number of results (1–100, default 10). Use 3–5 for quick lookups, 10–20 for broader research. More results cost tokens and the long tail rarely helps.

**`-t <d|w|m|y>`** — restrict to past day / week / month / year. **Critical for "latest" or "recent" questions** — without it, evergreen pages outrank fresh ones and you'll quote stale info.

**`-w <DOMAIN>`** — repeatable site filter. Use for official docs (`-w docs.python.org`), known-trusted sources, or to dodge spam.

**`-r <CODE>`** — region (e.g., `us-en`, `kr-ko`, `jp-jp`, `de-de`). Match the language of the query. Run `ddg --list-regions` to see them all.

**`--json`** — compact JSON envelope. Use only when parsing programmatically (counting results, extracting URLs into a script). For ordinary reading and citing, plain text is better.

**`--page <N>`** — paginate when the first page didn't have what you needed.

## Patterns

### Quick fact lookup
```sh
ddg -n 3 "current ceo of openai"
```
Three results is enough to triangulate a consensus answer.

### Latest news / recent updates
```sh
ddg -n 5 -t w "anthropic claude release"
```
The `-t w` filter is what makes this useful — without it you'll get older articles that rank well.

### Documentation
```sh
ddg -n 5 -w docs.python.org "asyncio gather exception"
```

### Fact-check a specific claim
```sh
ddg -n 5 "the exact phrasing of the claim"
```
Read snippets carefully. If sources disagree, surface that to the user — don't pick one and present it as fact.

### Broader research
Run several focused queries rather than one giant one. Three `-n 10` queries on different angles beat one `-n 30`.

## Reading the output

Each result has a position, title, URL, and a short snippet. The snippet is usually enough to decide whether to fetch the page in full with `WebFetch`. When citing to the user, include the URL so they can verify; if you only have a snippet, say "from the search snippet..." rather than implying you read the whole page.

## Gotchas

- **Rate limits**: in `--json` mode the response includes `meta.rate_limit.tokens_remaining`. If it hits 0, back off — don't fire more queries in a tight loop.
- **No instant answer is normal** — most queries just return the numbered list.
- **Region must match language** — a Korean query with `-r us-en` will return weaker results; use `-r kr-ko`.
- **Don't pipe to `head` to truncate** — use `-n` instead, otherwise a result may get chopped mid-snippet.
- **If the binary isn't installed**, install with `npm i -g duckduckgo-cli` or `cargo install duckduckgo-cli`.
