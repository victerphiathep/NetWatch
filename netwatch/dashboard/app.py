from dash import Dash

from netwatch.config import ASSETS_DIR
from netwatch.dashboard.callbacks import register_callbacks
from netwatch.dashboard.components import choose_default_node_id
from netwatch.dashboard.data_loaders import load_dashboard_data
from netwatch.dashboard.layout import create_layout


def create_dashboard_app():
    (
        raw_readings_dataframe,
        node_summary_dataframe,
        anomaly_readings_dataframe,
    ) = load_dashboard_data()
    default_node_id = choose_default_node_id(node_summary_dataframe)

    dashboard_app = Dash(__name__, assets_folder=str(ASSETS_DIR))
    dashboard_app.title = "NetWatch"
    dashboard_app.layout = create_layout(
        raw_readings_dataframe,
        node_summary_dataframe,
        anomaly_readings_dataframe,
        default_node_id,
    )
    register_callbacks(dashboard_app)

    return dashboard_app


app = create_dashboard_app()


if __name__ == "__main__":
    app.run(debug=False)
