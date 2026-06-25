# Post-Merge Copilot Agent Execution Prompt

**Created**: 2026-06-25T22:20:00Z  
**Trigger**: Start of post-merge Copilot agent session  
**Duration**: ~30 minutes (validation phase only)  
**Objective**: Validate merge integrity before continuing post-merge work  
**Authority**: Terminal reversion decision requires @mbaetiong escalation

---

## For the Post-Merge Copilot Agent: Your Mission (First 30 Minutes)

The 0D_base_ → main merge has just completed. Before you start any post-merge work, you have ONE critical task: **Validate that the merge didn't break the Copilot environment.**

Why? Because `copilot-setup-steps.yml` is fragile (YAML syntax, block scalars, no braces). If the merge changed it wrong, future agent sessions will fail silently.

**Your promise to the repository**: Validate once, decide cleanly (proceed or revert), document thoroughly, escalate clearly.

---

## Phase 1: Pre-Work Setup (5 minutes)

### Step 1A: Read Your Handoff Documents
These were created specifically to guide you:

1. **`.codex/POST_MERGE_SESSION_CONTINUATION_BRIEF.md`** — READ FIRST (3 min)
   - What's expected to work post-merge
   - What's known to fail (pre-existing issues)
   - Validation checklist
   
2. **`.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md`** — YOUR VALIDATION GUIDE (10 min)
   - Step-by-step checks for copilot-setup-steps.yml
   - YAML syntax validation
   - Environment variable verification
   
3. **`.codex/POST_MERGE_REVERSION_PROTOCOL.md`** — IF THINGS BREAK (5 min)
   - Failure classification (Category A/B/C)
   - Decision tree: when to revert vs. proceed
   - Reversion procedure (if needed)

4. **`.codex/POST_MERGE_ENVIRONMENT_BASELINE.md`** — YOUR REFERENCE (2 min)
   - Pre-existing dependency gaps (zstandard, sqlalchemy)
   - Test collection baseline
   - What's normal vs. regression

---

## Phase 2: Validation Execution (20 minutes)

### Step 2A: Run Copilot Setup Validation (7 min)

**Purpose**: Ensure copilot-setup-steps.yml is valid post-merge

**Command**:
```bash
cd /home/runner/work/_codex_/_codex_

# Run all validation checks from POST_MERGE_COPILOT_SETUP_VALIDATION.md
# Checks: YAML syntax, job name, block scalar, env vars, Python version, LFS config

# Quick version - run this:
yamllint .github/workflows/copilot-setup-steps.yml && \
  grep -q "copilot-setup-steps:" .github/workflows/copilot-setup-steps.yml && \
  sed -n '132,140p' .github/workflows/copilot-setup-steps.yml | grep -q "run: |" && \
  grep -q "COPILOT_AGENT_CCA_VERSION_LOCK" .github/workflows/copilot-setup-steps.yml && \
  echo "✅ All validation checks passed" || echo "❌ Validation failed"
```

**Decision**:
- ✅ All pass → Go to Step 2B
- ❌ Any fail → Go directly to REVERSION (Phase 3)

---

### Step 2B: Baseline Test Collection (8 min)

**Purpose**: Capture post-merge test environment state

**Command**:
```bash
cd /home/runner/work/_codex_/_codex_

# Collect and save test collection output
pytest --collect-only 2>&1 | tee .codex/POST_MERGE_TEST_COLLECTION_ACTUAL.txt

# Count errors
echo "---"
echo "Checking for errors..."
grep -c "ERROR\|ImportError\|ModuleNotFoundError" .codex/POST_MERGE_TEST_COLLECTION_ACTUAL.txt || echo "0 errors found"
```

**Expected Result**:
- Collection completes (may have import errors for optional deps)
- Errors match pre-existing baseline (zstandard, sqlalchemy)
- NO new errors in core modules

**Decision**:
- ✅ Same errors as baseline → Go to Step 2C
- ⚠️ Fewer errors → Go to Step 2C (improvement, document it)
- ❌ New core module errors → Go to REVERSION (Phase 3)

---

### Step 2C: Environment Variable Verification (5 min)

**Purpose**: Ensure CCA version lock and deduplication are active

**Command**:
```bash
echo "Checking CCA environment variables..."
echo "COPILOT_AGENT_CCA_VERSION_LOCK: ${COPILOT_AGENT_CCA_VERSION_LOCK:-MISSING}"
echo "COPILOT_AGENT_DEDUPLICATION_ENABLED: ${COPILOT_AGENT_DEDUPLICATION_ENABLED:-MISSING}"
echo "COPILOT_AGENT_TURN_ISOLATION_ENABLED: ${COPILOT_AGENT_TURN_ISOLATION_ENABLED:-MISSING}"

# Verify they're set correctly
[[ "$COPILOT_AGENT_CCA_VERSION_LOCK" == "stable" ]] && echo "✅ Version lock OK" || echo "❌ Version lock wrong"
[[ "$COPILOT_AGENT_DEDUPLICATION_ENABLED" == "true" ]] && echo "✅ Dedup enabled" || echo "❌ Dedup disabled"
[[ "$COPILOT_AGENT_TURN_ISOLATION_ENABLED" == "true" ]] && echo "✅ Turn isolation OK" || echo "❌ Turn isolation wrong"
```

