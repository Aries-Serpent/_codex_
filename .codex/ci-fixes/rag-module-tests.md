# CI Fix Tracking: RAG Module Tests

**Status**: ✅ Fixed
**Opened**: 2026-07-01T21:37:24Z
**Fixed**: 2026-07-01T21:43:51Z
**Workflow**: RAG Module Tests
**Run**: https://github.com/Aries-Serpent/_codex_/actions/runs/28549143166
**Issue**: #5183

## Root Cause

Dependency version conflict between workflow pins and `pyproject.toml` constraints:

**Workflow (.github/workflows/test-rag.yml)**:
- `pytest==9.0.2` (exact pin)
- `pytest-cov==7.0.0` (exact pin)
- `pytest-xdist==3.8.0` (exact pin)
- `pytest-timeout==2.3.1` (exact pin)
- `pytest-rerunfailures==14.0` (exact pin)
- `pytest-randomly==3.16.0` (exact pin)

**pyproject.toml [project.optional-dependencies.dev]**:
- `pytest>=9.0.3,<10.0.0` (requires minimum 9.0.3)
- `pytest-cov>=4.1.0,<6.0.0` (requires 4.x or 5.x, not 7.x)
- `pytest-xdist>=3.5.0,<4.0.0`
- `pytest-timeout>=2.2.0,<3.0.0`
- `pytest-rerunfailures>=12.0`
- `pytest-randomly>=3.15`

**Result**: pip dependency resolver `ResolutionImpossible` / `No matching distribution` error

## Fix Applied

Updated `.github/workflows/test-rag.yml` lines 176-178 to align with `pyproject.toml` constraints:

```diff
 PYTEST_PLUGINS=(
-  "pytest==9.0.2"
-  "pytest-cov==7.0.0"
-  "pytest-xdist==3.8.0"
-  "pytest-timeout==2.3.1"
-  "pytest-rerunfailures==14.0"
-  "pytest-randomly==3.16.0"
+  "pytest>=9.0.3,<10.0.0"
+  "pytest-cov>=4.1.0,<6.0.0"
+  "pytest-xdist>=3.5.0,<4.0.0"
+  "pytest-timeout>=2.2.0,<3.0.0"
+  "pytest-rerunfailures>=12.0"
+  "pytest-randomly>=3.15"
   "coverage>=7.10.6,<8"
 )
```

## Verification

The fix aligns workflow test dependency installation with `pyproject.toml` constraints, resolving the pip dependency conflict during the "Install dependencies" step.
