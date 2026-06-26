# NetWatch
Mock network capacity monitoring dashboard

__________________________________________

Generate mock readings
        ↓
Store in SQLite
        ↓
Use SQL to query raw data
        ↓
Use pandas to transform and summarize it
        ↓
Load summary data back into SQLite
        ↓
Visualize with Plotly
        ↓
Use RAG to ask questions about the results

___________________________________________

Node = shared network capacity point serving a group of customers
High utilization = many customers competing for finite bandwidth
Repeated high utilization = possible capacity risk
Capacity planning = deciding when and how to add relief before users suffer

## Code Organization

```text
netwatch/data_sources/
    Mock telemetry generation and exploratory scripts.

netwatch/pipeline/
    ETL jobs, data quality checks, and pipeline orchestration.

netwatch/analytics/
    Anomaly detection and summary-table transformations.

netwatch/reporting/
    SQL/reporting queries for inspecting outputs.

netwatch/api/
    FastAPI backend service.

netwatch/dashboard/
    Dash frontend application.

netwatch/visualization/
    Standalone Plotly chart generation.
```

Run the full local pipeline:

```powershell
python -m netwatch.pipeline.run_pipeline
```

## Local Medallion Tables

NetWatch uses SQLite as a local stand-in for Databricks-style lakehouse tables:

```text
Bronze: bronze_raw_node_readings
Silver: silver_validated_node_readings, silver_anomaly_readings
Gold:   gold_node_summary
```

The API and dashboard read from the medallion tables. Compatibility tables with the original names are still refreshed for older learning scripts.
