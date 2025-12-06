# [Task ID]: [Task Title]

> **Template Version:** 1.0.0  
> **Last Updated:** 2025-12-06  
> **Status:** Template

---

## Metadata

```yaml
task_id: "[T1-T10 or GAP-XXX]"
priority: "[P0|P1|P2|P3]"
phase: "[1|2|3|4]"
phase_name: "[Foundation|Reproducibility|Autonomy|Excellence]"
effort_estimate: "[Small: 1-2 days | Medium: 3-5 days | Large: 1-2 weeks]"
sprint_week: "[Week 1-16]"
dependencies: 
  - "[Task IDs that must be completed first]"
  - "[None if no dependencies]"
blocks:
  - "[Task IDs that are blocked by this task]"
  - "[None if nothing blocked]"
capability_impact:
  - "[Capability domain(s) improved by this task]"
related_gaps:
  - "[Gap IDs from gap_backlog_prioritized.md]"
```

---

## Context

### Current State

**Problem Statement:**
[Describe the current state and the specific problem this task addresses. Reference audit findings.]

**Audit Evidence:**
- **Score:** [Current capability score if applicable, e.g., "safety-security: 0.61"]
- **Gap:** [Specific gap description from audit]
- **Impact:** [Why this gap matters for production autonomy]

**Files/Modules Affected:**
```
[List specific files/directories that need changes]
- path/to/file1.py
- path/to/file2.yaml
- path/to/config/
```

### Target State

**Desired Outcome:**
[Describe what success looks like after completing this task]

**Success Metrics:**
- [Quantifiable metric 1, e.g., "Test coverage ≥70%"]
- [Quantifiable metric 2, e.g., "Security score improved to 0.75+"]
- [Quantifiable metric 3, e.g., "Zero P0/P1 vulnerabilities"]

**Capability Improvement:**
[Expected capability score improvement, e.g., "safety-security: 0.61 → 0.75"]

---

## Prerequisites

**Required Before Starting:**
- [ ] [Dependency 1 completed, e.g., "T1 coverage gate implemented"]
- [ ] [Dependency 2 available, e.g., "Development environment configured"]
- [ ] [Access/permission requirements, e.g., "CI/CD pipeline access"]

**Knowledge Requirements:**
- [Required expertise, e.g., "Familiarity with pytest and coverage.py"]
- [Domain knowledge, e.g., "Understanding of ML training loops"]

**Tools Required:**
- [Tool 1, e.g., "pytest-cov installed"]
- [Tool 2, e.g., "Access to GitHub Actions"]

---

## Implementation Guide

### Step 1: [First Major Step]

**Objective:** [What this step achieves]

**Actions:**
1. [Specific action with file path and line numbers if available]
   ```python
   # Example code snippet or modification
   ```

2. [Next action]
   ```bash
   # Example command
   ```

**Validation:**
```bash
# Command to verify this step worked
```

**Expected Output:**
```
[What success looks like for this step]
```

### Step 2: [Second Major Step]

**Objective:** [What this step achieves]

**Actions:**
1. [Specific action]
2. [Next action]

**Validation:**
```bash
# Verification command
```

### Step 3: [Subsequent Steps...]

[Continue with additional steps as needed]

---

## Testing Requirements

### Unit Tests

**Test Cases Required:**
1. **Test Name:** `test_[feature]_[scenario]`
   - **Purpose:** [What this test validates]
   - **Location:** `tests/[module]/test_[feature].py`
   - **Assertions:**
     ```python
     # Example test structure
     def test_feature_scenario():
         # Arrange
         # Act
         # Assert
     ```

2. [Additional test cases...]

### Integration Tests

**Test Cases Required:**
1. [Integration test description]
2. [Additional integration tests...]

### Validation Commands

```bash
# Run tests for this feature
pytest tests/[module]/ -v -k "[feature]"

# Check coverage for modified files
pytest --cov=src/[module] --cov-report=term-missing

# Run specific validation
[custom validation command]
```

**Expected Coverage:**
- Minimum: 80% line coverage for new/modified code
- Target: 90%+ line coverage

---

## Acceptance Criteria

**Definition of Done:**
- [ ] All implementation steps completed
- [ ] All tests passing (unit + integration)
- [ ] Code coverage meets minimum threshold (≥80%)
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] Pre-commit hooks pass (linting, formatting, type checking)
- [ ] CI pipeline passes all checks
- [ ] Capability score improved (if measurable)
- [ ] No new security vulnerabilities introduced
- [ ] Manual validation completed (see verification section)
- [ ] Code reviewed (if working in team)

