# _codex_ Reproducibility Checklist (Scaffolding)

This document tracks the core ingredients needed for **basic reproducibility**
of experiments and gap-resolution runs in `_codex_`.

The checklist is intentionally minimal and aligned with the current
implementation state. It can be expanded as the system matures.

## 1. Seeds & RNG

- [x] Global seed helper available:
  - `codex_ml.utils.reproducibility.set_global_seed(seed)`.
- [x] Simple RNG snapshot helper:
  - `codex_ml.utils.reproducibility.capture_rng_snapshot()`.

Operational guidance:

- At the start of any training or evaluation script, call
  `set_global_seed(<int>)` once.
- Record the chosen seed in:
  - experiment config (`conf/experiment/*.yaml`), and/or
  - run metadata (future tracking integrations).

## 2. Environment Snapshot

- [x] Environment snapshot tool:
  - `tools/codex_env_snapshot.py`
  - Outputs:
    - `codex_env_snapshot.json` (machine-readable)
    - `codex_env_snapshot.md` (human-readable)

Suggested use:

```bash
python tools/codex_env_snapshot.py
```

Run this alongside or shortly after executing a significant experiment or
gap-resolution sequence so the snapshot reflects the environment used.

## 3. Gap & Task Sequence Artifacts
- Gap registry:
  - `codex_gap_registry.yaml`
- YAML coverage report:
  - `codex_yaml_gap_report.md`
- Gap trends:
  - `codex_gap_trends.md`
- Change log:
  - `codex_change_log.md`
- Error questions:
  - `codex_error_questions.md`
- ML Test Score infra summary:
  - `codex_mltest_infra_summary.json` (from codex_mltest_runner.py)

These are produced by combinations of:
- `tools/codex_gap_registry.py`
- `tools/codex_yaml_gap_check.py`
- `tools/codex_gap_trends.py`
- `tools/codex_mltest_runner.py`
- `tools/codex_task_sequence_runner.py`
- `tools/codex_gap_pipeline.py`

## 4. Reproducibility Bundle Manifest
- Bundle manifest tool:
  - `tools/codex_reproducibility_bundle.py`
- Output:
  - `codex_reproducibility_manifest.json`

Example invocation:

```bash
python tools/codex_reproducibility_bundle.py \
  --audit _codex_status_update-2025-11-27.md \
  --manifest-out codex_reproducibility_manifest.json
```

The manifest references (best-effort):
- Audit file
- Gap registry + reports
- Change log + error questions
- ML test infra summary
- Environment snapshot (JSON + Markdown)
- Dependency audit and secret scan outputs

## 5. Minimal Reproducibility Flow
1. Set a global seed at the start of your script.
2. Run the task sequence (or at least the Search & Mapping + Best-Effort Construction phases).
3. Run ML Test Score–driven tests (e.g. infra category).
4. Capture the environment snapshot.
5. Generate the reproducibility manifest.

This sequence provides a solid baseline for reasoning about past runs and
debugging issues, while remaining lightweight and local-only.
