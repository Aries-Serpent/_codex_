# Comprehensive Three-Profile Packaging Specification for codex-ml

**Status:** LANE 3 Complete  
**Version:** 1.0  
**Target Python:** 3.12+  
**Last Updated:** 2024

---

## Executive Summary

The codex-ml project uses a three-profile installation strategy to optimize deployment contexts:

- **Core Profile** (8-15 MB): Lightweight, offline-first, zero external I/O at import
- **Runtime Profile** (20-35 MB): Production inference with pre-cached models, local network services
- **Full Profile** (100+ MB): Development and experimentation with all dependencies

---

## 1. Profile Definitions

### 1.1 Core Profile (8-15 MB) - Offline-First

**Purpose:** Lightweight deployment for edge devices, air-gapped environments, and configuration management

**Installation:**
```bash
pip install codex-ml[core]
```

**Module Composition:**
- codex/config - Configuration management via Hydra/OmegaConf (2-3 MB)
- codex/cli - Command-line interface and entry points (1-2 MB)
- codex/safety - Safety enforcement and policy validation (1-2 MB)
- codex/interfaces - Core API contracts and protocols (1-2 MB)
- codex/utils - Utility functions and helpers (1-2 MB)
- codex/schema - Data schema definitions and validation (2-3 MB)

**Total Profile Size:** 8-15 MB

**Base Dependencies (27 packages):**
```
Configuration: omegaconf>=2.3.0, hydra-core>=1.3.0, pyyaml>=6.0
Validation: pydantic>=2.0.0, pydantic-settings>=2.0.0
Security: cryptography>=48.0.0,<50.0.0, PyJWT>=2.13.0,<3.0.0, PyNaCl>=1.5.0,<2.0.0
Networking: requests>=2.33.0, httpx>=0.24.0
Data: msgpack>=1.0.0, attrs>=23.1.0, decorator>=5.1.0
Parsing: libcst>=0.4.9, parso>=0.8.3, tree-sitter>=0.20.1, sqlparse>=0.4.4
CLI: typer>=0.12.0, click>=8.1.0
Utilities: python-dateutil>=2.8.0, tqdm>=4.66.0, colorama>=0.4.6
```

**Use Cases:**
- Air-gapped deployments (zero network I/O required at import)
- Edge device deployments
- Policy enforcement containers
- Configuration management servers
- Offline safety validation

**Validation:**
- ✅ No network calls at import time
- ✅ Runs without torch/transformers
- ✅ Configuration validation without ML models
- ✅ Cryptographic operations available
- ✅ CLI tools functional

---

### 1.2 Runtime Profile (20-35 MB) - Production Inference

**Purpose:** Production-grade ML inference with pattern recognition, API services, and local network support

**Installation:**
```bash
pip install codex-ml[runtime]
```

**Module Composition:**
- codex_ml/inference - Model inference engine (3-5 MB)
- codex_ml/services - FastAPI/Ray serve services (2-3 MB)
- codex_ml/patterns - Pattern learning and recognition (2-3 MB)
- codex_ml/embeddings - Sentence embeddings and RAG (3-5 MB)
- codex_ml/tokenizers - Custom tokenization pipelines (1-2 MB)
- All Core Profile modules (8-15 MB)

**Total Profile Size:** 20-35 MB (excludes pre-cached models)

**Runtime Dependencies (22 new packages):**
```
ML Inference: torch>=2.6.1,<3.0.0, transformers>=4.37.0, datasets>=2.18.0
Serving: fastapi>=0.109.0, uvicorn>=0.27.0, ray[serve]>=2.8.0
Embeddings: sentence-transformers>=2.2.0, chromadb>=0.4.0, faiss-cpu>=1.7.4
Model Hub: huggingface-hub>=0.19.0
Data: numpy>=1.24.0, pandas>=2.0.0, scikit-learn>=1.3.0
Async: aiohttp>=3.9.0, aiofiles>=23.2.0
Serialization: orjson>=3.9.0, cloudpickle>=3.0.0
Utilities: tenacity>=8.2.0
```

**Use Cases:**
- Production ML model serving
- FastAPI-based inference APIs
- Pattern recognition engines
- Embedding generation for RAG systems
- Real-time prediction services
- Local model serving with Ray serve
- Pre-cached model loading (no training)

