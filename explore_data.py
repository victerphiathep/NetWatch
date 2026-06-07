from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).parent
DATA_FILE = PROJECT_ROOT / "data" / "mock_node_readings.csv"


def main():
    df = pd.read_csv(DATA_FILE)

    print("First 5 rows:")
    print(df.head())

    print("\nRows and columns:")
    print(df.shape)

    print("\nColumn names:")
    print(df.columns)

    print("\nDataFrame info:")
    df.info()

    print("\nSummary statistics:")
    print(df.describe())

    print("___NEW EXAMPLE___")

    print("\nSelected columns:")
    print(df[["timestamp", "node_id", "region", "download_utilization_pct"]].head())

    critical_readings = df[df["download_utilization_pct"] >= 85]

    print("\nCritical readings:")
    print(critical_readings.head())

    print("\nCritical reading count:")
    print(len(critical_readings))
    print("\nCritical readings by node:")
    print(get_crit_counts_by_node(critical_readings))


def get_crit_counts_by_node(critical_readings):
    critical_counts_by_node = (
        critical_readings
        .groupby("node_id")
        .size()
        .sort_values(ascending=False)
    )
    return critical_counts_by_node


if __name__ == "__main__":
    main()
