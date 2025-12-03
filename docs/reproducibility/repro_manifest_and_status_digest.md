# Reproducibility Manifest & Status Digest for `_codex_` (Scaffolding)

This document describes the current reproducibility manifest tooling in
`_codex_`, and how it ties together:

- Environment snapshot
- Dependencies
- Gap registry
- Experiment index
- Local gate (internal CI spine)

The implementation is deliberately minimal and offline-only.

## 1. Tool: `codex_repro_manifest.py`

Path:

- `tools/codex_repro_manifest.py`

Purpose:

- Aggregate several existing artifacts into a single, structured
  manifest and a human-readable Markdown digest.

Inputs (all optional, best-effort):

- `codex_env_snapshot.json`
- `codex_dependency_report.json`
- `codex_gap_registry.yaml`
- `codex_experiment_index.json`
- `codex_local_gate_report.json`

Outputs:

- `codex_reproducibility_manifest.json`
- `codex_reproducibility_manifest.md`

Example usage:

```bash
python tools/codex_repro_manifest.py \
  --repo-root . \
  --env-snapshot codex_env_snapshot.json \
  --dep-report codex_dependency_report.json \
  --gap-registry codex_gap_registry.yaml \
  --experiment-index codex_experiment_index.json \
  --local-gate codex_local_gate_report.json \
  --json-out codex_reproducibility_manifest.json \
  --md-out codex_reproducibility_manifest.md
```

If any of the input files are missing, the corresponding section in the
manifest is marked as `available: false` and omitted from detailed
summaries.

## 2. Manifest Structure

Top-level fields (JSON):

* `generated_at` – UTC timestamp when the manifest was built.
* `repo_root` – repository root path used.
* `inputs` – absolute paths of each input file.
* `summary` – aggregate sections:

  * `environment`
  * `dependencies`
  * `gaps`
  * `experiments`
  * `local_gate`

Each section contains a small, non-sensitive summary:

* Environment:

  * Python version
  * OS platform/release
  * Keys of any `CODEX_*` environment variables.
* Dependencies:

  * Total package count
  * Count of packages marked as `kind: direct` (if present).
* Gaps:

  * Total gaps
  * Counts by `status`
  * Counts by `risk_level`
* Experiments:

  * Total runs
  * Runs by mode (`train`, `eval`, etc.)
  * Unique config paths
* Local gate:

  * Overall return code
  * Total commands
  * List of failed command names.

## 3. Markdown Digest

`codex_reproducibility_manifest.md` is a human-readable summary with:

1. Environment
2. Dependencies
3. Gaps
4. Experiments
5. Local gate

Each section shows whether the corresponding input was available and,
if so, prints small aggregates (counts, modes, status/risk breakdown).

This digest is intended for:

* Quick operator review
* Attaching to internal status reports
* Anchoring reproducibility discussions

## 4. Relationship to Reproducibility Checklist

This manifest addresses several key items from common MLOps
reproducibility checklists:

* **Environment**:

  * Python/OS version recorded in a machine-readable file.
* **Dependencies**:

  * Package counts and direct dependencies recorded.
* **Code & Gaps**:

  * Gaps are captured via `codex_gap_registry.yaml` summaries.
* **Experiments**:

  * Runs and configs are summarized via `codex_experiment_index.json`.
* **Tests / Local CI**:

  * Local gate results (pass/fail) captured and summarized.

It does *not* attempt to solve:

* Full artifact versioning
* Dataset snapshots or hashes
* Cryptographic signing

Those can be added in future iterations, using this manifest as a
stable anchor.

## 5. Integration with Task Sequence

The task sequence (`codex_task_sequence.yaml`) includes a dedicated
step for running `codex_repro_manifest.py` near the end of the
pipeline. This ensures that:

* Each run of the sequence leaves behind a fresh manifest.
* Downstream tools can consume `codex_reproducibility_manifest.*`
  instead of recombining raw inputs.

The step is run with `record_and_continue` error handling, so failures
to build the manifest do not wipe out other work but are recorded in
the logs and gap registry.
