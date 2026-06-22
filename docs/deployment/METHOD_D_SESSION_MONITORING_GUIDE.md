# METHOD D SESSION MONITORING GUIDE — Real-Time Execution Verification

**Last Updated:** 2026-06-22

**Use this guide to monitor a live Copilot session executing the Method D patch.**

**Purpose:** Watch for the exact log markers that prove Method D is working correctly in real-time.

---

## 🟢 PRE-SESSION SETUP (5 minutes)

### 1. Open GitHub Actions Tab

```
URL: https://github.com/Aries-Serpent/_codex_/actions/workflows/copilot-setup-steps.yml
```

- [ ] Bookmark this URL
- [ ] Keep this tab open in a separate window
- [ ] Refresh every 30 seconds while monitoring

### 2. Prepare Log Search Tools

Have these ready on your screen:

```bash
# Terminal 1: Stream logs in real-time (if you have job ID)
gh run view <RUN_ID> --log

# Terminal 2: Or pull full logs after job completes
gh run download <RUN_ID> -D logs/
```

## 3. Create a Monitoring Notes Document

Open a text editor to document observations:

```markdown
# Session Monitoring Log — [Date & Time]

## Pre-Session
- Branch: chore/method-d-preload-deployment
- PR: #[number]
- Test started: [time]

## Real-Time Observations
- [time] Step started
- [time] Marker found: ...
- [time] ...

## Post-Session Summary
- [time] Job completed
- Status: PASS/FAIL
- Findings: ...
```

---

## 🔴 REAL-TIME MONITORING TIMELINE

### Timeline: Minute 0–2 (Checkout Phase)

**What's happening:** GitHub Actions is starting the job and checking out the repository

**Markers to expect:**
- `Run actions/checkout@...`
- `Checking out [branch name]`
- `Fetching ...` (git operations)

**Status indicator:**
- ✅ Expected to see these messages

**If not seen:**
- ⚠️ Job may be queued; wait another 30 seconds

---

### Timeline: Minute 2–5 (Session Preload Step Starts)

**What's happening:** The workflow is now running the session preload step

**🔴 CRITICAL MARKERS TO WATCH:**

```
Marker 1: "Session Context Pre-load"
├─ WHERE: Step name in the job log
├─ LOOK FOR: The step appears as a clickable/expandable section
└─ MEANING: ✅ Step started; YAML parsed successfully
```

**ACTION:** When you see "Session Context Pre-load" step, click to expand it.

---

### Timeline: Minute 3–7 (Inside Session Preload Group)

**What's happening:** The step is executing the Python preload script

**🔴 CRITICAL MARKERS:**

```
Marker 2: "::group::Session Context Pre-load"
├─ WHERE: Inside expanded "Session Context Pre-load" step
├─ LOOK FOR: This exact text as a log line
├─ MEANING: ✅ Block scalar executed; group started
├─ RECORD: Note the timestamp this appeared
└─ If missing after 5 min: ❌ YAML parse failure
```

**ACTION:** Copy the timestamp when you see this marker.

```
Marker 3: Python Script Output (OR Error)
├─ LOOK FOR EITHER:
│  ├─ Lines showing context being loaded (success case)
│  └─ "⚠️ session_preload.py failed (non-blocking)" (failure case)
├─ MEANING: ✅ Script is executing (either way)
└─ RECORD: What output you see
```

---

### Timeline: Minute 7–10 (Fallback & Group End)

**What's happening:** Step is completing (success or fallback execution)

**🔴 CRITICAL MARKERS:**

```
Marker 4: "::endgroup::"
├─ WHERE: End of the Session Context Pre-load step log
├─ LOOK FOR: This exact text
├─ MEANING: ✅ Group closed; step logic completed
├─ RECORD: Timestamp when you see this
└─ If missing after 10 min: ⚠️ Script hung (wait 2 more min)
```

**ACTION:** When you see `::endgroup::`, scroll up and review the entire group content to note:

