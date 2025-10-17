# Architecture Decision Record: Archive Configuration Management

> Generated: 2025-10-17 13:22:36 | Author: mbaetiong | Type: Enhancement Implementation

## Status

✅ **IMPLEMENTED** - Configuration management with TOML file support, environment variable fallback, and multi-backend support

---

## Problem Statement

Archive backend configuration was managed solely through environment variables (`CODEX_ARCHIVE_URL`, `CODEX_ARCHIVE_BACKEND`), which:

- Limited flexibility for multi-environment deployments
- Required setting multiple env vars for complex configurations (retry, logging, batch settings)
- Lacked schema validation and clear error messages
- Made it difficult to version control safely (credentials in env vars)

## Decision

Implement hierarchical configuration loading with precedence:

1. **Explicit file** (if provided via CLI/API)
2. **Default location** (`.codex/archive.toml`)
3. **Environment variables** (backward compatible)
4. **Safe defaults** (hardcoded fallbacks)

## Configuration Schema

### Backend Configuration

```toml
[backend]
type = "sqlite"  # sqlite | postgres | mariadb
url = "sqlite:///./.codex/archive.sqlite"
```

### Logging Configuration

```toml
[logging]
level = "info"  # debug | info | warn | error
format = "json"  # json | text
file = ".codex/archive.log"  # optional
```

### Retry Configuration

```toml
[retry]
enabled = false
max_attempts = 3
initial_delay = 1.0  # seconds
max_delay = 32.0
backoff_factor = 2.0
jitter = true
```

### Batch Configuration

```toml
[batch]
max_concurrent = 5
timeout_per_item = 300  # seconds
continue_on_error = false
```

### Performance Configuration

```toml
[performance]
enable_metrics = true
track_decompression = true
```

## Implementation Details

### Config Loader (`src/codex/archive/config.py`)

**Key Classes:**

- `ArchiveConfig` - Main configuration container
- `BackendConfig` - Backend-specific settings
- `LoggingConfig` - Logging parameters
- `RetryConfig` - Retry/backoff parameters
- `BatchConfig` - Batch operation parameters
- `PerformanceConfig` - Performance tracking settings

**Loading Methods:**

- `ArchiveConfig.from_env()` - Load from environment variables
- `ArchiveConfig.from_file(path)` - Load from TOML file
- `ArchiveConfig.load(config_file=None)` - Smart loader with precedence

### Environment Variable Precedence

All config sections have env var equivalents:

| Config Key | Environment Variable | Default |
|------------|----------------------|---------|
| `backend.type` | `CODEX_ARCHIVE_BACKEND` | `sqlite` |
| `backend.url` | `CODEX_ARCHIVE_URL` | `sqlite:///./.codex/archive.sqlite` |
| `logging.level` | `CODEX_ARCHIVE_LOG_LEVEL` | `info` |
| `logging.format` | `CODEX_ARCHIVE_LOG_FORMAT` | `json` |
| `retry.enabled` | `CODEX_ARCHIVE_RETRY_ENABLED` | `false` |
| `retry.max_attempts` | `CODEX_ARCHIVE_RETRY_MAX` | `3` |
| `retry.initial_delay` | `CODEX_ARCHIVE_RETRY_INITIAL` | `1.0` |
| `batch.max_concurrent` | `CODEX_ARCHIVE_BATCH_CONCURRENT` | `5` |
| `performance.enable_metrics` | `CODEX_ARCHIVE_PERF_ENABLED` | `true` |

## Benefits

✅ **Multi-environment Support** - Different configs per environment
✅ **Version Control Safe** - Config files can be committed (without credentials)
✅ **Backward Compatible** - Existing env vars still work
✅ **Schema Validation** - Dataclasses ensure type correctness
✅ **Clear Defaults** - Sensible fallbacks for all options
✅ **Credential Redaction** - URLs sanitized in logs/CLI output

## Testing Strategy

### Unit Tests (`tests/archive/test_config.py`)

- ✅ `test_from_env_defaults` - Env var loading with defaults
- ✅ `test_from_env_custom_values` - Env var override
- ✅ `test_from_file_valid` - TOML file loading
- ✅ `test_from_file_not_found` - Error handling
- ✅ `test_load_file_precedence` - File > env var > defaults
- ✅ `test_backend_type_valid` - Enum validation
- ✅ `test_to_dict` - Config serialization

### CLI Integration

```bash
# Show current configuration
$ codex archive config-show
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite (credentials redacted)
Log Level: info
Retry: disabled
Batch Concurrency: 5

# Show with debug (full URLs)
$ codex archive config-show --debug
Backend: sqlite
URL: sqlite:///./.codex/archive.sqlite
...
```

## Migration Path

### For Existing Deployments

**Option 1: Continue with env vars** (no change)

```bash
export CODEX_ARCHIVE_BACKEND=postgres
export CODEX_ARCHIVE_URL=postgres://host/db
# Config system auto-detects and uses env vars
```

**Option 2: Adopt TOML config file** (recommended)

```bash
# Create .codex/archive.toml
mkdir -p .codex
cat > .codex/archive.toml <<'EOF'
[backend]
type = "postgres"
url = "postgres://host/db"
[retry]
enabled = true
max_attempts = 5
EOF
# Env vars can still override
export CODEX_ARCHIVE_LOG_LEVEL=debug
```
