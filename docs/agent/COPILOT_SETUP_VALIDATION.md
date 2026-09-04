# Copilot Setup Steps Validation Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

Complete documentation for the pre-merge testing infrastructure for `.github/workflows/copilot-setup-steps.yml`.

## Table of Contents

1. [Overview](#overview)
2. [Test Categories](#test-categories)
3. [Running Tests Locally](#running-tests-locally)
4. [CI/CD Integration](#cicd-integration)
5. [Understanding Results](#understanding-results)
6. [Troubleshooting](#troubleshooting)
7. [Merge Gates](#merge-gates)

## Overview

The copilot-setup-steps.yml validation system ensures the critical GitHub Actions workflow that customizes the Copilot agent environment remains stable, secure, and functional. The system implements 12 test categories across 6 phases:

| Phase | Category | Tests | Risk Level |
|-------|----------|-------|-----------|
| 1 | YAML Validation | 2 | CRITICAL |
| 2 | Critical Variables | 1 | CRITICAL |
| 3 | Session Preload | 2 | CRITICAL |
| 4 | Integration | 2 | HIGH |
| 5 | Security | 3 | HIGH |
| 6 | Regression | 3 | MEDIUM |

## Test Categories

### Phase 1: YAML Validation (Section 1.1)

**Purpose:** Ensure the workflow file is syntactically valid YAML.

**Tests:**
- YAML syntax parse (Python yaml.safe_load)
- Proper indentation (2-space standard)

**Run individually:**
```bash
python scripts/ci/validate_copilot_setup_steps.py | grep "YAML"
```

**Failure actions:** BLOCKS MERGE

---

### Phase 2: Critical CCA Variables (Section 1.2 & 3.1-3.3)

**Purpose:** Verify all 3 variables required for multi-turn agentic loops are present with correct values.

**Critical variables:**
- `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`
- `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`
- `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`

**Why they matter:**
- **Version lock** prevents auto-upgrades that could introduce duplicate function call ID errors
- **Deduplication** enables the payload deduplicator that removes duplicate function calls
- **Turn isolation** ensures state is segregated between agentic turns

**Failure message example:**
```
 Critical CCA Variables: Missing required variables: COPILOT_AGENT_CCA_VERSION_LOCK
```

**Recovery:** These variables are in the workflow template at lines 99-101. Ensure they weren't accidentally removed during edits.

**Failure actions:** BLOCKS MERGE (severity: CRITICAL)

---

### Phase 3: Session Preload & Git Diff Protection (Section 1.3 & 4.1)

**Purpose:** Protect critical sections of the workflow from being accidentally broken.

**Tests:**
- Session preload uses block scalar syntax (`run: |`)
- Protected sections not removed (lines 99-101, 132-137)

**Protected sections:**
- Lines 99-101: CCA variables definitions
- Lines 132-137: Session Context Pre-load step

**Critical syntax requirement:**

```yaml
#  CORRECT (block scalar)
- name: " Session Context Pre-load"
  run: |
    if ! python3 .github/scripts/session_preload.py; then
      echo "warning"
    fi

#  WRONG (flow scalar) — CAUSES PARSE FAILURE
- name: " Session Context Pre-load"
  run: 'if ! python3 .github/scripts/session_preload.py; then echo "warning"; fi'
```

**Why:** yamllint 1.38.0 crashes on flow scalar brace syntax. The pipe operator allows shell conditionals to parse correctly.

**Failure actions:** BLOCKS MERGE (severity: CRITICAL)

---

## Phase 4: Integration Testing (Section 2.1-2.3)

**Purpose:** Verify dependent workflows and scripts are accessible and valid.

**Dependent workflows (must exist and be valid YAML):**
1. `.github/workflows/copilot-setup-validation.yml`
2. `.github/workflows/deferral-language-gate.yml`
3. `.github/workflows/workflow-execution-gate.yml`
4. `.github/workflows/validate.yml`

> Historical duplicates such as `wec-enforcement-gate.yml` and `workflow-compliance-gate.yml` are archived under `.github/workflow-archive/disabled/`; the active canonical gate is `workflow-execution-gate.yml`.

**Supporting scripts (must exist and have valid Python syntax):**
1. `.github/scripts/session_preload.py`
2. `scripts/ci/session_access_probe.py`
3. `scripts/ci/autonomous_rag_context.py`

**Environment variables (must be defined):**
- PYTHON_VERSION, NODE_VERSION, RUST_VERSION
- GIT_LFS_SKIP_SMUDGE
- CODEX_MASTER_KEY, CODEX_BACKUP_KEY
- COPILOT_* (CCA variables)

**Failure actions:** BLOCKS MERGE (severity: CRITICAL)

---

### Phase 5: Security & Secrets Testing (Section 5.1-5.3)

**Purpose:** Prevent security issues like hardcoded secrets and invalid token references.

**Tests:**
- Hardcoded secrets scan (pattern matching for token formats)
- Token reference validation (GITHUB_TOKEN, CODEX_MASTER_KEY, CODEX_BACKUP_KEY)
- YAML injection prevention (special character escaping)

**What triggers failures:**
- Hardcoded GitHub tokens (ghp_, ghu_, ghs_, ghe_ patterns)
- Hardcoded AWS access keys (AKIA pattern)
- Unquoted YAML values with special characters
- Missing required token references

**Failure actions:** BLOCKS MERGE (severity: CRITICAL)

---

### Phase 6: Regression Testing (Section 6.1-6.3)

**Purpose:** Detect unexpected file size growth, complexity increases, or configuration drift.

**Tests:**
- File size regression (baseline: 673 lines, tolerance: ±5%)
- Complexity analysis (job/step count)
- LFS configuration (verify not corrupted)

**Thresholds:**
- Warning: 750+ lines (might indicate bloat)
- Failure: 1000+ lines (too large, merge blocked)
- Acceptable: 640-700 lines (±5% tolerance)

**Complexity baseline:**
- 2 jobs (expected)
- 27 steps (expected)
- Warning if >30 steps (might indicate bloat)
- Failure if >50 steps (too complex)

**Failure actions:** BLOCKS MERGE if >1000 lines; WARNING if >750 lines

---

## Running Tests Locally

### Prerequisites

```bash
# Install Python 3.12+
python3 --version

# Install dependencies
pip install pyyaml yamllint
```

## Run All Validation Suites

```bash
# Run all three validation scripts
python scripts/ci/validate_copilot_setup_steps.py --repo-root .
python scripts/ci/validate_copilot_dependencies.py --repo-root .
python scripts/ci/validate_copilot_security.py --repo-root .
```

## Run Individual Validation Suites

```bash
# Core validation only
python scripts/ci/validate_copilot_setup_steps.py

# Integration tests only
python scripts/ci/validate_copilot_dependencies.py

# Security tests only
python scripts/ci/validate_copilot_security.py

# Legacy shell validation
bash scripts/ci/validate_setup_steps_yaml.sh
```

## Run Specific Tests Only

Each validation script supports filtering (add to scripts if needed):

```bash
# Check if file passes without detailed output
python scripts/ci/validate_copilot_setup_steps.py --check-only

# Output results as JSON
python scripts/ci/validate_copilot_setup_steps.py --json-output results.json
```

## Before Committing

```bash
# Quick smoke test
bash scripts/ci/validate_setup_steps_yaml.sh

# Full validation suite
python scripts/ci/validate_copilot_setup_steps.py && \
python scripts/ci/validate_copilot_dependencies.py && \
python scripts/ci/validate_copilot_security.py && \
echo " All validation tests passed!"
```

## CI/CD Integration

### Workflow File

The validation workflow is defined in:
```
.github/workflows/copilot-setup-validation.yml
```

### Triggers

The workflow runs automatically when:
- Pull request opened, updated, or ready for review
- Push to main branch (if file changed)
- Manual workflow dispatch

### Checks

The workflow creates 4 automated checks:
1. **Core Validation** — YAML syntax, CCA variables, session preload
2. **Integration Tests** — Dependent workflows, supporting scripts, env vars
3. **Security Tests** — Secrets, token references, injection prevention
4. **Legacy Shell Validation** — Backward compatibility with shell script

### PR Comment

After all tests complete, the workflow posts a summary comment on the PR:

```markdown
##  Copilot Setup Steps Validation

### Test Results
| Phase | Status | Result |
|-------|--------|--------|
| Core Validation |  | 9/9 passed |
| Integration |  | 4/4 passed |
| Security |  | 3/3 passed |

### Summary
**Total: 16/16 tests passed**

 **All validation tests passed!**

### Merge Gates
-  All automated tests pass
-  All 3 CCA variables present (validated by tests)
-  All 5 dependent workflows validate (validated by tests)
-  Security/secrets tests pass
-  File size within acceptable range (validated by tests)
-  At least 1 human reviewer approval
```

## Understanding Results

### Success (Exit Code 0)

All tests passed. Example output:

```
========================================================================================
Test Suite: Copilot Setup Steps Validation
========================================================================================
   YAML Syntax Parse: Valid YAML structure (no parse errors)
   YAML Indentation: Proper 2-space indentation throughout
   Critical CCA Variables: All 3 CCA variables present and correct
   Session Preload Block Scalar: Uses correct block scalar syntax (run: |)
   Git Diff Protection: Protected sections verified (CCA variables, session preload)
   Dependent Workflows (2.1): All 5 dependent workflows valid
   Supporting Scripts (2.2): All 3 supporting scripts valid
   Environment Variables (2.3): All 10 critical environment variables properly defined
   Hardcoded Secrets Scan (5.1): No obvious hardcoded secrets detected in workflow  # pragma: allowlist secret
   Token Reference Validation (5.2): All token references properly use GitHub secrets  # pragma: allowlist secret
   YAML Injection Prevention (5.3): YAML injection prevention check passed
   File Size Regression: 673 lines (+0.0% from baseline 673)
   Complexity Analysis: 2 jobs, 27 steps (within acceptable bounds)
   LFS Configuration: LFS configuration correct (GIT_LFS_SKIP_SMUDGE=1)

Summary: 14/14 passed

 All validation tests passed!
```

### Failure (Exit Code 1)

Critical tests failed. Example output:

```
========================================================================================
Test Suite: Copilot Setup Steps Validation
========================================================================================
   Critical CCA Variables: Missing required variables: COPILOT_AGENT_CCA_VERSION_LOCK
   Session Preload Block Scalar: Uses correct block scalar syntax (run: |)
  ...

Summary: 13/14 passed

 1 CRITICAL FAILURE(S) — MERGE BLOCKED
   - Critical CCA Variables: Missing required variables: COPILOT_AGENT_CCA_VERSION_LOCK
```

### Warning (Exit Code 2)

Non-critical tests failed. Example output:

```
 1 WARNING(S) — Review recommended
   - File Size Regression: File larger than warning threshold: 825 lines
```

## Troubleshooting

### Problem: "YAML parse error"

**Cause:** The workflow file has invalid YAML structure.

**Fix:**
1. Check for unmatched quotes or braces
2. Verify indentation is consistent (2 spaces)
3. Look for orphaned keys (`:` without value)
4. Run locally: `python -m yaml < .github/workflows/copilot-setup-steps.yml`

### Problem: "Session preload is NOT using block scalar"

**Cause:** The `run: |` syntax was changed to flow scalar or removed.

**Fix:**
```bash
# Restore from canonical baseline
git show 12f7a861:.github/workflows/copilot-setup-steps.yml > .github/workflows/copilot-setup-steps.yml
```

## Problem: "Missing required variables: COPILOT_AGENT_CCA_VERSION_LOCK"

**Cause:** CCA variables at lines 99-101 were deleted or commented out.

**Fix:**
1. Restore lines 99-101 from canonical baseline (commit 12f7a861)
2. Verify values: `"stable"`, `"true"`, `"true"`
3. Confirm indentation (must be under `env:` section)

### Problem: "Dependent workflow not found"

**Cause:** A required workflow file doesn't exist or path is wrong.

**Fix:**
1. Check the path is correct: `ls -la .github/workflows/`
2. Verify the file name matches exactly (case-sensitive)
3. If newly added, commit the dependency first

### Problem: "Supporting script has syntax error"

**Cause:** One of the three required scripts has invalid Python syntax.

**Fix:**
1. Identify which script: check the error message
2. Run syntax check: `python3 -m py_compile <script>`
3. Fix syntax errors in the script
4. Re-run validation

### Problem: "File too large: 1200 lines"

**Cause:** The workflow file grew beyond the acceptable threshold (1000 lines).

**Fix:**
1. Review recent changes for unnecessary additions
2. Check for duplicated steps or redundant sections
3. Split into multiple workflows if adding substantial functionality
4. Justify large changes in commit message

### Problem: "Hardcoded secrets detected"

**Cause:** Secret tokens or API keys are visible in the workflow.

**Fix:**
1. Identify the line with the secret
2. Replace with proper GitHub secret reference: `${{ secrets.SECRET_NAME }}`
3. Remove any exposed credentials from git history
4. Rotate the exposed secret

### Getting Help

If tests fail and you're unsure how to fix:

1. Check the error message and corresponding section above
2. Review the canonical baseline: `git show 12f7a861:.github/workflows/copilot-setup-steps.yml`
3. Compare your changes with the baseline
4. If still stuck, open an issue or contact @mbaetiong

## Merge Gates

The PR can only be merged when ALL of the following are true:

### Automated Requirements
- [ ] **All 6 CI job test suites pass** (0 failures)
- [ ] **All 3 CCA variables present & correct** (validated)
- [ ] **All 5 dependent workflows validate** (exist and valid YAML)
- [ ] **All 3 supporting scripts accessible** (exist and valid Python)
- [ ] **Security/secrets tests pass** (0 security issues)
- [ ] **File size within range** (<1000 lines, <750 warning)

### Human Requirements
- [ ] **At least 1 human code review** (using COPILOT_SETUP_REVIEW_CHECKLIST.md)
- [ ] **Reviewer approves the diff**
- [ ] **All commit messages are clear**

### Optional but Recommended ⭐
- [ ] Pre-merge workflow execution test passes
- [ ] Multi-turn session smoke test passes
- [ ] All documentation updated

### Blocking Conditions
- Any automated test fails
- CCA variables removed or incorrect
- Session preload converted to flow-scalar
- Hardcoded secrets detected
- File size >1000 lines
- Dependent workflows broken
- No human review

---

## Related Documents

- **Review Checklist**: [.github/COPILOT_SETUP_REVIEW_CHECKLIST.md](../../.github/COPILOT_SETUP_REVIEW_CHECKLIST.md)
- **Guard Documentation**: [docs/agent/COPILOT_SETUP_STEPS_GUARD.md](COPILOT_SETUP_STEPS_GUARD.md)
- **Validation Workflow**: [.github/workflows/copilot-setup-validation.yml](../../.github/workflows/copilot-setup-validation.yml)
- **CCA Integration**: [CODEBASE_AGENCY_POLICY.md](../.codex/CODEBASE_AGENCY_POLICY.md)

## Questions?

See the complete pre-merge testing plan or contact @mbaetiong.
