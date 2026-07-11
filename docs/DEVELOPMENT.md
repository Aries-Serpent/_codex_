# Development Setup Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08  
**Version**: 1.0.0

This guide walks you through setting up your development environment to contribute to Codex ML.

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Full Setup](#full-setup)
3. [IDE Configuration](#ide-configuration)
4. [Running Tests](#running-tests)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# 2. Install with development dependencies
pip install -e ".[dev,test]"

# 3. Install pre-commit hooks (optional but recommended)
pre-commit install

# 4. Verify setup
pytest --collect-only
```

Done! You're ready to start developing. See [Running Tests](#running-tests) for next steps.

---

## Full Setup

### Prerequisites

Check that you have the minimum requirements:

```bash
# Python 3.12+
python --version
# Expected: Python 3.12.x or higher

# Git
git --version
# Expected: git version 2.x or higher

# pip (Python package manager)
pip --version
# Expected: pip 24.x or higher
```

If you need to install or upgrade Python:

**Using pyenv** (Recommended):
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.0

# Set as local version
pyenv local 3.12.0

# Verify
python --version
```

**Using Homebrew** (macOS):
```bash
brew install python@3.12
```

**Using apt** (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv
```

**Using Windows Package Manager**:
```powershell
winget install Python.Python.3.12
```

### Clone the Repository

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
```

### Create Virtual Environment

**Using venv** (Built-in):
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate          # Linux/macOS
# OR
venv\Scripts\activate.bat         # Windows (cmd.exe)
# OR
venv\Scripts\Activate.ps1         # Windows (PowerShell)
```

**Using uv** (Faster):
```bash
# Install uv
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate        # Linux/macOS
# OR
.venv\Scripts\activate.bat       # Windows
```

### Install Development Dependencies

**Using pip**:
```bash
# Install with all extras
pip install -e ".[dev,test,docs]"

# Or install just what you need
pip install -e ".[dev]"      # Core development tools
pip install -e ".[test]"     # Testing framework
pip install -e ".[docs]"     # Documentation building
```

**Using uv**:
```bash
uv sync --all-extras
```

**What gets installed**:
- Core dependencies (PyYAML, Hydra, Pydantic, etc.)
- Development tools (black, ruff, mypy, pytest)
- Testing utilities (pytest-cov, pytest-asyncio)
- Documentation tools (mkdocs, sphinx)

### Install Pre-Commit Hooks

Pre-commit hooks automatically check your code before committing:

```bash
# Install pre-commit package
pip install pre-commit

# Install the hooks
pre-commit install

# (Optional) Run hooks on all files to verify
pre-commit run --all-files
```

**What gets checked**:
- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- Security vulnerabilities
- Secrets detection
- YAML validation
- Large file checks

### Verify Installation

```bash
# Check that dependencies are installed
pip list | grep -E "pytest|black|ruff"

# Verify Python path
python -c "import sys; print(sys.executable)"

# Test pytest
pytest --version

# Test basic import
python -c "from codex_ml import __version__; print(__version__)"
```

---

## IDE Configuration

### Visual Studio Code

**Recommended Extensions**:
1. [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) - Official Python support
2. [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) - Type checking
3. [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) - Code formatting
4. [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) - Linting
5. [Python Test Explorer](https://marketplace.visualstudio.com/items?itemName=littlefoxteam.vscode-python-test-adapter) - Test running

**Settings** (`.vscode/settings.json`):
```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    },
    "editor.rulers": [100]
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.ruffArgs": ["--line-length=100"],
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": [
    "--strict",
    "--ignore-missing-imports"
  ],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

**Launch configurations** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm / IntelliJ IDEA

**Configuration**:
1. **File → Settings → Project → Python Interpreter**
   - Select your virtual environment created above
   
2. **File → Settings → Editor → Code Style → Python**
   - Set line length to 100
   - Enable optimized imports

3. **File → Settings → Tools → Python Integrated Tools**
   - Test runner: pytest
   - Package management: pip

4. **File → Settings → Tools → Black**
   - Enable Black formatter
   - Set line length to 100

5. **File → Settings → Tools → Ruff**
   - Enable Ruff linter

### Vim / Neovim

**Using vim-python-lsp-config**:
```vim
" ~/.config/nvim/init.vim or ~/.vimrc
" Install vim-plug or your plugin manager first

" Code formatting
Plug 'dense-analysis/ale'
Plug 'psf/black'

" Type checking
Plug 'vim-python/python-lsp'

" Settings
let g:ale_fixers = {
    \ 'python': ['black', 'isort'],
    \ }
let g:ale_linters = {
    \ 'python': ['pylsp', 'mypy'],
    \ }
let g:black_linelength = 100
```

---

## Running Tests

### Quick Test Run

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_model.py

# Run specific test function
pytest tests/test_model.py::test_model_loading

# Run tests matching a pattern
pytest -k "test_model"
```

### With Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report in browser
open htmlcov/index.html          # macOS
xdg-open htmlcov/index.html      # Linux
start htmlcov\index.html         # Windows

# Check coverage threshold
pytest --cov=src --cov-fail-under=90
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run multiple markers
pytest -m "unit or integration"
```

### Debugging Tests

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Verbose output with capture disabled
pytest -vvs

# Run with full traceback
pytest --tb=long
```

---

## Common Tasks

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Format a specific file
black src/codex_ml/model.py

# Check formatting without changes
black --check src/
```

### Linting

```bash
# Check with Ruff
ruff check src/ tests/

# Fix issues automatically
ruff check --fix src/

# Check specific rule
ruff check --select E501 src/
```

### Type Checking

```bash
# Run mypy
mypy src/

# Mypy on specific file
mypy src/codex_ml/model.py

# Strict mode (recommended)
mypy --strict src/
```

### Import Sorting

```bash
# Sort imports with isort
isort src/ tests/

# Check without changes
isort --check-only src/
```

### Pre-commit Checks

```bash
# Run all hooks on changed files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Update hook versions
pre-commit autoupdate
```

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve locally
mkdocs serve

# View at http://localhost:8000
```

### Creating a Git Branch

```bash
# Create and switch to new branch
git checkout -b feature/my-new-feature

# Or use git switch (newer Git versions)
git switch -c feature/my-new-feature

# Push branch to remote
git push origin feature/my-new-feature
```

### Committing Changes

```bash
# Stage changes
git add src/codex_ml/model.py

# Commit with message
git commit -m "feat: add model validation"

# Or use interactive mode
git add -i

# Amend last commit
git commit --amend

# Amend without changing message
git commit --amend --no-edit
```

---

## Troubleshooting

### Python Version Issues

**Problem**: `python --version` shows wrong version

**Solution**:
```bash
# Check available versions
python3 --version
python3.12 --version

# Use specific version
python3.12 -m venv venv

# Or use pyenv
pyenv versions
pyenv local 3.12.0
```

### Virtual Environment Issues

**Problem**: Can't import packages after installing

**Solution**:
```bash
# Check if venv is activated
which python  # Should show path in venv/

# Reinstall venv
rm -rf venv/
python -m venv venv
source venv/bin/activate

# Reinstall packages
pip install -e ".[dev,test]"
```

### Pre-commit Hook Failures

**Problem**: Commit blocked by pre-commit hooks

**Solution**:
```bash
# Fix automatically (Black formatting, import sorting)
black src/ tests/
isort src/ tests/

# Fix linting issues
ruff check --fix src/

# Then commit again
git add .
git commit -m "your message"

# Or bypass hooks (only in emergencies)
git commit --no-verify
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'codex_ml'`

**Solution**:
```bash
# Check virtual environment is activated
which python  # Should show venv path

# Reinstall package in editable mode
pip install -e "."

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/_codex_"
```

### Test Discovery Issues

**Problem**: `pytest` can't find tests

**Solution**:
```bash
# Check pytest can collect tests
pytest --collect-only

# Check test file naming
# Test files should be: test_*.py or *_test.py

# Check __init__.py files
# Ensure test directories have __init__.py if needed

# Run with verbose output
pytest -v --tb=short
```

### mypy Errors

**Problem**: Type checking fails

**Solution**:
```bash
# Check mypy configuration
cat mypy.ini

# Run with specific settings
mypy --no-strict-optional src/

# Generate mypy cache
rm -rf .mypy_cache/
mypy src/
```

### Package Dependency Issues

**Problem**: Dependency conflicts or missing packages

**Solution**:
```bash
# List all dependencies
pip list

# Check for conflicts
pip check

# Upgrade pip
pip install --upgrade pip

# Clear cache and reinstall
pip cache purge
pip install -e ".[dev,test]" --force-reinstall
```

### Git Issues

**Problem**: `fatal: not a git repository`

**Solution**:
```bash
# Navigate to repo directory
cd _codex_

# Check git status
git status

# Clone if needed
git clone https://github.com/Aries-Serpent/_codex_.git
```

---

## Next Steps

1. **Make your first contribution**: See [CONTRIBUTING.md](../CONTRIBUTING.md#contribution-paths)
2. **Run tests**: `pytest`
3. **Check code style**: `black --check src/ && ruff check src/`
4. **Read the docs**: [docs/](../docs/)
5. **Get help**: Open a discussion if you're stuck

---

## Additional Resources

- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute
- **[Code Style Guide](dev/CODE_STYLE_GUIDE.md)** - Coding standards
- **[Testing Guide](dev/testing.md)** - Writing tests
- **[Documentation Index](MASTER_INDEX.md)** - All documentation

Happy coding! 🎉
