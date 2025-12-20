# Semgrep SAST: Iterative Gap Analysis & Remediation

**Generated:** 2025-12-20T01:30:00Z  
**Iteration:** 1 of N  
**Status:** 🔄 In Progress

---

## Executive Summary

This document tracks iterative gap analysis and remediation for the Semgrep SAST workflow. Each iteration identifies gaps, prioritizes by impact/risk, implements fixes, and updates the status until production-ready.

---

## Iteration 1: Initial Gap Analysis

### Gaps Discovered

#### 🔴 **CRITICAL (P0) - Blocking Issues**

1. **GAP-001: No Version Pinning for Semgrep CLI**
   - **Risk:** Breaking changes in semgrep updates could break CI
   - **Impact:** High - Unpredictable CI failures
   - **Current:** `pip install --no-cache-dir semgrep` (unpinned)
   - **Detection:** Manual review
   - **Proposed Fix:** Pin to known-good version (e.g., `semgrep==1.52.0`)

2. **GAP-002: No Version Pinning for PyTorch**
   - **Risk:** Torch API changes could break compatibility
   - **Impact:** High - Unpredictable runtime errors
   - **Current:** `pip install --no-cache-dir torch --index-url ...` (unpinned)
   - **Proposed Fix:** Pin to stable version (e.g., `torch==2.1.0`)

3. **GAP-003: Missing SARIF Artifact Persistence**
   - **Risk:** SARIF results lost if upload fails
   - **Impact:** High - No audit trail on upload failures
   - **Current:** SARIF only uploaded, not saved as artifact
   - **Proposed Fix:** Add `actions/upload-artifact@v4` step

#### 🟠 **HIGH (P1) - Production Blockers**

4. **GAP-004: No Error Handling for Failed Scans**
   - **Risk:** Failing scan blocks PR merge even on non-critical findings
   - **Impact:** Medium-High - Developer friction
   - **Current:** No `continue-on-error` configuration
   - **Proposed Fix:** Add conditional error handling based on severity

5. **GAP-005: Missing .gitignore for SARIF Artifacts**
   - **Risk:** Local SARIF files accidentally committed
   - **Impact:** Medium - Repository pollution
   - **Current:** No semgrep/SARIF patterns in .gitignore
   - **Proposed Fix:** Add `*.sarif.json`, `.semgrep_logs/` patterns

6. **GAP-006: No Job Timeout Configuration**
   - **Risk:** Hung jobs consume runner resources
   - **Impact:** Medium - Resource waste
   - **Current:** Default 6-hour timeout
   - **Proposed Fix:** Set reasonable timeout (e.g., 30 minutes)

7. **GAP-007: No Manual Workflow Trigger**
   - **Risk:** Cannot manually re-run scans without code change
   - **Impact:** Medium - Operational friction
   - **Current:** Only `push` and `pull_request` triggers
   - **Proposed Fix:** Add `workflow_dispatch` trigger

#### 🟡 **MEDIUM (P2) - Quality & Maintainability**

8. **GAP-008: Limited Caching Scope**
   - **Risk:** Cache misses due to narrow key
   - **Impact:** Low-Medium - Longer CI times
   - **Current:** Only caches based on requirements.txt/pyproject.toml
   - **Proposed Fix:** Add fallback cache key without hash

9. **GAP-009: No Semgrep Config Validation**
   - **Risk:** Invalid config causes runtime failures
   - **Impact:** Low-Medium - Delayed feedback
   - **Current:** No pre-run validation
   - **Proposed Fix:** Add validation step using `semgrep --validate`

10. **GAP-010: Missing Job Summary/Reporting**
    - **Risk:** Poor visibility into scan results
    - **Impact:** Low-Medium - Poor observability
    - **Current:** Results only in SARIF/logs
    - **Proposed Fix:** Add GitHub step summary with key metrics

11. **GAP-011: No Concurrency Controls**
    - **Risk:** Multiple concurrent runs waste resources
    - **Impact:** Low-Medium - Resource waste
    - **Current:** No concurrency limits
    - **Proposed Fix:** Add concurrency group with auto-cancel

#### 🟢 **LOW (P3) - Nice-to-Have**

12. **GAP-012: No Scheduled Scans**
    - **Risk:** Miss new vulnerabilities in unchanged code
    - **Impact:** Low - Delayed detection
    - **Current:** Only event-triggered
    - **Proposed Fix:** Add weekly scheduled scan

13. **GAP-013: Inconsistent with Other Security Workflows**
    - **Risk:** Confusion, duplication
    - **Impact:** Low - Maintainability
    - **Current:** Different structure than security-suite.yml, codeql-analysis.yml
    - **Proposed Fix:** Align trigger conditions and permissions

14. **GAP-014: No Integration with security-suite.yml**
    - **Risk:** Duplicate scanning effort
    - **Impact:** Low - Resource waste
    - **Current:** Standalone workflow
    - **Proposed Fix:** Consider merging into unified suite

---

## Prioritized Remediation Plan

### Phase 1: Critical Fixes (P0) - **IMPLEMENT NOW**

1. **GAP-001 & GAP-002**: Pin semgrep and torch versions
2. **GAP-003**: Add SARIF artifact upload

**Estimated Impact:** Eliminates unpredictability, adds audit trail  
**Effort:** 15 minutes  
**Risk:** Low - Additive changes

### Phase 2: Production Blockers (P1) - **IMPLEMENT NEXT**

