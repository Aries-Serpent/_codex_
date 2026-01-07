# PR #2207 Deployment Playbook: Step-by-Step Execution Guide
> Generated: 2024-11-14 17:46:51 UTC | Author: mbaetiong | Role: Secondary ⚡ Energy: 5/5

---

## 🎯 Deployment Overview

| Phase | Duration | Status |
|-------|----------|--------|
| **Pre-Deployment** | 10 min | ⏳ Pending |
| **Merge Execution** | 5 min | ⏳ Pending |
| **Post-Merge Validation** | 35 min | ⏳ Pending |
| **Health Check** | 10 min | ⏳ Pending |
| **Total** | ~60 min | ⏳ Pending |

---

## 📋 PHASE 1: PRE-DEPLOYMENT VERIFICATION (10 minutes)

### Step 1.1: Final Status Check

**Location:** GitHub PR #2207 page  
**Time:** ~2 minutes

```bash
# Command to verify PR state
gh pr view 2207 --json mergeable,mergeStateStatus,commits,statusCheckRollup
```text

**Expected Output:**
```text
mergeable: true
mergeStateStatus: CLEAN
commits: 102
statusCheckRollup:
  - context: tests.yml
    state: PASS
  - context: security_gates.yml
    state: PASS
  - context: nox_gates.yml
    state: PASS
```text

**Verification Checklist:**
- ☐ `mergeable` = `true`
- ☐ `mergeStateStatus` = `CLEAN`
- ☐ All status checks = `PASS`
- ☐ No pending reviews
- ☐ 102 commits confirmed

**If Any Check Fails:**
```text
⚠️ STOP DEPLOYMENT
→ Investigate failed check
→ Address issue in 0D_base_ branch
→ Push fix and wait for re-run
→ Return to Step 1.1
```text

---

### Step 1.2: Security Pre-Flight Check

**Location:** Local workstation  
**Time:** ~3 minutes

```bash
# Clone/update repository
cd ~/repos/Aries-Serpent/_codex_
git fetch origin
git checkout 0D_base_

# Quick security scan
bandit -r src/ --severity-level=HIGH

# Verify no hardcoded secrets
detect-secrets scan --baseline .secrets.baseline | grep -i "new"

# Check GPU packages
grep -E "(torch|cuda|tensorflow)" uv.lock | wc -l
# Expected: 0
```text

**Expected Results:**
- Bandit: 0 HIGH/CRITICAL issues
- Secrets: "No new secrets detected"
- GPU Check: "0"

**If Issues Found:**
```text
⚠️ HALT DEPLOYMENT
→ Create new PR for fixes
→ Address all findings
→ Obtain security clearance
→ Schedule new deployment window
```text

---

### Step 1.3: Team Notification & Approval

**Location:** Slack #deployments channel  
**Time:** ~3 minutes

**Message Template:**

```text
🚀 DEPLOYMENT NOTIFICATION: PR #2207

Title: 0D to main
Author: @mbaetiong
Changes: 126 files | +20,518 additions | -3,502 deletions

📋 Deployment Details:
  Scheduled Time: [DATE] [TIME] UTC
  Expected Duration: ~60 minutes
  Automation: ✅ Full (no manual steps needed)
  Rollback Available: ✅ Yes

✅ Pre-Checks Completed:
  ✓ All status checks: PASS
  ✓ Security scan: 0 HIGH/CRITICAL
  ✓ Coverage: 96%+ (verified)
  ✓ Dependencies: GPU removal confirmed
  ✓ Documentation: Complete

🎯 Action Items:
  [ ] @qa-team: Final coverage review
  [ ] @security-team: Acknowledge security clearance
  [ ] @devops-team: Confirm capacity
  [ ] @maintainers: Final approval

Proceed with merge? Reply: ✅ APPROVED or 🛑 ON HOLD
```text

