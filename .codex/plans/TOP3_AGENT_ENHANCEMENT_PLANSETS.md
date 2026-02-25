# Top-3 Agent Enhancement Plansets
> **Generated**: 2026-02-20
> **Session**: 45
> **PR**: #3340 (copilot/sub-pr-3336)
> **Mandate**: Ingest Mission Overview → Select Top-3 Agents for merge/update/develop to resolve CI failures, codebase maintenance, and agent orchestration

---

## 🔍 Mission Overview Ingestion

**Source**: PR #3340 comment (2026-02-20) by @mbaetiong
**Context**: 54 total agents (53 GitHub + 1 quantum reviewer) with 5 active Cognitive Brain phases

### Current Agent Landscape (Key CI-Relevant Clusters)

| Cluster | Existing Agents | Gap |
|---------|-----------------|-----|
| CI Failure Resolution | `ci-testing-agent`, `ci-emergency-response-agent`, `ci-failure-resolution-agent`, `ci-importerror-agent`, `ci-log-retrieval-agent`, `workflow-ci-fixer` | Fragmented — 6 agents, overlapping scope, no unified protocol |
| Codebase Maintenance | `repository-hygiene-agent`, `root-organizer-agent`, `test-alignment-fixer`, `test-coverage-monitor`, `datetime-modernizer` | No agent enforces cross-cutting standards (ruff/mypy/skipif policy) |
| Orchestration | `cognitive-brain-manager` (partial) | **No dedicated task-assignment manager/grader** exists |

### Evidence from Sessions 43-45 (this PR)

- **Sessions 43-45** required 31 CI failures fixed across 5 manual iterations
- Root causes repeated across sessions: PyTorch isinstance (12 tests), faiss lazy import, sitecustomize env, sys.exit regression, API drift
- No single agent could have handled all categories end-to-end
- Zero automated grading/scoring of agent work quality
- ci-testing-agent fixed 15-18 tests/session but missed cross-cutting patterns

---

## 🏆 Top-3 Agent Selections

### Recommendation Matrix

| Rank | Action | Target Agent | Rationale | Impact |
|------|--------|-------------|-----------|--------|
| 1 | **MERGE + UPGRADE** | `ci-testing-agent` ← absorb `ci-failure-resolution-agent` + `ci-emergency-response-agent` | Consolidate 3 overlapping CI agents into one production-grade unified resolver | Eliminates 31 repeated manual CI fix iterations |
| 2 | **DEVELOP (new)** | `agent-orchestrator` (new) | Task-assignment manager, grader, and routing supervisor — doesn't exist yet | Zero orchestration layer currently; sessions bounce between agents with no coordination |
| 3 | **UPDATE** | `workflow-ci-fixer` → enhance into `codebase-health-guardian` | Expand scope from YAML-only CI to full cross-cutting codebase maintenance enforcer | Prevents recurrence of ruff/mypy/skipif-policy violations across all PRs |

---

## PLANSET 1: Merge ci-testing-agent + ci-failure-resolution-agent + ci-emergency-response-agent

### Target: `ci-testing-agent` v4.0.0 (Unified CI Failure Resolver)

**Action**: MERGE three agents → single unified agent
**Files**: `.github/agents/ci-testing-agent.md` (primary), deprecate the other two

### Problem Being Solved

From sessions 43-45 evidence:
- `ci-testing-agent` handled Groups A-D (torch skipif, docker, PEFT, codexml_cli)
- But missed Groups 2-10 in session 45 (bf16, checkpoint, CRM, metrics, feature_store)
- `ci-failure-resolution-agent` has better artifact/log retrieval logic
- `ci-emergency-response-agent` has better rapid triage protocol
- **No single agent read ALL failure categories end-to-end**

### Merged Architecture

