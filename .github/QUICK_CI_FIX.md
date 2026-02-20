# Quick CI Fix Command

**For Users**: Use this command in PR comments to get automatic CI failure resolution.

---

## 🚀 Simple Command

```
@copilot Fix all failing checks using the auto-discovery protocol
```

That's it! Copilot will:
1. ✅ Find all failing workflow runs automatically (no links needed)
2. ✅ Download and analyze all failure logs
3. ✅ Check historical fix attempts to avoid thrashing
4. ✅ Implement permanent solutions (not parameter tweaks)
5. ✅ Update tracking logs and documentation

---

## 📋 What Happens Behind the Scenes

Copilot will automatically:

### 1. Discovery Phase
```
→ Get PR details and head commit SHA
→ List all workflow runs for this commit
→ Find all failed jobs
→ Download failure logs
```

### 2. Analysis Phase
```
→ Check .codex/CI_FAILURE_TRACKING_LOG.md for patterns
→ Review git history for previous fix attempts
→ Categorize failures (tests vs infrastructure vs config)
→ Identify root causes (not just symptoms)
```

### 3. Fix Phase
```
→ Run pre-flight validator
→ Implement minimal, targeted fixes
→ Verify fixes don't repeat previous mistakes
→ Run pre-flight validator again
```

### 4. Documentation Phase
```
→ Update CI failure tracking log
→ Create root cause analysis if new pattern
→ Commit with detailed explanation
→ Report progress with evidence
```

---

## 🎯 For Specific Workflows

If you want to focus on specific failures:

```
@copilot Fix the xdist worker crashes in PR #3248 using auto-discovery protocol
```

```
@copilot Fix test failures in Resilient Validation Suite using auto-discovery protocol  
```

---

## 🔍 For Investigation Only

If you just want analysis without fixes:

```
@copilot Analyze all failing checks using auto-discovery and report findings
```

This will:
- Find and categorize all failures
- Check for recurring patterns
- Provide root cause analysis
- Recommend fixes (but not implement)

---

## ⚡ Advanced Usage

### Check History First
```
@copilot Before fixing failures, check if these exact fixes were tried and reverted before
```

### With Pre-flight Validation
```
@copilot Fix failures after running pre-flight checks first
```

### With Tracking Log Update
```
@copilot Fix failures and update the CI tracking log with this resolution
```

---

## 📚 Reference

For details on what the protocol does, see:
- Full prompt: `.github/COPILOT_CI_FAILURE_PROMPT.md`
- Tracking log: `.codex/CI_FAILURE_TRACKING_LOG.md`
- Root cause analysis: `.codex/PR_3248_ROOT_CAUSE_ANALYSIS.md`

---

## 💡 Why This Works

**Old way** (manual):
```
User: The validation suite is failing
Copilot: Can you provide the workflow run links?
User: [pastes 5 URLs]
Copilot: [makes fixes]
[Same fixes fail next week because root cause wasn't addressed]
```

**New way** (automated):
```
User: @copilot Fix all failing checks using auto-discovery protocol
Copilot: [Automatically finds runs, analyzes logs, checks history, fixes root cause]
Copilot: [Documents solution to prevent recurrence]
```

---

## ✅ Expected Results

After using this command, you should see:

1. **Detailed Analysis Comment**:
   - All failures discovered automatically
   - Historical context (is this recurring?)
   - Root cause with evidence from logs
   
2. **Commit(s)**:
   - Minimal, targeted fixes
   - Detailed commit messages explaining WHY
   - References to tracking log entries

3. **Documentation Updates**:
   - New entry in CI failure tracking log
   - Root cause analysis if new pattern
   - Prevention measures documented

4. **Validation**:
   - Pre-flight checks pass
   - No repeated failed fixes
   - Permanent solution confirmed

---

## 🚨 If Copilot Asks for Links

If Copilot says "Can you provide the workflow run links?", respond:

```
@copilot You have GitHub MCP tools available. Use:
- github-mcp-server-actions_list to find workflow runs
- github-mcp-server-get_job_logs to get failure logs

See .github/COPILOT_CI_FAILURE_PROMPT.md for the full protocol.
```

---

**Pro tip**: Bookmark this file for quick reference when CI fails!

