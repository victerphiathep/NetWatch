"""
read mock_node_readings.csv
connect to SQLite
load the DataFrame into a table called raw_node_readings
print a row count
"""

import sqlite3

import pandas as pd

from netwatch.config import NETWATCH_DATABASE_FILE, RAW_READINGS_FILE

def main():
    raw_readings_dataframe = pd.read_csv(RAW_READINGS_FILE)

    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe.to_sql(
            "raw_node_readings",
            database_connection,
            if_exists="replace",
            index=False,
        )

        loaded_row_count = database_connection.execute(
            "SELECT COUNT(*) FROM raw_node_readings"
        ).fetchone()[0]

    print(f"Loaded {loaded_row_count} rows into {NETWATCH_DATABASE_FILE}")
    print("Table created: raw_node_readings")


if __name__ == "__main__":
    main()