```
ci-testing-agent v4.0 (Unified CI Resolver)
├── Phase 1: Log Retrieval (from ci-failure-resolution-agent)
│   ├── get_workflow_run(run_id) via GitHub MCP
│   ├── get_job_logs(failed_only=True, return_content=True)
│   └── Parse: extract FAILED test names + error messages
│
├── Phase 2: Triage (from ci-emergency-response-agent)
│   ├── Categorize by error pattern (isinstance, ImportError, API drift, etc.)
│   ├── Check base branch for pre-existing failures
│   └── Priority sort: regression > new failure > pre-existing
│
├── Phase 3: Fix Implementation (from ci-testing-agent)
│   ├── Pattern library (17 known patterns from sessions 37-45)
│   ├── skipif/importorskip/try-except policy enforcement
│   └── Source API fix vs test fix decision
│
├── Phase 4: Lint + Validation
│   ├── ruff check --fix on all changed files
│   ├── Import smoke tests
│   └── Targeted pytest on fixed tests
│
└── Phase 5: Commit + Report
    ├── report_progress() with full checklist
    └── Tracking log Attempt N entry
```

### Known Fix Patterns (to embed in agent)

| Pattern ID | Error Signature | Fix Method | Sessions Applied |
|------------|----------------|------------|-----------------|
| P-TORCH-312 | `isinstance() arg 2 must be a type` | `@pytest.mark.skipif(_TORCH_312_BUG)` | 43, 45 (×15 tests) |
| P-IMPORT-LAZY | Module available but dep not installed | `pytest.importorskip("dep")` at module level | 44 (faiss) |
| P-ENV-SPECIFIC | sitecustomize/docker/network required | `@pytest.mark.skipif(not _HAS_X)` flag | 44 (sitecustomize, docker) |
| P-API-DRIFT | AttributeError/KeyError on source obj | Fix source API + add backward-compat | 43 (EarlyStopping, health_check) |
| P-SENTINEL | None vs _UNSET ambiguity | Add sentinel object | 44 (TrainingEngine) |
| P-LOGIC-BUG | Test assert never true | Fix test logic | 44 (test_try_except_with_error) |
| P-EXIT-CODE | sys.exit(N) vs return N conflict | Use sys.exit(0) for graceful; check both suites | 45 (hydra cli regression) |
| P-MISSING-ATTR | `module has no attribute X` | Add X to source or update test | 45 (stage_s3_capabilities) |
| P-TYPE-ANNOTATION | `'function' not subscriptable` | `from __future__ import annotations` | 45 (feature_store.py) |
| P-MOCK-SETUP | MagicMock comparison fails | Fix mock return_value for specific attrs | 45 (bf16_probe) |

### Upgraded Capabilities

```yaml
name: CI Testing Agent
version: 4.0.0-unified
merged_from:
  - ci-testing-agent v3.0.0
  - ci-failure-resolution-agent v1.0.0
  - ci-emergency-response-agent v1.0.0

capabilities:
  - End-to-end CI failure resolution (log → fix → commit)
  - 10 known fix patterns (P-TORCH-312 through P-MOCK-SETUP)
  - Regression detection (checks if fix from one test breaks another)
  - ruff auto-fix on all touched files
  - Policy enforcement (no xfail, use skipif/importorskip)
  - Tracking log auto-update (Attempt N format)

protocol:
  - ALWAYS use github-mcp-server tools for log retrieval
  - NEVER use bash/curl to fetch CI data
  - ALWAYS run ruff on changed files before commit
  - NEVER add xfail(strict=False) — use skipif/skip only
  - ALWAYS check for regression: fix Group A → rerun Group A+B together

self_healing:
  - After commit: re-fetch CI run and verify failure count dropped
  - If new failures introduced: auto-classify and fix in same session
  - Max iterations: 5 before escalation to human
```

### Deprecation Plan
- Archive `ci-failure-resolution-agent.md` → `ci-failure-resolution-agent.md.DEPRECATED`
- Archive `ci-emergency-response-agent.md` → `ci-emergency-response-agent.md.DEPRECATED`
- Update `AGENT_REGISTRY.yaml`: remove deprecated, update ci-testing-agent entry
- Update `AGENT_SELECTION_GUIDE.md`: point all CI failure queries → ci-testing-agent v4

---

## PLANSET 2: Develop `agent-orchestrator` (NEW)

### Target: `agent-orchestrator` v1.0.0 (Task Assignment Manager + Grader)

