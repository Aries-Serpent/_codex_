# 🚀 POST-MERGE FOLLOW-UP PROMPT — Multi-Lane Custom Agent Coordination

**Purpose:** Continue in-progress work, validations, and monitoring after merge to main/0D_base_.  
**Scope:** Release investigation, PR comment resolution, parallel agent delegation.  
**Last Updated:** 2026-07-20T02:53:41Z  
**Activation Trigger:** Post-merge to main OR 0D_base_ branch

---

## 🎯 MULTI-LANE AGENT DELEGATION FRAMEWORK

### Phase 1: Parallel Investigation (Activate Agents)
Delegate the following tasks **in parallel** to specialized custom agents:

#### **Lane 1: Release Success Investigation**
- **Agent:** `pypi-publishing-operations-agent`
- **Task:** Comparative analysis of successful vs. failed releases
- **Objectives:**
  1. Analyze successful release commits (reference: `0b670311`, `2bd5fbb1`)
  2. Extract configuration & workflow patterns from successful releases
  3. Document PyPI OIDC setup, token generation, and publish steps
  4. Compare successful process to recent failure patterns
  5. Identify configuration drift, missing permissions, or token scope issues
  6. Generate remediation playbook with step-by-step fixes
- **Deliverable:** `.codex/RELEASE_SUCCESS_COMPARISON_ANALYSIS.md`
- **Success Criteria:** 
  - Successful releases fully documented
  - Root cause of recent failures identified
  - Remediation steps clear and actionable

#### **Lane 2: PR Comment Review & Resolution**
- **Agent:** `post-merge-doc-alignment-agent` (or suitable reviewer)
- **Task:** Explicit review of ALL PR comments with unanswered questions
- **Objectives:**
  1. Extract all comments from current PR
  2. Identify unanswered or unresolved comments
  3. For each unanswered comment:
     - Determine if answer requires code investigation
     - Provide explicit response with supporting evidence
     - Link to relevant commits or code sections
     - Tag with resolving commit SHA if applicable
  4. Generate comment resolution summary
  5. Post explicit replies to maintainer comments
- **Deliverable:** `.codex/PR_COMMENT_RESOLUTION_SUMMARY.md`
- **Success Criteria:**
  - 100% of unanswered comments addressed
  - Each response includes commit SHA or evidence link
  - All maintainer concerns explicitly acknowledged

#### **Lane 3: CI/Deployment Validation**
- **Agent:** `ci-emergency-response-agent`
- **Task:** Validate CI/CD pipeline status post-merge
- **Objectives:**
  1. Check all workflow runs on merged commit
  2. Identify any post-merge failures
  3. Compare failure patterns to pre-merge baseline
  4. If failures exist:
     - Extract failure logs
     - Identify if failures are introduced by merge or pre-existing
     - Apply fixes if introduced by this merge
     - Escalate if pre-existing but blocking
  5. Verify all required checks pass
- **Deliverable:** `.codex/POST_MERGE_CI_VALIDATION_REPORT.md`
- **Success Criteria:**
  - All required workflows passing
  - No new failure patterns introduced
  - Deployment readiness confirmed

#### **Lane 4: Monitoring & Health Check**
- **Agent:** `workflow-health-monitor` + `performance-monitor-agent`
- **Task:** Post-merge system health monitoring
- **Objectives:**
  1. Monitor deployment health metrics (latency, errors, uptime)
  2. Compare metrics to baseline before merge
  3. Check for performance regressions
  4. Verify all integrated services operational
  5. Generate health baseline for future reference
- **Deliverable:** `.codex/POST_MERGE_HEALTH_BASELINE.md`
- **Success Criteria:**
  - All metrics within acceptable thresholds
  - No performance regressions detected
  - System operational and stable

#### **Lane 5: Documentation Alignment**
- **Agent:** `post-merge-doc-alignment-agent`
- **Task:** Ensure documentation aligns with merge changes
- **Objectives:**
  1. Identify documentation affected by merge
  2. Verify all links still valid
  3. Update stale references if any
  4. Sync API documentation with code changes
  5. Update version numbers in guides
- **Deliverable:** `.codex/POST_MERGE_DOC_ALIGNMENT_REPORT.md`
- **Success Criteria:**
  - All documentation links valid
  - No stale references
  - Version numbers accurate

---

