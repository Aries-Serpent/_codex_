# AGENTS

Guidelines for contributors and Codex automation. Keep this file updated as conventions change.

## Environment Variables

- `CODEX_ENV_PYTHON_VERSION`, `CODEX_ENV_NODE_VERSION`, `CODEX_ENV_RUST_VERSION`, `CODEX_ENV_GO_VERSION`, `CODEX_ENV_SWIFT_VERSION` – select language versions during environment setup.
- `CODEX_SESSION_ID` – identifier for a logical session; group log events.
- `CODEX_SESSION_LOG_DIR` – directory for session log files (default: `.codex/sessions`).
- `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` – path to the SQLite database used by logging tools.
- `CODEX_SQLITE_POOL` – set to `1` to enable per-session SQLite connection pooling.

## Logging Roles

Use one of the following roles when recording conversation or session events: `system`, `user`, `assistant`, `tool`.

## Tooling & Testing

- Format with **Black**, lint with **Ruff**, sort imports with **isort**.
- Run type checks with **mypy** if changing Python modules.
- Before committing, run:

```bash
pre-commit run --files <changed_files>
nox -s tests
```

- Ensure optional test dependencies (e.g., `hydra-core`, `mlflow`) are installed or appropriately mocked.

## Useful Commands

- `python -m codex.logging.session_logger` – record session events.
- `python -m codex.logging.viewer` – view session logs.
- `python -m codex.logging.query_logs` – search conversation transcripts.

## Prohibited Actions

- Do **not** create or activate any GitHub Actions workflow files.
- Keep automation artefacts confined to `.codex/`.

## Log Directory & Retention

```
./.codex/
  session_logs.db
  sessions/<SESSION_ID>.ndjson
```

Retain logs for 30 days, then purge:

```
find ./.codex/sessions -type f -mtime +30 -print -delete || true
```

## Next Steps Toward Production Readiness

1. **Stabilize the test suite** – ensure all test dependencies (e.g., `hydra-core`, `mlflow`) are installed or mocked, and keep test module names unique to avoid import conflicts.
2. **Complete checkpoint resume functionality** – extend `run_hf_trainer` to load optimizer/scheduler state and verify resume logic with integration tests.
3. **Consolidate configuration management** – adopt Hydra consistently across training and CLI tools, and document configuration overrides for reproducibility.
4. **Expand safety and documentation** – flesh out `docs/safety.md` with concrete heuristics and red-team datasets. Add an architecture overview and examples to aid onboarding.