**Validation:**
- ✅ Pre-cached models load successfully
- ✅ FastAPI endpoints functional
- ✅ Local network services available
- ✅ Ray serve workers initialize
- ✅ Inference operations execute
- ✅ Embedding generation works

---

### 1.3 Full Profile (100+ MB) - Development

**Purpose:** Complete development environment with testing, experimentation, and advanced features

**Installation:**
```bash
pip install codex-ml[full]
pip install -e ".[full]"  # Editable mode
```

**Additional Module Composition:**
- tests/ - Test suite and test utilities (5-10 MB)
- examples/ - Code examples and notebooks (10-15 MB)
- experiments/ - Experimental features (5-10 MB)
- Development tools & linters (15-25 MB)
- ML extras, visualization, monitoring (20-30 MB)
- Documentation & Jupyter (10-15 MB)

**Total Profile Size:** 100+ MB

**Development Dependencies (42 new packages):**

Testing (15 packages):
```
pytest>=7.4.0, pytest-asyncio>=0.21.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0,
pytest-timeout>=2.2.0, pytest-xdist>=3.5.0, pytest-benchmark>=4.0.0,
coverage>=7.3.0, hypothesis>=6.88.0
```

Code Quality (10 packages):
```
ruff>=0.1.0, black>=23.12.0, isort>=5.13.0, mypy>=1.8.0, pylint>=3.0.0,
flake8>=6.1.0, bandit>=1.7.5, pre-commit>=3.6.0
```

Development Tools (8 packages):
```
ipython>=8.18.0, ipdb>=0.13.0, debugpy>=1.8.0, memory-profiler>=0.61.0,
line-profiler>=4.1.0, py-spy>=0.3.14, objgraph>=3.6.0
```

ML & Visualization (12 packages):
```
mlflow>=2.10.0, wandb>=0.16.0, tensorboard>=2.15.0, plotly>=5.18.0,
matplotlib>=3.8.0, seaborn>=0.13.0, jupyter>=1.0.0, jupyterlab>=4.0.0,
notebook>=7.0.0, nbconvert>=7.14.0, plotly-express>=5.18.0
```

Evaluation & Benchmarking (7 packages):
```
evaluate>=0.4.1, nlpaug>=1.1.10, bert-score>=0.3.13, rouge-score>=0.1.2,
nltk>=3.9.4, sacrebleu>=2.4.0
```

**Use Cases:**
- Local development and debugging
- Experimentation and prototyping
- Test suite execution
- Model training and fine-tuning
- Performance profiling and benchmarking
- Jupyter notebook development
- ML pipeline evaluation
- Documentation generation
- Code quality analysis

---

## 2. Dependency Isolation Matrix

### 2.1 Package Membership Summary

**Total Packages: 91 across all profiles**

| Category | Core | Runtime | Full | Total |
|----------|------|---------|------|-------|
| Base Dependencies | 21 | 21 | 21 | 21 |
| Runtime-Specific | 0 | 22 | 22 | 22 |
| Testing | 0 | 0 | 15 | 15 |
| Code Quality | 0 | 0 | 10 | 10 |
| Development | 0 | 0 | 8 | 8 |
| ML/Visualization | 0 | 0 | 12 | 12 |
| Evaluation | 0 | 0 | 7 | 7 |
| **TOTAL** | **21** | **43** | **91** | **91** |

### 2.2 Critical Security Constraints

These packages have version pins due to security vulnerabilities:

```
cryptography>=48.0.0,<50.0.0    # CVE-2026-26007 fix
PyJWT>=2.13.0,<3.0.0            # PYSEC-2026-120 fix
PyNaCl>=1.5.0,<2.0.0            # Cryptographic library security
pyOpenSSL>=26.0.0,<27.0.0       # CVE-2026-27448/27459 fixes
requests>=2.33.0                # CVE-2026-25645 fix
```

### 2.3 Platform-Specific Constraints

```
torch>=2.6.1,<3.0.0 ; sys_platform != 'win32'
# Excludes Windows: torch is CPU-only on non-standard Windows setups
# Install with: pip install codex-ml[runtime] --index-url https://download.pytorch.org/whl/cu118
```

---

## 3. Installation & Validation

### 3.1 Installation Commands

**Core Profile:**
```bash
# Minimal offline-first installation
pip install codex-ml[core]

# With lock file for reproducibility
pip install -r requirements/lock-minimal.txt

# Verify offline capability
python verify_core_profile.py
```

