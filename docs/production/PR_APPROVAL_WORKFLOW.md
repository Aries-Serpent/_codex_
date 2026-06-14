# Phase 6 Batch 2 — PR Approval Workflow & Governance Gates

**Version:** 1.0.0  
**Status:** FINAL  
**Audience:** All contributors, code reviewers, CI/CD operators  
**Last Updated:** 2026-02-22

---

## Overview

This document defines the PR approval workflow, governance gates, and review SLAs for all pull requests in the Aries-Serpent/_codex_ repository.

**Related Docs:**
- 📋 Full governance framework: `.codex/BATCH_2_GOVERNANCE_FRAMEWORK.md` (Part 3)
- ✅ Policy compliance checklist: `docs/production/POLICY_COMPLIANCE_CHECKLIST.md`

---

## Part 1: Gate Definitions & Requirements

### Gate 1: Code Review Gate (REQUIRED)

**Purpose:** Ensure code quality, maintainability, and adherence to project standards

**Trigger:** PR opened or marked "ready for review"

**Requirements:**

```yaml
Approval Count:
  - Minimum: 1 approval from code owners
  - Code owners: CODEOWNERS file (GitHub)
  - Exception: Owner (@mbaetiong) approval counts as 2
  
Comment Resolution:
  - All reviewer comments must be addressed
  - Resolve = dismiss comment + respond to feedback (or approve dismissal)
  - Comments can be dismissed if: deprecated, superseded, or invalid
  
Code Quality Criteria:
  - No obvious bugs or logic errors
  - Follows project style guide (linting passes)
  - Type safety (mypy/pylint pass)
  - No hardcoded values or magic numbers
  - Proper error handling
  - Documentation updated
```

**Enforcement:**

```yaml
Tool: GitHub branch protection rules
Status: ❌ HARD BLOCK (PR cannot merge)
Timeline: 24-48 hours expected
Escalation: Tech lead if stuck >72h
Manual Override: Owner approval required

Implementation:
  - Branch protection rule: require_code_review_approval_count ≥ 1
  - Require dismissal of stale reviews
  - Require up-to-date branches before merge
```

**Approval Evidence:**

```
What counts as valid approval:
  ✅ GitHub "Approve" review from code owner
  ✅ "Looks good to me" comment with approval emoji
  ✅ Code walk-through with documented sign-off
  
What does NOT count:
  ❌ Just opening the PR / commenting
  ❌ Approving without reviewing
  ❌ Approval from non-code-owner
```

---

### Gate 2: Security Scan Gate (REQUIRED)

**Purpose:** Prevent vulnerabilities, secrets, and security issues from reaching production

**Trigger:** PR created; re-triggered on every push

**Requirements:**

```yaml
CodeQL Analysis:
  - High/Critical issues: 0 (BLOCK)
  - Medium issues: 0 (WARN, reviewer discretion)
  - Low issues: 0 (WARN, auto-approve)
  
Secret Scanning:
  - Secrets detected: 0 (BLOCK)
  - False positives: Marked as such, auto-approved
  
Dependency Audit:
  - Critical vulnerabilities: 0 (BLOCK)
  - High vulnerabilities: 0 (BLOCK)
  - Medium/Low vulnerabilities: Reviewed by owner
  
License Compliance:
  - All dependencies use approved licenses: ✓
  - GPL/AGPL: Requires special approval
  - Unknown licenses: Escalated for review
```

**Enforcement:**

```yaml
Tools: 
  - CodeQL (GitHub Advanced Security)
  - Secret scanning (GitHub)
  - Dependabot audit (GitHub)
  - Semgrep + Bandit (custom workflows)
  
Status: ❌ HARD BLOCK (PR cannot merge)
Timeline: <15 minutes for scan completion
Override: Owner approval required via workflow dispatch
```

**High/Critical Finding Remediation:**

```yaml
If CodeQL reports HIGH/CRITICAL:
  1. Cannot merge until issue fixed or marked false positive
  2. Author must fix or owner must dismiss
  3. Dismissal requires documented reasoning
  4. Remediation evidence: commit message + code review comment
  
If Secret detected:
  1. Immediate PR block
  2. Secret must be removed and regenerated (if real)
  3. Audit log created of incident
  4. PR cannot proceed until secret removed
```

