from common import build_env, create_green_trips_source, create_jdbc_sink

COLUMNS_DDL = """
    window_start TIMESTAMP(3),
    pulocationid INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, pulocationid) NOT ENFORCED
"""

QUERY = """
    SELECT
        window_start,
        PULocationID,
        COUNT(*) AS num_trips
    FROM TABLE(
        TUMBLE(TABLE green_trips, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTE)
    )
    GROUP BY window_start, PULocationID
"""


def run():
    _, t_env = build_env(parallelism=1)
    create_green_trips_source(t_env)
    sink = create_jdbc_sink(t_env, "pu_trips_5min", COLUMNS_DDL)
    t_env.execute_sql(f"INSERT INTO {sink} {QUERY}").wait()


if __name__ == '__main__':
    run()
