# Experiment Records

Well-structured experiment notes make it easy to reproduce results and reason about follow-up work. This template captures the
minimum metadata required to tie together configuration snapshots, dataset manifests, run logs, and conclusions.

Use the template below when documenting a significant run (new model checkpoints, dataset versions, or evaluation results). All
fields are expected unless noted otherwise.

## Template

```markdown
# Experiment: <short title>
- **Date:** YYYY-MM-DD
- **Owner(s):** <name(s)>
- **Related PRs / Issues:** <links>
- **Run IDs:** <primary run ID(s)>
- **Seed(s):** <integer seeds used>

## Goals
- What question does this experiment answer?
- What hypothesis is being tested?

## Configuration
- **CLI invocation:** `python -m codex_ml.cli.train ...`
- **Config snapshot:** Reference to `params.ndjson` entry or inline summary of key options (learning rate, scheduler, etc.).
- **Derived parameters:** Effective batch size, tokens per update, gradient accumulation, etc.

## Data & Provenance
- **Datasets:** name, version/source, and pointers to manifests.
- **Checksums:** link to `split_manifest.json` and `split_checksums.json` (or equivalent) produced by the run.
- **Input revisions:** git commit SHA, dataset release tag, or storage URI.

## Results
- Primary metrics for train/val/test (include confidence intervals where relevant).
- Link to `metrics.ndjson`, TensorBoard, MLflow, or other dashboards.
- Screenshots or tables summarising final outcomes.

## Analysis
- Interpretation of the results: what worked, what regressed, and surprises.
- Comparison to previous baselines or control runs.
- Notable logs, anomalies, or qualitative findings.

## Follow-ups
- [ ] Immediate fixes or re-runs required.
- [ ] Longer-term ideas unlocked by this experiment.
- [ ] Documentation or code updates required.

## Artifacts
- `params.ndjson` – CLI/config snapshot.
- `metrics.ndjson` – structured metrics log.
- Additional artefacts (plots, checkpoints, notebooks).
```

### Usage Notes

1. Store experiment write-ups under the `experiments/` directory. File names should include the date and a short slug
   (for example, `experiments/2025-01-12_token_baseline.md`).
2. Reference run artefacts by relative path, and link to external dashboards (TensorBoard, MLflow) when enabled.
3. When multiple runs contribute to a single conclusion, summarise the aggregate findings and include a table mapping run IDs to
   their respective artefacts.
4. Cross-link PRs or issues that implemented follow-up actions so future readers can trace decisions back to implementation
   details.

A sample record using this template is available in `experiments/2025-01-15_smoke.md`.
