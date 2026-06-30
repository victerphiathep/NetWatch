import math
import sqlite3

import pandas as pd

from netwatch.config import (
    GOLD_NODE_FORECAST_TABLE,
    NETWATCH_DATABASE_FILE,
    SILVER_VALIDATED_READINGS_TABLE,
)


CRITICAL_UTILIZATION_THRESHOLD = 85
FORECAST_WATCH_WINDOW_DAYS = 30
FORECAST_HIGH_RISK_WINDOW_DAYS = 7


def calculate_days_until_critical(last_day_utilization, daily_utilization_change):
    if last_day_utilization >= CRITICAL_UTILIZATION_THRESHOLD:
        return 0

    if daily_utilization_change <= 0:
        return None

    days_until_critical = (
        CRITICAL_UTILIZATION_THRESHOLD - last_day_utilization
    ) / daily_utilization_change

    return math.ceil(days_until_critical)


def classify_forecast_risk(last_day_utilization, days_until_critical):
    if last_day_utilization >= CRITICAL_UTILIZATION_THRESHOLD:
        return "forecast_high_risk"

    if days_until_critical is None:
        return "forecast_stable"

    if days_until_critical <= FORECAST_HIGH_RISK_WINDOW_DAYS:
        return "forecast_high_risk"

    if days_until_critical <= FORECAST_WATCH_WINDOW_DAYS:
        return "forecast_watch"

    return "forecast_stable"


def build_node_forecast(raw_readings_dataframe):
    raw_readings_dataframe["timestamp"] = pd.to_datetime(
        raw_readings_dataframe["timestamp"]
    )
    raw_readings_dataframe["reading_date"] = raw_readings_dataframe[
        "timestamp"
    ].dt.date

    daily_node_utilization_dataframe = (
        raw_readings_dataframe.groupby(["node_id", "region", "reading_date"])
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
        daily_node_utilization_dataframe.groupby(["node_id", "region"])
        .first()
        .reset_index()
        .rename(
            columns={
                "reading_date": "first_reading_date",
                "daily_avg_download_utilization": "first_day_avg_download_utilization",
            }
        )
    )
    last_day_utilization_dataframe = (
        daily_node_utilization_dataframe.groupby(["node_id", "region"])
        .last()
        .reset_index()
        .rename(
            columns={
                "reading_date": "last_reading_date",
                "daily_avg_download_utilization": "last_day_avg_download_utilization",
            }
        )
    )

    node_forecast_dataframe = first_day_utilization_dataframe.merge(
        last_day_utilization_dataframe,
        on=["node_id", "region"],
        how="inner",
    )

    node_forecast_dataframe["observed_day_count"] = (
        pd.to_datetime(node_forecast_dataframe["last_reading_date"])
        - pd.to_datetime(node_forecast_dataframe["first_reading_date"])
    ).dt.days

    node_forecast_dataframe["daily_download_utilization_change"] = (
        (
            node_forecast_dataframe["last_day_avg_download_utilization"]
            - node_forecast_dataframe["first_day_avg_download_utilization"]
        )
        / node_forecast_dataframe["observed_day_count"].replace(0, 1)
    ).round(2)

    node_forecast_dataframe["projected_7_day_download_utilization"] = (
        node_forecast_dataframe["last_day_avg_download_utilization"]
        + (node_forecast_dataframe["daily_download_utilization_change"] * 7)
    ).clip(upper=100).round(2)

    node_forecast_dataframe["projected_30_day_download_utilization"] = (
        node_forecast_dataframe["last_day_avg_download_utilization"]
        + (node_forecast_dataframe["daily_download_utilization_change"] * 30)
    ).clip(upper=100).round(2)

    node_forecast_dataframe["days_until_critical"] = node_forecast_dataframe.apply(
        lambda node_record: calculate_days_until_critical(
            node_record["last_day_avg_download_utilization"],
            node_record["daily_download_utilization_change"],
        ),
        axis=1,
    )

    node_forecast_dataframe["forecast_risk_level"] = node_forecast_dataframe.apply(
        lambda node_record: classify_forecast_risk(
            node_record["last_day_avg_download_utilization"],
            node_record["days_until_critical"],
        ),
        axis=1,
    )

    return node_forecast_dataframe[
        [
            "node_id",
            "region",
            "first_reading_date",
            "last_reading_date",
            "first_day_avg_download_utilization",
            "last_day_avg_download_utilization",
            "daily_download_utilization_change",
            "projected_7_day_download_utilization",
            "projected_30_day_download_utilization",
            "days_until_critical",
            "forecast_risk_level",
        ]
    ]


def main():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe = pd.read_sql_query(
            f"SELECT * FROM {SILVER_VALIDATED_READINGS_TABLE}",
            database_connection,
        )

        node_forecast_dataframe = build_node_forecast(raw_readings_dataframe)

        node_forecast_dataframe.to_sql(
            GOLD_NODE_FORECAST_TABLE,
            database_connection,
            if_exists="replace",
            index=False,
        )

    print(node_forecast_dataframe)
    print(f"\nGold table created: {GOLD_NODE_FORECAST_TABLE}")


if __name__ == "__main__":
    main()
