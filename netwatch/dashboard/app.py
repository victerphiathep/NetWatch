from io import StringIO
import sqlite3

from dash import Dash, Input, Output, State, dash_table, dcc, html
from netwatch.dashboard import api_client
import pandas as pd
import plotly.express as px

from netwatch.config import ASSETS_DIR, NETWATCH_DATABASE_FILE


RISK_COLOR_MAP = {
    "high_risk": "#ff5d5d",
    "watch": "#f4c430",
    "normal": "#42d392",
}

PLOTLY_DARK_TEMPLATE = "plotly_dark"


def load_raw_readings_dataframe():
    raw_readings_dataframe = pd.DataFrame(api_client.fetch_raw_readings())

    raw_readings_dataframe["timestamp"] = pd.to_datetime(
        raw_readings_dataframe["timestamp"]
    )

    return raw_readings_dataframe


def load_node_summary_dataframe():
    node_summary_dataframe = api_client.fetch_node_summaries()
    return pd.DataFrame(node_summary_dataframe)


def load_anomaly_readings_dataframe():
    anomaly_readings_dataframe = pd.DataFrame(
        api_client.fetch_anomaly_readings())

    anomaly_readings_dataframe["timestamp"] = pd.to_datetime(
        anomaly_readings_dataframe["timestamp"]
    )

    return anomaly_readings_dataframe


def serialize_dataframe(dataframe):
    return dataframe.to_json(orient="split", date_format="iso")


def deserialize_dataframe(serialized_dataframe):
    return pd.read_json(StringIO(serialized_dataframe), orient="split")


def load_dashboard_data():
    raw_readings_dataframe = load_raw_readings_dataframe()
    node_summary_dataframe = load_node_summary_dataframe()
    anomaly_readings_dataframe = load_anomaly_readings_dataframe()

    return raw_readings_dataframe, node_summary_dataframe, anomaly_readings_dataframe


def create_node_options(node_summary_dataframe):
    return [
        {"label": node_id, "value": node_id}
        for node_id in sorted(node_summary_dataframe["node_id"].unique())
    ]


def choose_default_node_id(node_summary_dataframe):
    return node_summary_dataframe.sort_values(
        by=["critical_reading_count", "max_download_utilization"],
        ascending=False,
    ).iloc[0]["node_id"]


def create_metric_tile(label, value, tone="default"):
    return html.Div(
        [
            html.Div(label, className="metric-label"),
            html.Div(value, className="metric-value"),
        ],
        className=f"metric-tile metric-tile-{tone}",
    )


def get_recommended_node_action(node_summary_record):
    if node_summary_record["risk_level"] == "high_risk":
        return "Prioritize for capacity review"

    if node_summary_record["risk_level"] == "watch":
        return "Monitor during peak window"

    return "No immediate action"


def format_risk_label(risk_level):
    return risk_level.replace("_", " ").title()


def create_node_detail_item(label, value):
    return html.Div(
        [
            html.Div(label, className="detail-label"),
            html.Div(value, className="detail-value"),
        ],
        className="detail-item",
    )


def create_selected_node_detail_panel(node_summary_dataframe, selected_node_id):
    selected_node_record = node_summary_dataframe[
        node_summary_dataframe["node_id"] == selected_node_id
    ].iloc[0]

    risk_level = selected_node_record["risk_level"]
    recommended_action = get_recommended_node_action(selected_node_record)

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(selected_node_record["node_id"]),
                            html.P(selected_node_record["region"]),
                        ],
                        className="detail-title-group",
                    ),
                    html.Div(
                        format_risk_label(risk_level),
                        className=f"risk-pill risk-pill-{risk_level}",
                    ),
                ],
                className="detail-header",
            ),
            html.Div(
                [
                    create_node_detail_item(
                        "Avg download",
                        f"{selected_node_record['avg_download_utilization']:.2f}%",
                    ),
                    create_node_detail_item(
                        "Max download",
                        f"{selected_node_record['max_download_utilization']:.2f}%",
                    ),
                    create_node_detail_item(
                        "Critical readings",
                        int(selected_node_record["critical_reading_count"]),
                    ),
                    create_node_detail_item(
                        "Critical rate",
                        f"{selected_node_record['critical_reading_pct']:.2f}%",
                    ),
                    create_node_detail_item(
                        "Peak critical",
                        int(selected_node_record["peak_hour_critical_reading_count"]),
                    ),
                    create_node_detail_item(
                        "Peak max",
                        (
                            f"{selected_node_record['peak_hour_max_download_utilization']:.2f}%"
                        ),
                    ),
                    create_node_detail_item(
                        "First day avg",
                        (
                            f"{selected_node_record['first_day_avg_download_utilization']:.2f}%"
                        ),
                    ),
                    create_node_detail_item(
                        "Last day avg",
                        (
                            f"{selected_node_record['last_day_avg_download_utilization']:.2f}%"
                        ),
                    ),
                    create_node_detail_item(
                        "7-day change",
                        f"{selected_node_record['download_utilization_change']:+.2f} pts",
                    ),
                ],
                className="detail-grid",
            ),
            html.Div(
                [
                    html.Div("Recommended action", className="detail-label"),
                    html.Div(recommended_action, className="action-value"),
                ],
                className="action-panel",
            ),
        ],
        className="node-detail-panel",
    )


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


