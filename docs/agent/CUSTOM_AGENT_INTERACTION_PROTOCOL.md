# Multi-Agent Interaction Protocol Guide

> **Document:** Multi-Agent Interaction & Handoff Protocol  
> **Version:** 1.0.0  
> **Generated:** 2026-06-26  
> **Purpose:** Define standards for agent-to-agent communication, state handoff, and delegation workflows  

---

## Table of Contents

1. [Protocol Overview](#protocol-overview)
2. [Agent Lifecycle States](#agent-lifecycle-states)
3. [Communication Channels](#communication-channels)
4. [Handoff Protocol](#handoff-protocol)
5. [Result Verification](#result-verification)
6. [Error Handling & Escalation](#error-handling--escalation)
7. [State Machine Diagrams](#state-machine-diagrams)

---

## Protocol Overview

### Design Principles

1. **Stateless Communication** — Each agent receives complete context; no implicit shared state
2. **Explicit Handoff** — All work transitions are documented with results
3. **Result Verification** — Delegating agent validates returned results before using
4. **Graceful Degradation** — Failure in one agent doesn't cascade to others in parallel execution
5. **Audit Trail** — All interactions logged for accountability and replay

### Communication Flow

```
Delegating Agent (Primary)
    ↓
[Package Task Context] ← All needed info (scope, constraints, reference data)
    ↓
[Select Target Agent(s)] ← From capability matching
    ↓
[Issue Delegation] ← Send task with structured metadata
    ↓
Target Agent(s) (Specialist)
    ├→ [Receive & Parse] ← Validate task specification
    ├→ [Execute] ← Do the work
    ├→ [Produce Results] ← Structured output
    └→ [Signal Completion] ← Status + results to primary
    ↓
[Verify Results] ← Delegating agent validates
    ↓
[Handle Result] ← Integrate or escalate
```

---

## Agent Lifecycle States

### State Definitions

```
┌─────────────────────────────────────────────────┐
│ IDLE                                            │
│ Agent ready, no work assigned                   │
│ (memory state: task_queue = empty)              │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ RECEIVING                                       │
│ Accepting task delegation                       │
│ (memory state: task_context being captured)     │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ VALIDATING                                      │
│ Checking task specification and prerequisites   │
│ (memory state: capability_match assessment)     │
└─────────────────────────────────────────────────┘
        ↓ (if invalid) → ESCALATING
        ↓ (if valid)
┌─────────────────────────────────────────────────┐
│ EXECUTING                                       │
│ Performing assigned work                        │
│ (memory state: progress tracking)               │
└─────────────────────────────────────────────────┘
        ↓ (if success)
┌─────────────────────────────────────────────────┐
│ VERIFYING                                       │
│ Self-checking results before handoff            │
│ (memory state: validation results)              │
└─────────────────────────────────────────────────┘
        ↓ (if verified)
┌─────────────────────────────────────────────────┐
│ RETURNING                                       │
│ Returning results to delegating agent           │
│ (memory state: return_payload prepared)         │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ IDLE (again)                                    │
│ Ready for next task                             │
│ (memory state: results archived)                │
└─────────────────────────────────────────────────┘

Exceptional paths:
  EXECUTING → ESCALATING (blocker found)
           → FAILING (capability mismatch)
  VALIDATING → ESCALATING (prerequisites missing)
```

### State Transition Rules

| From | To | Condition | Action |
|------|----|-----------| -------|
| IDLE | RECEIVING | New task delegated | Load task context |
| RECEIVING | VALIDATING | Task parsed | Validate prerequisites |
| VALIDATING | EXECUTING | Validation passes | Begin work |
| VALIDATING | ESCALATING | Validation fails | Escalate with reason |
| EXECUTING | VERIFYING | Work completes | Run self-checks |
| EXECUTING | ESCALATING | Blocker found | Signal error |
| VERIFYING | RETURNING | Verification passes | Prepare results |
| VERIFYING | EXECUTING | Issue found | Attempt fix/retry |
| RETURNING | IDLE | Results sent | Clear task context |

---

## Communication Channels

### Channel 1: Task Delegation (Delegator → Target)

**Structure:**

```json
{
  "delegation": {
    "delegating_agent": "primary-agent-id",
    "target_agents": ["specialist-agent-1", "specialist-agent-2"],
    "task_id": "unique-uuid",
    "timestamp": "2026-06-26T18:30:00Z",
    "task": {
      "type": "fix|analyze|verify|generate",
      "domain": "ci-cd|testing|documentation|security|config",
      "scope": "description of what needs to be done",
      "constraints": {
        "time_limit": "seconds",
        "parallelizable": true,
        "blocking_precedence": 0
      }
    },
    "context": {
      "files_involved": ["path1", "path2"],
      "prior_results": {},
      "reference_data": {}
    },
    "success_criteria": [
      "criterion 1",
      "criterion 2"
    ]
  }
}
```

**Example:**

```json
{
  "delegation": {
    "delegating_agent": "unified-coverage-agent",
    "target_agents": ["autonomous-test-healer-agent"],
    "task_id": "task-20260626-001",
    "timestamp": "2026-06-26T18:30:00Z",
    "task": {
      "type": "fix",
      "domain": "testing",
      "scope": "Fix failing tests in tests/monitoring/",
      "constraints": {
        "time_limit": 1800,
        "parallelizable": true,
        "blocking_precedence": 0
      }
    },
    "context": {
      "files_involved": [
        "tests/monitoring/test_*.py"
      ],
      "prior_results": {
        "test_count": 42,
        "failing_count": 7,
        "failure_types": ["import_error", "assertion_failure"]
      },
      "reference_data": {
        "recent_changes": "commit abc123",
        "baseline_passing_count": 42
      }
    },
    "success_criteria": [
      "All 42 tests passing",
      "Coverage >= 90%",
      "No flaky failures"
    ]
  }
}
```

---

### Channel 2: Result Return (Target → Delegator)

**Structure:**

```json
{
  "result": {
    "task_id": "unique-uuid",
    "target_agent": "specialist-agent-id",
    "timestamp": "2026-06-26T18:45:00Z",
    "status": "success|partial|failure",
    "execution_time_seconds": 900,
    "outcome": {
      "type": "fix|analysis|verification|generation",
      "summary": "Brief summary of what was done",
      "details": "Detailed findings/changes"
    },
    "changes": {
      "files_modified": ["path1", "path2"],
      "lines_changed": 150,
      "commits": ["sha1", "sha2"]
    },
    "metrics": {
      "before": { "passing_tests": 35, "coverage": 0.85 },
      "after": { "passing_tests": 42, "coverage": 0.92 },
      "improvement": {
        "tests_fixed": 7,
        "coverage_gain": 0.07
      }
    },
    "verification": {
      "passed_all_criteria": true,
      "criteria_results": {
        "criterion_1": true,
        "criterion_2": true
      }
    },
    "next_steps": [
      "Manual review of failing test X",
      "Consider refactoring test suite Y"
    ]
  }
}
```

---

### Channel 3: Status Updates (During Execution)

**Asynchronous progress signals** (for long-running tasks):

```json
{
  "status_update": {
    "task_id": "unique-uuid",
    "target_agent": "specialist-agent-id",
    "timestamp": "2026-06-26T18:35:00Z",
    "progress": {
      "phase": "EXECUTING",
      "percentage_complete": 45,
      "current_activity": "Analyzing test failures in module X",
      "estimated_remaining_seconds": 450
    },
    "interim_metrics": {
      "items_processed": 19,
      "items_total": 42,
      "errors_encountered": 0
    }
  }
}
```

---

## Handoff Protocol

### Single-Agent Handoff (Sequential)

**Scenario:** Agent A completes work, Agent B continues from results.

```
Agent A (Primary)
    ↓
[Execute] → [Result: modified files, analysis]
    ↓
[Package State]
    - What was done
    - What changed
    - What's ready for next step
    - What still needs work
    ↓
[Delegate to Agent B]
    ← Task: "Continue from Agent A results"
    ← Context: Previous state included
    ↓
Agent B (Specialist)
    ↓
[Receive State] → Validate input from A
    ↓
[Continue Work] → Pick up where A left off
    ↓
[Return Results] → New state to A
```

**Example: CI Failure Triage**

```
1. ci-testing-agent (diagnoses: "Timeout in test_x.py:142")
   ↓ returns diagnosis + logs
2. autonomous-test-healer-agent (receives diagnosis)
   ↓ attempts fix based on known patterns
   ↓ returns fixed tests
3. ci-testing-agent validates fixes
   ↓ all tests pass
```

---

### Parallel Handoff (Concurrent)

**Scenario:** Multiple agents work in parallel on independent tasks.

```
Primary Agent
    ├→ [Delegate to Agent A] → Independent task A
    ├→ [Delegate to Agent B] → Independent task B
    └→ [Delegate to Agent C] → Independent task C
    ↓
    ├→ Agent A: [Execute] → [Return Result A]
    ├→ Agent B: [Execute] → [Return Result B]
    └→ Agent C: [Execute] → [Return Result C]
    ↓
Primary Agent
    ├→ [Collect Result A]
    ├→ [Collect Result B]
    ├→ [Collect Result C]
    ↓
    [Merge Results] → Consolidated outcome
    ↓
    [Verify No Conflicts] → Validate consistency
    ↓
    [Return Unified Result]
```

**Example: Multi-Domain Testing Audit**

```
unified-coverage-agent delegates:
├→ autonomous-test-healer-agent: Fix failing tests
├→ fragile-test-guardian: Stabilize flaky tests
└→ test-enhancement-agent: Add edge cases

All 3 work in parallel.

Results merged:
- Tests fixed: 7
- Tests stabilized: 3
- Edge cases added: 12
```

---

### Cascading Handoff (Dependent Sequential)

**Scenario:** Agent B depends on Agent A's output.

```
Agent A (must complete first)
    ↓
[Execute] → [Result: structured output]
    ↓
[Validate Result] → Check success criteria
    ↓ (if failed)
    └→ [Escalate] → Don't pass bad output to B
    ↓ (if passed)
    [Package for Agent B]
    ↓
[Delegate to Agent B] → "Here are A's results, continue"
    ↓
Agent B (dependent)
    ↓
[Receive A's Results] → Import into task context
    ↓
[Execute] → Do work based on A's output
    ↓
[Return Results]
```

**Example: Config Migration → Validation**

```
1. config-migration-assistant
   ↓ migrates legacy config to Hydra
   ↓ returns: migrated config files

2. config-validator (receives migrated files)
   ↓ validates Hydra format correctness
   ↓ returns: validation report + any needed fixes
```

---

## Result Verification

### Verification Checklist

Every agent should verify results before returning:

```
✓ Type Check
  - Result matches declared type (fix|analysis|verification)
  - Data structures well-formed

✓ Completeness Check
  - All success criteria addressed
  - No partial work without explanation
  - Changes documented

✓ Consistency Check
  - No conflicting changes
  - Logical coherence maintained
  - References up-to-date

✓ Quality Check
  - Code/docs follow style guide
  - No regressions introduced
  - Performance acceptable

✓ Audit Trail Check
  - Changes tracked with commit SHAs
  - Rationale documented
  - Timestamps accurate
```

### Self-Verification Pattern

```python
# Pseudo-code for agent verification
def verify_results(results, success_criteria):
    checks = {
        'type_valid': isinstance(results, expected_type),
        'completeness': all(
            criterion in results for criterion in success_criteria
        ),
        'consistency': validate_consistency(results),
        'quality': validate_quality(results),
        'audit_trail': all(
            commit_sha in results.get('commits', [])
            for commit_sha in results.get('applied_shas', [])
        )
    }

    if all(checks.values()):
        return {'status': 'VERIFIED', 'checks': checks}
    else:
        return {'status': 'FAILED', 'checks': checks, 'issues': [
            reason for reason, passed in checks.items() if not passed
        ]}
```

---

## Error Handling & Escalation

### Error Classification

| Error Type | Severity | Handler | Action |
|------------|----------|---------|--------|
| **Capability Mismatch** | HIGH | Delegator | Reselect agent |
| **Prerequisite Missing** | HIGH | Delegator | Address prerequisite, retry |
| **Task Specification Invalid** | MEDIUM | Target | Request clarification |
| **Execution Blocker** | MEDIUM | Target | Escalate, suggest workaround |
| **Partial Failure** | LOW | Target | Return partial + status |
| **Timeout** | MEDIUM | Delegator | Retry or escalate |
| **Resource Exhausted** | HIGH | Delegator | Queue or reroute |

### Escalation Path

```
Agent encounters issue
    ↓
[Can I fix this?]
    ├→ YES: Self-correct and continue
    ├→ NO, temporary: Retry with backoff
    ├→ NO, permanent: Request clarification from delegator
    ├→ NO, blocker: Escalate to orchestrator
    └→ NO, critical: Signal human escalation
    ↓
Delegator receives escalation
    ↓
[Can I resolve this?]
    ├→ YES: Provide clarification/fix to agent
    ├→ NO: Pass to orchestrator
    └→ CRITICAL: Signal human admin
```

### Escalation Signal Format

```json
{
  "escalation": {
    "task_id": "unique-uuid",
    "source_agent": "specialist-agent-id",
    "timestamp": "2026-06-26T18:45:00Z",
    "severity": "low|medium|high|critical",
    "issue_type": "capability_mismatch|blocker|timeout|resource_exhausted",
    "description": "What went wrong",
    "context": {
      "files_involved": [],
      "last_successful_state": {},
      "error_logs": ""
    },
    "recommended_action": "Retry|Reselect|Clarify|Escalate",
    "can_retry": true,
    "retry_backoff_seconds": 60
  }
}
```

---

## State Machine Diagrams

### Single Agent Workflow

```
     ┌─────┐
     │IDLE │◄────────────┐
     └──┬──┘             │
        │ task          │
        │ delegated     │
        ▼                │
  ┌──────────┐           │
  │RECEIVING │           │
  └──┬───────┘           │
     │                   │
     ├─ invalid ──┐      │
     │            ▼      │
     │      ┌──────────┐ │
     │      │ESCALATING│ │
     │      └──────────┘ │
     │                   │
     ├─ valid            │
     ▼                   │
┌──────────┐             │
│VALIDATING│             │
└──┬───────┘             │
   │ valid               │
   ▼                     │
┌──────────┐             │
│EXECUTING │             │
└──┬───────┘             │
   │ complete            │
   ▼                     │
┌──────────┐             │
│VERIFYING │             │
└──┬───────┘             │
   │ verified            │
   ▼                     │
┌──────────┐             │
│RETURNING │─────────────┘
└──────────┘
```

### Parallel Agent Workflow

```
        Delegator
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
  Agent1 Agent2 Agent3
   EXE    EXE    EXE
    │      │      │
    └──────┼──────┘
           │
      [Merge Results]
           │
      [Verify Consistency]
           │
    Return to Delegator
```

### Cascading Agent Workflow

```
   Agent-A
      │
      ├─ EXECUTING
      │
      ├─ VERIFYING
      │
      ├─ RETURNING
      │
      ▼ (A's output)

   Delegator
      │
      ├─ [Validate A's output]
      │
      ├─ [Package for B]
      │
      ▼ (dispatch B)

   Agent-B
      │
      ├─ RECEIVING (gets A's output)
      │
      ├─ EXECUTING (with A's context)
      │
      ├─ VERIFYING
      │
      ├─ RETURNING
      │
      ▼

   Delegator
      │
      └─ [Merge final results]
```

---

## See Also

- [Custom Agent Selection Framework](./CUSTOM_AGENT_SELECTION_FRAMEWORK.md)
- [Agent Workflow Coordination](./CUSTOM_AGENT_COORDINATION_WORKFLOWS.md)
- [Repeatable Processes](./CUSTOM_AGENT_REPEATABLE_PROCESSES.md)
- [AGENT_REGISTRY.yaml](../../.github/agents/AGENT_REGISTRY.yaml)
