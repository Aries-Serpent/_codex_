# Coverage Remediation Implementation Summary

## Objectives Achieved

✅ **1. Eliminate collection errors**
- Fixed typer.Typer import issues
- Fixed torch._C import issues with CPU-only wheels
- Fixed ConfigStore.exists() AttributeError with safe_exists shim

✅ **2. Deterministic dependencies**
- CPU-only torch wheels (2.3.1+cpu) installed via noxfile with explicit index-url
- Prevents CUDA variant installation
- Python 3.11 for stability

✅ **3. Prevent duplicate test module import mismatch**
- Renamed tests/eval/test_metrics.py → tests/eval/test_evaluation_metrics.py
- Removed original file to avoid shadowing

✅ **4. Add fail-fast preflight sanity**
- Enhanced .github/scripts/ci_dependency_sanity.py
- Runs before pytest in coverage session
- Validates critical imports and API presence

✅ **5. Add pytest marker**
- Added 'interfaces' marker to pytest.ini

## Files Modified

### A. requirements-dev.txt
- Updated pytest: 7.4.4 → >=9.0.0
- Added typer>=0.12.5, click>=8.1.7
- Added hydra-core>=1.3.2, pydantic>=2.5.0, defusedxml>=0.7.1, jsonschema>=4.22.0, requests>=2.31.0
- Removed torch entries (installed via noxfile with CPU index)

### B. noxfile.py (coverage session)
- Explicitly install typer>=0.12.5, click>=8.1.7
- Install CPU-only torch trio with --index-url https://download.pytorch.org/whl/cpu
- Run preflight script (.github/scripts/ci_dependency_sanity.py) before pytest
- Added inline pycache cleanup
- Enforces repo coverage ≥95% and per-target ≥96%

### C. .github/scripts/ci_dependency_sanity.py
- Added typer to CRITICAL imports
- Changed hydra.core → hydra.core.config_store for specificity
- Print module __file__ paths for diagnostics
- Check hasattr(typer, "Typer") for API validation
- Return exit code 2 on failure, 0 on success

### D. src/codex_ml/utils/hydra_cs.py
- Enhanced safe_exists(config_store, name, group=None)
- Handles ConfigStore.list(path) API correctly
- Returns True if config exists, False otherwise
- Compatible with both old and new Hydra versions

### E. src/codex_ml/cli/config.py
- Import safe_exists from codex_ml.utils.hydra_cs
- Use safe_exists(cs, name="app") instead of cs.exists(name="app")
- Use safe_exists(cs, group="experiment", name="debug") for grouped configs
- Prevents AttributeError on older Hydra versions

### F. tests/eval/test_evaluation_metrics.py
- Renamed from test_metrics.py to avoid import shadowing
- Original file removed from repository

### G. pytest.ini
- Added 'interfaces' marker to suppress warnings

### H. .github/workflows/ci.yml (coverage job)
- Set Python version: "3.11" (downgrade from 3.12 for torch CPU stability)
- Added pycache purge step before installing dependencies
- Run dependency sanity check before nox -s coverage

## Verification Tests

### Preflight Sanity Check
```
$ python .github/scripts/ci_dependency_sanity.py
[sanity] Checking critical imports...
[sanity] ✓ torch: /path/to/torch/__init__.py
[sanity] ✓ torch.nn.functional: /path/to/torch/nn/functional.py
[sanity] ✓ typer: /path/to/typer/__init__.py
[sanity] ✓ hydra.core.config_store: /path/to/hydra/core/config_store.py
[sanity] ✓ transformers: /path/to/transformers/__init__.py
[sanity] ✓ typer.Typer: present
[sanity] ✓ hydra.core.ConfigStore: importable
[sanity] ✓ All critical imports OK.
```

### Torch CPU Verification
```python
import torch
print('CUDA available:', torch.cuda.is_available())  # False
print('Torch version:', torch.__version__)  # 2.3.1+cpu
```

### safe_exists Function Tests
```python
Test 1 - name only: True
Test 2 - group + name: True
Test 3 - non-existent: False
Test 4 - wrong group: False
✓ All safe_exists tests passed
```

### register_configs Idempotency
```python
register_configs()  # First call
register_configs()  # Second call - no errors
✓ Idempotent registration successful
```

### Renamed Test File
```
$ pytest tests/eval/test_evaluation_metrics.py -v
tests/eval/test_evaluation_metrics.py::test_perplexity_from_logits PASSED
tests/eval/test_evaluation_metrics.py::test_token_accuracy PASSED
2 passed in 0.14s
```

### Security Scan
```
CodeQL: 0 alerts (python, actions)
```

## Determinism Anchors

| Variable | Value |
|----------|-------|
| CODEX_SEED | 42 |
| CODEX_DETERMINISM | 1 |
| HF_HUB_OFFLINE | 1 |
| TRANSFORMERS_OFFLINE | 1 |
| CODEX_OPTIONAL_SOFTFAIL | 1 |
| Python Version | 3.11 |
| Torch Version | 2.3.1+cpu |
| Pytest Version | >=9.0.0 |

## Post-Implementation Reporting

| Gate | Status | Notes |
|------|--------|-------|
| Preflight | ✅ | Module paths logged, all imports OK |
| Torch Import | ✅ | _C present, no NameError, CPU-only (2.3.1+cpu) |
| Typer CLI | ✅ | typer.Typer constructed and validated |
| Hydra ConfigStore | ✅ | safe_exists used, no AttributeError, idempotent |
| Metrics Tests | ✅ | No import file mismatch (renamed to test_evaluation_metrics.py) |
| Coverage XML | ⏳ | Will be generated in CI (artifacts/coverage.xml) |
| Targets ≥96% | ⏳ | Will be validated in CI |
| Repo ≥95% | ⏳ | Will be validated in CI (--cov-fail-under=95) |
| Warnings | ✅ | Only expected warnings (pydantic_settings) |
| Security | ✅ | 0 CodeQL alerts |

## Next Steps

1. CI pipeline will run coverage session with these changes
2. Verify artifacts/coverage.xml is generated
3. Confirm repo coverage ≥95%
4. Confirm per-target files achieve ≥96%:
   - src/codex_ml/evaluation/loop.py
   - src/codex_ml/evaluation/cli.py
   - src/codex_ml/checkpointing/bestk.py
   - src/codex_ml/logging/registry.py
   - src/codex/ast/cli.py
   - tools/validate_experiments.py

## Commit History

1. `00d91a3` - Initial plan
2. `c397418` - ci: stabilize coverage session (typer, torch CPU, hydra shim, pycache purge)
3. `cf149c1` - fix: remove index-url from requirements-dev.txt (handled by noxfile)
4. `0a33cec` - fix: improve safe_exists to handle ConfigStore.list() API correctly
