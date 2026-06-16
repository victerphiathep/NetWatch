"""
Node summary aggregation

node_id
region
avg_download_utilization
max_download_utilization
avg_upload_utilization
max_upload_utilization
critical_reading_count
total_reading_count
critical_reading_pct

Risk Mental Model:

high_risk:
    critical_reading_count >= 5
    OR max_download_utilization >= 90

watch:
    critical_reading_count >= 2
    OR avg_download_utilization >= 65

normal:
    everything else
"""

from pathlib import Path
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).parent
SUMMARY_FILE = PROJECT_ROOT / "data" / "node_summary.csv"
DB_FILE = PROJECT_ROOT / "data" / "netwatch.db"

RISK_SORT_ORDER = {
    "high_risk": 0,
    "watch": 1,
    "normal": 2,
}

def classify_node_risk(row):
    if row["critical_reading_count"] >= 5 or row["max_download_utilization"] >= 90:
        return "high_risk"

    if row["critical_reading_count"] >= 2 or row["avg_download_utilization"] >= 65:
        return "watch"

    return "normal"

def main():
    with sqlite3.connect(DB_FILE) as connection:
        df = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            connection,
        )

    node_summary = (
        df.groupby(["node_id", "region"])
        .agg(
            avg_download_utilization=("download_utilization_pct", "mean"),
            max_download_utilization=("download_utilization_pct", "max"),
            avg_upload_utilization=("upload_utilization_pct", "mean"),
            max_upload_utilization=("upload_utilization_pct", "max"),
            total_reading_count=("node_id", "size"),
        )
        .reset_index()
    )

    critical_counts = (
        df[df["download_utilization_pct"] >= 85]
        .groupby("node_id")
        .size()
        .reset_index(name="critical_reading_count")
    )

    node_summary = node_summary.merge(
        critical_counts,
        on="node_id",
        how="left",
    )

    node_summary["critical_reading_count"] = (
        node_summary["critical_reading_count"]
        .fillna(0)
        .astype(int)
    )

    node_summary["critical_reading_pct"] = (
        node_summary["critical_reading_count"]
        / node_summary["total_reading_count"]
        * 100
    ).round(2)

    node_summary["risk_level"] = node_summary.apply(classify_node_risk, axis=1)
    node_summary["risk_sort_order"] = node_summary["risk_level"].map(RISK_SORT_ORDER)

    node_summary = node_summary.sort_values(
        by=["risk_sort_order", "critical_reading_count", "max_download_utilization"],
        ascending=[True, False, False],
    ).drop(columns=["risk_sort_order"])

    with sqlite3.connect(DB_FILE) as connection:
        node_summary.to_sql(
            "node_summary",
            connection,
            if_exists="replace",
            index=False,
        )

    node_summary.to_csv(SUMMARY_FILE, index=False)

    print(node_summary)
    print(f"\nSaved node summary to {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
