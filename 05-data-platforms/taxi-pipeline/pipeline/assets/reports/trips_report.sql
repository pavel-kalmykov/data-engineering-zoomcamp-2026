/* @bruin

name: reports.trips_report
type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: trip_date
  time_granularity: date

columns:
  - name: trip_date
    type: date
    description: Date of the trips (truncated from pickup_datetime)
    primary_key: true
  - name: taxi_type
    type: varchar
    description: Taxi type (yellow or green)
    primary_key: true
  - name: payment_type_name
    type: varchar
    description: Human-readable payment method
    primary_key: true
  - name: trip_count
    type: bigint
    description: Number of trips in this group
    checks:
      - name: non_negative
  - name: total_revenue
    type: float
    description: Sum of total_amount for all trips in the group
  - name: total_tips
    type: float
    description: Sum of tip_amount for all trips in the group
  - name: avg_trip_distance
    type: float
    description: Average trip distance in miles

@bruin */

SELECT
    pickup_datetime::DATE                      AS trip_date,
    taxi_type,
    COALESCE(payment_type_name, 'unknown')     AS payment_type_name,
    COUNT(*)                                   AS trip_count,
    SUM(total_amount)                          AS total_revenue,
    SUM(tip_amount)                            AS total_tips,
    AVG(trip_distance)                         AS avg_trip_distance
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY 1, 2, 3
