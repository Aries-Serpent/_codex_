# Gap 19 Verification: DVC CI Pipeline Wiring

**Verdict:** NEEDS_WORK
**Date:** 2026-06-05

---

## DVC Pipeline Stages

`dvc.yaml` exists at repo root and defines **two pipeline stages**:

### Stage 1 — `prepare`
```yaml
prepare:
  cmd: python -m hhg_logistics.data.prepare "${params.paths.raw_input}" "${params.paths.prepared_dir}"
  deps:
    - src/hhg_logistics/data/prepare.py
    - "${params.paths.raw_input}"
  params:
    - prepare.seed
    - prepare.split
    - paths.raw_input
    - paths.prepared_dir
  outs:
    - "${paths.prepared_dir}"
```

### Stage 2 — `train_baseline`
```yaml
train_baseline:
  cmd: python -m hhg_logistics.train train.enable=true
  deps:
    - src/hhg_logistics/train.py
    - src/hhg_logistics/model/peft_utils.py
    - src/hhg_logistics/model/adapters.py
    - "${data.processed_dir}/features.csv"
  outs:
    - "${data.models_dir}"
```

Source files referenced by both stages **do exist** under `src/hhg_logistics/`.

---

## CI Integration Status

### `.dvc/` directory
- **MISSING.** `dvc init` has never been run. No `.dvc/` directory exists in the repository.

### `.dvc/config` (remote storage)
- **MISSING.** No remote storage backend (S3, GCS, Azure, local) has been configured.

### `params.yaml`
- **MISSING.** `dvc.yaml` references `params.paths.*`, `prepare.*`, and `data.*` via DVC params, but `params.yaml` does not exist at the repo root. `dvc repro` would fail immediately.

### `.dvc` tracked artifact files
- **NONE FOUND.** No `*.dvc` pointer files exist, meaning no artifacts are currently DVC-tracked.

### `.dvcignore`
- **EXISTS** at repo root. Contains standard exclusions (`.venv/`, `.git/`, `mlruns/`, etc.). This is the only DVC-related file that is properly in place.

### Workflow scan results
- Searched all `.github/workflows/*.yml` for: `dvc repro`, `dvc pull`, `dvc push`, `dvc run`, `dvc reproduce`
- **Result: ZERO MATCHES** — no workflow calls any DVC command.

### `data-quality-suite.yml`
- Exists and runs on PRs to `main`, `develop`, `0D_base_`, etc.
- Contains two jobs: `data_validation` (manifest/drift checks) and `determinism_check` (double-run pytest with `@pytest.mark.determinism`).
- **Does NOT invoke any DVC commands.** It calls `scripts/validate_dataset.py` and `scripts/check_data_drift.py`, which are independent of DVC.

### Artifact hash stability
- DVC-managed artifact version tracking is **not operational**: no `.dvc` pointer files, no remote, no `dvc repro` in CI. CI does not capture DVC-managed artifact versions.

---

## Missing Pieces (NEEDS_WORK)

| # | Missing Component | Required Action |
|---|-------------------|-----------------|
| 1 | `.dvc/` directory | Run `dvc init` and commit `.dvc/.gitignore` + `.dvc/config` |
| 2 | `params.yaml` | Create with `paths`, `prepare`, and `data` parameter namespaces matching `dvc.yaml` references |
| 3 | DVC remote storage | Configure a remote (`dvc remote add`) and commit `.dvc/config`; at minimum a local/CI-scoped remote for reproducibility checks |
| 4 | `*.dvc` artifact pointer files | Run `dvc add` on managed data/model artifacts and commit pointer files |
| 5 | CI workflow step invoking `dvc repro` | Add a CI step (ideally in `data-quality-suite.yml` or a new `dvc-pipeline.yml`) that runs `dvc pull && dvc repro --no-commit` and uploads stage outputs as artifacts |
| 6 | Artifact hash capture | Add a CI step that runs `dvc status` or `dvc params diff` and uploads the result as a workflow artifact for audit |

---

## Summary

`dvc.yaml` is a well-structured pipeline definition with two reproducible stages (`prepare` → `train_baseline`). However, DVC itself has **never been initialized** in this repository — the `.dvc/` directory, remote configuration, `params.yaml`, and all artifact pointer files are absent. No CI workflow invokes any DVC command. The gap label "needs CI pipeline wiring" understates the situation: the local DVC setup also needs to be completed before CI wiring is meaningful.