**Decision**:
- ✅ All correct → Go to Phase 4 (PROCEED)
- ❌ Any wrong → Go to REVERSION (Phase 3)

---

## Phase 3: Decision Point (2 minutes)

### ✅ PROCEED to Phase 4 if:
- ✅ YAML validation passed
- ✅ Test collection shows same/fewer errors vs. baseline
- ✅ Environment variables correct
- ✅ Python 3.12+

### ❌ REVERT if:
- ❌ YAML parse error
- ❌ 10+ NEW test collection errors
- ❌ Environment variables missing/wrong

### ⚠️ INVESTIGATE if:
- ⚠️ Optional deps missing (expected pre-existing)
- ⚠️ Warnings in yamllint (non-blocking)

---

## Phase 4: If Validation Passes → PROCEED (5 minutes)

### Step 4A: Document Success
```bash
# Create validation success record
cat > .codex/POST_MERGE_VALIDATION_PASSED.txt << 'EOF'
Post-Merge Validation: PASSED
Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)

YAML validation: ✅ Pass
Test collection: ✅ Baseline match
Environment vars: ✅ Correct

Next: Proceed to post-merge work
EOF

# Commit validation checkpoint
git add .codex/POST_MERGE_*.txt
git commit -m "Post-merge validation: PASSED

All checks passed. copilot-setup-steps.yml integrity verified.
Test collection matches pre-merge baseline.
Environment variables correct. Proceeding to post-merge work."
```

### Step 4B: Update Accountability
Edit `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`:

```markdown
## Session: Post-Merge Validation (2026-06-XX)

**Status**: ✅ PASSED

### Validation Results
- copilot-setup-steps.yml: Valid YAML, all checks pass
- Test collection: [X] errors (baseline: [X]) - NO REGRESSION
- Environment: CCA version lock active, deduplication enabled
- Pre-existing issues: zstandard/sqlalchemy missing (documented, not blocking)

### Decision
✅ **PROCEED** to post-merge work

### Next Steps
- Continue with remaining post-merge tasks
- Install optional deps if needed for specific work
- Document any additional findings
```

### Step 4C: Begin Post-Merge Work
You're now cleared to proceed with your assigned post-merge work.

---

## Phase 5: If Validation Fails → REVERT (Terminal Action)

### Step 5A: Capture Failure Evidence
```bash
# Document exact error state
cat > .codex/REVERSION_FAILURE_SNAPSHOT.txt << 'EOF'
=== POST-MERGE VALIDATION FAILURE ===
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Failure Type: [YAML parse / New test errors / Env var missing / Other]

YAML Validation Output:
$(yamllint .github/workflows/copilot-setup-steps.yml 2>&1 || true)

Test Collection Output (last 50 lines):
$(tail -50 .codex/POST_MERGE_TEST_COLLECTION_ACTUAL.txt 2>/dev/null || echo "N/A")

Environment Variables:
COPILOT_AGENT_CCA_VERSION_LOCK: ${COPILOT_AGENT_CCA_VERSION_LOCK:-MISSING}
COPILOT_AGENT_DEDUPLICATION_ENABLED: ${COPILOT_AGENT_DEDUPLICATION_ENABLED:-MISSING}
COPILOT_AGENT_TURN_ISOLATION_ENABLED: ${COPILOT_AGENT_TURN_ISOLATION_ENABLED:-MISSING}

Python Version:
$(python3 --version 2>&1)
EOF
```

### Step 5B: Classify Failure

Read `.codex/POST_MERGE_REVERSION_PROTOCOL.md` and determine:
- Is this **Category A** (MUST REVERT)?
  - YAML parse error
  - Python incompatibility
  - Pip conflict
  - 10+ new test errors
  
