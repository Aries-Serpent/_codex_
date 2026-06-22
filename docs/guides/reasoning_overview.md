# Reasoning overview

**Last Updated:** 2026-06-22

This guide orients you across the systems, checkpoints, and metrics that define the reasoning roadmap. Keep it close when
triaging milestones or proposing architectural changes.

## Milestone guardrails

| Milestone | Gate | Acceptance notes |
| --- | --- | --- |
| M0 | Trace coverage ≥95% on curated templates | Validate with `codex metrics summarize --metric reasoning.trace_coverage`. |
| M1 | Curriculum win rate ≥0.55 on `benchmarks/cot-lite` | Run the curriculum smoke in [First principles curricula](first_principles_curricula.md). |
| M2 | Shadow latency p95 ≤700 ms | Capture with `codex deploy --dry-run --latency-report`. |
| M3 | Weekly redeploy cadence with zero manual overrides | Enforced by the deployment checklist in [`templates/`](../templates/README.md). |

Milestones build sequentially: do not advance without closing action items or documenting explicit risk trade-offs in
[`status_updates/`](../status_updates/).

## Systems topology

1. **Authoring** — Hydra defaults stitch reasoning templates from `configs/training/reasoning/` with classical knobs. Updating a
   template requires bumping the manifest digest and notifying deployment partners.
2. **Training** — Training and trace capture are coordinated by the
   unified training stack:
   - `src/codex_ml/training/unified_training.py`
     exposes configuration for curriculum phases, continual replay,
     and resume strategy,
   - `src/codex_ml/train_loop.py`
     executes a single run, attaches the reasoning harness,
     and logs traces / checkpoints.
   When these docs refer to "the trainer", they mean this pair of
   modules (plus the Hydra overlays in
   `configs/training/reasoning/*`), not a class literally named
   `ReasoningTrainer`.
   Trace payloads mirror the schema described in [`../reference/reasoning_trace.md`](../reference/reasoning_trace.md).
3. **Evaluation** — Evaluators register under `codex_ml.eval.registry`. The reasoning profile uses tiered NDJSON ledgers
   (`.codex/metrics/reasoning.ndjson`) that feed status reports.
4. **Deployment** — Serving pods mount bespoke model bundles and rely on `codex deploy` to enforce manifest parity.

When proposing topology changes, update [`../diagrams/architecture.svg`](../diagrams/architecture.svg) and include a short
rationale in `status_updates/`.

## Training pipeline

1. Select a template: `codex reasoning-templates list` → choose an entry (for example `baseline`).
2. Compose overrides:
   ```bash
   codex-train +reasoning=baseline \
     curriculum.phase_schedule=starter \
     training.max_steps=500
   ```
3. Inspect traces:
   ```bash
   codex metrics summarize --metric reasoning.trace_coverage \
     --source .codex/metrics/reasoning.ndjson
   ```
4. Promote artifacts via `codex register --bundle ... --tag reasoning/<milestone>`.

Use the `curriculum.phase_schedule` knob to align experiment duration with milestone targets. For ablations, document the
variant name in `training.output_dir` so trace comparisons remain legible.

## Evaluation pipeline

1. Generate evaluation inputs with `codex datasets materialize --preset reasoning/baseline`.
2. Run the evaluator:
   ```bash
   codex evaluate --config configs/evaluation/reasoning.yaml \
     --run-id reasoning-milestone-m1 \
     --log-metrics .codex/metrics/reasoning.ndjson
   ```
3. Append commentary to `status_updates/<milestone>.md` summarising regressions or deltas.
4. Trigger the optional smoke: `codex evaluate --config ... --metrics-only` for dashboard-friendly output.

## Deployment pipeline

1. Validate manifests:
   ```bash
   codex deploy --config configs/deploy/reasoning_pod.yaml \
     --run-metadata-dir runs/train_loop/latest \
     --dry-run
   ```
   The deploy command consumes the offline `run_metadata.json` emitted by the
   training pipeline. Point `--run-metadata-dir` at the directory containing that
   file (for example, `runs/train_loop/latest`).
2. Shadow host in the target environment and confirm p95 latency ≤700 ms.
3. Update [`../deployment/reasoning_pod.md`](../deployment/reasoning_pod.md) with any override notes.
4. Promote the template via `codex reasoning-templates explain <name>` and store the explanation alongside the rollout PR.

## Observability

- **Trace ledger** — `.codex/metrics/reasoning.ndjson` (mirrors the evaluation ledger for quick correlation).
- **Model registry** — `artifacts/runs/<experiment>` seeded by `codex register`.
- **Redeploy dashboard** — Link your dashboards in [`../status_updates/README.md`](../status_updates/README.md) so releases can
  reference the same views.

Keep observability wiring hermetic: do not rely on third-party plugins without documenting mocks or fallbacks.
