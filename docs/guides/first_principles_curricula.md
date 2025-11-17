# First principles curricula

Curriculum-first training anchors the reasoning roadmap. This guide walks through how we design, stage, and evaluate
curricula across training, evaluation, and deployment.

## Design principles

1. **Start from the target metric** — Anchor every phase on the milestone gate (for example M1 win rate ≥0.55).
2. **Minimise hidden state** — Curriculum YAML fragments must be diff-friendly; prefer declarative overrides to custom code.
3. **Embed observability** — Each phase should emit trace markers (`phase_id`, `prompt_complexity`) for downstream dashboards.
4. **Document fallback paths** — Capture baselines in [`../status_updates/`](../status_updates/) before experimenting.

## Curriculum blueprint

| Phase | Objective | Dataset preset | Signals |
| --- | --- | --- | --- |
| Warm-up | Stabilise reasoning traces | `datasets/reasoning/warmup.jsonl` | Trace coverage, loss | 
| First principles | Teach decomposition heuristics | `datasets/reasoning/first_principles.jsonl` | Win rate, critique density |
| Challenge set | Stress bespoke behaviors | `datasets/reasoning/challenge.jsonl` | Latency deltas, judge disagreement |

Phase definitions live in `configs/training/reasoning/curricula/`. Each YAML file exports:

```yaml
phase_schedule:
  - id: warmup
    dataset: datasets/reasoning/warmup.jsonl
    steps: 200
  - id: first_principles
    dataset: datasets/reasoning/first_principles.jsonl
    steps: 400
  - id: challenge
    dataset: datasets/reasoning/challenge.jsonl
    steps: 300
```text

## Training pipeline

1. **Select** a curriculum file (for example `curriculum=first_principles`).
2. **Launch** training with explicit overrides:
   ```bash
   codex-train +reasoning=baseline \
     curriculum=first_principles \
     logging.reasoning_trace=true \
     training.output_dir=artifacts/runs/first-principles
   ```
3. **Monitor** traces with `codex metrics summarize --metric reasoning.trace_coverage`.
4. **Record** qualitative notes (prompt outliers, judge disagreements) in `status_updates/first_principles.md`.

## Evaluation pipeline

1. Materialise evaluation packs:
   ```bash
   codex datasets materialize --preset reasoning/first_principles
   ```
2. Run evaluators with curriculum tags:
   ```bash
   codex evaluate --config configs/evaluation/reasoning.yaml \
     curriculum.id=first_principles \
     --log-metrics .codex/metrics/reasoning.ndjson
   ```
3. Compare against baselines via `codex metrics compare --metric reasoning.win_rate --reference baseline`.
4. Capture feedback loops in `status_updates/first_principles.md`.

## Deployment pipeline

1. Verify the bundle:
   ```bash
   codex deploy --config configs/deploy/reasoning_pod.yaml \
     --model artifacts/runs/first-principles:last \
     --dry-run
   ```
2. Shadow host until latency and judge deltas meet the milestone gate.
3. Register the model with curriculum metadata:
   ```bash
   codex register --bundle artifacts/runs/first-principles:last \
     --tag reasoning/m1/first-principles \
     --notes "Curriculum M1 rollout"
   ```
4. Update rollout docs under [`../deployment/`](../deployment/) with observed risks or mitigations.

## Troubleshooting

- **Trace gaps** — Re-run with `logging.reasoning_trace=true` and verify `.codex/reasoning_runs/` contains phase markers.
- **Evaluator regressions** — Use `codex evaluate --metrics-only` to isolate metric drift before replaying full judge sweeps.
- **Deployment parity** — If bespoke hosts diverge, capture diffs in `status_updates/` and raise an action item against the M2
  gate.

Curricula evolve with the roadmap. Submit updates alongside milestone retrospectives and link the diff in your status report.
