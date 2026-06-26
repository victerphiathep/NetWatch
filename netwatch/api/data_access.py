import sqlite3

from netwatch.config import (
    GOLD_NODE_FORECAST_TABLE,
    GOLD_NODE_SUMMARY_TABLE,
    NETWATCH_DATABASE_FILE,
    SILVER_ANOMALY_READINGS_TABLE,
    SILVER_VALIDATED_READINGS_TABLE,
)


def fetch_all_rows(sql_query, query_parameters=()):
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        database_connection.row_factory = sqlite3.Row
        query_rows = database_connection.execute(
            sql_query,
            query_parameters,
        ).fetchall()

    return [dict(query_row) for query_row in query_rows]


def fetch_one_row(sql_query, query_parameters=()):
    rows = fetch_all_rows(sql_query, query_parameters)

    if not rows:
        return None

    return rows[0]


def fetch_raw_readings():
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {SILVER_VALIDATED_READINGS_TABLE}
        ORDER BY timestamp, node_id;
        """
    )


def fetch_node_summaries():
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {GOLD_NODE_SUMMARY_TABLE}
        ORDER BY
            CASE risk_level
                WHEN 'high_risk' THEN 0
                WHEN 'watch' THEN 1
                ELSE 2
            END,
            critical_reading_count DESC,
            max_download_utilization DESC;
        """
    )


def fetch_node_forecasts():
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {GOLD_NODE_FORECAST_TABLE}
        ORDER BY
            CASE forecast_risk_level
                WHEN 'forecast_high_risk' THEN 0
                WHEN 'forecast_watch' THEN 1
                ELSE 2
            END,
            days_until_critical IS NULL,
            days_until_critical,
            projected_30_day_download_utilization DESC;
        """
    )


def fetch_node_forecast(node_id):
    return fetch_one_row(
        f"""
        SELECT *
        FROM {GOLD_NODE_FORECAST_TABLE}
        WHERE node_id = ?;
        """,
        (node_id,),
    )


def fetch_node_summary(node_id):
    return fetch_one_row(
        f"""
        SELECT *
        FROM {GOLD_NODE_SUMMARY_TABLE}
        WHERE node_id = ?;
        """,
        (node_id,),
    )


def fetch_node_readings(node_id, limit):
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {SILVER_VALIDATED_READINGS_TABLE}
        WHERE node_id = ?
        ORDER BY timestamp
        LIMIT ?;
        """,
        (node_id, limit),
    )

def fetch_anomaly_readings():
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {SILVER_ANOMALY_READINGS_TABLE}
        ORDER BY anomaly_score DESC;
        """
    )


def fetch_node_anomalies(node_id):
    return fetch_all_rows(
        f"""
        SELECT *
        FROM {SILVER_ANOMALY_READINGS_TABLE}
        WHERE node_id = ?
        ORDER BY anomaly_score DESC;
        """,
        (node_id,),
    )


def fetch_regions():
    return fetch_all_rows(
        f"""
        SELECT DISTINCT region
        FROM {GOLD_NODE_SUMMARY_TABLE}
        ORDER BY region;
        """
    )


def fetch_region_risk_summary():
    return fetch_all_rows(
        f"""
        SELECT
            region,
            risk_level,
            COUNT(*) AS node_count
        FROM {GOLD_NODE_SUMMARY_TABLE}
        GROUP BY region, risk_level
        ORDER BY region, risk_level;
        """
    )
