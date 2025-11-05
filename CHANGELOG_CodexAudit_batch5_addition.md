
---

## Batch 5: Experiment Tracking & Config Discovery

**RC Items**: RC-11, RC-12, RC-13  
**Date**: 2025-11-05  
**Commits**: Current

### Changes

#### MLflow Offline Metadata Enrichment

**File**: `src/codex_ml/eval/runner.py`

**Change**: Added best-effort MLflow parameter logging when `CODEX_ENABLE_MLFLOW=1`

**Parameters Logged**:
```python
# When CODEX_ENABLE_MLFLOW=1 is set
mlflow.log_param("codex_git_commit", os.getenv("CODEX_GIT_COMMIT", ""))
mlflow.log_param("conda_env", os.getenv("CONDA_DEFAULT_ENV", ""))
mlflow.log_param("seed", seed_value)
mlflow.log_param("dataset_path", str(dataset_path.resolve()))
```

**Error Handling**: All logging wrapped in try-except; failures silently ignored

**Enablement**:
```bash
export CODEX_ENABLE_MLFLOW=1
export CODEX_GIT_COMMIT=$(git rev-parse --short HEAD)  # optional
# Run evaluation
```

#### MLflow Local UI Viewer

**File**: `scripts/tracking/mlflow_ui.sh` (new)

**Purpose**: Launch MLflow UI against local file store

**Usage**:
```bash
scripts/tracking/mlflow_ui.sh
# Access at: http://localhost:5000
```

**Environment**:
- `MLFLOW_TRACKING_URI`: Default `file:./mlruns`
- Port: 5000 (configurable)

**File**: `docs/tracking/Offline_MLflow.md` (new)

**Sections**:
- Overview of offline MLflow tracking
- Parameters logged and their sources
- Usage instructions
- Troubleshooting guide

#### Config Groups Discovery Tool

**File**: `tools/configs/list_groups.py` (new)

**Purpose**: Discover and list Hydra config groups (offline)

**Output Format**: JSON
```json
{
  "roots": ["/path/to/configs", ...],
  "note": "For fuller listing, use Hydra's compose API"
}
```

**Usage**:
```bash
python tools/configs/list_groups.py
# Or via nox
nox -s config_index
```

#### Nox Sessions

**File**: `noxfile.py` (updated)

**Sessions Added**:

1. `tracking_smoke` - MLflow file backend smoke test
```python
@nox.session(name="tracking_smoke")
def tracking_smoke(session: nox.Session) -> None:
    """Run local MLflow smoke test against file backend."""
    session.env["MLFLOW_TRACKING_URI"] = "file:./mlruns"
    # Creates mlruns directory and verifies setup
```

2. `config_index` - List Hydra config groups
```python
@nox.session(name="config_index")
def config_index(session: nox.Session) -> None:
    """List Hydra config groups (offline discovery)."""
    session.run("python", "tools/configs/list_groups.py")
```

**File**: `configs/development/noxfile.py` (updated)

**Session Added**: `config_index` (development variant with helpers)

### Rollback

```bash
git checkout <batch5_commit>~1 -- \
  src/codex_ml/eval/runner.py \
  scripts/tracking/mlflow_ui.sh \
  docs/tracking/Offline_MLflow.md \
  tools/configs/list_groups.py \
  noxfile.py \
  configs/development/noxfile.py
```

**Impact**: None. MLflow logging is opt-in; config discovery is informative only.

---

