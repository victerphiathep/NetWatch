from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


DATA_DIR = Path("data")
RAW_READINGS_FILE = DATA_DIR / "mock_node_readings.csv"

REGION_NODE_IDS = {
    "Philadelphia": ["PHL-001", "PHL-002", "PHL-003", "PHL-004"],
    "New York": ["NYC-001", "NYC-002", "NYC-003"],
    "Chicago": ["CHI-001", "CHI-002", "CHI-003"],
}


def classify_reading_status(download_utilization_pct):
    if download_utilization_pct >= 85:
        return "critical"
    if download_utilization_pct >= 70:
        return "warning"
    return "normal"


def calculate_peak_hour_utilization_boost(hour):
    if 18 <= hour <= 22:
        return 25
    if 12 <= hour <= 17:
        return 12
    if 6 <= hour <= 11:
        return 8
    return 0


def generate_mock_node_readings():
    random.seed(42)

    start_time = datetime(2026, 6, 1, 0, 0)
    days_to_generate = 7
    generated_reading_records = []

    for hour_offset in range(days_to_generate * 24):
        timestamp = start_time + timedelta(hours=hour_offset)

        for region, node_ids in REGION_NODE_IDS.items():
            for node_id in node_ids:
                base_utilization = random.uniform(25, 65)
                hourly_utilization_boost = calculate_peak_hour_utilization_boost(
                    timestamp.hour
                )
                utilization_noise = random.uniform(-5, 5)

                download_utilization_pct = round(
                    min(
                        base_utilization
                        + hourly_utilization_boost
                        + utilization_noise,
                        100,
                    ),
                    2,
                )
                upload_utilization_pct = round(
                    min(download_utilization_pct * random.uniform(0.35, 0.65), 100),
                    2,
                )

                generated_reading_records.append(
                    {
                        "timestamp": timestamp,
                        "node_id": node_id,
                        "region": region,
                        "download_utilization_pct": download_utilization_pct,
                        "upload_utilization_pct": upload_utilization_pct,
                        "capacity_mbps": 1000,
                        "status": classify_reading_status(download_utilization_pct),
                    }
                )

    return pd.DataFrame(generated_reading_records)


def main():
    DATA_DIR.mkdir(exist_ok=True)

    raw_readings_dataframe = generate_mock_node_readings()
    raw_readings_dataframe.to_csv(RAW_READINGS_FILE, index=False)

    print(f"Generated {len(raw_readings_dataframe)} rows")
    print(f"Saved mock readings to {RAW_READINGS_FILE}")
    print(raw_readings_dataframe.head())


if __name__ == "__main__":
    main()
