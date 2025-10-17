# Archive Restore Improvements: Complete Usage Guide

> Generated: 2025-10-17 13:22:36 | Author: mbaetiong | Updated: 2025-10-17

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

### Quick Start

Create `.codex/archive.toml` in your repository root:

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

### Configuration Precedence

```text
Explicit CLI file
    ↓ (if provided)
.codex/archive.toml
    ↓ (if exists)
Environment Variables
    ↓ (if set)
Safe Defaults
```

### Environment Variables Reference

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `CODEX_ARCHIVE_BACKEND` | sqlite\|postgres\|mariadb | sqlite | Backend type |
| `CODEX_ARCHIVE_URL` | Connection string | sqlite:///./.codex/archive.sqlite | Backend URL |
| `CODEX_ARCHIVE_LOG_LEVEL` | debug\|info\|warn\|error | info | Log verbosity |
| `CODEX_ARCHIVE_LOG_FORMAT` | json\|text | json | Log format |
| `CODEX_ARCHIVE_RETRY_ENABLED` | true\|false | false | Enable retry logic |
| `CODEX_ARCHIVE_RETRY_MAX` | 1-10 | 3 | Max retry attempts |
| `CODEX_ARCHIVE_BATCH_CONCURRENT` | 1-32 | 5 | Concurrent batch items |

### Show Configuration

```bash
# Show current config (URLs redacted)
$ codex archive config-show
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite (credentials redacted)
Log Level: info
Retry: disabled
Batch Concurrency: 5

# Show full config (debug mode - includes credentials)
$ codex archive config-show --debug
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite
...
```

---

## Structured Logging

### Log Levels

**DEBUG** - Detailed diagnostic information

```text
[2025-10-17T13:22:36.123Z] DEBUG Backend validation: OK
[2025-10-17T13:22:36.124Z] DEBUG Decompression codec: zstd
```

**INFO** - General operational information (default)

```text
[2025-10-17T13:22:36.125Z] INFO Restore completed in 245ms
```

**WARN** - Warning messages

```text
[2025-10-17T13:22:36.126Z] WARN Artifact near retention threshold
```

**ERROR** - Error conditions

```text
[2025-10-17T13:22:36.127Z] ERROR Restore failed: Tombstone not found
```

### Enabling Debug Logging

```bash
# Via environment variable
export CODEX_ARCHIVE_LOG_LEVEL=debug
codex archive restore <tombstone> output.txt --by user

# Via config file
cat > .codex/archive.toml <<'EOT'
[logging]
level = "debug"
EOT
```

### Log Output Format

**JSON Format** (default - recommended for production)

```json
{
  "ts": "2025-10-17T13:22:36.123Z",
  "level": "info",
  "action": "RESTORE",
  "actor": "user",
  "tombstone": "8e3531b9-c839-4a07-9dec-507c36136eb1",
  "duration_ms": 245.0,
  "backend": "sqlite"
}
```

**Text Format** (human-readable)

```text
[2025-10-17T13:22:36.123Z] INFO   Restore completed in 245ms
```

### Centralized Logging Integration

Archive logs are written to:

- **Stdout/Stderr** - Always (for CLI visibility)
- **Evidence Log** - `.codex/evidence/archive_ops.jsonl` (always JSON)
- **Optional File** - Specified via `logging.file` config

To send logs to ELK/Datadog/CloudWatch, pipe the evidence JSONL file:

```bash
tail -f .codex/evidence/archive_ops.jsonl | \
  fluentd -c fluentd.conf --config-dir /etc/fluentd/
```

---

## Retry Logic

### Overview

Retry mechanism with exponential backoff for transient failures:

- Covers: `ConnectionError`, `TimeoutError`, `OSError`
- **Backoff formula**: `delay = initial_delay * (backoff_factor ^ attempt)`
- **Capped at** `max_delay`
- **Optional jitter**: ±10% randomness for distributed load

### Configuration

```toml
[retry]
enabled = true
max_attempts = 3
initial_delay = 1.0  # seconds
max_delay = 32.0     # cap at 32 seconds
backoff_factor = 2.0
jitter = true        # add random variance
```

### Backoff Sequence Example

With defaults (`initial_delay=1.0`, `backoff_factor=2.0`, `max_delay=32.0`):

| Attempt | Base Delay | With Jitter | Actual Wait |
|---------|------------|-------------|-------------|
| 1 | 1.0s | 0.9-1.1s | ~1.0s |
| 2 | 2.0s | 1.8-2.2s | ~2.0s |
| 3 | 4.0s | 3.6-4.4s | ~4.0s |
| 4 | 8.0s | 7.2-8.8s | ~8.0s |
| 5 | 16.0s | 14.4-17.6s | ~16.0s |
| 6+ | 32.0s | 28.8-35.2s → capped | ~32.0s |

### Enabling Retry

