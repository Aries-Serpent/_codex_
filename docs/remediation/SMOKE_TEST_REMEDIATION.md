# Smoke Test Remediation Plan

## Problem Statement

Three smoke tests are currently failing in the test suite:
1. `test_cli_determinism_wiring` - Missing `codex_script` module
2. `test_validate_ok` - CLI parameter mismatch
3. `test_validate_bad` - CLI parameter mismatch

These are pre-existing failures not introduced by recent changes, but they should be addressed to maintain test suite health.

## Root Cause Analysis

### Test 1: test_cli_determinism_wiring

**Issue**: Test attempts to import `codex_script` module which doesn't exist.

**Expected**: 
```python
cs = importlib.import_module("codex_script")
assert hasattr(cs, "_init_determinism_from_env")
```

**Actual**: Module not found

**Root Cause**: Feature was planned but not implemented. Test was added speculatively.

### Tests 2-3: test_validate_ok/test_validate_bad

**Issue**: CLI runner is treating "file" as a positional argument instead of a subcommand.

**Expected**: `CliRunner().invoke(app, ["file", str(cfg)])`

**Actual**: Gets error "Invalid value for 'CONFIG_PATH': Path 'file' does not exist"

**Root Cause**: CLI structure Phase 5 have changed or test setup is incorrect.

## Proposed Solutions

### Option A: Complete the Implementation (Recommended)

Create the missing functionality to make tests pass.

#### For test_cli_determinism_wiring:

Create `src/codex_ml/cli/determinism.py` or add to existing module:

```python
# src/codex_ml/codex_script.py
import os

def _init_determinism_from_env():
    """Initialize determinism from environment variables."""
    if os.getenv("CODEX_DETERMINISM") == "1":
        seed = int(os.getenv("CODEX_SEED", "42"))
        num_threads = int(os.getenv("CODEX_NUM_THREADS", "1"))
        
        # Apply deterministic settings
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)
        
        # Set PyTorch if available
        try:
            import torch
            torch.manual_seed(seed)
            torch.set_num_threads(num_threads)
        except ImportError:
            pass
        
        return {
            "determinism_enabled": True,
            "seed": seed,
            "num_threads": num_threads
        }
    return {"determinism_enabled": False}
```

#### For test_validate_ok/test_validate_bad:

Fix the CLI invocation or update the app structure:

```python
# In tests/smoke/test_config_validate_cli.py
# Change from:
r = CliRunner().invoke(app, ["file", str(cfg)])

# To (if app has subcommands):
r = CliRunner().invoke(app.commands["file"], [str(cfg)])

# Or update the CLI app in codex_ml.cli.validate to have "file" as a command
```

### Option B: Skip Tests Temporarily (Quick Fix)

Mark tests as expected failures until implementation is complete:

```python
@pytest.mark.xfail(reason="codex_script module not yet implemented - see issue #XXXX")
def test_cli_determinism_wiring(monkeypatch):
    ...

@pytest.mark.xfail(reason="CLI structure needs update - see issue #XXXX")  
def test_validate_ok(tmp_path: Path):
    ...
```

### Option C: Remove Tests (Not Recommended)

Only if the features are definitely not planned.

## Recommendation

**Implement Option A** for the following reasons:
1. Determinism functionality is valuable for ML reproducibility
2. Config validation is a core feature
3. Tests represent intended functionality
4. Completing features improves codebase maturity

**Timeline**: 
- Determinism module: 2-4 hours
- CLI validation fix: 1-2 hours
- Testing and validation: 1 hour
- **Total**: ~1 business day

## Implementation Steps

1. Create `src/codex_ml/codex_script.py` with determinism functionality
2. Add tests to verify the module works correctly
3. Investigate CLI structure for validate command
4. Fix CLI invocation in tests or CLI app structure
5. Run smoke tests to verify fixes
6. Update documentation

## Success Criteria

- All smoke tests pass
- New functionality is properly tested
- Documentation updated
- No regressions in other tests

## Related Issues

- Smoke test failures tracked in PR #2459
- Related to determinism audit capabilities
- Part of broader test coverage improvement initiative
