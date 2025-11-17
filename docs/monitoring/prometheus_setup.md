# Prometheus Metrics Setup

Codex ML exposes Prometheus-compatible metrics for both CLI and service workflows. This guide covers the
minimal configuration needed to scrape the metrics endpoint and visualise the exported series.

## 1. Enable the metrics collector

Set the environment variables before launching the trainer or API runtime:

```bash
export CODEX_METRICS_ENABLED=1
export CODEX_METRICS_PORT=8000   # optional, defaults to 8000 when unset
python -m codex_ml.cli.train --config-name default
```text

When enabled the training loop instantiates a `CodexMetricsRegistry`, increments counters for each training step,
updates gauges with the most recent loss, and records epoch durations. Metrics are also appended to
`artifacts/metrics.ndjson` alongside structured session events for post-run analysis.

## 2. Run a Prometheus scraper

Create a `docker-compose.yml` with a Prometheus instance that targets the Codex metrics endpoint:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```text

The accompanying `prometheus.yml` instructs Prometheus to scrape the Codex FastAPI or CLI exporter:

```yaml
scrape_configs:
  - job_name: codex_ml
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```text

## 3. Inspect metrics

* Open http://localhost:9090 and query `codex_ml_training_steps_total` or
  `codex_ml_training_loss` to view live values.
* Combine the endpoint with Grafana to build dashboards for training curves and latency histograms.
* For offline runs, the metrics exported to `artifacts/metrics.ndjson` use the schema
  `{timestamp, metric_name, value, session_id}` so they can be ingested into any log analytics tool.

## 4. FastAPI integration

If you expose Codex as a service, register the `codex_ml.monitoring.metrics_export.metrics_endpoint_fastapi`
handler with FastAPI:

```python
from fastapi import FastAPI, Response
from codex_ml.monitoring import metrics_endpoint_fastapi

app = FastAPI()

@app.get("/metrics")
async def metrics() -> Response:
    return await metrics_endpoint_fastapi()
```text

The helper uses the global Prometheus registry by default, so any metrics recorded through
`CodexMetricsRegistry` are automatically exposed without additional wiring.

## 5. Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `ModuleNotFoundError: prometheus_client` | Install the optional dependency: `pip install prometheus-client`. The training loop gracefully falls back to a no-op collector when unavailable. |
| Port already in use | Set `CODEX_METRICS_PORT` to an unused port or configure the telemetry block in the Hydra config. |
| Missing `/metrics` endpoint | Confirm `metrics_endpoint_fastapi` is registered and that the Codex process started with `CODEX_METRICS_ENABLED=1`. |
