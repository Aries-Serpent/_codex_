# Observability

The telemetry module provides Prometheus metrics for key operations. Enable the metrics server via the CLI:

```bash
python -m codex_ml.telemetry.server
```
Use `track_time` to instrument functions and expose metrics on `/metrics`.
