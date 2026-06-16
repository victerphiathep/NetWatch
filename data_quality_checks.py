"""
Run data quality checks against the raw NetWatch telemetry table.
"""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).parent
DB_FILE = PROJECT_ROOT / "data" / "netwatch.db"
EXPECTED_READINGS_PER_NODE = 7 * 24


def collect_failures(checks):
    return [check["message"] for check in checks if check["failed"]]


def print_quality_report(results):
    print("Data quality report")
    print("-------------------")

    print("\nMissing values by column:")
    print(results["missing_values"])

    print("\nDuplicate node/timestamp readings:")
    print(results["duplicate_count"])

    print("\nInvalid download utilization rows:")
    print(results["invalid_download_count"])

    print("\nInvalid upload utilization rows:")
    print(results["invalid_upload_count"])

    print("\nReadings per node:")
    print(results["readings_per_node"])

    print("\nNodes with unexpected reading counts:")
    print(results["incomplete_nodes"])


def run_quality_checks(df):
    missing_values = df.isna().sum()

    duplicate_count = df.duplicated(
        subset=["node_id", "timestamp"]
    ).sum()

    invalid_download = df[
        (df["download_utilization_pct"] < 0)
        | (df["download_utilization_pct"] > 100)
    ]

    invalid_upload = df[
        (df["upload_utilization_pct"] < 0)
        | (df["upload_utilization_pct"] > 100)
    ]

    readings_per_node = (
        df.groupby("node_id")
        .size()
        .reset_index(name="reading_count")
    )

    incomplete_nodes = readings_per_node[
        readings_per_node["reading_count"] != EXPECTED_READINGS_PER_NODE
    ]

    results = {
        "missing_values": missing_values,
        "duplicate_count": duplicate_count,
        "invalid_download_count": len(invalid_download),
        "invalid_upload_count": len(invalid_upload),
        "readings_per_node": readings_per_node,
        "incomplete_nodes": incomplete_nodes,
    }

    checks = [
        {
            "name": "missing_values",
            "failed": missing_values.sum() > 0,
            "message": "Dataset contains missing values",
        },
        {
            "name": "duplicate_node_timestamps",
            "failed": duplicate_count > 0,
            "message": "Dataset contains duplicate node/timestamp readings",
        },
        {
            "name": "invalid_download_utilization",
            "failed": len(invalid_download) > 0,
            "message": "Dataset contains invalid download utilization values",
        },
        {
            "name": "invalid_upload_utilization",
            "failed": len(invalid_upload) > 0,
            "message": "Dataset contains invalid upload utilization values",
        },
        {
            "name": "unexpected_reading_counts",
            "failed": len(incomplete_nodes) > 0,
            "message": "Some nodes have unexpected reading counts",
        },
    ]

    return results, checks


def main():
    with sqlite3.connect(DB_FILE) as connection:
        df = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            connection,
        )

    results, checks = run_quality_checks(df)
    failures = collect_failures(checks)

    print_quality_report(results)

    if failures:
        print("\nData quality status: FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nData quality status: PASSED")


if __name__ == "__main__":
    main()
