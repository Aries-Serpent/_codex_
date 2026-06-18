# Copilot Setup Steps Code Review Checklist

Use this checklist when reviewing changes to `.github/workflows/copilot-setup-steps.yml`.

## 7.1 Code Review Requirements

- [ ] **CCA Variables Present**: Reviewer confirms all 3 critical CCA variables are present:
  - [ ] `COPILOT_AGENT_CCA_VERSION_LOCK: "stable"`
  - [ ] `COPILOT_AGENT_DEDUPLICATION_ENABLED: "true"`
  - [ ] `COPILOT_AGENT_TURN_ISOLATION_ENABLED: "true"`

- [ ] **Session Preload Intact**: Reviewer verifies session preload step (lines ~132-137):
  - [ ] Uses block scalar syntax (`run: |`)
  - [ ] Contains `continue-on-error: true`
  - [ ] Shell syntax is correct (if ! ... ; then ... fi)
  - [ ] Not converted to flow-scalar format (|| { })

- [ ] **No Unintended Changes**: Reviewer checks git diff for:
  - [ ] Protected sections not accidentally removed
  - [ ] No conversion of `run: |` to flow scalar
  - [ ] No hardcoded secrets introduced
  - [ ] No orphaned or missing keys

- [ ] **Diff Summary Approved**: Reviewer signs off on:
  - [ ] Changes address the original problem
  - [ ] Changes are minimal and surgical
  - [ ] All changes are intentional

## 7.2 Functional Review

- [ ] **Addresses Original Problem**: Changes solve the stated problem (e.g., broken workflow):
  - [ ] Reproducer scenario works
  - [ ] Error no longer occurs
  - [ ] Multi-turn agent capability preserved

- [ ] **No New Issues Introduced**:
  - [ ] No YAML syntax errors
  - [ ] No missing step definitions
  - [ ] All environment variables accessible
  - [ ] No circular dependencies

- [ ] **Multi-Turn Agent Support Maintained**:
  - [ ] Session preload step runs without blocking
  - [ ] CCA variables enable deduplication layer
  - [ ] Turn-state isolation is configured
  - [ ] Environment propagation works correctly

- [ ] **Error Handling Preserved**:
  - [ ] Non-blocking steps use `continue-on-error: true`
  - [ ] Failures don't prevent agent startup
  - [ ] Error messages are helpful
  - [ ] Fallback behavior is defined

## 7.3 Documentation Review

- [ ] **Commit Message Updated**:
  - [ ] Clear summary of changes
  - [ ] References related issues/PRs
  - [ ] Explains why changes were made
  - [ ] Follows conventional commit format

- [ ] **CHANGELOG.md Updated** (if applicable):
  - [ ] Entry describes the fix
  - [ ] Categorized correctly (Fix/Feature/Breaking)
  - [ ] Added to "Unreleased" section

- [ ] **Comments Explain Why** (for non-obvious changes):
  - [ ] Complex logic has explanatory comments
  - [ ] Any workarounds are documented
  - [ ] References to related docs or issues included

- [ ] **Related Documentation Updated**:
  - [ ] `.github/COPILOT_SETUP_STEPS_GUARD.md` updated if needed
  - [ ] `docs/agent/COPILOT_SETUP_VALIDATION.md` reflects changes
  - [ ] Any dependent workflow docs updated

## Additional Review Items

### For Changes to Critical Sections (lines 99-101, 132-137):

- [ ] Canonical baseline understood (commit 12f7a861 / blob 8c84a8c1)
- [ ] Changes tested locally first
- [ ] All validation scripts pass
- [ ] Backward compatibility maintained
- [ ] No format changes to block scalars

### For Changes to Session Preload:

- [ ] ⚠️ **CRITICAL**: Block scalar syntax (`run: |`) NOT changed to flow scalar
- [ ] Shell conditionals use brace-free format: `if ! ...; then ...; fi`
- [ ] No YAML parsing errors with yamllint
- [ ] Session preload is non-blocking (`continue-on-error: true`)

### For New Steps Added:

- [ ] Step is necessary and solves stated problem
- [ ] Step doesn't duplicate existing functionality
- [ ] Step is placed in correct phase (1-5)
- [ ] Step has appropriate `continue-on-error` setting
- [ ] Documentation explains why step is needed

## Review Decision

**After completing all checks above, select one:**

- ✅ **APPROVE** - All checks passed, ready for merge
- 🔄 **REQUEST CHANGES** - Found issues that must be fixed
- ⏸️ **COMMENT** - Minor suggestions, doesn't block merge

### Sign-Off

Reviewer: _________________

Date: _________________

Commit SHA: _________________

Comments:
```
[Add any additional notes here]
```

---

## Related Documents

- **Validation Plan**: [Pre-Merge Testing Plan](#implementing-pre-merge-testing-plan-for-copilot-setup-steps-yml)
- **Guard Documentation**: [COPILOT_SETUP_STEPS_GUARD.md](../docs/agent/COPILOT_SETUP_STEPS_GUARD.md)
- **Validation Tests**: [copilot-setup-validation.yml](.github/workflows/copilot-setup-validation.yml)
- **Baseline Commit**: `12f7a861`
- **Canonical Blob**: `8c84a8c1`

## Quick Links

- **Run Validation Locally**: `python scripts/ci/validate_copilot_setup_steps.py`
- **Run All Tests**: `.github/workflows/copilot-setup-validation.yml`
- **View Baseline**: `git show 12f7a861:.github/workflows/copilot-setup-steps.yml`
