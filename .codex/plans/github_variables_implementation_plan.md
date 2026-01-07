# GitHub Repository Variables Implementation Plan
# PR #2685 - V10 Development & Audit Infrastructure

> **Generated**: Current Cycle-01-03T19:49:22Z  
> **Author**: Copilot AI Agent  
> **Branch**: copilot/sub-pr-2682  
> **Purpose**: Leverage GitHub repo variables for deterministic audit configuration and V10 agent deployment

---

## 📋 Executive Summary

This plan outlines the implementation of GitHub Repository Variables for non-sensitive configuration data reuse across workflows, coupled with detailed plansets and promptsets for completing the V10 Custom Agent Development initiative.

**Key Objectives:**
1. Externalize audit configuration to GitHub Repository Variables (48KB limit)
2. Enable deterministic, reproducible audit runs across environments
3. Facilitate V10 agent development with configurable seeds and parameters
4. Provide promptsets for autonomous agent implementation

---

## 🎯 Phase 1: GitHub Repository Variables Setup

### 1.1 Priority Variables (Immediate Implementation)

#### Audit Infrastructure Variables

| Variable Name | Type | Value | Size | Purpose |
|---------------|------|-------|------|---------|
| `AUDIT_SAFEGUARD_KEYWORDS` | JSON Array | `["sha256","checksum","rng","seed","offline","WANDB_MODE","deterministic","nosec"]` | ~150B | Safeguard detection in S4 scoring |
| `AUDIT_MAX_READ_BYTES` | Integer | `200000` | ~6B | Deterministic file truncation |
| `AUDIT_WEIGHTS` | JSON Object | `{"functionality":0.25,"consistency":0.20,"tests":0.25,"safeguards":0.15,"documentation":0.15}` | ~120B | Component scoring weights |
| `AUDIT_LOW_THRESHOLD` | Float | `0.70` | ~4B | Low maturity gate |
| `AUDIT_REGRESSION_DELTA` | Float | `0.02` | ~4B | Regression detection threshold |
| `AUDIT_OUTPUT_DIRS` | JSON Object | `{"reports":"reports","artifacts":"audit_artifacts"}` | ~80B | Output path configuration |

**Total Size**: ~364 bytes (well under 48KB limit)

#### V10 Agent Configuration Variables

| Variable Name | Type | Value | Size | Purpose |
|---------------|------|-------|------|---------|
| `AGENT_SEEDS` | CSV | `46,47,48,49,50,51` | ~18B | Deterministic seeds for all V10 agents |
| `VALIDATION_SEED` | Integer | `42` | ~2B | Global validation seed |
| `EMERGENT_AGENT_SEED` | Integer | `46` | ~2B | Emergent Intelligence Agent seed |
| `PERF_MONITOR_SEED` | Integer | `47` | ~2B | Performance Monitor Agent seed |
| `DOC_AGENT_SEED` | Integer | `48` | ~2B | Documentation Agent seed |
| `CI_OPTIMIZER_SEED` | Integer | `49` | ~2B | CI Optimizer Agent seed |
| `REASONING_ADVISOR_SEED` | Integer | `50` | ~2B | Reasoning Advisor Agent seed |
| `ECOSYSTEM_COORD_SEED` | Integer | `51` | ~2B | Ecosystem Coordinator Agent seed |
| `CI_DURATION_NORMALIZATION_MS` | Integer | `1000` | ~4B | CI timing normalization baseline |
| `WANDB_MODE` | String | `"offline"` | ~8B | Offline telemetry enforcement |

**Total Size**: ~46 bytes

---

## 📚 Variable Catalog

### Complete Variable Reference

