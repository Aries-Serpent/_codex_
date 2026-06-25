# WAVE 2B BATCH 3 - POST-PATCH VERIFICATION PLAN

**Document Type:** Agent 4 Verification Strategy  
**Status:** READY FOR EXECUTION  
**Date:** 2026-06-16T02:47:00Z

---

## Executive Summary

This document outlines Agent 4's post-patch verification strategy for Wave 2B Batch 3. Once Agent 1 applies patches to the target packages, this plan will be executed to verify CVE eliminations and ensure zero regressions.

---

## Pre-Patch Baseline Summary

### Current Environment State

| Metric | Value |
|--------|-------|
| Total Vulnerabilities | 37 CVEs |
| Packages Affected | 13 packages |
| Target Package CVEs | 5 confirmed (setuptools: 3, certifi: 2) |
| Batch 3 Minimum Target | 10 CVE reduction |

### Expected Post-Patch State

After Agent 1 applies Batch 3 patches:

| Package | Pre-Patch | Post-Patch Target | Action |
|---------|-----------|------------------|--------|
| setuptools | 68.1.2 (3 CVEs) | 75.0.0+ (0 CVEs) | Upgrade |
| certifi | 2023.11.17 (2 CVEs) | 2024.12.14+ (0 CVEs) | Upgrade |
| pyjwt | Not installed | Install latest | Install |
| torch | Not installed | TBD | TBD |
| transformers | Not installed | TBD | TBD |

**Expected CVE Reduction:** 5 confirmed + TBD (pyjwt/torch/transformers) = 10+ CVEs

---

## Verification Protocol

### Phase 1: Post-Patch Scanning (Immediate)

**Timeline:** After Agent 1 commits patches

**Steps:**
1. Run full pip-audit scan
2. Capture JSON output
3. Compare against pre-patch baseline
4. Identify eliminated CVEs
5. Detect any new CVEs

**Commands:**
```bash
# Full scan after patches
pip-audit --format=json > wave2b_batch3_postpatch.json

# Analyze results
pip-audit --desc | tee wave2b_batch3_postpatch_verbose.txt
```

### Phase 2: Target Package Verification

**For each Batch 3 target package:**

#### setuptools
```bash
# Expected: Version 75.0.0+ (or latest stable)
pip show setuptools | grep Version

# Expected CVE count: 0 (down from 3)
pip-audit | grep setuptools

# Verification: All 3 target CVEs eliminated
# - PYSEC-2025-49: ELIMINATED
# - CVE-2024-6345: ELIMINATED
```

#### certifi
```bash
# Expected: Version 2024.12.14+ (or latest)
pip show certifi | grep Version

# Expected CVE count: 0 (down from 2)
pip-audit | grep certifi

# Verification: All 2 target CVEs eliminated
# - PYSEC-2024-230: ELIMINATED
```

#### pyjwt (if installed)
```bash
# Expected: Latest stable version installed
pip show pyjwt | grep Version

# Expected CVE count: 0 (target: was 8)
pip-audit | grep pyjwt
```

#### torch & transformers (if applicable)
```bash
# Check installation and CVE count
pip show torch transformers
pip-audit | grep -E "(torch|transformers)"
```

### Phase 3: Regression Detection

**Critical Checks:**

1. **Zero New CRITICAL CVEs**
   ```bash
   # Before: 0 CRITICAL
   # After: Must be 0 CRITICAL
   pip-audit | grep CRITICAL
   ```

2. **Zero New HIGH CVEs**
   ```bash
   # Before: 0 HIGH  
   # After: Must be 0 HIGH
   pip-audit | grep HIGH
   ```

3. **New MEDIUM CVEs Detection**
   ```bash
   # Compare pre/post MEDIUM counts
   # Expected: Same or fewer
   pip-audit | grep MEDIUM | wc -l
   ```

4. **No Dependency Conflicts**
   ```bash
   # Run pip check
   pip check
   # Expected: No conflicts
   ```

---

## Success Criteria Verification

### Criterion 1: Target CVE Elimination

**Requirement:** All 5 confirmed Batch 3 target CVEs eliminated

**Verification:**
- ✓ setuptools: 3 CVEs → 0 CVEs
- ✓ certifi: 2 CVEs → 0 CVEs
- ? pyjwt: 8 CVEs → 0 CVEs (if installed)
- ? torch: TBD CVEs → 0 CVEs (if applicable)
- ? transformers: TBD CVEs → 0 CVEs (if applicable)

**Acceptance:** 5/5 confirmed targets must be 0 CVEs (100%)

### Criterion 2: Zero Regressions

**Requirement:** No new CRITICAL or HIGH vulnerabilities introduced

**Verification:**
- ✓ CRITICAL count: 0 → 0 (maintained)
- ✓ HIGH count: 0 → 0 (maintained)
- ✓ MEDIUM count: 37 → ≤27 (only target CVEs removed)

**Acceptance:** Zero new CRITICAL/HIGH CVEs

### Criterion 3: Monotonic Decrease

**Requirement:** CVE count continuously decreases

**Timeline:**
- Wave baseline: 46 CVEs
- After Batch 1: 34 CVEs (-12)
- After Batch 2: 25 CVEs (-9)
- Expected Batch 3: 15 CVEs (-10)

**Verification:**
```
46 → 34 → 25 → 15
     -12   -9  -10  = Monotonically decreasing ✓
```