**Required Approvals:**
- ☐ QA Team acknowledgment
- ☐ Security Team clearance
- ☐ DevOps confirmation
- ☐ Maintainer approval

**If Approval Not Obtained:**
```text
⏸️ DEFER DEPLOYMENT
→ Document blockers
→ Schedule follow-up review
→ Keep PR in ready state
```text

---

## 🔀 PHASE 2: MERGE EXECUTION (5 minutes)

### Step 2.1: Pre-Merge Setup

**Location:** GitHub PR #2207 page  
**Time:** ~1 minute

```bash
# Ensure local main branch is up-to-date
git checkout main
git pull origin main

# Verify target state
git log --oneline -5 main
# Confirm HEAD = base commit of PR (65e02ec...)
```text

**Expected Output:**
```text
65e02ec... [base commit visible]
[previous commits...]
```text

---

### Step 2.2: Execute Merge

**Location:** GitHub PR #2207 page  
**Time:** ~2 minutes

**Method 1: GitHub UI (Recommended)**

1. Navigate to: https://github.com/Aries-Serpent/_codex_/pull/2207
2. Scroll to bottom → "Merge pull request" button
3. Select merge strategy: **Create a merge commit** (standard)
4. Confirm message:
   ```
   Merge pull request #2207 from Aries-Serpent/0D_base_
   
   0D to main
   
   CI/CD and Dependency Management Enhancements:
   - Enhanced .github/Copilot.md with CI/CD guidelines
   - Added .github/coverage_threshold.txt (96% minimum)
   - Updated .bandit.yaml with security exclusions
   
   Code Quality Review Response Documentation:
   - Added detailed PR #2224 review comments response
   
   Security and Dependency Tooling:
   - Removed GPU packages (CPU-only environment)
   - Logged dependency operations in audit trail
   ```
5. Click **Confirm merge**

**Method 2: GitHub CLI (Alternative)**

```bash
gh pr merge 2207 --merge --repo Aries-Serpent/_codex_
```text

**Expected Output:**
```text
✓ Pull request #2207 merged
✓ Merge commit: [SHA-12char]
```text

---

### Step 2.3: Post-Merge Confirmation

**Location:** GitHub PR #2207 page  
**Time:** ~2 minutes

```bash
# Verify merge completed
gh pr view 2207 --json merged,mergedAt,mergedBy

# Confirm main branch update
git checkout main
git pull origin main
git log --oneline -1
# Should show merge commit
```text

**Expected Output:**
```text
merged: true
mergedAt: [timestamp]
mergedBy: [your-username]
---
[merge commit SHA] Merge pull request #2207...
```text

**If Merge Failed:**
```text
🚨 MERGE ERROR
→ Check GitHub error message
→ Common issues:
  - Branch protection rules blocking merge
  - Status checks failed between pre-check and merge
  - Conflict emerged (rebase required)
→ Resolve issue and retry merge
```text

---

## ⚙️ PHASE 3: POST-MERGE VALIDATION (35 minutes)

### Step 3.1: Monitor Post-Merge Workflow (0-2 min after merge)

**Location:** GitHub Actions  
**Time:** ~2 minutes

```bash
# Check if post-merge workflow triggered
gh run list --workflow=post-merge-validation-optimized.yml -b main -n 1

# Expected: Most recent run should have started within 1-2 minutes
```text

**Expected Output:**
```text
STATUS  TITLE  BRANCH  EVENT  COMMIT  CREATED
✓ IN_PROGRESS  Merge pull request #2207...  main  push  [SHA]  ~1m ago
```text

**Verification:**
- ☐ Workflow triggered automatically
- ☐ Status shows "IN_PROGRESS" or "COMPLETED"
- ☐ Commit matches merge commit SHA

**If Workflow Didn't Trigger:**
```text
⚠️ Manual Trigger Required
→ gh workflow run post-merge-validation-optimized.yml -r main
→ Wait 1-2 minutes for workflow to appear
```text

---

