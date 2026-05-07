# Permanent Facts — Session Memory Seed
#
# This file stores known-recurring facts about the codebase.
# AI agents are explicitly instructed to read this file at the start of
# each session to avoid re-discovering known issues across sessions.
#
# Format: ## <fact-name> / root cause / fix / prevention

---

## HF_REVISION Leak Pattern

- **Issue:** `tests/models/conftest.py` set `HF_REVISION=abcdef0` at **module scope** via `os.environ.setdefault(...)`.
- **Impact:** The env var leaked across the entire test session, causing `HFModelUnavailableError` in tests that do not belong to `tests/models/` — specifically `tests/space_traversal/test_peft_comprehensive/`. Caused repeated CI failures in S105, S106, S107 (three full sessions of diagnosis).
- **Fix (S108):** Changed to a `scope="function"` autouse `monkeypatch` fixture. See `tests/models/conftest.py`.
- **Prevention:** Never set `os.environ[...]` or `os.environ.setdefault(...)` at module scope in conftest.py files. Always use `monkeypatch.setenv` inside a fixture.
- **Pattern:** P-042

---

## Lazy Import Pattern in legacy_api.py

- **Issue:** `src/codex_ml/training/legacy_api.py` uses **lazy imports inside `run_functional_training()`** (lines ~1155–1165) to avoid circular dependency issues at module load time.
- **Impact:** Test authors patched `sys.modules` at import time, expecting the mock to be seen by the function. Because the imports are deferred, the mock was invisible — causing "mock not called" failures across multiple test files.
- **Fix (S108):** Added a block comment at the lazy import site documenting the pattern. See `src/codex_ml/training/legacy_api.py`.
- **Prevention:** When writing tests for functions in `legacy_api.py`, **always** patch the **module attribute**: `monkeypatch.setattr(legacy_api, "get_model", mock_fn)`. Do NOT use `sys.modules` patching.
- **Pattern:** P-043

---

## Coverage Measurement Gap (local vs CI)

- **Issue:** The `pyproject.toml` comment at line ~467 says `~27.5% local`, but CI measures 50%+. The gap is caused by:
  1. Local runs skip tests requiring `torch`/`transformers` (not installed locally).
  2. CI installs the full `[test]` extra including `torch`, running more tests.
- **Impact:** Every session that raises `fail_under` risks setting it too high or too low because the local number is wrong.
- **Fix:** Use `make coverage` to get an accurate local number with the full test stack installed. Alternatively, read the CI artifact `coverage-baseline` from the last green run.
- **Prevention:** Before raising `fail_under`, check the CI coverage artifact. Do NOT rely on the comment in `pyproject.toml`.

---

## pytest-rerunfailures + pytest-timeout Thread Crash

- **Issue:** `pytest-rerunfailures` spawns a background `socket.accept()` server thread. `pytest-timeout` (thread mode) injects `Timeout` into **all** threads including the server thread. When the server thread tries to write to `sys.stderr` after pytest has closed it for capsys capture, you get `ValueError: I/O operation on closed file` + `lost sys.stderr`.
- **Fix:** Add `-p no:rerunfailures` to all sharded pytest commands.
- **Pattern:** P-038

---

## CodeQL Branch Coverage Gap

- **Issue:** `codeql-analysis.yml` originally only triggered on PRs to `main`/`develop`. PRs to `0D_base_` and `copilot/**` never ran CodeQL, so GHAS had no SARIF and showed "N configurations not found".
- **Fix:** Added `0D_base_` and `copilot/**` to `pull_request.branches`. Also added `go` to the language matrix (tools/github-secrets-cli has `go.mod`).
- **Pattern:** P-039

---

## Confirmed-Flaky Timing-Sensitive Tests (S229)

The following tests use `time.sleep()` for real-wall-clock expiry/timing checks
and have been marked `@pytest.mark.flaky(reruns=2)` to handle occasional failures
on loaded CI runners.

**Marked in S229 (2026-03-30):**

| File | Test | Reason |
|------|------|--------|
| `tests/space_traversal/test_performance.py` | `test_file_cache_expiry` | `time.sleep(1.1)` for TTL expiry — fails if runner is slow |
| `tests/space_traversal/test_performance.py` | `test_file_cache_cleanup_expired` | `time.sleep(1.1)` for TTL expiry — fails if runner is slow |
| `tests/space_traversal/test_performance.py` | `test_profile_stage_context_manager` | `time.sleep(0.05)` + boundary timing assertion `>= 0.05` |
| `tests/autonomy/test_integration_budget_exhaustion.py` | `TestBudgetCap.test_budget_cap_raises_on_exhaustion` | `budget_cap(max_seconds=0.001)` — very tight timeout, may not trigger under high load |
| `tests/autonomy/test_autonomy_scheduler.py` | `TestBudgetCap.test_budget_cap_raises_on_timeout` | `budget_cap(max_seconds=0.01)` — tight timeout, may not trigger under high load |

**Prevention:** When writing tests that depend on wall-clock timing (sleep-based TTL,
budget caps with millisecond precision), always add `@pytest.mark.flaky(reruns=2)`.
Import: `import pytest` at the top of the file; marker syntax:
```python
@pytest.mark.flaky(reruns=2)
def test_my_timing_sensitive_test(): ...
```
Note: Sharded CI runs pass `-p no:rerunfailures` (see P-038), which disables the
rerun plugin. In those runs, `@pytest.mark.flaky` is effectively a no-op and only
has an effect in non-sharded test runs.

- **Pattern:** P-044

- **Pattern:** P-045
  **Category:** Session Wrap-Up Gate
  **Summary:** ZERO MERGE CONFLICTS before every session close
  **Detail:** Before every `report_progress` push, agents MUST run:
  (1) `git fetch origin main`
  (2) `git diff --name-only --diff-filter=U` → must return EMPTY
  (3) grep for `<<<<<<< ` conflict markers → must return EMPTY
  If conflicts exist, resolve them first (keep HEAD for branch-specific files;
  run `sync_tracked_files --fix` after resolving `.secrets.baseline`).
  Policy doc: `.codex/docs/ZERO_CONFLICT_WRAP_UP_POLICY.md`
  Introduced: PR #4323 S30 2026-05-07 — `.secrets.baseline` conflict from
  `codebase-health-sweep.yml` auto-push to main while PR was active.
