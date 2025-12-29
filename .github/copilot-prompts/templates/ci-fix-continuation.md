# 🚨 CI/CD Fix Follow-Up Tasks - PR #{pr_number}

**PR**: #{pr_number} - {pr_title}  
**Branch**: `{branch}`  
**Failed Workflows**: {failed_workflow_count}  
**Priority**: 🔴 CRITICAL

---

## ⚠️ FAILING WORKFLOWS

{failing_workflows_list}

---

## 🔍 FAILURE ANALYSIS

### Workflow: {workflow_1_name}
- **Run ID**: [{run_1_id}](https://github.com/Aries-Serpent/_codex_/actions/runs/{run_1_id})
- **Error**: {error_1_summary}
- **Root Cause**: {root_cause_1}
- **Fix Required**: {fix_required_1}

---

## 🛠️ FIX IMPLEMENTATION

### Fix 1: {fix_1_name}

**Files to Modify**: {fix_1_files}

**Changes Required**:
```bash
{fix_1_commands}
```

**Validation**:
```bash
{fix_1_local_validation}

# CI validation
gh run rerun {run_1_id} --failed
gh run watch {new_run_id}
```

---

## ✅ SUCCESS CRITERIA

- [ ] All workflow checks passing (✅ green)
- [ ] No test failures
- [ ] No linting errors
- [ ] No security alerts

---

## 📊 MONITORING

```bash
# Check all workflow runs
gh run list --branch {branch} --limit 10

# Monitor specific workflow
gh run watch {run_id}

# Check PR status
gh pr checks {pr_number}
```

---

## 🤖 COPILOT CONTINUATION

Execute CI fixes in order of priority. Validate each fix before proceeding. Update this file with results after each fix attempt.

**Iteration Protocol**:
1. Apply fix
2. Run local validation
3. Commit changes
4. Trigger CI run
5. Monitor results
6. If fail: analyze, adjust, retry (max 5 iterations per fix)
7. If pass: mark complete (✅), proceed to next fix
