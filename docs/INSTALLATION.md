# Installation Guide - Aries-Serpent v0.1.0

**Document Type:** User Guide  
**Audience:** Developers, DevOps Engineers, System Administrators  
**Last Updated:** 2026-07-09

## Quick Start (30 seconds)

```bash
# Install from PyPI (recommended for users)
pip install codex-ml

# Or install from source
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e .
```

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**CPU:** 2+ cores (4+ recommended for ML models)  
**RAM:** 4GB minimum (8GB+ recommended)  
**Disk:** 2GB free space  
**Network:** Internet connection for initial setup

### Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Core runtime |
| pip | 24.0+ | Package manager |
| git | 2.40+ | Version control (for source installation) |
| Docker | 24.0+ | Container runtime (optional, for containers) |
| Kubernetes | 1.26+ | Orchestration (optional, for K8s deployment) |

### Optional Components

- **Docker Desktop:** For containerized deployment
- **Docker Compose:** For multi-container setups
- **kubectl:** For Kubernetes management
- **OpenAI API Key:** For AI features (get from https://platform.openai.com/api-keys)

## Installation Methods

### Method 1: PyPI Installation (Recommended for Users)

**Easiest method for most users.**

```bash
# Install latest version
pip install codex-ml

# Install specific version
pip install codex-ml==0.1.0

# Install with optional dependencies
pip install codex-ml[runtime]        # ML inference
pip install codex-ml[core]           # Lightweight core
pip install codex-ml[full]           # Development + all tools
```

**Verification:**
```bash
python -c "import codex_ml; print(codex_ml.__version__)"
# Output: 0.1.0
```

### Method 2: Development Installation (For Contributors)

**Install from source for development.**

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[full]"

# Verify installation
pytest tests/

# Run smoke test
python -m codex.cli --help
```

### Method 3: Docker Installation (For Containerized Deployment)

**Using pre-built Docker images.**

```bash
# Pull latest image
docker pull ghcr.io/aries-serpent/codex:0.1.0

# Run container
docker run -it ghcr.io/aries-serpent/codex:0.1.0 python -m codex.cli --help

# Run with mounted volume
docker run -it -v $(pwd):/workspace \
  ghcr.io/aries-serpent/codex:0.1.0 \
  python -m codex.cli train --config-name=my_config
```

### Method 4: Kubernetes Installation (For Enterprise Deployment)

**Deploy using Kubernetes manifests.**

```bash
# Apply Kubernetes manifests
kubectl apply -f manifests/k8s/base/

# Verify deployment
kubectl get pods -l app=codex

# Check service availability
kubectl get svc codex-api

# View logs
kubectl logs -l app=codex -f
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and dependencies
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Verify Python version
python3.12 --version

# Create and activate virtual environment
python3.12 -m venv codex-env
source codex-env/bin/activate

# Install codex-ml
pip install codex-ml[full]
```

### macOS (Intel/Apple Silicon)

```bash
# Using Homebrew (install if not present: /bin/bash -c "$(curl -fsSL ...)")
brew install python@3.12

# Create and activate virtual environment
python3.12 -m venv codex-env
source codex-env/bin/activate

# Install codex-ml
pip install codex-ml[full]

# Note: Apple Silicon (M1/M2) users may need to install some packages from conda-forge
conda create -n codex python=3.12 pyarrow
conda activate codex
pip install codex-ml[full]
```

### Windows (PowerShell)

```powershell
# Download Python 3.12 from https://www.python.org/downloads/
# OR use Windows Package Manager
winget install Python.Python.3.12

# Verify installation
python --version

# Create and activate virtual environment
python -m venv codex-env
.\codex-env\Scripts\Activate.ps1

# Install codex-ml
pip install codex-ml[full]

# If get-executionpolicy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker (All Platforms)

```bash
# Build from Dockerfile
docker build -t codex:latest .

# Or pull pre-built image
docker pull ghcr.io/aries-serpent/codex:0.1.0

# Run interactive shell
docker run -it codex:latest /bin/bash

# Run with GPU support (requires nvidia-docker)
docker run -it --gpus all codex:latest python -m codex.cli
```

## Verification

### Test Installation

```bash
# Check version
codex --version
# Output: codex-ml 0.1.0

# Check installed packages
pip show codex-ml

# List installed dependencies
pip freeze | grep -E "pydantic|hydra-core|typer"

# Run basic test
python -c "from codex.cli import main; print('Installation successful!')"
```

### Test Features

```bash
# Test CLI commands
codex config --help
codex train --help
codex eval --help

# Test Python import
python << 'EOF'
from codex.config import ConfigManager
from codex.cli import main
print("✓ Core modules imported successfully")
EOF

# Test with sample configuration
codex train --config-name=example hydra.run.dir=./test-run
```

### Test Docker Installation

```bash
# Run container
docker run --rm codex:latest python -c \
  "from codex import __version__; print(f'Codex {__version__}')"

# Run test suite in container
docker run --rm codex:latest pytest tests/ --tb=short
```

## Installation Profiles

### Core Profile (Lightweight)

```bash
pip install codex-ml[core]
```

**Size:** ~8-15 MB  
**Includes:** Configuration, CLI, safety enforcement  
**Use for:** Lightweight deployments, edge devices, offline environments

### Runtime Profile (Production)

```bash
pip install codex-ml[runtime]
```

**Size:** ~20-35 MB  
**Includes:** ML inference, pattern recognition, API services  
**Use for:** Production inference, API deployment, pattern learning

### Full Profile (Development)

```bash
pip install codex-ml[full]
```

**Size:** ~100+ MB  
**Includes:** Core + Runtime + development tools  
**Use for:** Development, testing, experimentation, research

## Uninstallation

```bash
# Remove codex-ml package
pip uninstall codex-ml -y

# Remove virtual environment
rm -rf codex-env/

# Clean pip cache
pip cache purge
```

## Troubleshooting

### Issue: "No module named 'codex'"

**Solution:**
```bash
# Verify installation
pip show codex-ml

# Reinstall if needed
pip install --upgrade codex-ml

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Issue: Version Mismatch

```bash
# Check installed version
python -c "import codex; print(codex.__version__)"

# Install specific version
pip install codex-ml==0.1.0

# Pin version in requirements.txt
echo "codex-ml==0.1.0" >> requirements.txt
```

### Issue: Dependency Conflicts

```bash
# Upgrade pip
pip install --upgrade pip

# Install compatible versions
pip install --force-reinstall codex-ml

# Use virtual environment
python -m venv clean-env
source clean-env/bin/activate
pip install codex-ml[full]
```

### Issue: Docker Image Not Found

```bash
# List available images
docker images | grep codex

# Pull latest image
docker pull ghcr.io/aries-serpent/codex:0.1.0

# Build from source
docker build -f Dockerfile.api -t codex:latest .
```

### Issue: Kubernetes Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>

# Check resource limits
kubectl top nodes
kubectl top pods

# Rollback deployment
kubectl rollout undo deployment/codex-api
```

## Getting Help

- **Documentation:** https://github.com/Aries-Serpent/_codex_/docs
- **Issues:** https://github.com/Aries-Serpent/_codex_/issues
- **Discussions:** https://github.com/Aries-Serpent/_codex_/discussions
- **Email:** support@aries-serpent.dev

---

**Status:** ✅ COMPLETE  
**Last Updated:** 2026-07-09
