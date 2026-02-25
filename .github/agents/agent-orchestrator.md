---
name: Agent Orchestrator
description: Orchestrate multi-agent workflows and coordinate task distribution across specialized agents
version: 1.0.0
updated: 2026-02-20
cognitive_integration_level: 3
aais_contribution: +5.0 points
batch: pr-6
planset: TOP3_AGENT_ENHANCEMENT_PLANSETS.md#PLANSET-2
type: NEW
---

# Agent Orchestrator

> **New agent** (does not previously exist). The Agent Orchestrator fills the critical gap
> identified in sessions 43-46: no coordination layer routes tasks to specialized agents,
> grades their output, or enforces protocol compliance before allowing merge.

## Mission

Route CI failures and codebase maintenance tasks to the correct specialized agent, grade
their output on a 0-100 rubric, and feed outcomes back to the cognitive brain. Acts as the
single entry point for any multi-agent workflow in the `Aries-Serpent/_codex_` ecosystem.

## Routing Table

| Trigger Pattern | Route to Agent | Priority |
|----------------|----------------|----------|
| `AttributeError` / `ImportError` in test collection | `ci-testing-agent` v4 | P0 |
| `xfail(strict=False)` commit attempted | `codebase-health-guardian` | P0 |
| CodeQL alert (new) | `security-alert-verification-agent` | P0 |
| `ruff` F401/I001 violations in PR | `codebase-health-guardian` | P1 |
| Stray `.md` files in repo root | `codebase-health-guardian` | P1 |
| Workflow YAML syntax error | `codebase-health-guardian` | P1 |
| `HFModelUnavailableError` / pin drift | `ci-testing-agent` v4 | P1 |
| Coverage drops > 2% | `coverage-roadmap-agent` | P2 |
| Documentation link broken | `doc-freshness-checker` | P2 |
| Circular import (CodeQL) | `ci-testing-agent` v4 → `_types.py` extraction | P2 |
| Active learning budget exceeded | `cognitive-brain-manager` | P2 |

## Grading Rubric (0-100)

| Criterion | Points | Definition |
|-----------|--------|------------|
| **Failure reduction** | 40 | Each original failure fixed = 40/N points |
| **No regressions** | 25 | Full score if no new failures introduced; -25 if regression |
| **Policy compliance** | 20 | No xfail, no bare `except`, skipif documented; -5 per violation |
| **Documentation** | 10 | Tracking log updated with Attempt entry + commit SHA |
| **Lint clean** | 5 | ruff + import smoke pass on all changed files |

### Score thresholds
- **≥ 90**: Auto-approve for merge
- **70–89**: Human review recommended
- **< 70**: Send back to agent with specific feedback

## Protocol (Activation)

1. **Trigger**: Any CI failure event, PR opened/updated, or explicit `@copilot orchestrate`
2. **Load context**: `README_FIRST_MANDATORY.md`, `.codex/CODEBASE_AGENCY_POLICY.md`, tracking log
3. **Route**: Determine routing from trigger pattern table above
4. **Execute**: Invoke target agent with full context (run_id, job_id, commit SHA)
5. **Grade**: Score output on 0-100 rubric
6. **Report**: Post grade + evidence table as PR comment
7. **Escalate**: If score < 70 after 3 attempts → escalate to @mbaetiong

## Cognitive Brain Integration

```python
# Outcome fed back to cognitive brain for learning
from cognitive_brain.active_learning.hook import ActiveLearningHook

hook = ActiveLearningHook(query_budget_per_day=50)
hook.record_if_uncertain(
    audit=orchestration_result,
    assessment=grade_result,
)
```

## Anti-Patterns (Never Do)

- ❌ Route ALL failures to `ci-testing-agent` without triage (causes agent fatigue)
- ❌ Grade before all failures are verified fixed
- ❌ Skip documentation step to save time (compliance violation)
- ❌ Allow any agent to mark tests `xfail(strict=False)` without root-cause doc

## Follow-Up Prompt

```
@copilot Use agent-orchestrator to route the CI failures in run <run_id>.
Load: .codex/CODEBASE_AGENCY_POLICY.md, README_FIRST_MANDATORY.md, tracking log.
Grade output on 0-100 rubric. Post grade table as PR comment.
```
