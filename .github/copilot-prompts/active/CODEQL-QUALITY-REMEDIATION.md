# 🔴 CodeQL Quality Remediation — Codebase-Wide Tracker

> **Static file — persists across ALL sessions and PRs.**
> Every Copilot session working on quality improvements MUST load this file first.
> Update progress in-place; do NOT create a new file per PR.

**Scan Reference:** commit `fd258fb786ef5df3b5ab1d89cf166fb4fc432f4e` (main, 2026-05-03)
**Scanner:** CodeQL GitHub Advanced Security
**Security Page:** https://github.com/Aries-Serpent/_codex_/security/quality
**Last Updated:** 2026-05-03
**Tracking PR:** #4204 (branch `copilot/add-validation-for-batch-size`)

---

## 📊 Finding Summary

| Severity | Rule | Count | Status |
|----------|------|-------|--------|
| 🔴 Error | `py/call-to-non-callable` | 4 | ⬜ Open |
| 🔴 Error | `py/call/wrong-arguments` | 2 | ⬜ Open |
| 🔴 Error | `py/call/wrong-named-argument` | 18 | ⬜ Open |
| 🟡 Warning | `py/missing-equals` | 1 | ⬜ Open |
| 🟡 Warning | `py/use-of-exit-or-quit` | 2 | ⬜ Open |
| 🟡 Warning | `py/comparison-of-constants` | 1 | ⬜ Open |
| 🟡 Warning | `py/comparison-of-identical-expressions` | 5 | ⬜ Open |
| 🟡 Warning | `py/implicit-string-concatenation-in-list` | 5 | ⬜ Open |
| 🟡 Warning | `py/unnecessary-pass` | 1 | ⬜ Open |
| 🟡 Warning | `py/unreachable-statement` | 33 | ⬜ Open |
| 🔵 Note | `js/unused-local-variable` | 4 | ⬜ Open |
| | **TOTAL** | **76** | |

---

## 🚀 Phase 1 — Error-Severity Fixes (P0 — Blocking, fix first)

> Runtime crashes. Fix before any Warning-level work.

### 1.1 `py/call-to-non-callable` — 4 findings

**What it means:** A non-callable (int, str, plain attribute) is being invoked with `()`.

**How to locate:**
```bash
# Navigate to the security findings page (requires browser/token):
# https://github.com/Aries-Serpent/_codex_/security/quality/rules/py%2Fcall-to-non-callable
#
# Or search locally for common patterns:
grep -rn "config\.\w\+()\|self\.\w\+()" src/ scripts/ --include="*.py" | \
  grep -v "def \|#\|logger\|print\|str()\|int()\|list()\|dict()\|set()\|tuple()" | head -40
```

**Fix pattern:**
```python
# ❌ BAD — attribute is an int, not callable
result = config.max_retries()

# ✅ FIX — access directly
result = config.max_retries
```

**Validation:**
```bash
python -m py_compile <file>
pytest tests/ -x -q --tb=short -k <related_test>
```

**Progress:** ⬜ 0/4 resolved — locations TBD (need CodeQL browser access)

---

### 1.2 `py/call/wrong-arguments` — 2 findings

**What it means:** A function is called with wrong number of positional arguments.

**How to locate:**
```bash
# https://github.com/Aries-Serpent/_codex_/security/quality/rules/py%2Fcall%2Fwrong-arguments
```

**Fix pattern:**
```python
# ❌ BAD — function expects 2 args, called with 3
def process(data, mode): ...
process(data, mode, extra)  # wrong

# ✅ FIX — match the signature
process(data, mode)
```

**Progress:** ⬜ 0/2 resolved — locations TBD

---

### 1.3 `py/call/wrong-named-argument` — 18 findings ⚠️ LARGEST ERROR GROUP

**What it means:** A keyword argument name does not match any parameter in the function's signature — usually a refactoring artifact where a parameter was renamed but call sites were not updated.

**How to locate:**
```bash
# https://github.com/Aries-Serpent/_codex_/security/quality/rules/py%2Fcall%2Fwrong-named-argument
#
# Known to require CodeQL interprocedural analysis — ruff/mypy will NOT catch these.
# Run locally with CodeQL CLI (available at /opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql)
```

