# 🚀 Campaign Execution Guide

This guide explains how to use the Campaign Framework to orchestrate multi-phase workflows with parallel agent delegation.

## Quick Start

### 1. List Available Campaigns

```bash
python -m codex campaign list
```

Displays all campaigns in `.codex/campaigns/CAMPAIGN_REGISTRY.yaml`:
- production-readiness-v1 (critical)
- coverage-improvement (high)
- self-heal-ci (high)
- security-hardening (critical)

### 2. Check Campaign Status

```bash
python -m codex campaign status production-readiness-v1
```

Shows current execution state, completed phases, and any escalations.

### 3. Run a Campaign

```bash
python -m codex campaign run production-readiness-v1
```

Executes the production readiness campaign:
1. Activates campaign
2. Executes phases sequentially (Phase 1 → Phase 2 → ... → Phase 5)
3. Within each phase, agents run in parallel
4. Verifies gates after each phase
5. Collects artifacts
6. Records learnings in pattern store

## Campaign Framework Architecture

### Core Components

```
CampaignDefinition
├── campaign_id: str
├── name: str
├── objectives: List[str]
├── phases: List[CampaignPhase]
├── success_criteria: List[str]
└── escalation_threshold: int (max iterations before human escalation)

CampaignPhase
├── phase_id: str
├── name: str
├── parallel_agents: List[str]
├── gate_condition: Callable (verifies phase success)
├── timeout_seconds: int
└── artifacts: List[str]

CampaignExecution (Runtime State)
├── campaign_id: str
├── current_phase_index: int
├── agent_results: Dict[str, Any]
├── phase_results: List[PhaseExecutionResult]
├── iterations: int
├── status: CampaignStatus
└── artifacts_collected: Dict[str, Path]
```

### Execution State Machine

```
IDLE
  ↓ [activate_campaign()]
ACTIVATED
  ↓ [execute_phase(0)]
PHASE_RUNNING (agents executing in parallel)
  ↓ [monitor_agents()]
GATE_CHECK
  ├─ [gate passes] → PHASE_1_COMPLETE
  │  ↓
  │  [execute_phase(1)]
  │  ↓ ... (repeat for phases 2-4)
  │
  └─ [gate fails, iter < threshold]
     ↓ [retry_phase()]
     (go back to PHASE_RUNNING)

  [gate fails, iter >= threshold]
  ↓ [escalate()]
ESCALATED (human intervention required)
  ↓
COMPLETE or FAILED (depending on escalation outcome)
```

## Parallel Agent Delegation

### Within-Phase Parallelism

Agents within a phase run in parallel. For example, Phase 2 of production-readiness-v1:

```yaml
- id: "2"
  name: "Coverage Expansion"
  parallel_agents:
    - unified-coverage-agent    # Identify gaps
    - test-enhancement-agent    # Improve existing tests
  timeout_seconds: 600
```

Execution timeline:
```
Time:   0s          300s          600s
        |-----------|-----------|
Agent 1 [======unified-coverage======]
Agent 2 [======test-enhancement====]
        
Both agents start at t=0s
Both must complete by t=600s
Gate check happens at t=600s+ when both finish or timeout
```

### Orchestration Patterns

**SEQUENTIAL_CHAIN:** Execute phases one after another (production-readiness-v1)
```
Phase 1 → Gate 1 → Phase 2 → Gate 2 → Phase 3 → ... → Complete
```

**PARALLEL_FAN_OUT:** Execute multiple agents within a phase in parallel
```
Phase X:
  Agent 1 --|
  Agent 2 --|-→ Aggregate Results → Gate X
  Agent 3 --|
```

**CONDITIONAL_ROUTING:** Choose agents based on conditions (self-heal-ci)
```
Diagnosis → Pattern Classification → Choose Fix Agent → Verify → Complete
```

## Campaign Registry Format

Campaigns are defined in `.codex/campaigns/CAMPAIGN_REGISTRY.yaml`:

```yaml
version: 2.0.0

campaigns:
  - id: my-campaign
    name: "Campaign Name"
    description: "What this campaign does"
    category: "deployment|quality|reliability|security"
    
    objectives:
      - "Objective 1"
      - "Objective 2"
    
    phases:
      - id: "1"
        name: "Phase Name"
        description: "Phase description"
        parallel_agents:
          - agent-id-1
          - agent-id-2
        gate_condition: "metric >= 100"  # Custom condition
        timeout_seconds: 600
        artifacts:
          - "expected_file_1.md"
          - "expected_file_2.json"
        metrics_expected:
          - "Metric 1"
          - "Metric 2"
    
    success_criteria:
      - "Criterion 1"
      - "Criterion 2"
    
    escalation_threshold: 3
    rollback_strategy: "revert_and_alert"  # or "commit_and_alert"
```

## Production Readiness Campaign (Phases 1-5)