**Action**: DEVELOP new agent — doesn't exist in any form
**Files**: `.github/agents/agent-orchestrator.md` (new)

### Problem Being Solved

From sessions 43-45:
- Primary agent made decisions: "delegate Groups A-D to ci-testing-agent"
- No formal protocol for WHICH agent handles WHICH failure category
- No grading/scoring of agent output quality
- Agent outputs are trusted without verification (ci-testing-agent says "26 fixed" — we trust it)
- No meta-loop: failed sessions repeat the same agent assignments

### Architecture

```
agent-orchestrator v1.0 (Task Assignment + Grading)
│
├── INTAKE: Parse task request
│   ├── Extract: PR number, failing checks, CI run IDs
│   ├── Load: Current tracking log (PR_X_FAILURE_TRACKING_LOG.md)
│   └── Load: Cognitive brain status (latest SESSION_N)
│
├── CLASSIFICATION: Map task → agent(s)
│   ├── CI test failures → ci-testing-agent v4
│   ├── CodeQL/security → security-alert-verification-agent
│   ├── Documentation gaps → documentation-quality-agent
│   ├── Type/lint → workflow-ci-fixer / codebase-health-guardian
│   ├── Active Learning / ML → rag-meta-tensor-regression-agent
│   └── Multi-category → sequence: [ci-testing-agent → codebase-health-guardian]
│
├── DISPATCH: Assign with contract
│   ├── Write task brief to /tmp/ORCHESTRATOR_TASK_{agent}.md
│   ├── Define success criteria (e.g., "0 failures in category X")
│   ├── Set time budget (max 15min per agent)
│   └── Define escalation trigger (>3 retry → human)
│
├── GRADING: Score agent output
│   ├── Criterion 1: Did failure count decrease? (40 pts)
│   ├── Criterion 2: No regressions introduced? (25 pts)
│   ├── Criterion 3: Policy compliance (no xfail)? (20 pts)
│   ├── Criterion 4: Tracking log updated? (10 pts)
│   └── Criterion 5: Lint clean? (5 pts)
│   Total: /100 → pass ≥ 80, retry if 60-79, escalate if <60
│
└── REPORT: Update cognitive brain
    ├── Write grade to tracking log
    ├── Update AGENT_REGISTRY with performance metrics
    └── Post follow-up prompt as comment
```

### Grading Rubric (Detailed)

```python
GRADING_RUBRIC = {
    "failure_reduction": {
        "weight": 40,
        "scoring": {
            "100%_fixed": 40,
            "75-99%_fixed": 30,
            "50-74%_fixed": 20,
            "25-49%_fixed": 10,
            "<25%_fixed": 0,
        }
    },
    "no_regression": {
        "weight": 25,
        "scoring": {
            "zero_regressions": 25,
            "1_regression_self_fixed": 15,
            "1_regression_unresolved": 0,
            "2+_regressions": -20,  # penalty
        }
    },
    "policy_compliance": {
        "weight": 20,
        "checks": [
            "no_xfail_added",       # +5
            "skipif_used_correctly", # +5
            "ruff_clean",           # +5
            "no_root_artifacts",    # +5
        ]
    },
    "documentation": {
        "weight": 10,
        "checks": [
            "tracking_log_updated",  # +5
            "cognitive_brain_updated", # +5
        ]
    },
    "lint_clean": {
        "weight": 5,
        "scoring": {
            "zero_ruff_errors": 5,
            "minor_fixable": 2,
            "requires_manual": 0,
        }
    }
}
```

### Activation Protocol

```markdown
@copilot use agent-orchestrator to assign and grade PR #3340 CI failures

## Required Input
- PR number: 3340
- Failing check URLs: [list]
- Available agents: [auto-detected from AGENT_REGISTRY]

## Expected Output
1. Task assignment brief per agent
2. Dispatch order (sequential or parallel)
3. Grade report after each agent completes
4. Final consolidated score: N/100
5. Cognitive brain status update
```

### Integration with Cognitive Brain

