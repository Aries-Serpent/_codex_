# PR #5194 CI Remediation Campaign Matrix

**Campaign Start:** 2026-07-02T18:51:15Z  
**Baseline SHA:** a97d62a5 (latest CI-bearing commit; a2c355e7 excluded due to `[skip ci]`)  
**Total Workflows:** 48 failed + 3 non-workflow checks = 51 total  
**Deduped Checklist:** 48 unique workflows (see below)  
**Priority Order:** 10 highest-priority unresolved → full remediation  

---

## 📊 Remediation Matrix (One-Line-Per-Workflow)

### PRIORITY TIER 1: CRITICAL BLOCKERS (Must-Fix Now)

| # | Workflow | Status | Lane | Root Cause | Action | Latest Run | Resolved SHA |
|---|----------|--------|------|-----------|--------|------------|--------------|
| 1 | validate.yml | ⏳ PENDING | validation | TBD | Diagnose & fix | - | - |
| 2 | workflow-compliance-gate.yml | ⏳ PENDING | policy | TBD | Diagnose & fix | - | - |
| 3 | pre-flight-validation.yml | ⏳ PENDING | validation | TBD | Diagnose & fix | - | - |
| 4 | unified-governance-check.yml | ⏳ PENDING | governance | TBD | Diagnose & fix | - | - |
| 5 | machine-readable-governance.yml | ⏳ PENDING | governance | TBD | Diagnose & fix | - | - |
| 6 | phase-9-3-router.yml | ⏳ PENDING | router | Missing `.codex/PHASE_9_3_CAPABILITY_INDEX.json` | Restore file & harden parsing | - | - |
| 7 | autonomy-phase-ci-matrix.yml | ⏳ PENDING | autonomy | No tests discovered / shard exit code 5 | Fix test discovery & exit handling | - | - |
| 8 | pre-merge-validation.yml | ⏳ PENDING | validation | TBD | Diagnose & fix | - | - |
| 9 | resilient_validation.yml | ⏳ PENDING | validation | TBD | Diagnose & fix | - | - |
| 10 | codeql-analysis.yml | ⏳ PENDING | security | CodeQL findings | Run & resolve alerts | - | - |

### PRIORITY TIER 2: HIGH-PRIORITY WORKFLOWS

| # | Workflow | Status | Lane | Root Cause | Action | Latest Run | Resolved SHA |
|---|----------|--------|------|-----------|--------|------------|--------------|
| 11 | security-scanning-suite.yml | ⏳ PENDING | security | TBD | Run & review | - | - |
| 12 | semgrep_sarif.yml | ⏳ PENDING | security | TBD | Run & review | - | - |
| 13 | copilot-setup-steps.yml | ⏳ PENDING | setup | Lines 141-147 shell brace syntax | Wrap in block scalar `\|` | - | - |
| 14 | ci-docker-build-healer.yml | ⏳ PENDING | docker | Multi-stage editable install | Diagnose & fix | - | - |
| 15 | build-preview-image | ⏳ PENDING | docker | startup-failure path | Diagnose container image issue | - | - |

### PRIORITY TIER 3: MEDIUM-PRIORITY WORKFLOWS (Likely Auto-Resolved)

| # | Workflow | Status | Lane | Root Cause | Action | Latest Run | Resolved SHA |
|---|----------|--------|------|-----------|--------|------------|--------------|
| 16 | comment-review-gate.yml | ✅ RESOLVED | review | Later success found | Confirm & mark green | - | - |
| 17 | secrets-baseline-enforcer.yml | ✅ RESOLVED | security | Later success found | Confirm & mark green | - | - |
| 18 | copilot-setup-validation.yml | ✅ RESOLVED | setup | Later success found | Confirm & mark green | - | - |
| 19 | actionlint-audit.yml | ✅ RESOLVED | audit | Later success found | Confirm & mark green | - | - |

### REMAINING 28 WORKFLOWS (All Lanes - Defer to Batch 2)

