from common import build_env, create_green_trips_source, create_jdbc_sink

COLUMNS_DDL = """
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    pulocationid INT,
    num_trips BIGINT,
    PRIMARY KEY (window_start, window_end, pulocationid) NOT ENFORCED
"""

QUERY = """
    SELECT
        window_start,
        window_end,
        PULocationID,
        COUNT(*) AS num_trips
    FROM TABLE(
        SESSION(TABLE green_trips PARTITION BY PULocationID, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTE)
    )
    GROUP BY window_start, window_end, PULocationID
"""


def run():
    _, t_env = build_env(parallelism=1)
    create_green_trips_source(t_env)
    sink = create_jdbc_sink(t_env, "pu_session_trips", COLUMNS_DDL)
    t_env.execute_sql(f"INSERT INTO {sink} {QUERY}").wait()


if __name__ == '__main__':
    run()