```yaml
cognitive_integration_level: 3  # Full orchestration
capabilities:
  - Read: tracking logs, agent registry, CI data
  - Write: task briefs, grade reports, cognitive brain status
  - Dispatch: invoke any registered agent as subtask
  - Grade: score agent output against rubric
  - Learn: update pattern library based on outcomes
```

---

## PLANSET 3: Update `workflow-ci-fixer` → `codebase-health-guardian` v2.0.0

### Target: `codebase-health-guardian` (Expanded Scope)

**Action**: UPDATE + RENAME existing `workflow-ci-fixer`
**Files**: `.github/agents/workflow-ci-fixer.agent.md` (upgrade in-place)

### Problem Being Solved

Current `workflow-ci-fixer` scope: GitHub Actions YAML syntax only
Required scope: Full cross-cutting codebase health enforcement

Evidence from sessions 43-45:
- Ruff I001 (import order) fires repeatedly across PRs
- W293 (trailing whitespace) introduced by ci-testing-agent in every session
- `from __future__ import annotations` missing in Python 3.9-compat files
- `xfail(strict=False)` policy violations added by agents without enforcement
- No automated check: "did this PR introduce any new xfail?"
- No enforcement: "all stray .md files must go to .codex/"

### Expanded Architecture

```
codebase-health-guardian v2.0 (Full Maintenance Enforcer)
│
├── DOMAIN 1: Workflow Health (existing workflow-ci-fixer scope)
│   ├── YAML syntax validation
│   ├── if: conditions (never if: false in active workflows)
│   └── Job dependency graph validation
│
├── DOMAIN 2: Python Code Quality (NEW)
│   ├── ruff check + fix on all PR-changed files
│   ├── Detect: trailing whitespace (W293), import order (I001)
│   ├── Detect: missing `from __future__ import annotations`
│   ├── Detect: `list[str]` subscript without annotations import
│   └── Auto-fix all fixable, report non-fixable
│
├── DOMAIN 3: Test Policy Enforcement (NEW - critical)
│   ├── Scan all NEW/CHANGED test files
│   ├── FORBIDDEN: xfail(strict=False) without base-branch proof
│   ├── REQUIRED for env deps: pytest.importorskip or @pytest.mark.skipif
│   ├── DETECT: bare `assert True` or always-passing assertions
│   ├── DETECT: try blocks that swallow exceptions silently
│   └── Report violations → block commit if policy_violation=True
│
├── DOMAIN 4: Artifact Hygiene (NEW)
│   ├── Detect stray .md files in repo root
│   ├── Move to .codex/ or reject
│   ├── Detect audit_artifacts/ not in .gitignore
│   └── Enforce: CI session reports match .gitignore patterns
│
└── DOMAIN 5: Cross-PR Pattern Learning (NEW)
    ├── After each run: record patterns applied
    ├── Build frequency table: which violations appear most?
    ├── Update .codex/CODEBASE_HEALTH_REPORT.md
    └── Feed top patterns → ci-testing-agent v4 pattern library
```

### Health Check Protocol

```python
HEALTH_DOMAINS = [
    {
        "id": "D1-WORKFLOW",
        "tool": "ruff check --select=YML",
        "severity": "error",
        "auto_fix": False
    },
    {
        "id": "D2-PYTHON-QUALITY",
        "tool": "ruff check --fix",
        "severity": "warning",
        "auto_fix": True,
        "patterns": ["W293", "I001", "F401", "E501"]
    },
    {
        "id": "D3-TEST-POLICY",
        "tool": "grep -rn 'xfail' tests/",
        "severity": "error",
        "auto_fix": False,
        "forbidden_patterns": [
            r"xfail\(strict=False\)",
            r"xfail\(\)  # noqa",
        ],
        "required_patterns": {
            "import_error": r"pytest\.importorskip\(",
            "env_skip": r"pytest\.mark\.skipif\(",
        }
    },
    {
        "id": "D4-ARTIFACT-HYGIENE",
        "tool": "find . -maxdepth 1 -name '*.md'",
        "severity": "warning",
        "auto_fix": True,  # auto-move to .codex/
        "excluded": ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"]
    }
]
```

