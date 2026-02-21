# Agentic Session Methodology (ASM) v1.0
> Framework: Orchestrated Session Management for Production Readiness
> Primary Orchestrator: `agent-orchestrator.md` v1.0.0
> Created: 2026-02-20 | Session 47 — PR #3336 / PR #3340
> Planset Source: `.codex/plans/TOP3_AGENT_ENHANCEMENT_PLANSETS.md`

---

## 🎯 TASK 0 — Objective

Develop an Agentic Methodology utilizing `agent-orchestrator` for efficient session management.
Each planned Session maps to a PLANSET with clear checkpoints, benchmarks, and a definitive
goal: **ALL failing checks resolved by session end**.

---

## 📐 Framework Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SESSION NN LIFECYCLE                                                   │
│                                                                         │
│  [STARTUP]          [TRIAGE]          [EXECUTE]          [VALIDATE]    │
│  ┌─────────┐        ┌─────────┐       ┌─────────┐        ┌──────────┐ │
│  │ Load    │───────▶│Orchestr-│──────▶│Speciali-│───────▶│ Health   │ │
│  │ Memory  │        │ator     │       │  zed    │        │ Guardian │ │
│  │ + PRs   │        │ Routes  │       │ Agents  │        │ D1-D4    │ │
│  └─────────┘        └─────────┘       └─────────┘        └──────────┘ │
│       │                  │                  │                  │       │
│   MANDATORY         GRADING             FIX + COMMIT       GATE CHECK  │
│   DOCS LOAD         RUBRIC             REPORT_PROGRESS     BEFORE PUSH │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 MANDATORY Session Startup Protocol (MSP)

Every session MUST begin by executing these steps in order. No deviation.

### MSP-1: Memory Load (≤ 2 min)

```
🔃 LOAD: Related Memory (store_memory facts from previous sessions)
🔃 LOAD: .codex/ACCOUNTABILITY_REPORT_*.md (lessons learned)
🔃 LOAD: .codex/CODEBASE_AGENCY_POLICY.md (prohibited patterns)
🔃 LOAD: .codex/plans/AGENTIC_SESSION_METHODOLOGY.md (this document)
```

**GitHub Utility — Commit-PR Awareness (GitHub MCP calls):**

```python
# Step 1: Identify current PR and branch
list_workflow_runs(branch=CURRENT_BRANCH, per_page=5)

# Step 2: Understand last 2 MERGED PRs
list_pull_requests(state="closed", sort="updated", direction="desc", per_page=5)
# → Get last 2 merged PR numbers and base commits

# Step 3: Load last 2 merged PRs' commit diffs for context
get_commit(sha=MERGED_PR_HEAD_SHA)  # PR N-1
get_commit(sha=MERGED_PR_HEAD_SHA)  # PR N-2

# Step 4: Inventory all open/draft PRs
list_pull_requests(state="open", per_page=20)
# → Identify stacked PRs, draft PRs, blocked PRs

# Step 5: Cherry-pick context from previous commits when files are missing/overwritten
# git_show_file_at_commit = get_commit(sha=PREVIOUS_SHA, include_diff=True)
# → Extract specific file contents from git history via GitHub MCP
```

### MSP-2: CI Awareness (≤ 3 min)

```python
# Get latest run for current branch
list_workflow_runs(branch=CURRENT_BRANCH, status="completed", per_page=3)

# For each failed run:
list_workflow_jobs(run_id=FAILED_RUN_ID)
# → Identify quick / slow / integration job IDs

# Get failure logs (only tail needed):
get_job_logs(job_id=FAILED_JOB_ID, failed_only=True, return_content=True, tail_lines=200)
```

### MSP-3: Baseline Snapshot (≤ 1 min)

```bash
# Local state check
git log --oneline -10         # recent commits
git status --short            # unstaged changes
git diff HEAD --stat          # what changed vs latest commit
```

---

## 🗺️ Session PLANSET Map — Path to Production Readiness

Each session has a **primary PLANSET** (mandatory) and optional secondary tasks.

