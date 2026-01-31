#!/usr/bin/env python3
"""
Quick CSV profiling script using DuckDB.
Provides fast statistics for large CSV files without loading into memory.

Usage:
    python csv_profile.py <file.csv>
    python csv_profile.py <file.csv> --sample 10000
"""

import sys
import argparse

try:
    import duckdb
except ImportError:
    print("Error: duckdb not installed. Run: pip install duckdb")
    sys.exit(1)


def profile_csv(filepath: str, sample_size: int | None = None) -> None:
    """Profile a CSV file and print statistics."""
    
    conn = duckdb.connect()
    
    # Get row count
    count = conn.execute(f"SELECT COUNT(*) FROM '{filepath}'").fetchone()[0]
    print(f"\n{'='*60}")
    print(f"FILE: {filepath}")
    print(f"ROWS: {count:,}")
    print(f"{'='*60}\n")
    
    # Get schema
    print("SCHEMA:")
    print("-" * 40)
    schema = conn.execute(f"DESCRIBE SELECT * FROM '{filepath}'").df()
    for _, row in schema.iterrows():
        print(f"  {row['column_name']:30} {row['column_type']}")
    print()
    
    # Sample data for statistics if file is large
    source = f"'{filepath}'"
    if sample_size and count > sample_size:
        source = f"(SELECT * FROM '{filepath}' USING SAMPLE {sample_size})"
        print(f"(Statistics based on sample of {sample_size:,} rows)\n")
    
    # Get statistics for each column
    print("COLUMN STATISTICS:")
    print("-" * 40)
    
    for _, row in schema.iterrows():
        col_name = row['column_name']
        col_type = row['column_type']
        
        stats = conn.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT("{col_name}") as non_null,
                COUNT(DISTINCT "{col_name}") as unique_vals
            FROM {source}
        """).fetchone()
        
        total, non_null, unique = stats
        null_count = total - non_null
        null_pct = (null_count / total * 100) if total > 0 else 0
        
        print(f"\n  {col_name} ({col_type})")
        print(f"    Non-null: {non_null:,} | Null: {null_count:,} ({null_pct:.1f}%)")
        print(f"    Unique values: {unique:,}")
        
        # Numeric stats
        if col_type in ('BIGINT', 'INTEGER', 'DOUBLE', 'FLOAT', 'DECIMAL'):
            num_stats = conn.execute(f"""
                SELECT 
                    MIN("{col_name}"),
                    MAX("{col_name}"),
                    AVG("{col_name}"),
                    MEDIAN("{col_name}")
                FROM {source}
            """).fetchone()
            print(f"    Min: {num_stats[0]} | Max: {num_stats[1]}")
            print(f"    Mean: {num_stats[2]:.2f} | Median: {num_stats[3]}")
        
        # String stats - show top values
        elif col_type == 'VARCHAR' and unique <= 20:
            top_vals = conn.execute(f"""
                SELECT "{col_name}", COUNT(*) as cnt
                FROM {source}
                WHERE "{col_name}" IS NOT NULL
                GROUP BY "{col_name}"
                ORDER BY cnt DESC
                LIMIT 5
            """).fetchall()
            if top_vals:
                print(f"    Top values: {', '.join(f'{v[0]} ({v[1]:,})' for v in top_vals)}")
    
    # Preview data
    print(f"\n{'='*60}")
    print("SAMPLE ROWS (first 5):")
    print("-" * 40)
    preview = conn.execute(f"SELECT * FROM '{filepath}' LIMIT 5").df()
    print(preview.to_string(index=False))
    print()


def main():
    parser = argparse.ArgumentParser(description="Profile a CSV file")
    parser.add_argument("file", help="Path to CSV file")
    parser.add_argument("--sample", type=int, help="Sample size for large files")
    args = parser.parse_args()
    
    profile_csv(args.file, args.sample)


if __name__ == "__main__":
    main()
