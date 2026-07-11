# 🎯 Multi-Agent Campaign Toolkit: Three Core Patterns

This document demonstrates three mission-critical patterns for reliable multi-agent campaign execution: **Checkpoint Lifecycle**, **Pre-Campaign Analysis**, and **Structured Campaign Planning**.

---

## Pattern 1: Checkpoint Lifecycle Integration 🔄

### Overview

Checkpoints transform campaigns from single-execution units into **resumable, observable workflows** where work can be tracked, interrupted, and resumed without loss of state.

### Implementation

#### Phase 1: Campaign Start Checkpoint
```bash
# At campaign launch, create an entry checkpoint
/checkpoint create \
  --title "Repository Consolidation Campaign - Phase 1 Discovery" \
  --tags stage=discovery,campaign=repo-consolidation,lanes=5 \
  --description "Initial scan of repository structure, identify duplicates and consolidation targets"
```

**Checkpoint captures**:
- Repository state snapshot (branch, commit, uncommitted changes)
- Campaign metadata (lanes, estimated duration)
- Baseline metrics (file count, folder structure)

#### Phase 2: Lane Execution Checkpoints
After each lane completes, create a lane-specific checkpoint:

```bash
# After Lane 1 (Security validation) completes
/checkpoint create \
  --title "Repository Consolidation Campaign - Lane 1 Complete: Security" \
  --tags stage=execution,lane=1,status=complete,campaign=repo-consolidation \
  --description "Lane 1 completed: 48 files scanned, 0 secrets detected, all security checks passed"
```

#### Phase 3: Campaign Completion Checkpoint
```bash
# After all lanes merge back to main
/checkpoint create \
  --title "Repository Consolidation Campaign - Phase 3 Complete: Integration" \
  --tags stage=completion,campaign=repo-consolidation,status=ready-for-release \
  --description "All lanes validated, merged, tested. Ready for production deployment."
```

### Usage Pattern

```yaml
# Checkpoint-driven session resume workflow
1. Query checkpoint history: /checkpoint list --campaign repo-consolidation
2. Extract last successful checkpoint state
3. Resume session: /resume <session-id> --from-checkpoint <checkpoint-id>
4. Continue multi-agent execution with preserved context
5. Create completion checkpoint when done
```

### Benefits

| Feature | Benefit |
|---------|---------|
| **Interruption Safety** | Stop campaign at any point, resume without repeating completed work |
| **Observability** | Track progress across 5-10 parallel lanes in shared checkpoint history |
| **Error Recovery** | On failure, roll back to last good checkpoint and re-execute lane |
| **Stakeholder Visibility** | Each checkpoint is auditable evidence of work completion |
| **Knowledge Preservation** | Checkpoints capture metrics, findings, and lane recommendations |

---

## Pattern 2: Pre-Campaign Analysis (Chronicle Improve + Cost-Tips) 📊

### Overview

Before executing a multi-lane campaign, run analysis to:
1. **Discover** optimization opportunities (chronicle improve)
2. **Estimate** cost/benefit tradeoffs (chronicle cost-tips)
3. **Allocate** lanes and agents intelligently

### Implementation

#### Step 1: Discovery Analysis
```bash
# Run comprehensive codebase analysis
/chronicle improve \
  --focus repository-structure \
  --scope full-codebase \
  --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_IMPROVE.json
```

**Output includes**:
- 25+ improvement opportunities (grouped by priority tier)
- Effort estimates (hours, complexity)
- Impact scores (maintainability, test coverage, security)
- Agent owner recommendations

#### Step 2: Cost-Benefit Analysis
```bash
# Analyze cost/benefit of proposed improvements
/chronicle cost-tips \
  --target-reduction 30% \
  --metrics build-time,lint-time,test-time \
  --scope repository-consolidation \
  --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_COST.json
```

**Output includes**:
- Estimated time savings per optimization
- Resource utilization impact
- Parallelization opportunities
- Risk assessment for each lane

#### Step 3: Build Lane Allocation Matrix

From analysis results, create decision matrix:

