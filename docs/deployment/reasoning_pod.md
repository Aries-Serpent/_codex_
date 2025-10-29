# Reasoning Pod (Dry-Run Deployment Preset)

## Purpose
The "reasoning pod" describes how a bespoke reasoning agent *would* be
packaged and hosted. It defines resource shape, expected inputs, and
telemetry expectations so that Product, Engineering, and on-call
stakeholders can reason about rollout impact without touching
production infrastructure.

This is explicitly **not** production hosting. It exists for:
- reproducibility review,
- resource sizing review (CPU / memory / GPU),
- telemetry + trace expectations,
- rollout ring declaration.

## Dry-run flow
1. Prepare or select a model bundle:

       artifacts/runs/reasoning-starter:last

2. Execute the dry run:

       codex deploy \
         --config configs/deploy/reasoning_pod.yaml \
         --model artifacts/runs/reasoning-starter:last \
         --dry-run

3. Inspect the generated manifest:
   - `image` / tag are correct for the artifact you intend to ship.
   - resource requests/limits make sense.
   - `CODEX_CURRICULUM_PHASE`, `CODEX_TRACE_MODE`,
     and `CODEX_EVAL_PRESET` are correct.
   - `rollout_ring` matches the ring you plan to target next
     (for example, "`0D_base_`").

Dry-run means no pod is created anywhere. It only renders the manifest
and surfaces warnings.

### Ring validation guardrail

`codex deploy --dry-run` reads `runs/train_loop/run_metadata.json` to enforce
rollout policy:

1. The training config must declare `metadata.rollout_ring`.
2. The recorded rollout ring must match the pod ring specified in this
   preset (`rollout_ring` at the root or `pod.ring`).
3. The command refuses to proceed without `--dry-run` in this maturity ring.

If any of those checks fail, the command exits non-zero with
`DEPLOYMENT BLOCKED`, preventing accidental promotion of mismatched runs.
This guardrail ties the training artifacts to deployment intent without
touching production infrastructure.

## Readiness gates before merging toward `main`
- Curriculum phase and trace mode for this model are documented.
- Offline evaluation gates (math / theorem / tool probes) pass their
  thresholds.
- A rollout ring is declared (`0A_base_` → `0B_base_` → `0C_base_`
  → `0D_base_` → `main`) and signed off.

Until all of those conditions are met and infra explicitly approves,
this pod configuration MUST NOT be treated as production.