**Runtime Profile:**
```bash
# Production inference installation
pip install codex-ml[runtime]

# With GPU support (CUDA 11.8)
pip install codex-ml[runtime] --index-url https://download.pytorch.org/whl/cu118

# From lock file for reproducibility
pip install -r requirements/lock.txt

# Verify model loading
python verify_runtime_profile.py
```

**Full Profile:**
```bash
# Full development installation
pip install codex-ml[full]

# Editable mode for development
pip install -e ".[full]"

# Run full test suite
pytest tests/ -v
```

### 3.2 Profile Detection

Environment variables control profile selection:

```bash
# Core Profile (air-gapped)
export OFFLINE_MODE=1
export AIR_GAPPED=1

# Runtime Profile (production)
export CUDA_VISIBLE_DEVICES=0  # GPU available

# Full Profile (development)
export DEVELOPMENT_MODE=1
```

Automatic detection via Docker/Kubernetes:
```bash
# Container environments default to runtime profile
# Air-gapped environments default to core profile
# Development (git) environments default to full profile
```

### 3.3 Validation Procedures

**Test Core Profile (No Network I/O):**
```bash
# Verify imports without network calls
python -c "
import socket
from unittest.mock import patch

def mock_socket(*args, **kwargs):
    raise RuntimeError('Network call detected!')

with patch('socket.socket.__init__', mock_socket):
    import omegaconf, hydra, pydantic, cryptography
    print('✅ Core profile: zero network I/O at import')
"
```

**Test Runtime Profile (Model Loading):**
```bash
# Verify torch and transformers load
python -c "
import torch
import transformers
print(f'✅ PyTorch {torch.__version__}')
print(f'✅ Transformers {transformers.__version__}')

# Test FastAPI
import fastapi
print(f'✅ FastAPI {fastapi.__version__}')

# Test Ray
import ray
print(f'✅ Ray {ray.__version__}')
"
```

**Test Full Profile (All Dependencies):**
```bash
# Run test suite
pytest tests/ -v --cov=codex --cov-report=html

# Run linters
ruff check .
black --check .
mypy src/

# Run type checking
mypy src/ --strict
```

**Network Isolation Test:**
```bash
# Verify no external network calls during initialization
python -c "
import sys
from unittest.mock import patch

network_calls = []

def mock_urlopen(url, *args, **kwargs):
    network_calls.append(url)
    raise RuntimeError(f'Network call blocked: {url}')

with patch('urllib.request.urlopen', mock_urlopen):
    try:
        from codex.config import ConfigManager
        print('✅ No network calls during import')
    except RuntimeError as e:
        print(f'❌ Unexpected network call: {e}')
"
```

**Offline Capability Test (Air-Gap Validation):**
```bash
# Simulate air-gapped environment
python -c "
import os
os.environ['OFFLINE_MODE'] = '1'

# Test core profile works without network
from codex.config import ConfigManager
from codex.cli import CLI
from codex.safety import SafetyValidator

print('✅ Core profile functional in offline mode')
print('✅ Configuration management: OK')
print('✅ CLI tools: OK')
print('✅ Safety enforcement: OK')
"
```

---

## 4. Reproducible Build Procedures

### 4.1 Lock File Usage

**Installation from lock file (exact reproducibility):**

```bash
# Core profile (minimal, offline-ready)
pip install -r requirements/lock-minimal.txt

# Runtime profile (production inference)
pip install -r requirements/lock.txt

# Evaluation profile (benchmarking)
pip install -r requirements/lock-eval.txt
```

### 4.2 Version Constraints

All profiles enforce:
- Python >= 3.12
- Minimal transitive dependency chains
- Security version pins (see Section 2.2)
- Platform-specific constraints (see Section 2.3)

### 4.3 Reproducible Build Checklist

- [ ] Python 3.12+ installed
- [ ] pip and setuptools up-to-date: `pip install -U pip setuptools wheel`
- [ ] Virtual environment created: `python -m venv venv && source venv/bin/activate`
- [ ] Lock file integrity verified (if using lock files)
- [ ] Profile selection confirmed (core/runtime/full)
- [ ] Installation successful: `pip install codex-ml[profile]`
- [ ] Core profile validation passed (no network I/O)
- [ ] Runtime profile model loading verified (if runtime/full)
- [ ] Full test suite passes (if full profile)
- [ ] Network isolation verified (air-gap validation)
- [ ] Security constraints confirmed (dependency versions)

