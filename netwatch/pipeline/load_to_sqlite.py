"""
Load source telemetry into the local bronze table.
"""

import sqlite3

import pandas as pd

from netwatch.config import (
    BRONZE_RAW_READINGS_TABLE,
    LEGACY_RAW_READINGS_TABLE,
    NETWATCH_DATABASE_FILE,
    RAW_READINGS_FILE,
)

def main():
    raw_readings_dataframe = pd.read_csv(RAW_READINGS_FILE)

    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe.to_sql(
            BRONZE_RAW_READINGS_TABLE,
            database_connection,
            if_exists="replace",
            index=False,
        )
        raw_readings_dataframe.to_sql(
            LEGACY_RAW_READINGS_TABLE,
            database_connection,
            if_exists="replace",
            index=False,
        )

        loaded_row_count = database_connection.execute(
            f"SELECT COUNT(*) FROM {BRONZE_RAW_READINGS_TABLE}"
        ).fetchone()[0]

    print(f"Loaded {loaded_row_count} rows into {NETWATCH_DATABASE_FILE}")
    print(f"Bronze table created: {BRONZE_RAW_READINGS_TABLE}")
    print(f"Compatibility table refreshed: {LEGACY_RAW_READINGS_TABLE}")


if __name__ == "__main__":
    main()
