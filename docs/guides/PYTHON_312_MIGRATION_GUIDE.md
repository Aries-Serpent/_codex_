# Python 3.12 Migration Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-25  
**Target Audience:** Users and Contributors

---

## 🎯 Overview

This repository now **requires Python 3.12.10 or later** (but < 3.13). Python 3.11 and earlier versions are no longer supported.

**Why this change?**
- Simplified CI/CD (50% faster, 50% cheaper)
- Cleaner codebase (no version conditionals)
- Modern Python features (PEP 695, 701, 698)
- Better performance and security

---

## 🚨 Breaking Changes

### What Changed
- **Minimum Python Version:** 3.11 → 3.12.10
- **Maximum Python Version:** None → <3.13
- **Configuration:** `requires-python = ">=3.12,<3.13"` in pyproject.toml
- **Workflows:** All CI/CD now runs on Python 3.12 only

### Impact
- ❌ Python 3.11 and earlier will **NOT work**
- ✅ Python 3.12.10+ will work
- ⚠️ Python 3.13+ will **NOT work** (not yet supported)

---

## 📋 Prerequisites

Before migrating, ensure you have:
- [ ] Backup of your current environment
- [ ] List of installed packages (`pip freeze > requirements-backup.txt`)
- [ ] Commit any uncommitted changes
- [ ] Administrative/sudo access (for system-wide Python installation)

---

## 🔧 Migration Steps

### For End Users

#### Step 1: Check Current Python Version

```bash
# Check your current Python version
python --version

# If it shows Python 3.12.x, you're already good!
# If not, continue with installation steps below
```

## Step 2: Install Python 3.12

**macOS (using Homebrew):**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Verify installation
python3.12 --version  # Should show Python 3.12.x
```

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev

# Verify installation
python3.12 --version  # Should show Python 3.12.x
```

**Windows:**
1. Download Python 3.12.10 from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python 3.12 to PATH"
4. Click "Install Now"
5. Verify in Command Prompt:
   ```cmd
   python --version
   ```

**Using pyenv (Recommended for Developers):**
```bash
# Install pyenv (if not already installed)
curl https://pyenv.run | bash

# Install Python 3.12.10
pyenv install 3.12.10

# Set as global version
pyenv global 3.12.10

# Verify
python --version  # Should show Python 3.12.10
```

## Step 3: Update Your Project

```bash
# Navigate to your project directory
cd path/to/your/project

# Remove old virtual environment
rm -rf .venv venv

# Create new virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate the virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -e .
# Or if you have a requirements file:
pip install -r requirements.txt

# Verify Python version in virtual environment
python --version  # Should show Python 3.12.x
```

## Step 4: Test Your Installation

```bash
# Run a simple test
python -c "import sys; print(f'Python {sys.version}')"

# Try importing the package
python -c "import codex_ml; print('Success!')"

# Run tests if available
pytest tests/ -v
```

---

## For Contributors

### Step 1: Install Python 3.12 (see above)

#### Step 2: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Use pyenv to set local version
pyenv local 3.12.10

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install --upgrade pip setuptools wheel
pip install -e ".[dev,test]"
```

## Step 3: Configure Development Tools

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files to verify setup
pre-commit run --all-files

# Verify linting and formatting tools
ruff check .
black --check .
mypy src/
```

## Step 4: Verify Everything Works

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term

# Check test collection
pytest tests/ --collect-only

# Verify Python version
python --version  # Must be 3.12.x
```

---

## 🐛 Troubleshooting

### Issue: "python: command not found" or "python3.12: command not found"

**Solution:**
```bash
# Check which Python versions are installed
ls /usr/bin/python*
ls /usr/local/bin/python*

# On macOS with Homebrew:
brew link python@3.12

# Add to PATH (add to ~/.bashrc or ~/.zshrc):
export PATH="/usr/local/opt/python@3.12/bin:$PATH"

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

## Issue: "No module named 'venv'"

**Solution:**
```bash
# Ubuntu/Debian:
sudo apt install python3.12-venv

# Verify venv is available:
python3.12 -m venv --help
```

