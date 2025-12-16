# AGENTS — Guidelines for contributors and Codex automation

> **Version**: 2.1.0  
> **Updated**: 2025-12-16  
> **CI/CD Status**: ✅ Fully Operational (45/45 workflows)

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
- **Integration tests**: Use `-m "not integration"` to exclude integration tests for faster local test runs:
  ```bash
  pytest -m "not integration"
  ```

## CI/CD Workflows (Updated 2025-12-16)

The repository has **45 active workflows** with 100% YAML validation passing:

| Category | Key Workflows |
|----------|---------------|
| Testing | `test-suite.yml`, `optimized-ci.yml`, `nox_gates.yml` |
| Security | `security-suite.yml`, `scheduled-dependency-audit.yml` |
| Documentation | `api-documentation.yml`, `pages-mkdocs.yml`, `docs.yml` |
| Deployment | `pre-release-deployment.yml`, `container-build.yml` |
| Automation | `self-healing-feedback-loop.yml`, `workflow-validator.yml` |

## Copilot Task Execution Protocol (CTEP)

For comprehensive task completion, activate CTEP mode:

**Activation commands:**
- `Enable CTEP`
- `CTEP Mode: ON`
- `Task mode: ON`

**Deactivation commands:**
- `Disable CTEP`
- `CTEP Mode: OFF`

See `.github/docs/Copilot_Task_Execution_Protocol.md` for full specification.

## Prohibited actions

- **Do not** create or activate any GitHub Actions workflows without proper review.
- Keep automation artifacts confined to `.codex/`.

## Useful commands

```python
# example: minimal agent
def run_agent(task: str) -> str:
    return f"ok: {task}"
```

Local checks before commit:
```bash
pre-commit run --all-files
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

Generate status update report:
```bash
# Generate comprehensive JSON status report
codex-status-audit --generate

# Or directly:
python tools/generate_status_update.py

# Output: .codex/status/_codex_status_update-YYYY-MM-DD.json
```

> Tip: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` disables 3rd-party plugin auto-loading for deterministic test runs in minimal environments.


## Patch Application Best Practices

**Reference**: RFC 3881, Git documentation, GitHub Codex issue #2235

### Pre-flight Validation

Before applying any patch:

1. **Validate patch format**:
   ```bash
   bash scripts/validate_patch.sh <patch-file>
   ```

2. **Dry-run with git**:
   ```bash
   git apply --check <patch-file>
   ```

3. **Ensure clean repo state**:
   ```bash
   git status  # Should be clean
   git pull    # Latest from remote
   ```

### Recommended Workflow

```bash
# 1. Validate
bash scripts/validate_patch.sh changes.patch || exit 1

# 2. Dry-run
git apply --check changes.patch || exit 1

# 3. Apply
git apply changes.patch

# 4. Test
pytest tests/ -v
pre-commit run --all-files

# 5. Commit
git add .
git commit -m "Apply patch: <description>"
```

## Tool Selection Guidelines

**Reference**: docs/guides/CODEX_TOOL_SELECTION.md

### Decision Tree

When modifying files:

1. **New file?** → Use `cat <<'EOF'`
2. **Single-line change?** → Use `sed -i`
3. **Formal patch with @@ markers?** → Use `apply_patch` (after validation)
4. **Complex with variables?** → Use temp file + validation
5. **Large multi-line change?** → Regenerate entire file with `cat <<'EOF'`

### Success Rates by Tool

| Tool | Success Rate | Conditions |
|------|-------------|-----------|
| `cat <<'EOF'` | 100% | New files, literals |
| `sed -i` | 85% | Simple replacements, no regex edge cases |
| `apply_patch` | 50-90% | Requires validation; improves to 95% with pre-flight check |
| Temp file + move | 95% | Complex generation, safe handoff |

See `docs/guides/CODEX_TOOL_SELECTION.md` for detailed examples.

## Config composition & overrides

You can inspect the composed defaults and override at the CLI:

```bash
python -m codex_ml.cli.config --info defaults   # show defaults list
python -m codex_ml.cli.config trainer.seed=123 trainer.deterministic=true logging.format=ndjson
```

See Hydra's docs for background on defaults lists and composition order.

## Related Documentation

- [Main AGENTS.md](/AGENTS.md) - Comprehensive operations playbook (Version 4.3.0)
- [CTEP Protocol](/.github/docs/Copilot_Task_Execution_Protocol.md) - Task execution protocol
- [CHANGELOG](/docs/CHANGELOG.md) - Version history
