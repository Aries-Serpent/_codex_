# Quick Start Guide for _codex_ Contributors

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-11  
> **Audience**: New contributors, AI agents, developers

---

## 🚀 5-Minute Setup

### Prerequisites

```bash
# Required
Python 3.10+
Git 2.30+
uv (recommended) or pip

# Optional
Docker (for containerized development)
```

### Quick Install

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install dependencies (using uv - recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"

# Verify installation
python -c "import codex; print(codex.__version__)"
```

### Run Tests

```bash
# Quick test (essential tests only)
pytest tests/unit/ -v --tb=short

# Full test suite
nox -s tests

# ML-specific tests
nox -s ml_tests
```

---

## 📁 Repository Structure

```
_codex_/
├── agents/                 # AI Agent infrastructure
│   ├── agent_memory.py     # Persistent memory system
│   ├── self_healing.py     # Automated remediation
│   ├── quantum_game_theory.py  # Physics-inspired decision making
│   └── prompts/            # Prompt templates
├── src/codex_ml/           # Core ML framework
│   ├── evaluation/         # Model evaluation
│   ├── features/           # Feature store
│   ├── integrations/       # External integrations
│   ├── plugins/            # Plugin system
│   ├── serving/            # Model serving
│   └── utils/              # Utilities
├── scripts/                # Automation scripts
├── tests/                  # Test suites
├── docs/                   # Documentation
└── .github/workflows/      # CI/CD
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
| [AGENTS.md](.././agents.md) | Agent development guide |
| [ARCHITECTURE_BLUEPRINT.md](../../ARCHITECTURE_BLUEPRINT.md) | System architecture |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines |
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
