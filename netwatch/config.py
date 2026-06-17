from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
CHARTS_DIR = PROJECT_ROOT / "charts"
ASSETS_DIR = PROJECT_ROOT / "assets"

RAW_READINGS_FILE = DATA_DIR / "mock_node_readings.csv"
NODE_SUMMARY_FILE = DATA_DIR / "node_summary.csv"
NETWATCH_DATABASE_FILE = DATA_DIR / "netwatch.db"
