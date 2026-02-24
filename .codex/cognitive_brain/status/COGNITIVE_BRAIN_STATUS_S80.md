# Cognitive Brain Status — Session S80

**Generated**: 2026-02-24  
**Session**: S80  
**PR**: #3348 (`copilot/sub-pr-3248-again`)  
**Base**: S79b (commit `3c43018`)

---

## Summary

S80 applied targeted fixes for 5 CI failure categories identified through systematic
CI log analysis and the DRQ-S75 Deep Research Report (comment #3948645073).

---

## S80 Changes Applied

### Fix 1 — `strategies.py` F401 (auto-fix CI blocker)
- **File**: `src/codex_ml/training/strategies.py:19`
- **Issue**: Module-level `import warnings` unused (F401); local import inside
  `LegacyStrategy.run()` is the only usage.
- **Fix**: Removed module-level `import warnings`.

### Fix 2 — `unified_training.py` F401 + I001 (auto-fix CI blocker)
- **File**: `src/codex_ml/training/unified_training.py:46`
- **Issue**: `resolve_strategy` imported directly but called via `strategies.resolve_strategy()`.
  Ruff F401 + I001 (import ordering after ruff --fix applied).
- **Fix**: Added `# noqa: F401  (re-exported for monkeypatching)` to keep the export
  for test monkeypatching compatibility; applied `ruff --fix` for I001.

### Fix 3 — `codex_ml.__getattr__` subpackage fallback (quick-suite blocker)
- **File**: `src/codex_ml/__init__.py`
- **Issue**: Custom `__getattr__` raises `AttributeError` for names not in
  `_EXPORT_MAP`, including sub-packages like `interfaces`. When pytest's monkeypatch
  resolves `"codex_ml.interfaces.tokenizer._AutoTokenizer"` via attribute access,
  `codex_ml.interfaces` was inaccessible before the subpackage had been imported in
  the current process, causing collection-time fixture setup to fail.
- **Fix**: Updated `__getattr__` to fall back to
  `import_module(f"codex_ml.{name}")` before raising `AttributeError`.

### Fix 4 — `solution_xml.py` nosec B314 (DRQ-S75-001)
- **File**: `src/codex/dynamics/solution_xml.py:32`
- **Issue**: Bandit B314 (CWE-611) alert fired on `from xml.etree.ElementTree import
  Element, SubElement` — false positive because these are used for tree
  *construction* only (not parsing), which is not an XXE attack surface.
- **Fix**: Added `# nosec B314` with justification comment per DRQ-S75-001-R1.

### Fix 5 — `retrieval/stores/__init__.py` FAISS guard (DRQ-S75-003 priority 1)
- **File**: `src/codex/retrieval/stores/__init__.py`
- **Issue**: `from .faiss_store import FAISSStore` unconditional. While the class
  definition loads successfully even without `faiss-cpu` (import faiss is deferred
  to `__init__`), tests that instantiate `FAISSStore` fail in minimal CI envs.
  Research confirmed the factory.py guarded pattern is the correct model.
- **Fix**: Wrapped import in `try/except ImportError`; `FAISSStore = None` fallback
  in minimal envs; added `_FAISS_AVAILABLE` sentinel for guarded downstream use.

---

## Dependabot PR Triage (S80)

| PR | Package | Old → New | Decision | Rationale |
|----|---------|-----------|----------|-----------|
| #3356 | `black` | 25.9.0 → 26.1.0 | ⏳ DEFER | Major version; 2026 stable style reformats many files |
| #3354 | `opentelemetry-sdk` | 1.37.0 → 1.39.1 | ⏳ DEFER | 2 breaking changes: `LogData` removed, class renames |
| #3352 | `dvc` | 3.64.2 → 3.66.1 | ⏳ DEFER | pathspec `<1` restriction conflicts with black 26.1.0 |
| #3349 | `transformers` | 5.0.0 → 5.2.0 | ⏳ DEFER | 3 breaking changes in core ML dep; compatibility audit needed |

---

## DRQ Research Addenda Applied (S80)

Per DRQ-S75 Deep Research Report v2 (comment #3948645073):

### DRQ-S75-001 — defusedxml
- **Status**: Research applied → Fix 4 (nosec B314 on solution_xml.py)
- **Open item**: `defuse_stdlib()` never called in production code; recommend adding
  to application startup for defense-in-depth. Filed as S81 recommendation.

### DRQ-S75-002 — cuDNN guard
- **Status**: R1 rule enforced (engine_hf_trainer.py, S79b). Deep research confirms
  `training/functional_training.py:443` assert-without-guarantee risk on CUDA.
  Fix: wrap assert with `set_reproducible()` auto-call or better error message.
  Filed as S81 recommendation.

### DRQ-S75-003 — FAISS import
- **Status**: Research applied → Fix 5 (guarded import in stores/__init__.py)
- **Open item**: `RetrievalEngine` still directly instantiates `FAISSStore` — should
  use `VectorStoreFactory.create("faiss", ...)` instead. Filed as S81 recommendation.

---

## CI Status After S80

| Suite | Expected Status | Notes |
|-------|----------------|-------|
| Fast (pre-commit) | ✅ PASS | F401/I001 fixed; trailing-ws clean |
| Quick | ✅ PASS | interfaces __getattr__ fix; S79b mcp_cli/data_utils/plugin_loader fixes |
| Slow | ✅ PASS | S79 checkpoint/epochs fixes still in effect |

---

## Pattern Learning

- **RF-13**: `__getattr__` in package `__init__.py` must fall back to
  `import_module(f"{__name__}.{name}")` before raising `AttributeError` to support
  pytest monkeypatch string-path resolution of subpackages.
- **RF-14**: Module-level `import X` where X is only used inside a method's own
  `import X` (local) is reported as F401 by ruff — remove the module-level import.
