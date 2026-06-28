# Agent Brief: Wave 4 - MyPy Type Annotation Hardening

**Target Agent:** mypy-manager-agent  
**Authority:** @mbaetiong (Autonomous GO CONTINUE)  
**Timeline:** Continuous (parallel with Waves 2-3-5)  
**Python Version:** 3.12+  
**Target:** 100% mypy passing (strict mode)  
**Status:** READY FOR DISPATCH  
**Coordinating Brief:** AGENT_BRIEF_STAGE_5_WAVE2_DELEGATION.md (Stage 5, Phase 6 Wave 1)

---

## Mission

Resolve mypy type annotation errors from Phase 5 Lane 5.2B analysis to achieve 100% passing type checks in strict mode. Modernize type hints (List→list, Dict→dict, Optional[X]→X|None) for Python 3.12+ compatibility and improve IDE support.

---

## Executive Summary

Phase 5 Lane 5.2B baseline:
- **Mypy Errors:** ~320-450 errors (categories TBD from Phase 5 output)
- **Error Categories:** Untyped functions, missing annotations, incompatible overrides, type narrowing issues
- **Scope:** Core modules (codex/, ml/, cognitive_brain/, utils/)
- **Timeline:** Continuous, parallel execution with Waves 2-3-5
- **Complexity:** MEDIUM (modernization + strict mode adoption)

---

## Type System Modernization

### Phase 1: Python 3.12 Syntax Updates (Week 1)

**Tasks:**

1. **List/Dict/Set/Tuple generics**
   ```python
   # Before (Python <3.9 style)
   from typing import List, Dict, Set, Tuple
   def func(items: List[str]) -> Dict[str, int]: ...
   
   # After (Python 3.9+ style)
   def func(items: list[str]) -> dict[str, int]: ...
   ```
   - Scope: All modules in `src/codex/`
   - Estimated effort: 40-60 files
   - Automated via: `python -m libcst.tool codemod remove_typing_imports ...`

2. **Union → X | Y syntax**
   ```python
   # Before
   from typing import Union, Optional
   def func(x: Union[str, int]) -> Optional[str]: ...
   
   # After
   def func(x: str | int) -> str | None: ...
   ```
   - Scope: All modules with Union/Optional
   - Estimated effort: 80-120 files
   - Automated via: libcst codemod union_to_pipe

3. **Remove `from __future__ import annotations` if applicable**
   - Verify if any modules still use PEP 563 (deferred evaluation)
   - Convert to runtime-evaluated annotations if applicable

### Phase 2: Missing Type Annotations (Week 1-2)

**Common patterns from Phase 5:**

1. **Untyped functions (most common)**
   ```python
   # Before
   def process_data(data):  # Missing type annotations
       return transform(data)
   
   # After
   def process_data(data: dict[str, Any]) -> dict[str, Any]:
       return transform(data)
   ```
   - Categories: CLI functions, utility functions, callbacks, internal helpers
   - Strategy: Add annotations to public APIs first; internal functions after

2. **Incomplete annotations**
   ```python
   # Before
   def handle_request(req) -> None:  # Missing input type
       pass
   
   # After
   def handle_request(req: Request) -> None:
       pass
   ```

3. **Generic functions without type parameters**
   ```python
   # Before
   def cache_get(key):
       return self.cache[key]
   
   # After
   def cache_get(self, key: str) -> Any:  # or use TypeVar T
       return self.cache[key]
   ```

### Phase 3: Strict Mode Compliance (Week 2-3)

**Mypy strict mode requirements:**

1. **Disallow untyped defs** (`--disallow-untyped-defs`)
   - All function definitions must have return type annotations
   - All parameters must have type annotations
   - Estimated files: 60-100

2. **Disallow untyped calls** (`--disallow-untyped-calls`)
   - All calls to untyped functions must be checked
   - May require wrapping legacy APIs with stubs

3. **Disallow incomplete defs** (`--disallow-incomplete-defs`)
   - Enforce complete annotations on all callables
   - No implicit `Any` without explicit annotation

4. **Disallow unimported types** (`--no-implicit-reexport`)
   - Require explicit imports for all type references
   - Clean up __init__.py re-exports

5. **Warn no return** (`--warn-no-return`)
   - All code paths must have return statements
   - Enforce explicit control flow

### Phase 4: Type Narrowing & Advanced (Week 3+)

**Advanced type system improvements:**

1. **TypeVar for generic functions**
   ```python
   from typing import TypeVar
   T = TypeVar('T')
   def first(seq: list[T]) -> T: ...
   ```

2. **TypedDict for structured dicts**
   ```python
   from typing import TypedDict
   class Config(TypedDict):
       name: str
       value: int
   ```

3. **Protocol for structural typing**
   ```python
   from typing import Protocol
   class Closeable(Protocol):
       def close(self) -> None: ...
   ```

4. **Overload for multiple signatures**
   ```python
   from typing import overload
   @overload
   def process(x: str) -> str: ...
   @overload
   def process(x: int) -> int: ...
   ```

---

## Mypy Configuration

**pyproject.toml [tool.mypy]:**

```ini
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_untyped_calls = true
disallow_incomplete_defs = true
disallow_unimported_types = true
no_implicit_reexport = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict = true

[tool.mypy-tests.*]
ignore_errors = true
disallow_untyped_defs = false
```

**Key:** Enable strict mode for core modules; relax for tests.

---

## Baseline & Remediation

### Phase 5 Lane 5.2B Error Categories (TBD)

From Phase 5 Lane 5.2B output, expected categories:

