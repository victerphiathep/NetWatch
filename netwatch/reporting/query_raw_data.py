"""
connect to SQLite database and run queries
"""

import sqlite3

from netwatch.config import (
    BRONZE_RAW_READINGS_TABLE,
    GOLD_NODE_FORECAST_TABLE,
    GOLD_NODE_SUMMARY_TABLE,
    NETWATCH_DATABASE_FILE,
    SILVER_ANOMALY_READINGS_TABLE,
)

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
            FROM {table_name};
            """.format(table_name=BRONZE_RAW_READINGS_TABLE),
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
            FROM {table_name}
            WHERE download_utilization_pct >= 85
            ORDER BY download_utilization_pct DESC
            LIMIT 10;
            """.format(table_name=BRONZE_RAW_READINGS_TABLE),
        )

        print("\nCritical reading count by node:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                COUNT(*) AS critical_reading_count
            FROM {table_name}
            WHERE download_utilization_pct >= 85
            GROUP BY node_id
            ORDER BY critical_reading_count DESC;
            """.format(table_name=BRONZE_RAW_READINGS_TABLE),
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
            FROM {table_name}
            WHERE risk_level = 'high_risk'
            ORDER BY
                critical_reading_count DESC,
                max_download_utilization DESC;
            """.format(table_name=GOLD_NODE_SUMMARY_TABLE),
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
            FROM {table_name}
            ORDER BY
                peak_hour_critical_reading_count DESC,
                peak_hour_max_download_utilization DESC;
            """.format(table_name=GOLD_NODE_SUMMARY_TABLE),
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
            FROM {table_name}
            ORDER BY download_utilization_change DESC
            LIMIT 5;
            """.format(table_name=GOLD_NODE_SUMMARY_TABLE),
        )

        print("\nRisk count by region:")
        print_query_results(
            database_connection,
            """
            SELECT
                region,
                risk_level,
                COUNT(*) AS node_count
            FROM {table_name}
            GROUP BY region, risk_level
            ORDER BY region, risk_level;
            """.format(table_name=GOLD_NODE_SUMMARY_TABLE),
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
            FROM {table_name}
            ORDER BY anomaly_score DESC
            LIMIT 10;
            """.format(table_name=SILVER_ANOMALY_READINGS_TABLE),
        )

        print("\nHighest forecasted capacity risk:")
        print_query_results(
            database_connection,
            """
            SELECT
                node_id,
                region,
                last_day_avg_download_utilization,
                daily_download_utilization_change,
                projected_30_day_download_utilization,
                days_until_critical,
                forecast_risk_level
            FROM {table_name}
            ORDER BY
                CASE forecast_risk_level
                    WHEN 'forecast_high_risk' THEN 0
                    WHEN 'forecast_watch' THEN 1
                    ELSE 2
                END,
                days_until_critical IS NULL,
                days_until_critical,
                projected_30_day_download_utilization DESC;
            """.format(table_name=GOLD_NODE_FORECAST_TABLE),
        )

if __name__ == "__main__":
    main()
