from dash import html

from netwatch.dashboard.formatting import format_risk_label


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


def create_metric_tiles(node_summary_dataframe):
    high_risk_node_count = len(
        node_summary_dataframe[node_summary_dataframe["risk_level"] == "high_risk"]
    )
    watch_node_count = len(
        node_summary_dataframe[node_summary_dataframe["risk_level"] == "watch"]
    )
    highest_risk_node_record = node_summary_dataframe.sort_values(
        by=["critical_reading_count", "max_download_utilization"],
        ascending=False,
    ).iloc[0]

    return [
        create_metric_tile("High-risk nodes", high_risk_node_count, "critical"),
        create_metric_tile("Watch nodes", watch_node_count, "watch"),
        create_metric_tile("Highest-risk node", highest_risk_node_record["node_id"]),
        create_metric_tile(
            "Max utilization",
            f"{highest_risk_node_record['max_download_utilization']:.2f}%",
        ),
    ]


def get_recommended_node_action(node_summary_record):
    if node_summary_record["risk_level"] == "high_risk":
        return "Prioritize for capacity review"

    if node_summary_record["risk_level"] == "watch":
        return "Monitor during peak window"

    return "No immediate action"


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
                        f"{selected_node_record['peak_hour_max_download_utilization']:.2f}%",
                    ),
                    create_node_detail_item(
                        "First day avg",
                        f"{selected_node_record['first_day_avg_download_utilization']:.2f}%",
                    ),
                    create_node_detail_item(
                        "Last day avg",
                        f"{selected_node_record['last_day_avg_download_utilization']:.2f}%",
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