| #  | Variable Name | Type | Default | Scope | Size | Consumers |
|----|---------------|------|---------|-------|------|-----------|
| 1  | `AUDIT_SAFEGUARD_KEYWORDS` | JSON | `["sha256","checksum",...]` | Repo | 150B | audit_runner.py (S4) |
| 2  | `AUDIT_MAX_READ_BYTES` | int | `200000` | Repo | 6B | audit_runner.py (S1/S4) |
| 3  | `AUDIT_DOMAIN_PATTERNS` | JSON | See workflow.yaml | Repo | 200B | audit_runner.py (S2) |
| 4  | `AUDIT_CAPABILITY_RULE_OVERRIDES` | JSON | — | Repo | 300B | audit_runner.py (S3) |
| 5  | `AUDIT_WEIGHTS` | JSON | `{0.25,0.20,0.25,0.15,0.15}` | Repo | 120B | audit_runner.py (S4/S6) |
| 6  | `AUDIT_LOW_THRESHOLD` | float | `0.70` | Repo | 4B | audit_runner.py (S5) |
| 7  | `AUDIT_REGRESSION_DELTA` | float | `0.02` | Repo | 4B | audit_runner.py (diff) |
| 8  | `AUDIT_MATRIX_TEMPLATE` | path | `templates/audit/...` | Repo | 50B | audit_runner.py (S6) |
| 9  | `AUDIT_OUTPUT_DIRS` | JSON | `{"reports":"reports",...}` | Repo | 80B | audit_runner.py (S6/S7) |
| 10 | `CI_DURATION_NORMALIZATION_MS` | int | `1000` | Repo | 4B | ci-testing-agent |
| 11 | `VALIDATION_SEED` | int | `42` | Repo | 2B | advanced_optimization.py |
| 12 | `EMERGENT_AGENT_SEED` | int | `46` | Repo | 2B | emergent-intelligence-agent |
| 13 | `PERF_MONITOR_SEED` | int | `47` | Repo | 2B | performance-monitor-agent |
| 14 | `DOC_AGENT_SEED` | int | `48` | Repo | 2B | documentation-agent |
| 15 | `CI_OPTIMIZER_SEED` | int | `49` | Repo | 2B | ci-optimizer-agent |
| 16 | `REASONING_ADVISOR_SEED` | int | `50` | Repo | 2B | reasoning-advisor-agent |
| 17 | `ECOSYSTEM_COORD_SEED` | int | `51` | Repo | 2B | ecosystem-coordinator-agent |
| 18 | `AGENT_SEEDS` | CSV | `46,47,48,49,50,51` | Org | 18B | All V10 agents |
| 19 | `WANDB_MODE` | str | `"offline"` | Repo | 8B | Telemetry tooling |
| **TOTAL** | **19 variables** | - | - | - | **958B** | **1.97% of 48KB** |

---

## 🚀 Quick Start Commands

### Create Variables via gh CLI

```bash
#!/bin/bash
# Set all V10 agent seed variables

gh variable set AGENT_SEEDS --body "46,47,48,49,50,51"
gh variable set VALIDATION_SEED --body "42"
gh variable set EMERGENT_AGENT_SEED --body "46"
gh variable set PERF_MONITOR_SEED --body "47"
gh variable set DOC_AGENT_SEED --body "48"
gh variable set CI_OPTIMIZER_SEED --body "49"
gh variable set REASONING_ADVISOR_SEED --body "50"
gh variable set ECOSYSTEM_COORD_SEED --body "51"
gh variable set WANDB_MODE --body "offline"
gh variable set CI_DURATION_NORMALIZATION_MS --body "1000"

# Set audit infrastructure variables
gh variable set AUDIT_SAFEGUARD_KEYWORDS --body '["sha256","checksum","rng","seed","offline","WANDB_MODE","deterministic","nosec"]'
gh variable set AUDIT_MAX_READ_BYTES --body "200000"
gh variable set AUDIT_WEIGHTS --body '{"functionality":0.25,"consistency":0.20,"tests":0.25,"safeguards":0.15,"documentation":0.15}'
gh variable set AUDIT_LOW_THRESHOLD --body "0.70"
gh variable set AUDIT_REGRESSION_DELTA --body "0.02"
gh variable set AUDIT_OUTPUT_DIRS --body '{"reports":"reports","artifacts":"audit_artifacts"}'

echo "✅ All variables created successfully"
```

### Validate Variables

```bash
# List all variables
gh variable list

# Check specific variable
gh variable get AGENT_SEEDS
```

---

## 📖 Usage Examples

### Example 1: Workflow with Variables

```yaml
name: V10 Agent Test
on: [push]

jobs:
  test-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Emergent Intelligence Agent
        env:
          AGENT_SEED: ${{ vars.EMERGENT_AGENT_SEED }}
          WANDB_MODE: ${{ vars.WANDB_MODE }}
        run: |
          python -c "import os; print(f'Using seed: {os.getenv(\"AGENT_SEED\")}')"
          python .github/agents/emergent-intelligence-agent/src/pattern_analyzer.py
```

### Example 2: Audit with Custom Weights

```yaml
      - name: Run Audit with Custom Weights
        env:
          AUDIT_WEIGHTS: ${{ vars.AUDIT_WEIGHTS }}
          AUDIT_LOW_THRESHOLD: ${{ vars.AUDIT_LOW_THRESHOLD }}
        run: |
          python scripts/space_traversal/audit_runner.py stage S4
```

### Example 3: Multi-Agent Coordination

```yaml
      - name: Run All V10 Agents
        env:
          AGENT_SEEDS: ${{ vars.AGENT_SEEDS }}
        run: |
          IFS=',' read -ra SEEDS <<< "$AGENT_SEEDS"
          for i in "${!SEEDS[@]}"; do
            echo "Running agent $i with seed ${SEEDS[$i]}"
          done
```

---

## 🎯 Success Criteria

- [x] Variable catalog documented (19 variables)
- [ ] All variables created in GitHub repository
- [ ] Audit runner updated to consume variables
- [ ] V10 agents configured to use seed variables
- [ ] Workflows updated to pass variables as env vars
- [ ] Validation script created and passing
- [ ] Documentation complete
- [ ] Zero hardcoded seeds in agent code
- [ ] Backward compatibility maintained (defaults)

---

*Generated for PR #2685 - Copilot AI Agent*