### Session Framework Structure

```
Session NN
├── PLANSET: <primary objective name>
├── Pre-conditions: <what must be true before this session starts>
├── Checkpoints:
│   ├── CP-1: <first verifiable milestone>
│   ├── CP-2: <second verifiable milestone>
│   └── CP-3: <final milestone — CI green>
├── Benchmarks:
│   ├── BM-1: <quantitative pass criterion>
│   └── BM-2: <quantitative pass criterion>
├── Agent Assignments: <which specialized agents to invoke>
├── Exit Criteria: ALL failing checks resolved
└── Escalation: If score < 70 after 3 iterations → @mbaetiong
```

---

## 📅 Planned Sessions Map (Active)

### Session 47 — CI Failure Resolution + TASK 0 Methodology
**PLANSET**: PLANSET-CI-047  
**Pre-conditions**: run 22227371821 failures identified  
**Agent Assignments**: `ci-testing-agent` v4.0, `codebase-health-guardian`

| Checkpoint | Target | Status |
|------------|--------|--------|
| CP-1: All 20 quick failures root-caused | ≤ 15 min | ✅ Complete |
| CP-2: All 5 slow failures root-caused | ≤ 15 min | ✅ Complete |
| CP-3: Fixes committed, CI triggered | ≤ 30 min | 🔄 In Progress |

**Benchmarks**:
- BM-1: `quick` suite ≤ 5 failures (down from 15)
- BM-2: `slow` suite = 0 failures (down from 5)
- BM-3: Auto-Fix Check exits 0

**Exit Criteria**: Both Resilient Validation suites GREEN

---

### Session 48 — P1.2 Python 3.12 Restore + Tokenization Circular Import Fix
**PLANSET**: PLANSET-P12-048  
**Pre-conditions**: base-branch `copilot/sub-pr-3248` CI confirmed green  
**Agent Assignments**: `ci-testing-agent` v4.0 (P-CYCLIC pattern)

| Checkpoint | Target |
|------------|--------|
| CP-1: Verify base branch CI green via `list_workflow_runs(branch="copilot/sub-pr-3248")` | ≤ 5 min |
| CP-2: Extract `_types.py` / `_protocols.py` from tokenization module | ≤ 30 min |
| CP-3: `pyproject.toml` `requires-python = ">=3.12"` restored | ≤ 5 min |
| CP-4: Smoke: `python -c "from codex_ml.tokenization.api import TokenizerAdapter"` | ≤ 2 min |

**Benchmarks**:
- BM-1: 0 circular import CodeQL alerts
- BM-2: All tokenization tests pass
- BM-3: `python_requires >= "3.12"` in pyproject.toml

---

### Session 49 — Extended Noise Validation (1000 scenarios) + Bayesian CPD Calibration
**PLANSET**: PLANSET-NOISE-049  
**Pre-conditions**: Session 48 complete  
**Agent Assignments**: `cognitive-brain-manager`, `quantum-compliance-tuning-agent`

| Checkpoint | Target |
|------------|--------|
| CP-1: Run `exp1b_revalidation.py --scenarios 1000 --noise-rate 0.10` | ≤ 20 min |
| CP-2: Verify ≥ 90% accuracy at 10% gate error on 1000 scenarios | Pass/Fail |
| CP-3: `update_cpds_em()` calibrated against real compliance corpus | ≤ 20 min |

**Benchmarks**:
- BM-1: Accuracy ≥ 90% at noise_rate=0.10, n=1000
- BM-2: CPD entropy decreases after EM update (convergence verified)

---

### Session 50 — PyTorch 2.7+ Skipif Guard Removal + datetime.now(UTC) Modernization
**PLANSET**: PLANSET-TORCH-050  
**Pre-conditions**: PyTorch 2.7+ available in CI environment  
**Agent Assignments**: `datetime-modernizer`, `ci-testing-agent` v4.0

