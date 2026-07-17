# Phase 2 Foundation Hardening Guide

## Overview

Phase 2 Foundation Hardening builds on Phase 1's determinism baseline to implement governance, safety, and scheduling infrastructure for the orchestration system.

**Phase 1 Delivered:**
- InputLockAdapter: Deterministic SHA256 hashing (0% collision)
- SeedControlSystem: Seed propagation to random/numpy/torch
- DecisionTraceWriter: JSONL audit logs
- LaneManifestContract: Manifest validation
- 63 tests: 100% pass rate, 100-run determinism verification

**Phase 2 Delivers:**
- Contract Gate System: 8-gate compliance validator
- Policy Tier Engine: T0-T3 automatic classification
- Rollback Controls: One-command recovery system
- Lane Scheduler v1: Basic lane execution coordinator
- 40+ tests: Comprehensive coverage of all modules
- No regressions: Phase 1 tests remain passing

---

## Module 1: Contract Gate System

### Purpose

Implements **8-gate compliance validation** to ensure all proposals meet governance requirements before execution.

### Eight Gates

| Gate | Name | Purpose |
|------|------|---------|
| 1 | Contract Schema Validation | Verify proposal structure |
| 2 | Regression Test Validation | Confirm tests pass |
| 3 | Security Audit Pass | Validate security review |
| 4 | Policy Tier Compliance | Check tier requirements |
| 5 | Input-Lock Immutability | Verify lock is signed |
| 6 | Output-Contract Schema Match | Validate output schema |
| 7 | Decision-Trace Integrity | Check trace completeness |
| 8 | Rollback Instruction Completeness | Validate rollback steps |

### Key Classes

- **`GateResult`**: Result of single gate validation
- **`ComplianceResult`**: Result of full 8-gate check
- **`ContractGateSystem`**: Main validator

### Usage

```python
from src.orchestration.gates.contract_gate import ContractGateSystem

system = ContractGateSystem()
proposal = {
    "proposal_id": "prop_001",
    "lane_id": "lane_a",
    "action_type": "code_change",
    "description": "Security patch",
    "policy_tier": "T2",
    "regression_tests": {"passed": True, "test_count": 50},
    "security_audit": {"passed": True, "issues": []},
    "input_lock": {"lock_hash": "abc123...", "is_signed": True},
    "output_contract": {"schema": {...}},
    "output": {...},
    "decision_trace": {"trace_id": "...", "is_signed": True, "entries": [...]},
    "rollback_instructions": {"steps": [...], "is_validated": True},
}

result = system.validate_all_gates(proposal)
print(f"All passed: {result.all_passed}")
print(f"Pass rate: {result.summary['pass_rate']}%")
```

### Integration Points

- **Phase 1**: Uses InputLockAdapter for immutability checks
- **Phase 1**: Uses DecisionTraceWriter for gate logging
- **Phase 3+**: Input to security factory workflows

---

## Module 2: Policy Tier Classification Engine

### Purpose

Automatically classifies actions into policy tiers (T0-T3) based on risk assessment.

### Tier Definitions

| Tier | Name | Examples | Required Gates | Approvers |
|------|------|----------|-----------------|-----------|
| T0 | Metadata-only | Logging, README updates | [1] | None |
| T1 | Low-risk operational | Tests, docs, minor fixes | [1, 2] | code-owner |
| T2 | Code-level | Security patches, APIs | [1, 2, 3, 4, 5, 6] | security-reviewer, code-owner |
| T3 | Governance | Tier system, approval chains | [1-8] | maintainer |

### Key Classes

- **`TierClassification`**: Classification result with justification
- **`PolicyTierEngine`**: Classification engine

### Usage

```python
from src.orchestration.healing.policy_tier_engine import PolicyTierEngine

classification = PolicyTierEngine.classify_action(
    action_description="Security patch for SQL injection vulnerability",
    affected_modules=["src/db/query.py", "src/api/endpoint.py"],
)

print(f"Tier: {classification.tier}")
print(f"Requires gates: {classification.required_gates}")
print(f"Requires approvers: {classification.required_approvers}")
print(f"Risk score: {classification.risk_score}")
```

### Risk Assessment

Risk scores are computed based on:
- Keywords in description (delete, security, breaking change, etc.)
- Number of affected modules
- Auto-escalation if risk exceeds tier threshold

Example:
- T0 action with risk >10 escalates to T1
- T1 action with risk >35 escalates to T2
- T2 action with risk >65 escalates to T3

### Integration Points

- **Phase 1**: Uses seed system for deterministic classification
- **Phase 3**: Feeds into approval workflow routing

---

## Module 3: Rollback Control System

### Purpose

Implements one-command recovery with step verification and failure handling.

### Key Classes

- **`RollbackStep`**: Single rollback operation
- **`RollbackStepResult`**: Result of step execution
- **`RollbackExecutionResult`**: Full rollback outcome
- **`RollbackControlSystem`**: Orchestrator

### Supported Step Types

