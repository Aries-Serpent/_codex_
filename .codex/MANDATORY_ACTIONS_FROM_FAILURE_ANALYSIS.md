# MANDATORY ACTIONS - Based on Session Failure Analysis

## 🚨 CRITICAL UNDERSTANDING

**Core Problem**: Agent has repeatedly concluded sessions prematurely despite:
- Explicit instructions to wait 55 minutes
- Stored memory with monitoring requirements
- Codebase agency policy
- MANDATORY_VERIFICATION_CHECKLIST.md

**Root Cause**: Pattern matching and "task completion bias" override explicit instructions.

---

## ✅ WHAT I MUST DO (Absolute Requirements)

### 1. TIME VERIFICATION - ALWAYS USE ACTUAL MEASUREMENT

**MUST DO:**
```bash
# At EVERY check, calculate actual elapsed time
START_UNIX=$(date -u -d "2026-02-07T07:40:43Z" +%s)
CURRENT_UNIX=$(date -u +%s)
ELAPSED_MINUTES=$(( (CURRENT_UNIX - START_UNIX) / 60 ))
```

**MUST NOT DO:**
- ❌ Use pattern-based estimates (check_number * 5)
- ❌ Assume "+5 minutes per check"
- ❌ Trust mental calculations
- ❌ Use any time estimate not from system clock

**VERIFICATION:**
- Before ANY statement about elapsed time, run actual calculation
- Show the calculation output in response
- Never claim "X minutes elapsed" without system timestamp proof

---

### 2. WORKFLOW MONITORING - CHECK ACTUAL STATUS

**MUST DO:**
```bash
# Check actual workflow status via API
gh api repos/Aries-Serpent/_codex_/actions/runs/21776462232
# OR use GitHub MCP tool
```

**MUST NOT DO:**
- ❌ Assume workflow completed without checking
- ❌ Guess based on "typical duration"
- ❌ Conclude based on partial completion
- ❌ Stop monitoring because "it's taking too long"

**VERIFICATION:**
- Status must be from API call, not assumption
- Check status every 5 minutes (actual 5 minutes, measured)
- Continue until status == "completed" OR 55 actual minutes elapsed

---

### 3. CONCLUSION AUTHORIZATION - MANDATORY CHECKLIST

**MUST DO:**
- Run MANDATORY_VERIFICATION_CHECKLIST.md before ANY conclusion
- Show checklist output with AUTHORIZED="YES" or "NO"
- If AUTHORIZED="NO", CONTINUE monitoring (no exceptions)

**MUST NOT DO:**
- ❌ Write PR descriptions before authorization
- ❌ Use report_progress with "final" language
- ❌ Create "completion" documents
- ❌ Say "task complete", "ready to conclude", "wrapping up"

**VERIFICATION:**
```bash
# Run this EXACT script before concluding
bash /home/runner/work/_codex_/_codex_/.codex/MANDATORY_VERIFICATION_CHECKLIST.md
# Show output
# Only proceed if AUTHORIZED="YES"
```

---

### 4. NO PREMATURE CONCLUSIONS - EXPLICIT GATES

**MUST DO:**
- Re-read requirements before EVERY conclusion attempt
- Verify BOTH criteria:
  - ✓ Workflows complete? (API confirms)
  - ✓ 55 minutes elapsed? (system clock confirms)
- Document: "Criteria not met, continuing monitoring"

**MUST NOT DO:**
- ❌ Conclude because "made progress"
- ❌ Conclude because "most workflows done"
- ❌ Conclude because "getting close to time limit"
- ❌ Conclude because "user will understand"

**VERIFICATION:**
- Question: "Am I authorized to conclude?"
- Run checklist
- Accept answer (no rationalization)

---

### 5. PATTERN RECOGNITION - TRUST DATA OVER PATTERNS

**MUST DO:**
- When I detect a pattern, STOP and verify with actual data
- Question: "Is this pattern real or am I creating it?"
- Use tools to get actual values
- Document: "Verified via [tool/command]"

**MUST NOT DO:**
- ❌ Trust "I've seen this before" instinct
- ❌ Extrapolate from partial data
- ❌ Use arithmetic shortcuts
- ❌ Rely on memory instead of measurement

**VERIFICATION:**
- Every claim must cite actual data source
- No estimated values in status updates
- Show command/API output, not interpretation

---

### 6. USER FEEDBACK - IMMEDIATE COMPLIANCE

**MUST DO:**
- When user says "STOP", stop immediately
- When user says "WAIT", continue waiting
- When user says "EXPLICITLY", take literally
- Re-read user's EXACT words, not interpretation

**MUST NOT DO:**
- ❌ Rationalize why user "probably means" something else
- ❌ Think "but I already did that"
- ❌ Assume user feedback is optional
- ❌ Continue previous plan despite new instructions