| Checkpoint | Target |
|------------|--------|
| CP-1: Check if torch.__version__.startswith("2.7") in CI | ≤ 2 min |
| CP-2: Remove all `_TORCH_312_BUG` skipif guards (if 2.7+) | ≤ 20 min |
| CP-3: Apply `datetime-modernizer` to all changed files | ≤ 20 min |

**Benchmarks**:
- BM-1: 0 `_TORCH_312_BUG` references in codebase (if torch 2.7+)
- BM-2: 0 `datetime.utcnow()` calls remaining (all converted to `datetime.now(UTC)`)

---

## 🤖 Agent Orchestration Protocol

### Trigger → Route → Grade → Report

```
┌──────────────────────────────────────────────────────────────┐
│  AGENT ORCHESTRATOR routing logic (use agent-orchestrator.md) │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  CI failure detected                                         │
│    → Classify error pattern (17 patterns in ci-testing-agent)│
│    → P0 (collection error, regression): immediate fix        │
│    → P1 (env dep, API drift): ci-testing-agent               │
│    → P2 (lint, artifact hygiene): codebase-health-guardian   │
│                                                              │
│  Grade output (0-100 rubric)                                │
│    → ≥ 90: auto-approve                                      │
│    → 70-89: recommend human review                           │
│    → < 70: send back (max 3 retries, then escalate)          │
│                                                              │
│  Feed outcome to cognitive brain                             │
│    → hook.record_if_uncertain(audit, assessment)             │
│    → update_cpds_em(corpus=[outcome]) if confident          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Agent Assignment Matrix

| Failure Category | Primary Agent | Secondary Agent | Max Iterations |
|----------------|---------------|-----------------|----------------|
| P0: Collection error (AttributeError, ImportError) | `ci-testing-agent` v4 | — | 2 |
| P1: API drift, missing export | `ci-testing-agent` v4 | `test-alignment-fixer` | 3 |
| P1: Optional dep missing (botocore, faiss) | `ci-testing-agent` v4 | — | 1 |
| P1: PyTorch 2.x+3.12 env bug | `ci-testing-agent` v4 | — | 1 |
| P1: HFModelUnavailableError | `ci-testing-agent` v4 | — | 1 |
| P2: ruff F401/I001 lint errors | `codebase-health-guardian` | — | 1 |
| P2: Stray .md files in root | `codebase-health-guardian` | — | 1 |
| P2: xfail policy violation | `codebase-health-guardian` | — | immediate block |
| P2: CodeQL alert (cyclic import) | `ci-testing-agent` v4 + P-CYCLIC | — | 2 |
| P3: Coverage drops > 2% | `coverage-roadmap-agent` | — | session-based |
| P3: Doc links broken | `doc-freshness-checker` | `link-validator-agent` | 1 |

---

## 🔧 GitHub MCP Integration Layer

### Expanded Capabilities (Session Startup Kit)

The following MCP functions MUST be used at every session start:

```python
# ── AWARENESS LAYER ────────────────────────────────────────────────

# 1. Current branch health
list_workflow_runs(branch=BRANCH, per_page=5)
list_workflow_jobs(run_id=LATEST_FAILED_RUN)
get_job_logs(job_id=FAILED_JOB, failed_only=True, tail_lines=200)

# 2. PR context (last 2 merged + all open)
list_pull_requests(state="closed", sort="updated", per_page=5)
list_pull_requests(state="open", per_page=20)

# 3. Commit archaeology (cherry-pick context from history)
list_commits(sha=BASE_BRANCH, per_page=10)
get_commit(sha=SPECIFIC_SHA, include_diff=True)
# → Restore overwritten file: examine diff, reconstruct original content

# 4. CodeQL and security
list_code_scanning_alerts(state="open")  # 0 high-severity required
list_secret_scanning_alerts(state="open")

# ── ACTION LAYER ────────────────────────────────────────────────────

# 5. Environment variable management (via GitHub REST API when needed)
# Note: Use secrets/variables via workflow dispatch, not direct API calls
# Pattern: Add to .github/workflows/set-env-vars.yml as workflow_dispatch

