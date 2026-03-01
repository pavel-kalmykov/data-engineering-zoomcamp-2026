/* @bruin

name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp

columns:
  - name: pickup_datetime
    type: timestamp
    description: Pickup timestamp
    primary_key: true
    nullable: false
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff timestamp
    primary_key: true
  - name: pickup_location_id
    type: integer
    description: TLC zone ID where the trip started
    primary_key: true
  - name: dropoff_location_id
    type: integer
    description: TLC zone ID where the trip ended
    primary_key: true
  - name: fare_amount
    type: float
    description: Base fare amount in USD
    primary_key: true
  - name: taxi_type
    type: varchar
    description: Taxi type (yellow or green)
    checks:
      - name: not_null
  - name: trip_distance
    type: float
    description: Distance traveled in miles
    checks:
      - name: non_negative
  - name: total_amount
    type: float
    description: Total amount charged to the passenger
  - name: payment_type_name
    type: varchar
    description: Human-readable payment method from lookup table

custom_checks:
  - name: all_trips_have_pickup_datetime
    description: Every staged trip must have a valid pickup timestamp
    query: |
      SELECT COUNT(*)
      FROM staging.trips
      WHERE pickup_datetime >= '{{ start_datetime }}'
        AND pickup_datetime < '{{ end_datetime }}'
        AND pickup_datetime IS NULL
    value: 0

@bruin */

WITH raw AS (
    SELECT
        pickup_datetime,
        dropoff_datetime,
        taxi_type,
        vendor_id,
        ratecode_id,
        store_and_fwd_flag,
        pu_location_id       AS pickup_location_id,
        do_location_id       AS dropoff_location_id,
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        payment_type,
        congestion_surcharge,
        extracted_at
    FROM ingestion.trips
    WHERE pickup_datetime >= '{{ start_datetime }}'
      AND pickup_datetime < '{{ end_datetime }}'
      AND pickup_datetime IS NOT NULL
),

deduplicated AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY pickup_datetime, dropoff_datetime,
                            pickup_location_id, dropoff_location_id, fare_amount
               ORDER BY extracted_at DESC
           ) AS rn
    FROM raw
)

SELECT
    d.pickup_datetime,
    d.dropoff_datetime,
    d.taxi_type,
    d.vendor_id,
    d.ratecode_id,
    d.store_and_fwd_flag,
    d.pickup_location_id,
    d.dropoff_location_id,
    d.passenger_count,
    d.trip_distance,
    d.fare_amount,
    d.extra,
    d.mta_tax,
    d.tip_amount,
    d.tolls_amount,
    d.improvement_surcharge,
    d.total_amount,
    d.payment_type,
    p.payment_type_name,
    d.congestion_surcharge,
    d.extracted_at
FROM deduplicated d
LEFT JOIN ingestion.payment_lookup p ON d.payment_type = p.payment_type_id
WHERE d.rn = 1