**Fix approach:**
1. For each finding: `grep -rn "def <function_name>" src/ scripts/ tests/` to find canonical signature.
2. Update the call site keyword to match the current parameter name.
3. Batch all findings in the same file into a single commit.

**Fix pattern:**
```python
# ❌ BAD — param renamed from 'input_text' to 'text'
def embed(text: str, model: str): ...
embed(input_text="hello", model="ada")  # wrong-named-argument

# ✅ FIX
embed(text="hello", model="ada")
```

**Progress:** ⬜ 0/18 resolved — locations require CodeQL scan

---

## 🟡 Phase 2 — Warning-Severity Reliability Fixes

### 2.1 `py/missing-equals` — 1 finding

**What it means:** A class defines new instance attributes in `__init__` without overriding `__eq__`, making equality comparisons use object identity instead of value.

**Fix template:**
```python
# ✅ Add to affected class:
def __eq__(self, other: object) -> bool:
    if not isinstance(other, type(self)):
        return NotImplemented
    return self.__dict__ == other.__dict__

def __hash__(self) -> int:
    return hash(tuple(sorted(self.__dict__.items())))
```

**Progress:** ⬜ 0/1 resolved

---

### 2.2 `py/use-of-exit-or-quit` — 2 findings

**What it means:** `exit()` / `quit()` are REPL-only builtins. Scripts and library code must use `sys.exit()`.

**How to find:**
```bash
grep -rn "\bexit()\|\bquit()" --include="*.py" src/ scripts/ | \
  grep -v "sys.exit\|os._exit\|ctx.exit\|#\|def exit\|def quit\|__exit__"
```

**Fix:**
```python
# ❌
exit(1)
# ✅
import sys
sys.exit(1)
```

**Progress:** ⬜ 0/2 resolved

---

## 🟡 Phase 3 — Warning-Severity Maintainability Fixes

### 3.1 `py/unreachable-statement` — 33 findings ⚠️ LARGEST OVERALL

**What it means:** Code after `return`, `raise`, `break`, `continue`, or unconditional `sys.exit()` is never executed.

**Search commands:**
```bash
# Run CodeQL locally for exact locations, or use:
python3 - <<'PYEOF'
import ast
from pathlib import Path

TERM = (ast.Return, ast.Raise, ast.Break, ast.Continue)

def check(body, path, findings):
    for i, s in enumerate(body):
        if isinstance(s, TERM) and i+1 < len(body):
            n = body[i+1]
            # Skip trailing docstrings/ellipsis
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant):
                continue
            findings.append(f"{path}:{n.lineno}")

findings = []
for p in list(Path('src').rglob('*.py')) + list(Path('scripts').rglob('*.py')):
    try:
        t = ast.parse(p.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:
        continue
    for node in ast.walk(t):
        for attr in ('body', 'orelse'):
            b = getattr(node, attr, [])
            if isinstance(b, list):
                check(b, p, findings)
for h in node.handlers if hasattr(node, 'handlers') else []:
    check(h.body, p, findings)
print(f"Found: {len(findings)}")
for f in findings:
    print(f)
PYEOF
```

**Fix approach:** Do NOT blindly delete — verify intent. Move logic before the terminating statement, or remove if genuinely dead code.

**Progress:** ⬜ 0/33 resolved

---

### 3.2 `py/comparison-of-identical-expressions` — 5 findings

**What it means:** Both sides of a comparison are the same expression (e.g. `x == x`), always evaluating to the same result. Almost always a typo.

**Known locations (from local AST scan):**
- `tests/agents/test_phase2_deep_coverage_batch10.py:461` — `nan == nan` (should use `math.isnan()`)
- `tests/coverage_push/test_edge_cases.py:175` — `nan_value == nan_value`
- `tests/integration/test_phase14_edge_cases_coverage.py:88` — `nan_value == nan_value`

**Fix:**
```python
# ❌ BAD
if x == x:   # always True — likely meant to compare two different vars

# ✅ FIX (for NaN checks specifically)
import math
assert math.isnan(result)

# ✅ FIX (for general typos)
if x == y:   # fix the intended variable
```

**Progress:** ⬜ 0/5 resolved (3 locations identified, 2 more need CodeQL)

---

