from datetime import datetime, timedelta
import random

import pandas as pd

from netwatch.config import DATA_DIR, RAW_READINGS_FILE

REGION_NODE_IDS = {
    "Philadelphia": ["PHL-001", "PHL-002", "PHL-003", "PHL-004"],
    "New York": ["NYC-001", "NYC-002", "NYC-003"],
    "Chicago": ["CHI-001", "CHI-002", "CHI-003"],
}

NODE_UTILIZATION_PROFILES = {
    "PHL-001": {
        "starting_utilization": 48,
        "daily_utilization_growth": 0.2,
        "noise_range": 4,
    },
    "PHL-002": {
        "starting_utilization": 52,
        "daily_utilization_growth": 1.0,
        "noise_range": 4,
    },
    "PHL-003": {
        "starting_utilization": 57,
        "daily_utilization_growth": 2.4,
        "noise_range": 3,
    },
    "PHL-004": {
        "starting_utilization": 60,
        "daily_utilization_growth": -0.8,
        "noise_range": 4,
    },
    "NYC-001": {
        "starting_utilization": 62,
        "daily_utilization_growth": 2.8,
        "noise_range": 3,
    },
    "NYC-002": {
        "starting_utilization": 50,
        "daily_utilization_growth": 0.5,
        "noise_range": 4,
    },
    "NYC-003": {
        "starting_utilization": 69,
        "daily_utilization_growth": 0.7,
        "noise_range": 5,
    },
    "CHI-001": {
        "starting_utilization": 45,
        "daily_utilization_growth": 0.0,
        "noise_range": 4,
    },
    "CHI-002": {
        "starting_utilization": 55,
        "daily_utilization_growth": 1.8,
        "noise_range": 3,
    },
    "CHI-003": {
        "starting_utilization": 66,
        "daily_utilization_growth": 2.2,
        "noise_range": 3,
    },
}


def classify_reading_status(download_utilization_pct):
    if download_utilization_pct >= 85:
        return "critical"
    if download_utilization_pct >= 70:
        return "warning"
    return "normal"


def calculate_peak_hour_utilization_boost(hour):
    if 18 <= hour <= 22:
        return 18
    if 12 <= hour <= 17:
        return 9
    if 6 <= hour <= 11:
        return 5
    return 0


def calculate_node_baseline_utilization(node_id, day_index):
    node_utilization_profile = NODE_UTILIZATION_PROFILES[node_id]

    return (
        node_utilization_profile["starting_utilization"]
        + (node_utilization_profile["daily_utilization_growth"] * day_index)
    )


def generate_mock_node_readings():
    random.seed(42)

    start_time = datetime(2026, 6, 1, 0, 0)
    days_to_generate = 7
    generated_reading_records = []

    for hour_offset in range(days_to_generate * 24):
        timestamp = start_time + timedelta(hours=hour_offset)
        day_index = hour_offset // 24

        for region, node_ids in REGION_NODE_IDS.items():
            for node_id in node_ids:
                node_utilization_profile = NODE_UTILIZATION_PROFILES[node_id]
                base_utilization = calculate_node_baseline_utilization(
                    node_id,
                    day_index,
                )
                hourly_utilization_boost = calculate_peak_hour_utilization_boost(
                    timestamp.hour
                )
                utilization_noise = random.uniform(
                    -node_utilization_profile["noise_range"],
                    node_utilization_profile["noise_range"],
                )

                raw_download_utilization_pct = (
                    base_utilization
                    + hourly_utilization_boost
                    + utilization_noise
                )
                download_utilization_pct = round(
                    max(0, min(raw_download_utilization_pct, 100)),
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
