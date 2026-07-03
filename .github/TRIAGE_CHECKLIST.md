# 🚨 CI Failure Triage Checklist

**Purpose**: Standardized process to triage, classify, and route CI failures to the appropriate remediation agent.  
**Authority**: Phase 3.6 CI Triage & Routing Pipeline  
**SLA**: Triage completion within **5 minutes** of failure detection.

---

## Quick Reference: Severity Levels

| Level | Description | SLA | Example | Auto-Route To |
|-------|---|---|---|---|
| **P0** | Merge gate broken; ALL PRs blocked | **15 min** | Hard failure in core test | `ci-emergency-response-agent` |
| **P1** | Critical path failure; blocks release | **1 hour** | Dataclass API drift; test fail | `test-alignment-fixer` / `autonomous-test-healer-agent` |
| **P2** | Important but non-blocking | **4 hours** | Flaky test; broken link | `fragile-test-guardian` / `link-validator-agent` |
| **P3** | Informational/approval gate | **24 hours** | Scanning findings; approval wait | Human review |

---

## Triage Workflow

### ✅ **PHASE 1: Immediate Classification** (5 minutes)

When a GitHub Actions run completes with **failure** or **action_required**:

```bash
□ Step 1.1: Capture Run Details
  - Run URL: https://github.com/Aries-Serpent/_codex_/actions/runs/{RUN_ID}
  - Run Status: [ ] failure  [ ] action_required  [ ] skipped
  - Workflow Name: _______________________
  - Failed Jobs: _________________________

□ Step 1.2: Quick Severity Guess
  - Is this a merge gate / merge-blocking status check? [ ] YES → P0
  - Does it affect critical test path (test suite, main build)? [ ] YES → P1
  - Does it affect optional workflows (doc, scanning, approval)? [ ] YES → P3
  - Default: P2
  - **Your P-Level**: [P0] [P1] [P2] [P3]

□ Step 1.3: Note Symptom Keywords
  Search logs for (copy–paste exact error):
  - [ ] "FAILED" / "AssertionError"
  - [ ] "Error:" / "error:"
  - [ ] "Traceback"
  - [ ] "timeout" / "TimeoutError"
  - [ ] "ImportError" / "ModuleNotFoundError"
  - [ ] "TypeError" (positional arg? missing?)
  - [ ] Other: ________________________________
```

---

### 📋 **PHASE 2: Root Cause Pattern Matching** (5–10 minutes)

**Use the Pattern Library below to match error message.**

#### **PATTERN 1: Import Pre-check Error**

**Symptom**: 
```
ImportError: parent 'codex.agents' not in sys.modules
```

**Match?** [ ] YES → **P1, Agent: ci-importerror-agent**

**Action**:
```bash
@copilot Use ci-importerror-agent to fix import reload issue in run #{RUN_ID}
```

---

#### **PATTERN 2: Dataclass Positional Migration Error**

**Symptom**:
```
TypeError: __init__() missing 1 required positional argument: 'status'
TypeError: __init__() takes X positional arguments but Y were given
```

**Match?** [ ] YES → **P1, Agent: test-alignment-fixer**

**Action**:
```bash
@copilot Use test-alignment-fixer to migrate dataclass constructors in run #{RUN_ID}
```

---

#### **PATTERN 3: CLI Exit Behavior Error**

**Symptom**:
```
AssertionError: SystemExit not raised
Expected: rc=2
Got: [SystemExit raised instead of return]
```

**Match?** [ ] YES → **P1, Agent: autonomous-test-healer-agent**

**Action**:
```bash
@copilot Use autonomous-test-healer-agent to normalize CLI exit behavior in run #{RUN_ID}
```

---

#### **PATTERN 4: Zero Boundary Validation Error**

**Symptom**:
```
AssertionError: assert 0 == 1
# or
take_n(0) returned [item] instead of []
```

**Match?** [ ] YES → **P1, Agent: autonomous-test-healer-agent**

**Action**:
```bash
@copilot Use autonomous-test-healer-agent to add zero-boundary checks in run #{RUN_ID}
```

---

#### **PATTERN 5: Pre-existing Failure (Known Issue)**

**Symptom**:
```
FAILED tests/ml/test_quantization.py::TestQuantization::test_precision_loss
# but this test also fails on base branch
```