- **`git_revert`**: Revert commits (requires commit_sha)
- **`data_migration`**: Execute data updates (requires operation)
- **`cleanup`**: Clean up resources (requires target)

### Usage

```python
from src.orchestration.safety.rollback_controls import RollbackControlSystem

system = RollbackControlSystem()
instruction = {
    "rollback_id": "rb_001",
    "steps": [
        {
            "step_id": "step_1",
            "step_type": "git_revert",
            "description": "Revert bad commit",
            "action": {"commit_sha": "abc123..."},
            "optional": False,
        },
        {
            "step_id": "step_2",
            "step_type": "data_migration",
            "description": "Restore database",
            "action": {"operation": "restore_from_backup"},
            "optional": False,
        },
    ],
}

result = system.execute_rollback(instruction)
print(f"Success: {result.success}")
print(f"Time: {result.total_execution_time_ms}ms")
```

### Failure Handling

- **Non-optional step fails**: Abort immediately, escalate to handler
- **Optional step fails**: Continue with next step
- **All steps pass**: Return success

### Integration Points

- **All modules**: Used for recovery on failures
- **Phase 1**: Logged to DecisionTraceWriter
- **Phase 3**: Triggered by security factory on violations

---

## Module 4: Lane Scheduler v1

### Purpose

Basic lane execution coordinator with dependency tracking and deterministic ordering.

### Key Concepts

- **Lane**: Logical execution unit with dependencies
- **Execution Order**: Topologically sorted based on dependencies
- **Lane State**: PENDING RUNNING PASSED/FAILED
- **Deterministic Ordering**: Same seed identical execution order

### Key Classes

- **`Lane`**: Represents a lane
- **`LaneSchedulerV1`**: Scheduler
- **`ScheduleResult`**: Execution result

### Usage

```python
from src.orchestration.scheduling.lane_scheduler_v1 import (
    LaneSchedulerV1,
    Lane,
    ExecutionMode,
)

scheduler = LaneSchedulerV1()

# Register lanes with dependencies
lane_a = Lane(lane_id="lane_a", name="Phase A")
lane_b = Lane(lane_id="lane_b", name="Phase B", upstream_dependencies=["lane_a"])
lane_c = Lane(lane_id="lane_c", name="Phase C", upstream_dependencies=["lane_a", "lane_b"])

scheduler.register_lanes([lane_a, lane_b, lane_c])

# Schedule all lanes
results = scheduler.schedule_all_lanes(mode=ExecutionMode.SEQUENTIAL)

for lane_id, result in results.items():
    print(f"{lane_id}: {result.state.value}")
```

### Execution Modes

- **SEQUENTIAL**: One lane at a time (v1)
- **PARALLEL**: Multiple lanes simultaneously (v2+)
- **SHARDED**: Lane tasks distributed (v2+)

### Integration Points

- **Phase 1**: Uses SeedControlSystem for deterministic ordering
- **Phase 3+**: Coordinated with security/performance workflows

---

## Integration with Phase 1

### Dependency Chain

```
Phase 1 (Determinism)
├── InputLockAdapter (immutability)
├── SeedControlSystem (determinism)
├── DecisionTraceWriter (audit logs)
└── LaneManifestContract (validation)
         ↓
Phase 2 (Foundation)
├── Contract Gate System (uses InputLock, DecisionTrace)
├── Policy Tier Engine (uses SeedControl)
├── Rollback Controls (uses DecisionTrace)
└── Lane Scheduler (uses SeedControl)
```

### No Regressions

- All Phase 1 tests remain passing
- Phase 1 modules work unchanged
- Phase 2 imports Phase 1 modules without modification

---

## Testing Strategy

### Test Coverage

- **Contract Gate Tests**: 15 tests (gates 1-8, all-pass, single-failure-blocks)
- **Policy Tier Tests**: 10 tests (T0-T3, escalation, batch)
- **Rollback Tests**: 8 tests (execution, verification, escalation)
- **Lane Scheduler Tests**: 7+ tests (dependencies, determinism, modes)
- **Total**: 40+ tests

### Running Tests

```bash
# Run all Phase 2 tests
pytest tests/orchestration/test_foundation_hardening.py -v

# Run specific test class
pytest tests/orchestration/test_foundation_hardening.py::TestContractGates -v

# Run with coverage
pytest tests/orchestration/test_foundation_hardening.py --cov=src/orchestration
```

---

## Phase 2 Phase 3 Gate

When Phase 2 completes, verify:

1. All 40+ tests pass
2. Phase 1 tests still pass (63 tests)
3. 8-gate compliance on mock Tier 2 proposals
4. Rollback execution for 5+ scenario types
5. Lane scheduler determinism with 10+ runs
6. Code coverage >85%

Once verified, Phase 3 (Security Factory) can begin.

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Tests passing | 40+ | |
| Phase 1 regressions | 0 | |
| 8-gate pass rate | 100% on valid proposals | |
| Tier classification accuracy | >95% | |
| Rollback success rate | 100% on valid instructions | |
| Code coverage | >85% | |
| Deterministic ordering | 100% consistency | |