| # | Workflow | Status | Lane | Root Cause | Action | Latest Run | Resolved SHA |
|---|----------|--------|------|-----------|--------|------------|--------------|
| 20 | agent-auth-delegation.yml | ⏳ PENDING | auth | TBD | Batch 2 | - | - |
| 21 | audit-qa-suite.yml | ⏳ PENDING | qa | TBD | Batch 2 | - | - |
| 22 | auth-tests.yml | ⏳ PENDING | testing | TBD | Batch 2 | - | - |
| 23 | auto-approve-workflows.yml | ⏳ PENDING | approval | TBD | Batch 2 | - | - |
| 24 | auto-fix-common-issues.yml | ⏳ PENDING | fix | TBD | Batch 2 | - | - |
| 25 | auto-fix-pr-check.yml | ⏳ PENDING | fix | TBD | Batch 2 | - | - |
| 26 | branch-rebase-gate.yml | ⏳ PENDING | git | TBD | Batch 2 | - | - |
| 27 | ci-checkpoint-validation.yml | ⏳ PENDING | checkpoint | TBD | Batch 2 | - | - |
| 28 | ci-health-monitor.yml | ⏳ PENDING | health | TBD | Batch 2 | - | - |
| 29 | code-quality-coverage-suite.yml | ⏳ PENDING | quality | TBD | Batch 2 | - | - |
| 30 | consistency-checks.yml | ⏳ PENDING | check | TBD | Batch 2 | - | - |
| 31 | copilot-agent-vars-bootstrap.yml | ⏳ PENDING | bootstrap | TBD | Batch 2 | - | - |
| 32 | coverage-ratchet.yml | ⏳ PENDING | coverage | TBD | Batch 2 | - | - |
| 33 | coverage-with-timeout.yml | ⏳ PENDING | coverage | TBD | Batch 2 | - | - |
| 34 | dependency-submission.yml | ⏳ PENDING | dependency | TBD | Batch 2 | - | - |
| 35 | detect-duplicates.yml | ⏳ PENDING | detect | TBD | Batch 2 | - | - |
| 36 | documentation-link-checker.yml | ⏳ PENDING | docs | TBD | Batch 2 | - | - |
| 37 | e-to-d-transition-gate.yml | ⏳ PENDING | gate | TBD | Batch 2 | - | - |
| 38 | github-guru.yml | ⏳ PENDING | guru | TBD | Batch 2 | - | - |
| 39 | issue-resolution-gate.yml | ⏳ PENDING | gate | TBD | Batch 2 | - | - |
| 40 | mypy-baseline.yml | ⏳ PENDING | typing | TBD | Batch 2 | - | - |
| 41 | phase-12-2-compliance-check.yml | ⏳ PENDING | phase | TBD | Batch 2 | - | - |
| 42 | pr-cost-check.yml | ⏳ PENDING | cost | TBD | Batch 2 | - | - |
| 43 | promotion-readiness-gate.yml | ⏳ PENDING | gate | TBD | Batch 2 | - | - |
| 44 | qa-walkthrough.yml | ⏳ PENDING | qa | TBD | Batch 2 | - | - |
| 45 | reference-integrity.yml | ⏳ PENDING | ref | TBD | Batch 2 | - | - |
| 46 | required-actions-enforcer.yml | ⏳ PENDING | enforce | TBD | Batch 2 | - | - |
| 47 | root-org-validation.yml | ⏳ PENDING | org | TBD | Batch 2 | - | - |
| 48 | scan-secrets-variables.yml | ⏳ PENDING | secret | TBD | Batch 2 | - | - |

### NON-WORKFLOW CHECKS (3 Total)

| # | Check | Status | Root Cause | Action | Latest Run | Resolved SHA |
|---|-------|--------|-----------|--------|------------|--------------|
| 49 | CodeQL | ⏳ PENDING | Security findings | Run analysis & remediate | - | - |
| 50 | Semgrep OSS | ⏳ PENDING | Security findings | Run analysis & remediate | - | - |
| 51 | Governance Compliance | ⏳ PENDING | TBD | Diagnose & fix | - | - |

---

## 🚀 Execution Plan by Lane

### Lane 1: Setup Drift (copilot-setup-steps.yml)
- **Issue:** Lines 141-147 shell braces in `run:` field
- **Fix:** Wrap in block scalar `|` operator
- **Status:** ⏳ READY FOR FIX

### Lane 2: Validation / Policy (5 workflows)
- **Workflows:** validate.yml, pre-flight-validation.yml, workflow-compliance-gate.yml, pre-merge-validation.yml, resilient_validation.yml
- **Action:** Diagnose in parallel, apply fixes by root cause
- **Status:** ⏳ READY FOR DIAGNOSIS

### Lane 3: Governance (3 workflows)
- **Workflows:** unified-governance-check.yml, machine-readable-governance.yml
- **Action:** Fix schema ref resolution for reference.schema.json
- **Status:** ⏳ READY FOR FIX

### Lane 4: Router (phase-9-3-router.yml)
- **Issue:** Missing `.codex/PHASE_9_3_CAPABILITY_INDEX.json`
- **Fix:** Restore file, harden empty-value parsing
- **Status:** ⏳ READY FOR FIX

