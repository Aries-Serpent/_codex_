# AGENTS

Guidelines for contributors and automated agents working in this repository. Keep this document updated as conventions evolve.

## Repository Notes
- Packaging is defined in `pyproject.toml`; install with `pip install -e .`.
- Command-line tasks live in `src/codex/cli.py` and can be invoked with `python -m codex.cli <task>`.
- Base configuration files are stored under `configs/` and are Hydra-compatible.

## Environment Variables
These control runtime configuration and logging:
- `CODEX_ENV_PYTHON_VERSION`, `CODEX_ENV_NODE_VERSION`, `CODEX_ENV_RUST_VERSION`, `CODEX_ENV_GO_VERSION`, `CODEX_ENV_SWIFT_VERSION` – select language versions during environment setup.
- `CODEX_SESSION_ID` – identifier for a logical session. Set to group log events.
- `CODEX_SESSION_LOG_DIR` – directory for session log files (defaults to `.codex/sessions`).
- `CODEX_LOG_DB_PATH` / `CODEX_DB_PATH` – path to the SQLite database used by logging tools.
- `CODEX_SQLITE_POOL` – set to `1` to enable per-session SQLite connection pooling.

## Logging Roles
Logging utilities expect roles from the set:
- `system`
- `user`
- `assistant`
- `tool`

Use these when recording conversation or session events.

## Testing & Checks
Run all checks locally before committing:
```bash
pre-commit run --all-files
pytest
```
(You may also use `nox -s tests` which wraps pytest with coverage.)

## Tool Usage
Common CLI entry points provided by this repository:
- `python -m codex.logging.session_logger` – record session events.
- `python -m codex.logging.viewer` – view session logs.
- `python -m codex.logging.query_logs` – search conversation transcripts.

## Coding Standards
- Format Python code with Black.
- Lint with Ruff and manage imports with isort (if configured).
- Run type checking via `mypy` using settings in `pyproject.toml`.
- Respect repository conventions noted in README and CONTRIBUTING.

## Scope & Non-Goals
- **Do NOT activate or introduce any GitHub Actions workflows.**
- Changes are limited to documentation and `.codex/*` outputs unless otherwise specified.

## Log Directory Layout & Retention
Structure:
```
./.codex/
  session_logs.db
  sessions/<SESSION_ID>.ndjson
```
Retention policy: keep NDJSON files and SQLite rows for 30 days; purge older logs.

## Next Steps Toward Production Readiness
1. **Stabilize the test suite**
   - Ensure all test dependencies (`hydra-core`, `mlflow`, etc.) are installed or mocked.
   - Resolve the duplicate test module and fix import paths.
2. **Complete checkpoint resume functionality**
   - Extend `run_hf_trainer` to load optimizer/scheduler state.
   - Verify resume logic with integration tests.
3. **Consolidate configuration management**
   - Adopt Hydra consistently across training and CLI tools.
   - Document configuration overrides for reproducibility.
4. **Expand safety and documentation**
   - Flesh out `docs/safety.md` with concrete heuristics and red-team datasets.
   - Add an architecture overview and examples to aid onboarding.

Addressing these items will close remaining gaps between the current codebase and production-ready standards.
