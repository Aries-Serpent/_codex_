# API Docs Build Troubleshooting

> Common Pitfalls & Fixes

## Overview

This guide addresses common issues encountered when building API documentation with pdoc3 and provides solutions.

## Common Issues

### 1. ImportError on optional dependencies

**Symptom**:
```text
ImportError: No module named 'wandb'
ImportError: No module named 'tensorboard'
ImportError: cannot import name 'functional' from 'torch.nn'
```
**Cause**: The module being documented imports optional dependencies that aren't installed.

**Solutions**:

**Option A**: Add to allowlist in validator
```bash
python tools/validate_api_docs.py \
  --package codex_ml \
  --allow-optional "wandb" "tensorboard" "torch" "transformers" "peft" "accelerate"
```

**Option B**: Gate imports in source code
```python
# In module that uses optional dependencies
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    wandb = None

# Use conditional imports
if WANDB_AVAILABLE:
    # wandb code here
    pass
```

**Option C**: Install optional dependencies
```bash
pip install -e ".[all]"  # Install all optional dependencies
# or
pip install wandb tensorboard  # Install specific ones
```

---

### 2. pdoc unavailable offline

**Symptom**:
```json
{
  "build_report": {
    "built": false,
    "notes": "pdoc unavailable: ModuleNotFoundError: No module named 'pdoc'"
  }
}
```

**Solution**:

```bash
# Install pdoc3
pip install pdoc3

# Or let the build script install it automatically
python tools/build_api_docs.py
```

**Offline workaround**: The validator will print a "skipped" note and exit gracefully.

---

### 3. Missing package on PYTHONPATH

**Symptom**:
```text
ModuleNotFoundError: No module named 'codex'
ModuleNotFoundError: No module named 'codex_ml'
```
**Cause**: Python can't find the package modules.

**Solutions**:

**Option A**: Install in editable mode (recommended)
```bash
pip install -e .
```

**Option B**: Set PYTHONPATH manually
```bash
export PYTHONPATH=/path/to/repo/src:$PYTHONPATH
python tools/build_api_docs.py
```

**Option C**: The build script automatically adds `src/` to path (already handled)

---

### 4. No HTML outputs after build

**Symptom**:
```json
{
  "build_report": {
    "built": true,
    "file_count": 0
  }
}
```

**Causes & Fixes**:

1. **Package has no public modules**
   - Verify package `__init__.py` exposes modules
   - Check that modules have public classes/functions

2. **Wrong package name**
   ```bash
   # Check available packages
   python -c "import codex.cli; print(codex.cli.__file__)"
   ```

3. **Clear artifacts and retry**
   ```bash
   rm -rf artifacts/docs/api/*
   python tools/build_api_docs.py
   ```

---

### 5. Modules not discovered during import scan

**Symptom**: Expected modules don't appear in documentation

**Causes & Fixes**:

1. **Missing `__init__.py`**
   - Ensure all package directories have `__init__.py`

2. **Namespace package configuration**
   ```python
   # In __init__.py
   from . import submodule  # Explicit import
   ```

3. **Dynamic imports not discovered**
   - pdoc scans static imports; ensure modules are imported in `__init__.py`

---

### 6. Local `torch` directory conflicts

**Symptom**:
```text
ImportError: cannot import name 'functional' from 'torch.nn' (/path/to/torch/nn/__init__.py)
```
**Cause**: A local `torch/` directory shadows the real PyTorch package.

**Solution**:
```bash
# Rename or remove local torch directory
mv torch torch_local

# Or ensure it's not in PYTHONPATH
```

---

### 7. Deprecation warnings in docs

**Symptom**:
```text
DeprecationWarning: codex_ml.interfaces.tokenizer_hf is deprecated
```
**Fix**: These are informational and don't block the build. To suppress:

```bash
python -W ignore::DeprecationWarning tools/build_api_docs.py
```

---

### 8. Permission denied writing to output directory

**Symptom**:
```text
PermissionError: [Errno 13] Permission denied: 'artifacts/docs/api'
```
**Solution**:
```bash
# Ensure directory is writable
chmod -R u+w artifacts/docs/

# Or use a different output directory
python tools/build_api_docs.py --output-dir /tmp/api_docs
```

---

### 9. Build succeeds but pages are blank

**Symptom**: HTML files generated but have no content

**Causes & Fixes**:

1. **Missing docstrings**
   ```python
   # Add module-level docstring
   """
   Module description here.
   """
   
   def my_function():
       """Function description."""
       pass
   ```

2. **Private modules (starting with `_`)**
   - pdoc3 skips private modules by default
   - Rename modules to not start with underscore if they should be public

---

### 10. Slow build performance

**Symptom**: Build takes a long time

**Solutions**:

1. **Build specific packages only**
   ```bash
   # Instead of all of codex_ml, build submodules
   python tools/build_api_docs.py --package codex.cli
   ```

2. **Skip optional modules**
   ```bash
   python tools/build_api_docs.py --skip-optional
   ```

3. **Use incremental builds** (not implemented yet)

---

## Diagnostic Commands

### Check package importability
```bash
# Test if package can be imported
PYTHONPATH=src python -c "import codex.cli; print('✓ codex.cli importable')"
PYTHONPATH=src python -c "import codex_ml; print('✓ codex_ml importable')"
```

### List package modules
```bash
# See what modules are discovered
python -c "
import pkgutil
import codex.cli
for mod in pkgutil.walk_packages(codex.cli.__path__, prefix='codex.cli.'):
    print(mod.name)
"
```

### Check pdoc installation
```bash
pdoc --version
python -c "import pdoc; print(pdoc.__version__)"
```

### Verify build output
```bash
# Check what was generated
find artifacts/docs/api -name "*.html" | head -20
```

## Escalation

If issues persist after trying these solutions:

1. **Gather information**:
   ```bash
   python tools/validate_api_docs.py \
     --package codex.cli \
     --out artifacts/docs/api \
     --summary > validation_report.json
   ```

2. **Include environment details**:
   ```bash
   python --version
   pip list | grep -E "pdoc|sphinx"
   echo $PYTHONPATH
   ```

3. **Attach the JSON report** and command used to reproduce

4. **Open an issue** on GitHub with `[docs]` tag

## Best Practices

### For Module Authors

1. **Add docstrings** to all public modules, classes, and functions
2. **Gate optional imports** with try/except
3. **Document parameters and return types** in docstrings
4. **Keep import dependencies minimal** for documentation modules

### For Documentation Builders

1. **Start with small packages** (like `codex.cli`) before attempting full builds
2. **Use `--skip-optional`** for minimal environments
3. **Check import errors** before debugging pdoc issues
4. **Keep output directory clean** between builds

## Related Documentation

- [API Build Validation Guide](../validation/API_Docs_Build_Validation.md)
- [API Documentation Guide](../api/README.md)
- [Build Script Documentation](../api/README.md#building-api-documentation)

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Import error on optional dep | Add to `--allow-optional` list |
| Missing PYTHONPATH | Run `pip install -e .` |
| No HTML output | Check package name and module structure |
| pdoc not found | Run `pip install pdoc3` |
| Stale artifacts | `rm -rf artifacts/docs/api/*` |
| Slow build | Use `--skip-optional` or build smaller packages |
