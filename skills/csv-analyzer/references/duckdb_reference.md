# DuckDB Reference for CSV Analysis

## Table of Contents
- [Reading Files](#reading-files)
- [Data Types](#data-types)
- [Filtering](#filtering)
- [Aggregations](#aggregations)
- [Window Functions](#window-functions)
- [String Functions](#string-functions)
- [Date/Time Functions](#date-time-functions)
- [Joins](#joins)
- [Writing Output](#writing-output)

## Reading Files

```sql
-- CSV (auto-detect settings)
SELECT * FROM 'file.csv'
SELECT * FROM read_csv('file.csv')

-- CSV with options
SELECT * FROM read_csv('file.csv', 
    header=true,
    delimiter=',',
    quote='"',
    escape='"',
    nullstr='NA',
    skip=1,
    columns={'col1': 'VARCHAR', 'col2': 'INTEGER'}
)

-- Multiple files
SELECT * FROM 'data_*.csv'
SELECT * FROM 'logs/**/*.csv'  -- recursive

-- Parquet (faster)
SELECT * FROM 'file.parquet'
SELECT * FROM read_parquet('data/*.parquet')

-- JSON
SELECT * FROM read_json('file.json')
SELECT * FROM read_json_auto('file.jsonl')
```

## Data Types

```sql
-- Cast types
SELECT column::INTEGER, column::VARCHAR, column::DATE
SELECT CAST(column AS DOUBLE)
SELECT TRY_CAST(column AS INTEGER)  -- returns NULL on failure

-- Type checking
SELECT typeof(column) FROM table

-- Common types: BOOLEAN, INTEGER, BIGINT, DOUBLE, VARCHAR, DATE, TIMESTAMP, INTERVAL
```

## Filtering

```sql
-- Basic
WHERE column = 'value'
WHERE column > 100
WHERE column BETWEEN 10 AND 20
WHERE column IN ('a', 'b', 'c')
WHERE column IS NOT NULL
WHERE column LIKE '%pattern%'
WHERE column ILIKE '%pattern%'  -- case insensitive

-- Regex
WHERE regexp_matches(column, '^[A-Z]+$')

-- Multiple conditions
WHERE (a > 10 AND b < 20) OR c = 'value'
```

## Aggregations

```sql
-- Basic aggregates
SELECT 
    COUNT(*),
    COUNT(DISTINCT column),
    SUM(value),
    AVG(value),
    MIN(value),
    MAX(value),
    MEDIAN(value),
    STDDEV(value),
    VARIANCE(value)
FROM table

-- Group by
SELECT category, COUNT(*), SUM(value)
FROM table
GROUP BY category
HAVING COUNT(*) > 10
ORDER BY COUNT(*) DESC

-- Group by multiple
SELECT cat1, cat2, SUM(value)
FROM table
GROUP BY cat1, cat2
GROUP BY ALL  -- auto group by non-aggregated columns

-- Rollup/Cube
SELECT category, subcategory, SUM(value)
FROM table
GROUP BY ROLLUP (category, subcategory)
```

## Window Functions

```sql
SELECT *,
    -- Ranking
    ROW_NUMBER() OVER (ORDER BY value DESC),
    RANK() OVER (ORDER BY value DESC),
    DENSE_RANK() OVER (ORDER BY value DESC),
    NTILE(4) OVER (ORDER BY value),
    
    -- Aggregates over window
    SUM(value) OVER (PARTITION BY category),
    AVG(value) OVER (PARTITION BY category ORDER BY date),
    
    -- Running totals
    SUM(value) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING),
    
    -- Moving averages
    AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
    
    -- Lead/Lag
    LAG(value, 1) OVER (ORDER BY date),
    LEAD(value, 1) OVER (ORDER BY date),
    
    -- First/Last
    FIRST_VALUE(value) OVER (PARTITION BY category ORDER BY date),
    LAST_VALUE(value) OVER (PARTITION BY category ORDER BY date)
FROM table
```

## String Functions

```sql
-- Basic
LENGTH(str), UPPER(str), LOWER(str), TRIM(str)
LEFT(str, n), RIGHT(str, n), SUBSTRING(str, start, len)
CONCAT(str1, str2), str1 || str2
REPLACE(str, 'old', 'new')
SPLIT_PART(str, delimiter, index)

-- Regex
regexp_extract(str, pattern, group)
regexp_replace(str, pattern, replacement)
regexp_matches(str, pattern)

-- Example: extract domain from URL
regexp_extract(url, 'https?://([^/]+)/', 1)
```

## Date Time Functions

```sql
-- Current
CURRENT_DATE, CURRENT_TIMESTAMP, NOW()

-- Extract parts
YEAR(date), MONTH(date), DAY(date)
HOUR(ts), MINUTE(ts), SECOND(ts)
DAYOFWEEK(date), DAYOFYEAR(date), WEEK(date)

-- Truncate
DATE_TRUNC('month', date)  -- 'year', 'quarter', 'month', 'week', 'day', 'hour'

-- Arithmetic
date + INTERVAL '7 days'
date - INTERVAL '1 month'
DATEDIFF('day', date1, date2)

-- Parse strings
STRPTIME(str, '%Y-%m-%d')::DATE
STRFTIME(date, '%Y-%m-%d')

-- Generate series
SELECT * FROM generate_series(DATE '2024-01-01', DATE '2024-12-31', INTERVAL '1 day')
```

## Joins

```sql
-- Inner join
SELECT a.*, b.col
FROM table_a a
JOIN table_b b ON a.id = b.id

-- Left/Right/Full outer
LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN

-- Cross join
CROSS JOIN

-- Anti join (rows in A not in B)
SELECT * FROM a
WHERE NOT EXISTS (SELECT 1 FROM b WHERE a.id = b.id)

-- Semi join (rows in A that exist in B)
SELECT * FROM a
WHERE EXISTS (SELECT 1 FROM b WHERE a.id = b.id)

-- Join files directly
SELECT a.*, b.*
FROM 'orders.csv' a
JOIN 'customers.csv' b ON a.customer_id = b.id
```

## Writing Output

```sql
-- CSV
COPY (SELECT * FROM table) TO 'output.csv' (HEADER, DELIMITER ',')

-- Parquet (recommended for large data)
COPY (SELECT * FROM table) TO 'output.parquet' (FORMAT PARQUET)
COPY (SELECT * FROM table) TO 'output.parquet' (FORMAT PARQUET, COMPRESSION 'zstd')

-- JSON
COPY (SELECT * FROM table) TO 'output.json' (FORMAT JSON)

-- Partitioned output
COPY (SELECT * FROM table) TO 'output' (FORMAT PARQUET, PARTITION_BY (year, month))
```

## Useful Patterns

```sql
-- Sample rows
SELECT * FROM table USING SAMPLE 1000
SELECT * FROM table USING SAMPLE 10%

-- Distinct values
SELECT DISTINCT column FROM table
SELECT DISTINCT ON (category) * FROM table ORDER BY value DESC

-- Conditional aggregation
SELECT 
    COUNT(*) FILTER (WHERE status = 'active') as active_count,
    SUM(value) FILTER (WHERE year = 2024) as sum_2024
FROM table

-- Pivot (manual)
SELECT category,
    SUM(CASE WHEN year = 2023 THEN value END) as y2023,
    SUM(CASE WHEN year = 2024 THEN value END) as y2024
FROM table
GROUP BY category

-- CTE (Common Table Expression)
WITH filtered AS (
    SELECT * FROM table WHERE status = 'active'
),
aggregated AS (
    SELECT category, SUM(value) as total FROM filtered GROUP BY category
)
SELECT * FROM aggregated WHERE total > 1000
```
