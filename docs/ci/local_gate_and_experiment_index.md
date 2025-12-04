# Local Gate Runner and Experiment Index

This document summarizes the lightweight tooling that exercises local quality
gates and indexes experiment metadata for quick review.

## Local Gate Runner

`tools/codex_local_gate_runner.py` executes shell commands defined in a YAML
configuration file (default: `codex_local_gate.yaml`). Each gate is a simple
command such as a pytest target or a formatting check. The runner captures
stdout/stderr, writes a JSON summary (`codex_local_gate_report.json`), and emits
a Markdown table (`codex_local_gate_report.md`).

Example configuration:

```yaml
gates:
  - name: tools-smoke
    cmd: "python -m pytest tests/tools -q"
  - name: codex-ml-smoke
    cmd: [python, -m, pytest, tests/codex_ml, -q]
```

Run the gates:

```bash
python tools/codex_local_gate_runner.py --repo-root . \
  --config codex_local_gate.yaml \
  --json-out codex_local_gate_report.json \
  --md-out codex_local_gate_report.md
```

The exit code reflects the last failing gate (or `0` if all succeed), making
the tool safe to include in larger task sequences.

## Experiment Index

`tools/codex_experiment_index.py` scans `runs/` for `meta.json` or
`experiment_meta.json` files and aggregates them into
`codex_experiment_index.json` plus a Markdown companion. The index captures the
relative path to each meta file and the loaded metadata payload, simplifying
post-run inspection and reproducibility tracking.

Usage:

```bash
python tools/codex_experiment_index.py --runs-dir runs \
  --json-out codex_experiment_index.json \
  --md-out codex_experiment_index.md
```

If no runs are present, the tool still produces empty outputs, making it safe
to run in automated pipelines.
