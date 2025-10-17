# Architecture Decision Record: Archive Configuration Management
> Generated: 2024-05-29 00:00:00 | Author: mbaetiong | Type: Enhancement Implementation

## Status
✅ **IMPLEMENTED** – Configuration management with TOML file support, environment variable fallback, and multi-backend support.

---

## Problem Statement
Archive backend configuration was previously managed solely through environment variables (`CODEX_ARCHIVE_URL`, `CODEX_ARCHIVE_BACKEND`). This approach:

* Limited flexibility across environments (local, staging, production).
* Required setting many environment variables for related features (logging, retry, batch operations).
* Provided minimal validation or discoverability of supported options.
* Made it harder to version-control safe defaults.

## Decision
Implement hierarchical configuration loading with a clear precedence order:

1. **Explicit file** – if `ArchiveConfig.load(config_file=...)` is called.
2. **Default file** – `.codex/archive.toml` in the working directory.
3. **Environment variables** – backwards compatible with previous behaviour.
4. **Code defaults** – frozen dataclass defaults.

## Configuration Schema
All sections are defined via frozen dataclasses in `codex.archive.config`.

### Backend Configuration
```toml
[backend]
type = "sqlite"  # sqlite | postgres | mariadb
url = "sqlite:///./.codex/archive.sqlite"
```

### Logging Configuration
```toml
[logging]
level = "info"   # debug | info | warn | error
format = "json"  # json | text
file = ".codex/archive.log"  # optional
```

### Retry Configuration
```toml
[retry]
enabled = false
max_attempts = 3
initial_delay = 1.0
max_delay = 32.0
backoff_factor = 2.0
jitter = true
```

### Batch Configuration
```toml
[batch]
max_concurrent = 5
timeout_per_item = 300
continue_on_error = false
```

### Performance Configuration
```toml
[performance]
enable_metrics = true
track_decompression = true
```

## Implementation Details
* `ArchiveConfig` (and supporting dataclasses) live in `src/codex/archive/config.py`.
* Loader helpers: `from_env`, `from_file`, and `load` implement the precedence rules.
* `ArchiveService` now accepts a `settings` object; it derives the backend runtime config (`ArchiveBackendConfig`) internally.
* CLI command `codex archive config-show` prints the effective configuration with optional redaction for connection URLs.

## Environment Variable Mapping
| Config key | Environment variable | Default |
|------------|----------------------|---------|
| `backend.type` | `CODEX_ARCHIVE_BACKEND` | `sqlite` |
| `backend.url` | `CODEX_ARCHIVE_URL` | `sqlite:///./.codex/archive.sqlite` |
| `logging.level` | `CODEX_ARCHIVE_LOG_LEVEL` | `info` |
| `logging.format` | `CODEX_ARCHIVE_LOG_FORMAT` | `json` |
| `logging.file` | `CODEX_ARCHIVE_LOG_FILE` | `None` |
| `retry.enabled` | `CODEX_ARCHIVE_RETRY_ENABLED` | `false` |
| `retry.max_attempts` | `CODEX_ARCHIVE_RETRY_MAX` | `3` |
| `retry.initial_delay` | `CODEX_ARCHIVE_RETRY_INITIAL` | `1.0` |
| `retry.max_delay` | `CODEX_ARCHIVE_RETRY_MAX_DELAY` | `32.0` |
| `retry.backoff_factor` | `CODEX_ARCHIVE_RETRY_BACKOFF` | `2.0` |
| `retry.jitter` | `CODEX_ARCHIVE_RETRY_JITTER` | `true` |
| `batch.max_concurrent` | `CODEX_ARCHIVE_BATCH_CONCURRENT` | `5` |
| `batch.timeout_per_item` | `CODEX_ARCHIVE_BATCH_TIMEOUT` | `300` |
| `batch.continue_on_error` | `CODEX_ARCHIVE_BATCH_CONTINUE` | `false` |
| `performance.enable_metrics` | `CODEX_ARCHIVE_PERF_ENABLED` | `true` |
| `performance.track_decompression` | `CODEX_ARCHIVE_PERF_DECOMP` | `true` |

## Benefits
* ✅ **Multi-environment support** – consistent structure for local/staging/production.
* ✅ **Version-control friendly** – shareable TOML with optional env override for secrets.
* ✅ **Backwards compatible** – environment-only deployments keep working.
* ✅ **Discoverability** – documented schema and CLI inspection.

## Testing Strategy
* Unit tests in `tests/archive/test_config.py` cover environment parsing, TOML loading, precedence, and serialisation.
* Integration tests in `tests/archive/test_improvements_integration.py` verify that the service honours TOML overrides.
* CLI smoke test via `codex archive config-show` demonstrates redacted output and debug flag behaviour.

## Migration Guidance
1. **Keep env vars** – no action required; defaults align with existing behaviour.
2. **Adopt TOML configuration**:
   ```bash
   mkdir -p .codex
   cat > .codex/archive.toml <<'CFG'
   [backend]
   type = "postgres"
   url = "postgres://user:pass@db/archive"

   [retry]
   enabled = true
   max_attempts = 5
   CFG
   ```
3. **Combine** – use TOML for defaults, override with env vars for temporary changes.

## Future Enhancements
* Hot-reload support for long-lived daemons.
* Validation hooks for unsupported backend types before runtime.
* Optional integration with secret stores (AWS Secrets Manager, Vault) for sensitive URLs.

## References
* Implementation: `src/codex/archive/config.py`
* Backend integration: `src/codex/archive/backend.py`
* Service wiring: `src/codex/archive/service.py`
* Tests: `tests/archive/test_config.py`, `tests/archive/test_improvements_integration.py`