## 🔍 RELEASE SUCCESS INVESTIGATION — DETAILED METHODOLOGY

### Step 1: Analyze Successful Release Pattern
**Reference Commits:** `0b670311` (GitHub Release), `2bd5fbb1` (PyPI 0.2.2)

```
For each successful release:
1. Extract commit metadata (author, timestamp, message)
2. Identify all changed files
3. Document workflow files used
4. Extract token/secret configuration
5. Note PyPI configuration state
6. Document GitHub Release creation process
7. Record any pre-release validation steps
```

### Step 2: Identify Success Factors
**Questions to Answer:**
- What authentication method was used? (Token vs OIDC)
- What version constraints were in place?
- How were pre-flight checks performed?
- What validation happened post-publish?
- Were there any manual approval steps?

### Step 3: Compare to Recent Failures
**Failure Analysis Pattern:**
```
For each recent failure:
1. Extract error message (exact)
2. Identify failure stage (build, publish, verify)
3. Determine root cause category:
   - Authentication/Token issue
   - Configuration mismatch
   - Workflow syntax error
   - Dependency conflict
   - Permission issue
4. Cross-reference with successful release workflow
5. Identify what step diverged from successful pattern
```

### Step 4: Generate Remediation Playbook
**Deliverable Format:**
```
# Release Fix Playbook

## Issue: [Description]
**Root Cause:** [From comparison analysis]
**Evidence:** [Commit refs showing difference]

### Fix Steps:
1. [Specific action]
2. [Verification step]
3. [Success criteria]

**Testing:** [How to validate before production]
```

---

## 💬 PR COMMENT RESOLUTION — EXPLICIT RESPONSE PROTOCOL

### Required Response Template
For **EACH** unanswered comment:

```
**Comment ID:** [GitHub comment ID]
**Original Question:** [Quote the question]
**Status:** RESOLVED ✅ / ACKNOWLEDGED / ESCALATED
**Resolving Commit:** [SHA or N/A]

**Response:**
[Explicit answer with supporting evidence]

**Evidence:**
- File: [path]
- Line: [line numbers]
- Change: [what was changed]
```

### Comment Categories & Response Requirements

| Category | Required | Example |
|----------|----------|---------|
| Code Review Question | YES | "Why was this function refactored?" |
| Security Alert | YES | "Is this vulnerability addressed?" |
| Test Coverage | YES | "Why is this path untested?" |
| Documentation Gap | YES | "Where is this documented?" |
| Design Decision | YES | "Why this approach vs. alternative?" |
| Acknowledgment Only | YES (Confirm) | "Got it, thanks for the note" |

### Process
1. **Extract Phase:** Automatically list all PR comments with status
2. **Analysis Phase:** For each unanswered comment, determine:
   - Is this a question requiring investigation?
   - Can it be answered with existing commit info?
   - Does it require new analysis/code changes?
3. **Response Phase:** Post explicit reply with:
   - Direct answer (not "we addressed this")
   - Commit SHA or code reference
   - Quote evidence from code/tests/docs
4. **Verification Phase:** Confirm no unanswered comments remain

---

## 🔄 RELEASE COMPARISON ANALYSIS — DETAILED CHECKLIST

### Reference: Successful Release (v0.2.2 / 2bd5fbb1)
**Proof:** https://pypi.org/project/codex-ml/0.2.2/

**Investigate:**
- [ ] What authentication method was used for PyPI upload?
- [ ] Were there any pre-release tags or versions?
- [ ] What was the workflow file state at publish time?
- [ ] Were there any manual steps in the release process?
- [ ] What was the Python environment setup?
- [ ] How was the build artifact created?
- [ ] What validation happened after publish?
- [ ] Were there any secrets or tokens rotated before/after?

### Recent Failure (v0.3.0+ attempts)
**Evidence:** PyPI workflow runs #1067-1068 (2026-07-19 to 2026-07-20)

**Investigate:**
- [ ] What is the error message exactly?
- [ ] At what stage does it fail (build vs. publish)?
- [ ] What changed in workflow between success and failure?
- [ ] Is OIDC configured differently than token auth was?
- [ ] Are token scopes/permissions correct?
- [ ] Is the PyPI project trusted publisher setup complete?
- [ ] Did build dependencies change?
- [ ] Are version numbers properly incremented?

### Comparison Matrix

