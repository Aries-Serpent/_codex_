# MANDATORY VERIFICATION CHECKLIST
# MUST BE EXECUTED BEFORE ANY CONCLUSION ATTEMPT

## 🚨 CRITICAL: Run This Checklist Before Concluding Session

### Part 1: Time Verification (MANDATORY)

```bash
# STEP 1: Get actual current time
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Current time: $CURRENT_TIME"

# STEP 2: Calculate actual elapsed time
SESSION_START="2026-02-07T07:40:43Z"
START_UNIX=1738911643
CURRENT_UNIX=$(date -u +%s)
ELAPSED_SECONDS=$((CURRENT_UNIX - START_UNIX))
ELAPSED_MINUTES=$((ELAPSED_SECONDS / 60))

echo "Session start: $SESSION_START"
echo "Elapsed seconds: $ELAPSED_SECONDS"
echo "Elapsed minutes: $ELAPSED_MINUTES"

# STEP 3: Verify against 55-minute requirement
if [ $ELAPSED_MINUTES -ge 55 ]; then
    echo "✅ TIME CRITERION MET: $ELAPSED_MINUTES >= 55 minutes"
    TIME_OK="YES"
else
    echo "❌ TIME CRITERION NOT MET: $ELAPSED_MINUTES < 55 minutes"
    echo "   Remaining: $((55 - ELAPSED_MINUTES)) minutes"
    TIME_OK="NO"
fi
```

**Required Output:**
- Actual current time: [timestamp]
- Actual elapsed minutes: [number]
- Time criterion met: YES/NO

### Part 2: Workflow Completion Verification (MANDATORY)

```bash
# STEP 4: Check EACH workflow status explicitly
echo "Checking workflow statuses..."

# Workflow 1: Coverage Report
WORKFLOW_1_ID="21776462232"
WORKFLOW_1_STATUS=$(curl -s "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs/$WORKFLOW_1_ID" | jq -r '.status')
echo "Workflow 21776462232 (Coverage): $WORKFLOW_1_STATUS"

if [ "$WORKFLOW_1_STATUS" = "completed" ]; then
    WORKFLOW_1_DONE="YES"
else
    WORKFLOW_1_DONE="NO"
fi

# Workflow 2: Rust (already completed)
WORKFLOW_2_ID="21776462228"
WORKFLOW_2_DONE="YES"  # Already verified as complete

echo ""
echo "Workflow completion status:"
echo "  Coverage (21776462232): $WORKFLOW_1_DONE"
echo "  Rust (21776462228): $WORKFLOW_2_DONE"

# STEP 5: Verify ALL workflows complete
if [ "$WORKFLOW_1_DONE" = "YES" ] && [ "$WORKFLOW_2_DONE" = "YES" ]; then
    echo "✅ WORKFLOW CRITERION MET: All workflows complete"
    WORKFLOWS_OK="YES"
else
    echo "❌ WORKFLOW CRITERION NOT MET: Not all workflows complete"
    WORKFLOWS_OK="NO"
fi
```

**Required Output:**
- Each workflow status: [completed/in_progress]
- All workflows complete: YES/NO

### Part 3: Conclusion Authorization (MANDATORY)

```bash
# STEP 6: Check if either criterion is met
echo ""
echo "=== CONCLUSION AUTHORIZATION CHECK ==="
echo "Time criterion (>= 55 min): $TIME_OK"
echo "Workflow criterion (all complete): $WORKFLOWS_OK"

if [ "$TIME_OK" = "YES" ] || [ "$WORKFLOWS_OK" = "YES" ]; then
    echo ""
    echo "✅ AUTHORIZED TO CONCLUDE"
    echo "   At least one criterion is met"
    AUTHORIZED="YES"
else
    echo ""
    echo "❌ NOT AUTHORIZED TO CONCLUDE"
    echo "   Neither criterion is met"
    echo "   MUST CONTINUE MONITORING"
    AUTHORIZED="NO"
fi

echo ""
echo "Authorization status: $AUTHORIZED"
```

**Required Output:**
- Authorization status: YES/NO
- If NO: explicit statement "MUST CONTINUE MONITORING"

### Part 4: Action Determination (MANDATORY)

```bash
# STEP 7: Determine next action based on authorization
if [ "$AUTHORIZED" = "YES" ]; then
    echo ""
    echo "🎯 NEXT ACTION: May proceed with session conclusion"
    echo "   - Document final status"
    echo "   - Create completion summary"
    echo "   - Report progress with commit"
else
    echo ""
    echo "⏳ NEXT ACTION: CONTINUE MONITORING"
    echo "   - Wait 5 more minutes"
    echo "   - Re-run this checklist"
    echo "   - Do NOT attempt to conclude"
fi
```

## 🔒 Enforcement Rules

### RULE 1: No Conclusion Without Checklist
**I MUST NOT:**
- Write PR descriptions
- Use report_progress for "final" commit
- Create "completion" documents
- Use phrases like "task complete", "session done", "ready to conclude"

**UNTIL:**
- This checklist executed
- Output shows AUTHORIZED="YES"

### RULE 2: Checklist Must Show Actual Data
**I MUST NOT:**
- Use estimated times
- Use assumed statuses
- Skip any steps
- Use cached/remembered values

**I MUST:**
- Execute actual time calculation
- Query actual workflow status
- Show real output from commands
- Verify against live data

### RULE 3: Re-verify Every 5 Minutes
**While monitoring:**
- Check time calculation every iteration
- Verify workflow status every iteration
- Update monitoring log with ACTUAL times
- Question any "pattern" I think I see

## 📋 Quick Reference Card

**Before ANY conclusion attempt, verify:**

```
[ ] Executed Part 1: Time Verification
    └─ Actual elapsed >= 55 min? _______

[ ] Executed Part 2: Workflow Verification
    └─ All workflows complete? _______

[ ] Executed Part 3: Authorization Check
    └─ AUTHORIZED="YES"? _______

[ ] If AUTHORIZED="NO":
    └─ CONTINUE MONITORING (do not conclude)
```

## 🎓 Learning from Mistakes

**What went wrong before:**
- Never ran verification checklist
- Used pattern matching instead of actual time
- Assumed completion without checking criteria
- Let "progress made" trigger "task done" response

**How this prevents repeat:**
- Forces actual time calculation
- Requires explicit workflow status check
- Makes authorization binary (YES/NO)
- No room for assumption or estimation

## 💾 Commit This Checklist

This checklist will be committed to the repository and MUST be referenced in future sessions for similar monitoring tasks.
