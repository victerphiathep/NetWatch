"""
read mock_node_readings.csv
connect to SQLite
load the DataFrame into a table called raw_node_readings
print a row count
"""

from pathlib import Path
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).parent
DATA_FILE = PROJECT_ROOT / "data" / "mock_node_readings.csv"
DB_FILE = PROJECT_ROOT / "data" / "netwatch.db"

def main():
    df = pd.read_csv(DATA_FILE)

    with sqlite3.connect(DB_FILE) as connection:
        df.to_sql(
            "raw_node_readings",
            connection,
            if_exists="replace",
            index=False,
        )

        row_count = connection.execute(
            "SELECT COUNT(*) FROM raw_node_readings"
        ).fetchone()[0]

    print(f"Loaded {row_count} rows into {DB_FILE}")
    print("Table created: raw_node_readings")


if __name__ == "__main__":
    main()