```json
{
  "lanes": [
    {
      "lane_id": 1,
      "agent": "unified-security-scanner",
      "focus": "Security validation",
      "from_improve": "Security Hardening (Tier 1)",
      "from_cost_tips": "Zero security regressions (high priority)",
      "parallelizable": true,
      "estimated_duration": "15 min"
    },
    {
      "lane_id": 2,
      "agent": "unified-coverage-agent",
      "focus": "Test coverage expansion",
      "from_improve": "Test Coverage Expansion (Tier 1, CRITICAL)",
      "from_cost_tips": "Time saved: 2+ hours per build cycle",
      "parallelizable": true,
      "estimated_duration": "45 min"
    },
    {
      "lane_id": 3,
      "agent": "test-pattern-guardian",
      "focus": "Fragile test stabilization",
      "from_improve": "Fix Fragile Tests (Tier 1, CRITICAL)",
      "from_cost_tips": "Stabilize CI (reduce flaky failures by 95%)",
      "parallelizable": true,
      "estimated_duration": "20 min"
    },
    {
      "lane_id": 4,
      "agent": "code-analysis-agent",
      "focus": "Reduce code complexity",
      "from_improve": "Reduce Code Complexity (Tier 1, CRITICAL)",
      "from_cost_tips": "Improve maintainability, reduce bugs 20-30%",
      "parallelizable": true,
      "estimated_duration": "60 min"
    },
    {
      "lane_id": 5,
      "agent": "documentation-consolidator",
      "focus": "Consolidate duplicate documentation",
      "from_improve": "Documentation Deduplication (Tier 2)",
      "from_cost_tips": "Reduce doc maintenance overhead by 25%",
      "parallelizable": true,
      "estimated_duration": "30 min"
    }
  ],
  "total_estimated_duration_serial": "170 min",
  "total_estimated_duration_parallel": "60 min",
  "parallelization_efficiency": "65%"
}
```

### Key Insights

- **Chronicle Improve** → **What to fix** (prioritized by impact)
- **Chronicle Cost-Tips** → **Why to fix now** (time/resource gains)
- **Combined** → **How to allocate lanes** (maximize parallelism + impact)

---

## Pattern 3: Structured Campaign Planning (/plan campaign) 📋

### Overview

`/plan campaign` generates a detailed, executable multi-lane plan with:
- Task decomposition
- Dependency graphs
- Agent lane assignments
- Error handling strategies
- Validation checkpoints

### Implementation

#### Command
```bash
/plan campaign \
  --name repository-consolidation \
  --description "Remove duplicate folders, consolidate docs, validate links, stabilize tests" \
  --lanes 5 \
  --estimate-duration 90 \
  --validate-links true \
  --from-analysis /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_IMPROVE.json \
  --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_PLAN_EXECUTABLE.md
```

#### Output Structure

```markdown
# Campaign Plan: Repository Consolidation

## Executive Summary
- **Duration**: 90 min (parallel) vs 170 min (serial) = 47% efficiency gain
- **Lanes**: 5 parallel agents
- **Risk Level**: LOW (all lanes independent, no blocking dependencies)
- **Rollback Strategy**: Checkpoint-based (revert to Phase 1 on lane failure)

## Phase 1: Pre-Execution (5 min)
- [ ] Create campaign entry checkpoint
- [ ] Verify all lane prerequisites (agents available, no conflicts)
- [ ] Snapshot repository state

## Phase 2: Parallel Lane Execution (60 min)
### Lane 1: Security Validation (15 min)
- **Agent**: unified-security-scanner
- **Tasks**:
  1. Scan for secrets in consolidated files
  2. Verify no regressions in security checks
  3. Validate OWASP Top 10 compliance
- **Success Criteria**: Zero secrets detected, all checks pass
- **On Failure**: Rollback changes from this lane only, create error checkpoint

### Lane 2: Test Coverage Expansion (45 min)
- **Agent**: unified-coverage-agent
- **Tasks**:
  1. Identify low-coverage modules in consolidated structure
  2. Generate gap-filling tests
  3. Validate coverage > 80% in critical paths
- **Success Criteria**: Coverage improved by 15%+ (59.7% → 75%+)
- **On Failure**: Mark as needs-review, escalate for secondary iteration

### Lane 3: Test Stabilization (20 min)
- **Agent**: autonomous-test-healer-agent
- **Tasks**:
  1. Detect fragile tests in consolidated modules
  2. Apply stabilization patterns (seed control, barriers)
  3. Re-run to verify no flakiness
- **Success Criteria**: All 6 identified fragile tests now stable
- **On Failure**: Create detailed analysis checkpoint for manual review

### Lane 4: Code Complexity Reduction (60 min)
- **Agent**: code-analysis-agent
- **Tasks**:
  1. Identify functions with cyclomatic complexity > 20
  2. Extract methods and refactor using Strategy pattern
  3. Run mypy to verify no type regressions
- **Success Criteria**: Max complexity reduced from 31 → 18
- **On Failure**: Partial credit for completed refactorings, defer rest to Phase 2

### Lane 5: Documentation Consolidation (30 min)
- **Agent**: documentation-consolidator
- **Tasks**:
  1. Identify duplicate docs (same title, similar content)
  2. Merge into canonical version with cross-references
  3. Update all broken links
- **Success Criteria**: 100% link health, zero duplicate pages
- **On Failure**: Create link validation checkpoint, retry

## Phase 3: Integration & Validation (20 min)
- [ ] Merge all lane changes into main branch
- [ ] Run full test suite (CI gate)
- [ ] Verify no regressions in production-critical paths
- [ ] Create campaign completion checkpoint

## Phase 4: Post-Campaign (5 min)
- [ ] Generate campaign summary report
- [ ] Archive checkpoints for audit trail
- [ ] Notify stakeholders of completion

## Error Handling Strategy

| Scenario | Lane | Action |
|----------|------|--------|
| Security failures | Lane 1 | Halt entire campaign, escalate |
| Coverage goals missed | Lane 2 | Continue, mark for follow-up |
| Test flakiness persists | Lane 3 | Create detailed analysis, defer |
| Refactoring incomplete | Lane 4 | Accept partial progress, schedule Phase 2 |
| Link validation fails | Lane 5 | Retry with `autonomous-test-healer-agent` |

## Dependency Graph

```
Phase 1 Start
    ↓