### Step 3.2: Monitor Test Execution (2-15 min after merge)

**Location:** GitHub Actions run details  
**Time:** ~5-10 minutes (watch progress)

```bash
# Get run ID
RUN_ID=$(gh run list --workflow=post-merge-validation-optimized.yml -b main -n 1 --json databaseId -q '.[0].databaseId')

# View workflow progress
gh run view $RUN_ID --log

# Check specific jobs
gh run view $RUN_ID --json jobs
```text

**Expected Jobs & Timeline:**

| Job | Duration | Status |
|-----|----------|--------|
| Setup | 1 min | ✅ |
| Dependency Validation | 2 min | ✅ |
| Full Test Suite | 8 min | ✅ |
| Coverage Report | 2 min | ✅ |
| Docker Build | 5 min | ✅ (if enabled) |
| Artifact Upload | 2 min | ✅ |

**Failure Response:**

If any job fails:
```text
🚨 WORKFLOW FAILURE DETECTED
→ gh run view $RUN_ID --log > failure-log.txt
→ Analyze logs for root cause
→ Determine if rollback needed (see Section 10)
```text

---

### Step 3.3: Verify Coverage Report (15-20 min after merge)

**Location:** GitHub Actions artifacts or coverage portal  
**Time:** ~2 minutes

```bash
# View artifacts generated
gh run view $RUN_ID --json artifacts

# Download coverage report
gh run download $RUN_ID -n coverage-report

# View report
cat coverage-report/coverage-summary.txt
```text

**Expected Coverage Metrics:**

```text
Name                 Stmts   Miss  Cover   Missing
----------------------------------------------------
src/                   850    20   97.6%   15-17, 45-48
src/module1/           220     5   97.7%   12, 89-91
src/module2/           180     3   98.3%   55-57
----------------------------------------------------
TOTAL                  1250    28   97.8%
```text

**Validation:**
- ☐ Overall coverage ≥ 96%
- ☐ No critical untested paths
- ☐ No regression from previous release

**If Coverage Below 96%:**
```text
⚠️ COVERAGE SHORTFALL
→ Determine if issue or acceptable variance
→ Review missing lines for severity
→ Document decision
→ If critical: proceed to rollback
```text

---

### Step 3.4: Docker Image Validation (20-30 min after merge)

**Location:** GitHub Actions run logs  
**Time:** ~2-3 minutes

```bash
# Check Docker build job output
gh run view $RUN_ID --log | grep -A 50 "Docker Build"

# Verify image was pushed
gh run view $RUN_ID --json artifacts | grep docker

# Test image locally (optional)
docker pull ghcr.io/aries-serpent/codex:latest
docker run --rm ghcr.io/aries-serpent/codex:latest --version
```text

**Expected Output:**
```text
Successfully built Docker image
Image SHA: sha256:[...hash...]
Image pushed to: ghcr.io/aries-serpent/codex:latest
```text

**Validation:**
- ☐ CPU-only base image used
- ☐ No GPU packages detected in image
- ☐ All dependencies installed
- ☐ Image runs successfully

---

### Step 3.5: Workflow Completion Check (30-35 min after merge)

**Location:** GitHub Actions  
**Time:** ~2 minutes

```bash
# Check final workflow status
gh run view $RUN_ID

# Expected: workflow-conclusion = success
# Expected: All jobs status = completed with ✓
```text

**Expected Output:**
```text
✓ WORKFLOW COMPLETED SUCCESSFULLY
  Total Duration: ~32 minutes
  Jobs Passed: 8/8
  Status: SUCCESS
```text

**Validation Checklist:**
- ☐ Workflow status: SUCCESS
- ☐ All jobs completed
- ☐ No retries or manual interventions
- ☐ Artifacts uploaded
- ☐ Notifications sent

**If Workflow Failed:**
```text
🚨 WORKFLOW FAILURE - ESCALATE
→ Document exact failure point
→ Review error messages in logs
→ Contact DevOps team
→ Proceed to ROLLBACK if critical
```text

