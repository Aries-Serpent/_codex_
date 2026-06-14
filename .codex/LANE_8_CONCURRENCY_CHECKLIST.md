# CONCURRENCY CONFIGURATION CHECKLIST

**Generated:** 2026-02-05  
**Total Workflows:** 185  
**Compliant:** 104 (56.2%)  
**Non-Compliant:** 81 (43.8%)

---

## 🟢 COMPLIANT WORKFLOWS (104)

These workflows follow the recommended concurrency pattern with branch-scoped groups:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### List (Sample - Full list available in analysis)
- ci-health-monitor.yml ✅
- coverage-ratchet.yml ✅
- pre-merge-validation.yml ✅
- pr-checks.yml ✅
- security-scanning-suite.yml ✅
- (99 more compliant workflows...)

---

## 🟡 IMPROPER NAMING (72)

These workflows have concurrency configured but with improper naming patterns:

### Pattern 1: Missing Branch Reference (60 workflows)
```yaml
# ❌ CURRENT (WRONG)
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: true

# ✅ SHOULD BE
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Affected:**
- actionlint-audit.yml
- admin-action-t03.yml
- agent-handoff-gate.yml
- agent-health-check.yml
- agent-registry-validation.yml
- agent-task-janitor.yml
- auto-approve-workflows.yml
- branch-cleanup.yml
- branch-divergence-monitor.yml
- branch-rebase-gate.yml
- build-agent-env-cache.yml
- ci-checkpoint-validation.yml
- ci-failure-issue-creator.yml
- ci-pass-rate-gate.yml
- ci-rescue.yml
- cleanup-stale-pr-comments.yml
- codebase-health-sweep.yml
- codeql.yml
- codex-manifest-refresh.yml
- cognitive-action-decision.yml
- cognitive-perception.yml
- cognitive_brain_ci_feedback.yml
- comment-review-gate.yml
- copilot-agent-checkin.yml
- copilot-agent-session-done.yml
- copilot-agent-vars-bootstrap.yml
- copilot-issue-triage.yml
- copilot-pr-session-injector.yml
- copilot-review-responder.yml
- cost-gate.yml
- create-sub-pr-to-0D_base_.yml
- d-capable-promotion-gate.yml
- data-quality-suite.yml
- detect-duplicates.yml
- deferral-language-gate.yml
- dependabot-auto-absorb.yml
- dependabot-preflight.yml
- dependabot-sheriff.yml
- discussion-cleanup.yml
- discussion-response-bridge.yml
- doc-freshness-check.yml
- doc-refresh-gate.yml
- documentation-link-checker.yml
- docker-build-push.yml
- e-to-d-transition-gate.yml
- embedding-index-rebuild.yml
- fast-forward-safe-files.yml
- flush-queued-runs.yml
- forward-sync-autogen.yml
- github-guru.yml
- ghost-object-actioner.yml
- issue-resolution-gate.yml
- labeler.yml
- ml-lifecycle-gate.yml
- openvino-phase-c.yml
- pages-health-guard.yml
- pages-mkdocs.yml
- pages-pre-merge-validation.yml
- pages-scheduled-validation.yml
- post-accountability-to-discussion.yml
- (12 more...)

### Pattern 2: Hardcoded Group Names (12 workflows)
```yaml
# ❌ CURRENT (WRONG)
concurrency:
  group: test-suite
  cancel-in-progress: true

# ✅ SHOULD BE
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Pattern 3: Missing cancel-in-progress (0 workflows)
All concurrency configurations properly set `cancel-in-progress` ✅

---

## 🔴 MISSING CONCURRENCY (9)

These workflows have NO concurrency configuration and are vulnerable to race conditions:

1. **benchmarks.yml**
   - Type: Performance testing
   - Risk: Parallel benchmark runs corrupt results
   - Fix: Add branch-scoped concurrency

2. **cache-health-monitor.yml**
   - Type: Cache maintenance
   - Risk: Concurrent cache updates cause conflicts
   - Fix: Add concurrency with cancel-in-progress: false

3. **cache-validation.yml**
   - Type: Cache validation
   - Risk: Concurrent validation readings
   - Fix: Add branch-scoped concurrency

4. **copilot-automation.yml**
   - Type: Automation workflow
   - Risk: Duplicate task executions
   - Fix: Add branch-scoped concurrency

