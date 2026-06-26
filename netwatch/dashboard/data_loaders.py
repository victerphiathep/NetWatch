from io import StringIO

import pandas as pd

from netwatch.dashboard import api_client


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
    anomaly_readings_dataframe = pd.DataFrame(api_client.fetch_anomaly_readings())

    anomaly_readings_dataframe["timestamp"] = pd.to_datetime(
        anomaly_readings_dataframe["timestamp"]
    )

    return anomaly_readings_dataframe


def load_node_forecast_dataframe():
    node_forecast_dataframe = api_client.fetch_node_forecasts()
    return pd.DataFrame(node_forecast_dataframe)


def serialize_dataframe(dataframe):
    return dataframe.to_json(orient="split", date_format="iso")


def deserialize_dataframe(serialized_dataframe):
    return pd.read_json(StringIO(serialized_dataframe), orient="split")


def load_dashboard_data():
    raw_readings_dataframe = load_raw_readings_dataframe()
    node_summary_dataframe = load_node_summary_dataframe()
    anomaly_readings_dataframe = load_anomaly_readings_dataframe()
    node_forecast_dataframe = load_node_forecast_dataframe()

    return (
        raw_readings_dataframe,
        node_summary_dataframe,
        anomaly_readings_dataframe,
        node_forecast_dataframe,
    )
