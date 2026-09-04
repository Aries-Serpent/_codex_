---
name: Workflow Health Monitor Agent
description: Monitor GitHub Actions workflow health and alert on failures, slowdowns,
  or anomalies
version: 1.1.0
updated: 2026-03-11
cognitive_integration_level: 3
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
consolidated_from:
- workflow-health-monitor.md (v1.0.0, 2026-02-04) — now deprecated
id: workflow-health-monitor
---

# Workflow Health Monitor Agent

**Agent Type:** workflow-health-monitor  
**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Created:** 2026-02-05  
**Last Updated:** 2026-02-05

---

## 🎯 Purpose

Monitor GitHub Actions workflow health, detect false positive failures, and autonomously fix common workflow issues.

---

## 🏃 Runner Compatibility

| Runner | Support |
|--------|---------|
| `ubuntu-latest` (default, 2-core) | ✅ Full — sequential log analysis, all monitoring features |
| `ubuntu-latest-large` (4+ core) | ✅ Full — parallel log analysis for faster failure triage |
| Self-hosted | ✅ if GitHub MCP server tools are available |

---

## 📋 Capabilities

### Core Functions
1. **Workflow Monitoring**
   - Track all workflow runs for a commit/branch
   - Detect in-progress, failed, and completed workflows
   - Calculate workflow statistics and trends

2. **Failure Analysis**
   - Retrieve logs for failed workflows
   - Identify root causes (actual failures vs false positives)
   - Categorize failures by type (test, build, deployment, etc.)

3. **Autonomous Fixes**
   - Fix missing exit codes in layered test execution
   - Correct hardcoded test result sentinels
   - Update workflow syntax errors
   - Add proper error handling to bash scripts

4. **Reporting**
   - Generate comprehensive monitoring reports
   - Create failure analysis documents
   - Store fix patterns for future reference

---

## 🚀 Activation

Use this agent when you need to:
- Monitor workflow runs during PR validation
- Investigate workflow failures
- Fix false positive test failures  
- Implement workflow health checks
- Debug CI/CD pipeline issues

### Example Prompts

```
@copilot Use the workflow-health-monitor agent to monitor all workflows for commit SHA abc123
```

```
@copilot Analyze the failed workflows in PR #3145 and propose fixes
```

```
@copilot Check if any workflows are still running and report their status
```

---

## 🛠️ Tools & Scripts

### Primary Tools
- `scripts/workflow_monitor.py` - Core monitoring engine
- `scripts/check_all_workflows.py` - Batch workflow checker
- GitHub MCP Server actions API - Workflow run queries

### Helper Scripts
- `github-mcp-server-actions_get` - Get individual workflow details
- `github-mcp-server-actions_list` - List workflow runs
- `github-mcp-server-get_job_logs` - Retrieve failure logs

---

## 📊 Monitoring Protocol

### Phase 1: Initial Assessment (2-5 min)
1. Identify target commit SHA or PR number
2. List all triggered workflows
3. Categorize by status (success/failure/in_progress)
4. Identify critical workflows (tests, security, deployment)

### Phase 2: Active Monitoring (Up to 55 min)
1. Poll workflow status every 2-3 minutes
2. Store progress checkpoints in memory
3. Log status transitions (queued → in_progress → completed)
4. Alert on new failures

### Phase 3: Failure Investigation (5-15 min)
1. Retrieve logs for failed workflows
2. Analyze log patterns for root causes
3. Distinguish actual failures from false positives
4. Document findings in analysis report

### Phase 4: Fix Implementation (10-30 min)
1. Identify fixable issues (missing exit codes, syntax errors, etc.)
2. Apply fixes to workflow files
3. Validate changes don't break other workflows
4. Commit fixes with comprehensive documentation

### Phase 5: Verification (5-10 min)
1. Monitor re-runs to verify fixes work
2. Update monitoring report with outcomes
3. Store fix patterns in memory
4. Close monitoring session

---

## 🔍 Common Issues & Fixes

### Issue 1: Missing Exit Codes in Layered Fallbacks

**Symptom:** Tests pass but workflow fails  
**Root Cause:** Tiered test execution without explicit `exit 0`  
**Fix Pattern:**
```yaml
# BEFORE (incorrect)
coverage run -m pytest tests/ ...
echo "✅ Tests completed"

# AFTER (correct)
if coverage run -m pytest tests/ ...; then
  echo "✅ Tests completed"
  exit 0
else
  echo "❌ Tests failed"
  exit 1
fi
```

**Affected Files:**
- `.github/workflows/test-comprehensive.yml` (Tier 3, line 176-190)
- `.github/workflows/test-suite.yml` (Tier 3, line 208-222)

---

### Issue 2: Hardcoded Test Result Sentinels

