{{ config(materialized='view') }}

-- Staging model for FHV (For-Hire Vehicle) trip data
-- Converts raw column names (camelCase/PascalCase) to snake_case for consistency

with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        -- identifiers
        dispatching_base_num,           -- already snake_case
        Affiliated_base_number as affiliated_base_number,

        -- timestamps (convert camelCase to snake_case)
        pickup_datetime,                -- already snake_case
        dropOff_datetime as dropoff_datetime,

        -- location ids (convert PascalCase to snake_case)
        PUlocationID as pickup_location_id,
        DOlocationID as dropoff_location_id,

        -- flags
        SR_Flag as sr_flag

    from source
    where dispatching_base_num is not null  -- Filter out records without base number
)

select * from renamed
