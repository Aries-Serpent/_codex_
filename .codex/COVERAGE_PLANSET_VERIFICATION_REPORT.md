# Coverage Planset Verification Report

> **Generated:** 2026-01-18
> **Purpose:** Verify all plansets exist for path from 2.87% to 100% coverage
> **Status:** ✅ PLANSETS VERIFIED

---

## Executive Summary

This document verifies that comprehensive plansets exist to achieve 100% test coverage from the current baseline of **2.87%** (as measured by CI) to **27.5%** (as measured locally) to the target of **100%**.

### Current State Analysis

| Metric | CI Value | Local Value | Discrepancy Reason |
|--------|----------|-------------|-------------------|
| Coverage | 2.87% | 27.5% | CI runs limited test subset |
| Threshold | 70% (noxfile.py) | 95% (pyproject.toml) | Configuration mismatch |
| Test Count | 1990+ created | Unknown executed | Not all tests discovered by CI |

### Root Cause: CI vs Local Coverage Gap

The CI reports 2.87% coverage because:
1. The pytest-xdist workers crash due to missing plugins
2. Many tests are skipped due to missing dependencies
3. The coverage only measures what actually runs

---

## Verified Plansets (Total: 1527+ lines)

### Primary Coverage Plansets ✅

| Planset | Path | Lines | Status |
|---------|------|-------|--------|
| Coverage Roadmap to 100% | `docs/COVERAGE_ROADMAP_TO_100_PERCENT.md` | 540 | ✅ Verified |
| Path to 100% Coverage | `.codex/cognitive_brain/PATH_TO_100_PERCENT_COVERAGE.md` | 361 | ✅ Verified |
| Coverage 100 Roadmap | `docs/testing/COVERAGE_100_ROADMAP.md` | 482 | ✅ Verified |
| Test Coverage Roadmap | `docs/testing/TEST_COVERAGE_ROADMAP.md` | 144 | ✅ Verified |

### Supporting Plansets ✅

| Planset | Path | Purpose |
|---------|------|---------|
| Phase 14 Test Coverage | `.codex/plans/PHASE_14_TEST_COVERAGE_IMPROVEMENT_PLANSET.md` | Foundation tests |
| Phase 15 Master Planset | `.codex/plans/PHASE_15_MASTER_PLANSET.md` | Advanced testing |
| Phase 16 Master Planset | `.codex/plans/PHASE_16_MASTER_PLANSET.md` | Documentation & security |
| Phase 17 Master Planset | `.codex/plans/PHASE_17_MASTER_PLANSET.md` | Reliability & performance |
| Phase 18 Master Planset | `.codex/plans/PHASE_18_MASTER_PLANSET.md` | Production deployment |
| Phase 19 Master Planset | `.codex/plans/PHASE_19_MASTER_PLANSET.md` | 100% coverage push |
| Phase 20 Master Planset | `.codex/plans/PHASE_20_MASTER_PLANSET.md` | Monitoring & automation |

---

## Coverage Path Summary

### Phase-by-Phase Target (from plansets)

| Phase | Coverage Target | Tests to Add | Duration |
|-------|-----------------|--------------|----------|
| Phase 14.0 | 0% → 30% | ~200 | 2 weeks |
| Phase 14.1 | 30% → 50% | ~180 | 3 weeks |
| Phase 14.2 | 50% → 70% | ~230 | 4 weeks |
| Phase 14.3 | 70% → 85% | ~150 | 3 weeks |
| Phase 14.4 | 85% → 100% | ~200 | 3 weeks |
| **Total** | **0% → 100%** | **~960 tests** | **15 weeks** |

### Module Priority Matrix (from plansets)

**Top 10 Priority Modules:**
1. `src/codex_ml/training/unified_training.py` - Score: 100
2. `src/codex_ml/cli/main.py` - Score: 100
3. `src/codex_ml/safety/moderation.py` - Score: 90
4. `src/codex_ml/data/loader.py` - Score: 90
5. `src/codex_ml/data/validation.py` - Score: 90
6. `src/codex/cli/main.py` - Score: 90
7. `src/codex/auth/oauth_manager.py` - Score: 90
8. `src/codex/security/storage.py` - Score: 90
9. `src/codex_ml/training/legacy_api.py` - Score: 80
10. `src/codex_ml/monitoring/codex_logging.py` - Score: 80

---

## Gap Analysis: Why CI Shows 2.87%

### Issue 1: pytest-xdist Worker Crashes
```
unrecognized arguments: --timeout=300 --timeout-method=thread --cov=...
maximum crashed workers reached: 8
```

**Root Cause:** pytest plugins not installed on xdist workers
**Fix Required:** Update workflow to install plugins before distribution

### Issue 2: Coverage Threshold Mismatch
```
pyproject.toml: fail_under = 95
noxfile.py: --cov-fail-under=70
```

**Root Cause:** Threshold changed in pyproject.toml but not in noxfile.py
**Fix Required:** Align thresholds or set realistic interim value

### Issue 3: Test Discovery
```
no tests ran in 126.27s
```

**Root Cause:** Tests not being discovered/executed properly
**Fix Required:** Fix test collection and xdist configuration

---

## Recommended Immediate Actions

### 1. Lower Coverage Threshold Temporarily
```python
# pyproject.toml
fail_under = 0  # Temporarily disable until CI fixed
```

### 2. Fix xdist Plugin Discovery
```yaml
# In workflow, ensure plugins installed before pytest
pip install pytest-timeout pytest-cov pytest-xdist pytest-rerunfailures
```

### 3. Align Threshold Configuration
```python
# noxfile.py - use pyproject.toml value
--cov-fail-under=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['tool']['coverage']['report']['fail_under'])")
```

---

## Verification Checklist

### Plansets Exist ✅
- [x] Primary coverage roadmap (docs/COVERAGE_ROADMAP_TO_100_PERCENT.md)
- [x] Path to 100% document (.codex/cognitive_brain/PATH_TO_100_PERCENT_COVERAGE.md)
- [x] Testing roadmaps (docs/testing/)
- [x] Phase plansets 14-20 (.codex/plans/)

### Plansets Are Complete ✅
- [x] Clear phase breakdown with targets
- [x] Module priority matrix defined
- [x] Test count estimates per phase
- [x] Duration estimates provided
- [x] Exit criteria defined

### Plansets Are Actionable ✅
- [x] Specific modules listed
- [x] Test categories defined
- [x] Coverage targets per module
- [x] Implementation steps provided

---

## Conclusion

**VERIFIED:** Comprehensive plansets exist to achieve 100% test coverage.

The gap between CI-reported (2.87%) and actual coverage is due to:
1. CI infrastructure issues (xdist crashes)
2. Threshold configuration mismatches
3. Test discovery problems

The plansets provide a clear 15-week path from 0% to 100% coverage with:
- 960+ tests to be created
- Clear phase-by-phase targets
- Module priority matrices
- Duration estimates

**Next Steps:**
1. Fix CI infrastructure issues
2. Lower threshold temporarily
3. Execute Phase 14.1+ per plansets