## Issue: pip install fails with "externally-managed-environment"

**Solution:**
```bash
# Always use a virtual environment (recommended):
python3.12 -m venv .venv
source .venv/bin/activate

# Or use pipx for global tools:
python3.12 -m pip install --user pipx
python3.12 -m pipx ensurepath
```

## Issue: Tests fail after migration

**Solution:**
```bash
# Clear pytest cache
rm -rf .pytest_cache __pycache__ .hypothesis

# Clear coverage data
rm -rf .coverage htmlcov

# Reinstall dependencies
pip install --force-reinstall -e ".[dev,test]"

# Run tests with verbose output
pytest tests/ -vv --tb=short
```

## Issue: Import errors after migration

**Solution:**
```bash
# Verify virtual environment is activated
which python  # Should point to .venv/bin/python

# Reinstall in editable mode
pip uninstall codex-ml
pip install -e .

# Check installed packages
pip list | grep codex
```

---

## ❓ FAQ

### Q: Why Python 3.12 specifically?

**A:** Python 3.12 offers:
- Improved performance (5-10% faster than 3.11)
- Better error messages
- Modern syntax features (PEP 695 type parameter syntax, PEP 701 f-string improvements)
- Active security support
- Industry standard (widely adopted)

### Q: Can I still use Python 3.11?

**A:** No. Python 3.11 is no longer supported in this repository. You must upgrade to Python 3.12.10 or later.

### Q: Will Python 3.13 work?

**A:** Not yet. The version constraint is `>=3.12,<3.13`, so Python 3.13 will not work until we explicitly add support.

### Q: How do I know if my code will work with Python 3.12?

**A:** Python 3.12 is largely compatible with 3.11. Key changes:
- `except*` syntax for ExceptionGroups (now standard)
- Improved f-string parsing
- Better type hints
- No breaking changes for most code

Run your tests after migration to verify compatibility.

### Q: What if I have multiple projects with different Python versions?

**A:** Use **pyenv** or **conda** to manage multiple Python versions:

```bash
# With pyenv
cd project-with-python-3.12
pyenv local 3.12.10

cd project-with-python-3.11
pyenv local 3.11.9

# Each project uses its own Python version
```

## Q: Do I need to update my code syntax?

**A:** Not required, but recommended for modern Python:

**Old (still works):**
```python
from typing import Union, Optional, List, Dict

def process(data: Union[str, int]) -> Optional[List[Dict[str, str]]]:
    pass
```

**New (Python 3.12 style):**
```python
def process(data: str | int) -> list[dict[str, str]] | None:
    pass
```

### Q: How do I report issues with the migration?

**A:**
1. Check this guide's troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with:
   - Python version (`python --version`)
   - Operating system
   - Error message
   - Steps to reproduce

---

## 📚 Additional Resources

### Official Python Documentation
- [What's New in Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [Python 3.12 Release Notes](https://www.python.org/downloads/release/python-31210/)
- [Python 3.12 Migration Guide](https://docs.python.org/3/howto/pyporting.html)

### Project Documentation
- **README.md** - Project overview and quick start
- **CONTRIBUTING.md** - Development setup and guidelines
- **AGENTS.md** - AI agent documentation and policies

### Related Documents
- `PR_2968_RESOLUTION_SUMMARY.md` - Full implementation details
- `PHASE_3_EXECUTION_COMPLETE.md` - Python 3.12 standardization details
- `PHASE_5_COMPLETE.md` - Retrospective and lessons learned

---

## ✅ Verification Checklist

After migration, verify:

- [ ] Python version is 3.12.x (`python --version`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Pre-commit hooks work (`pre-commit run --all-files`)
- [ ] No import errors when running code
- [ ] Development tools work (debugger, IDE, etc.)

---

## 🎉 Success!

If you've completed all steps and verification passes, you're all set! Welcome to Python 3.12! 🚀

**Need Help?**
- Create an issue on GitHub
- Check the FAQ section above
- Contact: @mbaetiong

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-25  
**Maintained by:** Aries-Serpent/_codex_ Team
