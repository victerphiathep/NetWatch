import sqlite3

import pandas as pd

from netwatch.config import NETWATCH_DATABASE_FILE


ANOMALY_STD_DEV_MULTIPLIER = 2


def detect_download_utilization_anomalies(raw_readings_dataframe):
    node_baseline_dataframe = (
        raw_readings_dataframe.groupby("node_id")
        .agg(
            node_avg_download_utilization=("download_utilization_pct", "mean"),
            node_std_download_utilization=("download_utilization_pct", "std"),
        )
        .reset_index()
    )

    readings_with_baseline_dataframe = raw_readings_dataframe.merge(
        node_baseline_dataframe,
        on="node_id",
        how="left",
    )

    readings_with_baseline_dataframe["anomaly_threshold"] = (
        readings_with_baseline_dataframe["node_avg_download_utilization"]
        + (
            ANOMALY_STD_DEV_MULTIPLIER
            * readings_with_baseline_dataframe["node_std_download_utilization"]
        )
    )

    anomaly_readings_dataframe = readings_with_baseline_dataframe[
        readings_with_baseline_dataframe["download_utilization_pct"]
        > readings_with_baseline_dataframe["anomaly_threshold"]
    ].copy()

    anomaly_readings_dataframe["anomaly_score"] = (
        (
            anomaly_readings_dataframe["download_utilization_pct"]
            - anomaly_readings_dataframe["node_avg_download_utilization"]
        )
        / anomaly_readings_dataframe["node_std_download_utilization"]
    ).round(2)

    return anomaly_readings_dataframe[
        [
            "timestamp",
            "node_id",
            "region",
            "download_utilization_pct",
            "node_avg_download_utilization",
            "node_std_download_utilization",
            "anomaly_threshold",
            "anomaly_score",
        ]
    ]


def main():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            database_connection,
        )

        anomaly_readings_dataframe = detect_download_utilization_anomalies(
            raw_readings_dataframe
        )

        anomaly_readings_dataframe.to_sql(
            "anomaly_readings",
            database_connection,
            if_exists="replace",
            index=False,
        )

    print(f"Detected {len(anomaly_readings_dataframe)} anomaly readings")
    print("Table created: anomaly_readings")
    print(anomaly_readings_dataframe.head())


if __name__ == "__main__":
    main()
