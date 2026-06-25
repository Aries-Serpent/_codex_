# Post-Merge Environment Baseline & Dependency Audit

**Created**: 2026-06-25T22:20:00Z  
**Purpose**: Establish baseline of pre-existing environmental issues that post-merge Copilot agent sessions will encounter  
**Status**: Pre-merge snapshot (baseline for post-merge validation)

---

## Environmental Context

### Python Version
- **Requirement**: `>=3.12` (enforced in `pyproject.toml:12`)
- **CI runner default**: Python 3.12.x
- **Post-merge expectation**: All sessions will have Python >=3.12

### Known Pre-Existing Dependency Gaps

These packages are either missing or optional and will cause test collection errors if not explicitly installed:

#### Critical Optional Dependencies
| Package | Version | Location | Purpose | Impact |
|---------|---------|----------|---------|--------|
| `zstandard` | (latest) | `requirements/dev.txt:23` | Data compression | Test collection failures if missing |
| `sqlalchemy` | `==2.0.50` | `requirements/lock.txt` (transitive) | Database ORM | Import errors in certain test modules |

#### Import Pattern Failures
Known test collection errors that occur in pre-existing baseline:
- Modules importing `zstandard` fail silently if package is missing
- Modules importing `sqlalchemy` fail if only transitive dependency exists (not explicitly installed)
- Some fixture definitions require both packages to be present

---

## Test Collection Baseline

### Pre-Merge Snapshot
- **Date**: 2026-06-25T22:20:00Z
- **Command**: `pytest --collect-only 2>&1`
- **Expected Status**: Test collection completes with known errors for optional deps
- **Baseline file**: To be generated as `.codex/PRE_MERGE_TEST_COLLECTION_STATUS.json`

### Known Collection Errors (Pre-Existing)
These errors are EXPECTED and should NOT trigger post-merge reversion:
1. Import errors for `zstandard` - affects data compression test modules
2. Import errors for `sqlalchemy` - affects database ORM test modules
3. Fixture setup failures due to missing optional dependencies

### Collection Error Classification
```
PRE-EXISTING (do not revert for these):
  - Missing optional deps (zstandard, sqlalchemy)
  - Import failures in specialized modules (RAG, database, compression)
  - Fixture setup errors for optional-dep-dependent tests

NEW ERRORS (trigger investigation/reversion):
  - Import errors in core modules (src/codex, config, CLI)
  - Test collection failures in previously passing files
  - Python path or package structure errors
  - YAML parsing errors in copilot-setup-steps.yml
```

---

## Copilot Setup Environment State

### copilot-setup-steps.yml Snapshot

**File**: `.github/workflows/copilot-setup-steps.yml`  
**Critical sections** (DO NOT REFACTOR):
- Lines 132-170: Session context preload step
  - Uses block scalar syntax `run: |`
  - Loads memory, policy, accountability, PDA loop state
  - No braces or flow-scalar syntax allowed (YAML parsing breaks)

**Working CCA configuration** (lines 99-101):
```yaml
COPILOT_AGENT_CCA_VERSION_LOCK: "stable"
COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"
COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"
```

### Environment Variables Injected
- `CODEX_MASTER_KEY` - primary GitHub token
- `CODEX_BACKUP_KEY` - fallback GitHub token
- CCA version lock vars (deduplication, turn isolation)
- LFS opt-in controls: `GIT_LFS_SKIP_SMUDGE=1` (default)

---

## Pre-Merge Dependency Verification

### Installation Commands for Post-Merge
If post-merge session encounters missing optional dependencies:

```bash
# Install optional test dependencies
pip install zstandard sqlalchemy

# Re-run test collection to verify resolution
pytest --collect-only 2>&1 | tee .codex/post-merge-collection-after-install.txt

# If collection now succeeds with same test count:
#   → Document: "Installing optional deps resolved pre-existing collection errors"
# If collection still has errors:
#   → Investigate specific import errors: python -c "import zstandard"
```

---

## Post-Merge Validation Protocol

### Step 1: Capture Baseline (Post-merge session's first action)
```bash
# After checkout, before any other work:
pytest --collect-only 2>&1 | tee .codex/POST_MERGE_TEST_COLLECTION_STATUS.txt
```

### Step 2: Compare Against Pre-Merge
- Diff pre-merge vs. post-merge collection output
- Generate `.codex/TEST_COLLECTION_DIFF_POST_MERGE.md`
- Document any NEW errors (regression indicator)

### Step 3: Classification Decision
```
IF (same errors as baseline) → "Pre-existing environmental issues"
   ACTION: Document, proceed with post-merge work
   
IF (fewer errors) → "Post-merge improved dependency handling"
   ACTION: Log as improvement, proceed
   
IF (new errors in core modules) → REGRESSION DETECTED
   ACTION: Escalate to @mbaetiong, prepare reversion
```

---

## Reversion Decision Tree

**See**: `.codex/POST_MERGE_REVERSION_PROTOCOL.md` (separate document)

### Summary Triggers
- ✅ PROCEED if: Collection errors unchanged vs. baseline
- ✅ PROCEED if: Only missing optional deps (can be installed)
- ❌ REVERT if: New YAML errors in copilot-setup-steps.yml
- ❌ REVERT if: Python environment incompatibility
- ❌ REVERT if: 10+ new test collection errors

---

## Future Session Expectations

Post-merge agent will encounter:
1. Missing `zstandard` and `sqlalchemy` in test environment (PRE-EXISTING)
2. Specific test files will fail collection until deps installed
3. Optional dependency failures are NOT a blocker
4. Core module test collection should pass

This document exists to make post-merge agent aware these are baseline issues, not regressions.
