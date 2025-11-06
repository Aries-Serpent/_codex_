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
- **Integration tests**: Use `-m "not integration"` to exclude integration tests for faster local test runs:
  ```bash
  pytest -m "not integration"
  ```

## Prohibited actions

- **Do not** create or activate any GitHub Actions workflows.
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

> Tip: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` disables 3rd-party plugin auto-loading for deterministic test runs in minimal environments. ([Happy Test][2])


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
git add -A
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

## Bash Formatting Standards

**Reference**: docs/guides/BASH_HEREDOC_REFERENCE.md

### Heredoc Quoting Rules

- **Use `<<'EOF'`** (quoted) for:
  - Literal shell scripts
  - JSON/YAML config
  - Code blocks (no variable expansion)
  - LaTeX, regex patterns

- **Use `<<EOF`** (unquoted) for:
  - Dynamic content
  - Environment variable interpolation
  - Command substitution
  - Use with caution on escape sequences

### Printf Formatting

**Always include `\n` explicitly**:
```bash
# ✅ CORRECT
printf "Line 1\nLine 2\n"

# ❌ WRONG (no newline at end)
printf "Line 1\nLine 2"
```

**Use `%b` for escape interpretation**:
```bash
# Enables escape sequences in arguments
printf "%b\n" "Line 1\nLine 2"
```

See `docs/guides/BASH_HEREDOC_REFERENCE.md` for comprehensive reference.

## Pre-flight Checklist Requirement

**For complex operations** (patches, refactoring, migrations):

1. Generate checklist:
   ```bash
   python scripts/generate_preflight.py \
     --task "Describe your operation" \
     --files "file1.py file2.py" \
     --pr 1926
   ```

2. Fill out checklist template:
   - [ ] Phase 1: Context collection
   - [ ] Phase 2: Tool inventory
   - [ ] Phase 3: Strategy definition
   - [ ] Phase 4: Risk assessment
   - [ ] Phase 5: Execution lock
   - [ ] Phase 6: Validation plan

3. Commit checklist before execution

Reference: `docs/codex/PRE_FLIGHT_CHECKLIST.md`

## Context Caching Patterns

**For performance optimization** (CODEX-004 fix):

Use session caching to avoid duplicate file I/O operations:

```python
from src.codex.utils.session_cache import FileCache

# Initialize cache at session start
cache = FileCache()
cache.add("scripts/survey.sh")
cache.add("src/config.py")

# Reference without re-reading
content = cache.get("scripts/survey.sh")

# Cache will auto-invalidate on file modification
cache.invalidate_if_modified("scripts/survey.sh")
```

Reference: `src/codex/utils/session_cache.py`

## Pre-commit Hook Management

**Reference**: `.pre-commit-config.yaml` (updated with timeouts)

### Configure Timeouts

Pre-commit hooks now have timeout settings (CODEX-003 fix):

- Semgrep: 600 seconds
- Bandit: 300 seconds
- Black/Ruff/isort: 60 seconds
- Mypy: 120 seconds

### Disable Hooks if Needed

```bash
# Check status
bash scripts/manage_hooks.sh status

# Temporarily disable (for speed/debugging)
bash scripts/manage_hooks.sh disable
git commit -m "Quick fix"

# Re-enable when done
bash scripts/manage_hooks.sh enable
```

Or skip for one commit:
```bash
git commit -n -m "Skip hooks this time"
```

Reference: `scripts/manage_hooks.sh`

## Validation Automation

**For efficient validation** (CODEX-010 fix):

Use automated validators instead of manual inspection:

```python
from src.codex.utils.validators import (
    validate_file_structure,
    validate_with_checksum,
    validate_with_diff,
)

# Structure validation
issues = validate_file_structure("script.py")
assert issues['valid_syntax']

# Checksum validation
valid, sha = validate_with_checksum("script.py")

# Diff comparison
identical, diff_output = validate_with_diff("original.py", "modified.py")
```

Reference: `src/codex/utils/validators.py`

## Session Context Discovery

**For automatic context** (CODEX-008 fix):

Automatically discover PR number and session info:

```python
from src.codex.utils.context_discovery import get_session_info

# Discover at session start
info = get_session_info()
# Returns: PR number, branch, commit, author, timestamp
```

Reference: `src/codex/utils/context_discovery.py`

## Config composition & overrides

You can inspect the composed defaults and override at the CLI:

```bash
python -m codex_ml.cli.config --info defaults   # show defaults list
python -m codex_ml.cli.config trainer.seed=123 trainer.deterministic=true logging.format=ndjson
```

See Hydra's docs for background on defaults lists and composition order.

[2]: https://docs.pytest.org/en/stable/how-to/plugins.html#disabling-plugin-auto-loading
