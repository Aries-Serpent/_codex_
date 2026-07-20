# Migration Guide: v0.2.2 → v0.3.0

**Date:** 2026-07-11  
**Target:** codex-ml v0.3.0  
**Compatibility:** Fully backward compatible | No breaking changes  
**Estimated Time:** 5-10 minutes  

---

## Overview

v0.3.0 is a **minor release** with full backward compatibility. Your existing code will continue to work without any modifications. This guide walks you through upgrading and verifies the installation.

---

## Quick Upgrade (5 minutes)

### Step 1: Upgrade the Package

```bash
# Option A: Upgrade in-place
pip install --upgrade codex-ml==0.3.0

# Option B: Using a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install codex-ml==0.3.0

# Option C: Using uv (faster)
uv pip install codex-ml==0.3.0
```

### Step 2: Verify Installation

```bash
# Check version
python -c "import codex_ml; print(f'codex-ml version: {codex_ml.__version__}')"

# Expected output: codex-ml version: 0.3.0

# List installed version and size
pip show codex-ml
```

### Step 3: Update Requirements Files (if applicable)

```bash
# If using requirements.txt
# Edit: requirements.txt
# Change: codex-ml==0.2.2
# To:     codex-ml==0.3.0

pip install -r requirements.txt

# If using pyproject.toml
# Edit: pyproject.toml dependencies section
# Change: codex-ml>=0.2.2
# To:     codex-ml>=0.3.0
```

---

## Installation Profiles

v0.3.0 continues the 3-profile packaging strategy:

### Profile: `core` (Recommended for most users)

```bash
pip install codex-ml[core]==0.3.0
# Size: 8-15 MB
# Use case: Lightweight, offline-first, edge devices
```

### Profile: `runtime` (For production services)

```bash
pip install codex-ml[runtime]==0.3.0
# Size: 20-35 MB
# Use case: Production inference, API services
```

### Profile: `full` (For development)

```bash
pip install codex-ml[full]==0.3.0
# Size: 100+ MB
# Use case: Development, testing, all features
```

---

## What's New in v0.3.0

### ✅ What Improved (You may benefit from these improvements)

| Feature | v0.2.2 | v0.3.0 | Benefit |
|---------|--------|--------|---------|
| **Security** | 6 known CWE issues | All 6 fixed | Enhanced protection |
| **Dependencies** | Older versions | Updated | Security patches, bug fixes |
| **Tests** | 1,200 tests | 1,247 tests | Better coverage (90.2%) |
| **Documentation** | v0.2.0-focused | v0.3.0-complete | Better reference material |
| **PyPI Auth** | OIDC (experimental) | Token-based | More reliable publishing |

### ⚠️ What May Require Attention (Breaking Changes)

**None.** v0.3.0 maintains full backward compatibility. Your code needs no changes.

### 🔒 Security Enhancements (Recommended)

If you use the following features, ensure they still work in your environment:

1. **SQL/Database Operations:** Path validation enhanced (CWE-22 fix)
2. **Web/API Endpoints:** XSS protection added (CWE-79 fix)
3. **Data Deserialization:** Unsafe patterns removed (CWE-502 fix)
4. **Configuration:** No hardcoded credentials (CWE-798 fix)

**Action:** No code changes needed unless you previously worked around these issues.

---

## Rollback (If Needed)

If you need to revert to v0.2.2:

```bash
# Reinstall previous version
pip install codex-ml==0.2.2

# Verify
python -c "import codex_ml; print(codex_ml.__version__)"
```

---

## Troubleshooting

### Issue: "No module named 'codex_ml'"

**Solution:** Ensure v0.3.0 is installed in the active Python environment:

```bash
# Check current Python
which python3

# Verify installation location
pip show codex-ml

# Reinstall if needed
pip install --force-reinstall codex-ml==0.3.0
```

### Issue: "Version conflict" or dependency errors

**Solution:** Use a clean virtual environment:

```bash
# Create fresh environment
python3 -m venv .venv_clean
source .venv_clean/bin/activate
pip install --upgrade pip setuptools wheel
pip install codex-ml==0.3.0
```

### Issue: "ImportError" after upgrade

**Solution:** Clear Python cache and rebuild:

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstall
pip install --force-reinstall --no-cache-dir codex-ml==0.3.0
```

### Issue: "Old version still showing"

**Solution:** Check for multiple Python installations:

```bash
# List all Python environments
python3 -m venv --help

# Check pip location
which pip

# Explicitly use pip from venv
/path/to/venv/bin/pip install codex-ml==0.3.0
```

---

## Configuration Changes

### Environment Variables

No environment variables changed in v0.3.0. If you set any custom ones, they remain valid.

### Configuration Files

If you use `hydra` or `omegaconf` configuration:

```yaml
# Your existing config/app.yaml works unchanged in v0.3.0
defaults:
  - model: bert
  - training: standard

model:
  name: bert-base-uncased
  # ... all your settings remain compatible
```

### CLI Commands

All CLI commands remain unchanged. Your scripts will continue to work:

```bash
# These all work in v0.3.0 exactly as in v0.2.2
codex-ml train --config config.yaml
codex-ml evaluate --model model.bin
codex-ml serve --port 8000
```

---

## Testing Your Upgrade

### Minimal Test

```python
import codex_ml
from codex_ml import training, evaluation

# Verify version
assert codex_ml.__version__ == "0.3.0"

# Test basic imports
print("✅ v0.3.0 imported successfully")
```

### Integration Test (if you have existing code)

```bash
# Run your existing test suite
pytest tests/

# Expected: All tests pass (no changes needed)
```

---

## Performance Impact

v0.3.0 has **no performance degradation**:

- ✅ Same execution speed as v0.2.2
- ✅ Same memory footprint
- ✅ No new dependencies that would slow startup
- ✅ Security fixes have negligible overhead

---

## Support

If you encounter issues:

1. **Check this guide:** Common issues section above
2. **GitHub Issues:** [Report a bug](https://github.com/Aries-Serpent/_codex_/issues/new)
3. **Documentation:** [Full docs](https://aries-serpent.github.io/_codex_/)
4. **Security:** [Report vulnerabilities](https://github.com/Aries-Serpent/_codex_/security)

---

## What's Next

After upgrading to v0.3.0, consider:

- 📚 Review [Release Notes](RELEASE_NOTES_v0.3.0.md) for detailed changes
- 🔒 Check [SECURITY.md](../SECURITY.md) for security best practices
- 📖 Explore [Documentation](https://aries-serpent.github.io/_codex_/) for new features
- 🚀 Run your test suite to confirm compatibility

---

## Additional Resources

- **PyPI Project:** https://pypi.org/project/codex-ml/0.3.0/
- **GitHub Release:** https://github.com/Aries-Serpent/_codex_/releases/tag/v0.3.0
- **Release Notes:** [RELEASE_NOTES_v0.3.0.md](RELEASE_NOTES_v0.3.0.md)
- **Installation Guide:** [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

---

**Last Updated:** 2026-07-20  
**Status:** ✅ Ready for v0.3.0 upgrade  
**Compatibility:** Fully backward compatible