### Lane 5: Autonomy (autonomy-phase-ci-matrix.yml)
- **Issue:** No tests discovered, shard exit code 5
- **Fix:** Fix test discovery logic, exit code handling
- **Status:** ⏳ READY FOR FIX

### Lane 6: Security (CodeQL, Semgrep, security-scanning-suite.yml, semgrep_sarif.yml)
- **Action:** Run analysis, generate & remediate alerts
- **Status:** ⏳ DEFERRED UNTIL LANES 1-5 GREEN

### Lane 7: Container (ci-docker-build-healer.yml, build-preview-image)
- **Action:** Debug multi-stage builds, editable installs
- **Status:** ⏳ DEFERRED UNTIL LANES 1-5 GREEN

---

## 📋 Deduped One-Line Checklist

```
TIER 1 CRITICAL (10 Workflows):
- [ ] 1. validate.yml → diagnose & fix root cause
- [ ] 2. workflow-compliance-gate.yml → diagnose & fix root cause
- [ ] 3. pre-flight-validation.yml → diagnose & fix root cause
- [ ] 4. unified-governance-check.yml → fix schema refs
- [ ] 5. machine-readable-governance.yml → fix schema refs
- [ ] 6. phase-9-3-router.yml → restore PHASE_9_3_CAPABILITY_INDEX.json
- [ ] 7. autonomy-phase-ci-matrix.yml → fix test discovery
- [ ] 8. pre-merge-validation.yml → diagnose & fix root cause
- [ ] 9. resilient_validation.yml → diagnose & fix root cause
- [ ] 10. codeql-analysis.yml → run & remediate

TIER 2 HIGH (5 Workflows):
- [ ] 11. security-scanning-suite.yml → run & review
- [ ] 12. semgrep_sarif.yml → run & review
- [ ] 13. copilot-setup-steps.yml → wrap shell braces in block scalar
- [ ] 14. ci-docker-build-healer.yml → debug multi-stage builds
- [ ] 15. build-preview-image → debug startup failure

TIER 3 CONFIRMED RESOLVED (4 Workflows):
- [ ] 16. comment-review-gate.yml → confirm green
- [ ] 17. secrets-baseline-enforcer.yml → confirm green
- [ ] 18. copilot-setup-validation.yml → confirm green
- [ ] 19. actionlint-audit.yml → confirm green

BATCH 2 DEFERRABLE (28 Workflows):
- [ ] 20-47. All remaining workflows in Batch 2 (defer for now)

NON-WORKFLOW CHECKS (3):
- [ ] 48. CodeQL → run & remediate
- [ ] 49. Semgrep OSS → run & remediate
- [ ] 50. Governance Compliance → diagnose & fix
```

---

## 🔧 Execution Commands (Ready to Run)

### Phase 1: Setup & Foundation
```bash
# Diagnose all Tier 1 workflows
python scripts/ci/auto_fix_common_issues.py --check-only --json-output .codex/pr5194-diagnostic.json

# Get latest run details for each Tier 1 workflow
gh run list --repo Aries-Serpent/_codex_ --branch copilot/explore-codebase-implement-tasks --limit 50 --json name,status,conclusion
```

### Phase 2: Targeted Fixes (by Lane)
```bash
# Lane 1: copilot-setup-steps.yml (lines 141-147)
# Manual edit required - wrap in block scalar

# Lane 3: Governance (schema refs)
# Restore/verify reference.schema.json references

# Lane 4: Router
# Restore .codex/PHASE_9_3_CAPABILITY_INDEX.json

# Lane 5: Autonomy
# Fix test discovery in autonomy-phase-ci-matrix.yml
```

### Phase 3: Verification
```bash
# Re-run Tier 1 workflows in priority order
gh workflow run validate.yml -r copilot/explore-codebase-implement-tasks
gh workflow run workflow-compliance-gate.yml -r copilot/explore-codebase-implement-tasks
# ... etc for all 10 Tier 1
```

---

## 📈 Success Criteria

✅ **Campaign Complete When:**
1. All 10 Tier 1 workflows show green check ✓
2. All 5 Tier 2 workflows show green check ✓
3. 4 Tier 3 workflows confirmed green ✓
4. CodeQL/Semgrep/Governance scans clear ✓
5. All per-workflow run URLs with success status collected ✓
6. Final proof bundle generated with SHA progression ✓

---

**Campaign Owner:** @mbaetiong (Auto-approval: wec:auto-approve enabled)  
**Created:** 2026-07-02T18:51:15Z  
**Next Step:** Diagnose Tier 1 workflows & execute fixes by lane
