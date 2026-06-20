# TRACK 4: Registry Configuration & Authentication Agent Brief

**Campaign:** Comprehensive Automation Campaign (Discussion #4872)  
**Track:** 4 - Registry Configuration & Authentication (Item 1)  
**Agent Assignment:** [PENDING - unified-governance-gate or general-purpose]  
**Agent ID:** automation-campaign-track4-registry  
**Duration:** 4-5 hours  
**Timeline:** Phase 2 Medium Priority (can start parallel to Phase 1 or after)

---

## EXECUTIVE BRIEF

Automate registry configuration validation and credential injection using Cognitive Brain patterns and webhook infrastructure. Enable one-time credential setup followed by fully automated validation and registry management.

**Input:** Cognitive Brain patterns, registry requirements from maintainer_execution documentation  
**Output:** Registry validation workflow + Cognitive Brain integration + webhook patterns  
**Success Criteria:** Workflow template created, registry patterns documented, validation script functional

---

## DETAILED TASKS

### Task 4.1: Cognitive Brain Registry Pattern Query (1 hour)

**Objective:** Query Cognitive Brain for registry configuration patterns and best practices

**Actions:**
1. Create `scripts/cognitive/query_registry_patterns.py`:
   - Query Cognitive Brain for registry configuration history
   - Extract patterns for: DockerHub, GHCR, private registries
   - Identify best practices and anti-patterns
   - Generate pattern confidence scores
   - Output to JSON: `registry_patterns.json`

2. Create pattern index:
   - `.codex/REGISTRY_PATTERNS_INDEX.md`
   - Document all discovered patterns
   - Include confidence levels
   - Link to supporting evidence

3. Integrate with Cognitive Brain:
   - Use Cognitive Brain API for pattern retrieval
   - Store query results for future reference
   - Enable pattern reuse across deployments

**Deliverables:**
- `scripts/cognitive/query_registry_patterns.py` (functional)
- `.codex/REGISTRY_PATTERNS_INDEX.md` (documentation)
- `registry_patterns.json` (pattern data)
- `.codex/TRACK_4_TASK_1_PATTERN_QUERY.md` (execution report)

**Success Criteria:**
- [ ] Pattern query script functional
- [ ] Cognitive Brain integration working
- [ ] Registry patterns documented
- [ ] Confidence scores assigned

---

### Task 4.2: Registry Validation Against Patterns (1.5 hours)

**Objective:** Create validation script to check registry configuration against discovered patterns

**Actions:**
1. Create `scripts/cognitive/validate_registry_config.py`:
   - Accept registry configuration input
   - Check against discovered patterns
   - Calculate configuration confidence score
   - Identify deviations from best practices
   - Generate validation report
   - Threshold: 0.8+ confidence for approval

2. Create validation rules:
   - Registry connectivity check
   - Authentication method validation
   - Registry credentials validation
   - Namespace/organization structure check
   - Network access verification

3. Generate validation report:
   - `.codex/REGISTRY_VALIDATION_REPORT.json`
   - Include all checks with results
   - Identify any blocking issues
   - Provide remediation suggestions

**Deliverables:**
- `scripts/cognitive/validate_registry_config.py` (functional)
- `.codex/REGISTRY_VALIDATION_RULES.md` (documentation)
- `registry_validation_report.json` (sample report)
- `.codex/TRACK_4_TASK_2_VALIDATION_SCRIPT.md` (execution report)

**Success Criteria:**
- [ ] Validation script functional
- [ ] All rules implemented
- [ ] Confidence scoring working
- [ ] Report generation clear

---

### Task 4.3: Registry Connectivity Testing (1 hour)

**Objective:** Create script to test registry connectivity and authentication

**Actions:**
1. Create `scripts/registry/test_connectivity.py`:
   - Test registry endpoint availability
   - Test DNS resolution
   - Test authentication with provided credentials
   - Test image pull permission
   - Test image push permission (if applicable)
   - Generate connectivity report

2. Implement for multiple registries:
   - DockerHub
   - GitHub Container Registry (GHCR)
   - Private Docker Registry
   - Amazon ECR (if applicable)
   - Google Container Registry (if applicable)

3. Create test report:
   - `.codex/REGISTRY_CONNECTIVITY_REPORT.md`
   - Include test results
   - Document any issues found
   - Provide remediation steps

**Deliverables:**
- `scripts/registry/test_connectivity.py` (functional)
- `.codex/REGISTRY_CONNECTIVITY_TEST_GUIDE.md` (documentation)
- `registry_connectivity_report.json` (test results)
- `.codex/TRACK_4_TASK_3_CONNECTIVITY_TESTING.md` (execution report)

**Success Criteria:**
- [ ] Connectivity tests working for all registry types
- [ ] Authentication tests functional
- [ ] Permission tests implemented
- [ ] Test report generated

---

### Task 4.4: GitHub Actions Workflow Template (1 hour)

**Objective:** Create reusable workflow for registry validation and credential injection

**Actions:**
1. Create `.github/workflows/cognitive-registry-validation.yml`:
   ```yaml
   # Inputs:
   # - registry_type: Registry type (dockerhub, ghcr, private)
   # 
   # Steps:
   # 1. Query Cognitive Brain for patterns
   # 2. Validate registry configuration
   # 3. Test registry connectivity
   # 4. Create approval gate for credential injection
   # 5. Store registry metadata in repo variables
   # 6. Trigger webhook to Cognitive Brain
   # 7. Create PR with credential injection instructions
   ```

2. Implement workflow:
   - Checkout repository
   - Call query_registry_patterns.py
   - Call validate_registry_config.py
   - Call test_connectivity.py
   - Create approval PR
   - Trigger webhook on completion
   - Store results in GitHub Actions artifacts

3. Add error handling:
   - Validation failure → manual review required
   - Connectivity test failure → diagnostic report
   - Approval gate → requires manual intervention

**Deliverables:**
- `.github/workflows/cognitive-registry-validation.yml` (complete workflow)
- `.codex/COGNITIVE_REGISTRY_WORKFLOW_GUIDE.md` (operational guide)
- `.codex/TRACK_4_TASK_4_WORKFLOW_IMPLEMENTATION.md` (execution report)

**Success Criteria:**
- [ ] Workflow syntax valid
- [ ] All steps execute successfully
- [ ] Approval gate operational
- [ ] Workflow operational in GitHub Actions

---

### Task 4.5: Webhook Integration & Repository Variables (1 hour)

**Objective:** Integrate webhook notifications and store registry metadata in repository variables

**Actions:**
1. Create webhook integration:
   - `.codex/WEBHOOK_REGISTRY_INTEGRATION.md`
   - Document webhook payload structure
   - Include HMAC-SHA256 verification
   - Define webhook security requirements

2. Create `scripts/webhook/notify_brain.py`:
   - Trigger webhook to Cognitive Brain on registry events
   - Include registry validation results
   - Store results in Cognitive Brain
   - Enable pattern learning from deployments

3. Store registry metadata:
   - Update `REGISTRY_TYPE` in GitHub Actions variables
   - Update `REGISTRY_ENDPOINT` in GitHub Actions variables
   - Update `REGISTRY_NAMESPACE` in GitHub Actions variables
   - Store validation timestamp

4. Create validation:
   - Verify webhook delivery
   - Confirm Cognitive Brain received data
   - Validate stored variables

**Deliverables:**
- `scripts/webhook/notify_brain.py` (functional)
- `.codex/WEBHOOK_REGISTRY_INTEGRATION.md` (documentation)
- `.codex/WEBHOOK_VALIDATION_REPORT.md` (validation results)
- `.codex/TRACK_4_TASK_5_WEBHOOK_INTEGRATION.md` (execution report)

**Success Criteria:**
- [ ] Webhook script functional
- [ ] Webhook delivery verified
- [ ] Repository variables updated
- [ ] Cognitive Brain integration confirmed

---

## INTEGRATION REQUIREMENTS

### Cognitive Brain Integration
- Query API: `query_registry_patterns(registry_type, environment)`
- Store API: `store_registry_metadata(registry_config, validation_results)`
- Pattern retrieval: Fetch registry best practices
- Learning loop: Store validation results for future pattern improvement

### Repository Variables Integration
- `REGISTRY_TYPE` - Primary registry type (dockerhub, ghcr, private)
- `REGISTRY_ENDPOINT` - Registry endpoint URL
- `REGISTRY_NAMESPACE` - Organization/namespace name
- `REGISTRY_VALIDATION_STATUS` - Latest validation status
- `REGISTRY_LAST_VALIDATED` - Timestamp of last validation

### Webhook Integration
- Webhook endpoint: Configure in GitHub repository settings
- Payload format: JSON with validation results
- Security: HMAC-SHA256 signature verification
- Retry policy: Automatic retry on failure

---

## DEPENDENCIES & BLOCKERS

### Required Before Start
- [ ] Cognitive Brain API available and documented
- [ ] Webhook infrastructure operational
- [ ] GitHub repository settings allow webhook configuration

### External Dependencies
- [ ] Registry endpoints accessible (for connectivity testing)
- [ ] Registry credentials available for authentication testing
- [ ] Network access to all registry types

### Known Blockers
- **Credentials Required:** Initial registry credentials must be provided (one-time setup)
- **Approval Gate:** Credential injection requires manual approval
- **Registry Access:** Tests require read/write access to registry

---

## SUCCESS DEFINITION

**Track 4 Complete When:**

1. ✅ All 5 tasks complete with deliverables
2. ✅ Cognitive Brain pattern query functional
3. ✅ Registry validation script tested and working
4. ✅ Connectivity tests passing for supported registries
5. ✅ Workflow template created and passes GitHub syntax validation
6. ✅ Webhook integration verified
7. ✅ Repository variables populated
8. ✅ All artifacts in `.codex/` and committed
9. ✅ Documentation complete and accurate
10. ✅ No breaking issues; all success criteria met

**Effort Target:** 4-5 hours  
**ROI:** 1-1.5 hours saved per deployment (credentials one-time, validation fully automated)

---

## REPORTING

**Progress Report Location:** `.codex/TRACK_4_REGISTRY_AUTOMATION_REPORT.md`  
**Update Frequency:** After each task completion  
**Final Report:** Consolidate into `.codex/AUTOMATION_CAMPAIGN_PROGRESS_DASHBOARD.md`

---

## AUTHORITY & APPROVAL

**Campaign Authority:** @mbaetiong (D-level autonomy)  
**Execution Authority:** This agent brief  
**Status:** READY FOR DELEGATION (after Phase 1 gate or in parallel)