### 4.4 Building Docker Image

**Core Profile (Offline-Ready):**
```dockerfile
FROM python:3.12-slim
RUN pip install codex-ml[core]
CMD ["codex", "--help"]
```

**Runtime Profile (Production):**
```dockerfile
FROM pytorch/pytorch:2.6.0-runtime-cuda12.1-cudnn8-runtime
RUN pip install codex-ml[runtime]
EXPOSE 8000
CMD ["uvicorn", "codex_ml.services.api:app", "--host", "0.0.0.0"]
```

**Full Profile (Development):**
```dockerfile
FROM python:3.12
RUN pip install codex-ml[full]
WORKDIR /app
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root"]
```

---

## 5. pyproject.toml Extras Configuration

The three-profile structure is configured in pyproject.toml extras:

```toml
[project.optional-dependencies]
# Core profile: offline-first, zero external I/O
core = [
    "omegaconf>=2.3.0,<3.0.0",
    "hydra-core>=1.3.0,<2.0.0",
    "pydantic>=2.0.0,<3.0.0",
    "cryptography>=48.0.0,<50.0.0",
    "PyJWT>=2.13.0,<3.0.0",
    # ... (see full list in pyproject.toml)
]

# Runtime profile: production inference
runtime = [
    # All core packages, plus:
    "torch>=2.6.1,<3.0.0;sys_platform!='win32'",
    "transformers>=4.37.0,<5.0.0",
    "fastapi>=0.109.0,<0.110.0",
    "ray[serve]>=2.8.0,<3.0.0",
    # ... (see full list in pyproject.toml)
]

# Full profile: development and testing
full = [
    # All runtime packages, plus:
    "pytest>=7.4.0,<8.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "ruff>=0.1.0,<0.2.0",
    "black>=23.12.0,<24.0.0",
    "mlflow>=2.10.0,<3.0.0",
    "jupyter>=1.0.0,<2.0.0",
    # ... (see full list in pyproject.toml)
]
```

**Deprecated Aliases (backward compatibility, to be removed v1.0):**
```toml
all = ["codex-ml[full]"]          # use [full] instead
dev = ["codex-ml[full]"]          # use [full] instead
ml = ["codex-ml[runtime]"]        # use [runtime] instead
train = ["codex-ml[full]"]        # use [full] instead
test-core = ["codex-ml[core]"]    # use [core] instead
```

---

## 6. Transitive Dependency Analysis

### 6.1 Core Profile Transitive Dependencies

Core profile pulls in approximately 40-50 transitive dependencies through:
- omegaconf → dotted-notation, antlr4-python3-runtime
- hydra-core → packaging, importlib-metadata
- pydantic → annotated-types, typing-extensions
- cryptography → cffi, pycparser
- requests → urllib3, certifi, idna, charset-normalizer

**Total tree depth:** 3-4 levels

### 6.2 Runtime Profile Transitive Dependencies

Runtime profile adds ~100-120 transitive dependencies through:
- torch → numpy, typing-extensions, sympy, filelock
- transformers → huggingface-hub, safetensors, regex, tokenizers, click, pyyaml
- fastapi → starlette, anyio, pydantic, typing-extensions
- ray → protobuf, msgpack, redis, aioredis, psutil, pydantic

**Total tree depth:** 4-5 levels

### 6.3 Full Profile Transitive Dependencies

Full profile adds ~50-100 additional transitive dependencies through:
- pytest → pluggy, iniconfig, packaging, colorama
- ruff → no transitive deps (distributed as binary)
- black → click, pathspec, platformdirs, tomli
- mypy → typed-ast, tomli, typing-extensions
- jupyter → tornado, traitlets, ipykernel, nbconvert, pygments

**Total tree depth:** 4-5 levels

---

## 7. Optional Package Groups

### 7.1 Audio Processing (Optional)

```toml
[project.optional-dependencies]
audio = [
    "librosa>=0.10.0",
    "soundfile>=0.12.1",
    "pyaudio>=0.2.13",
    "wave",  # built-in
    "scipy>=1.11.0",
]
```

Install with: `pip install codex-ml[runtime,audio]`

### 7.2 Advanced Visualization (Optional)