def create_metric_tiles(node_summary_dataframe):
    high_risk_node_count = len(
        node_summary_dataframe[node_summary_dataframe["risk_level"]
                               == "high_risk"]
    )
    watch_node_count = len(
        node_summary_dataframe[node_summary_dataframe["risk_level"] == "watch"]
    )
    highest_risk_node_record = node_summary_dataframe.sort_values(
        by=["critical_reading_count", "max_download_utilization"],
        ascending=False,
    ).iloc[0]

    return [
        create_metric_tile("High-risk nodes",
                           high_risk_node_count, "critical"),
        create_metric_tile("Watch nodes", watch_node_count, "watch"),
        create_metric_tile("Highest-risk node",
                           highest_risk_node_record["node_id"]),
        create_metric_tile(
            "Max utilization",
            f"{highest_risk_node_record['max_download_utilization']:.2f}%",
        ),
    ]


def create_dashboard_app():
    (
        raw_readings_dataframe,
        node_summary_dataframe,
        anomaly_readings_dataframe,
    ) = load_dashboard_data()
    default_node_id = choose_default_node_id(node_summary_dataframe)

    dashboard_app = Dash(__name__, assets_folder=str(ASSETS_DIR))
    dashboard_app.title = "NetWatch"

    dashboard_app.layout = html.Div(
        [
            dcc.Store(
                id="raw-readings-store",
                data=serialize_dataframe(raw_readings_dataframe),
            ),
            dcc.Store(
                id="node-summary-store",
                data=serialize_dataframe(node_summary_dataframe),
            ),
            dcc.Store(
                id="anomaly-readings-store",
                data=serialize_dataframe(anomaly_readings_dataframe),
            ),
            html.Header(
                [
                    html.Div(
                        [
                            html.H1("NetWatch"),
                            html.P("Network Capacity Monitoring"),
                        ],
                        className="title-group",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Node"),
                                    dcc.Dropdown(
                                        id="node-selector",
                                        options=create_node_options(
                                            node_summary_dataframe
                                        ),
                                        value=default_node_id,
                                        clearable=False,
                                    ),
                                ],
                                className="node-selector",
                            ),
                            html.Button(
                                "Refresh Data",
                                id="refresh-data-button",
                                n_clicks=0,
                                className="refresh-button",
                            ),
                            html.Div(
                                "Loaded from SQLite",
                                id="refresh-status",
                                className="refresh-status",
                            ),
                        ],
                        className="control-group",
                    ),
                ],
                className="dashboard-header",
            ),
            html.Div(
                [
                    html.Nav(
                        [
                            html.A("Overview", href="#overview"),
                            html.A("Node Detail", href="#node-detail"),
                            html.A("Utilization", href="#utilization"),
                            html.A("Daily Trend", href="#daily-trend"),
                            html.A("Node Ranking", href="#node-ranking"),
                            html.A("Regional Risk", href="#regional-risk"),
                            html.A("Anomalies", href="#anomalies"),
                            html.A("Summary Table", href="#summary-table"),
                        ],
                        className="dashboard-nav",
                    ),
                    html.Div(
                        [
                            html.Section(
                                id="overview",
                                children=create_metric_tiles(
                                    node_summary_dataframe),
                                className="metric-grid anchor-section",
                            ),
                            html.Main(
                                [
                                    html.Section(
                                        id="node-detail",
                                        children=create_selected_node_detail_panel(
                                            node_summary_dataframe,
                                            default_node_id,
                                        ),
                                        className="panel panel-wide panel-highlight anchor-section",
                                    ),
                                    html.Section(
                                        id="utilization",
                                        children=[
                                            dcc.Graph(
                                                id="node-utilization-chart",
                                                figure=create_node_utilization_figure(
                                                    raw_readings_dataframe,
                                                    anomaly_readings_dataframe,
                                                    default_node_id,
                                                ),
                                                config={
                                                    "displayModeBar": False},
                                            )
                                        ],
                                        className="panel panel-wide anchor-section",
                                    ),
                                    html.Section(
                                        id="daily-trend",
                                        children=[
                                            dcc.Graph(
                                                id="daily-average-trend-chart",
                                                figure=create_daily_average_trend_figure(
                                                    raw_readings_dataframe,
                                                    default_node_id,
                                                ),
                                                config={
                                                    "displayModeBar": False},
                                            )
                                        ],
                                        className="panel panel-wide anchor-section",
                                    ),
                                    html.Section(
                                        id="node-ranking",
                                        children=[
                                            dcc.Graph(
                                                id="critical-counts-chart",
                                                figure=create_critical_counts_figure(
                                                    node_summary_dataframe
                                                ),
                                                config={
                                                    "displayModeBar": False},
                                            )
                                        ],
                                        className="panel anchor-section",
                                    ),
                                    html.Section(
                                        id="regional-risk",
                                        children=[
                                            dcc.Graph(
                                                id="region-risk-chart",
                                                figure=create_region_risk_figure(
                                                    node_summary_dataframe
                                                ),
                                                config={
                                                    "displayModeBar": False},
                                            )
                                        ],
                                        className="panel anchor-section",
                                    ),
                                    html.Section(
                                        id="anomalies",
                                        children=[
                                            dcc.Graph(
                                                id="anomaly-counts-chart",
                                                figure=create_anomaly_counts_figure(
                                                    anomaly_readings_dataframe
                                                ),
                                                config={
                                                    "displayModeBar": False},
                                            )
                                        ],
                                        className="panel panel-wide anchor-section",
                                    ),
                                    html.Section(
                                        id="summary-table",
                                        children=[
                                            html.H2("Node Summary"),
                                            dash_table.DataTable(
                                                id="node-summary-table",
                                                data=node_summary_dataframe.round(2).to_dict(
                                                    "records"
                                                ),
                                                columns=[
                                                    {"name": column_name,
                                                        "id": column_name}
                                                    for column_name in node_summary_dataframe.columns
                                                ],
                                                page_size=10,
                                                sort_action="native",
                                                filter_action="native",
                                                style_table={
                                                    "overflowX": "auto"},
                                                style_cell={
                                                    "backgroundColor": "#111827",
                                                    "border": "1px solid #263244",
                                                    "color": "#dbeafe",
                                                    "fontFamily": "Arial",
                                                    "fontSize": 13,
                                                    "padding": "9px",
                                                    "textAlign": "left",
                                                },
                                                style_header={
                                                    "backgroundColor": "#1f2937",
                                                    "border": "1px solid #334155",
                                                    "color": "#f8fafc",
                                                    "fontWeight": "bold",
                                                },
                                                style_filter={
                                                    "backgroundColor": "#0f172a",
                                                    "color": "#dbeafe",
                                                },
                                            ),
                                        ],
                                        className="panel panel-wide anchor-section",
                                    ),
                                ],
                                className="dashboard-grid",
                            ),
                        ],
                        className="dashboard-content",
                    ),
                ],
                className="dashboard-body",
            ),
        ],
        className="dashboard-shell",
    )

    @dashboard_app.callback(
        Output("raw-readings-store", "data"),
        Output("node-summary-store", "data"),
        Output("anomaly-readings-store", "data"),
        Output("node-selector", "options"),
        Output("node-selector", "value"),
        Output("refresh-status", "children"),
        Input("refresh-data-button", "n_clicks"),
        State("node-selector", "value"),
    )
    def refresh_dashboard_data(refresh_click_count, selected_node_id):
        (
            refreshed_raw_readings_dataframe,
            refreshed_node_summary_dataframe,
            refreshed_anomaly_readings_dataframe,
        ) = load_dashboard_data()

        node_options = create_node_options(refreshed_node_summary_dataframe)
        available_node_ids = {
            node_option["value"]
            for node_option in node_options
        }
        refreshed_node_id = (
            selected_node_id
            if selected_node_id in available_node_ids
            else choose_default_node_id(refreshed_node_summary_dataframe)
        )

        return (
            serialize_dataframe(refreshed_raw_readings_dataframe),
            serialize_dataframe(refreshed_node_summary_dataframe),
            serialize_dataframe(refreshed_anomaly_readings_dataframe),
            node_options,
            refreshed_node_id,
            f"SQLite refresh count: {refresh_click_count}",
        )

    @dashboard_app.callback(
        Output("metric-grid", "children"),
        Output("critical-counts-chart", "figure"),
        Output("region-risk-chart", "figure"),
        Output("anomaly-counts-chart", "figure"),
        Output("node-summary-table", "data"),
        Output("node-summary-table", "columns"),
        Input("node-summary-store", "data"),
        Input("anomaly-readings-store", "data"),
    )
    def update_summary_views(
        serialized_node_summary_dataframe,
        serialized_anomaly_readings_dataframe,
    ):
        refreshed_node_summary_dataframe = deserialize_dataframe(
            serialized_node_summary_dataframe
        )
        refreshed_anomaly_readings_dataframe = deserialize_dataframe(
            serialized_anomaly_readings_dataframe
        )

        return (
            create_metric_tiles(refreshed_node_summary_dataframe),
            create_critical_counts_figure(refreshed_node_summary_dataframe),
            create_region_risk_figure(refreshed_node_summary_dataframe),
            create_anomaly_counts_figure(refreshed_anomaly_readings_dataframe),
            refreshed_node_summary_dataframe.round(2).to_dict("records"),
            [
                {"name": column_name, "id": column_name}
                for column_name in refreshed_node_summary_dataframe.columns
            ],
        )

    @dashboard_app.callback(
        Output("selected-node-detail-panel", "children"),
        Input("node-summary-store", "data"),
        Input("node-selector", "value"),
    )
    def update_selected_node_detail_panel(
        serialized_node_summary_dataframe,
        selected_node_id,
    ):
        refreshed_node_summary_dataframe = deserialize_dataframe(
            serialized_node_summary_dataframe
        )

        return create_selected_node_detail_panel(
            refreshed_node_summary_dataframe,
            selected_node_id,
        )

    @dashboard_app.callback(
        Output("node-utilization-chart", "figure"),
        Output("daily-average-trend-chart", "figure"),
        Input("raw-readings-store", "data"),
        Input("anomaly-readings-store", "data"),
        Input("node-selector", "value"),
    )
    def update_selected_node_trend_charts(
        serialized_raw_readings_dataframe,
        serialized_anomaly_readings_dataframe,
        selected_node_id,
    ):
        refreshed_raw_readings_dataframe = deserialize_dataframe(
            serialized_raw_readings_dataframe
        )
        refreshed_raw_readings_dataframe["timestamp"] = pd.to_datetime(
            refreshed_raw_readings_dataframe["timestamp"]
        )
        refreshed_anomaly_readings_dataframe = deserialize_dataframe(
            serialized_anomaly_readings_dataframe
        )
        refreshed_anomaly_readings_dataframe["timestamp"] = pd.to_datetime(
            refreshed_anomaly_readings_dataframe["timestamp"]
        )

        return (
            create_node_utilization_figure(
                refreshed_raw_readings_dataframe,
                refreshed_anomaly_readings_dataframe,
                selected_node_id,
            ),
            create_daily_average_trend_figure(
                refreshed_raw_readings_dataframe,
                selected_node_id,
            ),
        )

    return dashboard_app


app = create_dashboard_app()


if __name__ == "__main__":
    app.run(debug=False)
