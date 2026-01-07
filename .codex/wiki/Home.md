# Welcome to the _codex_ Wiki

**Repository:** [Aries-Serpent/_codex_](https://github.com/Aries-Serpent/_codex_)  
**Purpose:** ML training, evaluation, and plugin framework with autonomous agent capabilities  
**Status:** Active Development | Genesis Protocol Phase 1 Complete

---

## 🚀 Quick Start

### For Developers

**Getting Started in 5 Minutes:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aries-Serpent/_codex_.git
   cd _codex_
   ```

2. **Set up environment:**
   ```bash
   # Python 3.11+ required, 3.12 recommended
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

4. **Explore the codebase:**
   ```bash
   # View documentation
   cat README.md
   cat AGENTS.md
   
   # Check configuration
   ls configs/
   ```

### For AI Agents

**New AI Agent Orientation:**

1. 📚 **Must Read First:** [AGENTS.md](https://github.com/Aries-Serpent/_codex_/blob/main/AGENTS.md)
2. 🛡️ **Understand Constraints:** [Guardrails](https://github.com/Aries-Serpent/_codex_/blob/main/.codex/guardrails.md)
3. 🤖 **Operational Guide:** [Agent Operations](Agent-Operations.md)
4. 🎯 **Genesis Protocol:** [Genesis Protocol Guide](Genesis-Protocol.md)

---

## 📖 Documentation Structure

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [Home](Home.md) | Repository overview and quick start | Everyone |
| [README.md](https://github.com/Aries-Serpent/_codex_/blob/main/README.md) | Project introduction | Developers |
| [AGENTS.md](https://github.com/Aries-Serpent/_codex_/blob/main/AGENTS.md) | AI agent documentation | AI Agents |
| [CONTRIBUTING.md](https://github.com/Aries-Serpent/_codex_/blob/main/CONTRIBUTING.md) | Contribution guidelines | Contributors |

### Specialized Topics

| Document | Purpose | Audience |
|----------|---------|----------|
| [Genesis Protocol](Genesis-Protocol.md) | Autonomous agent initialization | Admins, Agents |
| [Agent Operations](Agent-Operations.md) | Agent decision framework | AI Agents |
| [Security](https://github.com/Aries-Serpent/_codex_/blob/main/SECURITY.md) | Security policies and reporting | Everyone |
| [Governance](https://github.com/Aries-Serpent/_codex_/blob/main/GOVERNANCE.md) | Project governance | Contributors |

---

## 🏗️ Repository Architecture

### Project Structure

```
_codex_/
├── .codex/              # Configuration and agent files
│   ├── guardrails.md    # Operational constraints
│   ├── autonomous_agent.yaml  # Agent configuration
│   ├── change_log.md    # Audit trail
│   └── wiki/            # Wiki documentation
├── .github/
│   └── workflows/       # CI/CD pipelines (disabled pre-Genesis)
├── src/
│   └── codex_ml/        # Main package
│       ├── cli.py       # Command-line interface
│       ├── training/    # Training utilities
│       ├── eval/        # Evaluation tools
│       └── utils/       # Helper functions
├── tests/               # Test suite (1500+ tests)
├── docs/                # Extended documentation
├── configs/             # Hydra configuration files
├── scripts/             # Automation scripts
└── examples/            # Usage examples
```

### Key Components

**Core Modules:**
- `codex_ml.training` - Training engines and utilities
- `codex_ml.eval` - Evaluation and metrics
- `codex_ml.monitoring` - MLflow, W&B integration
- `codex_ml.data` - Data loading and preprocessing
- `codex_ml.utils` - Shared utilities

**Configuration System:**
- **Hydra-based:** Flexible configuration management
- **Config Files:** Located in `configs/`
- **Override Syntax:** `python -m codex_ml.cli train --config configs/training/base.yaml trainer.epochs=10`

---

## 🧪 Testing

### Test Coverage

**Current Status:** 72% coverage | 1500+ tests

**Test Categories:**
- Unit tests: Core functionality
- Integration tests: End-to-end workflows
- Property-based tests: Edge case discovery (Hypothesis)
- Smoke tests: Quick validation

### Running Tests

```bash
# All tests
pytest tests/

# Specific category
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest tests/ --cov=src/codex_ml --cov-report=html

# Parallel execution
pytest tests/ -n auto

# Specific marker
pytest tests/ -m "not slow"
```

---

## 🔧 Development Workflow

### Standard Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test:**
   ```bash
   # Edit files
   # Run tests
   pytest tests/
   
   # Run linting
   ruff check .
   black .
   isort .
   ```

3. **Commit with conventional commits:**
   ```bash
   git commit -m "feat: add new training feature"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   # Open pull request on GitHub
   ```

### Code Quality Tools

**Linting and Formatting:**
- **Black:** Code formatting (line length: 100)
- **Ruff:** Fast Python linter
- **isort:** Import sorting
- **mypy:** Type checking

**Pre-commit Hooks:**
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📦 Key Dependencies

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **torch** | ≥2.6.0 | Deep learning framework |
| **transformers** | ≥4.48.0 | Hugging Face models |
| **hydra-core** | 1.3.2 | Configuration management |
| **mlflow** | ≥2.22.4 | Experiment tracking |
| **pytest** | ≥8.0.0 | Testing framework |

### Optional Dependencies

```bash
# Install with extras
pip install -e ".[dev]"      # Development tools
pip install -e ".[gpu]"      # GPU support
pip install -e ".[analysis]" # Code analysis
```

---

## 🔐 Security

### Security Status

**Last Scan:** 2025-12-26  
**Known Vulnerabilities:** 0 (after recent updates)  
**Security Score:** A+

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

**Instead:**
1. Email: Contact repository maintainer (@mbaetiong)
2. Use GitHub Security Advisories
3. Include: Description, impact, reproduction steps

See [SECURITY.md](https://github.com/Aries-Serpent/_codex_/blob/main/SECURITY.md) for details.

---

## 🤝 Contributing

### How to Contribute

1. Read [CONTRIBUTING.md](https://github.com/Aries-Serpent/_codex_/blob/main/CONTRIBUTING.md)
2. Check existing issues or create a new one
3. Fork the repository
4. Create a feature branch
5. Make your changes with tests
6. Submit a pull request

### Code of Conduct

This project follows a [Code of Conduct](https://github.com/Aries-Serpent/_codex_/blob/main/CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

## 📊 Project Stats

**Repository Metrics:**
- **Language:** Python (78.3%), Markdown (18%), Shell (2.5%)
- **Tests:** 1500+ test cases
- **Coverage:** 72%
- **Documentation:** 100+ markdown files
- **Contributors:** Community-driven

**Activity:**
- **Status:** Active Development
- **Last Update:** 2025-12-26
- **Next Milestone:** Genesis Protocol Phase 2

---

## 🔗 External Resources

### Community

- **GitHub Issues:** [Report bugs, request features](https://github.com/Aries-Serpent/_codex_/issues)
- **Discussions:** [Ask questions, share ideas](https://github.com/Aries-Serpent/_codex_/discussions)
- **Pull Requests:** [View open PRs](https://github.com/Aries-Serpent/_codex_/pulls)

### Documentation Links

- **PyTorch Docs:** [pytorch.org/docs](https://pytorch.org/docs)
- **Hugging Face Docs:** [huggingface.co/docs](https://huggingface.co/docs)
- **Hydra Docs:** [hydra.cc/docs](https://hydra.cc/docs)
- **MLflow Docs:** [mlflow.org/docs](https://mlflow.org/docs)

---

## 🆘 Getting Help

### Common Issues

**Installation Problems:**
- Ensure Python 3.11+ is installed
- Try upgrading pip: `pip install --upgrade pip`
- Use virtual environment to avoid conflicts

**Test Failures:**
- Run `pytest tests/ -v` for detailed output
- Check test requirements: `pip install -e ".[dev]"`
- Review test logs in `pytest.log`

**Import Errors:**
- Install in editable mode: `pip install -e .`
- Verify installation: `pip list | grep codex-ml`

### Where to Ask

**Technical Questions:**
- GitHub Discussions for general questions
- GitHub Issues for bugs and feature requests
- Stack Overflow with tag `codex-ml` (if applicable)

**Contact:**
- **Maintainer:** @mbaetiong
- **Email:** Check SECURITY.md for contact info

---

## 📋 Changelog

See [CHANGES.md](https://github.com/Aries-Serpent/_codex_/blob/main/CHANGES.md) and [.codex/change_log.md](https://github.com/Aries-Serpent/_codex_/blob/main/.codex/change_log.md) for detailed change history.

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](https://github.com/Aries-Serpent/_codex_/blob/main/LICENSE) for details.

---

**Wiki Last Updated:** 2025-12-26  
**Wiki Version:** 1.0.0  
**Next Review:** After Genesis Phase 2 completion

**Navigation:** Use the sidebar to explore specific topics in depth.
