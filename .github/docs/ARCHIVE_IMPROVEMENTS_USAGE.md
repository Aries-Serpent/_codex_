# Archive Restore Improvements: Usage Guide
> Generated: 2024-05-29 | Author: mbaetiong

---

## Table of Contents
1. [Configuration Management](#configuration-management)
2. [Structured Logging](#structured-logging)
3. [Retry Logic](#retry-logic)
4. [Batch Operations](#batch-operations)
5. [Performance Metrics](#performance-metrics)
6. [Multi-Backend Support](#multi-backend-support)
7. [Operational Examples](#operational-examples)

---

## Configuration Management
Create `.codex/archive.toml` to declare archive settings.

```toml
[backend]
type = "sqlite"
url = "sqlite:///./.codex/archive.sqlite"

[logging]
level = "info"
format = "json"

[retry]
enabled = true
max_attempts = 3
initial_delay = 1.0
max_delay = 32.0

[batch]
max_concurrent = 5
continue_on_error = false

[performance]
enable_metrics = true
```

**Precedence**
```
explicit file (ArchiveConfig.load(config_file=...))
      ↓
.codex/archive.toml
      ↓
environment variables
      ↓
built-in defaults
```

**Environment Overrides**
| Variable | Example | Purpose |
|----------|---------|---------|
| `CODEX_ARCHIVE_BACKEND` | `postgres` | Backend type override |
| `CODEX_ARCHIVE_URL` | `postgres://user@db/archive` | Connection string |
| `CODEX_ARCHIVE_LOG_LEVEL` | `debug` | Logging verbosity |
| `CODEX_ARCHIVE_RETRY_ENABLED` | `true` | Toggle retry decorator |
| `CODEX_ARCHIVE_BATCH_CONCURRENT` | `10` | Override concurrency |

**Inspect the effective config**
```bash
$ codex archive config-show
=== Archive Configuration ===
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite (credentials redacted)
Log Level: info
Retry: disabled
Batch Concurrency: 5
Performance Metrics: enabled

$ codex archive config-show --debug
=== Archive Configuration ===
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite
...
```

---

## Structured Logging
`codex.archive.logging_config.setup_logging` configures JSON or text output with URL redaction.

* JSON logs (default) are machine friendly and suitable for shipping to ELK/Splunk.
* Text logs are convenient for local debugging (`format = "text"`).
* Evidence events continue to be written to `.codex/evidence/archive_ops.jsonl`.

Example structured record:
```json
{
  "ts": "2024-05-29T10:31:42Z",
  "level": "info",
  "action": "RESTORE",
  "tombstone": "13b1...",
  "actor": "ops-user",
  "duration_ms": 248.2,
  "backend": "sqlite"
}
```

---

## Retry Logic
Use `codex.archive.retry.retry_with_backoff` to wrap transient operations.

```python
from codex.archive.retry import RetryConfig, retry_with_backoff

config = RetryConfig(max_attempts=5, initial_delay=0.5, max_delay=16.0, jitter=True)

@retry_with_backoff(config, transient_errors=(ConnectionError, TimeoutError))
def fetch_blob(tombstone: str) -> bytes:
    ...
```

`calculate_backoff(attempt, ...)` exposes the raw delay calculation for instrumentation or testing.

---

## Batch Operations
Restore many tombstones from a manifest.

```json
// manifest.json
{
  "items": [
    {"tombstone": "uuid-1", "output": "./restored/file1.txt"},
    {"tombstone": "uuid-2", "output": "./restored/file2.txt"}
  ]
}
```

```bash
$ codex archive batch-restore manifest.json --by ops-user
Processing 2 items from manifest...
Progress: 1/2 (50%)
Progress: 2/2 (100%)

Batch Restore Complete:
  ✓ Succeeded: 2
  ✗ Failed: 0
  Total Time: 415ms

Results saved to: batch_restore_20240529_103142.json
```

Key features:
* JSON or CSV manifests (with header `tombstone,output`).
* Progress callback printed per item.
* Results summary saved to disk and evidence log.
* `--continue-on-error` flag keeps processing even if some items fail.

---

## Performance Metrics
The `timer` context manager in `codex.archive.perf` captures durations in milliseconds.

```python
from codex.archive.perf import timer

with timer("restore") as metrics:
    service.restore_to_path(tombstone, output_path=Path("out.txt"), actor="ops-user")
print(metrics.duration_ms)
```

Batch restore records per-item `duration_ms`, enabling SLA dashboards.

---

## Multi-Backend Support
`ArchiveConfig` supports `sqlite`, `postgres`, and `mariadb`.

* Use SQLite (`sqlite:///...`) for local or single-node deployments.
* Use PostgreSQL (`postgres://user:pass@host:5432/db`) for HA setups.
* Use MariaDB/MySQL (`mysql://user:pass@host:3306/db`) when matching existing infrastructure.

The CLI health check redacts credentials by default:
```bash
$ codex archive health-check
=== Archive Health Check ===
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite (credentials redacted)
Status: ✓ OK
Items Retrievable: 0
```

---

## Operational Examples
### Development Sandbox
```bash
mkdir -p .codex
cat > .codex/archive.toml <<'CFG'
[backend]
type = "sqlite"
url = "sqlite:///./.codex/archive.sqlite"
[logging]
level = "debug"
format = "text"
CFG

# Archive a file
codex archive store demo ./obsolete.py --by dev --reason dead --commit HEAD

# Restore it
codex archive restore <tombstone> ./restored.py --by dev
```

### Production Bulk Restore
```bash
export CODEX_ARCHIVE_BACKEND=postgres
export CODEX_ARCHIVE_URL=postgres://archive:${PASSWORD}@db.prod.example.com/archive
export CODEX_ARCHIVE_RETRY_ENABLED=true
export CODEX_ARCHIVE_RETRY_MAX=5

codex archive batch-restore dr_manifest.json --by sre --continue-on-error
jq '.summary' batch_restore_*.json
```

### Troubleshooting a Failure
```bash
codex archive restore missing-tombstone ./out.txt --by ops --debug
# Inspect evidence log for details
jq 'select(.action=="RESTORE_FAIL")' .codex/evidence/archive_ops.jsonl | tail -5
```

---

Copilot is powered by AI; mistakes are possible. Share feedback via 👍 / 👎 to help improve the experience.
