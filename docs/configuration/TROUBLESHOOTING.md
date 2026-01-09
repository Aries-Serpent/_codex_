# Configuration Troubleshooting Guide

**Last Updated:** 2026-01-09  
**PS-01 Status:** Cycle 3 (Validation & Testing)

---

## Common Issues and Solutions

### Issue 1: Config File Not Found

**Symptom:**
```
MissingConfigException: Missing config file: conf/model/myconfig.yaml
```

**Cause:** Config file doesn't exist at specified path

**Solutions:**

1. **Check file exists:**
   ```bash
   ls -la conf/model/myconfig.yaml
   ```

2. **Use correct config name (without .yaml extension):**
   ```python
   # Wrong
   cfg = load_config("base.yaml", config_dir="conf/model")
   
   # Correct
   cfg = load_config("base", config_dir="conf/model")
   ```

3. **Enable fallback to legacy location:**
   ```python
   cfg = load_config("base", config_dir="conf/model", allow_fallback=True)
   ```

4. **Check if file is in legacy location:**
   ```bash
   find configs/ -name "myconfig.yaml"
   ```

---

### Issue 2: Module Not Found Error

**Symptom:**
```
ModuleNotFoundError: No module named 'codex'
```

**Cause:** Package not installed

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or without editable mode
pip install .
```

---

### Issue 3: YAML Syntax Error

**Symptom:**
```
yaml.scanner.ScannerError: while scanning a simple key
```

**Cause:** Invalid YAML syntax in config file

**Solutions:**

1. **Validate YAML syntax:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('conf/model/base.yaml'))"
   ```

2. **Common YAML mistakes:**
   ```yaml
   # Wrong: Missing space after colon
   key:value
   
   # Correct
   key: value
   
   # Wrong: Inconsistent indentation
   training:
     epochs: 10
       batch_size: 8
   
   # Correct: Consistent 2-space indentation
   training:
     epochs: 10
     batch_size: 8
   ```

3. **Check for tabs (YAML requires spaces):**
   ```bash
   grep -P '\t' conf/model/base.yaml
   ```

---

### Issue 4: Interpolation Not Working

**Symptom:**
```
Config shows literal "${training.epochs}" instead of value
```

**Cause:** Hydra not available or config not loaded via ConfigLoader

**Solutions:**

1. **Use ConfigLoader (not direct YAML loading):**
   ```python
   # Wrong
   import yaml
   with open("conf/training/base.yaml") as f:
       cfg = yaml.safe_load(f)  # Interpolation won't work
   
   # Correct
   from codex.utils.config_loader import load_config
   cfg = load_config("base", config_dir="conf/training")
   ```

2. **Check Hydra availability:**
   ```python
   try:
       import hydra
       print("Hydra available")
   except ImportError:
       print("Hydra not available - install with: pip install hydra-core")
   ```

---

### Issue 5: Attribute Access Fails

**Symptom:**
```
AttributeError: 'dict' object has no attribute 'training'
```

**Cause:** OmegaConf not available, config returned as dict

**Solution:**

Use dict access instead of attribute access:
```python
# Wrong (only works if OmegaConf available)
epochs = cfg.training.epochs

# Correct (always works)
epochs = cfg["training"]["epochs"]

# Or use .get() for safety
epochs = cfg.get("training", {}).get("epochs", 10)
```

---

### Issue 6: Duplicate Key Warning

**Symptom:**
```
DuplicateKeyError: found duplicate key 'epochs' in config
```

**Cause:** Same key defined multiple times in YAML

**Solution:**

1. **Find duplicate:**
   ```bash
   grep -n "epochs:" conf/training/base.yaml
   ```

2. **Use interpolation for aliases:**
   ```yaml
   # Wrong: Duplicate definition
   training:
     epochs: 10
   epochs: 10
   
   # Correct: Use interpolation
   training:
     epochs: 10
   epochs: ${training.epochs}
   ```

---

### Issue 7: Override Not Applied

**Symptom:**
```
Override "training.epochs=5" specified but value is still 10
```

**Cause:** Incorrect override syntax or order

**Solutions:**

1. **Check override syntax:**
   ```python
   # Wrong: Missing equals sign
   overrides = ["training.epochs 5"]
   
   # Wrong: Spaces around equals
   overrides = ["training.epochs = 5"]
   
   # Correct
   overrides = ["training.epochs=5"]
   ```

2. **Check key path:**
   ```yaml
   # Config structure
   training:
     params:
       epochs: 10
   
   # Wrong override path
   overrides = ["training.epochs=5"]
   
   # Correct override path
   overrides = ["training.params.epochs=5"]
   ```

3. **Verify override is applied:**
   ```python
   cfg = load_config("base", overrides=["training.epochs=5"])
   print(f"Epochs: {cfg['training']['epochs']}")  # Should print 5
   ```

---

### Issue 8: ImportError for Config Legacy

**Symptom:**
```
ImportError: cannot import name 'MissingConfigException' from 'config_legacy.errors'
```

**Cause:** Circular import or package not installed

**Solutions:**

1. **Install package:**
   ```bash
   pip install -e .
   ```

2. **Use new import path:**
   ```python
   # Old (deprecated)
   from config_legacy.errors import MissingConfigException
   
   # New (recommended)
   from codex.utils.config_loader import MissingConfigException
   ```

---

### Issue 9: Hydra Extras Warning

**Symptom:**
```
RuntimeWarning: Hydra extras plugin (`hydra.extra`) is unavailable
```

