from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
CHARTS_DIR = PROJECT_ROOT / "charts"
ASSETS_DIR = PROJECT_ROOT / "assets"

RAW_READINGS_FILE = DATA_DIR / "mock_node_readings.csv"
NODE_SUMMARY_FILE = DATA_DIR / "node_summary.csv"
NETWATCH_DATABASE_FILE = DATA_DIR / "netwatch.db"

BRONZE_RAW_READINGS_TABLE = "bronze_raw_node_readings"
SILVER_VALIDATED_READINGS_TABLE = "silver_validated_node_readings"
SILVER_ANOMALY_READINGS_TABLE = "silver_anomaly_readings"
GOLD_NODE_SUMMARY_TABLE = "gold_node_summary"
GOLD_NODE_FORECAST_TABLE = "gold_node_forecast"

LEGACY_RAW_READINGS_TABLE = "raw_node_readings"
LEGACY_ANOMALY_READINGS_TABLE = "anomaly_readings"
LEGACY_NODE_SUMMARY_TABLE = "node_summary"
