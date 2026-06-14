# Phase 6 Batch 2 — Policy Compliance Checklist for Contributors

**Version:** 1.0.0  
**Status:** FINAL  
**Audience:** All contributors (human & AI)  
**Last Updated:** 2026-02-22

---

## Overview

This checklist must be completed BEFORE submitting a pull request. It enforces the **CODEBASE_AGENCY_POLICY.md (v1.1.0)** and ensures compliance with all governance gates.

**Policy Reference:**
- 📋 Full policy: `.codex/CODEBASE_AGENCY_POLICY.md`
- 🛡️ Governance framework: `.codex/BATCH_2_GOVERNANCE_FRAMEWORK.md`

---

## Pre-Session Review (REQ-0) — REQUIRED BEFORE MAKING ANY CHANGES

This must be completed within the first 5 minutes of your session. Skipping this results in automatic PR rejection.

### Step 1: Review All Bot Comments ✓

**Action:** Go to the PR and read every comment from:
- ✅ `copilot-pull-request-reviewer[bot]` — Code review feedback
- ✅ `github-advanced-security[bot]` — Security alerts (CodeQL, secret scanning)
- ✅ `github-actions[bot]` — CI/CD status and gate failures
- ✅ **@mbaetiong** — Maintainer comments (BLOCKING — must reply to each one)

**Evidence Required:**
```
☐ Visited PR comments section
☐ Noted all bot comments
☐ Read and understood each @mbaetiong comment
☐ Replied to ALL @mbaetiong comments (even if just "acknowledged")
```

**Failure Mode:** PR auto-blocks if @mbaetiong comments remain unaddressed. See `comment-review-gate.yml` REQ-13.

---

### Step 2: Review Failing CI Checks ✓

**Action:** Fetch all failing workflows and identify each failure:

```bash
# Get latest workflow runs
gh run list --repo Aries-Serpent/_codex_ --limit 10 --json number,displayTitle,status,conclusion

# Get details on failures
gh run view <RUN_ID> --log | grep -A 5 "FAILED"
```

**For Each Failure, Identify:**
- ☐ Is it code-fixable? (Yes → FIX IT NOW; No → DOCUMENT IT)
- ☐ Root cause (import error, test failure, lint error, etc.)
- ☐ Which file/line caused it
- ☐ Whether it's pre-existing or new

**Evidence Required:**
```
☐ List of all failing checks identified
☐ Root cause documented for each failure
☐ Fixed all code-fixable failures
☐ Documented (but not fixed) infrastructure-only failures
```

---

### Step 3: Load Required Documents ✓

**Action:** Read the following files IN FULL (document mentions, not just skimming):

```bash
cat .codex/CODEBASE_AGENCY_POLICY.md
cat docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
cat .codex/CRITICAL_REPOSITORY_VARIABLES.md
cat .codex/BATCH_2_GOVERNANCE_FRAMEWORK.md
```

**Evidence Required:**
```
☐ CODEBASE_AGENCY_POLICY.md (Sections §0-§3a minimum)
☐ CRITICAL_REPOSITORY_VARIABLES.md (variable categories)
☐ BATCH_2_GOVERNANCE_FRAMEWORK.md (governance pillars)
☐ Loaded stored session memories
```

---

### Step 4: Check Merge Conflicts ✓

**Action:** Verify PR is mergeable without conflicts:

```bash
# Check if mergeable
gh pr view <PR_NUMBER> --json mergeable

# If mergeable: false, rebase and push
git fetch origin
git rebase origin/0D_base_
git push --force-with-lease
```

**Evidence Required:**
```
☐ PR merge status checked at session START
☐ Merge conflicts resolved (if present)
☐ Rebased on latest base branch
☐ Force-push completed (if needed)
☐ PR merge status verified at session END
```

---

## Work Execution Checklist

### Phase A: Deferral Language Policy Compliance ✓

**MANDATORY: The following phrases are FORBIDDEN in your PR body, commit messages, and comments:**

```
BLOCKED PHRASES (hard block — PR will not merge):
  ❌ "This is pre-existing" / "Pre-existing issue"
  ❌ "Out of scope" / "Not related to my PR"
  ❌ "Not my responsibility"
  ❌ "This is a future PR" / "Defer to next PR"
  ❌ "I won't fix this" / "Not fixing this"
```

**ALLOWED ALTERNATIVES (use these instead):**

