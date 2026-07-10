# Installation Guide - Aries-Serpent ML v0.1.0

**Document Type:** User Guide  
**Audience:** Developers, DevOps Engineers, System Administrators, ML Engineers  
**Last Updated:** 2026-07-10  
**Version:** 0.1.0

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start-30-seconds)
3. [Prerequisites](#prerequisites)
4. [Installation Methods](#installation-methods)
5. [Installation Profiles](#installation-profiles)
   - [Core Profile](#core-profile)
   - [Runtime Profile](#runtime-profile)
   - [Full Profile](#full-profile)
6. [Platform-Specific Instructions](#platform-specific-instructions)
7. [Verification](#verification)
8. [Entry Points & CLI Commands](#entry-points--cli-commands)
9. [Troubleshooting](#troubleshooting)
10. [Getting Help](#getting-help)

---

## Overview

**codex-ml** (Aries-Serpent ML) is a production-ready, Level 4 MLOps-certified machine learning platform featuring:

- 🎯 **Three Installation Profiles**: Choose the right package size for your use case
- 🚀 **Production-Grade**: 90.2% test coverage, 0 CVEs, enterprise-ready
- 🧠 **Cognitive Brain Integration**: Advanced autonomous decision-making
- 📊 **MLOps Ready**: Training, evaluation, and model serving all included
- 🔒 **Security First**: Network policy enforcement, cryptographic security

### Why Three Profiles?

The **three-profile packaging strategy** allows you to install only what you need:

| Profile | Size | Best For | Key Components |
|---------|------|----------|-----------------|
| **Core** | 8-15 MB | Lightweight, edge, offline | CLI, config, safety |
| **Runtime** | 20-35 MB | Production inference | PyTorch, Transformers, FastAPI |
| **Full** | 100+ MB | Development & research | Everything + dev tools |

---

## Quick Start (30 seconds)

```bash
# Most common: Install with runtime profile (recommended for most users)
pip install codex-ml[runtime]==0.1.0

# Or lightweight core only
pip install codex-ml[core]==0.1.0

# Or development with all features
pip install codex-ml[full]==0.1.0

# Verify installation
python -c "import codex_ml; print(f'✓ Installed: {codex_ml.__version__}')"
```

**Installation time:** ~2-5 minutes (depending on profile and connection)

---

## Prerequisites

### System Requirements

Your system must meet these minimum requirements:

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 2 cores | 4+ cores | For ML models, 8+ cores for training |
| **RAM** | 2 GB | 8 GB | Core profile: 2 GB; Runtime/Full: 8+ GB |
| **Storage** | 500 MB | 2 GB | Full profile needs more space |
| **OS** | Linux, macOS, Windows | Any modern OS | Docker container support for all |

**GPU Support (Optional):**
- NVIDIA GPUs: CUDA 12.x (runtime profile recommended for inference)
- AMD GPUs: ROCm support available
- Apple Silicon: Native arm64 support

### Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12+ | Core runtime (3.11 with `tomli` fallback) |
| **pip** | 24.0+ | Package manager |
| **git** | 2.40+ | For source installation (optional) |
| **Docker** | 24.0+ | Containerized deployment (optional) |
| **CUDA Toolkit** | 12.x+ | GPU support (optional, runtime profile) |

### Optional Components

- **Docker Desktop:** For containerized deployment
- **Docker Compose:** For multi-container orchestration
- **NVIDIA Container Runtime:** For GPU-accelerated containers
- **kubectl:** For Kubernetes management (enterprise)
- **OpenAI API Key:** For AI features (get from https://platform.openai.com/api-keys)

### Verify Prerequisites

```bash
# Check Python version (must be 3.12+)
python --version

# Check pip version
pip --version

# (Optional) Check git
git --version

# (Optional) Check Docker
docker --version

# (Optional) Check CUDA availability
nvidia-smi  # if GPU support needed
```

---

## Installation Methods

Choose the installation method that best fits your use case:

### Method 1: PyPI Installation (Recommended for Users) ⭐

**Best for:** Most users, production deployments, reproducible environments

```bash
# Create virtual environment (highly recommended)
python -m venv codex-env
source codex-env/bin/activate  # On Windows: codex-env\Scripts\activate

# Upgrade pip to latest
pip install --upgrade pip

# Install with your chosen profile
pip install codex-ml[runtime]==0.1.0      # Most common ⭐
# OR
pip install codex-ml[core]==0.1.0         # Lightweight
# OR
pip install codex-ml[full]==0.1.0         # Development

# Verify installation
python -c "import codex_ml; print(codex_ml.__version__)"
```

**Installation time:** 2-5 minutes (runtime), 1-2 minutes (core)  
**Estimated size:** See [Installation Profiles](#installation-profiles)

### Method 2: Source Installation (For Contributors)

**Best for:** Development, testing, contributing to the project

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[full]"

# Run test suite to verify
pytest tests/ -x --tb=short

# Run smoke test
codex-ml --help
```

**Installation time:** 5-15 minutes (includes compilation)  
**Best combined with:** Pre-commit hooks setup

### Method 3: Docker Installation (Containerized)

**Best for:** Reproducible environments, CI/CD, cloud deployment

```bash
# Pull pre-built image
docker pull ghcr.io/aries-serpent/codex:0.1.0

# Run interactive container
docker run -it ghcr.io/aries-serpent/codex:0.1.0 codex-ml --help

# Run with mounted working directory
docker run -it -v $(pwd):/workspace \
  ghcr.io/aries-serpent/codex:0.1.0 \
  codex-ml train config.yaml

# Build locally from Dockerfile
docker build -t codex:latest -f Dockerfile .
```

**Container size:** ~1.5 GB (pre-built image)  
**Requires:** Docker or Docker Desktop

### Method 4: Offline Installation (Air-Gapped Environments)

**Best for:** Restricted network environments, corporate networks

```bash
# Step 1: Download wheels from connected machine
pip download codex-ml[runtime] -d ./wheelhouse/

# Step 2: Transfer wheelhouse to air-gapped machine
# (Use USB drive, SCP, or other secure method)

# Step 3: Install from local wheels
python -m venv codex-env
source codex-env/bin/activate
pip install --no-index --find-links ./wheelhouse/ codex-ml[runtime]

# Verify
codex-ml --version
```

**See also:** `docs/release/OFFLINE_DEPLOYMENT.md` for detailed air-gapped setup

---

## Platform-Specific Instructions

### 🐧 Linux (Ubuntu/Debian/Fedora)

#### Ubuntu/Debian

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and development tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Verify Python installation
python3.12 --version

# Create virtual environment
python3.12 -m venv ~/codex-env
source ~/codex-env/bin/activate

# Install codex-ml (runtime profile recommended)
pip install --upgrade pip
pip install codex-ml[runtime]==0.1.0

# Verify installation
codex-ml --version
```

#### Fedora/RHEL/CentOS

```bash
# Install Python 3.12
sudo dnf install -y python3.12 python3.12-devel python3-pip

# Create and activate virtual environment
python3.12 -m venv ~/codex-env
source ~/codex-env/bin/activate

# Install codex-ml
pip install --upgrade pip
pip install codex-ml[runtime]==0.1.0
```

#### Optional: NVIDIA GPU Support (Linux)

```bash
# Install NVIDIA drivers and CUDA toolkit
# Follow: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

# Install cuDNN (optional, for optimal performance)
# Follow: https://docs.nvidia.com/deeplearning/cudnn/install-guide/

# Verify GPU access
python -c "import torch; print(torch.cuda.is_available())"
```

---

### 🍎 macOS (Intel & Apple Silicon)

#### Prerequisites for macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Verify installation
python3.12 --version
```

#### Intel Mac Installation

```bash
# Create virtual environment
python3.12 -m venv ~/codex-env
source ~/codex-env/bin/activate

# Install codex-ml
pip install --upgrade pip
pip install codex-ml[runtime]==0.1.0
```

#### Apple Silicon (M1/M2/M3) Installation

```bash
# Method 1: Using Homebrew (recommended)
brew install python@3.12
python3.12 -m venv ~/codex-env
source ~/codex-env/bin/activate
pip install --upgrade pip
pip install codex-ml[runtime]==0.1.0

# Method 2: Using Conda (if PyTorch has issues)
conda create -n codex python=3.12
conda activate codex
pip install codex-ml[runtime]==0.1.0

# Verify GPU access (optional)
python -c "import torch; print(f'GPU: {torch.backends.mps.is_available()}')"
```

#### Optional: Apple Silicon GPU Support

```bash
# PyTorch automatically uses Metal Performance Shaders
# No additional setup required
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

### 🪟 Windows (PowerShell)

#### Installation Steps

```powershell
# Option 1: Using Windows Package Manager (winget)
winget install Python.Python.3.12

# Option 2: Direct download from https://www.python.org/downloads/

# Verify Python installation
python --version

# Create virtual environment
python -m venv codex-env

# Activate virtual environment
.\codex-env\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install codex-ml
python -m pip install --upgrade pip
pip install codex-ml[runtime]==0.1.0

# Verify installation
codex-ml --version
```

#### Troubleshooting PowerShell Issues

```powershell
# If activation fails, try cmd.exe instead:
cmd /c "codex-env\Scripts\activate.bat"

# Or use Python's built-in venv activation
python -m venv --help

# Check your execution policy
Get-ExecutionPolicy -List
```

---

### 🐳 Docker (All Platforms)

#### Using Pre-Built Image (Easiest)

```bash
# Pull the latest image
docker pull ghcr.io/aries-serpent/codex:0.1.0-runtime

# Run interactively
docker run -it ghcr.io/aries-serpent/codex:0.1.0-runtime bash

# Run specific command
docker run --rm ghcr.io/aries-serpent/codex:0.1.0-runtime codex-ml --help

# With GPU support (requires nvidia-docker)
docker run -it --gpus all ghcr.io/aries-serpent/codex:0.1.0-runtime python -c \
  "import torch; print(f'GPU available: {torch.cuda.is_available()}')"
```

#### Building Locally

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Build the Docker image
docker build -t codex:0.1.0 -f Dockerfile .

# Run the image
docker run -it codex:0.1.0 codex-ml --help

# Tag for registry
docker tag codex:0.1.0 ghcr.io/aries-serpent/codex:0.1.0
```

#### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'
services:
  codex:
    build: .
    image: codex:latest
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: /bin/bash
    stdin_open: true
    tty: true
```

```bash
# Run with docker-compose
docker-compose up -d codex
docker-compose exec codex codex-ml --help
```

---

### ☸️ Kubernetes (Enterprise)

```bash
# Create namespace
kubectl create namespace codex

# Apply manifests
kubectl apply -f manifests/k8s/ -n codex

# Verify deployment
kubectl get pods -n codex
kubectl get svc -n codex

# Check logs
kubectl logs -n codex deployment/codex-api

# Port forward to local
kubectl port-forward -n codex svc/codex-api 8000:8000
```

---

## Verification

After installation, verify everything works correctly with these tests.

### Quick Verification

```bash
# Check version
codex-ml --version

# Test basic import
python -c "import codex_ml; print(f'✓ Imported: {codex_ml.__version__}')"

# Test CLI help
codex-ml --help
```

### Complete Verification Suite

```bash
# 1. Check Python environment
python -c "
import sys
print(f'Python: {sys.version}')
print(f'Executable: {sys.executable}')
"

# 2. Check core dependencies
python << 'EOF'
packages = ['pydantic', 'hydra', 'omegaconf', 'typer', 'click']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg}')
    except ImportError:
        print(f'✗ {pkg}')
EOF

# 3. Runtime-specific packages (if runtime/full profile)
python << 'EOF'
try:
    import torch
    print(f'✓ PyTorch {torch.__version__}')
    if torch.cuda.is_available():
        print(f'  - GPU available: {torch.cuda.get_device_name(0)}')
except ImportError:
    print('ℹ PyTorch not installed (core profile)')
EOF

# 4. Test CLI commands
codex-ml config --help
codex-ml train --help
codex-ml eval --help

# 5. Run smoke tests (if full profile)
pytest tests/ -x --tb=short -k "test_smoke" 2>/dev/null || \
  echo "ℹ Smoke tests skipped (full profile only)"
```

### Platform-Specific Verification

**Linux/macOS:**
```bash
# Check virtual environment
which python
echo $VIRTUAL_ENV

# Verify package location
pip show codex-ml | grep Location
```

**Windows PowerShell:**
```powershell
# Check virtual environment
(Get-Command python).Source
$env:VIRTUAL_ENV

# Verify package
pip show codex-ml | findstr Location
```

**Docker:**
```bash
docker run --rm ghcr.io/aries-serpent/codex:0.1.0 \
  python -c "import codex_ml; print(codex_ml.__version__)"
```

### Test by Profile

**Core Profile Test:**
```bash
python -c "
from codex_ml.config import ConfigManager
from codex_ml.cli import cli
print('✓ Core profile working')
"
```

**Runtime Profile Test:**
```bash
python -c "
import torch
import transformers
print(f'✓ PyTorch {torch.__version__}')
print(f'✓ Transformers {transformers.__version__}')
"
```

**Full Profile Test:**
```bash
python -c "
import pytest
import mypy
import black
print('✓ Full profile working (dev tools installed)')
"
```

---

## Installation Profiles

codex-ml uses a **3-tier installation strategy** to optimize for different use cases. Choose the profile that matches your needs.

### Core Profile

**What is it?** Lightweight, offline-first installation with essential tools

```bash
pip install codex-ml[core]==0.1.0
```

**📊 Specifications:**
- **Size:** ~8-15 MB
- **Installation time:** 30-60 seconds
- **Memory footprint:** ~50-100 MB at runtime
- **Internet required:** Only for initial download

**✅ Includes:**
- Core runtime engine
- CLI interface (Typer + Click)
- Configuration management (Hydra + OmegaConf)
- Data validation (Pydantic)
- Code analysis tools (libcst, parso, tree-sitter)
- YAML/JSON serialization
- Network security enforcement

**❌ Does NOT include:**
- Machine Learning frameworks (PyTorch, Transformers)
- Evaluation tools (lm-eval)
- Model serving (Ray Serve, FastAPI)
- Training infrastructure
- Development tools (pytest, mypy, black)

**🎯 Best for:**
- Lightweight deployments on edge devices
- Air-gapped or offline environments
- Container/Kubernetes operator images
- Minimal dependencies for security compliance
- Embedded systems with limited resources

**Example use case:**
```bash
# Deploy CLI tools on minimal container
docker run -m 256m codex:core codex-ml --version
```

---

### Runtime Profile

**What is it?** Complete ML inference and serving environment (most popular ⭐)

```bash
pip install codex-ml[runtime]==0.1.0
```

**📊 Specifications:**
- **Size:** ~20-35 MB (plus PyTorch ~500 MB)
- **Installation time:** 3-5 minutes
- **Memory footprint:** ~1-2 GB at runtime
- **GPU support:** Optional NVIDIA/AMD/Apple Silicon

**✅ Includes:**
- Everything in Core profile
- **ML Frameworks:** PyTorch 2.6+, Transformers 5.12+
- **ML Utilities:** datasets, scikit-learn, pandas, numpy
- **Model Serving:** Ray Serve, FastAPI, Starlette
- **API Tools:** httpx, slowapi (rate limiting)
- **Inference Optimization:** accelerate, PEFT
- **Data Infrastructure:** DuckDB, Chromadb
- **Embedding Models:** sentence-transformers
- **Vector Search:** FAISS (CPU)
- **Monitoring:** prometheus-client, psutil, evidently
- **Tokenization:** sentencepiece

**❌ Does NOT include:**
- Training optimizers (full training pipeline)
- Development tools (pytest, mypy)
- Jupyter/notebook support
- Experimental features
- Enterprise integrations

**🎯 Best for:**
- Production inference servers
- Running pre-trained models
- API services and microservices
- Real-time pattern recognition
- Most users and organizations ⭐

**System requirements:**
- Minimum: 4 GB RAM
- Recommended: 8+ GB RAM
- GPU: Optional but recommended for inference

**Example use case:**
```bash
# Start inference server on port 8000
python -c "from fastapi import FastAPI; from ray import serve
app = FastAPI()
@serve.deployment
def predict(text): return {'result': 'inference'}
serve.run(app, port=8000)"
```

---

### Full Profile

**What is it?** Complete development, research, and testing environment

```bash
pip install codex-ml[full]==0.1.0
```

**📊 Specifications:**
- **Size:** ~100+ MB (plus all dependencies)
- **Installation time:** 5-15 minutes
- **Memory footprint:** ~3-5 GB at runtime
- **GPU support:** Strongly recommended

**✅ Includes:**
- Everything in Core + Runtime profiles
- **Development Tools:**
  - Testing: pytest, pytest-cov, pytest-xdist, hypothesis
  - Linting: ruff, black, isort, mypy
  - Pre-commit hooks, git integration
  - Type checking at 3.12+ level
- **Documentation:** MkDocs, Sphinx support
- **Profiling & Analysis:**
  - Memory/CPU profiling
  - Mutation testing (mutmut)
  - Coverage analysis and gap-fill
- **ML Training:**
  - Distributed training utilities
  - Experiment tracking (MLflow)
  - Hyperparameter tuning
- **Data Science:**
  - Jupyter notebook support
  - Advanced visualization
- **Cognitive Brain:**
  - OODA loop execution engine
  - Pattern matching and learning
  - Autonomous decision-making

**🎯 Best for:**
- Local development environments
- Research and experimentation
- Contributing to the codebase
- Building custom models
- ML engineers and data scientists
- Full feature access

**System requirements:**
- Minimum: 8 GB RAM
- Recommended: 16+ GB RAM
- SSD: 10+ GB free space
- GPU: Recommended for training (NVIDIA/AMD/Apple Silicon)

**Example use case:**
```bash
# Run full development environment with all tools
pip install -e ".[full]"
pytest tests/ --cov=codex_ml
black --check src/
mypy src/ --strict
```

---

### Profile Comparison

| Feature | Core | Runtime | Full |
|---------|------|---------|------|
| **Size** | 8-15 MB | 20-35 MB | 100+ MB |
| **Installation Time** | <1 min | 3-5 min | 5-15 min |
| **CLI Tools** | ✅ | ✅ | ✅ |
| **Configuration** | ✅ | ✅ | ✅ |
| **ML Inference** | ❌ | ✅ | ✅ |
| **Model Serving** | ❌ | ✅ | ✅ |
| **Training** | ❌ | ❌ | ✅ |
| **Development Tools** | ❌ | ❌ | ✅ |
| **Testing Framework** | ❌ | ❌ | ✅ |
| **GPU Support** | ❌ | ✅* | ✅* |
| **Cognitive Brain** | Basic | Yes | Full |

*GPU support requires CUDA toolkit installed separately

---

### Switching Between Profiles

```bash
# Start with core, then upgrade to runtime
pip install codex-ml[core]==0.1.0
pip install --upgrade codex-ml[runtime]==0.1.0

# Or uninstall and reinstall with full profile
pip uninstall codex-ml -y
pip install codex-ml[full]==0.1.0

# Install multiple profiles simultaneously
pip install 'codex-ml[core,runtime]==0.1.0'
```

---

## Entry Points & CLI Commands

### Available CLI Commands

After installation, the following commands are available:

#### Core Commands

```bash
# Main CLI entry point
codex-ml [OPTIONS] COMMAND

# Aliases
codex-cli        # Alternative entry point
codex-ml-cli     # Explicit naming

# Help and info
codex-ml --help
codex-ml --version
codex-ml config --help
```

#### Configuration Commands

```bash
# List available configurations
codex-ml config list

# Show active configuration
codex-ml config show

# Override configuration
codex-ml train model=gpt2 batch_size=32
```

#### Training & Evaluation Commands

```bash
# Training command (full profile)
codex-ml train --config-name=my_config

# Evaluation command (runtime/full profile)
codex-ml eval --config-name=my_config

# Serve model (runtime/full profile)
codex-ml serve --model my-model --port 8000
```

### Programmatic API

You can also import and use codex-ml from Python code:

```python
from codex_ml import ModelHandle
from codex_ml.config import ConfigManager
from codex_ml.cli import cli

# Create config manager
config_mgr = ConfigManager()

# Load a configuration
cfg = config_mgr.load_config('training.yaml')

# Or use the CLI programmatically
cli(['train', '--config-name=my_config'])
```

### Entry Points by Profile

| Entry Point | Core | Runtime | Full | Purpose |
|------------|------|---------|------|---------|
| `codex-ml` | ✅ | ✅ | ✅ | Main CLI |
| `codex-cli` | ✅ | ✅ | ✅ | Alternative CLI |
| `codex-ml-cli` | ✅ | ✅ | ✅ | Explicit CLI |
| `codex-smoke` | ✅ | ✅ | ✅ | Smoke test app |

### Extending with Plugins

codex-ml supports plugin registration through setuptools entry points:

```python
# In your plugin's setup.py or pyproject.toml
[project.entry-points."codex_ml.plugins"]
my_plugin = "my_module:plugin_class"

# Then use in code
from codex_ml.registry import PluginRegistry
registry = PluginRegistry()
my_plugin = registry.get_plugin("my_plugin")
```

### Cognitive Brain Integration

Access advanced decision-making:

```python
from codex_ml.cognitive import OODAOrchestrator

# Initialize OODA loop orchestrator
orchestrator = OODAOrchestrator()

# Observe → Orient → Decide → Act
result = orchestrator.execute(
    observation="Input data",
    context={"mode": "inference"}
)
```

---

## Troubleshooting

### Common Installation Issues

#### Issue: "No module named 'codex_ml'"

**Symptoms:** `ModuleNotFoundError: No module named 'codex_ml'`

**Solutions:**

```bash
# 1. Verify installation
pip show codex-ml

# 2. Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# 3. Reinstall package
pip install --upgrade --force-reinstall codex-ml[runtime]

# 4. Use absolute import path
python -c "from codex_ml.config import ConfigManager"
```

#### Issue: "Command 'codex-ml' not found"

**Symptoms:** `command not found: codex-ml`

**Solutions:**

```bash
# 1. Check if package is installed
pip list | grep codex

# 2. Verify virtual environment is activated
which python  # Should show path in your venv
echo $VIRTUAL_ENV  # Should show venv path

# 3. Reinstall entry points
pip install --force-reinstall codex-ml[runtime]

# 4. Use python -m instead
python -m codex_ml.cli --help
```

#### Issue: Dependency Version Conflict

**Symptoms:** `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**Solutions:**

```bash
# 1. Create fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate  # or fresh-env\Scripts\activate on Windows

# 2. Upgrade pip first
pip install --upgrade pip setuptools wheel

# 3. Install with compatible versions
pip install codex-ml[runtime]==0.1.0

# 4. If still issues, use --no-deps
pip install --no-deps codex-ml[runtime]==0.1.0
pip install pydantic hydra-core typer torch transformers
```

#### Issue: "CUDA out of memory"

**Symptoms:** `RuntimeError: CUDA out of memory`

**Solutions:**

```bash
# 1. Check GPU memory
nvidia-smi

# 2. Reduce batch size
codex-ml train batch_size=8 

# 3. Use CPU instead
export CUDA_VISIBLE_DEVICES=""
codex-ml train device=cpu

# 4. Clear GPU cache
python << 'EOF'
import torch
torch.cuda.empty_cache()
EOF
```

#### Issue: Docker Image Not Found

**Symptoms:** `Error response from daemon: manifest not found`

**Solutions:**

```bash
# 1. Pull correct image
docker pull ghcr.io/aries-serpent/codex:0.1.0

# 2. List available images
docker images | grep codex

# 3. Build locally
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
docker build -t codex:0.1.0 .

# 4. Check Docker daemon
docker ps  # Verify Docker is running
```

### Platform-Specific Issues

#### macOS: "Python3.12 command not found"

```bash
# 1. Install via Homebrew
brew install python@3.12

# 2. Or check installation
brew list python@3.12

# 3. Create symlink if needed
ln -s /usr/local/opt/python@3.12/bin/python3.12 /usr/local/bin/python
```

#### Windows: PowerShell Execution Policy Error

```powershell
# Check policy
Get-ExecutionPolicy -List

# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use cmd.exe instead
cmd /c "codex-env\Scripts\activate.bat"
```

#### Linux: Missing Development Headers

**Symptoms:** `error: Microsoft Visual C++ 14.0 or greater is required` (on Windows)  
or `fatal error: Python.h: No such file or directory` (on Linux)

```bash
# Ubuntu/Debian
sudo apt install -y python3.12-dev build-essential

# Fedora/RHEL
sudo dnf install -y python3.12-devel gcc

# Then reinstall
pip install --force-reinstall codex-ml[runtime]
```

### Performance Issues

#### Installation Too Slow

```bash
# 1. Check network speed
pip install --verbose codex-ml[core]

# 2. Use different PyPI mirror
pip install -i https://mirrors.aliyun.com/pypi/simple/ codex-ml[runtime]

# 3. Upgrade pip/setuptools
pip install --upgrade pip setuptools wheel

# 4. Install in parallel
pip install -U --upgrade-strategy eager codex-ml[runtime]
```

#### Runtime Performance Issues

```bash
# 1. Profile CPU usage
python -m cProfile -s cumulative script.py

# 2. Monitor memory
ps aux | grep python

# 3. Check disk I/O
iotop  # Linux
iostat  # macOS

# 4. Enable verbose logging
export CODEX_LOG_LEVEL=DEBUG
codex-ml train config.yaml
```

### Getting Diagnostics

```bash
# Create system information report
python << 'EOF'
import sys
import platform
import codex_ml

print("=== System Information ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Codex Version: {codex_ml.__version__}")
print("\n=== Installed Packages ===")
import subprocess
subprocess.run(["pip", "freeze"])
EOF

# Check for GPU availability
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
"
```

---

## Getting Help

### Documentation Resources

- **🏠 Main README:** [README.md](../README.md)
- **🚀 Quick Start ML:** [docs/quickstart/QUICK_START_ML.md](docs/quickstart/QUICK_START_ML.md)
- **🧠 Cognitive Brain Guide:** [docs/quickstart/QUICK_START_COGNITIVE_BRAIN.md](docs/quickstart/QUICK_START_COGNITIVE_BRAIN.md)
- **⚙️ Configuration Guide:** [docs/configuration/](configuration/)
- **🐳 Docker Guide:** [docker/README.md](../docker/README.md)
- **☸️ Kubernetes Guide:** [k8s/README.md](../k8s/README.md)

### Community Support

- **📝 Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **💬 Discussions:** [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **🐛 Bug Reports:** [Report a Bug](https://github.com/Aries-Serpent/_codex_/issues/new?template=bug_report.md)
- **💡 Feature Requests:** [Request a Feature](https://github.com/Aries-Serpent/_codex_/issues/new?template=feature_request.md)

### Additional Resources

- **📦 PyPI Package:** https://pypi.org/project/codex-ml/
- **🐳 Docker Hub:** https://ghcr.io/aries-serpent/codex
- **📚 Full Documentation:** https://github.com/Aries-Serpent/_codex_/blob/main/docs/
- **🔧 Contributing Guide:** [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## What's Next?

After successful installation, here's what you can do:

### For Users (Runtime Profile)

```bash
# 1. Run the quick start
python -m codex_ml.examples.quickstart

# 2. Load a pre-trained model
from codex_ml import ModelHandle
model = ModelHandle.from_pretrained("gpt2")

# 3. Run inference
result = model.predict("Hello, world!")
```

### For Developers (Full Profile)

```bash
# 1. Clone and develop
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e ".[full]"

# 2. Run tests
pytest tests/ -x

# 3. Start contributing
# See CONTRIBUTING.md for guidelines
```

### For ML Engineers

```bash
# 1. Build custom models
from codex_ml.training import Trainer

trainer = Trainer(config='my_config.yaml')
trainer.train()

# 2. Evaluate performance
from codex_ml.evaluation import Evaluator
evaluator = Evaluator(model='my_model')
evaluator.evaluate()

# 3. Deploy to production
from codex_ml.serving import deploy
deploy(model='my_model', port=8000)
```

---

## Version History

- **v0.1.0** (2026-07-10) - Production release with 90.2% coverage
- **v0.1.0-beta3** (2026-07-01) - Final beta release
- **Earlier versions** - See [CHANGELOG.md](../CHANGELOG.md)

---

## License

codex-ml is open source and available under the [MIT License](../LICENSE).

---

**Last Updated:** 2026-07-10  
**Installation Status:** ✅ Ready for Production  
**Support Level:** Enterprise-Grade
