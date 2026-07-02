import sqlite3

from netwatch.config import (
    DOCS_DIR,
    GOLD_NODE_FORECAST_TABLE,
    GOLD_NODE_SUMMARY_TABLE,
    NETWATCH_DATABASE_FILE,
    SILVER_ANOMALY_READINGS_TABLE,
)


def format_node_summary_document(node_summary_row):
    return {
        "id": f"node-summary-{node_summary_row['node_id']}",
        "text": (
            f"Node {node_summary_row['node_id']} in {node_summary_row['region']} "
            f"has risk level {node_summary_row['risk_level']}. "
            f"Average download utilization is "
            f"{node_summary_row['avg_download_utilization']:.2f}%. "
            f"Maximum download utilization is "
            f"{node_summary_row['max_download_utilization']:.2f}%. "
            f"The node had {node_summary_row['critical_reading_count']} critical "
            f"readings, representing {node_summary_row['critical_reading_pct']:.2f}% "
            f"of readings. Peak-hour average download utilization is "
            f"{node_summary_row['peak_hour_avg_download_utilization']:.2f}%."
        ),
        "metadata": {
            "source": "gold_node_summary",
            "document_type": "node_summary",
            "node_id": node_summary_row["node_id"],
            "region": node_summary_row["region"],
        },
    }


def format_node_forecast_document(node_forecast_row):
    days_until_critical = node_forecast_row["days_until_critical"]
    days_until_critical_text = (
        "not projected to cross the critical threshold"
        if days_until_critical is None
        else f"projected to cross the critical threshold in {days_until_critical:.0f} days"
    )

    return {
        "id": f"node-forecast-{node_forecast_row['node_id']}",
        "text": (
            f"Forecast for node {node_forecast_row['node_id']} in "
            f"{node_forecast_row['region']}: forecast risk level is "
            f"{node_forecast_row['forecast_risk_level']}. "
            f"Last-day average download utilization is "
            f"{node_forecast_row['last_day_avg_download_utilization']:.2f}%. "
            f"Daily utilization change is "
            f"{node_forecast_row['daily_download_utilization_change']:.2f} "
            f"percentage points. The 7-day projection is "
            f"{node_forecast_row['projected_7_day_download_utilization']:.2f}%. "
            f"The 30-day projection is "
            f"{node_forecast_row['projected_30_day_download_utilization']:.2f}%. "
            f"The node is {days_until_critical_text}."
        ),
        "metadata": {
            "source": "gold_node_forecast",
            "document_type": "node_forecast",
            "node_id": node_forecast_row["node_id"],
            "region": node_forecast_row["region"],
        },
    }


def format_forecast_risk_summary_document(node_forecast_rows):
    forecast_nodes_by_risk_level = {}

    for node_forecast_row in node_forecast_rows:
        forecast_risk_level = node_forecast_row["forecast_risk_level"]
        forecast_nodes_by_risk_level.setdefault(forecast_risk_level, []).append(
            node_forecast_row["node_id"]
        )

    forecast_summary_parts = [
        f"{forecast_risk_level}: {', '.join(sorted(node_ids))}"
        for forecast_risk_level, node_ids in sorted(
            forecast_nodes_by_risk_level.items()
        )
    ]

    return {
        "id": "forecast-risk-summary",
        "text": (
            "Forecast risk summary for NetWatch nodes. "
            + "; ".join(forecast_summary_parts)
            + ". Forecast high-risk nodes should receive near-term capacity planning attention."
        ),
        "metadata": {
            "source": "gold_node_forecast",
            "document_type": "forecast_risk_summary",
        },
    }


def format_anomaly_summary_document(anomaly_rows):
    anomaly_count_by_node = {}

    for anomaly_row in anomaly_rows:
        node_id = anomaly_row["node_id"]
        anomaly_count_by_node[node_id] = anomaly_count_by_node.get(node_id, 0) + 1

    anomaly_summary_parts = [
        f"{node_id}: {anomaly_count} anomalies"
        for node_id, anomaly_count in sorted(
            anomaly_count_by_node.items(),
            key=lambda node_count: node_count[1],
            reverse=True,
        )
    ]

    return {
        "id": "anomaly-summary",
        "text": (
            "Anomaly summary across NetWatch nodes. "
            + "; ".join(anomaly_summary_parts)
        ),
        "metadata": {
            "source": "silver_anomaly_readings",
            "document_type": "anomaly_summary",
        },
    }


def load_markdown_documents():
    markdown_documents = []

    for markdown_file in sorted(DOCS_DIR.glob("*.md")):
        markdown_text = markdown_file.read_text(encoding="utf-8")
        markdown_documents.append(
            {
                "id": f"doc-{markdown_file.stem}",
                "text": markdown_text,
                "metadata": {
                    "source": str(markdown_file.relative_to(DOCS_DIR.parent)),
                    "document_type": "project_documentation",
                },
            }
        )

    return markdown_documents


def load_database_documents():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        database_connection.row_factory = sqlite3.Row

        node_summary_rows = database_connection.execute(
            f"SELECT * FROM {GOLD_NODE_SUMMARY_TABLE}"
        ).fetchall()
        node_forecast_rows = database_connection.execute(
            f"SELECT * FROM {GOLD_NODE_FORECAST_TABLE}"
        ).fetchall()
        anomaly_rows = database_connection.execute(
            f"SELECT * FROM {SILVER_ANOMALY_READINGS_TABLE}"
        ).fetchall()

    knowledge_documents = []
    knowledge_documents.extend(
        format_node_summary_document(node_summary_row)
        for node_summary_row in node_summary_rows
    )
    knowledge_documents.extend(
        format_node_forecast_document(node_forecast_row)
        for node_forecast_row in node_forecast_rows
    )
    knowledge_documents.append(
        format_forecast_risk_summary_document(node_forecast_rows)
    )

    if anomaly_rows:
        knowledge_documents.append(format_anomaly_summary_document(anomaly_rows))

    return knowledge_documents


def load_knowledge_documents():
    return load_database_documents() + load_markdown_documents()