---

### Gate 3: Test Coverage Gate (REQUIRED)

**Purpose:** Ensure code reliability and prevent regression

**Trigger:** PR tests complete (after code review starts)

**Requirements:**

```yaml
Coverage Threshold:
  - Minimum: CODEX_COVERAGE_THRESHOLD (default 80%)
  - New code must maintain or improve coverage
  - No coverage regression on existing code
  
Test Pass Rate:
  - All tests must pass: 0 failures
  - No skipped critical tests
  - All edge cases covered
  
Test Categories (all must pass):
  - Unit tests: 100% pass rate
  - Integration tests: 100% pass rate
  - Smoke tests: 100% pass rate
  - Security tests: 100% pass rate (if modified)
```

**Enforcement:**

```yaml
Tool: pytest + coverage + pytest-cov
Execution: Automatic on PR push
Status: ❌ HARD BLOCK (PR cannot merge)
Timeline: <60 minutes (or CODEX_TEST_TIMEOUT_MINUTES)
Report: Posted as PR comment with detailed breakdown

Waiver Conditions (rare, requires owner approval):
  - Critical security hotfix (coverage waived to 70%)
  - Infrastructure-only changes (no tests needed)
  - Test failures in pre-existing code (if not introduced by PR)
```

**Coverage Report Format:**

```
Coverage Summary:
  Overall: 82.5% (target: 80%) ✅
  
  File Breakdown:
    src/auth.py:      95.2% ✅
    src/api.py:       78.9% ⚠️ (below threshold)
    src/utils.py:     88.3% ✅
  
  Change Summary:
    Lines added: 245
    Lines tested: 203 (82.9%)
    Lines untested: 42 (17.1%)
  
  Regression Check:
    Main branch coverage: 82.1%
    This PR coverage: 82.5%
    Change: +0.4% ✅
```

---

### Gate 4: Documentation Review Gate (CONDITIONAL)

**Purpose:** Keep documentation in sync with code changes

**Trigger:** If PR modifies: docs/, README.md, API files, configs

**Requirements:**

```yaml
User-Facing Features:
  - README.md updated with feature description
  - User guide updated (if applicable)
  - Examples added to documentation
  - Links updated in docs
  
API Changes:
  - CHANGELOG.md updated with change summary
  - API documentation updated
  - Breaking changes clearly marked
  - Migration guide provided (if breaking)
  
Configuration Changes:
  - Configuration documentation updated
  - Environment variable documentation updated
  - Examples updated (if applicable)
  
New Modules:
  - Module docstring added
  - README created in module directory
  - Functions have docstrings
  - Examples provided
```

**Enforcement:**

```yaml
Tool: doc-freshness-checker agent
Status: ⚠️ WARNING (can merge with acknowledged warning)
Timeline: 6-24 hours for review
Escalation: Owner approval if docs significantly outdated

Block Conditions (upgrade to HARD BLOCK):
  - User-facing change with NO documentation
  - API change with NO CHANGELOG entry
  - Breaking change not marked as such
```

---

### Gate 5: Policy Compliance Gate (REQUIRED)

**Purpose:** Enforce CODEBASE_AGENCY_POLICY.md compliance

**Trigger:** PR body updated or commits pushed

**Requirements:**

```yaml
Deferral Language Check:
  - No blocked phrases (see POLICY_COMPLIANCE_CHECKLIST.md)
  - Proper escalation language only
  - All issues addressed or properly documented
  
Merge Conflict Check:
  - PR mergeable without manual conflict resolution
  - Base branch up-to-date
  - No unresolved conflicts in file tree
  
Integration Branch Validation:
  - PR targets correct branch (0D_base_ or main)
  - Not targeting wrong branch (old feature branches)
  - Follows integration branch model
  
Pre-Existing Issue Documentation:
  - If not fixing pre-existing issue: documented as known issue
  - Evidence in commit messages
  - Links to follow-up issues
```