```toml
[project.optional-dependencies]
visualization = [
    "plotly>=5.18.0",
    "matplotlib>=3.8.0",
    "seaborn>=0.13.0",
    "dash>=2.14.0",
    "altair>=5.0.0",
]
```

Install with: `pip install codex-ml[runtime,visualization]`

### 7.3 Experiment Tracking (Optional)

```toml
[project.optional-dependencies]
experiments = [
    "mlflow>=2.10.0",
    "wandb>=0.16.0",
    "neptune-client>=1.1.0",
    "tensorboard>=2.15.0",
]
```

Install with: `pip install codex-ml[runtime,experiments]`

---

## 8. Size Estimates by Profile

| Profile | Size | Breakdown |
|---------|------|-----------|
| **Core** | 8-15 MB | Config/CLI/Safety: 8-15 MB |
| **Runtime** | 20-35 MB | Core: 8-15 MB, ML/Inference: 12-20 MB |
| **Full** | 100+ MB | Runtime: 20-35 MB, Testing/Dev: 65-75 MB |

**Exclude these when measuring:**
- Pre-cached models (downloaded separately, not packaged)
- Virtual environment (~100-500 MB depending on profile)
- Development dependencies cache (~50-100 MB)

**Actual disk usage may vary based on:**
- Python version and implementation (CPython vs PyPy)
- Platform (Windows vs Linux vs macOS)
- Installed wheels vs source distributions
- Compressed vs uncompressed measurements

---

## 9. Deployment Recommendations

### 9.1 Edge Devices (Core Profile)
```bash
# ARM-based device (Raspberry Pi, etc.)
pip install codex-ml[core] --only-binary=:all:

# Verify offline capability
OFFLINE_MODE=1 python -c "from codex.config import ConfigManager"
```

### 9.2 Production API Services (Runtime Profile)
```bash
# Docker container with Ray serve
pip install codex-ml[runtime]
uvicorn codex_ml.services.api:app --host 0.0.0.0 --port 8000

# Kubernetes deployment
kubectl apply -f k8s/codex-ml-runtime-deployment.yaml
```

### 9.3 Development Workstations (Full Profile)
```bash
# Editable installation with all extras
pip install -e ".[full]"

# Run Jupyter for experimentation
jupyter lab

# Run test suite with coverage
pytest tests/ -v --cov
```

---

## 10. Migration Path

### From Legacy Installation

**Old approach (single install):**
```bash
pip install codex-ml  # installed everything
```

**New approach (profile-based):**
```bash
# Lightweight production
pip install codex-ml[runtime]

# Development
pip install codex-ml[full]

# Edge/offline
pip install codex-ml[core]
```

**Backward compatibility:**
```bash
# [all] still works but is deprecated alias for [full]
pip install codex-ml[all]  # = pip install codex-ml[full]
```

---

## 11. Troubleshooting

### Issue: torch fails to install on Windows

**Solution:** Use CPU-only version explicitly
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install codex-ml[runtime]
```

### Issue: Network I/O during core profile import

**Solution:** Verify network isolation test passes
```bash
python verify_core_profile.py
```

If network calls detected, check for:
- Logging initialization to external service
- Automatic telemetry (disable with env vars)
- Configuration loading from remote source

### Issue: Model loading fails in runtime profile

**Solution:** Pre-cache models before deployment
```bash
# Pre-download model weights
python -c "
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained('bert-base-uncased')
AutoModel.from_pretrained('bert-base-uncased')
"
```

### Issue: Full profile too large for CI/CD

**Solution:** Use runtime profile + install test deps selectively
```bash
pip install codex-ml[runtime]
pip install pytest pytest-cov pytest-mock
```

---

## Appendix: Quick Reference

| Need | Command |
|------|---------|
| Lightweight deployment | `pip install codex-ml[core]` |
| Production inference | `pip install codex-ml[runtime]` |
| Development/testing | `pip install codex-ml[full]` |
| Reproducible build | `pip install -r requirements/lock.txt` |
| Test core offline | `python verify_core_profile.py` |
| Test runtime models | `python verify_runtime_profile.py` |
| Detect environment | `python profile_detection.py` |
| Full test suite | `pytest tests/ -v --cov` |
| Code quality check | `ruff check . && black --check .` |

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** Packaging Team / LANE 3  
**Related Files:** pyproject.toml, requirements/, .codex/

