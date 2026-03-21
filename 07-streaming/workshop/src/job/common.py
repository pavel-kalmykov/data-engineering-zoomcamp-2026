from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

GREEN_TRIPS_SOURCE_DDL = """
    CREATE TABLE green_trips (
        lpep_pickup_datetime VARCHAR,
        lpep_dropoff_datetime VARCHAR,
        PULocationID INT,
        DOLocationID INT,
        passenger_count INT,
        trip_distance DOUBLE,
        tip_amount DOUBLE,
        total_amount DOUBLE,
        event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd''T''HH:mm:ss'),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'properties.bootstrap.servers' = 'redpanda:29092',
        'topic' = 'green-trips',
        'scan.startup.mode' = 'earliest-offset',
        'properties.auto.offset.reset' = 'earliest',
        'format' = 'json'
    );
"""

JDBC_OPTIONS = {
    "connector": "jdbc",
    "url": "jdbc:postgresql://postgres:5432/postgres",
    "username": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver",
}


def build_env(parallelism: int = 1):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)
    env.set_parallelism(parallelism)
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)
    return env, t_env


def create_green_trips_source(t_env) -> str:
    t_env.execute_sql(GREEN_TRIPS_SOURCE_DDL)
    return "green_trips"


def create_jdbc_sink(t_env, pg_table: str, columns_ddl: str) -> str:
    flink_table = f"{pg_table}_sink"
    jdbc_with = "\n".join(
        f"    '{k}' = '{v}'," for k, v in JDBC_OPTIONS.items()
    ).rstrip(",")
    ddl = f"""
        CREATE TABLE {flink_table} (
            {columns_ddl}
        ) WITH (
            {jdbc_with},
            'table-name' = '{pg_table}'
        );
    """
    t_env.execute_sql(ddl)
    return flink_table
