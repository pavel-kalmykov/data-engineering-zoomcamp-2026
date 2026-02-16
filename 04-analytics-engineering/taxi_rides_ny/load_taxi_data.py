#!/usr/bin/env python3
"""
Load NYC Taxi data into DuckDB.
Supports Yellow, Green, and FHV taxi data.

Usage:
    python load_taxi_data.py yellow green --year 2019 2020
    python load_taxi_data.py fhv --year 2019
    python load_taxi_data.py --all
"""

import argparse
import duckdb
import requests
from pathlib import Path
from typing import List

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"


def download_and_convert_file(
    taxi_type: str,
    year: int,
    month: int,
    data_dir: Path
) -> None:
    """Download a single CSV.gz file and convert to parquet."""
    parquet_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    parquet_filepath = data_dir / parquet_filename

    if parquet_filepath.exists():
        print(f"✓ Skipping {parquet_filename} (already exists)")
        return

    csv_gz_filename = f"{taxi_type}_tripdata_{year}-{month:02d}.csv.gz"
    csv_gz_filepath = data_dir / csv_gz_filename

    print(f"↓ Downloading {csv_gz_filename}...")
    response = requests.get(
        f"{BASE_URL}/{taxi_type}/{csv_gz_filename}",
        stream=True
    )
    response.raise_for_status()

    with open(csv_gz_filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"⚙ Converting {csv_gz_filename} to Parquet...")
    con = duckdb.connect()
    con.execute(f"""
        COPY (SELECT * FROM read_csv_auto('{csv_gz_filepath}'))
        TO '{parquet_filepath}' (FORMAT PARQUET)
    """)
    con.close()

    csv_gz_filepath.unlink()
    print(f"✓ Completed {parquet_filename}")


def download_taxi_data(taxi_type: str, years: List[int]) -> None:
    """Download and convert taxi data for given years."""
    data_dir = Path("data") / taxi_type
    data_dir.mkdir(exist_ok=True, parents=True)

    print(f"\n{'='*50}")
    print(f"Processing {taxi_type.upper()} taxi data")
    print('='*50)

    for year in years:
        for month in range(1, 13):
            download_and_convert_file(taxi_type, year, month, data_dir)


def load_into_duckdb(taxi_types: List[str]) -> None:
    """Load parquet files into DuckDB prod schema."""
    print("\n⚙ Loading data into DuckDB...")

    con = duckdb.connect("taxi_rides_ny.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS prod")

    for taxi_type in taxi_types:
        print(f"⚙ Loading {taxi_type} taxi data into prod.{taxi_type}_tripdata...")
        con.execute(f"""
            CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
            SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
        """)

        count = con.execute(
            f"SELECT COUNT(*) FROM prod.{taxi_type}_tripdata"
        ).fetchone()[0]
        print(f"✓ Loaded {count:,} rows into prod.{taxi_type}_tripdata")

    con.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load NYC Taxi data into DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s yellow green --year 2019 2020
  %(prog)s fhv --year 2019
  %(prog)s --all
        """
    )

    parser.add_argument(
        'taxi_types',
        nargs='*',
        choices=['yellow', 'green', 'fhv'],
        help='Taxi types to load (yellow, green, fhv)'
    )
    parser.add_argument(
        '--year',
        type=int,
        nargs='+',
        default=[2019, 2020],
        help='Years to download (default: 2019 2020)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Load all taxi types (yellow, green, fhv)'
    )

    args = parser.parse_args()

    # Determine which taxi types to process
    if args.all:
        taxi_types = ['yellow', 'green', 'fhv']
    elif not args.taxi_types:
        parser.error("Please specify taxi types or use --all")
    else:
        taxi_types = args.taxi_types

    print("NYC Taxi Data Loader")
    print("=" * 50)
    print(f"Taxi types: {', '.join(taxi_types)}")
    print(f"Years: {', '.join(map(str, args.year))}")
    print("=" * 50)

    # Download data for each taxi type
    for taxi_type in taxi_types:
        download_taxi_data(taxi_type, args.year)

    # Load all data into DuckDB
    load_into_duckdb(taxi_types)

    print("\n✓ All data loaded successfully!")


if __name__ == "__main__":
    main()