```
✅ INSTEAD OF "This is pre-existing": 
   "This issue exists in the codebase and is not related to my changes. 
    It is documented in issue #XYZ and should be addressed in a separate PR."

✅ INSTEAD OF "Out of scope":
   "This falls outside the scope of this PR (which addresses X). 
    I've created issue #XYZ to track it separately."

✅ INSTEAD OF "Not my responsibility":
   "This requires changes outside my domain of expertise. 
    I've escalated to @person-X in issue #XYZ."
```

**Enforcement:**
```
CI GATE: deferral-language-gate.yml
STATUS: ❌ HARD BLOCK (PR will not merge)
OVERRIDE: Owner approval required (@mbaetiong)
```

**Evidence Required:**
```
☐ Searched PR body for blocked phrases
☐ Searched commit messages for blocked phrases
☐ Searched comments for blocked phrases
☐ Used allowed alternatives where necessary
☐ No instances of blocked language detected
```

---

### Phase B: Comprehensive Issue Resolution ✓

**MANDATE: You must fix ALL encountered issues, not just your assigned work.**

**What counts as an "issue"?**
- ❌ Test failure in any module
- ❌ Linting error (`pylint`, `flake8`, `mypy`)
- ❌ Type checking error
- ❌ Documentation broken link
- ❌ Security vulnerability
- ❌ Coverage regression

**Evidence Required:**

```bash
# Find all test failures
pytest --tb=short 2>&1 | grep FAILED

# Fix each failure and document in commit
git commit -m "Fix failing test: module.test_function (related to PR work)"

# Verify all tests passing
pytest --tb=short 2>&1 | grep -c FAILED  # Should be 0
```

**Commit Message Format for Issue Fixes:**

```
Format: "Fix [CATEGORY]: [Description] ([related-to-main-work])"

Examples:
  ✅ "Fix test failure: test_auth_invalid_token (ensures PR doesn't break auth)"  # pragma: allowlist secret
  ✅ "Fix linting error: unused import in utils.py (cleanup before PR merge)"
  ✅ "Fix broken doc link: CONTRIBUTING.md → guides/setup.md (improves contributor experience)"
  ✅ "Fix security issue: SQL injection in query builder (critical vulnerability)"
```

**Evidence Required:**
```
☐ Ran full test suite: pytest
☐ Ran linters: pylint, flake8, mypy
☐ Checked for security issues: bandit, semgrep
☐ Verified documentation links: linkchecker docs/
☐ Fixed ALL encountered issues
☐ Committed fixes with proper commit messages
☐ Verified CI is now green
```

---

### Phase C: Code Quality & Improvement ✓

**MANDATE: Leave codebase better than you found it.**

**What counts as "improvement"?**
- ✅ Add type hints to untyped functions
- ✅ Refactor duplicated code
- ✅ Improve variable names (clarity)
- ✅ Add docstrings to undocumented functions
- ✅ Increase test coverage
- ✅ Optimize performance bottlenecks

**Evidence Required:**
```
☐ Identified at least 1 code quality opportunity
☐ Implemented improvement (type hints, refactor, docstring, etc.)
☐ Improvement doesn't break existing functionality
☐ Tests passing after improvement
☐ Commit message explains improvement rationale
☐ PR comment documents "Improvements Made" section
```

**Commit Message Format:**

```
Format: "Improve [CATEGORY]: [Description]"

Examples:
  ✅ "Improve typing: Add type hints to auth module functions"
  ✅ "Improve docs: Add docstring to parse_config function"
  ✅ "Improve test coverage: Add edge case tests for token validation"  # pragma: allowlist secret
  ✅ "Improve performance: Cache config parsing results (fixes N+1 query)"
```

---

### Phase D: Documentation Updates ✓

**REQUIRED Documentation Updates (by change type):**

| Change Type | Documentation Required | Status |
|-----------|------------------------|--------|
| User-facing feature | Update README.md + docs/ | ☐ |
| API change | Update CHANGELOG.md + API docs | ☐ |
| Configuration option | Update configuration guide | ☐ |
| New module | Add module docstring + README | ☐ |
| Bug fix | Update CHANGELOG.md | ☐ |
| Internal refactor | Update code comments | ☐ |

**CHANGELOG.md Format:**

