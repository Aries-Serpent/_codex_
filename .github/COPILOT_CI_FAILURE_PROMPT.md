# CI Failure Auto-Review Prompt Template

**Purpose**: Automated prompt for reviewing failing CI checks on any PR without manual link gathering.

---

## 🤖 Prompt for Copilot Agent

```markdown
@copilot Review and fix all failing CI checks for PR #[PR_NUMBER]

## Instructions

1. **Automatically retrieve failing checks**:
   - Use GitHub MCP tools to list all workflow runs for this PR
   - Identify failed jobs and get their logs
   - DO NOT ask me for links - you have the tools to find them

2. **Analyze failures systematically**:
   - Group failures by root cause (not by workflow name)
   - Check if issues are recurring (search `.codex/CI_FAILURE_TRACKING_LOG.md`)
   - Review previous fix attempts in git history before making changes

3. **Before making ANY changes**:
   - Read `.codex/PR_3248_ROOT_CAUSE_ANALYSIS.md` to avoid thrashing pattern
   - Check if this exact error has been "fixed" before and reverted
   - Run `python scripts/ci/pre_flight_check.py` to validate current state

4. **Fix failures with permanent solutions**:
   - Fix root causes, not symptoms
   - Don't just tweak parameters that were already tweaked before
   - Add entry to `.codex/CI_FAILURE_TRACKING_LOG.md` for each unique issue

5. **Report progress**:
   - Use report_progress after each meaningful fix
   - Include evidence that fix addresses root cause
   - Document why this fix won't be reverted later

## Required MCP Tool Usage

You MUST use these tools (don't ask me to provide info):

```python
# 1. Get all workflow runs for this PR
github-mcp-server-actions_list(
    method="list_workflow_runs",
    owner="Aries-Serpent",
    repo="_codex_",
    # Filter by PR branch or commit SHA
)

# 2. Get failed job details
github-mcp-server-actions_get(
    method="get_workflow_run",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id=<run_id>
)

# 3. Get job logs
github-mcp-server-get_job_logs(
    job_id=<job_id>,
    owner="Aries-Serpent",
    repo="_codex_",
    return_content=true,
    tail_lines=200
)
```

## Success Criteria

- [ ] All failing checks identified automatically (no manual links needed)
- [ ] Root cause analysis documented
- [ ] History checked for previous attempts
- [ ] Fixes are permanent (not parameter tweaks)
- [ ] Entry added to failure tracking log
- [ ] Pre-flight checks pass after fixes

## Documentation Requirements

After fixing, create or update:
1. Entry in `.codex/CI_FAILURE_TRACKING_LOG.md`
2. Root cause analysis if new failure pattern
3. Prevention measures to avoid recurrence
```

---

## 📋 Enhanced Prompt with Auto-Discovery

Use this for fully autonomous failure resolution:

```markdown
@copilot Comprehensive CI Failure Resolution for PR #[PR_NUMBER]

## Phase 1: Auto-Discovery (Required)

Execute these steps WITHOUT asking me for any information:

1. **Find the PR branch and latest commit**:
   ```
   - Use github-mcp-server-pull_request_read to get PR details
   - Extract head SHA and branch name
   ```

2. **List all workflow runs for this commit**:
   ```
   - Use github-mcp-server-actions_list with method="list_workflow_runs"
   - Filter by the PR's head SHA
   - Identify all runs with conclusion="failure"
   ```

3. **For EACH failed workflow run**:
   ```
   - Use github-mcp-server-actions_list with method="list_workflow_jobs"
   - Find all jobs with conclusion="failure"
   - Retrieve logs with github-mcp-server-get_job_logs
   ```

4. **Categorize failures**:
   ```
   - Test failures (actual test errors)
   - Infrastructure failures (xdist crashes, plugin issues)
   - Configuration failures (missing files, syntax errors)
   - Platform issues (GitHub service problems)
   ```

## Phase 2: Historical Analysis (Required)

Before making ANY changes:

1. **Check failure tracking log**:
   ```bash
   grep -A 20 "<error_pattern>" .codex/CI_FAILURE_TRACKING_LOG.md
   ```

2. **Review git history**:
   ```bash
   git log --all --oneline --grep="<keyword>" -- <affected_files>
   ```

3. **Identify thrashing patterns**:
   - Has this file been changed back and forth?
   - Were similar fixes reverted before?
   - Why did previous attempts fail?

## Phase 3: Root Cause Analysis (Required)

For EACH unique failure:

1. **Document in tracking log**:
   ```bash
   python scripts/ci/log_failure.py --issue "#[PR_NUMBER]" \
       --title "[Descriptive Title]" \
       --symptom "[Error message]" \
       --root-cause "[Technical explanation]" \
       --fix "[Permanent solution]" \
       --recurrence "[First/Nth occurrence]"
   ```

2. **Verify it's not a symptom of deeper issue**:
   - Is this the real problem or a side effect?
   - Will fixing this cause another failure elsewhere?
   - Have we seen cascading failures from similar fixes?

## Phase 4: Implementation (With Validation)

1. **Run pre-flight checks BEFORE changes**:
   ```bash
   python scripts/ci/pre_flight_check.py
   ```

2. **Make minimal, targeted fixes**:
   - Fix root cause, not symptoms
   - Avoid parameter tweaking
   - Ensure fix is permanent

3. **Run pre-flight checks AFTER changes**:
   ```bash
   python scripts/ci/pre_flight_check.py
   ```

4. **Commit with detailed message**:
   ```
   fix(<scope>): <what> - <why this time is different>

   Root Cause: <technical explanation>
   Previous Attempts: <list if applicable>
   Why This Works: <reasoning>
   Prevents Recurrence: <how>
   ```

## Phase 5: Reporting (Required)

Create a summary with:

1. **Failures Found** (auto-discovered, no manual input):
   - Workflow name, job name, run ID, job ID
   - Error messages (from logs)
   - Failure category

2. **Historical Context**:
   - Is this a new failure or recurring?
   - How many times has this been "fixed" before?
   - What changed between last success and now?

3. **Root Cause Analysis**:
   - What's really broken (not just symptoms)
   - Why previous fixes failed (if applicable)
   - Why this fix is permanent

4. **Validation**:
   - Pre-flight checks pass
   - No similar issues in other files
   - Entry added to tracking log

## Anti-Patterns to AVOID

❌ Don't ask: "Can you provide the workflow run links?"
✅ Do: Use MCP tools to find them automatically

❌ Don't say: "The issue appears to be X"
✅ Do: "Analyzed logs, confirmed root cause is X (evidence: <log excerpt>)"

❌ Don't make: Parameter tweaks to flags/versions without history check
✅ Do: Research why those values exist, document why changing

❌ Don't create: Fixes that were tried and reverted before
✅ Do: Understand why previous fix failed, make different fix

## Success Criteria

- [ ] Zero manual input required from me
- [ ] All failures discovered automatically via MCP tools
- [ ] Historical analysis shows this isn't repeating a failed fix
- [ ] Root cause documented with evidence
- [ ] Permanent solution implemented
- [ ] Tracking log updated
- [ ] Pre-flight checks pass

## If You Get Stuck

1. Search `.codex/` directory for similar issues
2. Check `git log` for file modification history
3. Ask specific technical questions about root cause
4. Escalate if this appears to be a platform bug

## Expected Deliverables

1. Complete failure analysis report (auto-generated)
2. Root cause documentation (with evidence)
3. Minimal, targeted fixes (permanent solutions)
4. Updated tracking log entries
5. Passing pre-flight checks
6. Commit with detailed reasoning
```

