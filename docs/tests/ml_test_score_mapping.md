# ML Test Score Mapping for `_codex_` (Scaffolding)

This document describes how `_codex_` maps tests to ML Test Score
categories using `codex_ml_test_map.yaml` and `tools/codex_mltest_runner.py`.

## 1. Categories

We use the following categories (aligned with ML Test Score practices):

- `data`
- `model`
- `infrastructure`
- `regression`
- `performance`

Each test entry in `codex_ml_test_map.yaml` specifies:

- `id` – unique identifier
- `category` – one of the above
- `description` – short summary
- `pytest_target` – argument passed to `pytest`

## 2. Running ML Tests

To run all mapped tests:

```bash
python tools/codex_mltest_runner.py \
  --repo-root . \
  --json-summary codex_mltest_summary.json
```

To run a specific category:

```bash
python tools/codex_mltest_runner.py \
  --repo-root . \
  --category infrastructure \
  --json-summary codex_mltest_infra_summary.json
```

The runner:

* Reads `codex_ml_test_map.yaml`.
* Selects entries matching the requested categories.
* Executes `pytest <pytest_target> -q` for each.
* Writes a JSON summary with:
  * Overall return code
  * Per-target stdout/stderr and exit status.

## 3. Integration with Task Sequence

`codex_task_sequence.yaml` uses:

* `tools/codex_mltest_runner.py` with category `infrastructure` during
  Best-Effort Construction.

The summary files (e.g. `codex_mltest_infra_summary.json`) can be
referenced from:

* Reproducibility manifest
* Gap registry
* Future dashboards and reporting.
