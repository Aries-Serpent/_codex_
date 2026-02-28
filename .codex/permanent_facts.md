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
