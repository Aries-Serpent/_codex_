# Structured JSON logging (stdlib only)

- One event per line (JSONL) emitted to **stderr**.
- Core fields: `timestamp`, `log.level`, `log.logger`, `event.name`, `message`.
- Error fields (ECS/OTel-friendly): `error.kind`, `error.message`, `error.stack`.
- Subprocess fields: `cmd`, `exit_code`, `process.duration_ms`, `output.stdout`, `output.stderr` (truncated flags).
- Configure level via `CODEX_LOG_LEVEL` (default `INFO`).

References: Python logging/argparse/subprocess docs; OpenTelemetry Logs Data Model; Elastic Common Schema error fields.
