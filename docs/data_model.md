# NetWatch Data Model

This document describes the current NetWatch tables and how they map to a real network capacity analytics system.

## Storage

Local database:

```text
data/netwatch.db
```

This SQLite database is a local stand-in for a production data warehouse, lakehouse, or Databricks/Spark-managed table environment.

## Table: raw_node_readings

`raw_node_readings` stores the raw hourly utilization telemetry used by the pipeline.

In a Comcast-like production environment, this table would map to raw or lightly cleaned telemetry collected from network devices, monitoring platforms, or capacity systems.

Grain:

```text
One row per node per timestamp
```

Expected volume in the mock dataset:

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

## Table: anomaly_readings

`anomaly_readings` stores raw readings that are unusually high compared with that node's own baseline.

This is a simple local version of an operational monitoring or anomaly detection layer.

Grain:

```text
One row per anomalous node reading
```

## Table: node_summary

`node_summary` stores node-level analytics derived from `raw_node_readings`.

This is the reporting/analytics layer. Dashboards, APIs, planning tools, and AI assistants should generally read from this table instead of recomputing from raw telemetry every time.

Grain:

```text
One row per node
```

Columns:

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
raw_node_readings
        |
netwatch/pipeline/data_quality_checks.py
        |
netwatch/analytics/anomaly_detection.py
        |
anomaly_readings
        |
netwatch/analytics/build_node_summary.py
        |
node_summary
        |
netwatch/reporting/query_raw_data.py
```

## Medallion Architecture Mapping

```text
Bronze
    raw_node_readings
    Raw hourly telemetry loaded from the mock source.

Silver
    quality-checked raw readings
    anomaly_readings
    Cleaned, validated, and enriched operational data.

Gold
    node_summary
    region risk summaries
    Business-facing reporting tables for dashboards, planning, APIs, and AI analysis.
```

## Production Mapping

| NetWatch | Production Equivalent |
| --- | --- |
| `mock_node_readings.csv` | Raw telemetry feed or source export |
| SQLite `netwatch.db` | Warehouse, lakehouse, Databricks, or Spark table storage |
| `raw_node_readings` | Raw telemetry or bronze table |
| `netwatch/pipeline/data_quality_checks.py` | Data quality gate or validation task |
| `netwatch/analytics/anomaly_detection.py` | Anomaly detection or monitoring job |
| `node_summary` | Curated analytics/reporting or gold table |
| `netwatch/reporting/query_raw_data.py` | Dashboard/API/reporting queries |
| `netwatch/api/app.py` | FastAPI backend service |
