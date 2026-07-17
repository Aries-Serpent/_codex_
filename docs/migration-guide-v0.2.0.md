# Migration Guide: v0.1.x to v0.2.0

**Version**: v0.2.0  
**Release Date**: 2026-07-20T02:00Z  
**Compatibility**: Python 3.12+  
**Breaking Changes**: None - Full backward compatibility maintained

---

## Overview

This migration guide provides step-by-step instructions for upgrading from codex-ml v0.1.x to v0.2.0. This is a stable production release with no breaking changes, focusing on performance optimization, security enhancements, and test coverage improvements.

---

## Table of Contents

1. [Pre-Upgrade Checklist](#pre-upgrade-checklist)
2. [Upgrade Procedures](#upgrade-procedures)
3. [Configuration Updates](#configuration-updates)
4. [Verification Steps](#verification-steps)
5. [Rollback Procedures](#rollback-procedures)
6. [Compatibility Matrix](#compatibility-matrix)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Upgrade Checklist

Before upgrading to v0.2.0, complete the following verification steps:

### 1. Verify Current Installation

```bash
# Check installed version
pip show codex-ml

# Expected output format:
# Name: codex-ml
# Version: 0.1.x
# ...

# Verify Python version
python --version
# Required: Python 3.12 or higher
```

### 2. Backup Current Configuration

```bash
# Backup existing configuration (if applicable)
cp -r ~/.codex ~/.codex.backup.0.1.x
cp -r ./config ./config.backup.0.1.x 2>/dev/null || true
```

### 3. Document Dependencies

```bash
# Export current dependency tree
pip freeze > requirements.frozen.0.1.x
pip freeze --all > requirements.all.0.1.x

# Save for comparison after upgrade
```

### 4. Review Active Processes

```bash
# Ensure no active codex-ml processes
ps aux | grep codex_ml

# Stop any running services gracefully
# Terminate any batch jobs that can wait until after upgrade
```

---

## Upgrade Procedures

### Step 1: Create Virtual Environment (Recommended)

```bash
# Create isolated environment for testing
python3.12 -m venv venv_0.2.0

# Activate virtual environment
source venv_0.2.0/bin/activate  # On macOS/Linux
# OR
venv_0.2.0\Scripts\activate  # On Windows
```

### Step 2: Upgrade Package

#### Option A: Direct Upgrade (Recommended)

```bash
# Upgrade to v0.2.0 with dependency resolution
pip install --upgrade codex-ml==0.2.0

# Verify installation
pip show codex-ml
# Expected output: Version: 0.2.0
```

#### Option B: Staged Upgrade with Constraints

```bash
# Install v0.2.0 with constraints file
pip install --upgrade codex-ml==0.2.0 \
    --constraint requirements.txt

# If constraints conflict, resolve manually
pip install --upgrade codex-ml==0.2.0 \
    --use-deprecated=legacy-resolver
```

#### Option C: Testing in Isolated Environment

```bash
# Create test environment
python3.12 -m venv test_env_0.2.0
source test_env_0.2.0/bin/activate

# Install v0.2.0 in test environment
pip install codex-ml==0.2.0

# Test imports and basic functionality (see Verification Steps below)

# If successful, proceed with main environment upgrade
```

### Step 3: Update Dependencies

```bash
# Resolve dependency tree
pip install --upgrade --force-reinstall codex-ml==0.2.0

# Verify no conflicts
pip check

# Expected output: No broken requirements found
```

---

## Configuration Updates

### No Configuration Changes Required

v0.2.0 maintains full backward compatibility with v0.1.x configurations. No changes are required to:

- YAML configuration files
- Environment variables
- API configuration
- Database schemas
- Cache settings

### Optional: Leverage New Performance Features

If desired, you can enable performance optimizations introduced in v0.2.0:

#### Enable Parallel Test Execution (Recommended)

```bash
# If using pytest, enable pytest-xdist
pip install pytest-xdist>=3.0.0

# Run tests with parallelization
pytest -n auto tests/

# Disable if conflicts with existing plugins
pytest --no-xdist tests/
```

#### Enable Cache Optimization

```python
# In your code, no changes required - cache optimization is automatic
# Previous behavior: Manual cache configuration
# New behavior: Automatic cache layer detection and optimization

from codex_ml.cache import CacheManager

# Usage remains identical to v0.1.x
cache = CacheManager()
value = cache.get("key", default=None)
cache.set("key", value, ttl=3600)
```

---

## Verification Steps

### 1. Verify Installation Success

```bash
# Check version
python -c "from codex_ml import __version__; print(__version__)"
# Expected output: 0.2.0

# Check installation location
python -c "import codex_ml; print(codex_ml.__file__)"
```

### 2. Test Core Imports

```bash
# Create test_imports.py
python << 'EOF'
import sys
try:
    from codex_ml.telemetry import Telemetry
    print("✓ Telemetry module imported successfully")
    
    from codex_ml.metrics import MetricsRegistry
    print("✓ Metrics module imported successfully")
    
    from codex_ml.safety import SafetyModeration
    print("✓ Safety module imported successfully")
    
    print("\n✓ All core imports successful")
    sys.exit(0)
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
EOF
```

### 3. Run Basic Functionality Tests

```bash
# Telemetry test
python << 'EOF'
from codex_ml.telemetry import Telemetry
telemetry = Telemetry()
print(f"Telemetry initialized: {telemetry is not None}")
EOF

# Metrics test
python << 'EOF'
from codex_ml.metrics import MetricsRegistry
registry = MetricsRegistry()
print(f"Metrics registry initialized: {registry is not None}")
EOF
```

### 4. Run Test Suite (If Available)

```bash
# Run tests from installed package
pytest codex_ml/tests/ -v

# Expected: Test suite completes with 100% pass rate
```

### 5. Performance Verification

```bash
# Verify performance improvements are applied
python << 'EOF'
import time
from codex_ml.cache import CacheManager

# Test cache performance
cache = CacheManager()
start = time.time()

for i in range(1000):
    cache.set(f"key_{i}", f"value_{i}", ttl=3600)
    value = cache.get(f"key_{i}")

elapsed = time.time() - start
print(f"1000 cache ops completed in {elapsed:.2f}s")
print("✓ Performance baseline acceptable" if elapsed < 5.0 else "✗ Performance degraded")
EOF
```

---

## Rollback Procedures

If you need to revert to v0.1.x after upgrading to v0.2.0:

### Immediate Rollback (Same Session)

```bash
# Option 1: Downgrade package immediately
pip install codex-ml==0.1.0

# Verify rollback
python -c "from codex_ml import __version__; print(__version__)"
# Expected output: 0.1.0

# Clear cache to avoid stale imports
python -c "import py_compile; py_compile.main(['-b', '.'])"
```

### Rollback from Backup

```bash
# If using virtual environment, switch to old environment
source venv_old/bin/activate  # Switch to v0.1.x venv

# OR restore from system backup
pip install -r requirements.frozen.0.1.x
```

### Rollback Database/Configuration

```bash
# If custom configurations were modified
cp -r ~/.codex.backup.0.1.x ~/.codex

# Verify rollback
ls -la ~/.codex
```

### Post-Rollback Verification

```bash
# Verify rollback success
python << 'EOF'
import codex_ml
print(f"Current version: {codex_ml.__version__}")
print("Rollback successful" if codex_ml.__version__.startswith("0.1") else "Rollback incomplete")
EOF
```

---

## Compatibility Matrix

### Python Version Support

| Version | Supported | Status |
|---------|-----------|--------|
| 3.11    | No        | Use v0.1.x |
| 3.12    | Yes       | Recommended |
| 3.13    | Yes       | Beta support |

### Dependency Compatibility

| Dependency | v0.1.x | v0.2.0 | Notes |
|-----------|--------|--------|-------|
| PyYAML | >=5.4 | >=6.0.1 | YAML parsing security improvements |
| PyJWT | >=2.0.0 | >=2.13.0 | JWT validation security hardening |
| Jinja2 | >=3.0.0 | >=3.1.6 | Template injection prevention |
| cryptography | >=35.0 | 48.0.0-<50.0.0 | Cryptographic hardening |
| setuptools | >=50.0 | >=78.1.1 | Build system requirements |

### Operating System Compatibility

| OS | v0.1.x | v0.2.0 | Status |
|----|--------|--------|--------|
| Linux (x86_64) | ✓ | ✓ | Fully supported |
| macOS (ARM/Intel) | ✓ | ✓ | Fully supported |
| Windows (x86_64) | ✓ | ✓ | Fully supported |

---

## Troubleshooting

### Issue 1: Import Errors After Upgrade

**Symptom**: `ImportError: No module named 'codex_ml'`

**Solution**:

```bash
# Verify installation
pip show codex-ml

# Reinstall if missing
pip install --force-reinstall codex-ml==0.2.0

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Verify imports
python -c "from codex_ml import __version__; print(__version__)"
```

### Issue 2: Dependency Conflicts

**Symptom**: `pip check` reports broken requirements

**Solution**:

```bash
# Identify conflicts
pip check

# Resolve with constraints
pip install --upgrade codex-ml==0.2.0 \
    --constraint requirements-compatible.txt

# If persistent, use fresh environment
python3.12 -m venv fresh_env
source fresh_env/bin/activate
pip install codex-ml==0.2.0
```

### Issue 3: Performance Degradation

**Symptom**: Slower execution than v0.1.x

**Solution**:

```bash
# Verify cache is functioning
python << 'EOF'
from codex_ml.cache import CacheManager
cache = CacheManager()
print(f"Cache backend: {cache.backend}")
print(f"Cache hit rate: {cache.stats()}")
EOF

# Check if pytest-xdist is enabled (may show as slower in single-thread mode)
pytest --no-xdist tests/

# Verify resource availability
free -h  # Check available memory
df -h    # Check disk space
```

### Issue 4: Configuration Not Loading

**Symptom**: Configuration files ignored after upgrade

**Solution**:

```bash
# Verify configuration file paths
python << 'EOF'
from codex_ml.config import Config
config = Config()
print(f"Config path: {config.config_path}")
print(f"Config loaded: {config.is_loaded}")
EOF

# Verify YAML syntax (no changes required for v0.1.x configs)
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Reload configuration
from codex_ml.config import Config
config = Config()
config.reload()
```

### Issue 5: Tests Failing After Upgrade

**Symptom**: Test failures that didn't occur in v0.1.x

**Solution**:

```bash
# Run tests with verbose output
pytest -vv tests/

# Check for flaky test issues (resolved in v0.2.0)
pytest --tb=short tests/

# If timing-sensitive tests fail, verify system resources
top -b -n 1 | head -20

# Run with single worker if parallelization causes issues
pytest --no-xdist tests/
```

---

## Additional Resources

### Documentation
- [CHANGELOG.md](../CHANGELOG.md) - Complete version history
- [RELEASE_NOTES_v0.2.0.md](./RELEASE_NOTES_v0.2.0.md) - Phase-by-phase release details
- [README.md](../README.md) - Project documentation

### Support
- GitHub Issues: https://github.com/Aries-Serpent/_codex_/issues
- Security Policy: [SECURITY.md](../SECURITY.md)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)

### Version History
- [v0.1.0 Release Notes](../docs/release/RELEASE_NOTES.md)
- Previous versions available on PyPI

---

## Migration Checklist

- [ ] Read Pre-Upgrade Checklist
- [ ] Verified current version and Python compatibility
- [ ] Backed up configuration files
- [ ] Documented dependencies
- [ ] Created test environment (optional)
- [ ] Upgraded to v0.2.0
- [ ] Ran verification steps
- [ ] Updated dependent code (if needed - no changes required)
- [ ] Tested core functionality
- [ ] Ran full test suite
- [ ] Verified performance improvements
- [ ] Deployed to production (if applicable)

---

## Support and Questions

If you encounter issues not covered in this guide:

1. Check the [CHANGELOG.md](../CHANGELOG.md) for known issues
2. Review [RELEASE_NOTES_v0.2.0.md](./RELEASE_NOTES_v0.2.0.md) for phase-specific details
3. Open an issue on [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
4. Consult the [SECURITY.md](../SECURITY.md) policy for security-related concerns

---

**Migration Guide Version**: 1.0  
**Last Updated**: 2026-07-20T02:00Z  
**Status**: Production Ready