**Match?** [ ] YES → **P2, Action: Document + Skip**

**Action**:
```bash
1. Verify failure exists on base branch:
   git checkout base_branch && pytest tests/ml/test_quantization.py -v
2. If yes: Add to tests/conftest.py _PREEXISTING_FAILURES dict
3. If no: Route to autonomous-test-healer-agent as P1
```

---

#### **No Pattern Match? → Go to Phase 3**

---

### 🔧 **PHASE 3: Advanced Troubleshooting** (10–20 minutes)

**If no pattern matched, diagnose the error:**

```bash
□ Step 3.1: Fetch Full Logs
  
  # Option A: GitHub MCP (if available)
  @copilot Use github-mcp-server-get_job_logs to fetch logs for job_id={JOB_ID}
  
  # Option B: GitHub CLI
  gh run view {RUN_ID} --log
  
  # Copy last 500 lines to /tmp/run.log

□ Step 3.2: Categorize Error Type
  - [ ] Test Assertion Failure → ci-testing-agent (P1)
  - [ ] Build Error (Docker, Rust) → ci-docker-build-healer (P1)
  - [ ] Timeout (>6h job) → ci-optimization-agent (P2)
  - [ ] Flaky (passes sometimes) → fragile-test-guardian (P2)
  - [ ] Link/Doc Issue → link-validator-agent (P2)
  - [ ] Workflow Config (YAML error) → workflow-ci-fixer (P0)
  - [ ] Permission/Secret Missing → secret-detection-agent (P1)
  - [ ] Self-Heal Loop (iterative failure) → self-healing-orchestrator-agent (P1)

□ Step 3.3: Route to Agent
  
  Refer to Agent Routing Lookup (below)
```

---

### 📍 **PHASE 4: Agent Routing** (2 minutes)

**Match error category to agent:**

| Error Pattern | Primary Agent | Fallback | P-Level | Time |
|---|---|---|---|---|
| **Hard Test Failure** (assert, logic) | `ci-testing-agent` | `autonomous-test-healer-agent` | P1 | 1h |
| **API Drift** (TypeError positional) | `test-alignment-fixer` | `autonomous-test-healer-agent` | P1 | 1h |
| **Import/Module Error** | `ci-importerror-agent` | `autonomous-test-healer-agent` | P1 | 1h |
| **Flaky Test** (intermittent) | `fragile-test-guardian` | `ci-resilience-emergency-response-agent` | P2 | 4h |
| **Timeout** (6h+ job) | `ci-optimization-agent` | `workflow-optimization-agent` | P2 | 4h |
| **Docker Build Error** | `ci-docker-build-healer` | `ci-failure-resolution-agent` | P1 | 2h |
| **Workflow Config** (YAML, job) | `workflow-ci-fixer` | `workflow-compliance-guardian` | P0 | 30m |
| **Merge Gate Broken** | `ci-emergency-response-agent` | `self-healing-orchestrator-agent` | P0 | **15m** |
| **Broken Link (Docs)** | `link-validator-agent` | `doc-freshness-checker` | P2 | 4h |
| **Missing Secret/Env Var** | `secret-detection-agent` | `repo-var-sync-agent` | P1 | 2h |
| **Self-Heal Loop** (stuck) | `self-healing-orchestrator-agent` | `ci-failure-resolution-agent` | P1 | 2h |

**Invoke Agent**:
```bash
@copilot Use {AGENT_NAME} to {TASK_DESCRIPTION} in run #{RUN_ID}

Example:
@copilot Use ci-testing-agent to debug FAILED test_metric_calculation in run #28637875494
```

---

### ✔️ **PHASE 5: Monitor Fix Attempt** (5–60 minutes)

```bash
□ Step 5.1: Wait for Agent Response
  - For P0: Check agent status every 5 minutes
  - For P1: Check every 15 minutes
  - For P2: Check every 1 hour

□ Step 5.2: Verify Fix (if agent proposes a change)
  - Run local test: pytest {SPECIFIC_TEST} -v
  - If PASS: Approve PR / merge fix
  - If FAIL: Re-route to fallback agent or escalate

□ Step 5.3: If Agent Times Out
  - P0: Escalate to ci-emergency-response-agent immediately
  - P1: Escalate to ci-failure-resolution-agent after 1h
  - P2: Escalate after 4h
```

