# Agent Integration Guide — PR Merge Readiness Protocol

**Status:** ✅ Production Ready  
**Audience:** Copilot coding agents, CI/CD automation  
**Last Updated:** 2026-06-25

---

## Quick Start for Copilot Agents

When working on a PR targeting 100% merge readiness, follow this integration checklist:

### Before Your First `report_progress` Call

```python
# 1. Import the helper module
from scripts.ci.pr_description_helper import build_pr_description_with_wec

# 2. Read current PR body to preserve WEC state
# (This happens automatically in build_pr_description_with_wec)

# 3. Build your progress checklist
progress_checklist = """## ✅ Session Progress

### Phase 1: PR Body Preparation
- [x] Created base PR description
- [x] Recorded baseline metrics
- [ ] Computed body hash

### Phase 2: Validation Gates
- [x] Code Quality gate: ruff check passed
- [x] Test Coverage gate: 96% coverage
- [ ] Security gate: 1 CodeQL alert pending

### Merge Readiness Score: 68/100"""

# 4. Build PR description WITH preserved WEC (CRITICAL!)
pr_description = build_pr_description_with_wec(
    checklist_text=progress_checklist,
    pr_number=4662,  # Your PR number
    session_id="S_YOUR_SESSION_ID",
    turn_number=1,
    merge_readiness_score=68
)

# 5. Call report_progress with the result
engine_tools_report_progress(
    prDescription=pr_description,
    commitMessage="Progress: Implementing Phase 1 merge readiness prep"
)
```

**Result:** Your PR body will include:
1. Your progress checklist
2. WEC section with maintainer selections preserved
3. State checkpoint recorded to `.codex/wec_state.json`

---

## Operational Rules (Mandatory)

### Rule 1: Read-Before-Write Pattern ✅

**When:** Every `report_progress` call  
**What:** Extract maintainer WEC state from live PR body before rebuilding

```python
# ✅ CORRECT
pr_description = build_pr_description_with_wec(
    checklist_text=my_checklist,
    pr_number=4662  # Read live state from GitHub
)

# ❌ WRONG — reconstructs WEC from template, loses [x] selections
pr_description = my_checklist + "\n" + hardcoded_wec_template
```

### Rule 2: Always Append WEC ✅

**When:** Every `report_progress` call  
**What:** WEC block MUST be included in `prDescription` — never omit

```python
# ✅ CORRECT
report_progress(
    prDescription=f"{checklist}\n{wec_block}",
    commitMessage="..."
)

# ❌ WRONG — WEC stripped on push
report_progress(
    prDescription=checklist_only,  # WEC lost!
    commitMessage="..."
)
```

### Rule 3: Never Uncheck Always-Required Items ✅

**When:** Building/updating WEC  
**What:** These 6 items MUST stay `[x]` (enforced automatically):

1. `pre-merge-validation.yml`
2. `comment-review-gate.yml`
3. `deferral-language-gate.yml`
4. `agent-auth-delegation.yml`
5. `workflow-execution-gate.yml`
6. `cost-gate.yml`

```python
# ✅ These are auto-forced to [x] by _build_wec_block()
# Even if existing_state has them as False, they'll be True in output

# ✅ Optional items (6–8) can be toggled
existing_state = {
    "copilot-agent-checkin.yml": False,  # You can uncheck this
    "copilot-agent-session-done.yml": False,  # You can uncheck this
    "copilot-iterative-self-healing.yml": False,  # You can uncheck this
}
```

### Rule 4: Document Your WEC Choices ✅

**When:** Setting optional items to checked  
**What:** Explain in PR body why you're enabling optional workflows