### 3.3 `py/implicit-string-concatenation-in-list` — 5 findings

**What it means:** Two adjacent string literals in a list are silently concatenated by Python because a comma is missing.

**How to find:**
```bash
# Use ruff:
python -m ruff check --select ISC001,ISC002 src/ scripts/ tests/ --output-format=text
```

**Fix:**
```python
# ❌ BAD — "foobar" — missing comma
items = ["foo" "bar", "baz"]

# ✅ FIX
items = ["foo", "bar", "baz"]
```

**Progress:** ⬜ 0/5 resolved — use `ruff --select ISC001` to find exact locations

---

### 3.4 `py/comparison-of-constants` — 1 finding

**What it means:** Both operands are compile-time constants — result never changes.

**Known candidate from local scan:**
- `tests/coverage_push/test_edge_cases.py:132` — `0.0 == 0` (always True)
- `tests/integration/test_phase14_edge_cases_coverage.py:420` — `10 == 10`

**Fix:** Replace with the variable that was intended, or remove the tautological guard.

**Progress:** ⬜ 0/1 resolved

---

### 3.5 `py/unnecessary-pass` — 1 finding

**What it means:** A `pass` statement exists alongside other statements in the same block (making it redundant).

**How to find:**
```bash
python -m ruff check --select PIE790 src/ scripts/ tests/ --output-format=text
```

**Fix:** Simply delete the `pass` statement.

**Progress:** ⬜ 0/1 resolved

---

## 🔵 Phase 4 — Note-Severity JavaScript Fixes

### 4.1 `js/unused-local-variable` — 4 findings

**What it means:** A variable/import is declared but never used.

**How to find:**
```bash
# https://github.com/Aries-Serpent/_codex_/security/quality/rules/js%2Funused-local-variable
npx eslint . --ext .js,.ts --rule '{"no-unused-vars": "error"}' 2>/dev/null | head -30
```

**Fix:** Remove unused declarations (or mark with `_` prefix if intentional).

**Progress:** ⬜ 0/4 resolved — locations require browser/CodeQL access

---

## 🔧 Verification Commands (run after EACH phase)

```bash
# After Phase 1 — error fixes
python -m py_compile $(git diff --name-only HEAD | grep '\.py$')
pytest tests/ -x -q --tb=short
ruff check $(git diff --name-only HEAD | grep '\.py$')

# After Phase 3 — maintainability fixes
python -m ruff check --select ISC001,ISC002,PIE790 src/ scripts/ tests/

# After ALL phases
pytest tests/ -v --tb=short -q
python scripts/ci/mypy_baseline.py --require-baseline
python scripts/ci/auto_fix_common_issues.py --check-only
python scripts/ci/sync_tracked_files.py --check
pre-commit run --all-files
```

---

## 📋 Session Handoff Protocol

**Every session that works on this tracker MUST:**

1. **Load this file first** — `cat .github/copilot-prompts/active/CODEQL-QUALITY-REMEDIATION.md`
2. **Check current CodeQL open alerts** — https://github.com/Aries-Serpent/_codex_/security/quality
3. **Fix the highest-priority open item** (Phase 1 before Phase 2, etc.)
4. **Update status rows** in the Finding Summary table above (`⬜ Open` → `✅ Fixed` with commit SHA)
5. **Update `Last Updated` date** at the top of this file
6. **Update `Tracking PR`** to the current PR number

---

## 📝 Completed Fix Log

| Date | Rule | Files Changed | Commit | Session/PR |
|------|------|---------------|--------|-----------|
| 2026-05-03 | (pre-remediation baseline established) | — | `fd258fb` | PR #4204 |

---

## 🔗 Related Resources

| Resource | Path |
|----------|------|
| Codebase Agency Policy | `.codex/CODEBASE_AGENCY_POLICY.md` |
| Agent Accountability Report | `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` |
| mypy Baseline | `.mypy_baseline` |
| Auto-Fix Script | `scripts/ci/auto_fix_common_issues.py` |
| Sync Tracked Files | `scripts/ci/sync_tracked_files.py` |
| PR #4204 Follow-Up | `.github/copilot-prompts/active/PR-4204-followup.md` |
| CodeQL Security Page | https://github.com/Aries-Serpent/_codex_/security/quality |
