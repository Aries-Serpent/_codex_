# Quick Start Guide for _codex_ Contributors

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Audience**: New contributors, AI agents, developers  
> **⏱️ Setup Time:** 5-15 minutes (30 min with Docker)

---

## 🚀 CHOOSE YOUR SETUP PATH

### Path A: Local Development (Recommended for Development) — 5-10 minutes

Best for: Active code development, rapid iteration, debugging

### Path B: Docker Development — 10-15 minutes

Best for: Isolated environment, reproducible setup, avoiding dependency conflicts

### Path C: Minimal Setup (Code Examples Only) — 5 minutes

Best for: Testing examples, simple scripts, learning

---

## 📋 Prerequisites

| Requirement | Linux | macOS | Windows | Notes |
|-------------|-------|-------|---------|-------|
| **Python 3.10+** | ✅ apt/dnf | ✅ Homebrew | ✅ winget/Chocolatey | `python --version` |
| **Git 2.30+** | ✅ apt/dnf | ✅ Homebrew | ✅ winget | `git --version` |
| **C/C++ compiler** | ✅ gcc/g++ | ✅ Xcode CLT | ⚠️ MSVC | For PyTorch compilation |
| **~2 GB free disk** | Required | Required | Required | Source + dependencies |

**Check prerequisites:**
```bash
python --version  # Should be 3.10+
git --version     # Should be 2.30+
gcc --version     # (Linux only) Should be 9.0+
```

---

## PATH A: Local Development Setup (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
```

**Troubleshooting:**
- `fatal: not a git repository`: Make sure you're in the cloned directory
- `Permission denied`: Use `ssh` key or `https` with PAT token

### Step 2: Install Dependencies

**Using `uv` (Recommended - Faster):**
```bash
# Install uv if needed
curl https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e ".[dev]"

# Install optional dependencies (ML stack)
uv pip install -e ".[ml,dev]"
```

**Using `pip` (Standard):**
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install optional ML stack
pip install -e ".[ml,dev]"
```

**Troubleshooting Common Issues:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'setuptools'` | Run `pip install --upgrade pip setuptools` |
| `error: legacy-install-failure` (on pip install) | Use `uv pip install` or update pip: `pip install --upgrade pip` |
| `CUDA not available` (PyTorch warning) | Normal if no GPU; CPU-only is fine for development |
| `Permission denied` on `/usr/local` | Use `python -m pip install --user -e ".[dev]"` |

### Step 3: Verify Installation

```bash
# Test Python imports
python -c "import codex; print(f'✅ _codex_ {codex.__version__} installed')"

# Test CLI
codex-cli --help

# Test core modules
python -c "import codex_ml; import src.mcp; print('✅ All core modules loaded')"
```

**Expected output:**
```
✅ _codex_ 0.1.0 installed
✅ All core modules loaded
```

### Step 4: Run Quick Tests

```bash
# Quick validation (1-2 minutes)
pytest tests/unit/test_imports.py -v

# Run specific test suite (2-5 minutes)
pytest tests/unit/ -v --tb=short -k "not slow"

# Full test suite (10-15 minutes)
pytest tests/ -v
```

**Troubleshooting:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` in tests | Re-run `uv pip install -e ".[dev]"` |
| `Segmentation fault` (PyTorch) | Likely environment issue; try Docker path |
| Tests timeout | Run with `--timeout=60` or use Path B (Docker) |

---

## PATH B: Docker Development Setup

### Step 1: Install Docker

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER  # Add user to docker group
```

**macOS:**
```bash
brew install docker docker-compose
# OR download Docker Desktop from https://www.docker.com/products/docker-desktop
```

**Windows:**
```bash
# Download Docker Desktop: https://www.docker.com/products/docker-desktop
# OR use winget: winget install Docker.DockerDesktop
```

### Step 2: Build & Run Docker Container

```bash
# Clone and enter directory
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Build Docker image (first time: 5-10 minutes)
docker build -t codex-dev:latest -f Dockerfile.dev .

# Run container with volume mount (interactive development)
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  codex-dev:latest \
  bash

# Inside container:
python -c "import codex; print(codex.__version__)"
pytest tests/unit/ -v
```

**Troubleshooting:**

| Error | Solution |
|-------|----------|
| `docker: command not found` | Docker not installed or not in PATH |
| `permission denied` | Run with `sudo` OR add user to docker group: `sudo usermod -aG docker $USER` |
| `image not found` | Rebuild with `docker build ...` or pull from registry |

---

## PATH C: Minimal Setup (Code Examples Only)

**For running code examples without full development environment:**

```bash
# Install minimal dependencies
pip install transformers torch numpy

