# Promotion Checklist: `0D_base_` → `main`

This checklist is the approval gate to move staged reasoning work from the `0D_base_` ring toward `main`.
It aligns Product, Infra, and Model/Training without requiring network access or external CI.

## 1. Artifacts captured
Before requesting promotion, the branch owner MUST have run at least one local training/eval cycle
using the approved reasoning config (for example `configs/training/reasoning/baseline.yaml`)
and MUST have these files in the training output directory (default `runs/train_loop/`):

- `run_metadata.json`
- `reasoning.json` (if reasoning harness was active)
- `evaluation.json` (if evaluation harness was active)

These are emitted automatically by the training loop; they snapshot:
- `metadata.rollout_ring`
- control-surface knobs:
  - `trace_mode`
  - `curriculum_preset`
  - `evaluation_preset`
  - `deployment_preset`
- ownership / escalation contact
- evaluation summary and reasoning summary (if present)

## 2. Status report / readiness summary
Run:

```bash
python -m codex_ml.cli.codex_cli status-report \
  --run-metadata-dir runs/train_loop
```

Attach the resulting JSON blob to the PR that proposes promotion.

## 3. Deployment dry-run validation
Run:

```bash
python -m codex_ml.cli.codex_cli deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --dry-run \
  --run-metadata-dir runs/train_loop
```

This MUST succeed. A nonzero exit code means `DEPLOYMENT BLOCKED`. That blocks promotion.

Enforced guarantees:
1. `metadata.rollout_ring` exists in `run_metadata.json`.
2. The rollout_ring in training matches the pod ring in `configs/deploy/reasoning_pod.yaml`.
3. We are explicitly in `--dry-run` mode (no live infra touch in this ring).

## 4. Status update document
There MUST be a survey/status file checked in under:

```text
docs/status_updates/survey-<ring>-and-<PR>-<DATESTAMP>.md
```

For example:
`docs/status_updates/survey-0D_base_-and-1926-2025-10-29.md`

This file captures the reconciled view of:
- training orchestration code (TrainLoop, UnifiedTraining)
- reasoning harness state (`_vectorise_model` / trace capture)
- curricula and baseline knobs
- evaluation presets
- deployment story and ring semantics
- any doc/code mismatches discovered in that survey

## 5. Explicit sign-off on evaluation preset
The reviewer MUST confirm one of:
1. The evaluation preset in `run_metadata.json.knobs.evaluation_preset` has passed offline evaluation, OR
2. The PR description includes an explicit human sign-off noting why it is acceptable to proceed (for example,
   "We accept limited evaluation coverage because this branch only fixes docs and CLI surface; no model behavior changes").

## 6. Final check list for `main`
Promotion from `0D_base_` toward `main` may proceed ONLY if:

- rollout_ring is declared AND matches pod ring.
- `codex_ml.cli.codex_cli status-report` has been attached to the PR.
- `codex_ml.cli.codex_cli deploy --dry-run` succeeded.
- Latest `docs/status_updates/survey-...` exists and is linked in the PR.
- The evaluation preset is either passing offline or explicitly signed off.

When all of the above boxes are checked, merge to `main` is allowed.
If any box is unchecked, promotion is blocked.

---

## 7. Control surface / future UI contract
The future "control surface" (front-end knobs for Product / Infra) is expected to read
exactly the fields surfaced by:

```bash
python -m codex_ml.cli.codex_cli status-report \
  --run-metadata-dir runs/train_loop
```

Specifically:
- `rollout_ring`
- `knobs.trace_mode`
- `knobs.curriculum_preset`
- `knobs.evaluation_preset`
- `knobs.deployment_preset`

These are considered the user-facing adjustable knobs for staged reasoning systems.
If any of these values are missing or clearly wrong, promotion MUST pause because the
front-end would not know what it's shipping.