┌───────────────────────────────────────┐
│   Phase 2: Parallel Lane Execution    │ (60 min)
│ ┌─────────────────────────────────┐   │
│ │ Lane 1: Security (15 min)       │   │
│ │ Lane 2: Coverage (45 min)       │   │
│ │ Lane 3: Test Stability (20 min) │   │
│ │ Lane 4: Complexity (60 min)     │   │
│ │ Lane 5: Docs (30 min)           │   │
│ └─────────────────────────────────┘   │
└───────────────────────────────────────┘
    ↓
Phase 3: Integration (20 min)
    ↓
Phase 4: Reporting (5 min)
```

## Delegation to Task Agent

```bash
# Execute entire campaign with orchestrator-agent managing all lanes
task orchestrator-agent \
  --name "repository-consolidation-campaign" \
  --prompt "Execute the campaign plan at /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_PLAN_EXECUTABLE.md using the following lane agents in parallel mode: unified-security-scanner, unified-coverage-agent, autonomous-test-healer-agent, code-analysis-agent, documentation-consolidator. Monitor completion and aggregate results." \
  --mode background \
  --max-retries 2 \
  --on_failure "escalate_and_report"
```

---

## Integration: Three Patterns Together 🔗

### Workflow

```
1. PRE-CAMPAIGN ANALYSIS (10 min)
   ├─ /chronicle improve → Discover opportunities
   ├─ /chronicle cost-tips → Estimate time savings
   └─ Build lane allocation matrix

2. CAMPAIGN PLANNING (5 min)
   └─ /plan campaign → Generate executable plan

3. CAMPAIGN EXECUTION (90 min)
   ├─ /checkpoint create → Entry checkpoint
   ├─ Dispatch 5 lanes in parallel via orchestrator-agent
   ├─ Monitor lane completion (checkpoint updates)
   ├─ Handle errors with rollback to last checkpoint
   └─ /checkpoint create → Completion checkpoint

4. POST-CAMPAIGN VALIDATION (10 min)
   ├─ Merge lane results
   ├─ Run full CI gate
   └─ Archive checkpoints
```

### Success Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| **Plan Accuracy** | All 5 lanes complete within ±10% of estimate | Duration logs |
| **Checkpoint Coverage** | Entry + 5 lane + completion = 7 checkpoints | Checkpoint history |
| **Lane Independence** | Zero blocking dependencies, all parallel | Execution timeline |
| **Error Recovery** | 100% of lane failures caught + reported | Error checkpoint history |
| **Results Quality** | All success criteria met | Integration validation |

---

## Quick Start: Repository Consolidation Campaign

### Step 1: Analyze (10 min)
```bash
/chronicle improve --focus repository-structure --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_IMPROVE.json
/chronicle cost-tips --target-reduction 30% --metrics build-time,lint-time --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_COST.json
```

### Step 2: Plan (5 min)
```bash
/plan campaign \
  --name repository-consolidation \
  --lanes 5 \
  --from-analysis /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_ANALYSIS_IMPROVE.json \
  --output /home/runner/work/_codex_/_codex_/.codex/CAMPAIGN_PLAN_EXECUTABLE.md
```

### Step 3: Execute (90 min)
```bash
/checkpoint create --title "Repo Consolidation - Entry" --tags stage=start,campaign=repo-consolidation

task orchestrator-agent \
  --name "repository-consolidation" \
  --prompt "Execute campaign plan" \
  --mode background

# Monitor checkpoints as lanes complete
/checkpoint list --campaign repository-consolidation
```

### Step 4: Validate (10 min)
- CI gates pass
- All checkpoints logged
- Archive for audit trail

---

## References

- **Checkpoint Documentation**: `.codex/docs/CHECKPOINT_MANAGER.md`
- **Chronicle Commands**: `.codex/CHRONICLE_TIPS_USAGE_GUIDE.md`
- **Campaign Architecture**: `.codex/PHASE_14_MASTER_ORCHESTRATION_BRIEF.md`
- **Multi-Agent Patterns**: `.codex/MULTI_AGENT_ORCHESTRATION_PATTERNS.md`

---

**Author**: Copilot Campaign Toolkit  
**Last Updated**: 2026-07-11T01:33:00Z  
**Version**: 1.0.0
