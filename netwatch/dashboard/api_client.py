import requests


API_BASE_URL = "http://127.0.0.1:8000"


def fetch_json(endpoint_path):
    api_response = requests.get(
        f"{API_BASE_URL}{endpoint_path}",
        timeout=10,
    )
    api_response.raise_for_status()
    return api_response.json()


def post_json(endpoint_path, payload):
    api_response = requests.post(
        f"{API_BASE_URL}{endpoint_path}",
        json=payload,
        timeout=45,
    )
    api_response.raise_for_status()
    return api_response.json()


def fetch_node_summaries():
    return fetch_json("/nodes")


def fetch_raw_readings():
    return fetch_json("/readings")


def fetch_anomaly_readings():
    return fetch_json("/anomalies")


def fetch_node_forecasts():
    return fetch_json("/forecasts")


def ask_netwatch_ai(question, result_count=5):
    return post_json(
        "/ai/ask",
        {
            "question": question,
            "result_count": result_count,
        },
    )
