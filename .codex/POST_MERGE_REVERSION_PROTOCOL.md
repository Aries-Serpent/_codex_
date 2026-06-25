# Post-Merge Reversion Protocol

**Created**: 2026-06-25T22:20:00Z  
**Purpose**: Define when and how to revert post-merge changes if critical failures occur  
**Authority**: Only @mbaetiong can approve reversion  
**Status**: Terminal action - not a retry trigger

---

## Core Principle

**Reversion is TERMINAL.** It is not a retry mechanism. If reversion is triggered, it requires human escalation and approval before any merge is re-attempted.

---

## Failure Classification

### Category A: REVERT IMMEDIATELY (BLOCKING)

These failures indicate critical incompatibility introduced by the merge:

| Failure Type | Detection | Action |
|--------------|-----------|--------|
| **YAML Parse Error** | `yamllint` fails on `copilot-setup-steps.yml` | Revert workflow file to main baseline |
| **Python Incompatibility** | `SyntaxError` or version error in imports | Revert problematic modules |
| **Dependency Conflict** | Pip resolver cannot satisfy constraints | Revert dependency changes |
| **10+ New Test Errors** | Collection introduces new errors in core modules | Revert merge entirely |

### Category B: INVESTIGATE (Non-blocking)

These failures are likely pre-existing or environmental and do NOT trigger automatic reversion:

| Failure Type | Detection | Action |
|--------------|-----------|--------|
| **Missing Optional Deps** | `zstandard`, `sqlalchemy` import errors | Install with `pip install` |
| **Pre-existing Test Errors** | Same errors as pre-merge baseline | Document in accountability report |
| **Collection Incomplete** | <100 tests collected (expected with missing deps) | Install optional deps and re-collect |
| **Fixture Setup Issues** | Optional-dep-dependent fixtures fail | Install optional deps |

### Category C: ESCALATE (Requires Investigation)

These require human judgment and may lead to reversion:

| Failure Type | Detection | Action |
|--------------|-----------|--------|
| **Secret Injection Failure** | `CODEX_MASTER_KEY` / `CODEX_BACKUP_KEY` not injected | Verify secrets are configured in GitHub; do NOT revert workflow |
| **LFS Policy Broken** | `GIT_LFS_SKIP_SMUDGE` not respected | Verify LFS settings; may need git config reset |
| **Environment Variable Loss** | CCA version lock vars missing | Check copilot-setup-steps.yml env block intact |

---

## Decision Tree: When to Revert

```
┌─ Post-Merge Agent Detects Failure
│
├─ YAML Parse Error in copilot-setup-steps.yml?
│  └─ YES → REVERT (Category A)
│
├─ Python SyntaxError or version incompatibility?
│  └─ YES → REVERT (Category A)
│
├─ Test collection shows 10+ NEW errors in core modules?
│  └─ YES → REVERT (Category A)
│
├─ Pip dependency conflict unresolvable?
│  └─ YES → REVERT (Category A)
│
├─ Missing optional deps (zstandard, sqlalchemy)?
│  └─ YES → Install and retry (Category B)
│
├─ Same test errors as pre-merge baseline?
│  └─ YES → Document and proceed (Category B)
│
├─ Secret/LFS/environment variable failure?
│  └─ YES → Investigate, escalate (Category C)
│
└─ All checks pass or only pre-existing issues?
   └─ YES → PROCEED to next phase
```

---

## Reversion Procedure (If Triggered)

### Step 1: Capture Evidence
```bash
# Document exact error state
echo "=== FAILURE STATE ===" > .codex/REVERSION_FAILURE_SNAPSHOT.txt
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> .codex/REVERSION_FAILURE_SNAPSHOT.txt
pytest --collect-only 2>&1 >> .codex/REVERSION_FAILURE_SNAPSHOT.txt
yamllint .github/workflows/copilot-setup-steps.yml 2>&1 >> .codex/REVERSION_FAILURE_SNAPSHOT.txt
python3 --version >> .codex/REVERSION_FAILURE_SNAPSHOT.txt
```

### Step 2: Identify What to Revert
```
IF (copilot-setup-steps.yml failure):
  REVERT: .github/workflows/copilot-setup-steps.yml to main baseline
  PRESERVE: All other changes in current branch
  
IF (dependency conflict):
  REVERT: pyproject.toml dependency changes to main baseline
  PRESERVE: Code changes
  
IF (comprehensive failure):
  REVERT: Entire merge (reset to main)
  PRESERVE: Failure documentation for @mbaetiong
```