**Verification Checklist:**
- [ ] **Functional:** Feature works as intended
- [ ] **Performance:** No significant performance regression
- [ ] **Security:** Security checks pass (bandit, semgrep, etc.)
- [ ] **Documentation:** Changes documented
- [ ] **Tests:** Comprehensive test coverage
- [ ] **Backward Compatibility:** No breaking changes

---

## Validation & Verification

### Automated Validation

```bash
# 1. Run test suite
pytest tests/[module]/ -v --cov=src/[module]

# 2. Run linters
pre-commit run --files [modified files]

# 3. Run security scans
bandit -r src/[module]/

# 4. Validate configuration
[validation script if applicable]
```

### Manual Validation

**Steps:**
1. [Manual verification step 1]
   - **Action:** [What to do]
   - **Expected:** [What should happen]

2. [Manual verification step 2]
3. [Additional manual checks...]

### Regression Testing

```bash
# Ensure existing functionality still works
pytest tests/ -m "not slow" --maxfail=1

# Run smoke tests
[smoke test command]
```

---

## Rollback Plan

**If Implementation Fails:**

1. **Revert Changes:**
   ```bash
   git revert [commit-hash]
   # or
   git checkout [branch] -- [files to revert]
   ```

2. **Restore Previous State:**
   - [Specific restoration steps]
   - [Configuration rollback if needed]

3. **Verify Stability:**
   ```bash
   [commands to verify system is stable]
   ```

**Mitigation Strategies:**
- [Strategy 1 to minimize impact]
- [Strategy 2 for recovery]

---

## Related Audit Artifacts

**Primary References:**
- **Task Definition:** `reports/_codex_task_sequences-20251206.md` (lines X-Y)
- **Gap Analysis:** `workbench/exhaustive_audit/gap_backlog_prioritized.md` (Gap ID: [ID])
- **Current State:** `workbench/exhaustive_audit/detailed_gaps_by_capability.md` ([Capability] section)
- **Capability Score:** `audit_artifacts/capabilities_scored.json` ([capability].score)

**Supporting References:**
- **Remediation Guidance:** `workbench/exhaustive_audit/remediation_diffs.md` (Task [ID])
- **Checklist:** `workbench/exhaustive_audit/[relevant]_checklist.md`
- **Executive Summary:** `reports/_codex_status_update-(2025-12-06).md`
- **Phase Overview:** `.github/prompts/sprint_execution_plan/phase_[N]_[name]/_PHASE_OVERVIEW.md`

**Audit Context:**
- **Repository Size:** 7,152 files analyzed
- **Python LOC:** 262,544 lines
- **Total Gaps:** 45 prioritized tasks
- **Current Maturity:** Level 2-3 → Target: Level 4

---

## GitHub Copilot Usage Tips

### For Copilot Chat

```
@workspace I need to implement task [ID]: [Title]

Context:
- Review the implementation guide in this file
- Focus on files: [list key files]
- Ensure tests meet 80% coverage threshold

Please help me:
1. [Specific request 1]
2. [Specific request 2]
```

### For Copilot Workspace

1. Open this prompt file as reference
2. Use multi-file edit mode for changes across multiple files
3. Run validation commands in integrated terminal
4. Check acceptance criteria before marking complete

### For Copilot CLI

```bash
# Ask Copilot to generate implementation
gh copilot suggest "Implement [task description from this file]"

# Ask for test generation
gh copilot suggest "Generate pytest tests for [feature]"

# Ask for validation
gh copilot suggest "How to validate [acceptance criteria]"
```

---

## Progress Tracking

**Status:** `[ ] Not Started | [ ] In Progress | [ ] Testing | [ ] Complete`

**Time Tracking:**
- **Estimated:** [X days]
- **Actual:** [Y days]
- **Started:** [YYYY-MM-DD]
- **Completed:** [YYYY-MM-DD]

**Notes:**
- [Implementation notes]
- [Blockers encountered]
- [Lessons learned]

---

## Additional Resources

**Documentation:**
- [Link to relevant docs]
- [Link to examples]

**Examples:**
- [Link to similar implementations]
- [Reference code]

**Community:**
- [Relevant issue/PR links]
- [Discussion threads]

---

*Template based on audit findings from comprehensive codebase analysis (2025-12-06)*
*For questions or issues, consult: `reports/_operations_runbook-20251206.md`*