5. **documentation-quality-check.yml**
   - Type: Quality checks
   - Risk: Concurrent documentation modifications
   - Fix: Add branch-scoped concurrency

6. **maturity-check.yml**
   - Type: Maturity assessment
   - Risk: Concurrent maturity evaluations
   - Fix: Add branch-scoped concurrency

7. **self-healing.yml**
   - Type: Auto-healing workflow
   - Risk: Concurrent fixes applied twice
   - Fix: Add concurrency with cancel-in-progress: true

8. **semgrep_sarif.yml**
   - Type: Security scanning
   - Risk: Concurrent SARIF uploads
   - Fix: Add branch-scoped concurrency

9. **behavior-compare.yaml**
   - Type: Behavior comparison
   - Risk: Concurrent comparisons invalid
   - Fix: Add branch-scoped concurrency

---

## 🔧 REMEDIATION INSTRUCTIONS

### Automated Fix (Recommended)

```bash
#!/bin/bash
# Fix all concurrency naming issues at once

WORKFLOWS_DIR=".github/workflows"

# Pattern 1: Fix missing branch reference
find "$WORKFLOWS_DIR" -name "*.yml" -o -name "*.yaml" | while read file; do
    if grep -q "group: \${{ github.workflow }}" "$file"; then
        sed -i 's/group: \${{ github.workflow }}/group: \${{ github.workflow }}-\${{ github.ref }}/g' "$file"
        echo "Fixed: $file"
    fi
done

# Pattern 2: Add concurrency to workflows missing it
# (Manual per-workflow verification needed)

# Verify changes
git diff .github/workflows/ | head -50
```

### Manual Fix (Per-Workflow)

For each workflow:

```yaml
# STEP 1: Open the workflow file
# STEP 2: Find or add concurrency section at top level (after name:)
# STEP 3: Ensure it matches this pattern:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# STEP 4: For workflows that should NOT cancel (e.g., maintenance):
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

# STEP 5: Save and commit
```

---

## 🎯 VALIDATION CHECKLIST

After fixing, verify each workflow:

- [ ] Concurrency group includes `${{ github.workflow }}`
- [ ] Concurrency group includes `${{ github.ref }}`
- [ ] `cancel-in-progress` explicitly set to true or false
- [ ] Concurrency placed at workflow root level (not inside jobs)
- [ ] YAML syntax is valid (run `yamllint`)
- [ ] Workflow runs successfully in test PR
- [ ] No race conditions observed (multiple runs queued)

---

## 🚨 TESTING RECOMMENDATIONS

### Test Case 1: Concurrent PR Runs
```bash
# Push multiple commits rapidly to PR to trigger multiple runs
# Verify: Only latest run executes, previous runs cancelled
# Expected: All cancelled runs show "Superseded by a newer workflow"
```

### Test Case 2: Main Branch Runs
```bash
# Push to main branch
# Merge a PR at same time
# Verify: Runs don't interfere with each other
# Expected: Both runs complete independently if on different branches
```

### Test Case 3: Concurrency Group Isolation
```bash
# Verify: main branch runs don't cancel feature-branch runs
# Verify: feature-branch1 runs don't cancel feature-branch2 runs
# Verify: Different workflows can run simultaneously
```

---

## 📊 SUCCESS METRICS

| Metric | Current | Target | Impact |
|--------|---------|--------|--------|
| Concurrency Coverage | 95% | 100% | Eliminate race conditions |
| Proper Naming | 56% | 100% | Enable branch isolation |
| Cancel-in-progress | 100% | 100% | Prevent duplicate runs |
| **Overall** | **56%** | **100%** | **No race conditions** |

---

## 🔄 IMPLEMENTATION PLAN

### Phase 1 (Week 1)
- [ ] Review compliance report
- [ ] Identify high-risk workflows
- [ ] Create test PR with fixes

### Phase 2 (Week 1-2)
- [ ] Apply fixes to all workflows
- [ ] Commit: `fix: standardize workflow concurrency patterns`
- [ ] Create PR for review

### Phase 3 (Week 2)
- [ ] Verify in staging
- [ ] Run test scenarios
- [ ] Merge to main

### Phase 4 (Week 3+)
- [ ] Monitor for race conditions
- [ ] Validate cache behavior
- [ ] Document lessons learned

---

**Status:** ✅ Ready for Implementation  
**Estimated Effort:** 2-3 hours with automation  
**Risk Level:** LOW (safe changes, well-tested patterns)