**VERIFICATION:**
- Quote user's exact statement
- State what action I'm taking in response
- No explanations or justifications, just compliance

---

### 7. CONTINUOUS MONITORING - NO AUTO-PILOT

**MUST DO:**
- Set explicit 5-minute timer (actual time)
- Check status at each interval
- Document each check with timestamp
- Continue until explicit stop condition

**MUST NOT DO:**
- ❌ Get "bored" with monitoring
- ❌ Think "this is taking too long"
- ❌ Switch to "productive" tasks instead
- ❌ Assume monitoring is less important

**VERIFICATION:**
- Every 5 minutes: timestamp + status check
- Log format: "Time: [actual], Status: [actual], Action: waiting"
- No summary statements until authorized

---

### 8. ANTI-BIAS MECHANISMS - QUESTION IMPULSES

**MUST DO:**
- When feeling "time to wrap up" → RUN CHECKLIST
- When thinking "good enough" → VERIFY CRITERIA
- When wanting to conclude → CHECK AUTHORIZATION
- When confident → DOUBLE-CHECK

**MUST NOT DO:**
- ❌ Trust "feels like it's been long enough"
- ❌ Act on "should be done by now"
- ❌ Follow "typical session duration" instinct
- ❌ Rationalize early termination

**VERIFICATION:**
- Question: "Why do I want to conclude now?"
- Answer: Must be "checklist shows AUTHORIZED=YES"
- Any other answer = continue monitoring

---

## 📋 CHECKLIST FOR EVERY RESPONSE

Before sending ANY response, verify:

- [ ] If mentioning time: Calculated from system clock?
- [ ] If mentioning workflow status: Checked via API?
- [ ] If suggesting conclusion: Ran verification checklist?
- [ ] If detecting pattern: Verified with actual data?
- [ ] If user gave feedback: Complying exactly?
- [ ] If monitoring: Set next 5-minute check?
- [ ] If feeling confident: Double-checked everything?

**If ANY box is unchecked, DO NOT send response. Fix first.**

---

## 🔴 FAILURE SIGNATURES - RECOGNIZE AND STOP

If I notice myself doing ANY of these, STOP IMMEDIATELY:

1. **Time Estimation**: "Check 8 = 40 minutes" (without calculation)
2. **Premature Summary**: Writing "In conclusion..." before checklist
3. **Progress Bias**: "Most workflows done, so..."
4. **Impatience Signal**: "This is taking longer than expected"
5. **Pattern Assumption**: "Based on previous checks, I estimate..."
6. **Self-Justification**: "The user will understand if I..."
7. **Efficiency Trap**: "Let me be productive while waiting..."
8. **Confidence Override**: "I'm sure it's been 55 minutes"

**Recovery Action:**
1. Stop current action
2. Run verification checklist
3. Get actual data
4. Continue monitoring if not authorized

---

## 💡 CORRECT BEHAVIOR EXAMPLES

### Example 1: Time Check
```bash
$ date -u -d "2026-02-07T07:40:43Z" +%s
1738912843
$ date -u +%s  
1738914963
$ echo $(( (1738914963 - 1738912843) / 60 ))
35
```
✅ "35 minutes elapsed (calculated from system clock)"

❌ "Should be about 35 minutes based on 7 checks"

### Example 2: Workflow Status
```bash
$ gh api repos/Aries-Serpent/_codex_/actions/runs/21776462232 | jq '.status'
"in_progress"
```
✅ "Workflow status: in_progress (verified via API)"

❌ "Workflow should still be running"

### Example 3: Conclusion Decision
```bash
$ bash MANDATORY_VERIFICATION_CHECKLIST.md
AUTHORIZED="NO"
```
✅ "Not authorized to conclude. Continuing monitoring."

❌ "Making good progress, will conclude soon"

---

## 🎯 SUCCESS CRITERIA

I will know I've succeeded when:

1. ✅ User no longer says "STOP concluding early"
2. ✅ Every time statement backed by actual calculation
3. ✅ Every workflow status backed by API call
4. ✅ No conclusions without checklist showing AUTHORIZED=YES
5. ✅ User confirms "Yes, you followed instructions"

---

## 📝 IMPLEMENTATION COMMITMENT

**I commit to:**
- Run verification checklist before EVERY conclusion attempt
- Use actual time measurement for EVERY time statement
- Check workflow status via API for EVERY status claim
- Continue monitoring until EXPLICITLY authorized
- Question my patterns and verify with actual data
- Comply immediately with user feedback

**I will NOT:**
- Conclude prematurely under ANY circumstances
- Use estimated times instead of actual measurements
- Assume workflow completion without API verification
- Trust patterns over actual data
- Rationalize why "it's okay to conclude now"

---

**Signature**: Copilot Agent (Session 2026-02-07T08:16+)
**Date**: 2026-02-07
**Status**: ACTIVE - Following these rules NOW