```markdown
# Changelog — [Version]

## [New/Fixed/Changed] — YYYY-MM-DD

### Added
- [Feature description] (#PR_NUMBER)

### Fixed
- [Bug fix description] (#PR_NUMBER)

### Changed
- [API change description] (#PR_NUMBER)

### Deprecated
- [Deprecation notice] (#PR_NUMBER)
```

**Evidence Required:**
```
☐ README.md updated (if user-facing)
☐ CHANGELOG.md updated
☐ API documentation updated (if applicable)
☐ Configuration guide updated (if applicable)
☐ Code comments added/clarified
☐ Docstrings added (if new functions)
```

---

### Phase E: Security & Privacy Review ✓

**MANDATORY Checks:**

```yaml
Code Security:
  ☐ No hardcoded secrets (API keys, tokens, credentials)
  ☐ No unvalidated user input
  ☐ No SQL injection vulnerabilities
  ☐ No XXE vulnerabilities in XML parsing
  ☐ Proper input validation throughout
  
Privacy:
  ☐ No PII (personally identifiable information) logged
  ☐ No sensitive data in error messages
  ☐ Proper access control checks
  ☐ No unauthorized data exposure
  
Dependencies:
  ☐ No new dependencies with known vulnerabilities
  ☐ Dependencies use approved licenses
  ☐ Pinned versions in lock file
```

**Tool Checks:**

```bash
# Secret scanning
python scripts/ci/secret_detection.py

# Dependency audit
pip audit

# Linting & security
bandit -r src/
semgrep --config p/security-audit --error
```

---

## Post-Session Validation

### Final Checklist (Before Requesting Review)

```yaml
Pre-Submission Verification:
  ☐ All 4 pre-session review steps completed (REQ-0)
  ☐ No deferral language in PR body / commits / comments
  ☐ All encountered issues fixed
  ☐ At least 1 code quality improvement made
  ☐ Documentation updated (if needed)
  ☐ Security checks passed
  ☐ Merge conflicts resolved
  ☐ All tests passing (pytest, linters, security checks)
  
PR Description Quality:
  ☐ Clear summary of changes
  ☐ Links to related issues/PRs
  ☐ Lists all fixes made (beyond main scope)
  ☐ Lists improvements made
  ☐ Includes testing evidence (test coverage change)
  ☐ References relevant documentation
  
Final CI Status:
  ☐ All GitHub Actions passing (green checkmarks)
  ☐ Code review gate passing
  ☐ Security gate passing
  ☐ Test coverage gate passing
  ☐ Policy compliance gate passing
```

---

## Enforcement & Consequences

### CI/CD Gates (Automatic Enforcement)

| Gate | Trigger | Enforcement | Override |
|------|---------|------------|----------|
| Deferral Language | PR body/commits | ❌ HARD BLOCK | Owner approval |
| Pre-Session Review | Bot comments unaddressed | ❌ HARD BLOCK | N/A |
| Test Coverage | Coverage < 80% | ❌ HARD BLOCK | N/A |
| Security Scan | High/critical issues | ❌ HARD BLOCK | Owner approval |
| Policy Compliance | Gate failures | ❌ HARD BLOCK | Owner approval |

### Accountability Tracking

**All violations logged and tracked:**
```
Violation Log: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md

Tracked Metrics:
  - Deferral language violations per session
  - Pre-session review completion rate
  - Issue resolution quality
  - Policy compliance rate
  - Override requests (frequency & justification)
```

---

## Quick Reference

### Command Cheatsheet

```bash
# Pre-session review automation
python scripts/ci/pre_session_review.py --pr <PR_NUMBER>

# Compliance check
python scripts/ci/policy_compliance_audit.py --pr <PR_NUMBER>

# Run full validation
pytest && pylint src/ && bandit -r src/ && semgrep --config p/security-audit

# Generate accountability report
python scripts/ci/generate_accountability_report.py --session-id $SESSION_ID
```

### Escalation Contacts

| Category | Escalation |
|----------|-----------|
| Policy Questions | @mbaetiong |
| Security Issues | Security team (#security) |
| Test Failures | Tech lead |
| Documentation | Documentation team |
| Infrastructure | Ops team |

---

**STATUS: ✅ POLICY COMPLIANCE CHECKLIST COMPLETE AND OPERATIONAL**

All governance requirements from CODEBASE_AGENCY_POLICY.md (v1.1.0) are now enforceable via this checklist and CI/CD gates.

