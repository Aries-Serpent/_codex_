# Remaining Work - PR #2205 Gap Analysis

**Generated:** 2025-11-11  
**Current HEAD:** 04fcefc (Fix P1: keep_last checkpoint retention leak in best-k)  
**Status:** P1 fixes complete (6/6), Iteration 1-3 implementation complete (100%), Gap items in progress

---

## Summary

All P1 bugs fixed and all components from Iterations 1-3 implemented. This document tracks the remaining gap items to reach 99-100 target score and complete all acceptance gates.

---

## Gap Table Status

| Area | Current State | Remaining To Do | Acceptance Criteria | Priority | Status |
|------|---------------|-----------------|---------------------|----------|--------|
| **Tests Coverage** | Regression tests added (8 tests); target ≥95% set | Generate coverage report; verify per-file thresholds; plan for 96-99% | pytest-cov XML/HTML; ≥95% on new/changed modules | HIGH | 🔄 READY |
| **Lint/Style** | Minor fixes applied; E501/E402/E741 pending | One-shot repo-wide E501 fix; targeted E402; rename E741 | ruff/black clean; no new warnings | MEDIUM | 📋 PLANNED |
| **Type Checking** | Type hints present; not executed | Run mypy on src/; address typing gaps | mypy passes; report attached | MEDIUM | 📋 PLANNED |
| **Security Gate** | Nox session unified; allowlist present | Run nox -s security; attach artifacts/security_report.json | No HIGH/CRITICAL unallowlisted | HIGH | 🔄 READY |
| **Determinism** | CLI compare supports check | Add cross-process repro tests; env snapshot | Determinism proof; env snapshot artifact | MEDIUM | 📋 PLANNED |
| **Config Validator** | Fixed + tested; nox session added | Run nox -s validate-configs in verification | Session green; logs attached | HIGH | 🔄 READY |
| **AST CLI** | Implemented with tests | Verify --json output; stable exit codes | Integration tests pass | MEDIUM | ✅ DONE |
| **Artifacts** | IMPLEMENTATION_STATUS.md created | Generate coverage.xml, security_report.json, validation logs | All artifacts committed/attached | HIGH | 🔄 IN PROGRESS |

---

## Detailed Action Items

### 1. Tests Coverage Report (HIGH PRIORITY - READY TO EXECUTE)

**Current State:**
- 8 regression tests added for P1 fixes
- All test files pass syntax validation
- Target: ≥95% for new/changed modules

**Action Items:**
```bash
# Generate coverage report
nox -s tests  # Runs pytest with coverage
# Or manually:
pytest --cov=src/codex_ml --cov=src/codex --cov-report=xml --cov-report=html --cov-report=term-missing

# Review coverage.xml and htmlcov/index.html
# Verify ≥95% on:
# - src/codex_ml/evaluation/loop.py
# - src/codex_ml/evaluation/cli.py
# - src/codex_ml/checkpointing/bestk.py
# - src/codex_ml/logging/registry.py
# - tools/validate_experiments.py
```

**Acceptance:**
- coverage.xml artifact generated and committed to artifacts/
- Coverage ≥95% on all new/changed modules
- Plan documented for reaching 96-99% in next iteration

---

### 2. Security Gate Execution (HIGH PRIORITY - READY TO EXECUTE)

**Current State:**
- Unified nox security session implemented (commit 749b1eb)
- Includes: pip-audit + allowlist + bandit + gitleaks
- security_allowlist.json present

**Action Items:**
```bash
# Run security scan
nox -s security

# This generates artifacts/security_report.json
# Verify no HIGH/CRITICAL vulnerabilities (or all allowlisted)
# Check bandit and gitleaks outputs
```

**Acceptance:**
- artifacts/security_report.json generated and committed
- No HIGH/CRITICAL vulnerabilities outside allowlist
- Bandit and gitleaks scans complete without blocking issues

---

### 3. Config Validator Execution (HIGH PRIORITY - READY TO EXECUTE)

**Current State:**
- validate-configs nox session added (commit 749b1eb)
- TOML/JSON validation fixed (commits 1341f45, 2dcc361)
- Schema exclusion working (commit 2dcc361)

