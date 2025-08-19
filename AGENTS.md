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
