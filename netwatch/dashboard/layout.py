from dash import dash_table, dcc, html

from netwatch.dashboard.components import (
    create_metric_tiles,
    create_node_options,
    create_selected_node_detail_panel,
)
from netwatch.dashboard.data_loaders import serialize_dataframe
from netwatch.dashboard.figures import (
    create_anomaly_counts_figure,
    create_critical_counts_figure,
    create_daily_average_trend_figure,
    create_node_utilization_figure,
    create_region_risk_figure,
)


def create_layout(
    raw_readings_dataframe,
    node_summary_dataframe,
    anomaly_readings_dataframe,
    default_node_id,
):
    return html.Div(
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
                                "Loaded from API",
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
                                children=html.Div(
                                    id="metric-grid",
                                    children=create_metric_tiles(
                                        node_summary_dataframe
                                    ),
                                    className="metric-grid",
                                ),
                                className="anchor-section",
                            ),
                            html.Main(
                                [
                                    html.Section(
                                        id="node-detail",
                                        children=html.Div(
                                            id="selected-node-detail-panel",
                                            children=create_selected_node_detail_panel(
                                                node_summary_dataframe,
                                                default_node_id,
                                            ),
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
                                                config={"displayModeBar": False},
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
                                                config={"displayModeBar": False},
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
                                                config={"displayModeBar": False},
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
                                                config={"displayModeBar": False},
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
                                                config={"displayModeBar": False},
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
                                                    {
                                                        "name": column_name,
                                                        "id": column_name,
                                                    }
                                                    for column_name in node_summary_dataframe.columns
                                                ],
                                                page_size=10,
                                                sort_action="native",
                                                filter_action="native",
                                                style_table={"overflowX": "auto"},
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
