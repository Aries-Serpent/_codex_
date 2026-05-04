# 🎯 PR Follow-Up Tasks — #4211

**PR**: #4211 — `fix: UNKNOWN_TIMESTAMP, RunLogger import, docstring caps, duplicate pragma, malformed ISO timestamp + CodeQL Waves 1–2`
**Branch**: `copilot/add-unknown-timestamp-constant`
**Author**: @Copilot
**Last Updated**: 2026-05-04T02:00Z
**Status**: 🔄 Wave 2 complete — Wave 3–7 queued

---

## ✅ COMPLETED WORK (this PR)

| Wave | Rules | Alerts Fixed | Commit |
|------|-------|-------------|--------|
| 0 — micro-fixes | UNKNOWN_TIMESTAMP, docstrings, pragma, ISO Z | 7 | `03c19be7` |
| 1 — Errors | `py/call-to-non-callable`, `py/call/wrong-arguments`, `py/call/wrong-named-argument`, `py/uninitialized-variable` | 38 | `82b95be` |
| 2 — Warnings | `py/unreachable-statement`, `py/multiple-definition` | 41 | `f385b6c` |

**Also completed this session:**
- `.github/workflows/codeql.yml` — CodeQL Advanced workflow (actions/go/javascript-typescript/python/rust, ubuntu-latest only, `security-extended,security-and-quality` queries)
  - Fixed SARIF category to `/language:<lang>/advanced` to avoid collision with `codeql-analysis.yml` (which uses `/language:<lang>`)
- `PR-4211-followup.md` — Fixed invalid `mypy --select` triage command; removed duplicate timestamp

---

## 🌊 REMAINING WAVES — sprint backlog

> **Rule:** Merge each wave's PR and wait for CodeQL re-scan to confirm 0 new findings before starting the next wave.

---

### 🌊 Wave 3 — Exception Hygiene (Reliability) ← NEXT

**Target rules:** `py/empty-except` (87), `py/unexpected-raise-in-special-method` (2), `py/catch-base-exception` (1) — **Total: ~90 findings**

**PR title:** `chore(quality): Wave 3 — exception hygiene [py/empty-except, py/catch-base-exception, py/unexpected-raise-in-special-method]`

#### Pre-scanned findings (top-10 by file)

| File | Line | Pattern |
|------|------|---------|
| `conftest.py` | 19 | empty except: pass |
| `conftest.py` | 342 | empty except: pass |
| `tests/test_rag_utils.py` | 68, 84, 150, 159, 237 | empty except: pass |
| `tests/test_mlflow_utils.py` | 100 | empty except: pass |
| (+ 82 more files) | | |

**Fix strategy:**
```python
# BEFORE (py/empty-except):
try:
    risky_operation()
except Exception:
    pass

# AFTER — use existing module logger:
try:
    risky_operation()
except Exception:
    logger.debug("Suppressed exception in handler", exc_info=True)
```

- For `except BaseException`: replace with `except Exception` unless `KeyboardInterrupt`/`SystemExit` handling is intentional (document with inline comment).
- For `__special__` methods raising non-standard exceptions: convert to `TypeError`, `ValueError`, `AttributeError`, `StopIteration`, or `NotImplementedError`.
- Use `ruff check --select=BLE001 --fix` to flag bare `except` clauses first.

**DO NOT** log sensitive data — cross-check against `services/ita/app/security.py` patterns.

**Bulk-fix command (generate targets):**
```bash
python -m ruff check --select=BLE001,E722 --output-format=json . > /tmp/wave3_targets.json
```

---

### 🌊 Wave 4 — Control Flow (Reliability)

**Target rules:** `py/mixed-returns` (25), `py/mixed-tuple-returns` (4) — **Total: ~29 findings**

**PR title:** `chore(quality): Wave 4 — control flow normalization [py/mixed-returns, py/mixed-tuple-returns]`

#### Pre-scanned findings (top-10 by file)

| File | Line | Function | Pattern |
|------|------|----------|---------|
| `tests/test_cli_hydra_validation.py` | 22 | `test_hydra_main_offline_compose` | mixed returns |
| `tests/test_sentencepiece_adapter.py` | 29 | `_stub_transformers` | mixed returns |
| `tools/codex_ingestion_workflow.py` | 353 | `patch_deep_research_script` | mixed returns |
| `agents/developer_orchestrator.py` | 563 | `_determine_implementation_order` | mixed returns |
| `agents/mental_mapping.py` | 1168 | `dfs` | mixed returns |
| `analysis/intuitive_aptitude.py` | 458 | `_analyze_docstring_style` | mixed returns |
| `training/checkpoint_manager.py` | 349 | `_update_best` | mixed returns |
| (+ 18 more) | | | |