**Action Items:**
```bash
# Run config validator
nox -s validate-configs

# Or manually:
python tools/validate_experiments.py \
  --schema configs/schemas/experiments.schema.json \
  --paths configs/experiments/

# Verify validation passes
# Check that schema files are excluded
```

**Acceptance:**
- validate-configs session runs successfully
- Validation logs show only config files validated (not schemas)
- No false failures

---

### 4. Lint/Style Normalization (MEDIUM PRIORITY - PLANNED)

**Current State:**
- Repository follows general style guidelines
- Some E501 (line length), E402 (import order), E741 (ambiguous names) remain

**Action Items:**
```bash
# Check current lint status
nox -s lint

# Or manually:
ruff check .
black --check .

# Fix issues:
# - E501: Use ruff or black to auto-format long lines
# - E402: Move imports to top of file where possible
# - E741: Rename ambiguous variable names (l, O, I)

# Auto-fix where safe:
ruff check --fix .
black .
```

**Acceptance:**
- ruff check . passes with no errors
- black --check . passes
- No new warnings introduced

---

### 5. Type Checking (MEDIUM PRIORITY - PLANNED)

**Current State:**
- Type hints present in most modules
- mypy not yet executed on PR changes

**Action Items:**
```bash
# Run type checker
nox -s typecheck

# Or manually:
mypy src/

# Address common issues:
# - Missing return type annotations
# - Protocol implementations
# - Optional types
# - Any usage reduction
```

**Acceptance:**
- mypy passes on src/ directory
- Type checking report attached to PR
- No blocking type errors

---

### 6. Determinism Tests (MEDIUM PRIORITY - PLANNED)

**Current State:**
- CLI report command supports --compare for determinism check
- Exit code 4 on mismatch

**Action Items:**
```bash
# Create cross-process reproducibility tests
# Example in tests/repro/test_determinism.py:
# 1. Run evaluation twice with same seed
# 2. Compare outputs byte-for-byte
# 3. Verify hash equality

# Add env snapshot test
# Capture environment variables, package versions
# Store in artifacts/env_snapshot.json
```

**Acceptance:**
- Determinism tests pass
- env_snapshot.json artifact generated
- Proof of reproducibility documented

---

### 7. Artifacts Collection (HIGH PRIORITY - IN PROGRESS)

**Current State:**
- IMPLEMENTATION_STATUS.md created
- Some artifacts generated

**Required Artifacts:**
```
artifacts/
├── coverage.xml              # From pytest-cov
├── htmlcov/                  # Coverage HTML report
├── security_report.json      # From nox -s security
├── validation_logs.txt       # From nox -s validate-configs
├── env_snapshot.json         # Environment details
└── docs/                     # API docs (if SKIP_OPTIONAL=1)
```

**Acceptance:**
- All required artifacts generated
- Artifacts committed to repository or linked in PR
- Artifact checksums documented

---

## Next Steps

### Immediate (Can execute now):
1. ✅ Run `nox -s tests` and generate coverage report
2. ✅ Run `nox -s security` and commit security_report.json
3. ✅ Run `nox -s validate-configs` and verify output

### Short-term (This iteration):
4. 📋 Run `nox -s lint` and fix reported issues
5. 📋 Run `nox -s typecheck` and address type errors
6. 📋 Commit all artifacts to artifacts/ directory

### Medium-term (Next iteration - 96-99% target):
7. 📋 Add determinism tests to tests/repro/
8. 📋 Add edge case tests to reach 96-99% coverage
9. 📋 Add golden baseline tests for regression prevention

---

## Notes

- All P1 bugs are now fixed (6 total)
- All components from Iterations 1-3 are implemented (100%)
- Remaining work is primarily validation, documentation, and quality gates
- No blocking issues preventing merge to 0D_base_
- Ready for promotion to main after gap items addressed

---

## References

- Execution Runbook: `reports/plans/_codex__ExecutionRunbook_Itr1_to_Itr3.md`
- Implementation Status: `IMPLEMENTATION_STATUS.md`
- Gap Table: Comment #3518311364
- Approval Gate: Comment #3518195426

---

**Last Updated:** 2025-11-11 (after commit 04fcefc)