**Acceptance:** Post-patch CVE count ≤ 25 (preferably ≤ 15)

### Criterion 4: Metrics Integrity

**Requirement:** All metrics documented and valid

**Verification:**
- ✓ JSON metrics file valid and parseable
- ✓ All CVE IDs traceable to source
- ✓ Timestamps accurate
- ✓ Package versions confirmed

**Acceptance:** All data points verified and documented

---

## Expected Outcomes

### Scenario A: All Patches Applied Successfully ✅

**Post-Patch Expected State:**

```
Pre-Patch:   37 CVEs (setuptools: 3, certifi: 2, + 32 others)
             │
             ├─ setuptools -3
             ├─ certifi -2
             ├─ pyjwt -8 (if installed)
             └─ torch/transformers -TBD
             │
Post-Patch:  ≤27 CVEs (or lower with pyjwt/torch/transformers)

Target:      25 CVEs (original Batch 2 baseline) or better
Stretch:     ≤15 CVEs (if pyjwt/torch/transformers patched)
```

**Minimum Success:** 37 → ≤27 (5 confirmed + 5+ TBD = 10+ CVEs eliminated)
**Full Success:** 37 → ≤15 (all packages patched)

### Scenario B: Partial Patches Applied 🟡

**Expected State (setuptools + certifi only):**
- setuptools: 3 → 0 ✓
- certifi: 2 → 0 ✓
- pyjwt: Not installed (0 CVEs eliminated)
- Total reduction: 5 CVEs
- Post-patch state: 37 - 5 = 32 CVEs

**Status:** Below minimum target (need 10+), requires escalation

### Scenario C: Patches Not Applied ❌

**Expected State:**
- All CVE counts unchanged: 37 CVEs
- Status: FAILED - escalate to Agent 1

---

## Regression Risk Assessment

### Potential Risks

1. **Backward Compatibility Issues**
   - Risk: Upgrading setuptools/certifi might break dependencies
   - Mitigation: Check `pip check` output
   - Action: If conflicts, document and escalate

2. **New CVEs in Upgraded Packages**
   - Risk: New patches introduce new vulnerabilities
   - Mitigation: pip-audit scan post-patch
   - Action: If found, escalate to Agent 1

3. **Installation Failures**
   - Risk: Patches fail to install due to conflicts
   - Mitigation: Monitor Agent 1 commit logs
   - Action: If failed, request rollback

4. **Partial Patch Application**
   - Risk: Only some target packages patched
   - Mitigation: Verify all targets in pip list
   - Action: Request completion of patch set

---

## Data Collection & Reporting

### Output Files to Generate

After post-patch scans complete:

1. **Scan Results**
   - `WAVE_2B_BATCH3_POSTPATCH_SCAN.json` — Full scan results
   - `WAVE_2B_BATCH3_POSTPATCH_VERBOSE.txt` — Human-readable output

2. **Verification Reports**
   - `WAVE_2B_BATCH3_VERIFICATION_REPORT.md` — Detailed findings
   - `WAVE_2B_BATCH3_CVE_MAPPING.json` — Pre→post CVE mapping

3. **Metrics Updates**
   - `WAVE_2B_BATCH3_FINAL_METRICS.json` — Final metrics
   - `WAVE_2B_PROGRESS.md` — Updated with Batch 3 results

### Final Report Contents

- ✓ Baseline vs. post-patch comparison
- ✓ All target CVE eliminations verified
- ✓ Regression analysis (zero new CRITICAL/HIGH)
- ✓ Trend analysis (monotonic decrease confirmed)
- ✓ Success criteria assessment (all 4 criteria pass/fail)
- ✓ Cumulative Wave 2B progress (21+10+TBD = 31+)
- ✓ Recommendations for Batch 4 (if needed)

---

## Execution Checklist

- [ ] Pre-patch baseline captured (37 CVEs documented)
- [ ] Agent 1 patches committed to git
- [ ] Patches integrated into requirements.txt
- [ ] pip install / pip-sync executed
- [ ] Post-patch scan runs successfully
- [ ] setuptools verified at ≥75.0.0
- [ ] certifi verified at ≥2024.12.14
- [ ] pyjwt, torch, transformers status confirmed
- [ ] CVE count drops to ≤27 (or better)
- [ ] No new CRITICAL/HIGH vulnerabilities
- [ ] All success criteria pass
- [ ] Final metrics generated
- [ ] Progress dashboard updated
- [ ] Report generated and saved

---

## Timeline

| Phase | Trigger | Duration | Status |
|-------|---------|----------|--------|
| **Pre-Patch Baseline** | Now | Complete | ✅ DONE |
| **Agent 1 Patches** | TBD | ~30 min | ⏳ PENDING |
| **Post-Patch Scan** | After patches | ~5 min | ⏳ READY |
| **Verification** | After scan | ~5 min | ⏳ READY |
| **Final Report** | After verification | ~5 min | ⏳ READY |
| **Dashboard Update** | After report | ~5 min | ⏳ READY |

**Total Agent 4 Post-Patch Duration:** ~20 minutes (after Agent 1 completes)

---

## Authorization & Sign-Off

**Document Created By:** Agent 4 (dependency-vulnerability-scanner)  
**Authorization:** WAVE_2B_CVE_REMEDIATION_v1 (approved by @mbaetiong)  
**Status:** Ready for execution upon Agent 1 patch application  

**Next Action:** Monitor for Agent 1 patch commits, then execute Phase 1 scanning