**Fix strategy:**
```python
# BEFORE (py/mixed-returns): some paths return value, some fall off end
def process(x):
    if x:
        return x * 2
    # implicit None return here — CodeQL flags this

# AFTER: explicit return on every path
def process(x):
    if x:
        return x * 2
    return None
```

For tuple returns:
```python
# BEFORE (py/mixed-tuple-returns):
def get_result():
    if success:
        return value, error_code  # tuple
    return None                   # not a tuple

# AFTER — consistent shape:
def get_result():
    if success:
        return value, error_code
    return None, -1               # same tuple shape
```

**Triage command:**
```bash
# mypy does not support --select for error filtering; use grep to filter output by keyword
python -m mypy src/ --ignore-missing-imports 2>&1 | grep -i "return"
```

---

### 🌊 Wave 5 — Import Hygiene (Maintainability)

**Target rules:** `py/import-and-import-from` (31), `py/repeated-import` (22), `py/unused-import` (16), `py/polluting-import` (2), `py/import-own-module` (1) — **Total: 72 findings**

**PR title:** `chore(quality): Wave 5 — import hygiene [py/import-and-import-from, py/repeated-import, py/unused-import, py/polluting-import, py/import-own-module]`

**Fix strategy:**
```bash
# Step 1: triage with ruff
python -m ruff check --select=F401,F811,F403,I --statistics . 2>&1 | head -30

# Step 2: auto-fix safe subsets (only commit diffs you've reasoned about)
python -m ruff check --select=F401,F811 --fix .

# Step 3: replace `from X import *` with explicit imports
grep -rn "import \*" src/ tests/ --include="*.py" | head -20
```

- `py/import-own-module`: search for `from codex_ml import codex_ml` or `import codex_ml.codex_ml` patterns.
- `py/polluting-import` (`from X import *`): resolve via explicit named imports; use `__all__` in the source module to limit exposure.

---

### 🌊 Wave 6 — Dead Code Sweep (Maintainability)

**Target rules:** `py/unused-global-variable` (118), `py/unused-local-variable` (92), `py/ineffectual-statement` (63), `js/unused-local-variable` (4), `py/commented-out-code` (1) — **Total: ~278 findings**

**PR title:** `chore(quality): Wave 6 — dead code sweep [py/unused-global-variable, py/unused-local-variable, py/ineffectual-statement, js/unused-local-variable]`

> ⚠️ **Split into sub-PRs if > 50 files touched.** Suggested split: `src/` then `tests/` then `scripts/`.

**Pre-deletion search protocol (per `CODEBASE_AGENCY_POLICY.md`):**

Before removing ANY global variable or function:
```bash
# Search for string-based references (getattr, importlib, templates)
grep -rn "\"VARIABLE_NAME\"\|'VARIABLE_NAME'\|getattr.*VARIABLE_NAME" . --include="*.py"
rg -l "VARIABLE_NAME" . --type=py
```
Document the search query in the PR description.

**Fix strategy:**
- `py/unused-global-variable`: check `__all__` first; if exported, add to `__all__` instead of deleting.
- `py/unused-local-variable`: rename to `_` if intentional discard; delete if dead.
- `py/ineffectual-statement`: docstring-like strings not assigned → either convert to docstring or delete.
- `js/unused-local-variable` (4 findings): run ESLint with `--rule 'no-unused-vars: error'`.
- `py/commented-out-code` (1 finding): move to ADR if historically valuable; otherwise delete.

**Triage commands:**
```bash
python -m ruff check --select=F841,F841 --statistics . | head -20
python -m vulture --min-confidence 80 src/ | head -40
```

---

### 🌊 Wave 7 — Style Polish (Maintainability/Reliability)

**Target rules:** `py/unnecessary-lambda` (5), `py/print-during-import` (1), `py/should-use-with` (1) — **Total: 7 findings**

**PR title:** `chore(quality): Wave 7 — style polish [py/unnecessary-lambda, py/print-during-import, py/should-use-with]`

**Fix strategy:**
```python
# py/unnecessary-lambda
sorted(items, key=lambda x: x.value)  →  sorted(items, key=attrgetter('value'))
callbacks.append(lambda: f(x))        →  callbacks.append(partial(f, x))

# py/print-during-import — move to guarded block or convert to logger.debug
print("module loaded")  →  logger.debug("module loaded")  # or if __name__ == "__main__"

# py/should-use-with
f = open("file")
data = f.read()
f.close()
→
with open("file") as f:
    data = f.read()
```

