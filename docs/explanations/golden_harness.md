# Golden Harness integration

The Golden Harness remains the contract for tracing and auditing training
behaviour. The new experiment tracking utilities complement it by writing
structured NDJSON suitable for scorecards without relying on MLflow or W&B.

- Use `start_run` / `finish_run` to bracket significant phases.
- Emit metrics with `log_metric` so downstream auditors can calculate trends.
- Aggregate runs with `scripts/analyze_experiments.py`; the generated JSON feeds
  the `experiment_summary` detector.

Because all artifacts are local, the harness can run in air-gapped environments
while preserving reproducibility evidence.