| Category | Count (est.) | Priority | Effort | Timeline |
|----------|--------------|----------|--------|----------|
| Untyped functions | 80-120 | HIGH | 20-40 hrs | Week 1-2 |
| Missing annotations | 60-100 | HIGH | 15-30 hrs | Week 1-2 |
| Incompatible overrides | 30-50 | MEDIUM | 10-20 hrs | Week 2-3 |
| Type narrowing issues | 40-60 | MEDIUM | 15-25 hrs | Week 2-3 |
| Invalid type args | 20-30 | LOW | 5-10 hrs | Week 3+ |
| Return type issues | 20-30 | MEDIUM | 8-15 hrs | Week 2-3 |
| **Total** | **250-390** | | **73-140 hrs** | |

**Estimated total effort:** 73-140 hours (10-18 days continuous, or ~2-3 weeks with other waves)

---

## Module Priority Order

### Tier 1: Core Infrastructure (Week 1)
1. `src/codex/utils/` - common types, utilities
2. `src/codex/errors.py` - exception classes
3. `src/codex/logging/` - logging configuration

### Tier 2: Public APIs (Week 2)
4. `src/codex/cli.py` - CLI entry points
5. `src/codex/ml/` - ML module public interfaces
6. `src/codex/cognitive_brain/` - cognitive brain APIs

### Tier 3: Integration (Week 3)
7. `src/codex/bridge/` - bridge implementations
8. `src/codex/data/` - data handling modules
9. Remaining internal modules

---

## Success Criteria

- ✅ All mypy errors resolved (0 errors in strict mode)
- ✅ Python 3.12 syntax modernization completed (List→list, etc.)
- ✅ All public APIs fully typed (no Any without justification)
- ✅ Strict mode enabled in pyproject.toml for core modules
- ✅ Type stubs created for external dependencies (if needed)
- ✅ Documentation updated with type annotation patterns
- ✅ No breaking changes to existing code (refactor type system only)
- ✅ CI/CD configured to run `mypy --strict` on every commit

---

## Dependencies & Preconditions

**Phase 6 Prerequisites:**
- Stage 4 completion: 79 TIER-1 tests implemented ✅
- Mypy configuration available (pyproject.toml) ✅

**External Dependencies:**
- mypy package (latest stable)
- Python 3.12+ runtime for testing
- Type stub packages (types-*) for external libraries
- IDE with mypy integration (optional, for local testing)

**Phase 5 Reference Data:**
- Phase 5 Lane 5.2B mypy error report (.json or .txt)
- Module dependency graph (for priority ordering)

---

## Constraints & Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Type narrowing false positives | MEDIUM | Review mypy output carefully; use `# type: ignore` sparingly with comment |
| Performance regression from complex types | LOW | Verify no performance regression in benchmarks after typing |
| Interaction with other waves | MEDIUM | Coordinate with Wave 2 (duplication) on refactored type utilities |
| Long type annotations (line length) | LOW | Use type aliases where helpful; ignore line length warnings for type defs |
| External library type stubs missing | MEDIUM | Create stubs for major dependencies (rope, mlflow, etc.) if needed |

---

## Dispatch Options

### Option A: Incremental (Recommended)
- Types added module-by-module as dependencies allow
- Strict mode enabled gradually
- Risk: Low (smaller changes, easier review)
- Timeline: 2-3 weeks continuous
- Parallelization: YES (independent of Waves 2-3-5)

### Option B: Bulk (Aggressive)
- All modernization in 2-3 large commits
- Risk: High (large diffs, harder review)
- Timeline: 5-7 days intense work
- Not recommended

### Option C: Staged (Balanced)
- Week 1: Python 3.12 syntax + missing annotations (Tier 1-2 modules)
- Week 2: Strict mode compliance + type narrowing (Tier 2-3 modules)
- Week 3+: Advanced typing (TypeVar, Protocol, Overload)
- Risk: Medium (balanced approach)
- Timeline: 2-3 weeks
- Recommended approach

**Recommended Approach:** Option C (Staged Incremental)

---

## Agent Instructions

### Pre-Dispatch Checklist

- [x] Authority verified: @mbaetiong pre-approved Wave 4
- [x] Mypy configuration ready (pyproject.toml)
- [x] Python 3.12 environment available
- [x] Phase 5 Lane 5.2B mypy report available
- [x] Communication channels active (dashboard)

### Dispatch Command

```bash
@copilot-assignment
Agent: mypy-manager-agent
Brief: AGENT_BRIEF_STAGE_5_WAVE4_MYPY.md
Authority: @mbaetiong (Autonomous GO CONTINUE)
Mode: Staged incremental (Option C recommended)
Timeline: Continuous (parallel with Waves 2-3-5)
Target: 100% mypy strict mode compliance, Python 3.12+ syntax
Coordination: PHASE_6_WAVE2_COORDINATION_DASHBOARD.md

PROCEED WITH TYPE SYSTEM HARDENING
```

---

## Output Artifacts

**Commits:**
- Format: `feat(types): Wave 4 — <module> strict type annotations (<category>)`
- Example: `feat(types): Wave 4 — utils module to strict typing (modernize generics)`

**PRs:**
- 1 PR per week or per Tier (Tier 1 → PR 1, Tier 2 → PR 2, etc.)
- All tests passing (regression suite)
- Mypy output showing 0 errors in strict mode
- Type coverage metrics attached

**Documentation:**
- Type annotation guide: `.codex/TYPE_ANNOTATION_GUIDE.md`
- Per-module summary: `.codex/WAVE_4_MODULE_TYPING_SUMMARY.md`
- Final report: `.codex/PHASE_6_WAVE_4_FINAL_REPORT.md`

---

**Coordinating Authority:** @mbaetiong  
**Autonomous Mode:** GO CONTINUE (all decision points approved)  
**Parallel Dispatch:** YES (independent of Waves 2-3-5)  
**Escalation Path:** Direct to @mbaetiong or agent-orchestrator