- Or **Category B** (INVESTIGATE, don't revert)?
  - Missing optional deps
  - Pre-existing test errors
  - Fixture setup issues

**If Category B**: Proceed to Step 4 (document and continue)

**If Category A**: Go to Step 5C

### Step 5C: Execute Reversion

```bash
# Get working version from main
git fetch origin main:refs/remotes/origin/main

# Identify what to revert
# Option 1: Revert specific file (if only copilot-setup-steps.yml broken)
git checkout origin/main -- .github/workflows/copilot-setup-steps.yml

# Option 2: Revert entire merge (if comprehensive failure)
git reset --hard origin/main

# Create reversion documentation
cat > .codex/REVERSION_ROOT_CAUSE.md << 'EOF'
# Reversion Root Cause Analysis

**Reverted**: .github/workflows/copilot-setup-steps.yml [or entire merge]
**Timestamp**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Failure Type**: [Specify]

## Error Details
[Copy error output from REVERSION_FAILURE_SNAPSHOT.txt]

## Why This Wasn't Caught Pre-Merge
[Analysis]

## Recovery Path
[What needs to be fixed before re-merge]
EOF

# Commit reversion
git add .codex/REVERSION_*.* 
git commit -m "REVERT: Post-merge validation failed - copilot-setup-steps.yml

Reversion triggered by: [Category A failure]
See .codex/REVERSION_FAILURE_SNAPSHOT.txt for error details
See .codex/REVERSION_ROOT_CAUSE.md for root cause analysis

Reverted: .github/workflows/copilot-setup-steps.yml to main baseline

Do not retry merge without @mbaetiong review and approval."
```

### Step 5D: Escalate to @mbaetiong

Create GitHub issue:

**Title**: `[REVERSION] Post-Merge Validation Failed - copilot-setup-steps.yml`

**Body**:
```markdown
## Post-Merge Validation Failure - Reversion Triggered

Copilot agent post-merge validation detected critical failure requiring reversion.

### Reverted Files
- `.github/workflows/copilot-setup-steps.yml` (YAML parse error) [or entire merge]

### Failure Classification
Category A: Critical incompatibility introduced by merge

### Evidence
- Failure snapshot: `.codex/REVERSION_FAILURE_SNAPSHOT.txt`
- Root cause analysis: `.codex/REVERSION_ROOT_CAUSE.md`
- Validation guide: `.codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md`

### Next Steps Required
1. Review failure documentation
2. Identify root cause in original PR
3. Approve fix strategy or defer merge
4. Explicitly notify when retry is approved

**DO NOT** retry merge without explicit approval.
**DO NOT** bypass this validation on next attempt.

@mbaetiong — your review required.
```

### Step 5E: STOP ALL WORK

**You are done.** Do not:
- Attempt to fix the code
- Continue with post-merge work
- Retry the merge

Wait for @mbaetiong to review and approve next steps.

---

## Expected Outcomes

### Outcome A: Validation Passes ✅
**Time**: ~25 minutes  
**Action**: Proceed to post-merge work  
**Next**: Standard post-merge tasks resume  

### Outcome B: Pre-Existing Issues Only ⚠️
**Time**: ~30 minutes (includes optional dep install if needed)  
**Action**: Document in accountability report  
**Next**: Proceed to post-merge work with caveat  

### Outcome C: Validation Fails (Revert) ❌
**Time**: ~15 minutes  
**Action**: Execute reversion, escalate to @mbaetiong  
**Next**: STOP — wait for human approval  

---

## Key Rules (HARD STOPS)

1. ✅ **Read all four handoff docs before starting work**
2. ✅ **Validate before proceeding** (25 min non-negotiable)
3. ✅ **Reversion is terminal** (not a retry trigger)
4. ✅ **Escalate immediately if validation fails** (don't fix, escalate)
5. ✅ **Store all evidence in .codex/** (not /tmp, per policy)
6. ✅ **Commit validation checkpoint** (git log records decision)

---

## Document Reference Map

| Document | Purpose | When to Use |
|----------|---------|------------|
| `POST_MERGE_SESSION_CONTINUATION_BRIEF.md` | First-read overview | START HERE |
| `POST_MERGE_COPILOT_SETUP_VALIDATION.md` | Step-by-step validation | Phase 2 execution |
| `POST_MERGE_ENVIRONMENT_BASELINE.md` | Reference baseline | Understand pre-existing issues |
| `POST_MERGE_REVERSION_PROTOCOL.md` | Decision tree + reversion | Phase 3 (if needed) |
| This prompt | Execution playbook | NOW (you're reading it) |

---

## Success Looks Like

✅ **Session starts post-merge**  
✅ **Validates copilot-setup-steps.yml in 7 min**  
✅ **Tests environment in 8 min**  
✅ **Verifies CCA variables in 5 min**  
✅ **Makes clear decision (proceed/revert) in 2 min**  
✅ **Documents findings**  
✅ **Commits checkpoint**  
✅ **Proceeds to work OR escalates cleanly**  

Total validation time: ~25-30 minutes. Not a bottleneck, a safeguard.

---

## You Are Ready

You have the tools, the documents, the decision tree, and the reversion protocol. 

**Go validate the merge. Good luck.** 🚀
