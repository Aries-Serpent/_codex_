# Python 3.12 Migration Plan

**Last Updated:** 2026-06-22

**Status**: Temporary — `requires-python = ">=3.11,<3.13"` (supports both)
**Target**: `requires-python = ">=3.12,<3.13"` (3.12-only, strict)
**Blocker**: Base branch `copilot/investigate-coherence-issue` CI uses Python 3.11
**Owner**: @mbaetiong
**Created**: 2026-02-19

---

## Background

This codebase originally required Python `>=3.12,<3.13`. When this PR was stacked on
`copilot/investigate-coherence-issue`, its GitHub Actions workflows run Python 3.11,
causing `pip install` failures. The temporary fix is `>=3.11,<3.13`.

**Evidence that the codebase IS 3.11-compatible** (static analysis run 2026-02-19):
- 0 files with Python 3.12-specific syntax (`type X =` PEP 695, relaxed f-string quotes)
- All `src/` and `tests/` files parse cleanly under `ast.parse(..., feature_version=(3,11))`
- `tomllib` imports all have `tomli` fallbacks guarded by `python_version < '3.11'`
- 735 files already use `from __future__ import annotations` (PEP 563 compatibility)

---

## Temporary Fix (in place)

```toml
# pyproject.toml line 15
requires-python = ">=3.11,<3.13"  # Temporarily support 3.11 for base branch CI compatibility
```

This is safe for production. No 3.11-incompatible syntax exists in the codebase.

---

## Phase 1 — Fix the Base Branch (Prerequisite)

**Goal**: Upgrade CI in `copilot/investigate-coherence-issue` to Python 3.12.

| Step | Action | File(s) | Owner |
|------|--------|---------|-------|
| 1.1 | Update workflow `python-version` to `"3.12"` in base branch | `.github/workflows/*.yml` | @mbaetiong |
| 1.2 | Confirm all tests pass on base branch with Python 3.12 | CI | @mbaetiong |
| 1.3 | Merge / rebase base branch | — | @mbaetiong |

**Grep to find all workflow files setting python-version:**
```bash
grep -rn "python-version" .github/workflows/ | grep -v "3.12"
```

---

## Phase 2 — Restore `>=3.12,<3.13` Constraint

Once base branch CI is on Python 3.12:

```toml
# pyproject.toml
requires-python = ">=3.12,<3.13"
```

Remove the `# Temporarily support 3.11` comment.

**Verification steps:**
```bash
# 1. Confirm no 3.11-fallbacks needed
grep -rn "tomli" pyproject.toml
# Should all have: python_version < '3.11' (still correct — handles <3.11 edge cases)

# 2. Run full test suite on 3.12
python3.12 -m pytest tests/ -x -q

# 3. Confirm CI passes
git push && # watch GitHub Actions
```

---

## Phase 3 — Optional: Adopt Python 3.12 Features (Enhancement)

With the constraint locked to 3.12+, these improvements become available:

### 3.1 `type` statement aliases (PEP 695)
Replace verbose `TypeAlias` forms:
```python
# Before (3.11 style)
from typing import TypeAlias
DecisionMap: TypeAlias = dict[str, float]

# After (3.12 native)
type DecisionMap = dict[str, float]
```

### 3.2 Generic classes with `[T]` syntax (PEP 695)
```python
# Before (3.11 style)
from typing import Generic, TypeVar
T = TypeVar("T")
class Stack(Generic[T]): ...

# After (3.12 native)
class Stack[T]: ...
```

### 3.3 `tomllib` — remove `tomli` fallback entries
Once `requires-python = ">=3.12"`, `tomllib` is always available (added in 3.11):
```toml
# pyproject.toml — remove these lines:
"tomli>=2.0; python_version < '3.11'",
```

### 3.4 Remove `from __future__ import annotations` (optional)
Since 3.12 evaluates annotations lazily by default for most use-cases, but removing
`from __future__ import annotations` changes runtime behaviour — only do this after
verifying no code relies on string-form annotations at runtime.

**Automated scan:**
```bash
grep -rn "get_type_hints\|__annotations__" src/ | grep -v "__pycache__"
```

---

## Phase 4 — Lock Upper Bound When 3.13 is Stable

When Python 3.13 GA ships and all dependencies support it:

```toml
requires-python = ">=3.12"   # or ">=3.12,<3.14" once 3.13 is tested
```

Run the same AST compatibility scan for 3.13:
```bash
python3 -c "
import ast, os
for root, _, files in os.walk('src'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f)) as fh:
                ast.parse(fh.read(), feature_version=(3,13))
"
```

---

## Checklist

- [x] Static analysis: 0 files with 3.12-only syntax (verified 2026-02-19)
- [x] Temporary fix applied: `>=3.11,<3.13` in `pyproject.toml`
- [ ] Phase 1: Base branch CI upgraded to Python 3.12
- [ ] Phase 2: `requires-python` restored to `>=3.12,<3.13`
- [ ] Phase 3: Optional — adopt PEP 695 generics and type aliases
- [ ] Phase 4: Upper bound relaxed after 3.13 validation

---

## References

- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) (Python 3.12)
- [PEP 563 — Postponed Evaluation of Annotations](https://peps.python.org/pep-0563/) (Python 3.7+)
- [tomllib — stdlib TOML parser](https://docs.python.org/3/library/tomllib.html) (Python 3.11+)
- [What's New in Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
