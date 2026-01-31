# Polars Reference for CSV Analysis

## Table of Contents
- [Reading Files](#reading-files)
- [Lazy vs Eager](#lazy-vs-eager)
- [Selecting Columns](#selecting-columns)
- [Filtering](#filtering)
- [Aggregations](#aggregations)
- [Window Functions](#window-functions)
- [String Operations](#string-operations)
- [Date/Time Operations](#date-time-operations)
- [Joins](#joins)
- [Writing Output](#writing-output)

## Reading Files

```python
import polars as pl

# CSV - Eager (loads into memory)
df = pl.read_csv("file.csv")

# CSV - Lazy (recommended for large files)
df = pl.scan_csv("file.csv")

# CSV with options
df = pl.scan_csv("file.csv",
    has_header=True,
    separator=",",
    skip_rows=1,
    n_rows=1000,  # limit rows
    null_values=["NA", ""],
    dtypes={"col1": pl.Utf8, "col2": pl.Int64}
)

# Multiple files
df = pl.scan_csv("data_*.csv")

# Parquet (faster)
df = pl.scan_parquet("file.parquet")
df = pl.scan_parquet("data/*.parquet")

# JSON
df = pl.read_json("file.json")
df = pl.read_ndjson("file.jsonl")
```

## Lazy vs Eager

```python
# Eager - executes immediately, loads all data
df = pl.read_csv("file.csv")
result = df.filter(pl.col("value") > 100)  # executes now

# Lazy - builds query plan, optimizes, executes on .collect()
df = pl.scan_csv("file.csv")
query = df.filter(pl.col("value") > 100)  # nothing executed yet
result = query.collect()  # executes optimized query

# Always use lazy (scan_*) for large files
# Benefits: query optimization, memory efficiency, parallel execution
```

## Selecting Columns

```python
# Select columns
df.select("col1", "col2")
df.select(pl.col("col1"), pl.col("col2"))
df.select(pl.all())
df.select(pl.exclude("unwanted_col"))

# Select by type
df.select(pl.col(pl.Utf8))  # all string columns
df.select(pl.col(pl.NUMERIC_DTYPES))  # all numeric

# Rename
df.rename({"old_name": "new_name"})

# Add/modify columns
df.with_columns(
    pl.col("value").alias("value_copy"),
    (pl.col("a") + pl.col("b")).alias("sum"),
    pl.lit("constant").alias("new_col")
)

# Drop columns
df.drop("col1", "col2")
```

## Filtering

```python
# Basic filters
df.filter(pl.col("value") > 100)
df.filter(pl.col("status") == "active")
df.filter(pl.col("name").is_null())
df.filter(pl.col("name").is_not_null())

# Multiple conditions
df.filter(
    (pl.col("value") > 100) & (pl.col("status") == "active")
)
df.filter(
    (pl.col("a") > 10) | (pl.col("b") < 5)
)

# In list
df.filter(pl.col("category").is_in(["a", "b", "c"]))

# String matching
df.filter(pl.col("name").str.contains("pattern"))
df.filter(pl.col("name").str.starts_with("prefix"))
df.filter(pl.col("name").str.ends_with("suffix"))

# Between
df.filter(pl.col("value").is_between(10, 100))

# Top N
df.top_k(10, by="value")
df.sort("value", descending=True).head(10)
```

## Aggregations

```python
# Basic aggregates
df.select(
    pl.len(),  # count rows
    pl.col("value").sum(),
    pl.col("value").mean(),
    pl.col("value").min(),
    pl.col("value").max(),
    pl.col("value").std(),
    pl.col("value").median(),
    pl.col("category").n_unique(),
)

# Group by
df.group_by("category").agg(
    pl.len().alias("count"),
    pl.col("value").sum().alias("total"),
    pl.col("value").mean().alias("avg"),
)

# Group by multiple columns
df.group_by("cat1", "cat2").agg(...)

# Group by with sorting
df.group_by("category").agg(...).sort("count", descending=True)

# Conditional aggregation
df.group_by("category").agg(
    pl.col("value").filter(pl.col("status") == "active").sum().alias("active_sum")
)
```

## Window Functions

```python
# Over (partition by)
df.with_columns(
    pl.col("value").sum().over("category").alias("category_total"),
    pl.col("value").mean().over("category").alias("category_avg"),
    pl.col("value").rank().over("category").alias("rank_in_category"),
)

# Rolling windows (sorted data)
df.sort("date").with_columns(
    pl.col("value").rolling_mean(window_size=7).alias("rolling_avg_7d"),
    pl.col("value").rolling_sum(window_size=30).alias("rolling_sum_30d"),
)

# Cumulative
df.with_columns(
    pl.col("value").cum_sum().alias("cumulative_sum"),
    pl.col("value").cum_max().alias("running_max"),
)

# Shift (lead/lag)
df.with_columns(
    pl.col("value").shift(1).alias("prev_value"),  # lag
    pl.col("value").shift(-1).alias("next_value"),  # lead
)
```

## String Operations

```python
# Basic
pl.col("str").str.len_chars()
pl.col("str").str.to_uppercase()
pl.col("str").str.to_lowercase()
pl.col("str").str.strip_chars()
pl.col("str").str.replace("old", "new")
pl.col("str").str.replace_all("old", "new")

# Split
pl.col("str").str.split(",")
pl.col("str").str.split(",").list.get(0)  # first element

# Regex
pl.col("str").str.extract(r"pattern", group_index=1)
pl.col("str").str.extract_all(r"pattern")
pl.col("str").str.contains(r"pattern")
pl.col("str").str.replace(r"pattern", "replacement")

# Example: extract domain from URL
pl.col("url").str.extract(r"https?://([^/]+)/", group_index=1)
```

## Date Time Operations

```python
# Parse strings to datetime
pl.col("date_str").str.to_datetime("%Y-%m-%d")
pl.col("ts_str").str.to_datetime("%Y-%m-%d %H:%M:%S")

# Extract parts
pl.col("date").dt.year()
pl.col("date").dt.month()
pl.col("date").dt.day()
pl.col("ts").dt.hour()
pl.col("ts").dt.minute()
pl.col("date").dt.weekday()  # 0=Monday
pl.col("date").dt.week()

# Truncate
pl.col("date").dt.truncate("1mo")  # month
pl.col("date").dt.truncate("1w")   # week
pl.col("date").dt.truncate("1d")   # day

# Arithmetic
pl.col("date") + pl.duration(days=7)
pl.col("date") - pl.duration(months=1)
(pl.col("date2") - pl.col("date1")).dt.total_days()

# Filter by date
df.filter(pl.col("date") >= pl.date(2024, 1, 1))
df.filter(pl.col("date").is_between(pl.date(2024, 1, 1), pl.date(2024, 12, 31)))
```

## Joins

```python
# Inner join
df1.join(df2, on="id", how="inner")

# Left/Right/Outer
df1.join(df2, on="id", how="left")
df1.join(df2, on="id", how="outer")

# Different column names
df1.join(df2, left_on="customer_id", right_on="id", how="left")

# Multiple join keys
df1.join(df2, on=["key1", "key2"], how="inner")

# Anti join (rows in df1 not in df2)
df1.join(df2, on="id", how="anti")

# Semi join (rows in df1 that exist in df2)
df1.join(df2, on="id", how="semi")

# Join lazy frames (recommended for large files)
orders = pl.scan_csv("orders.csv")
customers = pl.scan_csv("customers.csv")
result = orders.join(customers, left_on="customer_id", right_on="id").collect()
```

## Writing Output

```python
# CSV
df.write_csv("output.csv")
df.write_csv("output.csv", separator=",", include_header=True)

# Parquet (recommended)
df.write_parquet("output.parquet")
df.write_parquet("output.parquet", compression="zstd")

# JSON
df.write_json("output.json")
df.write_ndjson("output.jsonl")

# From lazy frame - collect then write
df.collect().write_csv("output.csv")

# Or use sink for streaming write (memory efficient)
df.sink_parquet("output.parquet")
df.sink_csv("output.csv")
```

## Useful Patterns

```python
# Sample rows
df.sample(n=1000)
df.sample(fraction=0.1)

# Unique values
df.select(pl.col("category").unique())
df.unique(subset=["col1", "col2"])

# Null handling
df.fill_null(0)
df.fill_null(strategy="forward")
df.drop_nulls()
df.drop_nulls(subset=["col1", "col2"])

# Type casting
df.with_columns(
    pl.col("str_col").cast(pl.Int64),
    pl.col("int_col").cast(pl.Utf8),
)

# Pivot
df.pivot(
    values="value",
    index="category",
    on="year",
    aggregate_function="sum"
)

# Unpivot (melt)
df.unpivot(
    index=["id"],
    on=["col1", "col2", "col3"],
    variable_name="metric",
    value_name="value"
)

# Describe (statistics)
df.describe()

# Schema
df.collect_schema()  # for lazy
df.schema  # for eager
```
