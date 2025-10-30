## Promotion / Readiness Checklist

Fill this out for any PR that:
- Promotes work from a rollout ring (for example `0D_base_`) toward `main`, OR
- Introduces / updates reasoning-serving infra (deployment presets, pod YAMLs, etc.).

If this PR is only docs or comments, fill what you can and explicitly say why promotion gating does not apply.

---

### 1. Rollout ring and branch context
- Target rollout_ring from training artifacts (run_metadata.json):  
  `rollout_ring = ____________________`

- Source branch / ring being promoted (e.g. `0D_base_`):  
  `branch = ____________________`

- Target branch (e.g. `main`):  
  `target = ____________________`

### 2. Survey snapshot
- Path to the committed survey snapshot under docs/status_updates/:  
  `docs/status_updates/____________________.md`

Confirm this file:
- Describes orchestrators (TrainLoop / UnifiedTraining), reasoning harness trace capture, curricula config, evaluation preset, deployment preset.
- Captures any known code/docs mismatches.

### 3. Status report
Attach the output of:

```bash
python -m codex_ml.cli.codex_cli status-report \
  --run-metadata-dir runs/train_loop
```

Paste JSON here (trim secrets if any):

```text
<status-report JSON here>
```

This MUST include:
- `rollout_ring`
- `knobs.trace_mode`
- `knobs.curriculum_preset`
- `knobs.evaluation_preset`
- `knobs.deployment_preset`

### 4. Dry-run deploy proof
Provide the output (or summary) of:

```bash
python -m codex_ml.cli.codex_cli deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --dry-run \
  --run-metadata-dir runs/train_loop
```

`codex_ml.cli.codex_cli deploy` MUST report success with `--dry-run`. If it printed `DEPLOYMENT BLOCKED`, stop and explain why.

Paste result / summary here:

```text
<deploy dry-run result>
```

### 5. Evaluation preset sign-off
Check ONE:

- [ ] Offline evaluation preset passed and is reflected in `evaluation.json`.
- [ ] This PR does not modify model behavior; safe to merge without new evaluation.
      Rationale:
      ____________________________________________

### 6. Ack: This PR follows docs/ops/promotion_checklist.md
- [ ] I confirm I walked through `docs/ops/promotion_checklist.md` and this PR satisfies the required gates.

---

Reviewer notes / escalation contact:
- Owner / escalation contact from run_metadata.json: ____________________
- Additional context:
  ______________________________________________________