---

### 📚 **PHASE 6: Document & Learn** (5 minutes)

```bash
□ Step 6.1: If Novel Pattern Discovered
  
  Add to .codex/plans/deep_research_ci_failure_patterns_*.md:
  
  ## Pattern X: [Error Type]
  - Symptom: [exact error message]
  - Root cause: [explanation]
  - Fix: [code example]
  - Agent: [which agent fixes it]

□ Step 6.2: If Long-Tail / Pre-existing Failure
  
  Add to tests/conftest.py:
  
  _PREEXISTING_FAILURES = {
      "tests/path/test_file.py::TestClass::test_name": {
          "reason": "explanation",
          "base_branch_commit": "sha...",
          "ticket": "https://github.com/..."
      }
  }

□ Step 6.3: Report to Memory Store
  
  runtime-tools-store_memory:
  - subject: "CI failure pattern: {PATTERN_TYPE}"
  - fact: "{ERROR_SIGNATURE} → fix with {AGENT_NAME}"
  - scope: "repository"
```

---

## Summary Checklist (Copy & Paste into Issue/PR)

Use this template to document triage decision:

```markdown
## CI Triage Report: Run #[RUN_ID]

**Workflow**: [NAME]  
**Status**: [failure / action_required / skipped]  
**Time to Classify**: [5 min]  

### Classification
- **Severity**: [P0 / P1 / P2 / P3]
- **Pattern**: [Pattern #N or "Custom Error"]
- **Root Cause**: [Brief explanation]

### Routing Decision
- **Primary Agent**: `[agent-name]`
- **Fallback Agent**: `[fallback-agent]`
- **SLA**: [XX minutes/hours]

### Action Taken
```bash
@copilot Use [agent-name] to [task description] in run #[RUN_ID]
```

### Status
- [ ] Agent invoked
- [ ] Fix applied
- [ ] Local test passed
- [ ] PR/merge approved
- [ ] Pattern documented

**Timeline**:
- Failure detected: [TIME]
- Triage complete: [TIME]
- Fix merged: [TIME]
- MTTR: [DURATION]
```

---

## Pro Tips 💡

1. **Time is money**: If you spend >5 min on Phase 1–2, jump to Phase 3 and invoke `ci-testing-agent` (it's faster than manual debugging).

2. **P0 = No Negotiation**: If you suspect P0, immediately invoke `ci-emergency-response-agent` and work backwards during remediation.

3. **Pattern Recognition is Key**: Keep the Pattern Library (5 patterns) memorized. 70% of failures match one of them.

4. **Document ASAP**: Add pre-existing failures to conftest.py immediately so they don't waste triage time next session.

5. **Escalate Early**: If an agent is slow or stuck after 30 min, escalate to `ci-failure-resolution-agent` (its job is to handle stuck agents).

---

## Frequently Asked Questions

**Q: How do I know if a test failure is "pre-existing" vs. "regression"?**

A: Run the test on the base branch (main):
```bash
git stash
git checkout origin/main
pytest tests/path/test_file.py::test_name -v
git checkout -
```
If it fails on main too → pre-existing → add to conftest.py  
If it passes on main → regression → route to ci-testing-agent (P1)

---

**Q: Should I manually fix bugs or use agents?**

A: **Always use agents** for CI failures (that's their job). You are the orchestrator, not the fixer. Your role is:
1. Classify (5 min)
2. Route (2 min)
3. Monitor (ongoing)

If you spend >10 min coding a fix manually, you should have used an agent instead.

---

**Q: What if the same failure happens twice?**

A: After the 2nd occurrence of a pattern:
1. Add it to the Pattern Library (or note if it's already there)
2. Propose a permanent fix (code change, linting rule, etc.) not just a triage marker
3. Open a ticket for root-cause resolution in the next phase

---

**Q: Is this process required for every failure?**

A: **Yes.** Even if you "know" how to fix it, document the triage decision. This builds institutional knowledge and prevents decision fatigue.

---

## Questions or Feedback?

Post in `.codex/PHASE_3_6_CI_TRIAGE_REPORT.md` or open an issue tagged `ci-triage`.

---

**Last Updated**: 2026-07-01  
**Authority**: Phase 3.6 Audit (Agent 6 of 7)  
**Next Review**: Phase 3.7 (Triage Automation)