### Phase 1: Security Hardening ✅ COMPLETE

**Agents:** unified-security-scanner

**Objectives:**
- Scan for XXE vulnerabilities
- Detect command injection patterns
- Verify logging practices
- Audit cryptographic implementations
- Validate URL handling

**Success Criteria:**
- 0 critical vulnerabilities
- 0 high-severity vulnerabilities
- 150+ files scanned

**Artifacts:**
```
.codex/campaign_artifacts/production-readiness-v1/phase_1/
├── SECURITY_FINDINGS_XXE_CMDINJECTION.md
├── SECURITY_FINDINGS_LOGGING.md
├── SECURITY_FINDINGS_HASHING_DESER.md
├── SECURITY_FINDINGS_URL_VALIDATION.md
└── SECURITY_PHASE1_COMPLETE.md
```

### Phase 2: Coverage Expansion ✅ COMPLETE

**Agents:** unified-coverage-agent, test-enhancement-agent (parallel)

**Objectives:**
- Identify zero/low-coverage modules
- Generate new tests
- Improve coverage metrics

**Success Criteria:**
- 88+ new test methods
- 12%+ coverage achieved
- All tests passing

**Artifacts:**
```
.codex/campaign_artifacts/production-readiness-v1/phase_2/
├── COVERAGE_GAP_ANALYSIS.md
├── COVERAGE_PHASE2_TEST_GENERATION_COMPLETE.md
├── tests/unit/test_checkpoint_core_resume.py
├── tests/unit/test_training_callbacks.py
└── ... (6 new test files)
```

### Phase 3: CI Stability ✅ COMPLETE

**Agents:** ci-auto-healer-agent, workflow-compliance-guardian (parallel)

**Objectives:**
- Audit GitHub Actions workflows
- Fix deprecated actions
- Ensure REQ-4/5 compliance
- Prevent workflow cascades

**Success Criteria:**
- 183 workflows audited
- 100% REQ compliance
- 0 deprecated actions

### Phase 4: Agent Architecture 🔵 IN PROGRESS

**Agents:** agent-orchestrator

**Objectives:**
- Validate 145-agent registry
- Sync cognitive brain memory
- Index pattern learning store
- Audit CAD-Mandate compliance

**Success Criteria:**
- All 145 agents active
- Memory sync < 80% capacity
- Pattern index complete

### Phase 5: Final Validation 🔵 IN PROGRESS

**Agents:** security-alert-verification-agent, unified-coverage-agent, workflow-compliance-guardian (parallel)

**Objectives:**
- **5a: Security Reaudit** — Verify Phase 1 findings remain fixed
- **5b: Coverage Validation** — Lock coverage at achieved threshold
- **5c: CI Compliance** — Verify all REQ gates passing

**Success Criteria:**
- 0 critical/high vulnerabilities
- Coverage >= 12%
- 100% REQ-1 to REQ-13 passing

## Integration with Existing Agents

### Custom Agent Routing

The Campaign Framework uses existing agent infrastructure:

```python
from src.codex.campaigns import CampaignOrchestrator, CampaignRegistryLoader
from pathlib import Path

# Load campaign definition
registry = CampaignRegistryLoader.load_registry(
    Path(".codex/campaigns/CAMPAIGN_REGISTRY.yaml")
)

campaign_def = registry["production-readiness-v1"]

# Create orchestrator
orchestrator = CampaignOrchestrator(campaign_def)

# Activate and execute
orchestrator.activate_campaign()

for phase_idx, phase in enumerate(campaign_def.phases):
    # Dispatch agents
    agent_ids = orchestrator.execute_phase(phase_idx)
    
    # Monitor execution
    results = orchestrator.monitor_agents(
        agent_ids,
        phase.timeout_seconds
    )
    
    # Verify gate
    gate_pass = orchestrator.verify_gate(phase_idx, results)
    
    if not gate_pass:
        # Retry or escalate
        pass
    
    # Collect artifacts
    orchestrator.collect_artifacts(phase_idx)

# Finalize
orchestrator.finalize(CampaignStatus.COMPLETE)
```

## Artifact Management

### Directory Structure

```
.codex/campaign_artifacts/
├── production-readiness-v1/
│   ├── phase_1/
│   │   ├── SECURITY_FINDINGS_XXE_CMDINJECTION.md
│   │   └── ...
│   ├── phase_2/
│   │   ├── COVERAGE_GAP_ANALYSIS.md
│   │   └── ...
│   └── phase_5/
│       ├── PRODUCTION_READINESS_MERGE_CERTIFICATION.md
│       └── ...
├── coverage-improvement/
│   ├── phase_1/
│   ├── phase_2/
│   └── phase_3/
└── campaign_executions.jsonl
```

### Artifact Retention

- Phase artifacts: 180-day retention (configurable)
- Execution logs: 365-day retention
- Pattern learnings: Indefinite (fed to pattern_learning_store.json)

