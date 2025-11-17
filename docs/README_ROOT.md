# codex-universal

<!-- manifest-digest:start -->
[![Manifest SHA256](https://img.shields.io/badge/manifest-unknown-blue)](#)
<!-- manifest-digest:end -->

The `_codex_` image now centers on **reasoning agents**. Use this document as the top-level map for roadmap milestones,
architecture references, and the bespoke-model hosting workflow that underpins every guided rollout.

## Orientation

| Goal | Where to start |
| --- | --- |
| Understand the reasoning roadmap | [Reasoning milestones](#reasoning-roadmap-milestones) |
| Skim architecture dependencies | [Architecture diagrams](#architecture-at-a-glance) |
| Launch a bespoke model | [Hosting bespoke reasoning models](#hosting-bespoke-reasoning-models) |
| Train/evaluate/deploy | [Guided pipelines](#guided-reasoning-pipelines) |

### Repo Map (Reasoning-Focused)
You can now surface a reasoning-focused repository map:

```bash
codex repo-map --reasoning
```text

This highlights reasoning overlays, evaluation presets, and trace-capture knobs.

## Reasoning roadmap milestones

| Milestone | Focus | Target signal |
| --- | --- | --- |
| **M0: Observability baseline** | Boot instrumented inference traces across offline smoke runs. | Trace coverage ≥95% on curated reasoning templates. |
| **M1: Curriculum-first training** | Establish first-principles curricula and replay strategies. | `reasoning.win_rate` ≥0.55 on `benchmarks/cot-lite`. |
| **M2: Model hosting hardening** | Promote bespoke models into hermetic serving pods. | Shadow-hosted latency p95 ≤ 700 ms with parity alerts. |
| **M3: Flywheel automation** | Continuous evaluation + redeploy gates orchestrated via Codex. | Weekly redeploy cadence with zero manual overrides. |

Track milestone burndown using the `reasoning_status` table exported by:

```bash
codex repo-map --reasoning
```text

Slice specific categories (for example, rollout rings and curricula) with:

```bash
codex repo-map --reasoning --include rollout_ring --include curriculum
```text

For backlog triage, anchor discussions in [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md).

### Control surface knobs and promotion checklist

`codex repo-map --reasoning` surfaces a shared set of knobs defined in
[`configs/training/reasoning/baseline.yaml`](../configs/training/reasoning/baseline.yaml):

- `trace_mode`
- `curriculum.preset`
- `evaluation.preset`
- `deployment.preset`
- `metadata.rollout_ring`

Every smoke run of the training loop writes machine-readable artifacts under `runs/train_loop/`:

- `run_metadata.json` — captures `metadata.*`, the selected presets, and the rollout ring.
- `reasoning.json` — snapshot of the reasoning harness configuration plus runtime summary.
- `evaluation.json` — evaluation preset enforced for the run.

Promotion toward `main` requires:

1. The evaluation preset to pass (or carry explicit sign-off in status reports).
2. `metadata.rollout_ring` declared in the training config and matching the target pod ring.
3. `codex deploy --dry-run` to succeed, which enforces the ring match between training output and `configs/deploy/reasoning_pod.yaml`.

Reviewers preparing a `0D_base_` → `main` merge should walk the dedicated checklist in [`docs/ops/promotion_checklist.md`](ops/promotion_checklist.md).
It also requires attaching the outputs of:

- `codex_ml.cli.codex_cli status-report`
- `codex_ml.cli.codex_cli deploy --dry-run`
- and linking the latest `docs/status_updates/survey-<ring>-and-<PR>-<DATESTAMP>.md`

## Architecture at a glance

The canonical topology is captured in [`docs/diagrams/architecture.svg`](diagrams/architecture.svg). Pair it with the
Mermaid source (`architecture.mmd`) when proposing changes so reviewers can diff rendered assets and source together.

Key flows:

1. **Authoring** — Hydra configuration layers resolve reasoning templates from `configs/training/reasoning/*` before model
   instantiation.
2. **Training** — Training is orchestrated by:
   - `src/codex_ml/training/unified_training.py`
     (deterministic seeding, checkpoint / resume plumbing,
      continual replay strategy hooks),
   - `src/codex_ml/train_loop.py`
     (per-run executor that injects the reasoning harness,
      logs traces, and rotates checkpoints).
   These modules together are "the trainer".
   They replace older references to a standalone
   `codex_ml.trainer.ReasoningTrainer`.
3. **Deployment** — Bespoke models are packaged with manifest digests
   and signed hooks for downstream registries.

When modifying the topology, update both the diagram and [`docs/guides/serving_reproducibility.md`](guides/serving_reproducibility.md).

## Hosting bespoke reasoning models

1. **Bootstrap the project**
   ```bash
   uv sync --extra reasoning --extra cli --frozen
   source .venv/bin/activate
   codex repo-map --reasoning
   ```
2. **Select a template** using `codex reasoning-templates list` (see [`codex_cli`](../src/codex_cli/app.py)). Templates
   live under `configs/training/reasoning/` and ship default datasets plus evaluator bindings.
3. **Materialise runtime overlays**
   ```bash
   codex-train +reasoning=baseline curriculum.phase_schedule=starter
   ```
   This composes reasoning overrides on top of the legacy defaults so classical experiments keep working.
4. **Register the artifact** with deterministic metadata before handoff:
   ```bash
   codex register --bundle artifacts/runs/reasoning-baseline \
     --expect manifest.sha256 --tag reasoning/m0/bespoke
   ```

For service integrations, adopt the PodSpec defined in
[`docs/deployment/reasoning_pod.md`](deployment/reasoning_pod.md).
This PodSpec is a **dry-run template**, not production hosting.
Its job is to make resource shape, telemetry, curriculum phase,
trace capture mode, and rollout ring explicit before anything moves
toward `main`. A dry-run configuration is provided at
[`configs/deploy/reasoning_pod.yaml`](../configs/deploy/reasoning_pod.yaml).
Link the generated manifest to your rollout plan.

## Guided reasoning pipelines

Follow the deep dives in the new guides:

- [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md) — systems overview and milestone guardrails.
- [`docs/guides/first_principles_curricula.md`](guides/first_principles_curricula.md) — curriculum design and evaluation cadences.

### Training quickstart

```bash
codex-train +reasoning=baseline \
  curriculum.phase_schedule=starter \
  training.max_steps=500 \
  logging.reasoning_trace=true \
  training.output_dir=artifacts/runs/reasoning-starter
```text

The `+reasoning=baseline` defaults hook into `configs/training/reasoning/baseline.yaml` and emit trace artefacts that downstream
analysis notebooks can load. Curricula definitions are stored as YAML fragments so you can diff changes between cohorts.

### Evaluation handoff

```bash
codex evaluate --config configs/evaluation/reasoning.yaml \
  --log-metrics .codex/metrics/reasoning.ndjson \
  --run-id reasoning-milestone-m1
```text

Every evaluation appends to the NDJSON ledger with per-phase metrics. Use `codex metrics summarize` for quick trend
checks when preparing milestone readouts.

### Deployment checks

```bash
codex deploy --config configs/deploy/reasoning_pod.yaml \
  --dry-run

# Optional: if your train loop emits run metadata to a non-default path:
# codex deploy --config configs/deploy/reasoning_pod.yaml \
#   --run-metadata-dir runs/train_loop \
#   --dry-run
```text
Always leave `--dry-run` in place. The manifest is a review artifact, not a production action, and the embedded
`rollout_ring` is an intent badge rather than permission to ship. Dry runs confirm manifest parity, bundler signatures,
and runtime allowances required by bespoke hosts. Redeployments should always be paired with
`codex reasoning-templates explain <name>` to document why a template was chosen.

## Offline validation helpers

```bash
HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CODEX_MLFLOW_ENABLE=0 WANDB_MODE=offline \
  nox -s tests_offline
```text

This run exports standard offline toggles and keeps artefacts under `.codex/` for reproducibility (metrics, checkpoints,
reasoning traces). Combine it with `codex_cli.app checkpoint-smoke` to validate serialization paths without GPUs.

## Next steps

1. Align sprint planning with the [milestones](#reasoning-roadmap-milestones).
2. Review [`docs/guides/reasoning_overview.md`](guides/reasoning_overview.md) before opening architecture PRs.
3. Wire bespoke hosting expectations into status reports using the templates in [`docs/templates`](templates/README.md).
