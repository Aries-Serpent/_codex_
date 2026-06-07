# Gap 2 — Bandit/Semgrep Remediation Evidence

**Status:** ✅ IMPLEMENTED  
**Wave:** 1 / Lane A — Security/Compliance  
**Agent:** `code-scanning-remediation-agent` (`wave1-gap2-bandit-semgrep-1`)  
**Completed:** 2026-06-05

---

## Scan Results

| Tool    | Severity        | Before | After |
|---------|-----------------|--------|-------|
| bandit  | HIGH / CRITICAL | 0      | 0     |
| bandit  | MEDIUM          | 0      | 0     |
| semgrep | ERROR           | 3      | 0     |
| semgrep | WARNING         | 2      | 0     |

---

## Fixes Applied

### 1. `src/codex_ml/plugins/registry.py:90` — `exec()` eliminated (3 semgrep ERRORs)
- **Issue:** Arbitrary lines from `.pth` distribution files executed via `exec(entry, {})`
- **Fix:** Replaced with `importlib.import_module()` gated by strict regex `^import\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$`
  — only simple `import a.b.c` patterns are allowed; complex/chained lines are safely skipped and logged
- Added `import importlib` and `import re`

### 2. `src/codex_ml/safety/filters.py:317` — `ast.literal_eval` false positive (1 semgrep ERROR)
- **Issue:** Local `insecure_eval.yml` rule incorrectly groups `ast.literal_eval` with `eval`/`exec` (CWE-94)
- **Fix:** Added `# nosemgrep: semgrep_rules.python.python.insecure.eval` with explanatory comment
  — `ast.literal_eval` is the *safe* alternative: only parses Python literals, cannot execute arbitrary code

### 3. `src/codex_ml/utils/safe_pickle.py:116` — acknowledged `pickle.loads` (1 semgrep WARNING)
- **Issue:** `pickle.loads` flagged despite existing defenses
- **Defenses already present:** `use_restricted_unpickler=True` default → `RestrictedUnpickler`; `logger.warning()` always emitted; `# nosec B301`
- **Fix:** Added `# nosemgrep: semgrep_rules.py-pickle-load` alongside existing `# nosec`

---

## Test Run
```
141 passed, 3 skipped in 12.87s  (plugins, safety, safe_pickle, registry modules)
```

---

## Evidence Chain
- **bandit:** 0 HIGH/CRITICAL before and after (baseline clean)
- **semgrep:** 5 findings → 0 after targeted fixes
- **Tests:** 141 pass, 0 fail
- **Artifacts:** `workbench/bandit_results.json`, `workbench/semgrep_results.json` (agent-produced)
