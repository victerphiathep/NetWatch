"""
connect to SQLite database and run queries
"""

from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).parent
DB_FILE = PROJECT_ROOT / "data" / "netwatch.db"

def run_query(connection, query):
    rows = connection.execute(query).fetchall()

    for row in rows:
        print(row)

def main():
    with sqlite3.connect(DB_FILE) as connection:
        print("Total raw readings:")
        run_query(
            connection,
            """
            SELECT COUNT(*)
            FROM raw_node_readings;
            """,
        )

        print("\nTop 10 critical readings:")
        run_query(
            connection,
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
        run_query(
            connection,
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
        run_query(
            connection,
            """
            SELECT
                node_id,
                region,
                avg_download_utilization,
                max_download_utilization,
                critical_reading_count,
                critical_reading_pct,
                risk_level
            FROM node_summary
            WHERE risk_level = 'high_risk'
            ORDER BY
                critical_reading_count DESC,
                max_download_utilization DESC;
            """,
        )

        print("\nRisk count by region:")
        run_query(
            connection,
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

if __name__ == "__main__":
    main()