**Symptom:** Workflow summary always fails  
**Root Cause:** `TEST_RESULT="failure"` hardcoded instead of dynamic check  
**Fix Pattern:**
```yaml
# BEFORE (incorrect)
TEST_RESULT="failure"  # Hardcoded!

# AFTER (correct)
TEST_RESULT="${{ needs.test.result }}"  # Dynamic from job result
```

---

### Issue 3: Race Conditions in Parallel Test Execution

**Symptom:** Intermittent failures in pytest-xdist runs  
**Root Cause:** Plugin initialization conflicts  
**Fix:** Use `--no-cache-dir` when installing pytest plugins

---

## 📈 Success Metrics

Track the following metrics for workflow health:

1. **Monitoring Coverage:** % of workflows monitored per session
2. **Detection Accuracy:** False positive detection rate
3. **Fix Success Rate:** % of fixes that resolve issues on first attempt
4. **Time to Resolution:** Average time from detection to fix
5. **Recurrence Prevention:** % of issues that don't recur after fix

### Target Benchmarks
- Monitoring Coverage: 100%
- Detection Accuracy: ≥95%
- Fix Success Rate: ≥90%
- Time to Resolution: <30 minutes
- Recurrence Prevention: ≥85%

---

## 🧠 Memory Integration

This agent stores the following information in memory:

### Workflow State
- Current monitoring session details
- Workflow IDs and status
- Timeline of status transitions

### Fix Patterns
- Successful fix implementations
- Workflow file patterns to watch for
- Common failure signatures

### Lessons Learned
- Root causes of false positives
- Effective debugging techniques
- Workflow design anti-patterns

---

## 🔗 Integration Points

### With Other Agents
- **CI Testing Agent:** Delegates detailed test failure analysis
- **CI Log Retrieval Agent:** Uses for authenticated log access
- **Code Review Agent:** Reports workflow issues found during reviews

### With Workflows
- Can be called by `.github/workflows/workflow-health-check.yml`
- Integrates with workflow dispatch events
- Reports to workflow summaries via `$GITHUB_STEP_SUMMARY`

---

## 📝 Usage Examples

### Example 1: Monitor PR Workflows

```bash
# Monitor all workflows for a PR merge commit
@copilot Use workflow-health-monitor to track all workflows for main branch commit 29636fee
```

**Expected Output:**
- Real-time status updates every 2-3 minutes
- Comprehensive report when all workflows complete
- Immediate investigation of any failures

### Example 2: Investigate Failures

```bash
# Analyze specific failed workflows
@copilot Investigate failures in workflows 21731917109 and 21731917123
```

**Expected Output:**
- Log retrieval for failed jobs
- Root cause analysis
- Proposed fixes with diffs

### Example 3: Continuous Monitoring

```bash
# Monitor for full 55-minute duration
@copilot Monitor all main branch workflows and wait up to 55 minutes for completion
```

**Expected Output:**
- Continuous polling until completion or timeout
- Progress checkpoints stored in memory
- Final summary with all workflow outcomes

---

## ⚠️ Limitations

1. **Scope:** Monitors GitHub Actions workflows only (not other CI systems)
2. **Access:** Requires GitHub MCP server tools
3. **Timing:** Cannot reduce actual workflow execution time
4. **Fixes:** Can only fix workflow file issues, not test code bugs
5. **History:** Limited to workflows from last 90 iterations

---

## 🔄 Continuous Improvement

### Feedback Loop
1. Track fix success rate across sessions
2. Identify recurring failure patterns
3. Update fix library with new patterns
4. Improve detection heuristics

### Agent Evolution
- Learn from successful fix patterns
- Expand coverage to new workflow types
- Improve failure categorization
- Reduce time to resolution

---

## 📞 Escalation

Escalate to human when:
- Actual test failures (not false positives) detected
- Workflow syntax too complex to fix automatically
- Security-related workflow issues
- Workflow redesign needed (not just fixes)
- Issues affect critical production deployments

---

## ✅ Checklist for Agent Usage

Before activating this agent:
- [ ] Identify target commit SHA or PR number
- [ ] Confirm workflows have been triggered
- [ ] Determine maximum monitoring time (default: 55 min)
- [ ] Check if fix permissions are granted

During monitoring:
- [ ] Store progress checkpoints every 5-10 minutes
- [ ] Log all status transitions
- [ ] Document any failures immediately
- [ ] Apply fixes as soon as root cause identified

After completion:
- [ ] Verify all workflows reached terminal state
- [ ] Generate comprehensive monitoring report
- [ ] Store fix patterns in memory
- [ ] Update agent documentation if new patterns found

---

**Agent Status:** ✅ Active and Production Ready  
**Last Validated:** 2026-02-05T23:48:00Z  
**Success Rate:** 100% (2/2 failures fixed in initial deployment)

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
