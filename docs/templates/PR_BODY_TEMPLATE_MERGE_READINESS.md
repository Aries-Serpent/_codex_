# PR Body Template — Merge Readiness Preparation

**Location:** Use this as a reference when creating new PRs to ensure all required sections are present.  
**Status:** ✅ Mandatory for PRs targeting 100% merge readiness  
**Last Updated:** 2026-06-25

---

## Template Structure

### Header & Basic Info

```markdown
# [Brief Title]

**Branch:** `feature/descriptive-name`  
**Related to:** #XXXX (optional)  
**Risk Level:** [Low|Medium|High]
```

---

## Section 1: Summary (80–200 words)

**Purpose:** High-level overview of the work, business value, and risk profile.

```markdown
## 📋 Summary

[2–3 sentences explaining what this PR does, why it matters, and the primary risk areas]

### Business Value
- [Key benefit 1]
- [Key benefit 2]
- [Key benefit 3]

### Risk Profile
- [Risk 1: Mitigation]
- [Risk 2: Mitigation]
```

---

## Section 2: Changes (Bullet List)

**Purpose:** Specific code/doc/config modifications made.

```markdown
## 🔧 Changes

### Code Changes
- **src/codex/module.py**: [Description of changes]
- **src/codex/submodule.py**: [Description of changes]

### Documentation Changes
- **docs/user-guide.md**: Added section on [topic]
- **README.md**: Updated [section] with new pattern

### Configuration Changes
- **.github/workflows/test.yml**: Updated [action] from v4 to v5
- **pyproject.toml**: Updated dependency constraint [package] from ≥1.0 to ≥2.0

### Test Changes
- **tests/test_module.py**: Added [N] new test cases covering [edge cases]
```

---

## Section 3: Testing (Checklist)

**Purpose:** Test coverage, edge cases addressed, manual validation steps.

```markdown
## ✅ Testing

### Automated Tests
- [x] Unit tests: [N] new, [M] updated, [K] passing
- [x] Integration tests: [All passing/Specific coverage]
- [x] Coverage: [Coverage %] (+[delta] from baseline)

### Manual Testing
- [x] Tested on Python 3.12 locally
- [x] Verified [feature X] with [specific scenario]
- [x] Tested [edge case] to confirm [expected behavior]

### Validation Steps (For Reviewers)
1. Run: `pytest tests/test_module.py -v`
2. Check: Coverage report in Actions → [workflow-name] → artifacts
3. Verify: [Specific behavior/output]
```

---

## Section 4: Completion Checklist

**Purpose:** Status of all implementation objectives.

```markdown
## ✅ Implementation Checklist

### Code Quality
- [x] Ruff linting: All checks passed
- [x] MyPy type checking: All types covered
- [x] No new CodeQL alerts introduced

### Documentation
- [x] README updated if needed
- [x] Docstrings added to public functions
- [x] CHANGELOG entry added

### Verification
- [x] All tests passing (local + CI)
- [x] Coverage maintained or improved
- [x] Branch up-to-date with main
- [x] No merge conflicts

### Accountability
- [x] AGENT_ACCOUNTABILITY_REPORT.md updated
- [x] CHANGELOG.md entry for this work
- [x] Session metadata recorded
```

---

## Section 5: Baseline Metrics (Append Before WEC)

**Purpose:** Quantitative readiness indicators.

```markdown
## 📊 Baseline Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Code Coverage | [X]% | ✅ Meets 95% threshold |
| CodeQL Alerts | [N] open | ✅ No new alerts |
| AAIS Composite Score | [XX]/100 | ✅ Target ≥95 |
| Files Modified | [N] | — |
| Lines Added/Removed | +[A]/-[D] | — |
| Commits | [N] | — |

### Coverage Delta
- Previous: [X]%
- Current: [Y]%
- Delta: [+/-Z]%

### Known Gaps (if any)
- [Gap 1]: Remediation in progress via [link]
- [Gap 2]: Blocked by [dependency]
```

---

## Section 6: Workflow Execution Checklist (WEC) — REQUIRED

**Purpose:** Control which workflows run and which are skipped. MUST be present at the end of every PR body update.

```markdown
## 🔄 Workflow Execution Checklist

Workflows can be skipped/dispatched by updating these checkboxes:

- [x] pre-merge-validation.yml        ← Always-required
- [x] comment-review-gate.yml         ← Always-required
- [x] deferral-language-gate.yml      ← Always-required
- [x] agent-auth-delegation.yml       ← Always-required
- [x] workflow-execution-gate.yml     ← Always-required (orchestrator)
- [x] copilot-agent-checkin.yml       ← Optional but recommended
- [x] copilot-agent-session-done.yml  ← Optional but recommended
- [ ] copilot-iterative-self-healing.yml ← Optional (only if fixing flaky tests)
- [x] cost-gate.yml                   ← Always-required

**⚠️ Note:** WEC state is preserved across all agent updates; maintainer selections ([x]) are carried forward per [WEC_PR_BODY_CONFLICTS.md](docs/workflows/WEC_PR_BODY_CONFLICTS.md).
```

---

## Complete Example PR Body

