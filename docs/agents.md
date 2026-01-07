# AGENTS — Guidelines for contributors and Codex automation

> **Version**: 2.1.0  
> **Updated**: 2025-12-16  
> **CI/CD Status**: ✅ Fully Operational

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
- Coverage gates target **`src/codex_ml`**; run `pytest --cov=src/codex_ml --cov-fail-under=3.5` when checking locally.
- Optional deps (e.g., `hydra-core`, `mlflow`): install in a dedicated env or provide mocks.

## CI/CD Workflows

As of Previous Cycle-12-16:
- **45 active workflows** (all passing YAML validation)
- **GitHub Pages**: Enabled with MkDocs (`pages-mkdocs.yml`)
- **Key workflows**:
  - `test-suite.yml` - Main test runner
  - `optimized-ci.yml` - Optimized CI with pytest-split
  - `security-suite.yml` - Security scanning
  - `api-documentation.yml` - API docs generation
  - `pages-mkdocs.yml` - Documentation deployment

## Copilot Task Execution Protocol (CTEP)

Activate comprehensive task completion mode with:
- `Enable CTEP` or `CTEP Mode: ON` or `Task mode: ON`

See `.github/docs/Copilot_Task_Execution_Protocol.md` for full specification.

## Prohibited actions

- **Do not** create or activate any GitHub Actions workflows without proper review.
- Keep automation artifacts confined to `.codex/`.
  - Evidence (plan/apply) is written to `.codex/evidence/` as JSONL for auditability.

## Useful commands

```python
# example: minimal agent
def run_agent(task: str) -> str:
    return f"ok: {task}"
```

Local checks before commit:
```bash
pre-commit run --all-files
# Deterministic tests; ML suites are optionally skipped if torch isn't installed.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

> Tip: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` disables 3rd-party plugin auto-loading for deterministic test runs in minimal environments.

## Config composition & overrides

You can inspect the composed defaults and override at the CLI:

```bash
python -m codex_ml.cli.config --info defaults   # show defaults list
python -m codex_ml.cli.config trainer.seed=123 trainer.deterministic=true logging.format=ndjson
```

See Hydra's docs for background on defaults lists and composition order.

## Related Documentation

- [Main AGENTS.md](../AGENTS.md) - Comprehensive operations playbook
- [CTEP Protocol](/.github/docs/Copilot_Task_Execution_Protocol.md) - Task execution protocol
- [CHANGELOG](CHANGELOG.md) - Version history