# 6. Trigger orchestration
# Trigger specific workflow via workflow_dispatch for manual runs
github-mcp-server-actions_list(method="list_workflows")  # find workflow ID
# → Use GitHub web UI or workflow_dispatch for triggering
```

### File Recovery Protocol (Cherry-Pick from History)

When a file is accidentally overwritten or deleted:

```python
# Step 1: Find the commit where the file was last correct
list_commits(sha=BRANCH, per_page=30)

# Step 2: Get the file content at that commit
get_commit(sha=LAST_GOOD_SHA, include_diff=True)
# → Extract the file content from the diff

# Step 3: Reconstruct the file locally
# edit() tool to apply the restored content

# Step 4: Verify
python -m py_compile <restored_file>
```

### Repository Environment Variables

Variables that agents may need to set/verify:

| Variable | Location | Purpose | Set By |
|----------|----------|---------|--------|
| `CODEX_ACTIVE_LEARNING` | GitHub Actions env | Enable AL queries | `agent-orchestrator` |
| `HF_REVISION` | GitHub Actions env | HuggingFace model pin | CI workflow |
| `CODEX_ARCHIVE_URL` | Repository secret | Archive backend | Human admin |
| `CI` | GitHub Actions built-in | Skip docker/network tests | Automatic |
| `PYTHONPATH` | CI workflow step | Module resolution | CI workflow |

**Pattern for adding env vars via workflow:**
```yaml
# .github/workflows/resilient-validation.yml
env:
  CODEX_ACTIVE_LEARNING: ${{ vars.CODEX_ACTIVE_LEARNING || 'false' }}
  CODEX_SESSION_LOG_DIR: .codex/sessions
```

---

## 🛡️ codebase-health-guardian Integration

`codebase-health-guardian` runs BEFORE every `report_progress` commit as a pre-commit gate:

### Pre-Commit Checklist (automated via guardian)

```
D1 — Workflow YAML:
[ ] No YAML syntax errors in .github/workflows/
[ ] No deprecated actions/checkout@v2

D2 — Python Quality:
[ ] ruff check --fix <changed_files> exits 0
[ ] python -m py_compile <changed_files> succeeds
[ ] import smoke: python -c "from <module> import <symbol>"

D3 — Test Policy:
[ ] No xfail(strict=False) without base-branch SHA
[ ] No new bare except: in test files
[ ] Skip guards use skipif or pytest.skip() with documented reason

