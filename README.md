# Skills

Agent skills for Claude Code, Cursor, Codex, and other coding agents.

## Available Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [csv-analyzer](./skills/csv-analyzer) | Analyze large CSV files (1M+ rows) with DuckDB and Polars | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/csv-analyzer` |
| [ddgr](./skills/ddgr) | Search the web using DuckDuckGo via ddgr CLI | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/ddgr` |
| [duckdb-cli](./skills/duckdb-cli) | Query and analyze data (CSV/Parquet/JSON) using DuckDB CLI | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/duckdb-cli` |
| [wachi](./skills/wachi) | Install and use wachi CLI to monitor any URL for new content and get notifications via 90+ services | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/wachi` |
| [web-scraper](./skills/web-scraper) | Bulk-scrape structured data from websites by discovering APIs through HAR capture | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/web-scraper` |

## Installation

Install any skill using the [skills CLI](https://github.com/vercel-labs/skills):

```bash
# Install csv-analyzer
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/csv-analyzer

# Install ddgr
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/ddgr

# Install duckdb-cli
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/duckdb-cli

# Install wachi
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/wachi

# Install web-scraper
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/web-scraper
```

## License

MIT
