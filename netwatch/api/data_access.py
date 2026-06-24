import sqlite3

from netwatch.config import NETWATCH_DATABASE_FILE


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
        """
        SELECT *
        FROM raw_node_readings
        ORDER BY timestamp, node_id;
        """
    )


def fetch_node_summaries():
    return fetch_all_rows(
        """
        SELECT *
        FROM node_summary
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


def fetch_node_summary(node_id):
    return fetch_one_row(
        """
        SELECT *
        FROM node_summary
        WHERE node_id = ?;
        """,
        (node_id,),
    )


def fetch_node_readings(node_id, limit):
    return fetch_all_rows(
        """
        SELECT *
        FROM raw_node_readings
        WHERE node_id = ?
        ORDER BY timestamp
        LIMIT ?;
        """,
        (node_id, limit),
    )

def fetch_anomaly_readings():
    return fetch_all_rows(
        """
        SELECT *
        FROM anomaly_readings
        ORDER BY anomaly_score DESC;
        """
    )


def fetch_node_anomalies(node_id):
    return fetch_all_rows(
        """
        SELECT *
        FROM anomaly_readings
        WHERE node_id = ?
        ORDER BY anomaly_score DESC;
        """,
        (node_id,),
    )


def fetch_regions():
    return fetch_all_rows(
        """
        SELECT DISTINCT region
        FROM node_summary
        ORDER BY region;
        """
    )


def fetch_region_risk_summary():
    return fetch_all_rows(
        """
        SELECT
            region,
            risk_level,
            COUNT(*) AS node_count
        FROM node_summary
        GROUP BY region, risk_level
        ORDER BY region, risk_level;
        """
    )
