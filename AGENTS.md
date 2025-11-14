# AGENTS

Guidelines for contributors and Codex automation. Keep this file updated as conventions change.

> **Version**: 2.1.0 (Merged operational + dependency documentation)  
> **Generated**: 2025-11-14  
> **Authors**: mbaetiong, GitHub Copilot

## Table of Contents

- [Repository Overview](#repository-overview)
- [Environment Variables](#environment-variables)
- [Logging & Evidence Surfaces](#logging--evidence-surfaces)
- [Logging Roles](#logging-roles)
- [Dependency Retention & Segmentation](#dependency-retention--segmentation)
- [Tooling, Testing & Checks](#tooling-testing--checks)
- [CLI & Tool Usage](#cli--tool-usage)
- [Optional Dependencies & Mocking](#optional-dependencies--mocking)
- [Prohibited Actions & Scope](#prohibited-actions--scope)
- [Log Directory Layout & Retention](#log-directory-layout--retention)
- [Error Handling & Backward Compatibility](#error-handling--backward-compatibility)
- [Configuration Management (Hydra)](#configuration-management-hydra)
- [Production Readiness Checklist](#production-readiness-checklist)
- [Troubleshooting](#troubleshooting)
- [Contact / Maintainers](#contact--maintainers)

## Repository Overview

**Packaging**: Defined in `pyproject.toml`; install with `pip install -e .`

**Command-line tasks**: Live in `src/codex/cli.py` and can be invoked with:
```bash
python -m codex.cli <command>
```

**Project Structure**:
```
Aries-Serpent/_codex_/
├── .github/
│   ├── docs/              # Documentation
│   ├── scripts/           # CI/CD scripts
│   └── workflows/         # GitHub Actions (DO NOT CREATE/ACTIVATE)
├── src/
│   └── codex/
│       ├── cli.py         # Main CLI entry point
│       ├── config/        # Configuration management
│       ├── logging/       # Logging infrastructure
│       │   ├── session_logger.py
│       │   ├── viewer.py
│       │   └── query_logs.py
│       └── ...
├── configs/               # Hydra configuration files
├── pyproject.toml         # Package configuration
├── noxfile.py             # Test automation
└── .codex/
    ├── sessions/          # Session log files
    ├── logs/              # Error logs
    └── session_logs.db    # SQLite database
```

## Environment Variables

This repository uses environment variables prefixed with `CODEX_` for runtime configuration. All environment variables support validation and have sensible defaults.

| Variable | Default | Type | Description | Validation |
|----------|---------|------|-------------|------------|
| `CODEX_ENV_PYTHON_VERSION` | `3.12` | string | Python version for environment setup | Semantic version format |
| `CODEX_ENV_NODE_VERSION` | — | string | Node.js version (optional) | Semantic version format |
| `CODEX_ENV_RUST_VERSION` | — | string | Rust version (optional) | Semantic version format |
| `CODEX_ENV_GO_VERSION` | — | string | Go version (optional) | Semantic version format |
| `CODEX_ENV_SWIFT_VERSION` | — | string | Swift version (optional) | Semantic version format |
| `CODEX_SESSION_ID` | auto-generated UUID | string | Identifier for logical session; groups log events | UUID format |
| `CODEX_SESSION_LOG_DIR` | `.codex/sessions` | path | Directory for session log files | Must be writable |
| `CODEX_LOG_DB_PATH` | `.codex/session_logs.db` | path | Path to SQLite database for logs | Must be writable |
| `CODEX_DB_PATH` | `.codex/session_logs.db` | path | Alternative path to SQLite database | Must be writable |
| `CODEX_SQLITE_POOL` | `0` | boolean | Enable per-session SQLite connection pooling | `0` or `1` |
| `CODEX_FORCE_CPU` | `1` | boolean | Enforce CPU-only torch installation | `0` or `1` |
| `CODEX_CPU_MINIMAL` | `0` | boolean | Slim ML augmentation (lean subset) | `0` or `1` |
| `CODEX_VENDOR_PURGE` | `1` | boolean | Activate purge phase (uninstall vendor wheels) | `0` or `1` |
| `CODEX_ABORT_ON_GPU_PULL` | `0` | boolean | Hard fail if GPU wheels observed | `0` or `1` |
| `CODEX_DEPENDENCY_EVIDENCE_ENABLE` | `1` | boolean | Record dependency operations | `0` or `1` |
| `CODEX_COLLECT_COVERAGE` | `0` | boolean | Enable coverage collection in tests | `0` or `1` |

### Environment Variable Usage

```bash
# Set session ID for log correlation
export CODEX_SESSION_ID="session-$(date +%s)"

# Enable SQLite connection pooling
export CODEX_SQLITE_POOL=1

# Enable coverage collection
export CODEX_COLLECT_COVERAGE=1

# Validate current environment
python -m codex.cli validate-env
```

## Logging Roles

Session logging supports the following roles for categorizing log entries:

| Role | Purpose | Example Use Case | Required |
|------|---------|------------------|----------|
| `system` | System-level events and initialization | Session start/end, configuration changes | Core |
| `user` | User input and commands | CLI commands, user queries | Core |
| `assistant` | Agent responses and outputs | Generated responses, analysis results | Core |
| `tool` | Tool execution and results | External command output, API responses | Core |
| `INFO` | Informational messages | Progress updates, status messages | Extended |
| `WARN` | Warning messages | Non-fatal issues, deprecation notices | Extended |

### Logging Role Usage

```python
from codex.logging.session_logger import log_message

# Log a user message
log_message(session_id="my-session", role="user", message="Analyze this code")

# Log a tool execution
log_message(session_id="my-session", role="tool", message="Executed: pytest")

# Log a system event
log_message(session_id="my-session", role="system", message="Session initialized")
```

## Logging & Evidence Surfaces

The repository maintains structured evidence logs for audit and compliance purposes.

| Path | Purpose | Rotation | Notes |
|------|---------|----------|-------|
| `.codex/evidence/archive_ops.jsonl` | Archive & restore operations (tombstones) | Append-only; rotate quarterly | Dual-control purge approvals preserved |
| `.codex/evidence/dependency_ops.jsonl` | Dependency segmentation & vendor purge evidence | Append-only; rotate weekly if >1MB | Actions: TORCH_PREINSTALL, DEPENDENCY_VENDOR_SCAN, DEPENDENCY_VENDOR_PURGE, LOCK_PRUNE, MINIMAL_AUGMENT, TORCH_REINSTALL |
| `.codex/logs/*` | Script-level warnings/errors | Ad-hoc | Do not manually edit evidence JSONL lines |
| `.codex/cache/*` | Transient metrics (timings, hashes) | Recreatable | Safe to prune |

### Evidence JSON Schema (Dependency)

Each line is a JSON object (example):
```json
{
  "ts": "2025-11-12T16:25:09Z",
  "action": "DEPENDENCY_VENDOR_PURGE",
  "tool": "setup",
  "mode": "primary",
  "vendors": [],
  "purged_count": 6,
  "vendor_hash_before": "7e9f...",
  "vendor_hash_after": "",
  "vendor_list_before": "nvidia-cublas-cu12 nvidia-nvtx-cu12",
  "vendor_list_after": "",
  "lock_prune_action": "dryrun",
  "lock_prune_lines_removed": 14,
  "torch_version": "2.8.0+cpu",
  "note": "",
  "actor": "github-actions[bot]",
  "session_id": "S123-456"
}
```

Required keys: `ts`, `action`, `tool` (schema validation session: `nox -s evidence_check`).

## Dependency Retention & Segmentation

Guidelines for managing dependencies across test sessions.

| Family | Session | Removal Requires ADR | Evidence Source |
|--------|---------|----------------------|-----------------|
| torch | ml_tests | Yes | dependency_ops.jsonl |
| transformers/tokenizers/safetensors | ml_tests | No (if kept segmented) | dependency_ops.jsonl |
| accelerate / peft | ml_tests | No | dependency_ops.jsonl |
| eval metrics (lm-eval, rouge-score, sacrebleu, nltk) | eval_tests | No (CHANGELOG note if bulk removal) | dependency_ops.jsonl |
| scientific (scipy, scikit-learn, statsmodels, pandas) | eval_tests | Yes if baseline removal | dependency_ops.jsonl |
| jupyterlab / notebook / nbconvert / matplotlib | notebook_env | Yes if baseline integration proposed | dependency_ops.jsonl |
| nvidia-* / triton / torchtriton | purge automation | No (purge logs suffice) | dependency_ops.jsonl |
| mlflow / ray | dedicated feature session | Yes if dropped entirely | ADR + dependency_ops.jsonl |

**Policy**: Baseline `tests` session MUST NOT install heavy ML/eval stacks unless explicitly justified and documented.

For detailed dependency management procedures, see the backup documentation in `AGENTS.md.backup_20251114_035816`.

## Tooling, Testing & Checks

### Code Quality Tools

- **Formatter**: Black
- **Linter**: Ruff
- **Import Sorter**: isort
- **Type Checker**: mypy

### Pre-Commit Workflow

Before committing changes, run:

```bash
# Run pre-commit on changed files
pre-commit run --files <changed_files>

# Or run on all files
pre-commit run --all-files
```

### Testing Workflow

```bash
# Run all tests
nox -s tests

# Run ML tests
nox -s ml_tests

# Run evaluation tests
nox -s eval_tests

# Run tests with coverage
CODEX_COLLECT_COVERAGE=1 nox -s tests

# View coverage report locally
nox -s coverage-local
```

### Type Checking

If changing Python modules, run:

```bash
mypy src/codex
```

## CLI & Tool Usage

The Codex CLI provides commands for session management, logging, and environment validation.

### Session Logger

Record session events to the database:

```bash
# Log a user message
python -m codex.cli session-logger --role=user --message="Starting analysis"

# Log with specific session ID
python -m codex.cli session-logger \
  --session-id=my-session \
  --role=assistant \
  --message="Analysis complete"
```

### Log Viewer

View session logs in various formats:

```bash
# View latest session
python -m codex.cli viewer

# View specific session
python -m codex.cli viewer --session-id=abc123

# Output as JSON
python -m codex.cli viewer --format=json
```

### Query Logs

Search through conversation transcripts:

```bash
# Search for specific text
python -m codex.cli query-logs --search="error"

# Filter by role
python -m codex.cli query-logs --search="test" --role=tool

# Combined search
python -m codex.cli query-logs --search="coverage" --role=user
```

### Environment Validation

Validate and display current environment configuration:

```bash
# Validate environment
python -m codex.cli validate-env

# Output shows all CODEX_* variables and their values
```

## Optional Dependencies & Mocking

Some tests require optional dependencies that may not be installed in all environments. The test infrastructure handles this gracefully.

### Optional Dependencies

- **hydra-core**: Configuration management (Hydra)
- **mlflow**: Experiment tracking
- **ray**: Distributed computing
- **jupyter**: Notebook support

### Mocking Strategy

When optional dependencies are not available, tests use mocks:

```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_optional_deps():
    """Mock optional dependencies if not installed."""
    try:
        import mlflow
    except ImportError:
        mlflow = MagicMock()
        # Use mock in tests
    
    try:
        import hydra
    except ImportError:
        hydra = MagicMock()
        # Use mock in tests
```

### Installing Optional Dependencies

```bash
# Install ML dependencies
pip install -r requirements-ml-cpu.txt

# Install evaluation dependencies
pip install -r requirements-eval.txt

# Install notebook dependencies
pip install -r requirements-notebook.txt

# Install all development dependencies
pip install -e ".[dev]"
```

## Prohibited Actions & Scope

### Do NOT

- **Create or activate** any GitHub Actions workflow files
- **Modify** production workflows without ADR (Architecture Decision Record)
- **Store** secrets or credentials in code
- **Remove** working files or code unless absolutely necessary
- **Edit** evidence JSONL lines manually
- **Delete** log files without retention policy compliance
- **Disable** coverage gating without team approval

### Keep Confined

- Automation artifacts → `.codex/` directory only
- Log files → `.codex/logs/` and `.codex/sessions/`
- Evidence files → `.codex/evidence/`
- Temporary files → `/tmp/` or `.codex/cache/`

## Log Directory Layout & Retention

### Directory Structure

```
.codex/
├── sessions/              # Session-specific log files
│   └── session_*.log      # Rotated based on session ID
├── logs/                  # Application logs
│   ├── errors_*.log       # Daily error logs
│   └── implementation_*.log  # Implementation task logs
├── evidence/              # Audit trail
│   ├── archive_ops.jsonl  # Archive operations (append-only, quarterly rotation)
│   └── dependency_ops.jsonl  # Dependency operations (append-only, weekly rotation if >1MB)
├── cache/                 # Transient metrics (safe to prune)
└── session_logs.db        # SQLite database
```

### Retention Policy

| Path | Rotation | Retention | Notes |
|------|----------|-----------|-------|
| `.codex/evidence/*.jsonl` | Quarterly / 1MB | Permanent | ADR required for deletion |
| `.codex/logs/errors_*.log` | Daily | 30 days | Compress after 7 days |
| `.codex/sessions/*.log` | Per session | 14 days | Auto-cleanup on session end |
| `.codex/cache/*` | N/A | Recreatable | Safe to delete |
| `.codex/session_logs.db` | N/A | Permanent | Backup before schema changes |

### Manual Cleanup

```bash
# Compress old logs
find .codex/logs -name "*.log" -mtime +7 -exec gzip {} \;

# Remove old session logs
find .codex/sessions -name "*.log" -mtime +14 -delete

# Clear cache
rm -rf .codex/cache/*
```

## Error Handling & Backward Compatibility

### Error Logging Framework

All errors are logged to `.codex/logs/` with:
- Timestamp
- Error type and message
- Full traceback
- Context (function, arguments, environment)

### Using the Error Handler

```python
from codex.logging.error_handler import error_handler

# Decorator usage
@error_handler.log_errors
def risky_function():
    # Your code here
    pass

# Direct logging
try:
    # Some operation
    pass
except Exception as e:
    error_handler.log_error(
        e,
        context={'operation': 'data_processing'},
        fatal=False  # Set to True to exit after logging
    )
```

### Graceful Degradation

When components fail:
1. Log error with full context
2. Print user-friendly message to stderr
3. Continue with remaining tasks (if possible)
4. Exit with non-zero code if critical failure

### Backward Compatibility Guidelines

- Maintain existing environment variable names
- Support legacy configuration formats
- Provide migration helpers for schema changes
- Document breaking changes in CHANGELOG

## Configuration Management (Hydra)

Hydra is used for hierarchical configuration management.

### Configuration Files

Located in `configs/` directory:
```
configs/
├── config.yaml          # Main configuration
├── db/
│   ├── sqlite.yaml
│   └── postgres.yaml
└── logging/
    ├── debug.yaml
    └── production.yaml
```

### Using Hydra Configurations

```python
import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    # Access configuration
    db_path = cfg.db.path
    log_level = cfg.logging.level
```

### Override Configuration

```bash
# Override via command line
python script.py db.path=.codex/custom.db logging.level=DEBUG

# Override via environment
HYDRA_FULL_ERROR=1 python script.py
```

## Production Readiness Checklist

Before deploying or merging major changes:

- [ ] All tests pass: `nox -s tests`
- [ ] Coverage ≥ 85%: `CODEX_COLLECT_COVERAGE=1 nox -s tests`
- [ ] No linting errors: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/codex`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Environment validation passes: `python -m codex.cli validate-env`
- [ ] Evidence logs reviewed (if applicable)
- [ ] Security scan complete (if dependency changes)
- [ ] ADR created (if architectural change)

## Troubleshooting

### Common Issues

#### Issue: Session logs not being created

**Symptoms**: No files in `.codex/sessions/`, database empty

**Solutions**:
1. Check `CODEX_SESSION_LOG_DIR` is writable
2. Verify `CODEX_LOG_DB_PATH` is accessible
3. Check SQLite database permissions
4. Review logs in `.codex/logs/errors_*.log`

```bash
# Verify directory permissions
ls -la .codex/
mkdir -p .codex/sessions .codex/logs

# Test database connectivity
python -c "import sqlite3; sqlite3.connect('.codex/session_logs.db').close()"
```

#### Issue: Tests failing with import errors

**Symptoms**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
1. Install development dependencies: `pip install -e ".[dev]"`
2. Check Python version: `python --version` (should be 3.10+)
3. Verify virtual environment is activated
4. Clear pytest cache: `rm -rf .pytest_cache`

```bash
# Reinstall in development mode
pip install -e ".[dev]"

# Verify installation
python -c "import codex; print(codex.__version__)"
```

#### Issue: Coverage below threshold

**Symptoms**: CI fails with coverage error

**Solutions**:
1. Run coverage locally: `CODEX_COLLECT_COVERAGE=1 nox -s tests`
2. View HTML report: `open artifacts/htmlcov/index.html`
3. Add tests for uncovered lines
4. Check for test markers: `pytest --markers`

```bash
# View coverage report
CODEX_COLLECT_COVERAGE=1 nox -s tests
python -m http.server -d artifacts/htmlcov 8000
# Open http://localhost:8000 in browser
```

#### Issue: Pre-commit hooks failing

**Symptoms**: `pre-commit run` fails with errors

**Solutions**:
1. Update hooks: `pre-commit autoupdate`
2. Clear cache: `pre-commit clean`
3. Reinstall hooks: `pre-commit install --install-hooks`
4. Run specific hook: `pre-commit run <hook-id> --all-files`

```bash
# Fix common issues
pre-commit clean
pre-commit install --install-hooks
pre-commit run --all-files
```

#### Issue: Environment variables not recognized

**Symptoms**: Defaults used instead of set values

**Solutions**:
1. Export variables: `export CODEX_SESSION_ID=abc123`
2. Check variable names (must start with `CODEX_`)
3. Verify no typos in variable names
4. Use validate-env: `python -m codex.cli validate-env`

```bash
# Debug environment
env | grep CODEX_

# Validate configuration
python -m codex.cli validate-env
```

### Getting Help

| Issue Type | Resource | Response Time |
|------------|----------|---------------|
| Bug reports | GitHub Issues | 1-2 business days |
| Feature requests | GitHub Discussions | 3-5 business days |
| Security issues | Security Policy (SECURITY.md) | 24 hours |
| Documentation | README.md, CONTRIBUTING.md | N/A |

## Contact / Maintainers

### Primary Contacts

| Role | Contact | Responsibilities |
|------|---------|-----------------|
| Platform Lead | @mbaetiong | Infrastructure, CI/CD, Architecture |
| QA Integration | @platform-qa | Testing, Quality Gates, Evidence |
| Security | SECURITY.md | Vulnerability reporting |

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, community support
- **Pull Requests**: Code contributions, documentation updates

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Change Control

All structural changes require:
- **ADR** (Architecture Decision Record) for scope expansions, OR
- **CHANGELOG entry** for non-breaking adjustments

ADRs are stored in `docs/arch/` directory.

---

## Attribution

**Generated**: 2025-11-14  
**Primary Author**: mbaetiong  
**Version**: 2.0 (Enhanced with comprehensive documentation)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2025-11-14 | Enhanced with comprehensive documentation, environment variables, logging infrastructure |
| 1.0 | 2025-11-12 | Initial version with dependency segmentation documentation |

---

*End of AGENTS.md*