# Test basic import
python -c "from transformers import AutoTokenizer; print('✅ Ready for examples')"
```

---

## 📁 Repository Structure

```
_codex_/
├── agents/                     # AI Agent infrastructure
│   ├── agent_memory.py         # Persistent memory system
│   ├── self_healing.py         # Automated remediation
│   ├── quantum_game_theory.py  # Physics-inspired decision making
│   └── prompts/                # Prompt templates
├── src/
│   ├── codex_ml/               # Core ML framework
│   │   ├── evaluation/         # Model evaluation
│   │   ├── training/           # Training pipeline
│   │   ├── serving/            # Model serving (FastAPI + Ray Serve)
│   │   └── utils/              # Utilities
│   ├── mcp/                    # Model Context Protocol (MCP) system
│   │   ├── server/             # MCP server implementation
│   │   ├── backends/           # Backend adapters (Pinecone, Redis, etc.)
│   │   └── embeddings/         # Embedding system
│   └── codex_cli/              # Command-line interface
├── tests/                      # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
├── docs/                       # Documentation (you are here!)
│   ├── onboarding/             # Getting started guides
│   ├── deployment/             # Production deployment guides
│   ├── api/                    # API references
│   └── troubleshooting/        # Troubleshooting guides
├── scripts/                    # Automation scripts
├── docker/                     # Docker configurations
├── .github/workflows/          # CI/CD workflows
├── pyproject.toml              # Python project metadata
└── README.md                   # Root project README
```

---

## 🔧 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow these guidelines:
- Keep changes minimal and focused
- Add tests for new functionality
- Update documentation if needed

### 3. Run Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/codex_ml/

# Run tests
pytest tests/ -v
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: description of your change"
git push origin feature/your-feature-name
```

### 5. Open Pull Request

Use the PR template and ensure:
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code review requested

---

## 🤖 AI Agent Integration

### Using Agent Memory

```python
from agents.agent_memory import AgentMemorySystem

# Initialize memory system
memory = AgentMemorySystem(agent_id="my_agent")

# Start a task
frame = memory.start_task("Fix code review comments")

# Record decisions
memory.store_decision(
    task_id="task_123",
    decision="Use AST parsing",
    rationale="More reliable than regex",
    context={"file": "analyzer.py"}
)

# Get guidance
guidance = memory.get_guidance("debug test failure")
print(guidance['suggested_approach'])

# Complete task
memory.complete_task(success=True, summary="Fixed all issues")
```

### Using Self-Healing

```python
from agents.self_healing import SelfHealingEngine

# Initialize engine
engine = SelfHealingEngine(repo_path=".")

# Run health check
report = engine.run_health_check()
print(f"Health score: {report.health_score}")

# Get remediation suggestions
for issue in report.issues:
    print(f"Issue: {issue.description}")
    print(f"Fix: {issue.suggested_fix}")
```

---

## 📚 Key Documentation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](../agents.md) | Agent development guide |
| [ARCHITECTURE_BLUEPRINT.md](../ARCHITECTURE_BLUEPRINT.md) | System architecture |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines |
| [API_REFERENCE.md](../API_REFERENCE.md) | API documentation |
| [INCIDENT_RESPONSE.md](../operations/INCIDENT_RESPONSE.md) | Incident procedures |

---

## 🔍 Common Tasks

### Adding a New Feature

1. Check existing implementations in `src/codex_ml/`
2. Add implementation with tests
3. Update `__init__.py` exports
4. Add documentation

### Debugging Test Failures

1. Check `agents/prompts/debugging/test-failure-debugging.md`
2. Run specific test: `pytest tests/path/to/test.py::test_name -v`
3. Use `--pdb` for interactive debugging

### Running Security Scans

```bash
# Run security scans
bandit -r src/ -ll

# Check dependencies
pip-audit

# Secret scanning
detect-secrets scan
```

---

## 🆘 Getting Help

1. **Documentation**: Check `/docs` directory
2. **Issues**: Search existing GitHub issues
3. **Prompts**: Use `agents/prompts/` for AI assistance
4. **Troubleshooting**: See `docs/troubleshooting/`

---

## ✅ Checklist for First PR

- [ ] Forked and cloned repository
- [ ] Installed dependencies
- [ ] Tests pass locally
- [ ] Created feature branch
- [ ] Made focused changes
- [ ] Added/updated tests
- [ ] Ran linting and formatting
- [ ] Updated documentation
- [ ] Opened PR with template

---

Welcome to the _codex_ project! 🎉
