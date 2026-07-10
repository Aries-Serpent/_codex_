# P19 Shadow Imports — Tracking Issue

**Status:** 🔴 Open  
**Priority:** P1 (blocks Resilient Validation Suite + Pre-Merge Validation)  
**Opened:** 2026-03-29 (S228)  
**Labels:** `p19-shadow-imports`, `ci-failure`, `needs-pr`

---

## Problem Summary

Approximately **40 tests** in the Resilient Validation Suite and Pre-Merge Validation workflows
fail with `ImportError` / `ModuleNotFoundError` because several source files use **shadow import
paths** (`config.openai_client`, `services.github.client`) that resolve correctly when `src/` is
on `sys.path` (as configured in `pytest.ini` via `pythonpath = . src`) but **fail in CI
environments** where the venv is built without the `src/` pythonpath config being applied during
import resolution (e.g., when modules are imported transitively before pytest's conftest.py runs
or when running outside pytest).

### Root Causes

| Code | Pattern | Risk |
|------|---------|------|
| `P19-SHADOW-EXPANDED-001` | Root-level `__init__.py` in `training/`, `utils/`, `models/`, `services/`, `config/` **shadows** `src/` counterparts | Silent wrong-module resolution |
| `P19-SHADOW-REVERT-001` | `from config.X import Y` resolves to wrong root-level shadow in some envs | `ImportError` or stale module loaded |
| `P19-BATCH-WATCH-001` | `try/except ImportError` blocks that rely on `src.` prefix stripped by P19 batch | Branch becomes unreachable |

---

## Affected Files

### Source (`src/`)

| File | Shadow Import | Correct Import |
|------|--------------|----------------|
| `src/agents/autonomous_runner.py:25` | `from config.openai_client import CodexOpenAIClient, ExecutionResult` | `from src.config.openai_client import ...` OR ensure `src/` in PYTHONPATH |
| `src/agents/orchestrator.py:24` | `from config.openai_client import CodexOpenAIClient, ExecutionResult` | Same |
| `src/mcp/tools/github_logs.py:47` | `from services.github.client import GitHubClientSync` | `from src.services.github.client import ...` |
| `src/codex/cli_github_logs.py:21` | `from services.github.client import GitHubClientSync` | Same |
| `src/codex/api/github_logs.py:75` | `from services.github.client import GitHubClientSync` | Same |

### Tests

| File | Shadow Import |
|------|--------------|
| `tests/config/test_openai_client.py` | Multiple `from config.openai_client import ...` |
| `tests/test_github_logs.py` | `from src.services.github.client import ...` (uses `src.` prefix — correct) |
| `tests/services/test_github_client_phase9_1.py` | `services.github.client` references |
| `tests/agents/test_autonomous_runner.py` | `config.openai_client` transitive |

---

## Failing Test Scope (CI)

| Workflow | Suite | Failures |
|----------|-------|---------|
| Resilient Validation Suite | `quick`, `integration` groups | ~40 ImportError |
| Pre-Merge Validation | full suite | ~40 ImportError |
| Iterative Self-Healing CI | triggered as cascade | coverage-timeout |

---

## Fix Strategy

### Option A — Add `src/` pythonpath to CI venv activation (non-invasive)
Add `export PYTHONPATH="${PYTHONPATH}:${GITHUB_WORKSPACE}/src"` to the venv setup step in
affected workflows. **Fast** but requires touching every workflow.

### Option B — Fix the imports at source (recommended)
Change all `from config.X import Y` → `from codex.config.X import Y` (the canonical installed
package path under the `codex` namespace), and `from services.github.client` →
`from codex.services.github.client`. This is safe because `src/codex/` is the installed
package root.

**Verification:**
```bash
python -c "from codex.config import openai_client; print('OK')"  # should work
python -c "from src.config import openai_client; print('OK')"    # works via PYTHONPATH
python -c "from config import openai_client; print('OK')"        # shadow — unreliable
```

### Option C — Add `conftest.py` sys.path fix (stopgap)
Add to root `conftest.py`:
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
```
This ensures `src/` is on the path before any module import during pytest collection.
**Already partially done** via `pytest.ini` `pythonpath = . src` but doesn't help non-pytest
invocations.

### Recommended Fix (Option B + Option C)
1. Add `conftest.py` sys.path guard (Option C) as immediate stopgap — 1 line change
2. File a dedicated PR to migrate all shadow imports to canonical `codex.*` paths (Option B)

---

## Copilot Coding Agent PR Prompt

Use this prompt to trigger a Copilot PR fixing the module paths:

```
@copilot open a pull request to fix P19 shadow imports:

## Task: Fix P19 Shadow Import Module Paths

Files to update:
- src/agents/autonomous_runner.py:25 — `from config.openai_client` → `from codex.config.openai_client`
- src/agents/orchestrator.py:24 — same
- src/mcp/tools/github_logs.py:47 — `from services.github.client` → `from codex.services.github.client`
- src/codex/cli_github_logs.py:21 — same
- src/codex/api/github_logs.py:75 — same
- tests/config/test_openai_client.py — update all `from config.openai_client` → `from codex.config.openai_client`
- tests/agents/test_autonomous_runner.py — update transitive import

Additionally add to conftest.py root:
```python
import sys, pathlib
_SRC = pathlib.Path(__file__).parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
```

Validate with:
1. `python -m pytest tests/config/test_openai_client.py tests/agents/test_autonomous_runner.py -x -q`
2. `python -m ruff check src/agents/ src/mcp/ src/codex/ tests/config/ tests/agents/ --select=E,F,I`
3. `python scripts/ci/sync_tracked_files.py --check`

Scope: Resilient Validation Suite, Pre-Merge Validation
Tracking: .codex/issues/P19_SHADOW_IMPORTS_TRACKING.md
```

---

## Artefacts & Related Links

| Type | Link |
|------|------|
| CI Health Alert | [#3791](https://github.com/Aries-Serpent/_codex_/issues/3791) |
| PR #3790 description | Cites P19 as pre-existing open failure |
| iterative-self-healing-ci.yml:165 | `coverage-timeout` handler cites P19 |
| docs/ci/PR_LIFECYCLE.md:188 | P19 pattern table |
| docs/ci/PR_LIFECYCLE.md:379-382 | P19-BATCH-001 / WATCH-001 / SHADOW-EXPANDED-001 / SHADOW-REVERT-001 |
| docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md:S145 | P19 shadow-safe backfill session |

---

## Progress Tracker

- [x] Document issue scope (S228)
- [x] Identify affected files
- [x] Write Copilot PR prompt
- [x] Confirm Option C stopgap already in place (`conftest.py` lines 28-48 — `_sys.path.insert(0, _src)` guard)
- [ ] Open dedicated PR with Option B fix (canonical `codex.*` imports)
- [ ] Verify Resilient Validation Suite passes after fix
- [ ] Close this tracking issue
