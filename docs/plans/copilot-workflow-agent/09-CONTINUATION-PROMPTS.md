# Continuation Prompts for Copilot Workflow Agent

> Generated: 2025-12-16  
> Purpose: Ready-to-use prompts for resuming implementation

## Quick Start

### Resume from Last Checkpoint
```
@copilot Resume from checkpoint CWAA-20251216-001 in docs/plans/copilot-workflow-agent/08-CHECKPOINTS.md
```

## Batch Execution Prompts

### B2 - Workflow Inventory
```
@copilot Execute Batch B2 from docs/plans/copilot-workflow-agent/01-BATCHSET.md

Implement the Workflow Inventory system:
1. Create src/services/workflow/inventory.py
2. Create src/services/workflow/parser.py
3. Create src/services/workflow/types.py
4. Create tests/services/workflow/test_inventory.py

Requirements:
- Scan all .github/workflows/*.yml files
- Parse YAML and extract metadata (name, triggers, inputs, jobs)
- Identify workflow_dispatch-enabled workflows
- Build dependency graph
- Handle malformed YAML gracefully
- Cache parsed results

Target: 15+ tests, all passing
```

### B3 - Session State
```
@copilot Execute Batch B3 from docs/plans/copilot-workflow-agent/01-BATCHSET.md

Implement Session State management:
1. Create src/services/session/state.py
2. Create src/services/session/storage.py
3. Create src/services/session/types.py
4. Create tests/services/session/test_state.py

Requirements:
- Pydantic models for session state
- File-based storage in .copilot/state/
- Atomic writes (temp + rename)
- Checkpoint save/restore
- Corruption detection and recovery

Target: 15+ tests, all passing
```

### B4 - Agent Orchestrator
```
@copilot Execute Batch B4 from docs/plans/copilot-workflow-agent/01-BATCHSET.md

Implement the Agent Orchestrator:
1. Create src/services/agent/orchestrator.py
2. Create src/services/agent/actions.py
3. Create src/services/agent/types.py
4. Create tests/services/agent/test_orchestrator.py

Requirements:
- PLAN→ACT→OBSERVE→VERIFY flow
- Integrate GitHub client, workflow inventory, session state
- Action queue with priorities
- Dry-run mode for previews
- Cancellation support

Target: 20+ tests, all passing
```

### B5 - Failure Detector
```
@copilot Execute Batch B5 from docs/plans/copilot-workflow-agent/01-BATCHSET.md

Implement the Failure Detector:
1. Create src/services/healing/detector.py
2. Create src/services/healing/patterns.py
3. Create src/services/healing/types.py
4. Create tests/services/healing/test_detector.py

Requirements:
- Pattern matching for 10+ failure types
- Contextual error extraction
- Confidence scoring
- Extensible pattern registry

Target: 15+ tests, all passing
```

### B6 - Auto-Remediator
```
@copilot Execute Batch B6 from docs/plans/copilot-workflow-agent/01-BATCHSET.md

Implement the Auto-Remediator:
1. Create src/services/healing/remediator.py
2. Create src/services/healing/strategies.py
3. Create src/services/healing/patches.py
4. Create tests/services/healing/test_remediator.py

Requirements:
- Remediation strategies for common failures
- Patch generation and validation
- Approval gate integration
- Success rate tracking

Target: 15+ tests, all passing
```

## Status Check Prompts

### View Overall Status
```
@copilot Show status of all batches in docs/plans/copilot-workflow-agent/01-BATCHSET.md and identify next actions
```

### View Phase Progress
```
@copilot Show Phase 1 progress from docs/plans/copilot-workflow-agent/00-PLANSET.md
```

### Run Gap Analysis
```
@copilot Analyze docs/plans/copilot-workflow-agent/ and identify remaining gaps, risks, and incomplete implementations
```

## Verification Prompts

### Run All Tests
```
@copilot Run all Copilot Workflow Agent tests:
pytest tests/services/github/ tests/services/workflow/ tests/services/session/ tests/services/agent/ tests/services/healing/ -v
```

### Validate Implementation
```
@copilot Verify Batch B1-B2 implementation meets acceptance criteria from docs/plans/copilot-workflow-agent/01-BATCHSET.md
```

## Emergency Recovery

### If Tests Fail
```
@copilot Fix failing tests in tests/services/[module]/:
1. Check import paths
2. Verify mocks are configured
3. Ensure async tests use pytest.mark.asyncio
4. Run tests individually to isolate issues
```

### If Implementation Incomplete
```
@copilot Resume implementation of [BATCH_ID] from last checkpoint, focusing on:
1. Missing files
2. Incomplete functions
3. Missing tests
```

---

## Session History

| Date | Checkpoint | Batches Completed | Notes |
|------|------------|-------------------|-------|
| 2025-12-16 | CWAA-20251216-001 | B0, B1 | Initial implementation |

---

*Use these prompts to continue implementation in future sessions.*
