# Gap 14 Verification: Prometheus Metrics

**Verdict:** IMPLEMENTED
**Date:** 2026-06-05

---

## Test Results

All three tests in the target files pass cleanly with `prometheus_client` present:

```
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /tmp/workspace/Aries-Serpent/_codex_
configfile: pytest.ini

tests/monitoring/test_prometheus_metrics_registry.py ..   [ 66%]
tests/monitoring/test_prometheus_fallback.py .            [100%]

3 passed in 0.26s
```

Full monitoring suite (`tests/monitoring/`):
```
1 failed, 189 passed, 3 skipped, 2 xfailed in 3.68s
```
The single failure (`test_engine_bootstrap`) is an unrelated PyTorch device-count stub issue, not Prometheus.

---

## Integration Status

### Core Implementation Modules

| File | Status | Description |
|------|--------|-------------|
| `src/codex_ml/monitoring/prometheus_metrics.py` | ✅ | `CodexMetricsRegistry` with Counter / Gauge / Histogram + `_NoopMetric` fallback |
| `src/codex_ml/monitoring/prometheus.py` | ✅ | `maybe_export_metrics()` — starts `prometheus_client.start_http_server` or falls back to NDJSON sink |
| `src/codex_ml/telemetry/server.py` | ✅ | `start_metrics_server(port, addr)` wrapping `prometheus_client.start_http_server` |
| `src/codex_ml/monitoring/__init__.py` | ✅ | Re-exports `CodexMetricsRegistry` and `metrics_enabled` |
| `src/codex_ml/telemetry/__init__.py` | ✅ | Re-exports `start_metrics_server` |

### Application Wiring

**`src/codex_ml/train_loop.py`** — fully wired:
- Imports `CodexMetricsRegistry`, `metrics_enabled` from `codex_ml.monitoring`
- Imports `start_metrics_server` from `codex_ml.telemetry`
- When `metrics_enabled()` or `telemetry_enable` flag is set, instantiates `CodexMetricsRegistry()`,
  sets `active_sessions`, and calls `start_metrics_server(port=port_candidate)` on startup
- Instruments training loop: `record_training_step(loss)`, `observe_data_loading(...)`,
  `observe_training_duration(...)` per epoch
- Clears `active_sessions` on shutdown

**`src/codex_ml/cli/codex_cli.py`** — fully wired:
- Imports `start_metrics_server` from `codex_ml.telemetry`
- CLI `train` command calls `start_metrics_server(port=port)` and prints an error if
  `prometheus_client` is missing

### Metrics Registered

`CodexMetricsRegistry` registers the following metrics under the `codex_ml` namespace:

| Metric name | Type | Description |
|-------------|------|-------------|
| `codex_ml_training_steps_total` | Counter | Total training steps completed |
| `codex_ml_training_loss` | Gauge | Current training loss |
| `codex_ml_training_duration_seconds` | Histogram | Training loop duration |
| `codex_ml_inference_requests_total` | Counter | Total inference requests (label: `endpoint`) |
| `codex_ml_inference_latency_seconds` | Histogram | Inference latency (label: `endpoint`) |
| `codex_ml_data_loading_duration_seconds` | Histogram | Data loader iteration time |
| `codex_ml_active_sessions` | Gauge | Active training/inference sessions |

### Fallback Behaviour

- When `prometheus_client` is unavailable, `CodexMetricsRegistry` switches every metric to a
  `_NoopMetric` stub — all methods (`inc`, `set`, `observe`, `labels`, `time`) are no-ops that
  keep a local `_value` float.
- `maybe_export_metrics()` (in `prometheus.py`) falls back to `_FallbackCounter` /
  `_FallbackGauge` objects that write NDJSON records to
  `artifacts/metrics/prometheus/prometheus.ndjson`.
- `fallback_status()` exposes `(active, path, reason)` so callers can detect and report the
  fallback state.

### HTTP Scrape Endpoint

The Prometheus HTTP scrape endpoint is provided by `prometheus_client.start_http_server`, which
starts a separate HTTP server (default port `8000` in the CLI; configurable). This exposes the
standard `/metrics` text format that any Prometheus server can scrape.

**Note:** `monitoring/dashboard_api.py` (the FastAPI dashboard) does **not** expose a
`/metrics` endpoint in Prometheus text format — it serves internal JSON metrics at
`/api/metrics/{ci,security,agents}`. These are two separate systems:
the dashboard is for human/UI consumption; the `start_http_server` path is for Prometheus scraping.

### DVC / CI Integration

- `dvc.yaml`: no Prometheus scrape or push stage defined.
- `.github/workflows/`: no workflow step scrapes or validates the `/metrics` endpoint.
- Metrics collection is gated behind the `CODEX_METRICS_ENABLED` env var (or the
  `--telemetry-enable` CLI flag), so it is opt-in and intentionally off in CI.

---

## Missing Pieces (if NEEDS_WORK)

**Not applicable — verdict is IMPLEMENTED.**

For completeness, items that are present but not yet integrated:

1. **`maybe_export_metrics()` not called from any app entry point** — tested directly but not
   invoked in `train_loop.py` or the CLI. The train-loop uses `start_metrics_server` instead,
   which is equivalent. `maybe_export_metrics` is an alternative helper for FastAPI apps.

2. **`dashboard_api.py` has no Prometheus-format `/metrics` route** — the dashboard serves
   custom JSON. Adding a `generate_latest`-backed `/metrics` route would allow Prometheus to
   scrape the dashboard process directly, but the training-loop `start_http_server` path already
   satisfies typical scraping requirements.

3. **No CI validation of the `/metrics` endpoint** — there is no workflow job that starts the
   metrics server and asserts the endpoint is reachable or well-formed. This would strengthen
   the integration confidence but is not required for the feature to be considered implemented.

---

## Summary

Gap 14 is **IMPLEMENTED**. The full wiring chain exists:

```
train_loop.py / codex_cli.py
  └─ CodexMetricsRegistry  (prometheus_metrics.py)  — 7 metrics registered
  └─ start_metrics_server  (telemetry/server.py)    — HTTP scrape endpoint
  └─ _NoopMetric / NDJSON fallback                  — graceful degradation
```

All three target tests pass. The implementation handles both the happy path (prometheus_client
installed) and the fallback path (NDJSON sink), with full coverage tested by
`test_prometheus_metrics_registry.py` and `test_prometheus_fallback.py`.
