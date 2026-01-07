# config_legacy Module (Deprecated)

**⚠️ DEPRECATED - DO NOT USE**

This directory was renamed from `hydra/` to `config_legacy/` to prevent shadowing of the `hydra-core` package from site-packages.

## Background

Having a local `hydra/` directory in the repository root creates "split-brain" ambiguity:
- Python's import system Phase 5 resolve `import hydra` to this local directory instead of the installed `hydra-core` package
- This causes inconsistent behavior depending on `PYTHONPATH` and import order
- It violates the principle of single source of truth for package resolution

## Migration Guide

### For Users
**Do NOT import from this module.** Use the standard hydra-core package instead:

```python
# ❌ OLD (deprecated)
from config_legacy import compose, initialize_config_dir

# ✅ NEW (correct)
import hydra
from hydra import compose, initialize_config_dir
```

### For Maintainers
This shim module will be removed in a future version. All references to `hydra/` or `config_legacy/` should be refactored to use the official `hydra-core` package.

## Removal Timeline
- **Current**: Deprecated with warnings
- **Next major version**: Module will be removed entirely

## References
- Remediation tracking: See `docs/validation/Convergence_Runbook.md`
- Shadowing detection: `scripts/remediation/verify_conflicts.py`
- Import analysis: `scripts/remediation/analyze_legacy_usage.py`