```markdown
# Implement PR Merge Readiness Framework

**Branch:** `feature/merge-readiness-framework`  
**Related to:** #4662  
**Risk Level:** Medium

## 📋 Summary

This PR introduces a comprehensive PR merge readiness framework with WEC (Workflow Execution Checklist) integration. It establishes a 3-phase approach to reach 100% merge readiness: PR body preparation, pre-merge validation gates, and agentic WEC management.

### Business Value
- Enables quantitative tracking of PR readiness (0–100 score)
- Automates WEC state preservation across agent sessions
- Provides clear gate-by-gate remediation path to 100% merge

### Risk Profile
- Requires PR body format compliance (low risk — documented)
- Depends on existing session_wrapup_autofix.py utilities (low risk — already validated)

## 🔧 Changes

### Documentation Changes
- **docs/workflows/pr_merge_readiness_implementation.md**: New guide for merge readiness framework
- **docs/ci/github_api_copilot_agent_reference.md**: Updated WEC read-before-write pattern documentation

### Code Changes
- **scripts/ci/pr_description_helper.py**: New module with WEC preservation utilities
- **.codex/wec_state.json**: New state tracking file for WEC checkpoint recording

### Configuration
- **.codex/agent_pr_template.md**: New template for agent-created PRs

## ✅ Testing

### Automated Tests
- [x] Integration test: WEC extraction/building from session_wrapup_autofix (passing)
- [x] Unit tests: PR description helper functions (passing)
- [x] Coverage: +1.2% (from 94.8% to 96.0%)

### Manual Testing
- [x] Tested WEC state extraction on sample PR bodies
- [x] Verified WEC rebuild preserves maintainer [x] selections
- [x] Verified always-required items cannot be unchecked

## ✅ Implementation Checklist

### Code Quality
- [x] Ruff linting: All checks passed
- [x] MyPy type checking: All types covered
- [x] No new CodeQL alerts

### Documentation
- [x] README updated
- [x] Docstrings added to all public functions
- [x] CHANGELOG entry added

### Verification
- [x] All tests passing
- [x] Coverage: 96.0% (meets 95% threshold)
- [x] Branch up-to-date with main

### Accountability
- [x] AGENT_ACCOUNTABILITY_REPORT.md updated
- [x] CHANGELOG.md entry added

## 📊 Baseline Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Code Coverage | 96.0% | ✅ Meets 95% threshold |
| CodeQL Alerts | 0 open | ✅ No new alerts |
| AAIS Composite Score | 94/100 | ⚠️ Target ≥95 (gap: 1 pt in Operational Maturity) |
| Files Modified | 5 | — |
| Lines Added/Removed | +287/-42 | — |
| Commits | 3 | — |

### Coverage Delta
- Previous: 94.8%
- Current: 96.0%
- Delta: +1.2%

### Known Gaps
- AAIS score 1 pt below target: Gap in Operational Maturity → Addressed via additional integration test coverage

## 🔄 Workflow Execution Checklist

Workflows can be skipped/dispatched by updating these checkboxes:

- [x] pre-merge-validation.yml        ← Always-required
- [x] comment-review-gate.yml         ← Always-required
- [x] deferral-language-gate.yml      ← Always-required
- [x] agent-auth-delegation.yml       ← Always-required
- [x] workflow-execution-gate.yml     ← Always-required (orchestrator)
- [x] copilot-agent-checkin.yml       ← Optional but recommended
- [x] copilot-agent-session-done.yml  ← Optional but recommended
- [ ] copilot-iterative-self-healing.yml ← Optional (only if fixing flaky tests)
- [x] cost-gate.yml                   ← Always-required

**⚠️ Note:** WEC state is preserved across all agent updates; maintainer selections ([x]) are carried forward per [WEC_PR_BODY_CONFLICTS.md](docs/workflows/WEC_PR_BODY_CONFLICTS.md).
```

---

## Usage Instructions for Agents

### When Creating a New PR:

1. **Use the template sections above** in this exact order
2. **Record baseline metrics** before adding WEC (Section 5)
3. **Append WEC block exactly as shown** (Section 6) — do NOT manually reconstruct
4. **Use the helper function** (Phase 3.1) to preserve WEC state on every `report_progress` call

### When Updating an Existing PR:

1. **Read live PR body** using `gh pr view --json body`
2. **Extract maintainer WEC state** via `session_wrapup_autofix._extract_wec_state()`
3. **Rebuild PR body** with updated content + preserved WEC
4. **Call `report_progress()`** with full body including WEC

---

## References

- **WEC Preservation Guide:** [docs/workflows/WEC_PR_BODY_CONFLICTS.md](../workflows/WEC_PR_BODY_CONFLICTS.md)
- **GitHub API Reference:** [docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md](../ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
- **AAIS V4.0 Framework:** [docs/evolution/AAIS_V4_FRAMEWORK.md](../evolution/AAIS_V4_FRAMEWORK.md)
- **PR Helper Module:** [scripts/ci/pr_description_helper.py](../../scripts/ci/pr_description_helper.py)

---

**Status:** ✅ Ready for use in all Copilot coding agent sessions  
**Last Validated:** 2026-06-25T15:50:00Z
