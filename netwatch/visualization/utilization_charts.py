import sqlite3

import pandas as pd
import plotly.express as px

from netwatch.config import CHARTS_DIR, NETWATCH_DATABASE_FILE


def load_raw_readings_dataframe():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        raw_readings_dataframe = pd.read_sql_query(
            "SELECT * FROM raw_node_readings",
            database_connection,
        )

    raw_readings_dataframe["timestamp"] = pd.to_datetime(
        raw_readings_dataframe["timestamp"]
    )

    return raw_readings_dataframe


def load_node_summary_dataframe():
    with sqlite3.connect(NETWATCH_DATABASE_FILE) as database_connection:
        node_summary_dataframe = pd.read_sql_query(
            "SELECT * FROM node_summary",
            database_connection,
        )

    return node_summary_dataframe


def create_node_utilization_chart(raw_readings_dataframe, node_id):
    node_readings_dataframe = raw_readings_dataframe[
        raw_readings_dataframe["node_id"] == node_id
    ]

    node_utilization_figure = px.line(
        node_readings_dataframe,
        x="timestamp",
        y="download_utilization_pct",
        title=f"Download Utilization Over Time: {node_id}",
        markers=True,
    )

    node_utilization_figure.add_hline(
        y=85,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical threshold",
    )

    return node_utilization_figure


def create_critical_counts_chart(node_summary_dataframe):
    critical_counts_figure = px.bar(
        node_summary_dataframe,
        x="node_id",
        y="critical_reading_count",
        color="risk_level",
        title="Critical Reading Count By Node",
    )

    return critical_counts_figure


def create_region_risk_chart(node_summary_dataframe):
    region_risk_dataframe = (
        node_summary_dataframe.groupby(["region", "risk_level"])
        .size()
        .reset_index(name="node_count")
    )

    region_risk_figure = px.bar(
        region_risk_dataframe,
        x="region",
        y="node_count",
        color="risk_level",
        title="Node Risk Count By Region",
        barmode="group",
    )

    return region_risk_figure


def main():
    CHARTS_DIR.mkdir(exist_ok=True)

    raw_readings_dataframe = load_raw_readings_dataframe()
    node_summary_dataframe = load_node_summary_dataframe()

    node_utilization_chart = create_node_utilization_chart(
        raw_readings_dataframe,
        node_id="CHI-003",
    )
    critical_counts_chart = create_critical_counts_chart(node_summary_dataframe)
    region_risk_chart = create_region_risk_chart(node_summary_dataframe)

    node_utilization_chart.write_html(CHARTS_DIR / "chi_003_utilization.html")
    critical_counts_chart.write_html(CHARTS_DIR / "critical_counts_by_node.html")
    region_risk_chart.write_html(CHARTS_DIR / "risk_count_by_region.html")

    print(f"Saved charts to {CHARTS_DIR}")


if __name__ == "__main__":
    main()
