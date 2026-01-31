---
name: csv-analyzer
description: Analyze and process large CSV files (1M+ rows) using DuckDB and Polars. Use when the user asks to analyze, query, filter, aggregate, join, or transform CSV data. Triggers on requests like "analyze this CSV", "query CSV file", "filter large dataset", "aggregate CSV data", "join CSV files", "CSV statistics", or any data analysis task involving CSV/TSV/Parquet files.
---

# CSV Analyzer

Analyze large CSV files (1M+ rows) efficiently using DuckDB (SQL) and Polars (DataFrame API).

## Tool Selection

| Task | Use DuckDB | Use Polars |
|------|------------|------------|
| SQL queries on CSV | Yes | No |
| Aggregations, GROUP BY | Yes | Yes |
| Joins between files | Yes (better) | Yes |
| Chained transformations | No | Yes (better) |
| Larger-than-memory | Yes | Yes (lazy mode) |
| Quick stats/preview | Yes | Yes |

**Default to DuckDB** for most analytical queries. Use Polars for complex DataFrame transformations.

## Quick Start

### DuckDB - Query CSV directly (no loading needed)

```python
import duckdb

# Query CSV file directly - no need to load into memory
result = duckdb.sql("""
    SELECT column1, COUNT(*) as cnt
    FROM 'data.csv'
    GROUP BY column1
    ORDER BY cnt DESC
    LIMIT 10
""").df()
```

### Polars - DataFrame operations

```python
import polars as pl

# Lazy mode for large files (recommended)
df = pl.scan_csv("data.csv")
result = (
    df.filter(pl.col("value") > 100)
    .group_by("category")
    .agg(pl.col("value").sum())
    .collect()
)
```

## Common Operations

### 1. Preview Data

```python
# DuckDB
duckdb.sql("SELECT * FROM 'data.csv' LIMIT 10").df()
duckdb.sql("DESCRIBE SELECT * FROM 'data.csv'").df()  # Schema

# Polars
pl.read_csv("data.csv", n_rows=10)
pl.scan_csv("data.csv").collect_schema()  # Schema
```

### 2. Row Count

```python
# DuckDB
duckdb.sql("SELECT COUNT(*) FROM 'data.csv'").fetchone()[0]

# Polars
pl.scan_csv("data.csv").select(pl.len()).collect().item()
```

### 3. Filter Rows

```python
# DuckDB
duckdb.sql("""
    SELECT * FROM 'data.csv'
    WHERE status = 'active' AND value > 1000
""").df()

# Polars
pl.scan_csv("data.csv").filter(
    (pl.col("status") == "active") & (pl.col("value") > 1000)
).collect()
```

### 4. Aggregations

```python
# DuckDB
duckdb.sql("""
    SELECT category,
           COUNT(*) as count,
           SUM(value) as total,
           AVG(value) as avg,
           MIN(value) as min,
           MAX(value) as max
    FROM 'data.csv'
    GROUP BY category
""").df()

# Polars
pl.scan_csv("data.csv").group_by("category").agg(
    pl.len().alias("count"),
    pl.col("value").sum().alias("total"),
    pl.col("value").mean().alias("avg"),
    pl.col("value").min().alias("min"),
    pl.col("value").max().alias("max"),
).collect()
```

### 5. Join Multiple CSVs

```python
# DuckDB (best for joins)
duckdb.sql("""
    SELECT a.*, b.extra_info
    FROM 'orders.csv' a
    LEFT JOIN 'customers.csv' b ON a.customer_id = b.id
""").df()

# Polars
orders = pl.scan_csv("orders.csv")
customers = pl.scan_csv("customers.csv")
orders.join(customers, left_on="customer_id", right_on="id", how="left").collect()
```

### 6. Window Functions

```python
# DuckDB
duckdb.sql("""
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) as rank,
           SUM(value) OVER (PARTITION BY category) as category_total
    FROM 'data.csv'
""").df()

# Polars
pl.scan_csv("data.csv").with_columns(
    pl.col("value").rank(descending=True).over("category").alias("rank"),
    pl.col("value").sum().over("category").alias("category_total"),
).collect()
```

### 7. Date/Time Operations

```python
# DuckDB
duckdb.sql("""
    SELECT DATE_TRUNC('month', date_col) as month,
           SUM(value) as monthly_total
    FROM 'data.csv'
    GROUP BY 1
    ORDER BY 1
""").df()

# Polars
pl.scan_csv("data.csv").with_columns(
    pl.col("date_col").str.to_datetime()
).group_by(pl.col("date_col").dt.month()).agg(
    pl.col("value").sum()
).collect()
```

### 8. Export Results

```python
# DuckDB - write to various formats
duckdb.sql("COPY (SELECT * FROM 'data.csv' WHERE value > 100) TO 'filtered.csv'")
duckdb.sql("COPY (SELECT * FROM 'data.csv') TO 'output.parquet' (FORMAT PARQUET)")

# Polars
df.write_csv("output.csv")
df.write_parquet("output.parquet")
```

## Performance Tips

1. **Use Parquet instead of CSV** when possible - 10x faster reads
   ```python
   # Convert CSV to Parquet once
   duckdb.sql("COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT PARQUET)")
   # Then query Parquet
   duckdb.sql("SELECT * FROM 'data.parquet' WHERE ...")
   ```

2. **DuckDB can query multiple files with glob patterns**
   ```python
   duckdb.sql("SELECT * FROM 'data_*.csv'")  # All matching files
   duckdb.sql("SELECT * FROM 'logs/**/*.csv'")  # Recursive
   ```

3. **Polars lazy mode** for memory efficiency
   ```python
   # Always use scan_csv (lazy) instead of read_csv for large files
   df = pl.scan_csv("large.csv")  # Nothing loaded yet
   result = df.filter(...).select(...).collect()  # Optimized execution
   ```

4. **DuckDB memory limits** for very large files
   ```python
   duckdb.sql("SET memory_limit = '8GB'")
   ```

## Installation

```bash
pip install duckdb polars
```

## References

- See `references/duckdb_reference.md` for DuckDB SQL syntax
- See `references/polars_reference.md` for Polars DataFrame API