**Enforcement:**

```yaml
Tools:
  - deferral-language-gate.yml (CI workflow)
  - cognitive-preflight workflow (REQ-11)
  - policy-compliance-audit.py (script)
  
Status: ❌ HARD BLOCK (PR cannot merge)
Timeline: <2 minutes for check, 1-24 hours for remediation
Remediation: Specific fix requirements posted as PR comment
```

**Policy Violation Remediation Example:**

```
❌ POLICY COMPLIANCE GATE FAILED

Violation: Deferral language detected in PR body
- Found: "This is pre-existing"
- Line: PR description, second paragraph
- Status: Blocking merge

Required Action:
  1. Edit PR description
  2. Replace "This is pre-existing" with approved alternative
  3. Commit any code changes addressing the issue
  4. Push to trigger re-check
  
Approved Alternatives:
  ✅ "This issue exists in the codebase and is documented in #XYZ"
  ✅ "Escalated to @person in separate issue #XYZ"
```

---

## Part 2: Gate Sequence & Decision Matrix

### 2.1 Standard Gate Sequence (Feature/Bug Fix)

```
┌─────────────────────────────────────────────────────────────┐
│  PR Created → All 5 Gates Evaluated in Parallel              │
└─────────────────────────────────────────────────────────────┘

Gate 1: Code Review    [waiting for reviewer]
Gate 2: Security Scan  [running]
Gate 3: Test Coverage  [running]
Gate 4: Docs Check     [conditional - if applicable]
Gate 5: Policy         [running]

Timeline: Gates 2,3,5 complete in <2 minutes
          Code review completes in 24-48 hours
          Docs review completes in 6-24 hours (if needed)
```

### 2.2 Decision Matrix: All Gates Outcome

```yaml
Scenario 1: ALL GATES GREEN
  - Code review: ✅ Approved
  - Security: ✅ 0 high/critical issues
  - Test coverage: ✅ 82% (>80%)
  - Docs: ✅ Updated (or N/A)
  - Policy: ✅ Compliant
  
  RESULT: ✅ APPROVED FOR MERGE
  Action: Auto-post approval comment
  Timeline: Immediate
  Merge: Ready for owner/tech lead

Scenario 2: SECURITY GATE RED
  - Code review: ✅ Approved
  - Security: ❌ HIGH issue detected (SQL injection)
  - Test coverage: ✅ 82%
  - Docs: ✅ Updated
  - Policy: ✅ Compliant
  
  RESULT: ❌ BLOCKED FOR MERGE
  Action: Post remediation steps (fix SQL injection)
  Timeline: Author must fix, then re-check
  Merge: Cannot proceed until security issue fixed

Scenario 3: TEST COVERAGE RED
  - Code review: ✅ Approved
  - Security: ✅ 0 issues
  - Test coverage: ❌ 72% (<80%)
  - Docs: ✅ Updated
  - Policy: ✅ Compliant
  
  RESULT: ❌ BLOCKED FOR MERGE
  Action: Post coverage report with specific gaps
  Timeline: Author must add tests to reach 80%
  Merge: Cannot proceed until coverage meets threshold

Scenario 4: CODE REVIEW PENDING
  - Code review: ⏳ Pending (no approvals yet)
  - Security: ✅ 0 issues
  - Test coverage: ✅ 85%
  - Docs: ✅ Updated
  - Policy: ✅ Compliant
  
  RESULT: ⏳ WAITING FOR CODE REVIEW
  Action: Post request for reviewer
  Timeline: 24-48 hours expected
  Merge: Cannot proceed until code review approved

Scenario 5: POLICY VIOLATION
  - Code review: ✅ Approved
  - Security: ✅ 0 issues
  - Test coverage: ✅ 85%
  - Docs: ✅ Updated
  - Policy: ❌ Deferral language found
  
  RESULT: ❌ BLOCKED FOR MERGE
  Action: Post policy violation details + fix instructions
  Timeline: Author fixes deferral language in PR description
  Merge: Cannot proceed until policy compliant

Scenario 6: MULTIPLE GATES RED
  - Code review: ❌ 1 comment unresolved
  - Security: ❌ MEDIUM issue detected
  - Test coverage: ❌ 75% (<80%)
  - Docs: ⚠️ Update recommended
  - Policy: ✅ Compliant
  
  RESULT: ❌ BLOCKED FOR MERGE (critical issues)
           ⚠️ WARNINGS (non-blocking)
  Action: Post summary of all failures with priorities
  Timeline: Fix critical issues first (security, coverage)
  Merge: Cannot proceed
```