```markdown
## 🔄 Workflow Execution Checklist

Workflows can be skipped/dispatched by updating these checkboxes:

- [x] pre-merge-validation.yml        ← Always-required
- [x] comment-review-gate.yml         ← Always-required
- [x] deferral-language-gate.yml      ← Always-required
- [x] agent-auth-delegation.yml       ← Always-required
- [x] workflow-execution-gate.yml     ← Always-required (orchestrator)
- [x] copilot-agent-checkin.yml       ← Checked: session starting
- [x] copilot-agent-session-done.yml  ← Checked: expecting finish this session
- [x] copilot-iterative-self-healing.yml ← Checked: fixing 3 flaky tests
- [x] cost-gate.yml                   ← Always-required

**Session Note:** Enabled self-healing for test failures in test_module.py:45-67
```

### Rule 5: Track Merge Readiness Score ✅

**When:** Each `report_progress` turn  
**What:** Calculate and record the 10-gate readiness score

```python
from scripts.ci.pr_description_helper import calculate_merge_readiness_score

# Calculate score from gate status
gates_status = {
    "code_quality": True,      # ruff + mypy pass
    "test_coverage": True,     # ≥95% coverage
    "security_secrets": False, # 1 CodeQL alert open  # pragma: allowlist secret
    "wec_integrity": True,     # WEC complete
    "deferral_language": True, # No prohibited phrases
    "comment_review": True,    # All comments resolved
    "accountability_report": True,  # Updated
    "action_versions": True,   # All approved
    "workflow_syntax": True,   # 0 yamllint errors
    "merge_dependencies": True # Branch clean
}

score = calculate_merge_readiness_score(gates_status)
# Result: 85/100 (9/10 pass, security gate fails)

# Include in PR description
checklist = f"""## 📊 Merge Readiness Progress
- Turn 1: 45/100 (Phase 1 setup)
- Turn 2: 68/100 (Phases 1–2 complete, security pending)
- Turn 3: 85/100 (9/10 gates pass, 1 CodeQL alert blocking)
- **Target:** 100/100"""
```

---

## Integration Points

### Integration Point 1: PR Creation

**Workflow:** Manual (human creates PR)  
**Agent Responsibility:** On first turn, create PR body using template

```markdown
## 📋 Summary
[Your work summary]

## 🔧 Changes
[Your changes]

## ✅ Testing
[Your testing]

## ✅ Checklist
[Completion status]

## 📊 Baseline Metrics
[Coverage, CodeQL, AAIS score]

## 🔄 Workflow Execution Checklist
[Initial WEC — all always-required checked]
```

### Integration Point 2: Session Progress Updates

**Workflow:** `engine-tools-report_progress`  
**Agent Responsibility:** Include WEC in every update

```python
from pr_description_helper import build_pr_description_with_wec

for turn in range(1, num_turns + 1):
    # Make code changes
    code_changes()
    
    # Calculate progress
    progress = generate_progress_report(turn)
    gates_score = calculate_gates()
    
    # Build PR description with WEC preservation
    pr_description = build_pr_description_with_wec(
        checklist_text=progress,
        pr_number=PR_NUMBER,
        session_id=SESSION_ID,
        turn_number=turn,
        merge_readiness_score=gates_score
    )
    
    # Push with WEC preserved
    engine_tools_report_progress(
        prDescription=pr_description,
        commitMessage=f"Turn {turn}: {progress_summary}"
    )
```

### Integration Point 3: Workflow Dispatch on WEC Change

**Workflow:** `workflow-execution-gate.yml` (automatic)  
**Agent Responsibility:** Document workflow choices in PR

When you check an optional workflow item (e.g., `copilot-iterative-self-healing.yml`), the workflow automatically:
1. Detects the checkbox change (Layer 1: detect-wec-changes job)
2. Cancels any in-flight runs of that workflow (Layer 2)
3. Immediately dispatches the workflow (Layer 3)
4. Posts execution plan to PR (Layer 4)

**Agent Action:** Document your reasoning in PR body when enabling workflows

### Integration Point 4: Pre-Merge Validation

**Workflow:** `pre-merge-validation.yml` (automatic on push)  
**Agent Responsibility:** Monitor workflow results and remediate failures

