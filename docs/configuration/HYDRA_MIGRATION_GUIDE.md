# Configuration System Migration Guide

**Status:** PS-01 Pre-commit Cycle 1 Complete  
**Last Updated:** 2026-01-08

## Overview

This guide documents the migration from legacy configuration handling to the new centralized Hydra-based configuration system introduced in Planset 01 (PS-01).

## What Changed

### New Components

1. **Structured Error Configuration** (`conf/errors/defaults.yaml`)
   - Centralized error definitions with codes, severities, and resolutions
   - Categories: config_errors, hydra_errors, filesystem_errors, yaml_errors
   - Default settings for error handling behavior

2. **Centralized Config Loader** (`src/codex/utils/config_loader.py`)
   - Unified API for loading configuration via Hydra Compose API
   - Robust fallback mechanisms for offline/testing environments
   - Support for config overrides and validation
   - 71%+ test coverage

### Deprecated Components

1. **config_legacy/errors.py**
   - Now deprecated with compatibility shim
   - Re-exports from `codex.utils.config_loader.MissingConfigException`
   - Will be removed in future version (Q2 2026)

## Migration Path

### For New Code

Use the new config loader:

```python
from codex.utils.config_loader import load_config, load_error_config

# Load configuration
cfg = load_config("myconfig", config_dir="conf")

# Load error definitions
errors = load_error_config()

# Access structured errors
from codex.utils.config_loader import get_loader
loader = get_loader()
error = loader.get_error("config_errors", "missing_config")
print(error.format())  # [CONFIG_001] Missing configuration file
```

### For Existing Code

Existing imports from `config_legacy.errors` will continue to work but emit deprecation warnings:

```python
# OLD (deprecated but still works)
from config_legacy.errors import MissingConfigException

# NEW (recommended)
from codex.utils.config_loader import MissingConfigException
```

## Configuration File Structure

### Error Configuration Schema

```yaml
# conf/errors/defaults.yaml
category_name:
  error_key:
    code: "ERROR_CODE"
    message: "Error message with {placeholders}"
    severity: "error|warning|info"
    resolution: "How to fix this error"

defaults:
  log_errors: true
  raise_on_error: true
  fallback_enabled: true
```

### Application Configuration

Place your configuration files in `conf/` directory:

```yaml
# conf/myapp.yaml
app:
  name: myapp
  version: 1.0.0

database:
  host: localhost
  port: 5432
```

## API Reference

### ConfigLoader Class

```python
from codex.utils.config_loader import ConfigLoader

loader = ConfigLoader(repo_root=None)  # Auto-detects repo root

# Load configuration
cfg = loader.load_config(
    config_name="base",
    config_dir="conf",
    overrides=["key=value"],
    allow_fallback=True
)

# Get structured error
error = loader.get_error("config_errors", "missing_config")
```

### Global Functions

```python
from codex.utils.config_loader import load_config, load_error_config, get_loader

# Load config using global loader
cfg = load_config("myconfig")

# Load error configuration
errors = load_error_config()

# Get global loader instance
loader = get_loader()
```

## Configuration Overrides

Hydra-style overrides are supported:

```python
cfg = load_config(
    "base",
    overrides=[
        "app.debug=true",
        "database.port=3306",
        "nested.deep.value=42"
    ]
)
```

## Error Handling

### Structured Errors

```python
from codex.utils.config_loader import get_loader

loader = get_loader()
error = loader.get_error("config_errors", "missing_config")

if error:
    print(f"Code: {error.code}")
    print(f"Message: {error.message}")
    print(f"Severity: {error.severity}")
    print(f"Resolution: {error.resolution}")
    
    # Format with context
    formatted = error.format(file="myconfig.yaml")
    print(formatted)
```

### Exception Handling

```python
from codex.utils.config_loader import MissingConfigException, load_config

try:
    cfg = load_config("nonexistent", allow_fallback=False)
except MissingConfigException as e:
    print(f"Missing: {e.missing_cfg_file}")
    print(f"Message: {e.message}")
```

## Testing

### Unit Tests

See `tests/test_config_loader.py` for comprehensive test examples:

- 29 test cases
- 71.29% code coverage
- Tests for success cases, errors, edge cases, and integration

### Test Fixtures

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "conf"
    config_dir.mkdir()
    
    # Create test config
    test_config = config_dir / "test.yaml"
    test_config.write_text("key: value")
    
    return tmp_path
```

## Backward Compatibility

### Compatibility Period

- **Current Phase:** Deprecation warnings active
- **Removal Target:** Q2 2026 (v2.0.0)
- **Support Window:** 2 implementation cycles (6 months)

### Migration Checklist

- [ ] Update imports from `config_legacy.errors` to `codex.utils.config_loader`
- [ ] Move configuration files to `conf/` directory
- [ ] Add error definitions to `conf/errors/defaults.yaml`
- [ ] Update config loading code to use new API
- [ ] Run tests to verify functionality
- [ ] Review and resolve deprecation warnings

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'codex'`
- **Solution:** Install the package: `pip install -e .`

**Issue:** `MissingConfigException` when loading config
- **Solution:** Check config file exists at expected path, or set `allow_fallback=True`

**Issue:** Deprecation warnings from `config_legacy`
- **Solution:** Update imports to use `codex.utils.config_loader`

**Issue:** Hydra extras not available
- **Solution:** Set `CODEX_ALLOW_MISSING_HYDRA_EXTRA=1` for testing, or install hydra-core

### Debug Mode

Enable debug logging to troubleshoot config loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from codex.utils.config_loader import load_config
cfg = load_config("myconfig")
```

## Next Steps

### Pre-commit Cycle 2

- Audit `configs/` directory for migration candidates
- Create migration mapping document
- Move additional configs to `conf/` structure
- Update import paths across codebase

### Pre-commit Cycle 3

- Full test suite validation
- Schema validation implementation
- Usage pattern documentation
- Troubleshooting guide expansion

## References

- Planset 01: `.github/plans/PLANSET_01_CONFIGURATION_CONSOLIDATION.md`
- Hydra Documentation: https://hydra.cc/
- Test Suite: `tests/test_config_loader.py`
- Error Config: `conf/errors/defaults.yaml`

## Support

For issues or questions:
- Check this migration guide
- Review test cases in `tests/test_config_loader.py`
- Consult `.codex/AI_AGENT_UTILITIES_REGISTRY.md`
- File an issue with the "configuration" label
