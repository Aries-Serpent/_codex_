# ⚙️ PHASE X TRACK GAMMA - GITHUB ACTIONS WORKFLOW ENFORCEMENT BRIEF

**Track:** γ (GitHub Actions Workflow Compliance)  
**Execution Window:** 2026-06-20 12:00Z → 2026-06-21 10:00Z (22 hours)  
**Agents:** 3 (parallel, independent)  
**Root Cause:** 16% of CI failures (90/543) from workflow syntax, deprecated actions, version mismatches

---

## PROBLEM STATEMENT

**Current State:**
- 90+ workflow failures from syntax errors + deprecated actions
- 40+ workflows use `@latest` instead of pinned action versions
- 25+ workflows use deprecated GitHub Actions syntax
- Concurrency/timeout rules inconsistently applied

**Root Causes:**
1. **Deprecated Action Versions** (40% of failures)
   - `actions/checkout@v3` (deprecated, should use v4)
   - `actions/setup-python@v3` (should use v4 or v5)
   - `actions/cache@v2` (should use v3)
   
2. **Workflow Syntax Issues** (35% of failures)
   - Missing `shell: bash` specifications
   - Incorrect `run:` field formatting (no pipe `|` for multi-line)
   - Invalid job dependencies (needs → if conditions)

3. **Concurrency & Timeout** (25% of failures)
   - No concurrency limits (causing duplicate runs)
   - Missing job timeouts (runs infinitely)
   - Branch scoping incorrect or missing

---

## SUCCESS METRICS

| Metric | Target | Verification |
|--------|--------|--------------|
| **Workflow Syntax Errors** | <5 (94% reduction) | actionlint audit |
| **Deprecated Actions** | 0 instances | Version scan audit |
| **Pinned Versions** | 100% (no @latest) | grep audit |
| **Concurrency Compliance** | 100% of workflows | Policy scan |
| **Timeout Compliance** | 100% of workflows | Policy scan |

---

## AGENT ASSIGNMENTS

### Agent 1: workflow-compliance-guardian
**Task:** Enforce governance rules (concurrency, timeouts, branch scoping)

**Responsibilities:**
1. Scan all 186 workflows for compliance violations
2. Enforce rules:
   - All workflows must have concurrency limits
   - All jobs must have timeouts (max 6 hours)
   - All workflows must have branch scoping
3. Generate compliance report:
   - `.codex/TRACK_GAMMA_COMPLIANCE_VIOLATIONS.md`
   - 40+ workflows missing concurrency limits
   - 30+ workflows missing timeouts
   - 20+ workflows missing branch scoping
4. Output: Auto-fix patches for all violations

**Success Criteria:**
- 100% of workflows have concurrency limits
- 100% of workflows have job timeouts
- 100% of workflows have branch scoping

**Output:** `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_COMPLIANCE.md`

---

### Agent 2: workflow-ci-fixer
**Task:** Fix workflow syntax errors and deprecated action versions

**Responsibilities:**
1. Run actionlint to identify syntax errors
2. Fix issues:
   - Update deprecated actions to latest stable versions (v4/v5)
   - Add `shell: bash` specifications
   - Fix multi-line `run:` fields (use `|` block scalar)
   - Correct job dependencies
3. Generate workflow updates:
   - `.codex/TRACK_GAMMA_WORKFLOW_FIXES.yaml`
   - 25+ action version updates
   - 30+ syntax fixes
4. Validate: actionlint passes on all workflows

**Success Criteria:**
- All deprecated actions updated
- All workflow syntax valid (actionlint clean)
- All workflows use pinned action versions

**Output:** `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_SYNTAX_FIXES.md`

---

### Agent 3: workflow-optimization-agent
**Task:** Remove redundancy and optimize workflow parallelism

**Responsibilities:**
1. Analyze 186 workflows for consolidation opportunities
2. Identify duplicates:
   - 6 coverage workflows → 2 consolidated
   - 5 validation workflows → 2 consolidated
   - 4 security workflows → 2 consolidated
3. Generate consolidation plan:
   - `.codex/TRACK_GAMMA_CONSOLIDATION_OPPORTUNITIES.md`
   - 50+ workflows eligible for merge
   - Estimated 37% reduction (186 → 120)
4. Recommend matrix parallelism improvements

**Success Criteria:**
- Consolidation plan validates against PARITY_CHECKLIST.md
- No loss of coverage/validation capability
- 37% reduction target achievable

**Output:** `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_OPTIMIZATION.md`

---

## DELIVERABLES

### Track Output (Final)
- **File:** `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_FIXES.md`
- **Contents:**
  - Executive summary (90 failures → <5)
  - Compliance enforcement report
  - Workflow syntax fixes
  - Consolidation opportunities
  - Deployment readiness checklist

### Agent-Specific Outputs
1. `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_COMPLIANCE.md` (Agent 1)
2. `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_SYNTAX_FIXES.md` (Agent 2)
3. `.codex/PHASE_X_TRACK_GAMMA_WORKFLOW_OPTIMIZATION.md` (Agent 3)

---

## SUCCESS GATE VERIFICATION

**Gate 3: Workflow Compliance**
- ✅ <5 syntax errors remaining (from 90)
- ✅ 0 deprecated actions in use
- ✅ 100% of workflows pinned to specific versions
- ✅ actionlint audit passes

---

**Track Brief Created:** 2026-06-20T06:24:58Z UTC