```
Questions to answer:
- Did the Python script produce output (success case)?
- Did the fallback run ("⚠️ failed" message)?
- Are there any error messages?
- How many lines of output in total?
```

---

### Timeline: Minute 10–15 (Session Access Probe Starts)

**What's happening:** Next step in the workflow should be running (Session Access Probe)

**🔴 CRITICAL MARKERS:**

```
Marker 5: "Session Access Probe"
├─ WHERE: As a new step in the job log
├─ LOOK FOR: The step appears after Session Context Pre-load
├─ MEANING: ✅ Preload didn't hard-fail; workflow continued
├─ RECORD: Did this step appear? When?
└─ If NOT found after 15 min: ⚠️ Preload may have blocked workflow
```

**ACTION:** If you see Session Access Probe starting, Method D is working so far. ✅

**Record in monitoring notes:**
```markdown
## Execution Timeline
- [HH:MM] Session Context Pre-load step started
- [HH:MM] ::group::Session Context Pre-load marker found
- [HH:MM] Python script output observed (or fallback executed)
- [HH:MM] ::endgroup:: marker found
- [HH:MM] Session Access Probe started (workflow continued)
```

---

## 📊 MARKER REFERENCE TABLE

**Use this table while monitoring. Search for each marker in logs:**

| Marker | Status | Location | Timeline | Action |
|--------|--------|----------|----------|--------|
| `Session Context Pre-load` | ✅ Expected | Step name | Min 2–5 | Click to expand |
| `::group::Session Context Pre-load` | ✅ Expected | Inside step logs | Min 3–7 | Record timestamp |
| `⚠️ session_preload.py failed` | ⚠️ Possible | Inside group | Min 5–10 | Non-blocking; continue |
| `SESSION_PRELOAD_STATUS=failed` | ⚠️ Possible | Inside group | Min 5–10 | Fallback executed |
| `::endgroup::` | ✅ Expected | Step end | Min 7–10 | Record timestamp |
| `Session Access Probe` | ✅ Expected | Next step | Min 10–15 | Workflow continued ✅ |
| `YAML parse error` | ❌ ERROR | Early in logs | Min 0–2 | **STOP** — syntax issue |
| `unexpected key` | ❌ ERROR | Early in logs | Min 0–2 | **STOP** — syntax issue |
| `[Step] did not start` | ❌ ERROR | Job summary | Min 15+ | **STOP** — workflow failed |

---

## 🚨 LIVE ISSUE DETECTION

**If you observe any of these during monitoring, note it immediately:**

### Issue A: No `::group::` marker within 5 minutes

**Observation:** You see `Session Context Pre-load` step but no `::group::` inside it

**Diagnosis:** YAML syntax error — the block scalar didn't parse

**Action:**
1. **Record:** Screenshot the step log
2. **Stop:** Job will likely fail soon
3. **Check:** Validate YAML locally again
   ```bash
   yamllint .github/workflows/copilot-setup-steps.yml
   ```
4. **Fix:** Re-apply patch and re-push

**Result:** ❌ Method D not applied correctly; do not proceed to validation

---

### Issue B: `::group::` appears, but `::endgroup::` never comes (step hangs)

**Observation:**
- You see `::group::Session Context Pre-load` at min 5
- But at min 15, `::endgroup::` still not found
- Step is still "running" (no completion status)

**Diagnosis:** Python script hung (not YAML issue)

**Action:**
1. **Wait 2 more minutes** (scripts can be slow)
2. **If still hanging after 7 more minutes (min 22 total):**
   - The session_preload.py script has a bug or deadlock
   - This is NOT a Method D issue (YAML is fine)
   - Stop the job manually
   ```bash
   gh run cancel <RUN_ID>
   ```

**Result:** ⚠️ Preload script needs debugging (separate from Method D validation)

---

### Issue C: `::endgroup::` appears, but Session Access Probe never starts