### Activation

```markdown
## Trigger 1: Pre-commit hook
# Runs automatically on every commit via pre-commit

## Trigger 2: Manual
@copilot run codebase-health-guardian on PR #3340

## Trigger 3: Orchestrator dispatch
# agent-orchestrator dispatches after ci-testing-agent completes
# to catch any policy violations introduced by CI fixes

## Output
{
    "domains_checked": 4,
    "violations": [
        {"domain": "D3-TEST-POLICY", "file": "...", "line": N, "pattern": "xfail"},
    ],
    "auto_fixed": 12,
    "manual_required": 2,
    "health_score": 87/100
}
```

### Integration Points

```yaml
integrates_with:
  - ci-testing-agent v4: receives health violations after each fix session
  - agent-orchestrator: dispatched as "post-fix validation step"
  - workflow-ci-fixer: replaces and extends (backward compat preserved)
  - AGENT_REGISTRY: updates health_score per PR

pre_commit_hook:
  - run: python scripts/ci/codebase_health_guardian.py --check-only
  - fail_on: D3-TEST-POLICY violations (xfail abuse)
  - warn_on: D2-PYTHON-QUALITY, D4-ARTIFACT-HYGIENE
```

---

## 📐 Implementation Dependency Graph

```
PHASE 1 (Immediate — this session):
  └── Plansets documented ✅ (this file)

PHASE 2 (Next 2 sessions):
  ├── Implement PLANSET 3: codebase-health-guardian
  │   ├── Update workflow-ci-fixer.agent.md in-place
  │   └── Add D3-TEST-POLICY and D4-ARTIFACT-HYGIENE sections
  │
  └── Implement PLANSET 1: ci-testing-agent v4 merge
      ├── Update ci-testing-agent.md with merged protocol
      ├── Add 10 known fix patterns to agent definition
      └── Mark ci-failure-resolution-agent + ci-emergency-response-agent as deprecated

PHASE 3 (Following session):
  └── Implement PLANSET 2: agent-orchestrator (new)
      ├── Create agent-orchestrator.md
      ├── Define grading rubric
      └── Add to AGENT_REGISTRY.yaml
```

---

## 📊 Expected Impact

| Metric | Current (Sessions 43-45) | After Implementation |
|--------|--------------------------|---------------------|
| CI fix iterations per PR | 5+ manual iterations | 1-2 automated |
| Tests fixed per agent session | 15-18 | 25-31 (unified patterns) |
| Regressions introduced | 1-3 per session (e.g., sys.exit(1)) | 0 (health guardian catches) |
| Policy violations (xfail) | Recurring | Blocked at commit |
| Stray root .md files | Every session | Auto-moved |
| Agent grading | None | 0-100 score per session |
| Session continuity | Relies on memory | Tracking log + orchestrator state |

---

## 🔁 Follow-Up Prompt (for next session)

```markdown
@copilot AGENT-ENHANCEMENT Phase 2:

1. Implement PLANSET 3 (codebase-health-guardian):
   - Update .github/agents/workflow-ci-fixer.agent.md with domains D2-D5
   - Add pre-commit hook integration section
   - Test with: grep -rn 'xfail' tests/ | grep -v "TORCH_312_BUG\|_PREEXISTING"

2. Implement PLANSET 1 (ci-testing-agent v4 merge):
   - Update .github/agents/ci-testing-agent.md:
     * Add Phase 1 (Log Retrieval) and Phase 2 (Triage) from merged agents
     * Embed 10 known fix patterns table
     * Add regression-detection protocol
   - Create .github/agents/ci-failure-resolution-agent.md.DEPRECATED
   - Create .github/agents/ci-emergency-response-agent.md.DEPRECATED
   - Update AGENT_REGISTRY.yaml

3. Verify: CI is green on copilot/sub-pr-3336
4. Verify: codeql_checker shows 0 new alerts

Reference: .codex/plans/TOP3_AGENT_ENHANCEMENT_PLANSETS.md
```

---

*Document generated: Session 45, 2026-02-20*
*Status: PLANSET READY — Awaiting Phase 2 implementation*
