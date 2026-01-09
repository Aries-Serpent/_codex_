# PS-01: Configuration Consolidation Deployment Guide

## Prerequisites
- Python 3.9+
- Hydra 1.3+
- Repository access

## Deployment Steps

### Step 1: Install Dependencies
```bash
pip install --no-cache-dir hydra-core omegaconf
```

### Step 2: Verify Configuration Structure
```bash
ls -la conf/
# Should contain: errors/, model/, services/
```

### Step 3: Test Configuration Loading
```python
from codex.utils.config_loader import load_config
cfg = load_config("base", config_dir="conf/model")
print(cfg)
```

### Step 4: Run Validation Tests
```bash
pytest tests/test_config_loader.py -v
```

### Step 5: Deploy to Production
```bash
# Copy conf/ directory
cp -r conf/ $PRODUCTION_PATH/conf/

# Verify environment variables
echo $CODEX_CONFIG_DIR
```

## Rollback Procedure
```bash
# Restore legacy configs
cp -r configs/ $PRODUCTION_PATH/configs/

# Revert code to previous commit
git checkout HEAD~1 -- src/codex/utils/config_loader.py
```

## Verification
- [ ] Configuration loads without errors
- [ ] All 30 tests passing
- [ ] Dual-path fallback working
- [ ] Performance: Config loading <100ms

**Status:** ✅ Production Ready
**Last Updated:** 2026-01-09
