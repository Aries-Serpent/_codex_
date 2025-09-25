# AGENTS — Guidelines for contributors and Codex automation

Keep this document updated as conventions evolve.

## Environment variables

| Variable | Purpose | Default / Notes |
|---|---|---|
| `CODEX_ENV_PYTHON_VERSION` | Select Python version for env setup | Provisioning only |
| `CODEX_ENV_NODE_VERSION` | Select Node.js version | Provisioning only |
| `CODEX_ENV_RUST_VERSION` | Select Rust version | Provisioning only |
| `CODEX_ENV_GO_VERSION` | Select Go version | Provisioning only |
| `CODEX_ENV_SWIFT_VERSION` | Select Swift version | Provisioning only |
| `CODEX_SESSION_ID` | Logical session identifier | UUID per session |
| `CODEX_SESSION_LOG_DIR` | Session logs directory | `.codex/sessions` |
| `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` | SQLite DB path for logs | `.codex/session_logs.db` |
| `CODEX_SQLITE_POOL` | Per-session SQLite connection pooling | `0` (disabled); set `1` to enable |

## Logging roles

| Role | Intended use |
|---|---|
| `system` | Orchestrator/system events |
| `user` | Human input/actions |
| `assistant` | Assistant/Codex output |
| `tool` | External tool events (e.g., git, mlflow) |

## Tooling & testing

- Format with **Black**, lint with **Ruff**, sort imports with **isort**.
- Run **mypy** on Python changes.
- Before committing, run:

```bash
pre-commit run --files <changed_files>
nox -s tests
```
- Optional deps (e.g., `hydra-core`, `mlflow`): install in a dedicated env or provide mocks.

## Prohibited actions

- **Do not** create or activate any GitHub Actions workflows.
- Keep automation artifacts confined to `.codex/`.

## Useful commands

```bash
python -m codex.logging.session_logger   # record session events
python -m codex.logging.viewer           # view session logs
python -m codex.logging.query_logs       # search transcripts
```