### Step 3: Create Reversion Documentation

Create `.codex/REVERSION_ROOT_CAUSE.md`:
```markdown
# Reversion Root Cause Analysis

**Reverted**: [file list]
**Timestamp**: 2026-06-XX...
**Reason**: [Category A/B/C] - [specific failure]

## Error Details
[Full error output]

## Why This Wasn't Caught Pre-Merge
[Analysis of testing gaps]

## Recovery Path
[Steps to fix and re-merge]
```

### Step 4: Escalate to @mbaetiong

Create GitHub issue with label `reversion-required`:
```
Title: [REVERSION] Post-Merge Failure - copilot-setup-steps.yml

## Summary
Post-merge validation triggered reversion protocol.

## Reverted Files
- .github/workflows/copilot-setup-steps.yml (YAML parse error)

## Root Cause
[See .codex/REVERSION_ROOT_CAUSE.md for full analysis]

## Evidence
- Failure snapshot: .codex/REVERSION_FAILURE_SNAPSHOT.txt
- Root cause analysis: .codex/REVERSION_ROOT_CAUSE.md
- Session: @copilot [agent session ID]

## Decision Required
- Approve retry with fix
- Document as known issue for future merges
- Escalate to infrastructure team
```

### Step 5: Halt All Work

**DO NOT**:
- Attempt to fix the reverted code immediately
- Re-merge without @mbaetiong approval
- Continue post-merge work in current branch

**WAIT FOR**:
- @mbaetiong review of failure documentation
- Explicit approval to retry or escalate further

---

## Reversion is Terminal: Examples

### Example 1: YAML Syntax Error (REVERT)
```
Scenario: Post-merge, copilot-setup-steps.yml lines 143-147 have flow-scalar syntax
Detection: yamllint error "found undefined alias"
Action: 
  1. Capture error state → .codex/REVERSION_FAILURE_SNAPSHOT.txt
  2. Revert .github/workflows/copilot-setup-steps.yml
  3. Document root cause → .codex/REVERSION_ROOT_CAUSE.md
  4. Create escalation issue
  5. STOP — wait for @mbaetiong approval
```

### Example 2: Missing Optional Deps (DO NOT REVERT)
```
Scenario: Post-merge, pytest collection shows zstandard ImportError
Detection: "ModuleNotFoundError: No module named 'zstandard'"
Action:
  1. Verify error matches pre-merge baseline
  2. Install: pip install zstandard
  3. Re-run: pytest --collect-only
  4. If collection succeeds → Document and proceed
  5. CONTINUE post-merge work
```

### Example 3: Pip Conflict (REVERT)
```
Scenario: Post-merge, pip install fails with incompatible versions
Detection: "ERROR: pip's dependency resolver does not currently take into account all the packages that are installed"
Action:
  1. Capture error → .codex/REVERSION_FAILURE_SNAPSHOT.txt
  2. Revert pyproject.toml changes
  3. Document conflict → .codex/REVERSION_ROOT_CAUSE.md
  4. Create escalation issue
  5. STOP — wait for human review
```

---

## Post-Reversion: What Happens Next

After reversion is documented and escalated:

1. **Human decision made by @mbaetiong**:
   - Approve specific code fix + retry
   - Defer merge to future session
   - Escalate to infrastructure team
   - Other decision

2. **Only after approval** can:
   - New PR be created with fixes
   - Merge be re-attempted
   - Work continue

3. **No automatic retries** allowed

---

## Key Constraints (HARD RULES)

1. ✅ **Reversion is documented** - Must create `.codex/REVERSION_ROOT_CAUSE.md`
2. ✅ **Reversion is escalated** - Must create issue and tag @mbaetiong
3. ✅ **Reversion is terminal** - Must STOP and wait for approval
4. ✅ **Never retry automatically** - This is a blocker, not a transient error
5. ✅ **Preserve evidence** - Keep .codex/ files; never delete failure logs

---

## Session Continuation Expectation

If reversion is NOT triggered and post-merge validates successfully:
- Continue with standard post-merge work
- Document any pre-existing issues encountered
- Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with baseline vs. post-merge diff
- Proceed to remaining Phase work