---

## 🔧 Quick Command for User

Save this as an alias or snippet:

```bash
# In PR comment, just type:
@copilot Fix all failing checks using auto-discovery protocol

# Or with PR number:
@copilot Fix all failing checks for PR #3248 using auto-discovery protocol
```

---

## 📊 Example Expected Response Format

When Copilot follows this prompt, they should respond with:

```markdown
## 🔍 Auto-Discovery Results

**PR #3248 Analysis**

### Workflow Runs Found
- Run ID 22049575907: Resilient Validation Suite (FAILED)
  - Job 63704735364 (slow): FAILED after 7m
  - Job 63704735367 (integration): FAILED after 6m
  - Job 63704735388 (quick): FAILED after 6m

### Failures Categorized
1. **Infrastructure** (3 jobs):
   - xdist worker crashes
   - Error: "unrecognized arguments: --timeout=X -n Y"

2. **Tests** (5 failures in slow job):
   - DummyOptimizer missing param_groups (4 tests)
   - CLI validation match pattern (1 test)

### Historical Context
Checked `.codex/CI_FAILURE_TRACKING_LOG.md`:
- Xdist crashes: 5th occurrence (ba81d9b7, c7043ec5, de6430f7, ac49a922)
- Pattern: Flag thrashing (add -p flags → remove → add again)

### Root Cause Analysis
**Not symptom**: "unrecognized arguments"
**Real issue**: pip install -e .[dev] changes plugin versions after install
**Evidence**:
- de6430f7 added `-p` flags → worked once
- ac49a922 removed them → "Plugin already registered"
- This is dependency version mismatch, not config issue

### Solution (Permanent)
Pin exact plugin versions BEFORE package install:
```yaml
pip install pytest==8.4.2 pytest-xdist==3.8.0 pytest-timeout==2.4.0
pip install -e .[dev]  # Won't change pinned versions
```

No `-p` flags needed - plugins auto-discover when versions stable.

### Validation
✅ Pre-flight checks pass
✅ History shows this breaks thrashing cycle
✅ Tracking log updated with entry
✅ Root cause analysis documented

Proceeding with implementation...
```

---

## 🎯 Integration with Existing Tools

This prompt works with the tools we created:

1. **MCP Tools**: Auto-discovery of failures
2. **Tracking Log**: Historical pattern analysis
3. **Pre-flight Validator**: Before/after validation
4. **Root Cause Docs**: Reference for avoiding thrashing

---

## 📝 Template for Future Sessions

Save this in `.github/copilot-instructions.md`:

```markdown
# Copilot CI Failure Protocol

When asked to fix CI failures:

1. **NEVER** ask for workflow URLs - use MCP tools to discover
2. **ALWAYS** check `.codex/CI_FAILURE_TRACKING_LOG.md` first
3. **ALWAYS** run `scripts/ci/pre_flight_check.py` before/after
4. **NEVER** repeat a fix that was previously reverted
5. **ALWAYS** document root cause with evidence
6. **ALWAYS** update tracking log

See `.codex/SESSION_SUMMARY_PR_3248.md` for example of proper process.
```

---

**This prompt ensures**:
- ✅ No manual link gathering needed
- ✅ Automatic historical analysis
- ✅ Root cause focus
- ✅ Permanent solutions
- ✅ Documentation required
- ✅ Prevents thrashing