**Triage command:**
```bash
python -m ruff check --select=E731 --statistics .
grep -rn "^print(" src/ --include="*.py" | grep -v "if __name__"
grep -rn "\.open\|open(" src/ --include="*.py" | grep -v "with open"
```

---

## 🔧 CodeQL Advanced Workflow (`.github/workflows/codeql.yml`)

Added in this session. Covers:
- Languages: `actions`, `go`, `javascript-typescript`, `python`, `rust`
- Runner: `ubuntu-latest` (no swift/macos)
- Queries: `security-extended,security-and-quality`
- Schedule: Saturday 18:44 UTC (offset from `codeql-analysis.yml` Sunday 03:00)
- Jobs: `analyze`, `post-codeql-auto-approve`, `rescue-comment`

Validation after merge:
```bash
# Confirm workflow file is valid YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/codeql.yml'))"
# Check actionlint (if available)
actionlint .github/workflows/codeql.yml
```

---

## ✅ EXECUTION CHECKLIST

- [x] Wave 0 — micro-fixes (7 quality items)
- [x] Wave 1 — 38 Error-level CodeQL alerts
- [x] Wave 2 — `py/unreachable-statement` (38), `py/multiple-definition` (1) — **41 total**
- [x] `.github/workflows/codeql.yml` — CodeQL Advanced (ubuntu-latest, all 5 languages, distinct `/advanced` SARIF categories)
- [ ] Wave 3 — exception hygiene (~90 findings) — PR: `chore(quality): Wave 3`
- [ ] Wave 4 — control flow (~29 findings) — PR: `chore(quality): Wave 4`
- [ ] Wave 5 — import hygiene (~72 findings) — PR: `chore(quality): Wave 5`
- [ ] Wave 6 — dead code sweep (~278 findings) — PR: `chore(quality): Wave 6` (split if > 50 files)
- [ ] Wave 7 — style polish (~7 findings) — PR: `chore(quality): Wave 7`
- [ ] Final: 0 open findings on Code Quality dashboard (Maintainability ≥ Good, Reliability ≥ Good)

---

## 🔍 Validation Commands (run after each session)

```bash
# Lint all modified files
python -m ruff check src/ tests/ scripts/ --output-format=concise

# Tracked file consistency
python3 scripts/ci/sync_tracked_files.py --fix

# Type check (after touching src/)
python3 scripts/ci/mypy_baseline.py --require-baseline

# Auto-fix check
python scripts/ci/auto_fix_common_issues.py --check-only --json-output .codex/diagnostic-report.json

# Session wrapup
python3 scripts/ci/session_wrapup_autofix.py --pr-number 4211
```

- [ ] Documentation updated
- [ ] Self-review completed (5 passes, 0 concerns)

---

## 🔍 MANDATORY SELF-REVIEW PROTOCOL

**CRITICAL**: Perform 5 comprehensive self-review passes BEFORE concluding.

### Pass 1: Code Quality & Correctness
- [ ] All syntax errors resolved
- [ ] No linting warnings introduced
- [ ] Type hints correct
- [ ] Error handling comprehensive
- [ ] Edge cases covered

### Pass 2: Testing & Validation
- [ ] All tests passing locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved
- [ ] CI/CD checks passing

### Pass 3: Documentation & Communication
- [ ] Code comments added for complex logic
- [ ] Docstrings updated
- [ ] README reflects changes
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

### Pass 4: Security & Safety
- [ ] No hardcoded secrets or credentials
- [ ] Input validation added
- [ ] Dependencies reviewed (no vulnerabilities)
- [ ] Security implications documented

### Pass 5: Integration & Dependencies
- [ ] No breaking changes (or properly documented)
- [ ] Backward compatibility maintained
- [ ] Cross-PR dependencies resolved
- [ ] No regressions introduced

**Failure Protocol**: If ANY checkpoint fails, document issue, create resolution plan, execute within current session, re-run until all checks clear. **NEVER defer** without explicit reasoning.

---

## 🤖 COPILOT AGENT INSTRUCTIONS

**When you see `@copilot continue` in PR #4211:**

1. Load this prompt from `.github/copilot-prompts/active/PR-4211-followup.md`
2. Execute Priority 1 tasks in order, validating each
3. Then execute Priority 2 tasks
4. Review Priority 3 tasks
5. Update this file after each task (add ✅ for completed)
6. Perform mandatory 5-pass self-review
7. Post comprehensive status as PR comment
8. Generate new continuation if work remains

**Self-Review Mandate**: Perform 5 comprehensive passes. Address ALL concerns until 0 issues remain. NEVER defer work without explicit reasoning and resolution plan.

---

**Generated**: 2026-05-04  
**Template Version**: 2.0.0