---

## Part 3: Review SLAs & Escalation

### 3.1 Standard Review Timeline

| Gate | Initial Review | Re-review | Override |
|------|---|---|---|
| Code Review | 24-48h | 4-8h | 4h escalation |
| Security Scan | <2 min | <2 min | 1h owner escalation |
| Test Coverage | <60 min | <60 min | 2h escalation |
| Docs Review | 6-24h | 2-4h | 8h escalation |
| Policy Check | <2 min | <2 min | Immediate owner escalation |

### 3.2 Escalation Paths

**Issue: Code review stuck for >48 hours**

```yaml
Timeline:
  Hour 24: Reviewer pinged via @mention
  Hour 36: Tech lead pinged (if no response)
  Hour 48: Issue escalated to owner (@mbaetiong)
  Hour 60: Owner force-approves or requests rebase

Escalation Chain:
  Original Reviewer → Tech Lead → Owner → Override
```

**Issue: Security gate blocked for >4 hours**

```yaml
Timeline:
  Hour 0: Issue posted by bot
  Hour 2: Security team pinged (if HIGH/CRITICAL)
  Hour 4: Owner pinged if not resolved
  Hour 6: Owner force-override (with incident documentation)

For False Positives:
  - Security team reviews and dismisses
  - If agreed false positive: Immediate approval
  - Audit entry created documenting dismissal
```

**Issue: Test coverage regression**

```yaml
Timeline:
  Min 0: Coverage report posted
  Hour 1: Author reviews gap report
  Hour 6: If not addressed, tech lead pings
  Hour 24: Tech lead may request override
  Hour 48: Owner can force-override (rare)

Override Conditions:
  - Coverage regression is minimal (<1%)
  - Regression is in test infrastructure (not core code)
  - Hotfix situation (critical production issue)
```

---

## Part 4: Approval Chain by File Type

### 4.1 Standard Files (Most Changes)

```yaml
Files:
  - src/codex_ml/**/*.py
  - src/apis/**
  - tests/**
  - docs/user-guides/**

Approval Chain:
  1. Code review: 1 code owner approval
  2. Security gate: Pass (0 HIGH/CRITICAL)
  3. Test coverage: >80%
  4. Policy: Compliant
  
Required Approvers: 1 code owner (from CODEOWNERS)
SLA: 48 hours code review, <2 min gates
```

### 4.2 Configuration & Infrastructure

```yaml
Files:
  - .github/workflows/**
  - pyproject.toml
  - requirements/**
  - configs/**
  - terraform/**
  - docker/**

Approval Chain:
  1. Code review: 1 tech lead approval
  2. Security gate: Pass
  3. Test coverage: >70% (infrastructure may have fewer tests)
  4. Policy: Compliant
  5. Owner approval: @mbaetiong (for major changes)
  
Special Handling:
  - Breaking changes in pyproject.toml: Owner + 1 tech lead
  - New GitHub Actions: Owner approval mandatory
  - Secret rotation: Owner approval mandatory
  - Infra changes: Tech lead + owner approval
  
Required Approvers: Tech lead minimum, owner for major
SLA: 48 hours, escalate to owner if tech lead unavailable
```

### 4.3 Security & Critical Files

```yaml
Files:
  - src/codex_ml/security/**
  - .github/security/**
  - src/codex_ml/auth/**
  - SECURITY.md
  - requirements-lock.txt (with new deps)

Approval Chain:
  1. Code review: Security lead + code owner
  2. Security gate: Pass (0 issues, even LOW)
  3. Test coverage: >85% (strict)
  4. Threat modeling: Reviewed (if applicable)
  5. Owner approval: @mbaetiong (mandatory)
  6. Policy: Compliant
  
Required Approvers: Security lead + owner (@mbaetiong)
SLA: 24 hours (expedited), escalate immediately if delayed
```

