# Installation Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 0.1.0  
**Last Updated: 2026-07-09
**Audience:** DevOps, SRE, Developers

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Verification](#verification)
4. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Python | ≥3.12 | Runtime environment |
| pip | ≥24.0 | Python package manager |
| Docker | ≥20.10 (optional) | Container deployment |
| kubectl | ≥1.28 (optional) | Kubernetes cluster management |

### Verification

```bash
python --version  # Should output: Python 3.12.x or higher
pip --version     # Should output: pip 24.x or higher
```

---

## Installation Methods

### PyPI Installation (Recommended)

```bash
# Basic installation
pip install codex-ml==0.1.0

# With ML capabilities
pip install codex-ml[ml]==0.1.0

# With Cognitive Brain
pip install codex-ml[cognitive]==0.1.0

# All extras
pip install codex-ml[ml,cognitive,core,dev]==0.1.0

# Verify
python -c "import codex; print(f'Codex {codex.__version__}')"
```

### Docker Installation

```bash
# Pull image
docker pull aries-serpent-api:0.1.0-final

# Run container
docker run -p 8000:8000 aries-serpent-api:0.1.0-final

# Verify
curl http://localhost:8000/health
```

### From Source

```bash
# Clone
git clone https://github.com/Aries-Serpent/_codex_
cd _codex_

# Install with dev tools
pip install -e ".[dev,ml,cognitive]"

# Verify
python -m codex.cli --help
```

---

## Verification

```bash
# Import test
python -c "import codex; print(codex.__version__)"

# CLI test
python -m codex.cli --version

# ML test (if installed)
python -c "from codex.ml import InferencePipeline; print('OK')"
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'codex'`

```bash
pip install --force-reinstall codex-ml==0.1.0
```

### `ImportError: cannot import name 'X'`

```bash
pip install --upgrade codex-ml
pip install codex-ml[ml,cognitive,core]
```

### Docker pull fails

```bash
docker login
docker pull aries-serpent-api:0.1.0-final
```

### Port already in use

```bash
docker run -p 9000:8000 aries-serpent-api:0.1.0-final
```

---

**Documentation:** [docs/](../)  
**Issues:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)  
**Last Updated: 2026-07-09