**Observation:**
- Session Context Pre-load step completes (you see `::endgroup::`)
- But Session Access Probe step never appears
- Job stops or hangs after preload

**Diagnosis:** Preload hard-failed despite `continue-on-error: true`

**Action:**
1. **Check for critical errors in preload logs**
   ```bash
   grep -i "fatal\|error\|exception" <logs>
   ```
2. **If error found:** This indicates a real problem in session_preload.py
   - Not a Method D syntax issue
   - Needs debugging of the Python script itself
3. **If no error:** This is a GitHub Actions engine issue (rare)
   - Re-trigger the job
   - Contact GitHub support if it persists

**Result:** ⚠️ Problem in preload script or GitHub Actions, not Method D

---

### Issue D: All markers found, but job shows FAILED

**Observation:**
- All markers appear correctly
- Session Access Probe starts
- But at the end, job shows ❌ FAILED

**Diagnosis:** Failure is in a downstream step, not preload

**Action:**
1. **Check which step failed**
   - Look for the step with ❌ status
   - Likely not "Session Context Pre-load"
2. **If Session Access Probe or RAG Build failed:**
   - This is unrelated to Method D
   - Fix the broken downstream step
3. **If Session Context Pre-load shows ❌:**
   - This is unexpected (should show ✅ due to `continue-on-error: true`)
   - Review the preload logs for the failure

**Result:** ⚠️ Other issue in workflow; Method D itself is executing

---

### Issue E: All markers found, but Agent Modified the Preload Step

**Observation:**
- Session runs successfully
- All Method D markers appear in logs
- But when you check PR commits, Copilot made commits that modified the preload step

**Diagnosis:** Agent regression — agent "fixed" or "simplified" the step

**Action:**
1. **Document the agent's changes:**
   ```bash
   git show <agent-commit>:.github/workflows/copilot-setup-steps.yml | grep -A10 "Session Context Pre-load"
   ```
2. **Compare to Method D patch** — what changed?
   - Removed `::group::`?
   - Changed `run: |` to `run: python3 ...`?
   - Removed `id: session_preload`?
3. **Severity:**
   - **Low:** Guard comment removed (reapply it)
   - **High:** Syntax changed to old broken form (regression cycle repeating)
4. **Decision:**
   - **Low severity:** Proceed, add guard comment again
   - **High severity:** ❌ Do NOT merge; create issue documenting regression

**Result:** 🔴 CRITICAL — Agent is still regressing the fix

---

## 📋 POST-SESSION LOG ANALYSIS

**After the job completes, perform detailed log forensics:**

### Step 1: Download Full Logs

```bash
# Get the run ID from the Actions tab URL
RUN_ID=<paste from URL>

# Download logs
gh run download $RUN_ID -D session_logs/
cd session_logs/

# Find the setup steps log file
ls -la | grep copilot-setup-steps
```

## Step 2: Extract Session Preload Section

```bash
# Show all lines mentioning "preload" or groups
grep -i "session context pre-load\|::group::\|::endgroup::" copilot-setup-steps.txt > preload_markers.txt

# Show full preload step output
grep -A50 "Session Context Pre-load" copilot-setup-steps.txt > preload_full.txt
```

## Step 3: Verify Key Markers

```bash
# Check marker presence
echo "=== Marker Check ==="
grep "::group::Session Context Pre-load" copilot-setup-steps.txt && echo "✅ Group start found" || echo "❌ Group start missing"
grep "::endgroup::" copilot-setup-steps.txt && echo "✅ Group end found" || echo "❌ Group end missing"
grep "SESSION_PRELOAD_STATUS" copilot-setup-steps.txt && echo "ℹ️ Fallback status found" || echo "ℹ️ Fallback not used (preload succeeded)"
grep "Session Access Probe" copilot-setup-steps.txt && echo "✅ Next step ran" || echo "❌ Next step didn't run"
```

## Step 4: Check for Errors

