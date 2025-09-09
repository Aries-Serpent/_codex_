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

This document collects the repository conventions, runtime configuration, testing commands, and operational constraints for contributors and automated agents (Codex automation) in the Aries-Serpent/_codex_ repository. Keep this file updated as conventions evolve.

Table of contents
- Repository overview
- Environment variables (table)
- Logging roles (table)
- Tooling, testing & checks
- CLI & tool usage
- Optional/third-party test dependencies and mocking guidance
- Prohibited actions & scope
- Log directory layout & retention
- Error handling & backward compatibility guidance
- Configuration management (Hydra)
- Next steps toward production readiness
- Troubleshooting checklist
- Contact / maintainers

Repository overview
- Packaging: defined in pyproject.toml; install with pip install -e .
- Command-line tasks live in src/codex/cli.py and can be invoked with python -m codex.cli <task>.
- Base configuration files are stored under configs/ and are Hydra-compatible.

Environment variables
This table lists environment variables used to control runtime configuration and logging. Where sensible, defaults are indicated and guidance for safe values is provided.

| Variable | Purpose | Default / Notes |
|---|---|---|
| CODEX_ENV_PYTHON_VERSION | Select Python version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_NODE_VERSION | Select Node.js version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_RUST_VERSION | Select Rust version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_GO_VERSION | Select Go version for environment setup | Used by environment provisioning tools |
| CODEX_ENV_SWIFT_VERSION | Select Swift version for environment setup | Used by environment provisioning tools |
| CODEX_SESSION_ID | Identifier for a logical session; groups log events | Generate per session (UUID recommended) |
| CODEX_SESSION_LOG_DIR | Directory for session log files | .codex/sessions |
| CODEX_LOG_DB_PATH / CODEX_DB_PATH | Path to the SQLite DB used by logging tools | .codex/session_logs.db |
| CODEX_SQLITE_POOL | Enable per-session SQLite connection pooling | 0 (disabled). Set to 1 to enable |

Logging roles
Logging utilities and session recorders expect a consistent set of roles. Use these roles when recording conversation or session events.

| Role | Intended use |
|---|---|
| system | System-generated events, orchestration, internal state changes |
| user | End-user messages or human agent actions |
| assistant | Generated assistant responses (Codex/agent) |
| tool | Events produced by external tools or integrations (e.g., git, mlflow) |

Tooling, testing & checks
Run all checks locally before committing. The repository uses common Python tooling; adhere to the configuration in pyproject.toml.

Recommended local checks:
```bash
# Run pre-commit hooks for changed files
pre-commit run --files <changed_files>

# Run the test suite (nox runs pytest with coverage)
nox -s tests
```

Formatting & static checks
- Format Python code with Black.
- Lint with Ruff.
- Sort imports with isort (if configured).
- Run type checks with mypy when changing Python modules.

CLI & tool usage
Common CLI entry points provided by this repository:
- python -m codex.logging.session_logger — record session events
- python -m codex.logging.viewer — view session logs
- python -m codex.logging.query_logs — search conversation transcripts
- python -m codex.cli <task> — run repository CLI tasks

When writing new CLI tasks:
- Follow existing patterns in src/codex/cli.py.
- Register argument parsing and Hydra-compatible configuration where applicable.
- Provide clear help strings and exit codes.

Optional / third-party test dependencies and mocking guidance
Some tests require optional third-party packages (for example, hydra-core, mlflow). To avoid fragile tests in CI or local runs, adopt one of these approaches:
- Install optional test dependencies in a dedicated test environment:
  pip install -r requirements-tests-optional.txt
- Prefer explicit mocks for services like mlflow or heavy integrations. Example: use pytest-mock or monkeypatch to replace mlflow imports or functions when the dependency is not available.
- Keep test module names unique to avoid import conflicts. If you add tests that use the same module names in different directories, make them unique (e.g., tests/test_mlflow_integration.py -> tests/test_mlflow_integration_unique.py).