```bash
# Via config file
cat > .codex/archive.toml <<'EOT'
[retry]
enabled = true
max_attempts = 5
EOT

# Via environment variable
export CODEX_ARCHIVE_RETRY_ENABLED=true
export CODEX_ARCHIVE_RETRY_MAX=5
```

### Retry Behavior in Evidence Logs

```json
{
  "action": "RESTORE",
  "actor": "user",
  "tombstone": "uuid",
  "attempt": 1,
  "status": "retrying",
  "reason": "Connection timeout"
}
```

After final success/failure, detailed event is recorded with total duration.

---

## Batch Operations

### Overview

Restore multiple tombstones from a manifest file with:

- Progress tracking
- Per-item status reporting
- Partial failure handling
- Results summary

### Manifest Formats

**JSON Format** (recommended)

```json
{
  "items": [
    {
      "tombstone": "uuid-1",
      "output": "/path/to/file1.txt"
    },
    {
      "tombstone": "uuid-2",
      "output": "/path/to/file2.txt"
    }
  ]
}
```

**CSV Format**

```csv
tombstone,output
uuid-1,/path/to/file1.txt
uuid-2,/path/to/file2.txt
```

### Basic Usage

```bash
# Create manifest
cat > manifest.json <<'EOT'
{
  "items": [
    {"tombstone": "8e3531b9...", "output": "./file1.txt"},
    {"tombstone": "9f4641c0...", "output": "./file2.txt"}
  ]
}
EOT

# Restore all items
$ codex archive batch-restore manifest.json --by user
Processing 2 items from manifest...
Progress: 1/2 (50%)
Progress: 2/2 (100%)
Batch Restore Complete:
  ✓ Succeeded: 2
  ✗ Failed: 0
  Total Time: 489.0ms
Results saved to: batch_restore_20251017_132236.json
```

### Configuration

```toml
[batch]
max_concurrent = 5           # max parallel restores
timeout_per_item = 300       # seconds per item
continue_on_error = false    # stop on first failure?
```

### Continue on Error

```bash
# Continue processing even if some items fail
$ codex archive batch-restore manifest.json --by user --continue-on-error
Processing 5 items...
Progress: 1/5 (20%)
Progress: 2/5 (40%)
[ERROR] Item 3 failed: Tombstone not found
Progress: 3/5 (60%)
...
Batch Restore Complete:
  ✓ Succeeded: 4
  ✗ Failed: 1
Results saved to: batch_restore_20251017_132236.json
```

### Results File

```json
{
  "items": [
    {
      "item": {
        "tombstone": "uuid-1",
        "output": "/path/to/file1.txt"
      },
      "status": "success",
      "duration_ms": 234.5,
      "error": null
    },
    {
      "item": {
        "tombstone": "uuid-2",
        "output": "/path/to/file2.txt"
      },
      "status": "failed",
      "duration_ms": 12.3,
      "error": "Tombstone not found"
    }
  ],
  "summary": {
    "total": 2,
    "succeeded": 1,
    "failed": 1,
    "skipped": 0,
    "total_duration_ms": 246.8
  }
}
```

### Resume from Checkpoint

For large batch operations, restart from a specific item:

```bash
# Original run failed at item 50
$ codex archive batch-restore manifest.json --by user
# ... fails at item 50 of 100

# Resume from item 50
$ codex archive batch-restore manifest.json --by user --resume-from 50
Progress: 50/100 (50%)
...
```

---

## Performance Metrics

### Overview

All restore operations include timing data:

- **Operation duration** - Total restore time
- **Decompression timing** - Time to decompress artifact
- **File write timing** - Time to write output file

### Enabling Metrics

```toml
[performance]
enable_metrics = true
track_decompression = true
```

### Evidence Log Format

```json
{
  "action": "RESTORE",
  "actor": "user",
  "tombstone": "uuid",
  "duration_ms": 245.0,
  "decompression_ms": 12.3,
  "write_ms": 5.1,
  "backend": "sqlite"
}
```

### CLI Output with Metrics

```bash
$ CODEX_ARCHIVE_LOG_LEVEL=info codex archive restore uuid out.txt --by user
[2025-10-17T13:22:36] INFO Restore started
[2025-10-17T13:22:36] INFO Decompression completed in 12.3ms
[2025-10-17T13:22:36] INFO File written in 5.1ms
[2025-10-17T13:22:36] INFO Restore completed in 245.0ms total
output.txt
```

### SLA Monitoring

Track restore performance over time:

```bash
# Extract timing data from evidence logs
jq '.duration_ms' .codex/evidence/archive_ops.jsonl | \
  jq -s 'add/length'  # Calculate average

# Results histogram
jq '.duration_ms' .codex/evidence/archive_ops.jsonl | sort -n | tail -20
```

---

## Multi-Backend Support

### Supported Backends

| Backend | URL Format | Status | Use Case |
|---------|------------|--------|----------|
| **SQLite** | `sqlite:///path/to/archive.db` | ✅ Production | Local/single-node |
| **PostgreSQL** | `postgres://user@host/db` | ✅ Production | Distributed/HA |
| **MariaDB** | `mysql://user@host/db` | ✅ Production | MySQL-compatible |