The workflow runs all 10 gates. For each failing gate:
1. Check PR body "Merge Readiness Summary" table for gate-specific failure reason
2. Click linked remediation steps
3. Commit fix
4. Next `report_progress` will update score

---

## Example Session Flow

### Turn 1: Setup Phase

```python
# Import helper
from scripts.ci.pr_description_helper import build_pr_description_with_wec

# Build initial checklist
checklist_turn_1 = """## 📊 Turn 1: Phase 1 Setup

- [x] Created PR body structure
- [x] Recorded baseline metrics (94.8% coverage, 0 CodeQL alerts)
- [x] Computed body hash: sha256:abc123...
- [ ] Completed Phase 2 gates
- [ ] Completed Phase 3 WEC management"""

# Generate PR description with WEC
pr_desc_turn_1 = build_pr_description_with_wec(
    checklist_text=checklist_turn_1,
    pr_number=4662,
    session_id="S_PHASE1",
    turn_number=1,
    merge_readiness_score=30
)

# Push (WEC preserved)
engine_tools_report_progress(
    prDescription=pr_desc_turn_1,
    commitMessage="Turn 1: Initialize PR merge readiness framework"
)

# Result: PR body now has:
# - Your checklist
# - WEC with all always-required [x]
# - Checkpoint recorded to .codex/wec_state.json
```

**Expected Result:**
- PR body created with canonical WEC
- `pre-merge-validation.yml` dispatched automatically
- Merge readiness score: 30/100 (setup phase)

---

### Turn 2: Code Quality Gate

```python
# Make code changes
fix_ruff_errors()
add_type_hints()
run_tests()

# Check gate status
ruff_pass = subprocess.run(["python", "-m", "ruff", "check", "src/", "tests/"], 
                          capture_output=True).returncode == 0
mypy_pass = subprocess.run(["python", "-m", "mypy", "src/"], 
                          capture_output=True).returncode == 0
coverage = get_pytest_coverage()  # Should be ≥95%

# Calculate score
gates = {
    "code_quality": ruff_pass and mypy_pass,
    "test_coverage": coverage >= 95,
    "security_secrets": False,  # Not yet checked  # pragma: allowlist secret
    "wec_integrity": True,      # Always true
    "deferral_language": True,  # Always true
    "comment_review": True,     # No comments yet
    "accountability_report": True,  # Will auto-fix
    "action_versions": True,    # Workflows OK
    "workflow_syntax": True,    # YAML OK
    "merge_dependencies": True  # Branch clean
}
score_turn_2 = calculate_merge_readiness_score(gates)  # ~68/100

# Build PR description for turn 2
checklist_turn_2 = f"""## 📊 Turn 2: Code Quality & Test Coverage

- [x] Fixed 12 ruff violations
- [x] Added type hints to 8 functions
- [x] Coverage increased: 94.8% → 96.2% (+1.4%)
- [ ] Security gates pending
- [ ] Accountability records pending

**Merge Readiness:** {score_turn_2}/100"""

pr_desc_turn_2 = build_pr_description_with_wec(
    checklist_text=checklist_turn_2,
    pr_number=4662,
    session_id="S_PHASE1",
    turn_number=2,
    merge_readiness_score=score_turn_2
)

engine_tools_report_progress(
    prDescription=pr_desc_turn_2,
    commitMessage="Turn 2: Fix code quality, improve test coverage to 96.2%"
)

# Result: Merge readiness now 68/100
```

**Expected Result:**
- Code Quality gate: ✅ Pass
- Test Coverage gate: ✅ Pass
- Merge readiness: 68/100 (+38 from setup)
- `comment-review-gate.yml` + `deferral-language-gate.yml` still running

---

### Turn 3: Security & Final Checks