Prohibited actions & scope
- Do NOT create or activate any GitHub Actions workflow files.
- Keep automation artifacts confined to the .codex/ directory unless a change is explicitly approved.
- Repository changes are limited to documentation and .codex/* outputs unless otherwise specified by maintainers.
- Respect repository conventions noted in README and CONTRIBUTING.

Log directory layout & retention
Structure:
```
./.codex/
  session_logs.db
  sessions/<SESSION_ID>.ndjson
```

Retention policy
- Retain NDJSON files and SQLite rows for 30 days. Purge older logs using (safe, best-effort):
```bash
# Purge session files older than 30 days (best-effort)
find ./.codex/sessions -type f -mtime +30 -print -delete || true

# Optionally vacuum the SQLite DB after purging rows (use with care)
# sqlite3 .codex/session_logs.db "VACUUM;"
```

Error handling & backward compatibility guidance
This repository must be resilient when optional dependencies or environment differences exist.

General patterns
- Fail fast with clear, actionable error messages when a critical configuration is missing.
- Provide safe fallbacks (no-op or mocked implementations) for optional integrations (e.g., mlflow, hydra-core). Prefer explicit runtime detection:
  - Try to import optional libraries and set a boolean flag (HAS_MLFLOW). If missing, log a warning and use a stub adapter for tests or runtime.
- Where configuration files are missing, provide helpful suggestions and exit codes, e.g., return non-zero with printed guidance.

Example Python pattern (guidance, not a code insertion):
```python
try:
    import mlflow
    HAS_MLFLOW = True
except Exception:
    HAS_MLFLOW = False
    logger.warning("mlflow is not available; mlflow integration disabled.")
```
- When invoking external tooling that may fail (e.g., database writes), wrap calls with retries and custom exceptions. Maintain idempotency where appropriate.

Backward compatibility
- When changing configuration keys or CLI flags, accept legacy keys/flags for at least one release cycle and emit a deprecation warning with migration instructions.
- Keep stable output formats (NDJSON, SQLite schema) backward compatible; version the schema when incompatible changes are required and provide migration scripts.

Configuration management (Hydra)
- Base configuration files live in configs/ and are Hydra-compatible.
- When adding new Hydra configs, document overrides and example commands to reproduce runs. Example:
```bash
python -m codex.cli train --config-name=my_config hydra.run.dir=./runs/my_run
```

Next steps toward production readiness
1. Stabilize the test suite
   - Ensure optional test dependencies (hydra-core, mlflow, etc.) are installed in test environments or suitably mocked.
   - Resolve duplicate test module names and fix import path issues.
2. Complete checkpoint resume functionality
   - Extend run_hf_trainer to load optimizer/scheduler state and verify resume logic with integration tests.
3. Consolidate configuration management
   - Adopt Hydra consistently across training and CLI tools.
   - Document configuration overrides for reproducibility (examples and recommended patterns).
4. Expand safety and documentation
   - Flesh out docs/safety.md with concrete heuristics and red-team datasets.
   - Add an architecture overview and examples to aid onboarding.
5. Logging & observability improvements
   - Add structured logging schemas for session events and schema versioning.
   - Provide a small helper to migrate older session logs if schema changes are introduced.

Troubleshooting checklist (quick)
- Tests failing due to missing optional deps: either install them in the test env or mock them in tests.
- Session logs not found: verify CODEX_SESSION_LOG_DIR and CODEX_SESSION_ID values.
- CLI tasks failing with Hydra errors: ensure configs/ contain the requested config-name and hydra-core is available.
- Database lock errors on SQLite: consider CODEX_SQLITE_POOL usage or use per-session DB files; add retries and short backoff.

Contact / maintainers
- For repository-specific policy changes, open an issue in Aries-Serpent/_codex_ and tag maintainers.
- For urgent security or data-leak concerns, follow the repository escalation path documented in CONTRIBUTING or contact maintainers directly.

End of document.