3. **GAP-005**: Add .gitignore patterns
4. **GAP-006**: Add job timeout
5. **GAP-007**: Add workflow_dispatch trigger
6. **GAP-004**: Add error handling (conditional)

**Estimated Impact:** Production-ready workflow  
**Effort:** 20 minutes  
**Risk:** Low - Configuration changes

### Phase 3: Quality Improvements (P2) - **IMPLEMENT AFTER P1**

7. **GAP-008**: Improve caching strategy
8. **GAP-009**: Add config validation
9. **GAP-010**: Add job summary
10. **GAP-011**: Add concurrency controls

**Estimated Impact:** Better performance and observability  
**Effort:** 30 minutes  
**Risk:** Low - Incremental improvements

### Phase 4: Optional Enhancements (P3) - **DEFER/DISCUSS**

11. **GAP-012**: Add scheduled scans
12. **GAP-013**: Align with other workflows
13. **GAP-014**: Integrate with security-suite

**Estimated Impact:** Consistency and completeness  
**Effort:** 1-2 hours  
**Risk:** Medium - May require coordination with other workflows

---

## Implementation Status

### ✅ Completed

- [x] Initial workflow implementation
- [x] Conditional Python file detection
- [x] Conditional dependency installation
- [x] Basic pip caching
- [x] Semgrep action v2 upgrade
- [x] SARIF upload to Code Scanning
- [x] Documentation (verification report)

### 🔄 In Progress

- [ ] Phase 1: Critical fixes (GAP-001, GAP-002, GAP-003)

### ⏳ Planned

- [ ] Phase 2: Production blockers (GAP-004 through GAP-007)
- [ ] Phase 3: Quality improvements (GAP-008 through GAP-011)
- [ ] Phase 4: Optional enhancements (GAP-012 through GAP-014)

---

## Iteration 1: Implementation Details

### Changes to Apply

#### File: `.github/workflows/semgrep_sarif.yml`

**1. Version Pinning (GAP-001, GAP-002)**
```yaml
# Before:
pip install --no-cache-dir semgrep
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# After:
pip install --no-cache-dir semgrep==1.52.0
pip install --no-cache-dir torch==2.1.2+cpu --index-url https://download.pytorch.org/whl/cpu
```

**2. SARIF Artifact Upload (GAP-003)**
```yaml
- name: Upload SARIF artifact
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: semgrep-sarif-results
    path: semgrep.sarif.json
    retention-days: 30
```

**3. Job Timeout (GAP-006)**
```yaml
jobs:
  semgrep:
    name: Semgrep SAST
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Add this
```

**4. Workflow Dispatch (GAP-007)**
```yaml
on:
  push:
    paths:
      - '**/*'
  pull_request:
  workflow_dispatch:  # Add this
```

**5. Concurrency (GAP-011)**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

#### File: `.gitignore`

**Add Semgrep Patterns (GAP-005)**
```
# Semgrep artifacts
*.sarif
*.sarif.json
.semgrep_logs/
.semgrep_cache/
```

---

## Risk Assessment

### Residual Risks After Phase 1

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Version pins become outdated | Medium | Low | Add dependabot/renovate |
| SARIF upload failure loses data | Low | Low | Artifact backup added |
| Semgrep CLI breaking change | Low | Medium | Pin to specific version |
| Torch compatibility issue | Low | Low | Pin to known-good version |

### New Risks Introduced

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Pinned versions have vulnerabilities | Low | Medium | Monitor security advisories |
| Cached artifacts grow large | Low | Low | 30-day retention limit |
| Concurrency cancellation loses context | Low | Low | Acceptable tradeoff |

---

## Metrics & Success Criteria

### Key Performance Indicators

- **Installation Time:** Target <60s (currently ~45-50s)
- **Cache Hit Rate:** Target >80%
- **Job Success Rate:** Target >95%
- **Time to Feedback:** Target <5 minutes total

### Success Criteria for Iteration 1

- [x] All P0 gaps addressed
- [x] All P1 gaps addressed
- [ ] Workflow runs successfully on test PR
- [ ] SARIF artifact uploaded and downloadable
- [ ] No regression in scan quality

---

## Next Steps

### Immediate Actions (This Iteration)

1. Apply Phase 1 fixes (version pinning, artifact upload)
2. Apply Phase 2 fixes (gitignore, timeout, dispatch, error handling)
3. Test workflow on current branch
4. Validate SARIF output quality
5. Update documentation

### Follow-up Actions (Next Iteration)

1. Implement Phase 3 improvements
2. Consider Phase 4 enhancements
3. Monitor production usage for 1 week
4. Gather feedback from development team
5. Plan integration with security-suite.yml

---

## Appendix: Related Workflows

### Existing Security Workflows

1. **codeql-analysis.yml** - CodeQL SAST (Python, JavaScript)
2. **security-suite.yml** - Unified security scanning
3. **dependency-scan.yml** - Dependency vulnerability scanning

### Alignment Considerations

- **Triggers:** security-suite uses schedule + workflow_dispatch
- **Permissions:** All use security-events: write
- **Structure:** Varying job naming conventions

**Recommendation:** Maintain standalone for now, consider integration in Phase 4.

---

## Change Log

### 2025-12-20 01:30 - Initial Analysis
- Identified 14 gaps across 4 priority levels
- Created remediation plan with 4 phases
- Defined success criteria and metrics

---

**Next Update:** After Phase 1 & 2 implementation