**Cause:** Optional Hydra extras not installed

**Solutions:**

1. **Install with test extras:**
   ```bash
   pip install -e '.[test]'
   ```

2. **Or install hydra-core:**
   ```bash
   pip install hydra-core==1.3.2
   ```

3. **Suppress warning for tests:**
   ```bash
   export CODEX_ALLOW_MISSING_HYDRA_EXTRA=1
   pytest tests/
   ```

---

### Issue 10: Config Loading Too Slow

**Symptom:**
```
Config loading takes >1 second
```

**Cause:** Large config hierarchy or slow file I/O

**Solutions:**

1. **Profile loading time:**
   ```python
   import time
   from codex.utils.config_loader import load_config
   
   start = time.time()
   cfg = load_config("base", config_dir="conf/training")
   print(f"Load time: {time.time() - start:.3f}s")
   ```

2. **Cache loaded configs:**
   ```python
   # Create singleton loader
   from codex.utils.config_loader import get_loader
   
   loader = get_loader()  # Cached globally
   cfg = loader.load_config("base", config_dir="conf/training")
   ```

3. **Reduce config hierarchy depth:**
   - Flatten deeply nested defaults lists
   - Consolidate related configs

---

### Issue 11: Deprecation Warning

**Symptom:**
```
DeprecationWarning: config_legacy.errors is deprecated
```

**Cause:** Using deprecated import path

**Solution:**

Update imports:
```python
# Old (deprecated)
from config_legacy.errors import MissingConfigException

# New (recommended)
from codex.utils.config_loader import MissingConfigException
```

---

### Issue 12: Config Not Found in Tests

**Symptom:**
```
Tests pass locally but fail in CI with MissingConfigException
```

**Cause:** Config path not accessible from CI environment

**Solutions:**

1. **Use allow_fallback in tests:**
   ```python
   cfg = load_config("base", config_dir="conf/model", allow_fallback=True)
   ```

2. **Create test fixtures:**
   ```python
   @pytest.fixture
   def test_config(tmp_path):
       config_dir = tmp_path / "conf" / "model"
       config_dir.mkdir(parents=True)
       
       config_file = config_dir / "base.yaml"
       config_file.write_text("model:\n  name: test")
       
       return tmp_path
   
   def test_something(test_config):
       from codex.utils.config_loader import ConfigLoader
       loader = ConfigLoader(repo_root=test_config)
       cfg = loader.load_config("base", config_dir="conf/model")
   ```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from codex.utils.config_loader import load_config
cfg = load_config("base", config_dir="conf/model")
```

### Inspect Config Structure

```python
from codex.utils.config_loader import load_config

cfg = load_config("base", config_dir="conf/training")

# Print all keys
print("Config keys:", list(cfg.keys()) if hasattr(cfg, 'keys') else dir(cfg))

# Print full config
from pprint import pprint
pprint(dict(cfg) if hasattr(cfg, 'items') else cfg)
```

### Verify Interpolation Resolution

```python
from omegaconf import OmegaConf

cfg = load_config("base", config_dir="conf/training")

# Check if value is interpolation
if OmegaConf.is_interpolation(cfg, "epochs"):
    print("epochs is an interpolation")
    
# Get interpolation target
if OmegaConf.is_interpolation(cfg, "epochs"):
    print(f"Resolves to: {cfg.epochs}")
```

---

## Getting Help

### 1. Check Documentation
- [CONFIG_USAGE.md](CONFIG_USAGE.md) - Usage patterns and examples
- [HYDRA_MIGRATION_GUIDE.md](HYDRA_MIGRATION_GUIDE.md) - Migration instructions
- [MIGRATION_MAPPING.md](MIGRATION_MAPPING.md) - Config inventory and mapping

### 2. Check Test Examples
```bash
# See test cases for correct usage
cat tests/test_config_loader.py
```

### 3. Validate Config File
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('conf/model/base.yaml'))"

# Check with ConfigLoader
python -c "
from codex.utils.config_loader import load_config
cfg = load_config('base', config_dir='conf/model')
print('✓ Config loads successfully')
"
```

### 4. File an Issue
If problem persists:
1. Create GitHub issue with label "configuration"
2. Include:
   - Error message and stack trace
   - Config file content (sanitized)
   - Steps to reproduce
   - Environment details (Python version, OS)

---

## Quick Reference

### Essential Commands

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('file.yaml'))"

# Test config loading
python -c "from codex.utils.config_loader import load_config; load_config('base', config_dir='conf/model')"

# Run config tests
pytest tests/test_config_loader.py -v

# Find config files
find conf/ -name "*.yaml"

# Check for deprecated imports
grep -r "from config_legacy" src/ tests/
```

### Environment Variables

```bash
# Suppress Hydra extras warning
export CODEX_ALLOW_MISSING_HYDRA_EXTRA=1

# Enable debug logging
export CODEX_LOG_LEVEL=DEBUG
```

---

## Reporting Bugs

When reporting configuration-related bugs, include:

1. **Error message:** Full stack trace
2. **Config file:** Content (sanitize sensitive data)
3. **Code snippet:** How you're loading the config
4. **Environment:**
   ```bash
   python --version
   pip list | grep -E "(hydra|omegaconf|pyyaml)"
   ```
5. **Steps to reproduce:** Minimal example

---

**Maintained By:** PS-01 Configuration Consolidation  
**Last Updated:** 2026-01-09  
**Questions:** File an issue with "configuration" label
