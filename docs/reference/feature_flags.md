# Feature Flags (Local-Only Guards)

All feature flags are disabled by default and must be explicitly enabled via environment variables.

## Available Flags

### `CODEX_ENABLE_PEFT=1`
Enable PEFT (Parameter-Efficient Fine-Tuning) hooks. Requires optional `peft` dependency.

**Default**: Disabled  
**Usage**:
```bash
export CODEX_ENABLE_PEFT=1
python -m codex_ml.cli.train --config config.yaml
```text

### `CODEX_ENABLE_MLFLOW=1`
Enable MLflow experiment tracking (local filesystem only).

**Default**: Disabled  
**Tracking URI**: `file:artifacts/mlruns`  
**Usage**:
```bash
export CODEX_ENABLE_MLFLOW=1
python -m codex_ml.eval.runner --config config.yaml
```text

### `CODEX_ENABLE_PERF_SAMPLER=1`
Enable performance sampling during evaluation (CPU/GPU/memory metrics).

**Default**: Disabled  
**Output**: `artifacts/logs/perf.ndjson`  
**Requirements**: `psutil` (optional: `pynvml` for GPU metrics)  
**Usage**:
```bash
export CODEX_ENABLE_PERF_SAMPLER=1
python -m codex_ml.eval.runner --config config.yaml
```text

### `CODEX_ENABLE_SIGNING`
Enable cryptographic signing for archive standardization.

**Default**: Disabled (uses mock signing)  
**Usage**:
```bash
export CODEX_ENABLE_SIGNING=true
python -m codex.archive.cli validate-standardization --check-signatures
```text

## Design Principles

1. **Opt-in**: All features disabled by default
2. **Offline-first**: No network calls when enabled
3. **Graceful degradation**: Missing dependencies don't cause failures
4. **Local-only**: All outputs to local filesystem
5. **Reversible**: Can disable without code changes

## Adding New Flags

When adding a new feature flag:
1. Use `CODEX_` prefix
2. Check with `os.getenv("CODEX_FLAG_NAME") == "1"`
3. Wrap in try/except for graceful failure
4. Document in this file
5. Add to relevant documentation
