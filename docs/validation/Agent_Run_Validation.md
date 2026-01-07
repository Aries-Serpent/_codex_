# [Validation]: Agent-Run Capability & Limits  
> Generated: Previous Cycle-11-06 10:49:42 | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## Purpose
Validate the Agent environment used for heavy jobs (distributed, LoRA, perf). Capture capabilities for deterministic builds and testing.

## Commands

```bash
# Probe agent environment
python scripts/agent/probe_env.py

# Optional gated tests (Agent-run)
ACCELERATE_TEST=1 pytest -q tests/integration/test_distributed_init.py || true
RUN_LORA_TESTS=1 pytest -q tests/modeling/test_lora_minimal.py || true
```text

## Outputs

| Path | Description |
|------|-------------|
| audit_artifacts/agent_env.json | Snapshot of agent environment |
| audit_artifacts/canonical_manifest.json | Canonical SHAs for determinism |
| audit_artifacts/baselines/<ts>/ | Stored baselines (rotated) |

## Notes

- Heavy jobs default to Agent-run; CI remains CPU-only and fast.
- Baseline size growth mitigated via rotation (retain N recent).
