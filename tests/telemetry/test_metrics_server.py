import http.client
import time

from codex_ml.telemetry import REQUEST_LATENCY, start_metrics_server, track_time


def test_metrics_server_exports_metrics():
    started = start_metrics_server(port=8001)
    if not started:
        return  # prometheus_client missing

    @track_time(REQUEST_LATENCY)
    def dummy():
        pass

    dummy()
    time.sleep(0.1)
    conn = http.client.HTTPConnection("localhost", 8001)
    conn.request("GET", "/metrics")
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    assert "data_load_seconds" in data
