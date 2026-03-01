"""@bruin

name: ingestion.trips
type: python
image: python:3.11

connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: taxi_type
    type: varchar
    description: Taxi type (yellow or green)
  - name: extracted_at
    type: timestamp
    description: UTC timestamp when the record was extracted
  - name: pickup_datetime
    type: timestamp
    description: Pickup timestamp, normalized from tpep_/lpep_ source columns
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff timestamp, normalized from tpep_/lpep_ source columns

@bruin"""

import json
import os
from datetime import datetime, date
from io import BytesIO

import polars as pl
import requests
from dateutil.relativedelta import relativedelta

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def materialize():
    start_date = datetime.strptime(os.environ["BRUIN_START_DATE"], "%Y-%m-%d").date()
    end_date = datetime.strptime(os.environ["BRUIN_END_DATE"], "%Y-%m-%d").date()
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])

    frames = []
    extracted_at = datetime.utcnow()
    current = date(start_date.year, start_date.month, 1)
    end = date(end_date.year, end_date.month, 1)

    while current <= end:
        year, month = current.year, current.month
        for taxi_type in taxi_types:
            url = f"{BASE_URL}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            try:
                print(f"Fetching {url}...")
                response = requests.get(url, timeout=120)
                response.raise_for_status()
                df = pl.read_parquet(BytesIO(response.content))
                df = df.with_columns([
                    pl.lit(taxi_type).alias("taxi_type"),
                    pl.lit(extracted_at).alias("extracted_at"),
                ])
                # normalize pickup/dropoff datetime across taxi types
                # (yellow: tpep_*, green: lpep_*)
                if "tpep_pickup_datetime" in df.columns:
                    df = df.with_columns(df["tpep_pickup_datetime"].alias("pickup_datetime"))
                elif "lpep_pickup_datetime" in df.columns:
                    df = df.with_columns(df["lpep_pickup_datetime"].alias("pickup_datetime"))
                if "tpep_dropoff_datetime" in df.columns:
                    df = df.with_columns(df["tpep_dropoff_datetime"].alias("dropoff_datetime"))
                elif "lpep_dropoff_datetime" in df.columns:
                    df = df.with_columns(df["lpep_dropoff_datetime"].alias("dropoff_datetime"))
                frames.append(df)
                print(f"  -> {df.height:,} rows")
            except Exception as e:
                print(f"Warning: could not fetch {url}: {e}")
        current += relativedelta(months=1)

    if not frames:
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal")
