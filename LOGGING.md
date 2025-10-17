# Structured JSON logging (stdlib only)

- One event per line (JSONL) emitted to **stderr**.
- Core fields: `timestamp`, `log.level`, `log.logger`, `event.name`, `message`.
- Error fields (ECS/OTel-friendly): `error.kind`, `error.message`, `error.stack`.
- Subprocess fields: `cmd`, `exit_code`, `process.duration_ms`, `output.stdout`, `output.stderr` (truncated flags).
- Configure level via `CODEX_LOG_LEVEL` (default `INFO`).

References: Python logging/argparse/subprocess docs; OpenTelemetry Logs Data Model; Elastic Common Schema error fields.

## Fallback metrics writer

- When `psutil` or `pynvml` are unavailable, `src/logging_utils.setup_logging` now
  initialises a JSONL fallback writer (enabled by default).
- Metrics passed to `log_metrics(...)` are appended to
  `LoggingConfig.fallback_metrics_path` (defaults to `metrics_fallback.ndjson`).
- Each entry includes the log step, a floating-point timestamp, and the metric
  payload so observability pipelines retain minimal telemetry even without
  optional system libraries.
