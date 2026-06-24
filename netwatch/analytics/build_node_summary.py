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
peak_hour_avg_download_utilization
peak_hour_max_download_utilization
peak_hour_critical_reading_count
first_day_avg_download_utilization
last_day_avg_download_utilization
download_utilization_change

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

import sqlite3

import pandas as pd

from netwatch.config import NETWATCH_DATABASE_FILE, NODE_SUMMARY_FILE

RISK_LEVEL_SORT_ORDER = {
    "high_risk": 0,
    "watch": 1,
    "normal": 2,
}

PEAK_HOUR_START = 18
PEAK_HOUR_END = 22

def classify_node_risk(node_summary_record):
    if (
        node_summary_record["critical_reading_count"] >= 5
        or node_summary_record["max_download_utilization"] >= 90
    ):
        return "high_risk"

    if (
        node_summary_record["critical_reading_count"] >= 2
        or node_summary_record["avg_download_utilization"] >= 65
    ):
        return "watch"

    return "normal"

def main():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            database_connection,
        )

    raw_readings_dataframe["timestamp"] = pd.to_datetime(
        raw_readings_dataframe["timestamp"]
    )
    raw_readings_dataframe["reading_date"] = raw_readings_dataframe[
        "timestamp"
    ].dt.date
    raw_readings_dataframe["hour"] = raw_readings_dataframe["timestamp"].dt.hour
    raw_readings_dataframe["is_peak_hour"] = raw_readings_dataframe["hour"].between(
        PEAK_HOUR_START,
        PEAK_HOUR_END,
    )

    node_summary_dataframe = (
        raw_readings_dataframe.groupby(["node_id", "region"])
        .agg(
            avg_download_utilization=("download_utilization_pct", "mean"),
            max_download_utilization=("download_utilization_pct", "max"),
            avg_upload_utilization=("upload_utilization_pct", "mean"),
            max_upload_utilization=("upload_utilization_pct", "max"),
            total_reading_count=("node_id", "size"),
        )
        .reset_index()
    )

    critical_reading_counts_by_node = (
        raw_readings_dataframe[
            raw_readings_dataframe["download_utilization_pct"] >= 85
        ]
        .groupby("node_id")
        .size()
        .reset_index(name="critical_reading_count")
    )

    node_summary_dataframe = node_summary_dataframe.merge(
        critical_reading_counts_by_node,
        on="node_id",
        how="left",
    )

    peak_hour_readings_dataframe = raw_readings_dataframe[
        raw_readings_dataframe["is_peak_hour"]
    ]
    peak_hour_summary_dataframe = (
        peak_hour_readings_dataframe.groupby("node_id")
        .agg(
            peak_hour_avg_download_utilization=(
                "download_utilization_pct",
                "mean",
            ),
            peak_hour_max_download_utilization=(
                "download_utilization_pct",
                "max",
            ),
            peak_hour_total_reading_count=("node_id", "size"),
        )
        .reset_index()
    )
    peak_hour_critical_counts_by_node = (
        peak_hour_readings_dataframe[
            peak_hour_readings_dataframe["download_utilization_pct"] >= 85
        ]
        .groupby("node_id")
        .size()
        .reset_index(name="peak_hour_critical_reading_count")
    )

    node_summary_dataframe = node_summary_dataframe.merge(
        peak_hour_summary_dataframe,
        on="node_id",
        how="left",
    )
    node_summary_dataframe = node_summary_dataframe.merge(
        peak_hour_critical_counts_by_node,
        on="node_id",
        how="left",
    )

    daily_node_utilization_dataframe = (
        raw_readings_dataframe.groupby(["node_id", "reading_date"])
        .agg(
            daily_avg_download_utilization=(
                "download_utilization_pct",
                "mean",
            )
        )
        .reset_index()
        .sort_values(by=["node_id", "reading_date"])
    )
    first_day_utilization_dataframe = (
        daily_node_utilization_dataframe.groupby("node_id")
        .first()
        .reset_index()[["node_id", "daily_avg_download_utilization"]]
        .rename(
            columns={
                "daily_avg_download_utilization": "first_day_avg_download_utilization"
            }
        )
    )
    last_day_utilization_dataframe = (
        daily_node_utilization_dataframe.groupby("node_id")
        .last()
        .reset_index()[["node_id", "daily_avg_download_utilization"]]
        .rename(
            columns={
                "daily_avg_download_utilization": "last_day_avg_download_utilization"
            }
        )
    )

    node_summary_dataframe = node_summary_dataframe.merge(
        first_day_utilization_dataframe,
        on="node_id",
        how="left",
    )
    node_summary_dataframe = node_summary_dataframe.merge(
        last_day_utilization_dataframe,
        on="node_id",
        how="left",
    )

    node_summary_dataframe["critical_reading_count"] = (
        node_summary_dataframe["critical_reading_count"]
        .fillna(0)
        .astype(int)
    )
    node_summary_dataframe["peak_hour_critical_reading_count"] = (
        node_summary_dataframe["peak_hour_critical_reading_count"]
        .fillna(0)
        .astype(int)
    )

    node_summary_dataframe["critical_reading_pct"] = (
        node_summary_dataframe["critical_reading_count"]
        / node_summary_dataframe["total_reading_count"]
        * 100
    ).round(2)
    node_summary_dataframe["download_utilization_change"] = (
        node_summary_dataframe["last_day_avg_download_utilization"]
        - node_summary_dataframe["first_day_avg_download_utilization"]
    ).round(2)

    node_summary_dataframe["risk_level"] = node_summary_dataframe.apply(
        classify_node_risk,
        axis=1,
    )
    node_summary_dataframe["risk_sort_order"] = node_summary_dataframe[
        "risk_level"
    ].map(RISK_LEVEL_SORT_ORDER)

    node_summary_dataframe = node_summary_dataframe.sort_values(
        by=["risk_sort_order", "critical_reading_count", "max_download_utilization"],
        ascending=[True, False, False],
    ).drop(columns=["risk_sort_order"])

    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        node_summary_dataframe.to_sql(
            "node_summary",
            database_connection,
            if_exists="replace",
            index=False,
        )

    node_summary_dataframe.to_csv(NODE_SUMMARY_FILE, index=False)

    print(node_summary_dataframe)
    print(f"\nSaved node summary to {NODE_SUMMARY_FILE}")


if __name__ == "__main__":
    main()
