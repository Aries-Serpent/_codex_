# Local Development Environment Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-06-22  
> **Status**: Active  
> **Audience**: Developers, Contributors, Data Scientists  

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Python Environment Setup](#python-environment-setup)
4. [Dependency Installation](#dependency-installation)
5. [Database Configuration](#database-configuration)
6. [Local Server Startup](#local-server-startup)
7. [IDE Configuration](#ide-configuration)
8. [Pre-Commit Hooks](#pre-commit-hooks)
9. [Troubleshooting](#troubleshooting)
10. [Development Workflow](#development-workflow)

---

## Quick Start

For experienced developers, here's the 5-minute setup:

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in editable mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start development server
python -m src.codex_ml.cli --mode dev
```

---

## System Requirements

### Minimum Specifications

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | macOS 11+, Ubuntu 20.04+, Windows 10+ | macOS 12+, Ubuntu 22.04+, Windows 11 |
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Disk | 50 GB free | 100 GB free |
| Python | 3.9+ | 3.11+ |

### Operating System-Specific Setup

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3.11 git postgresql

# Start PostgreSQL
brew services start postgresql
```

## Ubuntu/Debian

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
  build-essential git postgresql postgresql-contrib \
  libpq-dev curl wget

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Windows

```powershell
# Using Chocolatey (or download from official sites)
choco install python311 git postgresql

# Start PostgreSQL service
Start-Service -Name postgresql-x64-15
```

## Required Tools

- **Git**: Version control
- **Python 3.11+**: Programming language
- **pip**: Python package manager
- **uv** (optional): Faster package installer
- **PostgreSQL**: Database
- **Docker** (optional): Containerization

---

## Python Environment Setup

### Step 1: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/Aries-Serpent/_codex_.git

# Using SSH (if configured)
git clone git@github.com:Aries-Serpent/_codex_.git

cd _codex_
```

## Step 2: Create Virtual Environment

```bash
# Using venv (built-in)
python3.11 -m venv venv

# OR using conda
conda create -n codex python=3.11
conda activate codex

# Activate the environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows PowerShell
# or
.\venv\Scripts\activate.bat  # Windows CMD
```

## Step 3: Upgrade pip and Build Tools

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install uv for faster builds (optional but recommended)
pip install uv
```

## Step 4: Verify Python Installation

```bash
# Check Python version
python --version
# Expected: Python 3.11.x

# Check pip version
pip --version

# Check location
which python  # Linux/macOS
where python  # Windows
```

---

## Dependency Installation

### Install Development Dependencies

```bash
# Install in editable mode with all development extras
pip install -e ".[dev,test,docs]"

# OR using uv (faster)
uv pip install -e ".[dev,test,docs]"
```

## Install Specific Requirements Files

```bash
# Core requirements
pip install -r requirements.txt

# Development tools
pip install -r requirements-dev.txt

# Testing and coverage
pip install -r requirements-test.txt

# ML/Scientific stack
pip install -r requirements-ml-cpu.txt  # CPU only
# or
pip install -r requirements-ml-lite.txt  # Minimal dependencies
```

## Verify Installation

```bash
# Test core imports
python -c "import src.codex_ml; print('✓ Core installed')"

# Test development tools
python -c "import pytest; import black; print('✓ Dev tools installed')"

# List installed packages
pip list | grep codex

# Check dependency tree
pip install pipdeptree
pipdeptree
```

## Troubleshooting Installation Issues

**Issue**: Module not found errors

```bash
# Ensure you're in the virtual environment
which python  # Should show path in venv/

# Reinstall in editable mode
pip install -e . --force-reinstall

# Check PYTHONPATH
echo $PYTHONPATH
```

**Issue**: Compilation errors with C extensions

```bash
# macOS: Install Xcode command line tools
xcode-select --install

# Ubuntu: Install build-essential
sudo apt install -y build-essential python3-dev

# Windows: Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

---

## Database Configuration

### PostgreSQL Setup

#### macOS

```bash
# Start PostgreSQL (if using Homebrew)
brew services start postgresql

# Or manually
pg_ctl -D /usr/local/var/postgres start
```

## Ubuntu

```bash
# PostgreSQL is managed by systemd
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify running
sudo systemctl status postgresql
```

## Windows

```powershell
# Start service (if not auto-starting)
Start-Service -Name postgresql-x64-15

# Verify
Get-Service postgresql-x64-15
```

## Create Development Database

```bash
# Connect to PostgreSQL
psql postgres

# Create development database
CREATE DATABASE codex_dev;
CREATE USER codex_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE codex_dev TO codex_user;

# Exit
\q
```

## Configure Database Connection

Create `.env.local`:

```bash
# Database
DATABASE_URL=******localhost:5432/codex_dev

# API
API_HOST=127.0.0.1
API_PORT=8000

# Debug
DEBUG=True
LOG_LEVEL=DEBUG

# Features
ENABLE_CACHE=false
```

## Initialize Database Schema

```bash
# Run migrations
python -m src.codex_ml.db migrate

# Verify schema
psql -U codex_user -d codex_dev -c "\dt"
```

---

## Local Server Startup

### Development Server

```bash
# Start with default settings
python -m src.codex_ml.cli --mode dev

# Start with custom config
python -m src.codex_ml.cli --mode dev --config configs/dev.yaml

# Start with logging
python -m src.codex_ml.cli --mode dev --log-level DEBUG

# Start on custom port
python -m src.codex_ml.cli --mode dev --port 9000
```

## Using Flask/FastAPI Directly

```bash
# Flask development server (auto-reload on changes)
export FLASK_APP=src.codex_ml.api.app
export FLASK_ENV=development
flask run

# FastAPI development server with live reload
uvicorn src.codex_ml.api.app:app --reload --port 8000

# With debugging
uvicorn src.codex_ml.api.app:app --reload --port 8000 --log-level debug
```

## Using Docker Compose (Optional)

```bash
# Start all services locally
docker-compose -f docker-compose.dev.yml up

# Start specific service
docker-compose -f docker-compose.dev.yml up codex

# View logs
docker-compose -f docker-compose.dev.yml logs -f codex

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/docs

# View metrics
curl http://localhost:8000/metrics
```

---

## IDE Configuration

### Visual Studio Code

**Install extensions**:
- Python (Microsoft)
- Pylance
- Black Formatter
- Pylint
- autoDocstring

**`.vscode/settings.json`**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

**`.vscode/launch.json`**:
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
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "src/codex_ml/api/app.py",
        "FLASK_ENV": "development"
      },
      "args": ["run"],
      "jinja": true
    },
    {
      "name": "Python: Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v", "-s"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm Professional

1. **Open Project**:
   - File → Open → Select `_codex_` directory

2. **Configure Python Interpreter**:
   - Settings → Project → Python Interpreter
   - Click ⚙️ → Add...
   - Select Existing Environment
   - Browse to `venv/bin/python`

3. **Enable Debug Mode**:
   - Run → Edit Configurations
   - Create new Python configuration
   - Set Script Path to module name
   - Enable "Reload changed modules"

4. **Code Style Settings**:
   - Settings → Editor → Code Style → Python
   - Set line length to 100
   - Enable Black formatter

### Vim/Neovim

**`~/.config/nvim/init.vim`** (example configuration):
```vim
" Python LSP setup with coc
call coc#config("python", {
  \ "lspPath": "~/.local/bin/pylsp",
  \ "pythonPath": "<path-to-venv>/bin/python"
\})
```

---

## Pre-Commit Hooks

### Install Pre-Commit Framework

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Verify installation
pre-commit run --all-files
```

## Configuration File

**`.pre-commit-config.yaml`** (already in repo):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: debug-statements
```

### Manual Code Quality Checks

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

---

## Troubleshooting

### Common Issues and Solutions

**Issue 1: Virtual Environment Not Activating**

```bash
# Windows: Execution Policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation
python -c "import sys; print(sys.prefix)"
# Should show path to venv/
```

**Issue 2: Module Import Errors**

```bash
# Check PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Reinstall in development mode
pip install -e . --force-reinstall --no-deps

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

**Issue 3: PostgreSQL Connection Errors**

```bash
# Test PostgreSQL connectivity
psql -U codex_user -d codex_dev -c "SELECT 1;"

# Check PostgreSQL is running
pg_isready

# View PostgreSQL logs
tail -f /var/lib/postgresql/data/postgresql.log  # Linux

# Reset PostgreSQL password
psql -U postgres -c "ALTER USER codex_user PASSWORD 'new_password';"
```

**Issue 4: Dependency Conflicts**

```bash
# Create fresh virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate

# Install with constraint file
pip install -r requirements.txt --constraint constraints.txt

# Check dependency tree
pip install pipdeptree
pipdeptree --warn fail
```

**Issue 5: Slow Performance**

```bash
# Profile with cProfile
python -m cProfile -o profile.stats src/codex_ml/cli.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats

# Memory profiling
pip install memory-profiler
python -m memory_profiler src/codex_ml/cli.py
```

---

## Development Workflow

### Typical Development Session

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Update from main branch
git pull origin main

# 3. Create feature branch
git checkout -b feature/my-feature

# 4. Make changes and run tests
pytest tests/ -v

# 5. Format and lint
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# 6. Commit changes
git add .
git commit -m "Add my feature"

# 7. Push and open PR
git push origin feature/my-feature
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_training.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel
pytest -n auto

# Run with verbose output
pytest -v -s

# Watch mode (auto-run on file changes)
ptw  # requires pytest-watch
```

## Debugging

```bash
# Start debugger with breakpoint()
python -m pdb src/codex_ml/cli.py

# Debug with PyCharm: Run → Debug 'config_name'

# Debug with VS Code: F5

# Remote debugging
python -m pdb --pdbrc=.pdbrc script.py
```

## Code Review Preparation

```bash
# Run full test suite
pytest tests/ --cov=src --cov-report=term-missing

# Check type hints
mypy src/ --strict

# Run security checks
bandit -r src/

# Check code quality
radon cc src/ -a

# Generate documentation
sphinx-build -b html docs/ docs/_build
```

---

## Next Steps

1. **Clone and setup**: Follow Quick Start section
2. **Read architecture**: See [ARCHITECTURE.md](../ARCHITECTURE.md)
3. **Explore codebase**: Check [Repository Structure](../ARCHITECTURE_BLUEPRINT.md#repository-structure)
4. **Join development**: Follow contribution guidelines in [CONTRIBUTING.md](../../CONTRIBUTING.md)
5. **Ask for help**: Open issue in GitHub or check [Discussions](https://github.com/Aries-Serpent/_codex_/discussions)

---

## References

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [VS Code Python Guide](https://code.visualstudio.com/docs/languages/python)
- [Pre-commit Framework](https://pre-commit.com/)