D4 — Artifact Hygiene:
[ ] No new .md files in repo root (move to .codex/)
[ ] No FIXED_TESTS.txt, CI_FIXES*.md, TASK_SUMMARY.md in root
[ ] audit_artifacts/** in .gitignore
```

**Invocation pattern:**
```
@copilot Use codebase-health-guardian to validate all changed files before commit.
Enforce D1-D4. Auto-fix D2. Block if D3 violations. Report gate table.
```

---

## 📊 Grading Rubric (per Session)

| Criterion | Points | How to Measure |
|-----------|--------|----------------|
| **Failure reduction** | 40 | (failures_fixed / total_failures) × 40 |
| **No regressions** | 25 | 0 if any new failure introduced; 25 if none |
| **Policy compliance** | 20 | -5 per xfail violation, -5 per stray .md file |
| **Documentation** | 10 | Tracking log updated with Attempt NN + commit SHA |
| **Lint clean** | 5 | ruff exits 0 + import smoke passes |

**Session 47 target score: ≥ 90**  
**Minimum acceptable: ≥ 70 (human review), < 70 = retry**

---

## 🧠 Cognitive Brain Continual Improvement Loop

Each session outcome feeds back into the cognitive brain:

```python
# After each session completes:
from cognitive_brain.active_learning.hook import ActiveLearningHook
from cognitive_brain.analytics.bayesian import BayesianAssessor

hook = ActiveLearningHook(query_budget_per_day=50)
assessor = BayesianAssessor()

# Record session outcome for learning
hook.record_if_uncertain(
    audit={"session": SESSION_NN, "failures_fixed": N, "regressions": 0},
    assessment={"score": GRADE_SCORE, "policy_violations": 0}
)

# Update CPDs with session outcomes corpus
assessor.update_cpds_em(
    corpus=[session_outcome_dict],
    learning_rate=0.05  # Conservative update rate for production
)

# Store key facts for next session
store_memory(
    subject="CI failure patterns",
    fact=f"Session {SESSION_NN}: {N} failures fixed. Root causes: {patterns}",
    citations=f"Commit {COMMIT_SHA}, run {RUN_ID}",
    category="general"
)
```

---

## 📝 Session Status Template

Copy this template for each session cognitive brain status file:

**File**: `.codex/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR{PR}_SESSION{NN}_COMPLETE.md`

```markdown
# Cognitive Brain Status — PR #{PR} Session {NN} Complete
> Generated: {TIMESTAMP}

## Session Summary
- **Session**: {NN}
- **PR**: #{PR}
- **Branch**: {BRANCH}
- **Latest Commit**: {SHA}
- **Grade**: {SCORE}/100

## Failures Fixed: {N}/{TOTAL}
| Test | Error Type | Fix Applied | Pattern |
|------|-----------|-------------|---------|
| {test_id} | {error} | {fix} | {P-XX} |

## Policy Compliance
- xfail violations: 0 ✅
- stray .md files: 0 ✅
- ruff lint: PASS ✅

## Agent Assignments Used
- {agent}: {task_description} → Grade: {sub_score}

## Cognitive Brain Update
- CPD EM update: {applied/skipped}
- AL budget: {N}/{BUDGET} queries used today

## Next Session
- Session {NN+1} PLANSET: {PLANSET_NAME}
- Pre-conditions: {conditions}
- Primary agent: {agent}
```

---

## 🚨 Anti-Patterns (Never Do)

Per `.codex/CODEBASE_AGENCY_POLICY.md`:

| Anti-Pattern | Trigger | Consequence |
|-------------|---------|-------------|
| `xfail(strict=False)` without base-branch SHA | D3 policy violation | Blocked by guardian |
| "These failures are not from my changes" | Policy violation | Automatic citation |
| Fix only some failures and ignore rest | Policy violation | Score < 70 → retry |
| Commit stray `.md` files to root | D4 violation | Auto-moved by guardian |
| `pickle.load()` fallback after security fix | Security regression | CodeQL alert |
| `sys.exit(1)` for graceful degradation | P-CLI-EXIT regression | Breaks subprocess tests |

---

## 🔁 Follow-Up Prompt (for next session)

```
@copilot Use AGENTIC_SESSION_METHODOLOGY.md to execute Session {NN+1}.

MSP-1: Load memory, accountability reports, codebase agency policy, and this methodology.
MSP-2: Run list_workflow_runs(branch=CURRENT_BRANCH) to identify failing CI jobs.
MSP-3: Execute git log --oneline -10 and git status to understand current state.

PLANSET: {PLANSET_NAME}
Pre-conditions: {CONDITIONS}
Primary agent: {AGENT}
Exit criteria: All failing checks resolved.

Invoke agent-orchestrator to route failures to specialized agents.
Grade output on 0-100 rubric.
Use codebase-health-guardian as pre-commit gate (D1-D4).
Feed outcomes to cognitive brain via update_cpds_em().
```

---

## 📚 Reference Documents

| Document | Purpose |
|----------|---------|
| `.codex/CODEBASE_AGENCY_POLICY.md` | Prohibited patterns, mandatory policy |
| `.codex/ACCOUNTABILITY_REPORT_*.md` | Session lessons learned |
| `.codex/PRODUCTION_READINESS_CONSOLIDATION_MAP.md` | Full 6-phase journey map |
| `.codex/plans/TOP3_AGENT_ENHANCEMENT_PLANSETS.md` | Agent enhancement roadmap |
| `.codex/PR_3248_FAILURE_TRACKING_LOG.md` | Failure attempt audit trail |
| `.github/agents/agent-orchestrator.md` | Routing table + grading rubric |
| `.github/agents/ci-testing-agent.md` | 17 known fix patterns |
| `.github/agents/codebase-health-guardian.md` | D1-D4 health enforcement |
| `.codex/plans/AGENT_ECOSYSTEM_COGNITIVE_BRAIN_INTEGRATION_PLANSET.md` | E-01..E-12, M-01..M-05, DR-011..DR-016 |

---

## 🗓️ Session 57 PLANSET — OODA Formalization + Memory Persistence

> Context: Agent Ecosystem Master Synthesis ingested S56 (Comment #3938173408)

**Pre-conditions:**
- Commit `9528c3c` CodeQL/F401 fixes verified green in CI
- `ruff check` passes on all changed files
- `AGENT_ECOSYSTEM_COGNITIVE_BRAIN_INTEGRATION_PLANSET.md` committed ✅

**Primary Tasks (in order):**

| # | Task | File(s) | Physics | D1–D4 |
|---|------|---------|---------|-------|
| S57-1 | **E-01**: Add `Planner` ABC to `SelfHealingEngine` | `agents/self_healing.py` | Path 🛤️ | Mandatory |
| S57-2 | **E-01**: Add `Planner` ABC to `WorkflowNavigator` | `agents/workflow_navigator.py` | Path 🛤️ | Mandatory |
| S57-3 | **E-02**: Create `SQLiteMemory(MemoryInterface)` | `agents/sqlite_memory.py` (new) | Redundancy 🔀 | Mandatory |
| S57-4 | **E-06**: Wire `ReflectionLoop` → `AdaptiveScoringOptimizer` | `agents/physics_orchestrator.py` | Patterns 👁️ | Mandatory |
| S57-5 | **A1**: Pin ruff version in `requirements/dev.txt` + all CI workflows | CI config files | Balance ⚖️ | D1 only |
| S57-6 | **E-11**: `datetime.now(UTC)` pass on `agents/*.py` files | All `agents/*.py` | Balance ⚖️ | D1 only |
| S57-7 | CI verify: confirm `9528c3c` tests green (Art_RAG + Auto-Fix + CodeQL) | GitHub MCP monitor | — | MSP-2 |

**Exit criteria:**
- All 7 tasks complete
- `pytest tests/agents/ -q --timeout=60` passes
- Grade ≥ 85/100

**Agent Routing:**
- E-01/E-02: `ci-testing-agent` (validation after changes)
- E-06: `test-alignment-fixer` (update test expectations for new feedback loop)
- A1: `workflow-ci-fixer` (CI workflow ruff pin)
- E-11: `datetime-modernizer` (automated datetime pass)

---

## 🗓️ Session 58 PLANSET — Agent Merges + k₁ + GitHub API

**Pre-conditions:** Session 57 all tasks green

**Primary Tasks:**

| # | Task | Files | Physics |
|---|------|-------|---------|
| S58-1 | **E-03**: k₁ weight refinement (Phase 8.0) | `adaptive_scoring.py` | Balance ⚖️ |
| S58-2 | **M-01**: `unified-security-scanner` agent spec + workflow | `.github/agents/`, `.github/workflows/` | Balance ⚖️ |
| S58-3 | **M-02**: `unified-doc-agent` spec | `.github/agents/` | Patterns 👁️ |
| S58-4 | **M-03**: `ci-triage-pipeline-agent` spec | `.github/agents/` | Path 🛤️ |
| S58-5 | **E-04**: Complete `_github_api_post_review()` in guru agent | `.github/agents/github-guru-agent/` | Fields 🔄 |
| S58-6 | **A3**: `session_reviewer.py` for GitHub Guru Agent | `.github/agents/github-guru-agent/` | Patterns 👁️ |
| S58-7 | Update `AGENT_REGISTRY.yaml` — mark 12 agents deprecated (M-01..M-03 merge) | `.github/agents/AGENT_REGISTRY.yaml` | — |

**Exit criteria:** All 7 tasks complete + `pytest .github/agents/github-guru-agent/tests/ -q` passes with ≥115 tests