---

## ✅ PHASE 4: HEALTH CHECK & FINALIZATION (10 minutes)

### Step 4.1: Main Branch Verification

**Location:** Local terminal  
**Time:** ~2 minutes

```bash
# Pull latest main branch
git checkout main
git pull origin main

# Verify merge commit present
git log --oneline -5 main

# Check file changes applied
git diff main~1 main --name-only | wc -l
# Expected: 126 files changed

# Verify key files present
test -f .github/coverage_threshold.txt && echo "✓ Coverage threshold file present"
test -f .github/docs/AGENTS_PR2224*.md && echo "✓ Review response doc present"
grep -q "96" .github/coverage_threshold.txt && echo "✓ Coverage threshold set to 96%"
```text

**Expected Output:**
```text
65e02ec Merge pull request #2207...
[previous commits]
---
126
✓ Coverage threshold file present
✓ Review response doc present
✓ Coverage threshold set to 96%
```text

---

### Step 4.2: Deployment Status Notification

**Location:** Slack #deployments channel  
**Time:** ~2 minutes

**Success Message Template:**

```text
✅ DEPLOYMENT SUCCESSFUL: PR #2207

📊 Summary:
  Merge Time: [timestamp]
  Duration: ~60 minutes (planned)
  Actual Duration: ___ minutes
  
📈 Post-Merge Validation Results:
  ✓ All 8 workflow jobs: PASS
  ✓ Test coverage: 97.8% (target: 96%)
  ✓ Docker build: SUCCESS
  ✓ Artifact archival: COMPLETE
  
🔍 Key Changes Deployed:
  ✓ CI/CD guidelines: .github/Copilot.md
  ✓ Coverage threshold: .github/coverage_threshold.txt (96%)
  ✓ Security configuration: .bandit.yaml updated
  ✓ GPU packages: Removed (CPU-only confirmed)
  
📋 Next Steps:
  [ ] Monitor application logs for 2 hours
  [ ] Verify no error spikes
  [ ] Confirm user-facing functionality
  [ ] Schedule post-deployment review

Deployment completed by: @[your-username]
Approvals: @qa-team, @security-team, @devops-team
```text

---

### Step 4.3: Follow-Up Actions

**Location:** GitHub Issues & Project Board  
**Time:** ~2 minutes

**Create Follow-Up Issues:**

```bash
# Issue 1: Implement PR #2224 review comments
gh issue create --title "Implement PR #2224 Code Review Responses" \
  --body "Address code quality feedback documented in .github/docs/AGENTS_PR2224_Review_Comments_Response_Copilot.md" \
  --label enhancement --project "Development"

# Issue 2: Monitor coverage trends
gh issue create --title "Monitor Coverage Trends Post-PR2207" \
  --body "Track coverage over next 2 sprints to ensure 96% threshold sustainable" \
  --label monitoring --project "QA"

# Issue 3: GPU support planning (future)
gh issue create --title "Plan GPU Support Implementation" \
  --body "GPU packages removed for PR #2207. Plan re-introduction with proper CI/CD support." \
  --label future --project "Infrastructure"
```text

---

## 🔄 PHASE 5: POST-DEPLOYMENT MONITORING (Continuous for 2 hours)

### Step 5.1: Application Log Monitoring

**Time:** 2 hours post-merge

```bash
# Monitor application logs for errors
tail -f logs/application.log | grep ERROR

# Check error rates
curl http://metrics.example.com/api/error-rate

# Verify no new exception patterns
grep -i "exception\|traceback\|fatal" logs/application.log | wc -l
# Expected: 0 or very low (baseline)
```text

**Acceptable Error Baseline:**
- No new error types
- Error rate unchanged from pre-deployment
- No cascading failures

---

### Step 5.2: Health Check Dashboard

**Time:** Every 15 minutes for 2 hours

