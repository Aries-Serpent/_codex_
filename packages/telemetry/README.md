# codex-ml-telemetry

Framework-neutral telemetry contracts and Prometheus export helpers extracted from
the `codex-ml` monorepo. This package is an alpha-stage federation boundary; the
existing `codex_ml.telemetry` API remains supported during migration.

## Installation

```console
pip install "codex-ml-telemetry[prometheus]"
```

The base installation has no runtime dependencies. Install the `prometheus` extra
to expose metrics over HTTP.

## Public API

- `MetricsRegistry` exposes model accuracy, HTTP request/error/latency, active-request,
  and active-model metrics.
- `HealthReport` and `HealthStatus` are immutable, JSON-compatible health contracts.
- `render_prometheus` renders a registry without coupling to a web framework.
- `start_metrics_server` starts a localhost-bound Prometheus endpoint.
- `track_time` and the three legacy metric constants preserve the initial compatibility
  surface used by `codex_ml.telemetry`.

See `docs/adr/ADR-009-federated-package-boundaries.md` for ownership and migration rules.