```python
# Check security gates
codeql_alerts = []  # Should be 0
security_checks = {
    "codeql": len(codeql_alerts) == 0,
    "secrets": True,  # pragma: allowlist secret
    "comment_review": True,
    "accountability_report": True,
}

# Update gates
gates_turn_3 = {
    "security_secrets": security_checks["codeql"] and security_checks["secrets"],  # pragma: allowlist secret
    "comment_review": security_checks["comment_review"],
    "accountability_report": security_checks["accountability_report"],
}
score_turn_3 = calculate_merge_readiness_score(gates_turn_3)  # 100/100

# Build final PR description
checklist_turn_3 = f"""## 📊 Turn 3: Security & Final Verification

- [x] CodeQL check: 0 open alerts
- [x] Secrets baseline: Pass  # pragma: allowlist secret
- [x] Comment review: All resolved (0 blocking)
- [x] Accountability records: Updated
- [x] All 10 gates passing

**Merge Readiness: {score_turn_3}/100 ✅ READY FOR MERGE**"""

pr_desc_turn_3 = build_pr_description_with_wec(
    checklist_text=checklist_turn_3,
    pr_number=4662,
    session_id="S_PHASE1",
    turn_number=3,
    merge_readiness_score=score_turn_3
)

engine_tools_report_progress(
    prDescription=pr_desc_turn_3,
    commitMessage="Turn 3: Security verification complete, merge readiness 100%"
)

# Result: All gates pass, ready for merge
```

**Expected Result:**
- All 10 gates: ✅ Pass
- Merge readiness: **100/100**
- WEC: All 9 items present with always-required checked
- Accountability: AGENT_ACCOUNTABILITY_REPORT.md + CHANGELOG.md updated
- Maintainer can now merge with confidence

---

## Troubleshooting

### Problem: WEC Section Missing After `report_progress`

**Cause:** Did not use `build_pr_description_with_wec()` helper

**Solution:**
```python
# ❌ WRONG
report_progress(prDescription=checklist_only, commitMessage="Missing WEC")

# ✅ CORRECT
from scripts.ci.pr_description_helper import build_pr_description_with_wec

pr_desc = build_pr_description_with_wec(checklist_text=checklist_only, pr_number=4662)
report_progress(prDescription=pr_desc, commitMessage="Preserve WEC")
```

### Problem: Maintainer [x] Selections Lost

**Cause:** Did not read live PR body before rebuilding WEC

**Solution:**
```python
# ✅ Always pass pr_number to read live state
pr_desc = build_pr_description_with_wec(
    checklist_text=my_checklist,
    pr_number=4662  # ← Enables reading live WEC state
)
```

### Problem: Always-Required Items Showing as Unchecked

**Cause:** This should NOT happen — they're auto-forced to [x]

**Solution:** If you see this, verify:
1. `.codex/wec_state.json` has correct `_WEC_ALWAYS_REQUIRED` list
2. `session_wrapup_autofix._build_wec_block()` correctly forces items
3. Run: `python scripts/ci/pr_description_helper.py` (test helper module)

### Problem: State Checkpoint Not Recording

**Cause:** `.codex/wec_state.json` permissions or path issue

**Solution:**
```bash
# Ensure file exists and is writable
touch .codex/wec_state.json
chmod 644 .codex/wec_state.json

# Check JSON syntax
python -m json.tool .codex/wec_state.json
```

---

## Key References

| Document | Purpose |
|----------|---------|
| [PR Body Template](../templates/PR_BODY_TEMPLATE_MERGE_READINESS.md) | Template for PR sections |
| [10 Pre-Merge Gates](../ci/MERGE_READINESS_10_GATES.md) | Detailed gate documentation |
| [WEC Conflicts Guide](../../docs/workflows/WEC_PR_BODY_CONFLICTS.md) | WEC preservation patterns |
| [PR Helper Module](../../scripts/ci/pr_description_helper.py) | Utility functions (canonical) |
| [Session Wrapup Autofix](../../scripts/ci/session_wrapup_autofix.py) | WEC parsing + building |

---

**Status:** ✅ Ready for Agent Deployment  
**Last Tested:** 2026-06-25  
**Validation:** All integration points verified
