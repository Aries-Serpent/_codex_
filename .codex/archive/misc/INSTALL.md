# Install Guide - Aries-Serpent ML v0.1.0-final

## Prerequisites

- Python 3.12+
- `pip` (latest)
- Release artifact: `codex_ml-0.1.0-py3-none-any.whl`

## Installation Profiles

Aries-Serpent ML uses a **3-profile packaging strategy**:

| Profile | Size | Use Case | Install Command |
|---------|------|----------|-----------------|
| **core** | 8-15 MB | Lightweight, offline-first, edge devices | `pip install codex-ml[core]==0.1.0` |
| **runtime** | 20-35 MB | Production inference + services | `pip install codex-ml[runtime]==0.1.0` |
| **full** | 100+ MB | Development + all features | `pip install codex-ml[full]==0.1.0` |

## Standard Install (PyPI)

### Recommended: From PyPI (Latest v0.1.0-final)

```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m pip install --upgrade pip

# Install from PyPI (v0.1.0)
python -m pip install codex-ml==0.1.0

# Or install with specific profile
python -m pip install 'codex-ml[core]==0.1.0'      # Lightweight
python -m pip install 'codex-ml[runtime]==0.1.0'   # Production
python -m pip install 'codex-ml[full]==0.1.0'      # Development

# Verify installation
python -c "import codex; print(codex.__version__)"
```

## Local Wheel Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Install from wheel file
python -m pip install codex_ml-0.1.0-py3-none-any.whl

# Verify installation
codex --help
```

## Offline Install (Air-Gapped)

Use `OFFLINE_BOOTSTRAP.sh` with a local wheelhouse.
The bootstrap flow uses the offline bootstrap module directly.

```bash
./OFFLINE_BOOTSTRAP.sh \
  --wheelhouse ./wheelhouse \
  --artifact ./dist/codex_ml-0.1.0-py3-none-any.whl
```

## Verify Isolated Networking

By default, networking is fail-closed via `.codex/network-policy.yaml`.
Only localhost is allowlisted until explicitly expanded.

## Installation Profiles in Detail

### Core Profile (8-15 MB)
**Use Case:** Edge devices, lightweight deployments, offline-first environments

```bash
pip install codex-ml[core]==0.1.0
```

**Includes:**
- Core codex runtime
- CLI interface (Typer)
- Configuration engine (Hydra)
- Lightweight utilities

**Does NOT include:**
- ML frameworks (PyTorch, Transformers)
- Evaluation tools
- Ray Serve
- Heavy dependencies

### Runtime Profile (20-35 MB)
**Use Case:** Production inference, API services, model serving

```bash
pip install codex-ml[runtime]==0.1.0
```

**Includes:**
- Everything in core
- PyTorch + Transformers
- Ray Serve
- FastAPI integration
- Model serving infrastructure

**Does NOT include:**
- Training utilities
- Development tools
- Full test suites
- Optional integrations

### Full Profile (100+ MB)
**Use Case:** Development, research, testing, all features

```bash
pip install aries-serpent-ml[full]==0.1.0
```

**Includes:**
- Everything in core and runtime
- Training engines
- Evaluation frameworks (lm-eval)
- Development tools
- Testing infrastructure
- All optional integrations

## Verification

After installation, verify everything works:

```bash
# Check version
python -c "import codex; print(codex.__version__)"

# Test CLI
codex --help

# Test imports
python -c "from codex_ml import ModelHandle; print('✓ Core ML import OK')"
python -c "from codex.cognitive import OODAOrchestrator; print('✓ Cognitive Brain import OK')"
```

## Upgrading from Previous Versions

```bash
# Upgrade to latest v0.1.0
pip install --upgrade aries-serpent-ml==0.1.0

# Upgrade to latest with profile
pip install --upgrade 'aries-serpent-ml[runtime]==0.1.0'
```

## Uninstall

```bash
pip uninstall aries-serpent-ml
```

## Getting Help

- **Installation Issues:** [.codex/archive/misc/INSTALL.md](.codex/archive/misc/INSTALL.md)
- **Quick Start ML:** [docs/quickstart/QUICK_START_ML.md](docs/quickstart/QUICK_START_ML.md)
- **Getting Started Guide:** [docs/getting-started.md](docs/getting-started.md)
- **Full Documentation:** [docs/](docs/)

```bash
python - <<'PY'
from safety import PolicyViolationError, enforce_network_policy

try:
    enforce_network_policy("https://example.com")
except PolicyViolationError:
    print("policy enforcement active")
PY
```
