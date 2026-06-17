"""
connect to SQLite database and run queries
"""

import sqlite3

from netwatch.config import NETWATCH_DATABASE_FILE

def print_query_results(database_connection, sql_query):
    query_rows = database_connection.execute(sql_query).fetchall()

    for query_row in query_rows:
        print(query_row)

def main():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        print("Total raw readings:")
        print_query_results(
            database_connection,
            """
            SELECT COUNT(*)
            FROM raw_node_readings;
            """,
        )

        print("\nTop 10 critical readings:")
        print_query_results(
            database_connection,
            """
            SELECT
                timestamp,
                node_id,
                region,
                download_utilization_pct,
                status
            FROM raw_node_readings
            WHERE download_utilization_pct >= 85
            ORDER BY download_utilization_pct DESC
            LIMIT 10;
            """,
        )

        print("\nCritical reading count by node:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                COUNT(*) AS critical_reading_count
            FROM raw_node_readings
            WHERE download_utilization_pct >= 85
            GROUP BY node_id
            ORDER BY critical_reading_count DESC;
            """,
        )

        print("\nHigh-risk node summary:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                region,
                avg_download_utilization,
                max_download_utilization,
                critical_reading_count,
                critical_reading_pct,
                peak_hour_critical_reading_count,
                peak_hour_max_download_utilization,
                download_utilization_change,
                risk_level
            FROM node_summary
            WHERE risk_level = 'high_risk'
            ORDER BY
                critical_reading_count DESC,
                max_download_utilization DESC;
            """,
        )

        print("\nPeak-hour critical reading count by node:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                region,
                peak_hour_critical_reading_count,
                peak_hour_avg_download_utilization,
                peak_hour_max_download_utilization
            FROM node_summary
            ORDER BY
                peak_hour_critical_reading_count DESC,
                peak_hour_max_download_utilization DESC;
            """,
        )

        print("\nLargest download utilization increases:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                region,
                first_day_avg_download_utilization,
                last_day_avg_download_utilization,
                download_utilization_change
            FROM node_summary
            ORDER BY download_utilization_change DESC
            LIMIT 5;
            """,
        )

        print("\nRisk count by region:")
        print_query_results(
            database_connection,
            """
            SELECT
                region,
                risk_level,
                COUNT(*) AS node_count
            FROM node_summary
            GROUP BY region, risk_level
            ORDER BY region, risk_level;
            """,
        )

        print("\nTop anomaly readings:")
        print_query_results(
            database_connection,
            """
            SELECT
                timestamp,
                node_id,
                region,
                download_utilization_pct,
                anomaly_threshold,
                anomaly_score
            FROM anomaly_readings
            ORDER BY anomaly_score DESC
            LIMIT 10;
            """,
        )

if __name__ == "__main__":
    main()
