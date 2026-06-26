# NetWatch Data Model

This document describes the current NetWatch tables and how they map to a real network capacity analytics system.

## Storage

Local database:

```text
data/netwatch.db
```

SQLite is our local stand-in for a production warehouse, lakehouse, or Databricks/Spark-managed table environment.

## Medallion Architecture

NetWatch now uses Databricks-style medallion table names locally.

```text
Bronze
    bronze_raw_node_readings
    Raw hourly telemetry loaded from the mock source.

Silver
    silver_validated_node_readings
    Quality-checked telemetry that passed validation.

    silver_anomaly_readings
    Enriched operational data containing unusual utilization readings.

Gold
    gold_node_summary
    Business-facing reporting table used by the API, dashboard, planning views, and future AI analysis.

    gold_node_forecast
    Business-facing forecast table used to identify nodes that may cross a critical utilization threshold.
```

Compatibility tables still exist:

```text
raw_node_readings
anomaly_readings
node_summary
```

Those older names are refreshed by the pipeline so previous scripts and learning notes still work.

## Table: bronze_raw_node_readings

`bronze_raw_node_readings` stores the raw hourly utilization telemetry loaded from `data/mock_node_readings.csv`.

In a Comcast-like production environment, this maps to raw or lightly cleaned telemetry collected from network devices, monitoring platforms, or capacity systems.

Grain:

```text
One row per node per timestamp
```

Expected volume:

```text
10 nodes x 7 days x 24 hours = 1,680 rows
```

Columns:

| Column | Type | Description |
| --- | --- | --- |
| `timestamp` | text/datetime-like | Hourly timestamp for the reading. |
| `node_id` | text | Unique identifier for the network node. |
| `region` | text | Region or market the node belongs to. |
| `download_utilization_pct` | float | Downstream utilization percentage for the node at that timestamp. |
| `upload_utilization_pct` | float | Upstream utilization percentage for the node at that timestamp. |
| `capacity_mbps` | integer | Simulated total capacity for the node in Mbps. |
| `status` | text | Reading-level status: `normal`, `warning`, or `critical`. |

Primary uniqueness expectation:

```text
node_id + timestamp should be unique
```

## Table: silver_validated_node_readings

`silver_validated_node_readings` stores telemetry that passed the local data quality checks.

Current checks:

```text
No missing values
No duplicate node/timestamp readings
Download utilization is between 0 and 100
Upload utilization is between 0 and 100
Each node has the expected number of readings
```

In production, Silver tables usually include cleaned, standardized, deduplicated, and enriched data that downstream systems can trust more than raw source data.

## Table: silver_anomaly_readings

`silver_anomaly_readings` stores readings that are unusually high compared with that node's own baseline.

This is a simple local version of an operational monitoring or anomaly detection layer.

Grain:

```text
One row per anomalous node reading
```

## Table: gold_node_summary

`gold_node_summary` stores node-level analytics derived from `silver_validated_node_readings`.

This is the reporting and planning layer. Dashboards, APIs, planning tools, and AI assistants should generally read from Gold tables instead of recomputing from raw telemetry every time.

Grain:

```text
One row per node
```

Selected columns:

| Column | Type | Description |
| --- | --- | --- |
| `node_id` | text | Unique identifier for the network node. |
| `region` | text | Region or market the node belongs to. |
| `avg_download_utilization` | float | Average downstream utilization across the reporting window. |
| `max_download_utilization` | float | Highest downstream utilization observed across the reporting window. |
| `avg_upload_utilization` | float | Average upstream utilization across the reporting window. |
| `max_upload_utilization` | float | Highest upstream utilization observed across the reporting window. |
| `total_reading_count` | integer | Total number of raw readings available for the node. |
| `critical_reading_count` | integer | Number of readings where downstream utilization was at least 85%. |
| `critical_reading_pct` | float | Percentage of readings that were critical. |
| `risk_level` | text | Node-level risk label: `normal`, `watch`, or `high_risk`. |

## Table: gold_node_forecast

`gold_node_forecast` stores simple capacity forecasts derived from `silver_validated_node_readings`.

This is not machine learning yet. It is a first planning model based on daily average utilization change.

Grain:

```text
One row per node
```

Selected columns:

| Column | Type | Description |
| --- | --- | --- |
| `node_id` | text | Unique identifier for the network node. |
| `region` | text | Region or market the node belongs to. |
| `first_day_avg_download_utilization` | float | First daily average in the observed window. |
| `last_day_avg_download_utilization` | float | Last daily average in the observed window. |
| `daily_download_utilization_change` | float | Estimated daily utilization change in percentage points. |
| `projected_7_day_download_utilization` | float | Projected utilization seven days after the last observed day. |
| `projected_30_day_download_utilization` | float | Projected utilization thirty days after the last observed day. |
| `days_until_critical` | integer/null | Estimated days until the node reaches 85% average utilization. |
| `forecast_risk_level` | text | Forecast label: `forecast_high_risk`, `forecast_watch`, or `forecast_stable`. |

## Package Layout

```text
netwatch/data_sources/
    Mock upstream telemetry sources and data exploration scripts.

netwatch/pipeline/
    ETL orchestration, database loading, and data quality jobs.

netwatch/analytics/
    Transformations that create analytical tables such as anomaly readings and node summaries.

netwatch/reporting/
    SQL/reporting queries used to inspect analytical outputs.

netwatch/api/
    FastAPI backend service.

netwatch/dashboard/
    Dash frontend application.
```

## Pipeline Flow

```text
netwatch/data_sources/generate_mock_data.py
        |
data/mock_node_readings.csv
        |
netwatch/pipeline/load_to_sqlite.py
        |
bronze_raw_node_readings
        |
netwatch/pipeline/data_quality_checks.py
        |
silver_validated_node_readings
        |
netwatch/analytics/anomaly_detection.py
        |
silver_anomaly_readings
        |
netwatch/analytics/build_node_summary.py
        |
gold_node_summary
        |
netwatch/analytics/build_node_forecast.py
        |
gold_node_forecast
        |
FastAPI + Dash dashboard
```

## Production Mapping

| NetWatch | Production Equivalent |
| --- | --- |
| `mock_node_readings.csv` | Raw telemetry feed or source export |
| SQLite `netwatch.db` | Warehouse, lakehouse, Databricks, or Spark table storage |
| `bronze_raw_node_readings` | Bronze/raw telemetry table |
| `silver_validated_node_readings` | Silver validated telemetry table |
| `silver_anomaly_readings` | Silver enriched monitoring table |
| `gold_node_summary` | Gold reporting/planning table |
| `gold_node_forecast` | Gold forecasting/planning table |
| `netwatch/pipeline/data_quality_checks.py` | Data quality gate or validation task |
| `netwatch/analytics/anomaly_detection.py` | Anomaly detection or monitoring job |
| `netwatch/api/app.py` | FastAPI backend service |
