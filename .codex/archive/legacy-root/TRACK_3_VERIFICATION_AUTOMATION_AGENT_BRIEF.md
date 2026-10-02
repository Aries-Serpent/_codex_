# TRACK 3: Post-Deployment Verification Automation Agent Brief

**Campaign:** Comprehensive Automation Campaign (Discussion #4872)  
**Track:** 3 - Post-Deployment Verification Runbook (Item 8)  
**Agent Assignment:** autonomous-test-healer-agent (or general-purpose)  
**Agent ID:** automation-campaign-track3-verification  
**Duration:** 3-4 hours  
**Timeline:** Phase 1 Quick Wins (parallel with Tracks 1,2)

---

## EXECUTIVE BRIEF

Automate post-deployment verification procedures that validate successful deployment across all environments. Create comprehensive verification runbooks, health check procedures, and success criteria that enable rapid go/no-go decisions after deployment.

**Input:** E2E test suite, health check patterns, critical path documentation  
**Output:** Verification runbook + workflow template + smoke tests  
**Success Criteria:** All automated smoke tests passing, verification checklist operational

---

## DETAILED TASKS

### Task 3.1: Critical Path Extraction (0.75 hours)

**Objective:** Extract critical business paths from codebase for verification

**Actions:**
1. Analyze codebase to identify critical paths:
   - Authentication flow
   - Data ingestion pipeline
   - Model inference pipeline
   - API response paths
   - Data persistence

2. Create `scripts/deployment/extract_critical_paths.py`:
   - Scan source code for main entry points
   - Identify critical functions and classes
   - Extract documented business flows
   - Document expected success paths
   - Generate critical path diagram (mermaid)

3. Generate critical paths document:
   - `.codex/CRITICAL_PATHS_FOR_VERIFICATION.md`
   - Include sequence diagrams
   - Include expected latencies
   - Include expected error handling

**Deliverables:**
- `scripts/deployment/extract_critical_paths.py` (functional)
- `.codex/CRITICAL_PATHS_FOR_VERIFICATION.md` (documentation)
- `.codex/CRITICAL_PATHS_DIAGRAM.md` (mermaid diagrams)
- `.codex/TRACK_3_TASK_1_CRITICAL_PATHS.md` (execution report)

**Success Criteria:**
- [ ] All critical paths identified
- [ ] Critical path documentation clear
- [ ] Expected latencies documented
- [ ] Diagrams generated and understandable

---

### Task 3.2: Verification Checklist Generation (1 hour)

**Objective:** Create comprehensive verification checklist for post-deployment validation

**Actions:**
1. Create `scripts/deployment/generate_verify_checklist.py`:
   - Input: Target environment, deployment version
   - Generate pre-deployment checks
   - Generate per-critical-path verification steps
   - Generate health check procedures
   - Generate success criteria per step
   - Generate edge case testing procedures

2. Generate checklist templates:
   - `.codex/verification-checklists/VERIFICATION_CHECKLIST_PRODUCTION.md`
   - `.codex/verification-checklists/VERIFICATION_CHECKLIST_STAGING.md`
   - `.codex/verification-checklists/VERIFICATION_CHECKLIST_DEV.md`

3. Checklist format:
   - [ ] Step description
   - Expected: What should happen
   - Verify: How to verify
   - Action on failure: What to do if verification fails
   - Estimated time: How long should this take

**Deliverables:**
- `scripts/deployment/generate_verify_checklist.py` (functional)
- `.codex/verification-checklists/` (directory with environment-specific checklists)
- `.codex/VERIFICATION_CHECKLIST_GUIDE.md` (usage guide)
- `.codex/TRACK_3_TASK_2_VERIFICATION_CHECKLISTS.md` (execution report)

**Success Criteria:**
- [ ] Checklists generated for all environments
- [ ] All steps clear and actionable
- [ ] Expected outcomes documented
- [ ] Failure procedures documented

---

### Task 3.3: Automated Smoke Tests (1 hour)

**Objective:** Implement automated smoke tests that validate core functionality

**Actions:**
1. Create `tests/e2e/smoke_tests.py` (or enhance existing):
   - Authentication test (successful login)
   - Health endpoint test
   - Data ingestion test (sample data)
   - API response test (typical request)
   - Data retrieval test
   - Error handling test (invalid request)
   - Timeout handling test

2. Create `tests/e2e/critical_path_tests.py`:
   - Test each critical path identified in Task 3.1
   - Include success path
   - Include common error paths
   - Include edge cases
   - Document expected latencies

3. Configuration:
   - Environment-specific test data
   - Configurable endpoints and timeouts
   - Clear pass/fail criteria
   - Detailed failure reporting

**Deliverables:**
- `tests/e2e/smoke_tests.py` (comprehensive test suite)
- `tests/e2e/critical_path_tests.py` (critical path validation)
- `.codex/SMOKE_TEST_GUIDE.md` (how to run and interpret results)
- `.codex/TRACK_3_TASK_3_SMOKE_TESTS.md` (execution report)

**Success Criteria:**
- [ ] All smoke tests passing in dev environment
- [ ] Critical path tests comprehensive
- [ ] Test execution time <5 minutes
- [ ] Clear pass/fail reporting

---

### Task 3.4: Health Check Procedures (0.75 hours)

**Objective:** Document health check procedures and endpoints

**Actions:**
1. Identify all health check endpoints:
   - `/health` - Basic liveness check
   - `/ready` - Readiness check
   - `/metrics` - Prometheus metrics
   - `/status` - Detailed status endpoint (if available)

2. Create `scripts/deployment/health_check_runner.py`:
   - Iterate through all health check endpoints
   - Validate response codes (200 expected)
   - Parse response content
   - Check response time <threshold
   - Generate health report

3. Create health check guide:
   - `.codex/HEALTH_CHECK_PROCEDURES.md`
   - Include what each endpoint checks
   - Include expected response format
   - Include failure interpretation
   - Include remediation procedures

**Deliverables:**
- `scripts/deployment/health_check_runner.py` (functional)
- `.codex/HEALTH_CHECK_PROCEDURES.md` (documentation)
- `.codex/HEALTH_CHECK_RESPONSES.md` (expected responses reference)
- `.codex/TRACK_3_TASK_4_HEALTH_CHECKS.md` (execution report)

**Success Criteria:**
- [ ] All health endpoints identified
- [ ] Health check script functional
- [ ] Expected responses documented
- [ ] Interpretation guide clear

---

### Task 3.5: Success Criteria Documentation (0.5 hours)

**Objective:** Document success criteria for each environment

**Actions:**
1. Create `.codex/SUCCESS_CRITERIA_BY_ENVIRONMENT.md`:
   - Dev environment criteria
   - Staging environment criteria
   - Production environment criteria
   - Rollback decision criteria

2. Define criteria:
   - All smoke tests passing
   - All health checks operational
   - All critical paths verified
   - No error spikes in logs
   - Response times within SLA
   - No data inconsistencies

3. Create go/no-go decision matrix:
   - Passing criteria → GO (approve for production)
   - Warning criteria → CONDITIONAL (investigate before GO)
   - Failing criteria → NO-GO (trigger rollback)

**Deliverables:**
- `.codex/SUCCESS_CRITERIA_BY_ENVIRONMENT.md` (comprehensive criteria)
- `.codex/GO_NO_GO_DECISION_MATRIX.md` (decision guide)
- `.codex/TRACK_3_TASK_5_SUCCESS_CRITERIA.md` (execution report)

**Success Criteria:**
- [ ] Criteria specific to each environment
- [ ] Clear pass/fail thresholds
- [ ] Decision matrix unambiguous
- [ ] Integration with automated checks clear

---

### Task 3.6: GitHub Actions Workflow Template (0.5 hours)

**Objective:** Create reusable workflow for automated post-deployment verification

**Actions:**
1. Create `.github/workflows/automated-post-deployment-verification.yml`:
   ```yaml
   # Triggered: workflow_dispatch
   # Inputs:
   # - environment: Environment to verify (dev/staging/production)
   #
   # Steps:
   # 1. Generate verification checklist
   # 2. Run automated smoke tests
   # 3. Execute health checks
   # 4. Generate verification report
   # 5. Evaluate go/no-go decision
   # 6. Create artifact
   # 7. Output decision status
   ```

2. Implement workflow:
   - Checkout repository
   - Generate verification checklist
   - Run smoke tests
   - Run critical path tests
   - Run health checks
   - Generate comprehensive report
   - Store report as artifact
   - Comment on PR/release with results

**Deliverables:**
- `.github/workflows/automated-post-deployment-verification.yml` (complete workflow)
- `.codex/AUTOMATED_VERIFICATION_WORKFLOW_GUIDE.md` (operational guide)
- `.codex/TRACK_3_TASK_6_WORKFLOW_IMPLEMENTATION.md` (execution report)

**Success Criteria:**
- [ ] Workflow syntax valid
- [ ] All steps execute successfully
- [ ] Verification results clear and actionable
- [ ] Workflow operational in GitHub Actions

---

## INTEGRATION REQUIREMENTS

### Test Framework
- Existing: pytest, E2E test infrastructure
- Extensions: Environment-specific fixtures
- Configuration: Load from environment variables

### Cognitive Brain Integration
- Query Cognitive Brain for verification patterns: "get_verification_patterns"
- Store verification results: "store_verification_results"
- Use Cognitive Brain for failure analysis

### Artifact Management
- Verification checklists: `.codex/verification-checklists/`
- Test results: `.codex/verification-results/`
- Health check reports: `.codex/health-reports/`
- Workflow artifacts: GitHub Actions artifacts

---

## DEPENDENCIES & BLOCKERS

### Required Before Start
- [ ] E2E test suite exists and passing
- [ ] Health check endpoints implemented
- [ ] Test data available for all environments

### External Dependencies
- [ ] All target environments deployed and accessible
- [ ] Test credentials available
- [ ] Network access to all health endpoints

### Known Blockers
- **Human Interpretation:** Verification results require human judgment for edge cases
- **Environment Access:** Staging and production environment access required

---

## SUCCESS DEFINITION

**Track 3 Complete When:**

1. ✅ All 6 tasks complete with deliverables
2. ✅ All smoke tests passing in all environments
3. ✅ Health check procedures validated
4. ✅ Verification checklist comprehensive and accurate
5. ✅ Success criteria clearly defined and documented
6. ✅ `.github/workflows/automated-post-deployment-verification.yml` created and operational
7. ✅ All artifacts in `.codex/` and committed
8. ✅ Documentation complete and accurate
9. ✅ No breaking issues; all success criteria met

**Effort Target:** 3-4 hours  
**ROI:** 2-3 hours saved per deployment

---

## REPORTING

**Progress Report Location:** `.codex/TRACK_3_VERIFICATION_RUNBOOK_REPORT.md`  
**Update Frequency:** After each task completion  
**Final Report:** Consolidate into `.codex/AUTOMATION_CAMPAIGN_PROGRESS_DASHBOARD.md`

---

## AUTHORITY & APPROVAL

**Campaign Authority:** @mbaetiong (D-level autonomy)  
**Execution Authority:** This agent brief  
**Status:** READY FOR DELEGATION
