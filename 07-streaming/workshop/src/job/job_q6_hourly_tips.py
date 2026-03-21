from common import build_env, create_green_trips_source, create_jdbc_sink

COLUMNS_DDL = """
    window_start TIMESTAMP(3),
    total_tip DOUBLE,
    PRIMARY KEY (window_start) NOT ENFORCED
"""

QUERY = """
    SELECT
        window_start,
        SUM(tip_amount) AS total_tip
    FROM TABLE(
        TUMBLE(TABLE green_trips, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
    )
    GROUP BY window_start
"""


def run():
    _, t_env = build_env(parallelism=1)
    create_green_trips_source(t_env)
    sink = create_jdbc_sink(t_env, "hourly_tips", COLUMNS_DDL)
    t_env.execute_sql(f"INSERT INTO {sink} {QUERY}").wait()


if __name__ == '__main__':
    run()
