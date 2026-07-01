import pandas as pd
from dash import Input, Output, State

from netwatch.dashboard.components import (
    choose_default_node_id,
    create_forecast_metric_tiles,
    create_metric_tiles,
    create_node_options,
    create_selected_node_detail_panel,
    create_selected_node_forecast_panel,
)
from netwatch.dashboard.data_loaders import (
    deserialize_dataframe,
    load_dashboard_data,
    serialize_dataframe,
)
from netwatch.dashboard.figures import (
    create_anomaly_counts_figure,
    create_critical_counts_figure,
    create_daily_average_trend_figure,
    create_forecast_projection_figure,
    create_node_utilization_figure,
    create_region_risk_figure,
)


def register_callbacks(dashboard_app):
    @dashboard_app.callback(
        Output("raw-readings-store", "data"),
        Output("node-summary-store", "data"),
        Output("anomaly-readings-store", "data"),
        Output("node-forecast-store", "data"),
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
            refreshed_node_forecast_dataframe,
        ) = load_dashboard_data()

        node_options = create_node_options(refreshed_node_summary_dataframe)
        available_node_ids = {node_option["value"] for node_option in node_options}
        refreshed_node_id = (
            selected_node_id
            if selected_node_id in available_node_ids
            else choose_default_node_id(refreshed_node_summary_dataframe)
        )

        return (
            serialize_dataframe(refreshed_raw_readings_dataframe),
            serialize_dataframe(refreshed_node_summary_dataframe),
            serialize_dataframe(refreshed_anomaly_readings_dataframe),
            serialize_dataframe(refreshed_node_forecast_dataframe),
            node_options,
            refreshed_node_id,
            f"API refresh count: {refresh_click_count}",
        )

    @dashboard_app.callback(
        Output("metric-grid", "children"),
        Output("critical-counts-chart", "figure"),
        Output("region-risk-chart", "figure"),
        Output("anomaly-counts-chart", "figure"),
        Output("forecast-metric-grid", "children"),
        Output("forecast-projection-chart", "figure"),
        Output("node-summary-table", "data"),
        Output("node-summary-table", "columns"),
        Output("node-forecast-table", "data"),
        Output("node-forecast-table", "columns"),
        Input("node-summary-store", "data"),
        Input("anomaly-readings-store", "data"),
        Input("node-forecast-store", "data"),
    )
    def update_summary_views(
        serialized_node_summary_dataframe,
        serialized_anomaly_readings_dataframe,
        serialized_node_forecast_dataframe,
    ):
        refreshed_node_summary_dataframe = deserialize_dataframe(
            serialized_node_summary_dataframe
        )
        refreshed_anomaly_readings_dataframe = deserialize_dataframe(
            serialized_anomaly_readings_dataframe
        )
        refreshed_node_forecast_dataframe = deserialize_dataframe(
            serialized_node_forecast_dataframe
        )

        return (
            create_metric_tiles(refreshed_node_summary_dataframe),
            create_critical_counts_figure(refreshed_node_summary_dataframe),
            create_region_risk_figure(refreshed_node_summary_dataframe),
            create_anomaly_counts_figure(refreshed_anomaly_readings_dataframe),
            create_forecast_metric_tiles(refreshed_node_forecast_dataframe),
            create_forecast_projection_figure(refreshed_node_forecast_dataframe),
            refreshed_node_summary_dataframe.round(2).to_dict("records"),
            [
                {"name": column_name, "id": column_name}
                for column_name in refreshed_node_summary_dataframe.columns
            ],
            refreshed_node_forecast_dataframe.round(2).to_dict("records"),
            [
                {"name": column_name, "id": column_name}
                for column_name in refreshed_node_forecast_dataframe.columns
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
        Output("selected-node-forecast-panel", "children"),
        Input("node-forecast-store", "data"),
        Input("node-selector", "value"),
    )
    def update_selected_node_forecast_panel(
        serialized_node_forecast_dataframe,
        selected_node_id,
    ):
        refreshed_node_forecast_dataframe = deserialize_dataframe(
            serialized_node_forecast_dataframe
        )

        return create_selected_node_forecast_panel(
            refreshed_node_forecast_dataframe,
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
