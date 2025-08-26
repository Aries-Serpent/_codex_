# BEGIN: CODEX_PROMETHEUS
from __future__ import annotations


def maybe_export_metrics(app=None, port: int = 9000):
    try:
        from prometheus_client import Counter, Gauge, start_http_server
    except Exception:
        return None
    start_http_server(port)
    counters = {"requests_total": Counter("requests_total", "Total requests")}
    gauges = {"queue_depth": Gauge("queue_depth", "Queue depth")}
    return counters, gauges


# END: CODEX_PROMETHEUS