## Monitoring & Debugging

### Check Campaign Status

```bash
python -m codex campaign status production-readiness-v1
```

Output:
```
Campaign: Production Deployment Readiness Campaign
Status: in_progress
Current Phase: 4/5 (Agent Architecture)
Progress: 360/600 seconds (60%)
Agents: 1 running, 0 completed, 0 failed

Phase Results:
  Phase 1: ✅ PASS (358s)
  Phase 2: ✅ PASS (355s)
  Phase 3: ✅ PASS (409s)
  Phase 4: ⏳ IN PROGRESS
```

### View Execution Log

```bash
tail -f .codex/aftermath/campaign_executions.jsonl
```

Output:
```json
{
  "campaign_id": "production-readiness-v1",
  "status": "in_progress",
  "activation_time": "2026-06-13T00:10:00Z",
  "phases_completed": 3,
  "iterations": 0
}
```

### Check Pattern Learnings

```bash
python -m codex pattern search campaign_execution
```

Shows all patterns learned from campaign executions.

## Troubleshooting

### Campaign Stuck in Phase X

**Symptom:** Campaign running for >timeout_seconds in a phase

**Solution:**
1. Check agent logs: `python -m codex agent logs {agent_id}`
2. Verify all dependencies available
3. If issue persists, escalate: `python -m codex campaign escalate {campaign_id}`

### Gate Condition Failing

**Symptom:** Phase gate verification fails repeatedly (>threshold iterations)

**Solution:**
1. Review phase objectives in CAMPAIGN_REGISTRY.yaml
2. Check agent output artifacts
3. Verify success criteria are achievable
4. Consider adjusting escalation_threshold

### Artifact Not Collected

**Symptom:** Expected artifact file missing from campaign_artifacts/

**Solution:**
1. Verify artifact path in phase definition matches actual agent output
2. Check if agent completed successfully (status: "completed")
3. Verify artifact directory permissions

## Advanced: Creating Custom Campaigns

### Step 1: Define Campaign in Registry

Add entry to `.codex/campaigns/CAMPAIGN_REGISTRY.yaml`:

```yaml
- id: my-custom-campaign
  name: "My Custom Campaign"
  description: "Does something specific"
  category: "quality"
  objectives: [...]
  phases:
    - id: "1"
      name: "Phase 1"
      parallel_agents: [agent-1, agent-2]
      gate_condition: "custom_metric >= threshold"
      timeout_seconds: 600
      artifacts: [...]
  success_criteria: [...]
```

### Step 2: Implement Custom Gate Condition

```python
def my_gate_condition(agent_results: Dict[str, Any]) -> bool:
    """Custom gate: all agents succeeded and metric >= threshold."""
    for agent_id, result in agent_results.items():
        if result.get("status") != "completed":
            return False
        if result.get("metric", 0) < 100:
            return False
    return True
```

### Step 3: Run Campaign

```bash
python -m codex campaign run my-custom-campaign
```

## Integration with GitHub

### Automatic PR Checks

Campaigns can be triggered automatically on:
- PR creation/update
- Scheduled triggers (cron)
- Manual dispatch
- Issue/discussion events

Configuration in `.github/workflows/campaign-executor.yml` (create this):

```yaml
name: Campaign Executor

on:
  push:
    branches: [main, 0D_base_]
  pull_request:
  schedule:
    - cron: "0 2 * * 0"  # Weekly

jobs:
  run-campaigns:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      
      - name: Run Campaign
        run: |
          python -m codex campaign run production-readiness-v1
      
      - name: Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: campaign-artifacts
          path: .codex/campaign_artifacts/
```

## References

- **Campaign Registry:** `.codex/campaigns/CAMPAIGN_REGISTRY.yaml`
- **Orchestrator Implementation:** `src/codex/campaigns/orchestrator.py`
- **Pattern Learning Store:** `.codex/cognitive_brain/pattern_learning_store.json`
- **Execution Logs:** `.codex/aftermath/campaign_executions.jsonl`
- **Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml` (145 active agents)

## FAQ

**Q: How many campaigns can run concurrently?**
A: Max 1 campaign per session (due to artifact isolation). Multiple campaigns can chain (Phase A → Phase B).

**Q: What happens if an agent times out?**
A: Agent marked as "timeout", phase gate fails, retry logic triggered (up to escalation_threshold).

**Q: Can I pause/resume a campaign?**
A: Yes, through session checkpoints. Campaign state saved in campaign_executions.jsonl.

**Q: How do learnings feed back to agent routing?**
A: Patterns stored in pattern_learning_store.json, used by agent-orchestrator for future routing.

**Q: What's the relationship between campaigns and existing orchestrators?**
A: Campaigns are a meta-layer; they delegate to orchestrating agents (agent-orchestrator, self-healing-orchestrator-agent, etc.).
