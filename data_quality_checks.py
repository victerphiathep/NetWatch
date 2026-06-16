"""
Run data quality checks against the raw NetWatch telemetry table.
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).parent
NETWATCH_DATABASE_FILE = PROJECT_ROOT / "data" / "netwatch.db"
EXPECTED_READINGS_PER_NODE = 7 * 24


def collect_failure_messages(quality_check_definitions):
    return [
        quality_check["message"]
        for quality_check in quality_check_definitions
        if quality_check["failed"]
    ]


def print_quality_report(quality_check_results):
    print("Data quality report")
    print("-------------------")

    print("\nMissing values by column:")
    print(quality_check_results["missing_values_by_column"])

    print("\nDuplicate node/timestamp readings:")
    print(quality_check_results["duplicate_node_timestamp_count"])

    print("\nInvalid download utilization rows:")
    print(quality_check_results["invalid_download_reading_count"])

    print("\nInvalid upload utilization rows:")
    print(quality_check_results["invalid_upload_reading_count"])

    print("\nReadings per node:")
    print(quality_check_results["readings_per_node_dataframe"])

    print("\nNodes with unexpected reading counts:")
    print(quality_check_results["incomplete_nodes_dataframe"])


def run_quality_checks(raw_readings_dataframe):
    missing_values_by_column = raw_readings_dataframe.isna().sum()

    duplicate_node_timestamp_count = raw_readings_dataframe.duplicated(
        subset=["node_id", "timestamp"]
    ).sum()

    invalid_download_readings = raw_readings_dataframe[
        (raw_readings_dataframe["download_utilization_pct"] < 0)
        | (raw_readings_dataframe["download_utilization_pct"] > 100)
    ]

    invalid_upload_readings = raw_readings_dataframe[
        (raw_readings_dataframe["upload_utilization_pct"] < 0)
        | (raw_readings_dataframe["upload_utilization_pct"] > 100)
    ]

    readings_per_node_dataframe = (
        raw_readings_dataframe.groupby("node_id")
        .size()
        .reset_index(name="reading_count")
    )

    incomplete_nodes_dataframe = readings_per_node_dataframe[
        readings_per_node_dataframe["reading_count"] != EXPECTED_READINGS_PER_NODE
    ]

    quality_check_results = {
        "missing_values_by_column": missing_values_by_column,
        "duplicate_node_timestamp_count": duplicate_node_timestamp_count,
        "invalid_download_reading_count": len(invalid_download_readings),
        "invalid_upload_reading_count": len(invalid_upload_readings),
        "readings_per_node_dataframe": readings_per_node_dataframe,
        "incomplete_nodes_dataframe": incomplete_nodes_dataframe,
    }

    quality_check_definitions = [
        {
            "name": "missing_values",
            "failed": missing_values_by_column.sum() > 0,
            "message": "Dataset contains missing values",
        },
        {
            "name": "duplicate_node_timestamps",
            "failed": duplicate_node_timestamp_count > 0,
            "message": "Dataset contains duplicate node/timestamp readings",
        },
        {
            "name": "invalid_download_utilization",
            "failed": len(invalid_download_readings) > 0,
            "message": "Dataset contains invalid download utilization values",
        },
        {
            "name": "invalid_upload_utilization",
            "failed": len(invalid_upload_readings) > 0,
            "message": "Dataset contains invalid upload utilization values",
        },
        {
            "name": "unexpected_reading_counts",
            "failed": len(incomplete_nodes_dataframe) > 0,
            "message": "Some nodes have unexpected reading counts",
        },
    ]

    return quality_check_results, quality_check_definitions


def main():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            database_connection,
        )

    quality_check_results, quality_check_definitions = run_quality_checks(
        raw_readings_dataframe
    )
    failure_messages = collect_failure_messages(quality_check_definitions)

    print_quality_report(quality_check_results)

    if failure_messages:
        print("\nData quality status: FAILED")
        for failure_message in failure_messages:
            print(f"- {failure_message}")
        raise SystemExit(1)

    print("\nData quality status: PASSED")


if __name__ == "__main__":
    main()
