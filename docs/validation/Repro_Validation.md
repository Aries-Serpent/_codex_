# Validation: Reproducibility — Seed, Env Snapshot, Checkpoint Metadata

> Generated: 2024-11-05 07:27:25 | Author: mbaetiong

## Objective

Validate deterministic behavior, environment snapshot emission, and checkpoint metadata presence in the codex_ml evaluation and training pipelines.

## Prerequisites

- Local repository clone with changes from status audit implementation
- Python 3.10+ installed
- No network access required

## Validation Checklist

### 1. Deterministic Evaluation

**Command**:
```bash
nox -s repro_smoke
```text

**Expected Outcome**:
- `tests/test_metrics_generative.py` passes
- `tests/eval/test_eval_provenance_capture.py` passes  
- `tests/plugins/test_metric_plugin_loading.py` passes
- Exit code 0

**What This Validates**:
- Evaluation produces identical metrics when run with same seed
- Environment snapshot is written with correct fields
- Git commit hash is captured when available

**Troubleshooting**:
- If tests fail due to missing dependencies, install with: `pip install -e .[metrics]`
- If git commit is unavailable, test accepts `None` or empty string (acceptable for non-git environments)

### 2. Environment Snapshot Emission

**Command**:
```bash
# Run a sample evaluation
python -m pytest tests/eval/test_eval_provenance_capture.py::test_evaluation_captures_git_commit_in_provenance -v
```text

**Expected Outcome**:
- Test creates `output_dir/provenance/environment.json`
- File contains:
  - `python`: Python version string
  - `platform`: Platform string
  - `git_commit`: Git commit hash (or null if git unavailable)
  - `pip_freeze`: List of installed packages

**Inspect Output**:
```bash
# After test run, check the generated file
cat /tmp/pytest-of-*/pytest-current/test_evaluation_captures_git_*/eval_output/provenance/environment.json
```text

**Expected Structure**:
```json
{
  "python": "3.12.3 (main, ...)",
  "platform": "Linux-...",
  "git_commit": "abc123def456...",
  "pip_freeze": ["package==1.0.0", ...],
  "hardware": {...}
}
```text

### 3. Checkpoint Metadata Version

**Note**: This validation focuses on the checkpoint metadata format. The actual checkpoint tests are in Phase 1 (deferred).

**What To Verify**:
- Checkpoint manager includes `format_version` in `.meta.json`
- Checkpoint manager includes `codex_commit` in `.meta.json` (when git available)

**File Location**:
- Implementation: `training/checkpoint_manager.py` or `src/codex_ml/checkpointing/`
- Tests: Phase 1 tests (deferred in current batch)

**Expected Metadata Structure**:
```json
{
  "format_version": "1.0",
  "codex_commit": "abc123...",
  "created_at": "2024-11-05T...",
  "model_config": {...}
}
```text

## Acceptance Criteria

| Check | Command | Expected Result | Status |
|-------|---------|----------------|--------|
| Reproducibility smoke tests | `nox -s repro_smoke` | All tests pass | ✓ |
| Environment snapshot fields | Inspect `environment.json` | Contains python, platform, git_commit, pip_freeze | ✓ |
| Deterministic metrics | Run evaluation twice with same seed | Identical metric values | ✓ |
| Plugin loading non-fatal | Plugin init in tests | Does not raise, returns int count | ✓ |
| System metrics toggle (optional) | `codex-train --system-metrics ...` | Emits system metrics without changing training determinism | ✓ |

## Notes

### Network Independence

All validation steps work offline:
- No external API calls
- No package downloads (after initial installation)
- No git clone operations

### Git Availability

If git is unavailable:
- `git_commit` field may be `null` or empty string
- This is acceptable and documented
- Tests handle this gracefully

### Optional Dependencies

Generative metrics (BLEU/ROUGE) are optional:
- Tests pass whether dependencies are installed or not
- Metrics return `None` when dependencies missing
- Runner raises clear error only when explicitly requested

## Troubleshooting

### Test Failures

**Issue**: `nox -s repro_smoke` fails with import errors

**Solution**:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or install package with extras
pip install -e ".[metrics,test]"
```text

**Issue**: Git commit not captured

**Solution**:
- Verify you're in a git repository: `git rev-parse HEAD`
- If not in git repo, this is expected; tests handle gracefully
- Check provenance module handles this: `python -c "from codex_ml.utils.provenance import _git_commit; print(_git_commit())"`

**Issue**: Environment snapshot missing fields

**Solution**:
- Check that `export_environment()` is being called in eval runner
- Verify output directory permissions
- Review test output for specific field that's missing

### Performance

Smoke tests should complete in < 10 seconds:
- If slower, check for network calls (should be none)
- Verify pytest plugin autoload is disabled
- Check test isolation

## See Also

- [Reproducibility Guide](../repro.md) - Detailed reproducibility documentation
- [Metrics Validation](Metrics_Validation.md) - Generative metrics validation
- [Plugin Guide](../guides/plugins.md) - Plugin system documentation
