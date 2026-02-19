# Skills

Agent skills for Claude Code, Cursor, Codex, and other coding agents.

## Available Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [csv-analyzer](./skills/csv-analyzer) | Analyze large CSV files (1M+ rows) with DuckDB and Polars | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/csv-analyzer` |
| [ddgr](./skills/ddgr) | Search the web using DuckDuckGo via ddgr CLI | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/ddgr` |
| [duckdb-cli](./skills/duckdb-cli) | Query and analyze data (CSV/Parquet/JSON) using DuckDB CLI | `npx skills add https://github.com/ysm-dev/skills/tree/main/skills/duckdb-cli` |

## Installation

Install any skill using the [skills CLI](https://github.com/vercel-labs/skills):

```bash
# Install csv-analyzer
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/csv-analyzer

# Install ddgr
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/ddgr

# Install duckdb-cli
npx skills add https://github.com/ysm-dev/skills/tree/main/skills/duckdb-cli
```

## License

MIT
