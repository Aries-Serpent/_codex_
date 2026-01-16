# Legacy Code Migration Guide

**Created:** 2026-01-16  
**Status:** Reference Documentation  
**Version:** 1.0.0

---

## Executive Summary

This guide documents the deprecated legacy shim modules (`config_legacy/` and `yaml_legacy/`) and provides migration guidance for codebases that may have direct imports.

## Deprecated Modules

### config_legacy/

**Status:** ⚠️ DEPRECATED - Shim for hydra-core  
**Recommended:** Use `import hydra` directly

The `config_legacy/` module is a backward-compatibility shim that was created when the local `hydra/` directory was renamed to avoid shadowing the installed `hydra-core` package.

#### Current Behavior

The module attempts to load the real `hydra-core` package and re-exports its API:

```python
# This is deprecated:
from config_legacy import compose, initialize_config_dir

# Use this instead:
from hydra import compose, initialize_config_dir
```

#### Files Using config_legacy (Current State)

The following files use the fallback pattern `try: import hydra except: import config_legacy`:

| File | Usage Pattern |
|------|---------------|
| `src/cli.py` | Fallback import for compose/initialize_config_dir |
| `src/codex/utils/config_loader.py` | Fallback for MissingConfigException |
| `src/tokenization/train_tokenizer.py` | Fallback import for hydra module |
| `src/hhg_logistics/train.py` | Fallback for hydra and utils |
| `src/hhg_logistics/eval/harness.py` | Fallback import for hydra |
| `src/hhg_logistics/serve/app.py` | Fallback import for hydra |
| `src/hhg_logistics/main.py` | Fallback import for hydra |
| `src/codex_ml/utils/config_loader.py` | Fallback imports |
| `src/codex_ml/cli/train.py` | Fallback for hydra and utils |
| `src/codex_ml/cli/hydra_entry.py` | Fallback import for hydra |
| `src/codex_ml/cli/evaluate.py` | Fallback for to_absolute_path |
| `src/codex_ml/cli/config.py` | Fallback for ConfigStore |
| `src/codex_ml/cli/hydra_main.py` | Fallback import for hydra |

#### Migration Strategy

Since `hydra-core>=1.3.2` is now explicitly required in `pyproject.toml`, the fallback imports should never be triggered in production. The fallback pattern provides safety during development and testing when hydra may not be installed.

**Option A: Keep Fallback Pattern (Recommended for now)**
- Minimal disruption
- Graceful degradation during development
- No breaking changes

**Option B: Remove Fallback (Future v2.0.0)**
- Cleaner codebase
- Breaking change for any external users relying on fallback
- Requires major version bump

### yaml_legacy/

**Status:** ⚠️ DEPRECATED - Shim for PyYAML  
**Recommended:** Use `import yaml` directly

The `yaml_legacy/` module provides a fallback when PyYAML is not installed, using JSON parsing as a minimal substitute.

#### Current Behavior

```python
# This is deprecated:
from yaml_legacy import safe_load, safe_dump

# Use this instead:
from yaml import safe_load, safe_dump
```

#### Usage Status

**No direct imports found** - The yaml_legacy module is not directly imported anywhere in the codebase. It can be safely removed in a future version.

## Migration Commands

### Verify No Breaking Imports

```bash
# Check for config_legacy imports
grep -rn "from config_legacy\|import config_legacy" --include="*.py" src/

# Check for yaml_legacy imports
grep -rn "from yaml_legacy\|import yaml_legacy" --include="*.py" src/

# Verify hydra is importable
python -c "import hydra; print(hydra.__version__)"

# Verify yaml is importable
python -c "import yaml; print(yaml.__version__)"
```

### Run Tests to Verify Migration

```bash
# Run full test suite
pytest tests/ -v

# Run tests that specifically test hydra/config functionality
pytest tests/ -k "hydra or config" -v
```

## Version Upgrade Strategy

### Current (v1.x.x)
- Legacy shims remain for backward compatibility
- Fallback imports provide development flexibility
- No breaking changes

### Future (v2.0.0)
- Consider removing config_legacy/ directory
- Consider removing yaml_legacy/ directory
- Major version bump for breaking change
- Comprehensive migration guide provided

## Dependencies Verified

The following dependencies are now explicitly required and tested:

| Dependency | Version | Purpose |
|------------|---------|---------|
| hydra-core | ==1.3.2 | Configuration management |
| omegaconf | >=2.3 | Configuration library |
| pyyaml | >=6.0 | YAML parsing |

## Support

For questions about legacy code migration:
1. Check this guide
2. Review the planset at `.codex/plans/LEGACY_CODE_REMOVAL_PLANSET.md`
3. Open an issue if migration guidance is needed

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-16
