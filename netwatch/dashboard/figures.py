import plotly.express as px

from netwatch.dashboard.constants import PLOTLY_DARK_TEMPLATE, RISK_COLOR_MAP


def apply_dark_chart_layout(plotly_figure):
    plotly_figure.update_layout(
        template=PLOTLY_DARK_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dbeafe", "family": "Arial"},
        margin={"l": 36, "r": 24, "t": 58, "b": 36},
        legend_title_text="",
        title={"font": {"size": 18}},
    )
    plotly_figure.update_xaxes(gridcolor="#263244", zerolinecolor="#263244")
    plotly_figure.update_yaxes(gridcolor="#263244", zerolinecolor="#263244")
    return plotly_figure


def create_node_utilization_figure(
    raw_readings_dataframe,
    anomaly_readings_dataframe,
    selected_node_id,
):
    selected_node_readings_dataframe = raw_readings_dataframe[
        raw_readings_dataframe["node_id"] == selected_node_id
    ]

    node_utilization_figure = px.line(
        selected_node_readings_dataframe,
        x="timestamp",
        y="download_utilization_pct",
        markers=True,
        title=f"Download Utilization Trend: {selected_node_id}",
    )

    node_utilization_figure.update_traces(
        line={"color": "#60a5fa", "width": 3},
        marker={"size": 6, "color": "#93c5fd"},
    )

    node_utilization_figure.add_hline(
        y=85,
        line_dash="dash",
        line_color="#ff5d5d",
        annotation_text="Critical threshold",
        annotation_font_color="#fecaca",
    )

    selected_node_anomalies_dataframe = anomaly_readings_dataframe[
        anomaly_readings_dataframe["node_id"] == selected_node_id
    ]

    if not selected_node_anomalies_dataframe.empty:
        node_utilization_figure.add_scatter(
            x=selected_node_anomalies_dataframe["timestamp"],
            y=selected_node_anomalies_dataframe["download_utilization_pct"],
            mode="markers",
            marker={
                "color": "#f97316",
                "size": 12,
                "symbol": "diamond",
                "line": {"color": "#fed7aa", "width": 1},
            },
            name="Anomaly",
        )

    node_utilization_figure.update_layout(
        yaxis_title="Download utilization (%)",
        xaxis_title="Timestamp",
    )

    return apply_dark_chart_layout(node_utilization_figure)


def create_daily_average_trend_figure(raw_readings_dataframe, selected_node_id):
    selected_node_readings_dataframe = raw_readings_dataframe[
        raw_readings_dataframe["node_id"] == selected_node_id
    ].copy()
    selected_node_readings_dataframe["reading_date"] = selected_node_readings_dataframe[
        "timestamp"
    ].dt.date

    daily_average_dataframe = (
        selected_node_readings_dataframe.groupby("reading_date")
        .agg(
            daily_avg_download_utilization=(
                "download_utilization_pct",
                "mean",
            )
        )
        .reset_index()
    )

    daily_trend_figure = px.line(
        daily_average_dataframe,
        x="reading_date",
        y="daily_avg_download_utilization",
        markers=True,
        title=f"Daily Average Download Trend: {selected_node_id}",
    )

    daily_trend_figure.update_traces(
        line={"color": "#14b8a6", "width": 3},
        marker={"size": 8, "color": "#5eead4"},
    )

    daily_trend_figure.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily avg download utilization (%)",
    )

    return apply_dark_chart_layout(daily_trend_figure)


def create_critical_counts_figure(node_summary_dataframe):
    critical_counts_figure = px.bar(
        node_summary_dataframe.sort_values(
            by="critical_reading_count",
            ascending=False,
        ),
        x="node_id",
        y="critical_reading_count",
        color="risk_level",
        color_discrete_map=RISK_COLOR_MAP,
        title="Critical Reading Count By Node",
    )

    critical_counts_figure.update_layout(
        xaxis_title="Node",
        yaxis_title="Critical readings",
    )

    return apply_dark_chart_layout(critical_counts_figure)


def create_region_risk_figure(node_summary_dataframe):
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
        color_discrete_map=RISK_COLOR_MAP,
        barmode="group",
        title="Node Risk Count By Region",
    )

    region_risk_figure.update_layout(
        xaxis_title="Region",
        yaxis_title="Node count",
    )

    return apply_dark_chart_layout(region_risk_figure)


def create_anomaly_counts_figure(anomaly_readings_dataframe):
    anomaly_counts_dataframe = (
        anomaly_readings_dataframe.groupby(["node_id", "region"])
        .size()
        .reset_index(name="anomaly_count")
        .sort_values(by="anomaly_count", ascending=False)
    )

    anomaly_counts_figure = px.bar(
        anomaly_counts_dataframe,
        x="node_id",
        y="anomaly_count",
        color="region",
        title="Anomaly Count By Node",
    )

    anomaly_counts_figure.update_layout(
        xaxis_title="Node",
        yaxis_title="Anomaly readings",
    )

    return apply_dark_chart_layout(anomaly_counts_figure)
