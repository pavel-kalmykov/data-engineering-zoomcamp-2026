#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "polars>=1.19.0",
#   "adbc-driver-postgresql>=0.10.0",
#   "pyarrow>=22.0.0",
#   "click>=8.3.1",
# ]
# ///
"""
Ingest NYC green taxi data and zones into PostgreSQL.

Usage:
    uv run ingest_data.py
    uv run ingest_data.py --pg-host localhost --pg-port 5433

This script uses uv's inline dependency management (PEP 723).
Dependencies are declared in the script header and automatically installed.
Uses Polars with ADBC for fast data loading.
Reads parquet files in batches to avoid OOM on large datasets.
"""

import click
import polars as pl
import pyarrow.parquet as pq


# Batch size for reading parquet files (rows per batch)
BATCH_SIZE = 10_000


@click.command()
@click.option('--pg-user', default='postgres', help='PostgreSQL user')
@click.option('--pg-pass', default='postgres', help='PostgreSQL password')
@click.option('--pg-host', default='db', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--green-taxi-file', default='data/green_tripdata_2025-11.parquet', help='Green taxi parquet file path')
@click.option('--zones-file', default='data/taxi_zone_lookup.csv', help='Zones CSV file path')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, green_taxi_file, zones_file):
    """Ingest NYC green taxi data and zones into PostgreSQL database."""

    connection_uri = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'

    # Load green taxi data in batches to avoid OOM
    print(f"Loading green taxi data from {green_taxi_file} in batches...")
    parquet_file = pq.ParquetFile(green_taxi_file)
    total_rows = 0

    for i, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
        # Convert Arrow batch to Polars DataFrame
        df_batch = pl.from_arrow(batch)

        # First batch replaces table, subsequent batches append
        df_batch.write_database(
            table_name='green_taxi_data',
            connection=connection_uri,
            if_table_exists='replace' if i == 0 else 'append',
            engine='adbc'
        )

        total_rows += len(df_batch)
        print(f"  Batch {i+1}: {len(df_batch)} rows (total: {total_rows})")

    print(f"Loaded {total_rows} green taxi records in {i+1} batches")

    # Load zones with Polars (small file, no batching needed)
    print(f"Loading zones from {zones_file}...")
    df_zones = pl.read_csv(zones_file)
    df_zones.write_database(
        table_name='zones',
        connection=connection_uri,
        if_table_exists='replace',
        engine='adbc'
    )
    print(f"Loaded {len(df_zones)} zone records")

if __name__ == '__main__':
    run()