**Metrics to Monitor:**

| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| CPU Usage | 40-60% | > 80% |
| Memory Usage | 50-70% | > 85% |
| Request Latency | 100-200ms | > 500ms |
| Error Rate | < 0.1% | > 1% |
| Deployment Status | GREEN | YELLOW/RED |

```bash
# Quick health check command
curl http://health.example.com/api/status | jq .
```text

---

### Step 5.3: User Impact Assessment

**Time:** Continuous, with formal review at 2-hour mark

**Checks:**
- ☐ No user-reported issues in support channel
- ☐ No spike in error logs
- ☐ Feature functionality verified
- ☐ Performance metrics normal

**If Issues Detected:**
```text
⚠️ POTENTIAL ISSUE - Assess Severity

MINOR (< 5 users affected):
  → Log issue, continue monitoring
  → Create bug report for next sprint

MAJOR (> 5 users affected):
  → Initiate incident response
  → Consider rollback (see Section 10)

CRITICAL (Production down):
  → EXECUTE IMMEDIATE ROLLBACK
  → See Rollback Procedures below
```text

---

## 🔁 EMERGENCY: ROLLBACK PROCEDURES

### Trigger Conditions for Rollback

**Automatic Rollback Decision Criteria:**

- [ ] Post-merge validation workflow failed (exit code ≠ 0)
- [ ] Coverage dropped below 96%
- [ ] Critical security vulnerability discovered
- [ ] Application not starting post-deployment
- [ ] Error rate > 5x baseline

**Manual Rollback Decision Criteria:**

- [ ] Multiple user reports of broken features
- [ ] Performance degradation (latency > 2x)
- [ ] Data corruption or loss
- [ ] Security breach confirmed

### Rollback Execution

**Step 1: Announce Rollback (1 minute)**

```bash
# Notify team
echo "🚨 ROLLBACK INITIATED - PR #2207" | slurp-notify @dev-team
```text

**Step 2: Execute Rollback Command (1 minute)**

```bash
# Revert the merge commit
gh pr revert 2207 --repo Aries-Serpent/_codex_

# Verify revert PR created
gh pr list --repo Aries-Serpent/_codex_ -s open -l revert
```text

**Step 3: Create Incident Report (5 minutes)**

```bash
gh issue create \
  --title "Incident: PR #2207 Rollback Executed" \
  --body "
## Rollback Reason
[Specific reason from trigger list]

## Timeline
- Merge: [time]
- Issue Detected: [time]
- Rollback Initiated: [time]

## Impact
- Duration: [minutes]
- Users Affected: [number]
- Features Down: [list]

## Root Cause Analysis
[To be completed post-incident]

## Prevention
[Lessons learned and preventive measures]
" \
  --label incident --label rollback
```text

**Step 4: Post-Incident Review (Within 24 hours)**

```text
Participants:
  - Author (mbaetiong)
  - Security Lead
  - QA Lead
  - DevOps Lead
  - Incident Commander

Agenda:
  1. Timeline review
  2. Root cause analysis
  3. Contributing factors
  4. Corrective actions
  5. Follow-up items
```text

---

## 📞 SUPPORT CONTACTS

**During Deployment Execution:**

| Issue | Contact | Priority | Response Time |
|-------|---------|----------|-----------------|
| Technical Error | DevOps Team | URGENT | 5 min |
| Security Alert | @security-lead | CRITICAL | 2 min |
| Coverage Problem | @qa-lead | HIGH | 10 min |
| General Question | @maintainers | NORMAL | 30 min |

**Emergency Escalation:**
- On-Call DevOps: _____________________
- On-Call Security: _____________________
- Incident Commander: _____________________

---

**Playbook Version:** 1.0  
**Last Updated:** 2024-11-14 17:46:51 UTC  
**Next Review:** Post-deployment (2024-11-14 19:46:51 UTC)  
**Author:** mbaetiong | **Reviewer:** @maintainers
