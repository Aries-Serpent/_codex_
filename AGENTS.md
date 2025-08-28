# AGENTS

This document provides guidelines for contributors and automated agents working in this repository. Update it as conventions evolve.

## Environment variables

These variables control runtime configuration and logging:

- `CODEX_ENV_PYTHON_VERSION`, `CODEX_ENV_NODE_VERSION`, `CODEX_ENV_RUST_VERSION`, `CODEX_ENV_GO_VERSION`, `CODEX_ENV_SWIFT_VERSION` – select language versions during environment setup.
- `CODEX_SESSION_ID` – identifier for a logical session. Set to group log events.
- `CODEX_SESSION_LOG_DIR` – directory for session log files (defaults to `.codex/sessions`).
- `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` – path to the SQLite database used by logging tools.
- `CODEX_SQLITE_POOL` – set to `1` to enable per-session SQLite connection pooling.

## Logging roles

Logging utilities expect roles from the set:

- `system`
- `user`
- `assistant`
- `tool`

Use these when recording conversation or session events.

## Testing expectations

Before committing, run all checks locally:

```bash
pre-commit run --all-files
pytest
```

## Tool usage

Common CLI entry points provided by this repository:

- `python -m codex.logging.session_logger` – record session events.
- `python -m codex.logging.viewer` – view session logs.
- `python -m codex.logging.query_logs` – search conversation transcripts.

Keep this document updated as conventions evolve.

______________________________________________________________________

# AGENTS.md — Maintainers & Automation Guide

## Scope & Non-Goals

- **DO NOT ACTIVATE ANY GitHub Actions files.** This document is discoverable by automation and humans.
- Changes are restricted to documentation and `.codex/*` outputs.

## Logging Environment

- `CODEX_SESSION_ID`: unique session identifier (UUID/GUID).
- `CODEX_LOG_DB_PATH`: path to SQLite/NDJSON logs (default: `.codex/session_logs.db`).
- NDJSON session traces: `.codex/sessions/<SESSION_ID>.ndjson`
- Logs are retained for 30 days; purge older logs to satisfy enterprise retention policy.

## Required Tools

- Core: black, mypy, pre-commit, pytest, ruff
- Install hooks:
  ```bash
  pip install pre-commit && pre-commit install
  pre-commit run --all-files
  ```
- Test locally:
  ```bash
  pytest -q
  ```

## Coding Standards (summary)

- Python: format with Black, lint with Ruff, imports with isort (if configured).
- Type checking: run `mypy` using the configuration in `pyproject.toml` (or `pyright` as configured).
- Respect repository conventions noted in README and CONTRIBUTING (if present).

## CI Reference (read-only)

- Continuous Integration runs `pre-commit run --all-files` and `pytest` on PRs/commits.
- See the workflow definition under `.github/workflows/ci.yml` (do **not** modify or activate).

### Log Directory Layout & Retention

Structure:
./.codex/
session_logs.db
sessions/
\<SESSION_ID>.ndjson

Retention:
Keep NDJSON files and SQLite rows for 30 days. Purge anything older.

Symbolic policy:
purge(file) = 1 if age_days(file) > 30 else 0

POSIX purge example:
find ./.codex/sessions -type f -mtime +30 -print -delete || true

PowerShell purge example:
Get-ChildItem ..codex\\sessions -File | Where-Object { $\_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force