### 4.4 Documentation & User-Facing

```yaml
Files:
  - README.md
  - CONTRIBUTING.md
  - docs/
  - CHANGELOG.md
  - API documentation

Approval Chain:
  1. Content review: Tech lead or documentation team
  2. Policy: Compliant (links working, etc.)
  3. Link validation: Automated check
  
Special Handling:
  - User-facing feature descriptions: Product lead review
  - API changes: API maintainer approval
  - Breaking changes: Owner notification
  
Required Approvers: 1 tech lead (or doc team)
SLA: 24 hours, relaxed timeline OK
```

---

## Part 5: PR Status Dashboard & Monitoring

### 5.1 Merge Readiness Indicator

**PR Comment Posted by Bot:**

```
╔════════════════════════════════════════════════════════════╗
║                   MERGE READINESS CHECK                     ║
╚════════════════════════════════════════════════════════════╝

  Code Review:        ✅ Approved (1/1)
  Security Scan:      ✅ 0 HIGH/CRITICAL issues
  Test Coverage:      ✅ 82% (target: 80%)
  Documentation:      ✅ Updated
  Policy Compliance:  ✅ Deferral language check passed
  Merge Conflicts:    ✅ None
  
STATUS: ✅ APPROVED FOR MERGE
Approved by: @reviewer1 (@code-owner)
Ready to merge after: 2026-02-22 15:30 UTC

Actions available:
  [MERGE] (owner only)
  [REQUEST CHANGES] (reviewer only)
```

### 5.2 Failure Notification

**PR Comment Posted by Bot:**

```
╔════════════════════════════════════════════════════════════╗
║                   MERGE BLOCKED - ISSUES FOUND              ║
╚════════════════════════════════════════════════════════════╝

❌ Code Review
  - 1 unresolved comment from @reviewer1
  - Action: Resolve comment or approve dismissal
  
❌ Test Coverage
  - Coverage: 72% (target: 80%)
  - Gap: 8% (245 lines, 42 untested)
  - Files below threshold:
    • src/api.py: 78.9% (need +1.1%)
  - Action: Add tests for untested lines
  
⚠️ Documentation
  - API documentation not updated
  - Note: Not blocking merge, but recommended
  - Action: Update API docs when convenient

🔧 Next Steps:
  1. Resolve the code review comment
  2. Add tests to reach 80% coverage
  3. Recommend: Update API documentation
  4. Push changes to retrigger gates
```

---

## Summary & Quick Reference

**Gate Checklist for Authors:**

```
Before requesting review:
  ☐ All tests passing locally
  ☐ Coverage ≥80%
  ☐ Linters passing (pylint, flake8, mypy)
  ☐ No hardcoded secrets
  ☐ Documentation updated
  ☐ Commit messages follow conventions
  ☐ PR description includes what/why/testing evidence
  ☐ No deferral language in PR body

During review:
  ☐ Respond to all reviewer comments promptly
  ☐ Push updates to retrigger gate checks
  ☐ Wait for all gates to turn green

After gates pass:
  ☐ Ensure code review approved
  ☐ Ready for owner/tech lead to merge
  ☐ Monitor post-merge CI (if applicable)
```

**Reviewer Checklist:**

```
Code Review Gates:
  ☐ Code follows project style guide
  ☐ Logic is correct and maintainable
  ☐ Error handling is comprehensive
  ☐ Tests cover the changes
  ☐ Documentation is updated
  ☐ No obvious security issues
  ☐ Performance impact acceptable
  ☐ Comments are resolved or dismissed

Final Approval:
  ☐ All code review criteria met
  ☐ All gates passing (security, tests, docs, policy)
  ☐ Merge conflicts resolved
  ☐ Ready for production
```

✅ **PR APPROVAL WORKFLOW: COMPLETE & OPERATIONAL**

