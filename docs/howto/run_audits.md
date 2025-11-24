# How-to: run audits and collect experiment summaries

1. Execute your training or evaluation runs. Each invocation of `codex-train`
   records events under `artifacts/experiments/<run_id>/` using NDJSON.
2. After a batch of runs, aggregate results:
   ```bash
   python scripts/analyze_experiments.py --base-dir artifacts/experiments
   ```
   This generates `artifacts/experiment_summary.md` and
   `artifacts/experiment_summary.json`.
3. Feed the summary into the audit scorecard:
   ```bash
   python -m codex_ml.cli.detectors run
   ```
   The detector suite now includes an `experiment_summary` check that reports the
   number of runs and aggregated metrics.
4. Attach the markdown summary to review artifacts. It references only local
   outputs and respects offline mode.

If experiments are missing, the detector reports a zero score and points to the
expected summary path.
