#  Codex ML: 5-Minute Onboarding Quickstart
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> **Total Setup Time:** 5 minutes (local) or 15 minutes (Docker)  
> **Audience:** New developers, ML engineers, AI researchers  
> **Updated: 2026-06-27

---

## ⚡ TL;DR — One-Command Setup

### Local Setup (Recommended)
```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
python -m codex.cli train --config config/examples/minimal.yaml
```

### Docker Setup
```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
docker build -t codex-ml .
docker run -it codex-ml python -m codex.cli train --config config/examples/minimal.yaml
```

** Success:** You should see training logs and a checkpoint saved to `outputs/`.

---

## 📋 Prerequisites Check (< 1 minute)

```bash
# Check Python version (need 3.12+)
python --version

# Check Git
git --version

# Check C++ compiler (for PyTorch)
gcc --version  # Linux
clang --version  # macOS
# Windows: Install Microsoft C++ Build Tools
```

| System | Command | Expected Output |
|--------|---------|-----------------|
| **Python** | `python --version` | Python 3.12.x |
| **Git** | `git --version` | git version 2.30+ |
| **C++ (Linux)** | `gcc --version` | gcc 9.0+ |
| **C++ (macOS)** | `clang --version` | clang 12.0+ |

---

##  Path 1: Local Development Setup (5 minutes)

### Step 1: Clone & Navigate (1 min)
```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
```

### Step 2: Create Virtual Environment (1 min)
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies (2 min)
```bash
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"  # Install in editable mode with dev dependencies
```

**Expected:** Should complete without errors. Total size ~1.5 GB.

### Step 4: Run First Example (1 min)
```bash
# Run the minimal training example
python -m codex.cli train --config config/examples/minimal.yaml

# Or try a specific example
python examples/basic_training.py
```

** Success Indicators:**
- Training logs appear in console
- Checkpoint saved to `outputs/checkpoints/`
- No errors or warnings

---

##  Path 2: Docker Setup (15 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
```

### Step 2: Build Docker Image
```bash
docker build -t codex-ml:latest .
```

### Step 3: Run Container
```bash
# Interactive shell
docker run -it codex-ml:latest /bin/bash

# Or run a command directly
docker run -it codex-ml:latest python -m codex.cli train --config config/examples/minimal.yaml
```

### Step 4: Mount Local Volume (for development)
```bash
docker run -it -v $(pwd):/workspace codex-ml:latest /bin/bash
cd /workspace
python -m codex.cli train --config config/examples/minimal.yaml
```

---

##  Path 3: Minimal Setup (Code Examples Only)

If you just want to explore code without full installation:

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install only core dependencies (minimal)
pip install -r requirements-minimal.txt

# Try an example
python -c "from codex.cli import app; print('Import successful!')"
```

---

## 🧭 What to Do Next?

###  Interested in Agents & Automation?
→ Read [Cognitive Brain Guide](./cognitive_brain/README.md)
- 145+ autonomous agents
- Decision-making patterns
- Self-healing CI/CD

###  Interested in Machine Learning?
→ Read [ML Training Guide](./training/README.md)
- Distributed training with PyTorch
- Hyperparameter tuning with Hydra
- Evaluation & benchmarking

### 🏗️ Interested in Infrastructure & Deployment?
→ Read [Infrastructure Guide](./infrastructure/README.md)
- Ray Serve for model serving
- Kubernetes deployment
- Cloud storage integration

### 🔧 Interested in Configuration & Customization?
→ Read [Configuration Guide](./configuration/HYDRA_GUIDE.md)
- Hydra defaults and sweeps
- Environment variables
- Plugin architecture

###  Want to Understand the Architecture?
→ Read [Architecture Deep Dive](./architecture/INDEX.md)
- 5-layer architecture
- Design patterns
- Extension points

### 🤝 Ready to Contribute?
→ Read [Contributing Guide](../CONTRIBUTING.md)
- Development workflow
- Code standards
- PR process

---

##  Verify Installation

Run this to verify everything is set up correctly:

```bash
# Check imports
python -c "
import codex
import hydra
import torch
import ray
print(' All core imports successful!')
"

# Check CLI
python -m codex.cli --help

# Run tests (quick smoke test)
pytest tests/unit/test_imports.py -v
```

---

## 🆘 Common Setup Issues

###  "Python 3.12 not found"
**Solution:** Install Python 3.12+
```bash
# macOS with Homebrew
brew install python@3.12
python3.12 -m venv .venv

# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv
python3.12 -m venv .venv

# Windows: Download from python.org
```

###  "ModuleNotFoundError: No module named 'torch'"
**Solution:** Reinstall dependencies
```bash
pip install --force-reinstall torch
pip install -e ".[dev]"
```

###  "C++ compiler not found (Windows)"
**Solution:** Install Microsoft C++ Build Tools
1. Download from [Microsoft Visual C++](https://visualstudio.microsoft.com/cpp-build-tools/)
2. Run installer and select "C++ build tools"
3. Restart terminal and try again

###  "cuda/GPU errors"
**Solution:** Use CPU-only build
```bash
# Uninstall GPU PyTorch
pip uninstall torch torchvision torchaudio -y

# Install CPU-only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

###  "Permission denied" on `.venv/bin/activate`
**Solution:** Make it executable
```bash
chmod +x .venv/bin/activate
source .venv/bin/activate
```

**More issues?** → See [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

## 🎓 Next Steps: Learning Paths

### Beginner Path (2-4 hours)
1. **Installation & First Run** ← You are here
2. **[Navigate the Codebase](./LEARNING_PATHS.md#beginner-path)**
3. **Run the First Example**
4. **Understand Hydra Configuration**

### Intermediate Path (6-8 hours)
1. **Understand the 5-Layer Architecture**
2. **Train a Custom Model**
3. **Evaluate & Debug**
4. **Add a Custom Component**

### Advanced Path (10-16 hours)
1. **Deep Dive: Cognitive Brain**
2. **Contributing New Features**
3. **Performance Optimization**
4. **Security & Hardening**

→ Full paths: [Learning Paths](./LEARNING_PATHS.md)

---

##  Key Resources

| Resource | Purpose | Time |
|----------|---------|------|
| [Quick Start](./onboarding/QUICK_START.md) | Extended setup guide | 15 min |
| [Architecture](./architecture/INDEX.md) | System design & layers | 20 min |
| [Configuration](./configuration/HYDRA_GUIDE.md) | Hydra + OmegaConf guide | 10 min |
| [Contributing](../CONTRIBUTING.md) | Development workflow | 10 min |
| [Troubleshooting](./TROUBLESHOOTING.md) | Common issues & fixes | As needed |

---

##  Pro Tips

- **Use editable install**: `pip install -e ".[dev]"` lets you edit code without reinstalling
- **Activate venv every session**: Always run `source .venv/bin/activate` before coding
- **Check requirements**: Different setups available:
  - `requirements-minimal.txt` — Core only
  - `requirements.txt` — Full feature set
  - `requirements-dev.txt` — Development tools
  - `requirements-test.txt` — Testing tools
- **Use Docker for reproducibility**: Docker ensures same environment across machines
- **Test your setup early**: Run tests to catch issues before starting development

---

##  Getting Help

- **Setup issues?** → [Troubleshooting Guide](./TROUBLESHOOTING.md)
- **Architecture questions?** → [Architecture Guide](./architecture/INDEX.md)
- **Configuration help?** → [Configuration Guide](./configuration/HYDRA_GUIDE.md)
- **Contributing?** → [Contributing Guide](../CONTRIBUTING.md)
- **Found a bug?** → [Open an Issue](https://github.com/Aries-Serpent/_codex_/issues)

---

## ✨ You're Ready!

You've successfully set up Codex ML! 🎉

**Next:** Pick a path above based on your interests and start exploring.

**Questions?** Check [Troubleshooting](./TROUBLESHOOTING.md) or open an issue.

**Happy coding!** 
