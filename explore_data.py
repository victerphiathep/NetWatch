"""
Exploring data and getting a feel for it before we do any transformations or build any models.
"""


from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).parent
DATA_FILE = PROJECT_ROOT / "data" / "mock_node_readings.csv"


def main():
    raw_readings_dataframe = pd.read_csv(DATA_FILE)

    print("First 5 rows:")
    print(raw_readings_dataframe.head())

    print("\nRows and columns:")
    print(raw_readings_dataframe.shape)

    print("\nColumn names:")
    print(raw_readings_dataframe.columns)

    print("\nDataFrame info:")
    raw_readings_dataframe.info()

    print("\nSummary statistics:")
    print(raw_readings_dataframe.describe())

    print("___NEW EXAMPLE___")

    print("\nSelected columns:")
    print(
        raw_readings_dataframe[
            ["timestamp", "node_id", "region", "download_utilization_pct"]
        ].head()
    )

    critical_readings_dataframe = raw_readings_dataframe[
        raw_readings_dataframe["download_utilization_pct"] >= 85
    ]

    print("\nCritical readings:")
    print(critical_readings_dataframe.head())

    print("\nCritical reading count:")
    print(len(critical_readings_dataframe))
    print("\nCritical readings by node:")
    print(get_critical_reading_counts_by_node(critical_readings_dataframe))


def get_critical_reading_counts_by_node(critical_readings_dataframe):
    critical_counts_by_node = (
        critical_readings_dataframe
        .groupby("node_id")
        .size()
        .sort_values(ascending=False)
    )
    return critical_counts_by_node


if __name__ == "__main__":
    main()