| Aspect | v0.2.2 Success | Recent Failure | Delta | Action |
|--------|---|---|---|---|
| Auth Method | ? | OIDC | ? | Verify OIDC config |
| Workflow Version | ? | Latest | ? | Check for regressions |
| Token Permissions | ? | id-token:write | ? | Validate scopes |
| PyPI Config | ? | Trusted Publisher | ? | Verify trusted pub setup |
| Build Method | ? | `python -m build` | ? | Compare build steps |

---

## 📋 ACTIVATION CHECKLIST

### Pre-Agent Activation
- [ ] Read this prompt fully
- [ ] Identify current PR number and merge commit SHA
- [ ] Extract all PR comments into review queue
- [ ] Document any known failures or alerts
- [ ] Verify agent availability (check agent dashboard)

### Agent Coordination
- [ ] Lane 1 (Release Investigation) — **START**
- [ ] Lane 2 (PR Comment Resolution) — **START**
- [ ] Lane 3 (CI Validation) — **START**
- [ ] Lane 4 (Health Monitoring) — **START**
- [ ] Lane 5 (Doc Alignment) — **START**
- [ ] All lanes running in parallel ✅

### During Execution
- [ ] Monitor agent progress in real-time
- [ ] Escalate blockers immediately
- [ ] Check for inter-lane dependencies
- [ ] Log all findings to `.codex/` directory
- [ ] Post progress updates to PR

### Post-Completion (All Lanes)
- [ ] Review Lane 1 deliverable (release analysis)
- [ ] Verify Lane 2 responses (100% PR comments)
- [ ] Confirm Lane 3 status (CI passing)
- [ ] Validate Lane 4 metrics (health OK)
- [ ] Check Lane 5 links (docs aligned)
- [ ] Consolidate findings into final report
- [ ] Post session summary to PR

---

## 📊 EXPECTED DELIVERABLES

```
.codex/
├── POST_MERGE_FOLLOWUP_PROMPT.md ............. This document
├── RELEASE_SUCCESS_COMPARISON_ANALYSIS.md ... Lane 1 output
├── PR_COMMENT_RESOLUTION_SUMMARY.md ........ Lane 2 output
├── POST_MERGE_CI_VALIDATION_REPORT.md ...... Lane 3 output
├── POST_MERGE_HEALTH_BASELINE.md ........... Lane 4 output
├── POST_MERGE_DOC_ALIGNMENT_REPORT.md ...... Lane 5 output
└── POST_MERGE_CONSOLIDATION_SUMMARY.md .... Final summary
```

---

## 🚨 ESCALATION TRIGGERS

### Automatic Escalation Required If:
1. **Release Analysis:** Root cause not determinable from commit history
2. **PR Comments:** Unanswerable questions (policy decision needed)
3. **CI Validation:** Post-merge failures blocking deployment
4. **Health Check:** Metrics outside acceptable threshold ranges
5. **Doc Alignment:** Broken links or missing critical docs

### Escalation Process
```
1. Document blocker in session context
2. Tag @mbaetiong with issue details
3. Provide options (if decision needed)
4. Propose timeline for resolution
5. Continue with other lanes while escalated item resolves
```

---

## 📞 REFERENCE DOCUMENTATION

- **Successful Release:** https://github.com/Aries-Serpent/_codex_/commit/0b670311d5880dae1687a909ea27e65b5ef0518c
- **PyPI Release Proof:** https://pypi.org/project/codex-ml/0.2.2/
- **PyPI Publish Workflow:** `.github/workflows/pypi-publish.yml`
- **Monitoring Report:** `.codex/pypi_workflow_monitoring_2026_07_20.md`
- **Agent Accountability:** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

---

## ✅ COMPLETION CRITERIA

Post-merge follow-up is **COMPLETE** when:
- ✅ Lane 1: Release analysis delivered with remediation playbook
- ✅ Lane 2: All PR comments explicitly answered with commit refs
- ✅ Lane 3: CI validation confirms post-merge stability
- ✅ Lane 4: Health metrics within acceptable ranges
- ✅ Lane 5: All documentation links verified and updated
- ✅ All deliverables committed to `.codex/`
- ✅ Final consolidation summary posted to PR
- ✅ No escalated blockers remaining (or documented with timeline)

---

**Generated:** 2026-07-20T02:53:41Z  
**Scope:** All merges to main and 0D_base_ branches  
**Status:** 🟢 READY FOR ACTIVATION
