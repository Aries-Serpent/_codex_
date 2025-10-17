# Codex Archive Improvements – Usage Guide

This guide describes the new operational capabilities that ship with the archive
improvements package: configuration management, structured logging, retry
policies, batch restores, and performance instrumentation.

## 1. Configuration Management

1. Create a configuration file (optional) at `.codex/archive.toml`:

   ```toml
   [backend]
   backend = "postgres"
   url = "postgresql://codex:***@db/archive"

   [logging]
   level = "info"
   format = "json"

   [retry]
   max_attempts = 4
   initial_delay = 1.0

   [batch]
   results_path = "./.codex/archive/batch_results.json"
   progress_interval = 5

   [performance]
   enabled = true
   emit_to_evidence = true
   ```

2. Override values via environment variables when needed (highest precedence):

   ```bash
   export CODEX_ARCHIVE_URL="sqlite:///./.codex/test.sqlite"
   export CODEX_ARCHIVE_RETRY_ATTEMPTS=2
   ```

3. Inspect the composed configuration:

   ```bash
   codex archive config-show
   codex archive config-show --config-file path/to/archive.toml
   ```

## 2. Structured Logging

* Configure logging via the `[logging]` section.
* `format = "json"` produces deterministic NDJSON entries suitable for log
  aggregation.
* Evidence entries are appended to `.codex/evidence/archive_ops.jsonl` by default
  and can be overridden via the `CODEX_EVIDENCE_DIR` environment variable or the
  `logging.evidence_file` setting.

## 3. Retry Policies

The retry decorator automatically handles transient errors raised by
`ConnectionError`, `TimeoutError`, or `OSError`.

```python
from codex.archive.retry import retry_with_backoff, RetryConfig

@retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.5))
def fetch_blob(tombstone: str) -> bytes:
    ...
```

Retries are deterministic in tests when the `seed` attribute is provided.

## 4. Batch Restore Workflow

### Manifest formats

* **JSON** – either a list or an object with an `items` array.

  ```json
  {
    "items": [
      {"tombstone": "abc", "output": "restores/abc.bin"},
      {"tombstone": "def", "output": "restores/def.bin", "actor": "alice"}
    ]
  }
  ```

* **CSV** – headers: `tombstone`, `output`, optional `actor`.

  ```csv
  tombstone,output,actor
  abc,restores/abc.bin,
  def,restores/def.bin,bob
  ```

### CLI invocation

```bash
codex archive batch-restore manifest.json --actor ops-team
codex archive batch-restore manifest.csv --actor ops-team --results batch-results.json
```

* `--dry-run` validates the manifest and prints the number of entries without
  touching the backend.
* Progress updates and restore outcomes are logged to stderr at the interval
  defined in the configuration (default: every 10 items).

## 5. Performance Metrics

* `codex.archive.perf.timer` is used internally to record batch durations.
* Per-item metrics are attached to the batch results and to evidence logs when
  `performance.enabled` is `true`.

## 6. CLI Enhancements

* `codex archive config-show` – view the effective configuration.
* `codex archive batch-restore` – run manifest-driven restores with retries and
  evidence logging.
* `codex archive health-check --debug` – now emits structured evidence records
  indicating success or failure.

## 7. Troubleshooting

| Symptom | Suggested action |
|---------|------------------|
| `Unsupported archive backend` | Verify `backend.backend` is one of `sqlite`, `postgres`, `mariadb`. |
| Batch restore exits early | Inspect the evidence log – failed entries include sanitized exception details. |
| Metrics missing from evidence | Ensure `performance.enabled` and `performance.emit_to_evidence` are set to `true`. |
| CLI prints credentials | Use `--debug` only for local diagnostics. Non-debug output is automatically redacted. |
