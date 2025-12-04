# Environment Snapshot and Dependency Report

This guide describes the lightweight, offline tooling that captures the local execution context for _codex_. The artifacts are intended to be fast to generate and easy to audit, forming the base inputs for downstream reproducibility manifests.

## Environment Snapshot

`tools/codex_env_snapshot.py` records high-signal details about the current interpreter and platform:

- Python version and executable path
- Host platform metadata (system, release, machine)
- Full environment variables (sorted for determinism)
- Installed distributions via `importlib.metadata`

Example usage:

```bash
python tools/codex_env_snapshot.py --out codex_env_snapshot.json
```

The output is a JSON document suitable for offline archival. Include it with experiment outputs to support later debugging or manifest generation.

## Dependency Report

`tools/codex_dependency_report.py` enumerates installed Python packages and their versions using `importlib.metadata`. It mirrors the snapshot format and sorts package names alphabetically for consistency.

```bash
python tools/codex_dependency_report.py --out codex_dependency_report.json
```

The report is intentionally minimal—no network calls or package resolution are performed—ensuring it can be run in locked-down environments.

## Relationship to Reproducibility Manifest

Both artifacts feed into the reproducibility manifest builder. When running `tools/codex_repro_manifest.py`, supply the snapshot and dependency paths via `--env-snapshot` and `--dep-report` to embed the captured context in the consolidated report.

## ML Test Runner Stub

`tools/codex_mltest_runner.py` provides a category-aware wrapper over pytest using the structured mapping in `codex_ml_test_map.yaml`. It is designed for quick smoke validation across data, model, infra, regression, and performance buckets.

```bash
python tools/codex_mltest_runner.py --map codex_ml_test_map.yaml --category data --json-summary codex_mltest_results.json
```

The summary JSON reports the overall return code and per-category test groupings, making it easy to integrate into bespoke task sequences or local gate scripts.