```bash
# Search for any errors in the preload section
sed -n '/Session Context Pre-load/,/::endgroup::/p' copilot-setup-steps.txt | \
  grep -i "error\|fail\|exception\|fatal" && echo "⚠️ Errors found in preload" || echo "✅ No errors in preload"
```

## Step 5: Verify Agent Didn't Break It

```bash
# Download PR commits
gh pr view <PR_NUM> --json commits -q '.commits[].oid' > commits.txt

# For each Copilot commit, check if it modified the preload step
while read COMMIT; do
  if git show $COMMIT -- .github/workflows/copilot-setup-steps.yml | grep -q "Session Context Pre-load"; then
    echo "Agent modified preload in commit $COMMIT"
    git show $COMMIT -- .github/workflows/copilot-setup-steps.yml | grep -A10 "Session Context Pre-load"
  fi
done < commits.txt
```

---

## ✅ SUCCESS CRITERIA

**Method D is working correctly IF:**

1. ✅ `::group::Session Context Pre-load` appears in logs
2. ✅ `::endgroup::` appears in logs (same step)
3. ✅ Session Access Probe starts (next step runs)
4. ✅ No YAML parse errors
5. ✅ Agent didn't modify the preload step

**If ALL 5 criteria met:** Proceed to validation checklist Phase 7 (Sign-Off)

**If ANY criterion missing:** Document the issue and troubleshoot (see issues above)

---

## 📝 MONITORING LOG TEMPLATE

**Save this template and fill it during monitoring:**

```markdown
# Method D Session Monitoring Log

**Date:** [date]
**Session started:** [time]
**Branch:** chore/method-d-preload-deployment
**PR Number:** #[num]

## Real-Time Timeline

| Minute | Marker | Status | Notes |
|--------|--------|--------|-------|
| 2–5 | Session Context Pre-load step visible | ✅ / ❌ | Appeared at [time] |
| 3–7 | ::group::Session Context Pre-load | ✅ / ❌ | Appeared at [time] |
| 5–10 | Script output or fallback | ✅ / ❌ | [Describe output] |
| 7–10 | ::endgroup:: | ✅ / ❌ | Appeared at [time] |
| 10–15 | Session Access Probe | ✅ / ❌ | Started at [time] |

## Post-Session Verification

- [ ] All markers found
- [ ] No YAML parse errors
- [ ] No script hang
- [ ] Workflow continued (Access Probe ran)
- [ ] Agent didn't modify step
- [ ] Guard comment intact

## Forensic Findings

[Paste output from log analysis above]

## Final Status

- [ ] PASS — All criteria met; safe to merge
- [ ] FAIL — Issues found; needs troubleshooting

## Issues Found (if any)

[Document any regressions or errors]
```

---

## 🎯 NEXT STEPS

**After monitoring completes:**

1. **Successful session?**
   - ✅ Proceed to validation checklist (Phase 7: Sign-Off)
   - Move to merge and main deployment

2. **Issues found?**
   - Document in this monitoring log
   - Review troubleshooting section
   - Fix and re-deploy test session

3. **Critical regression (agent broke it)?**
   - Don't merge to main
   - Create issue with regression evidence
   - Consider stronger prevention (pre-commit hook, branch rules)

---

## Quick Reference: Commands During Monitoring

```bash
# Open logs in real-time
gh run view --log <RUN_ID> | tail -f

# Search for markers in saved logs
grep "::group::" logs/copilot-setup-steps.txt
grep "::endgroup::" logs/copilot-setup-steps.txt
grep "SESSION_PRELOAD_STATUS" logs/copilot-setup-steps.txt
grep "Session Access Probe" logs/copilot-setup-steps.txt

# Check for YAML errors
grep -i "yaml\|parse\|error" logs/copilot-setup-steps.txt

# Get preload section only
sed -n '/Session Context Pre-load/,/Session Access Probe/p' logs/copilot-setup-steps.txt
```

---

**Monitoring guide complete. Use this during your live session to catch issues in real-time.**