### Backend Configuration

**SQLite** (default - no auth needed)

```toml
[backend]
type = "sqlite"
url = "sqlite:///./.codex/archive.sqlite"
```

**PostgreSQL**

```toml
[backend]
type = "postgres"
url = "postgres://archive_user@db.example.com:5432/archive_db"
```

**MariaDB**

```toml
[backend]
type = "mariadb"
url = "mysql://archive_user@db.example.com:3306/archive_db"
```

### Backend Health Check

```bash
$ codex archive health-check
=== Archive Health Check ===
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite (credentials redacted)
Status: ✓ OK
Items Retrievable: 245

# With debug (full URL)
$ codex archive health-check --debug
=== Archive Health Check ===
Backend: postgres
URL: postgres://user@localhost/archive
Status: ✓ OK
Items Retrievable: 1523
```

---

## Operational Examples

### Example 1: Development Setup (SQLite, Local)

```bash
# Create config
mkdir -p .codex
cat > .codex/archive.toml <<'EOT'
[backend]
type = "sqlite"
url = "sqlite:///./.codex/archive.sqlite"
[logging]
level = "debug"
format = "text"
[retry]
enabled = false
[performance]
enable_metrics = true
EOT

# Archive a file
$ codex archive store my-repo ./old_module.py \
  --by developer --reason "dead" --commit HEAD
{
  "tombstone": "8e3531b9-...",
  "sha256": "abc123...",
  "size_bytes": 1024,
  ...
}

# Restore it
$ codex archive restore 8e3531b9-... ./restored_module.py --by developer
./restored_module.py

# View logs
$ cat .codex/evidence/archive_ops.jsonl | jq .
```

### Example 2: Production Setup (PostgreSQL, Retry+Batch)

```bash
# Production config with retry and batch support
cat > .codex/archive.toml <<'EOT'
[backend]
type = "postgres"
url = "postgres://archive_user:${DB_PASSWORD}@db.prod.example.com/archive_db"
[logging]
level = "info"
format = "json"
file = ".codex/archive.log"
[retry]
enabled = true
max_attempts = 5
initial_delay = 2.0
max_delay = 64.0
[batch]
max_concurrent = 10
continue_on_error = true
[performance]
enable_metrics = true
EOT

# Create manifest for bulk restore
cat > disaster_recovery.json <<'EOT'
{
  "items": [
    {"tombstone": "uuid-1", "output": "/data/recovered/file1.txt"},
    {"tombstone": "uuid-2", "output": "/data/recovered/file2.txt"}
  ]
}
EOT

# Execute batch restore with retry
$ codex archive batch-restore disaster_recovery.json --by ops --continue-on-error
Processing 2 items...
Progress: 1/2 (50%)
Progress: 2/2 (100%)
Results saved to: batch_restore_20251017_132236.json

# Verify results
$ jq '.summary' batch_restore_20251017_132236.json
{
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "total_duration_ms": 1245.0
}
```

### Example 3: Debugging with Full Logging

```bash
# Enable debug logging to troubleshoot issues
$ CODEX_ARCHIVE_LOG_LEVEL=debug \
  codex archive restore problematic-uuid output.txt --by debug_user
[2025-10-17T13:22:36] DEBUG Backend validation: OK (postgres)
[2025-10-17T13:22:36] DEBUG Archive URL: postgres://... (credentials redacted)
[2025-10-17T13:22:36] DEBUG Retrieving restore payload for tombstone=...
[2025-10-17T13:22:36] DEBUG Decompression codec: zstd
[2025-10-17T13:22:36] DEBUG Decompression completed in 15.2ms
[2025-10-17T13:22:36] INFO Restore completed in 234.5ms
output.txt
```

---

## Troubleshooting

### Issue: Restore Hangs

**Symptoms**: Restore command appears frozen

**Solutions**:

1. Increase timeout in batch config: `timeout_per_item = 600`
2. Check database connectivity: `codex archive health-check`
3. Review logs: `tail -50 .codex/archive.log`

### Issue: High Restore Latency

**Symptoms**: Restores taking >1 second

**Solutions**:

1. Review performance metrics: `jq '.duration_ms' .codex/evidence/archive_ops.jsonl`
2. Check decompression overhead: Enable `track_decompression = true`
3. Consider database indexing if using PostgreSQL

### Issue: Batch Restore Partial Failures

**Symptoms**: Some items fail in batch operation

**Solutions**:

1. Review results file: `jq '.items[] | select(.status=="failed")' batch_results.json`
2. Retry individual items: `codex archive restore <tombstone> out.txt --by user`
3. Update manifest and retry: Remove succeeded items, retry failed ones

---

Copilot is powered by AI, so mistakes are possible. Leave a comment via the 👍 👎 to share your feedback and help improve the experience.
