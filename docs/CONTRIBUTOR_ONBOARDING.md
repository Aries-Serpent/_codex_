# Contributor Onboarding Guide

Welcome to the Codex repository! This guide will help you get started as a contributor, whether you're a human developer or an AI Agent.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Repository Overview](#repository-overview)
3. [Development Setup](#development-setup)
4. [Understanding the Codebase](#understanding-the-codebase)
5. [Making Your First Contribution](#making-your-first-contribution)
6. [Testing Guidelines](#testing-guidelines)
7. [Code Review Process](#code-review-process)
8. [AI Agent Integration](#ai-agent-integration)
9. [Common Workflows](#common-workflows)
10. [Getting Help](#getting-help)

---

## Quick Start

### For Human Contributors

```bash
# 1. Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .
pip install -r requirements-dev.txt

# 4. Run tests to verify setup
pytest tests/ -v

# 5. Start exploring!
python -m codex.cli --help
```

### For AI Agents

```
1. Read AGENTS.md for comprehensive agent guidance
2. Review agents/prompts/ for pre-defined workflows
3. Use workflow navigator for common tasks
4. Follow this onboarding guide for contribution patterns
```

---

## Repository Overview

### Purpose

Codex is a Level 4 MLOps production system with:
- **Audit Pipeline v1.5.5**: Deterministic capability tracking
- **1,208+ tests**: Comprehensive test coverage
- **693 documentation files**: Extensive documentation
- **AI-First Design**: Built for AI Assistant/Agent intuitiveness

### Key Statistics

- **MLOps Maturity**: Level 4 Certified (100/100 score)
- **Test Coverage**: 72%
- **Capabilities Tracked**: 39 (18/18 critical at maturity)
- **Python Version**: 3.9-3.12 supported
- **Repository Size**: ~200,000 lines of code

### Architecture

```
_codex_/
├── src/codex_ml/          # Core ML code
├── training/              # Training pipelines
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── agents/                # AI Agent infrastructure
├── .github/workflows/     # CI/CD pipelines
└── requirements*.txt      # Dependencies
```

---

## Development Setup

### Prerequisites

- Python 3.9+ (3.12 recommended)
- Git
- pip and virtualenv
- (Optional) Docker for containerized development

### Detailed Setup

#### 1. Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Common variables:
- `CODEX_ENV_PYTHON_VERSION`: Python version (default: detected)
- `CODEX_SESSION_ID`: Session identifier
- `CODEX_LOG_DB_PATH`: SQLite database path

#### 2. Install Development Tools

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install linters
pip install ruff black isort mypy

# Install testing tools
pip install pytest pytest-cov hypothesis
```

#### 3. Verify Installation

```bash
# Check Python installation
python --version

# Check dependencies
pip list | grep -E "pytest|ruff|black"

# Run sample test
pytest tests/test_tokenization.py -v
```

#### 4. IDE Setup

**VS Code:**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

**PyCharm:**
- Enable Ruff in Settings → Tools → External Tools
- Set test runner to pytest
- Enable type checking with mypy

---

## Understanding the Codebase

### Core Concepts

#### 1. Deterministic Audit Pipeline

Located in `scripts/space_traversal/`:
- `audit_runner.py`: Main audit orchestration
- `trend_database.py`: SQLite-based trend storage
- `viz_*.py`: Multiple visualization formats

#### 2. Capability System

Capabilities are tracked and scored:
- **Config**: `codex_capability_map.yaml`
- **Scores**: `audit_artifacts/capabilities_scored.json`
- **Trends**: `.codex/trends/trends.db`

#### 3. Agent Infrastructure

Located in `agents/`:
- `workflow_navigator.py`: Tokenized workflow execution
- `prompts/`: Pre-defined prompts for common tasks
- `ORCHESTRATION.md`: Physics-inspired decision-making

#### 4. Testing Philosophy

- **Comprehensive**: 1,208+ test files
- **Fast**: Most tests run in < 1 second
- **Isolated**: Each test is independent
- **Deterministic**: No flaky tests

### Code Organization

```
Key Files:
- AGENTS.md                 # Main agent guide
- COMPREHENSIVE_GAP_ANALYSIS.md  # Current gaps and priorities
- codex_gap_registry.yaml   # Known gaps tracking

Core Modules:
- src/codex_ml/training/    # Training pipelines
- src/codex_ml/evaluation/  # Evaluation metrics
- src/codex_ml/connectors/  # Storage connectors
- src/codex_ml/plugins/     # Plugin system

Scripts:
- scripts/space_traversal/  # Audit pipeline
- scripts/archive_files.py  # Archival automation
- scripts/dependency_analyzer.py  # Dependency analysis

Tests:
- tests/                    # Main test suite
- tests/capabilities/       # Capability-specific tests
- tests/space_traversal/    # Audit pipeline tests
```

---

## Making Your First Contribution

### Step-by-Step Guide

#### 1. Find an Issue

Good first issues:
- Look for `good-first-issue` label
- Check `COMPREHENSIVE_GAP_ANALYSIS.md` for priorities
- Review `codex_gap_registry.yaml` for known gaps

#### 2. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/bug-description
```

#### 3. Make Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation if needed
- Keep commits small and focused

#### 4. Run Tests and Linters

```bash
# Format code
black src/ scripts/ tests/
isort src/ scripts/ tests/

# Lint code
ruff check src/ scripts/ tests/

# Run tests
pytest tests/ -v

# Type check (if applicable)
mypy src/codex_ml/
```

#### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add feature description

- Detail 1
- Detail 2"

# Push to your fork
git push origin feature/your-feature-name
```

#### 6. Create Pull Request

- Go to GitHub repository
- Click "New Pull Request"
- Fill in PR template
- Link related issues
- Wait for review

### Commit Message Format

Use conventional commits:

```
type(scope): Short description

Longer description if needed

- Bullet point 1
- Bullet point 2

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/modifications
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

---

## Testing Guidelines

### Writing Tests

```python
# tests/test_example.py
import pytest

def test_basic_functionality():
    """Test basic functionality."""
    result = function_under_test()
    assert result == expected_value

def test_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        function_with_error()

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["key"] == "value"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific file
pytest tests/test_example.py -v

# Run specific test
pytest tests/test_example.py::test_basic_functionality -v

# Run with coverage
pytest tests/ --cov=src/codex_ml --cov-report=term

# Run tests matching pattern
pytest -k "tokenization" -v
```

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Smoke tests**: Quick sanity checks
- **Property-based tests**: Hypothesis-driven tests

---

## Code Review Process

### Review Checklist

**For Authors:**
- [ ] Tests pass locally
- [ ] Code is formatted and linted
- [ ] Documentation updated
- [ ] PR description is clear
- [ ] Commits are clean

**For Reviewers:**
- [ ] Code follows repository conventions
- [ ] Tests are comprehensive
- [ ] Changes are minimal and focused
- [ ] Documentation is accurate
- [ ] No security vulnerabilities

### Responding to Feedback

- Address all comments
- Ask for clarification if needed
- Make requested changes in new commits
- Re-request review when ready

---

## AI Agent Integration

### For AI Agents

The repository is designed for AI Agent intuitiveness:

#### Workflow Navigator

```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()

# Execute audit
navigator.execute('AUDIT_EXEC')

# Generate documentation
navigator.execute('DOC_GEN')

# Self-healing
navigator.execute('SELF_HEAL')
```

#### Pre-Defined Prompts

Located in `agents/prompts/`:
- **Audit**: audit/run-full-audit.md
- **Debugging**: debugging/test-failure-debugging.md
- **Organization**: organization/repository-cleanup.md
- **Deployment**: deployment/pre-release-deployment.md

#### Agent Guidelines

Read `AGENTS.md` for comprehensive guidance on:
- Agent architecture
- Workflow tokens
- Physics-inspired orchestration
- Mental mapping

---

## Common Workflows

### Workflow 1: Add New Test

```bash
# 1. Create test file
touch tests/test_new_feature.py

# 2. Write test
cat > tests/test_new_feature.py << 'EOF'
def test_new_feature():
    assert True
EOF

# 3. Run test
pytest tests/test_new_feature.py -v

# 4. Commit
git add tests/test_new_feature.py
git commit -m "test: Add tests for new feature"
```

### Workflow 2: Fix Bug

```bash
# 1. Reproduce bug
pytest tests/test_failing.py -v

# 2. Fix bug in source
# Edit src/codex_ml/module.py

# 3. Verify fix
pytest tests/test_failing.py -v

# 4. Commit
git add src/codex_ml/module.py
git commit -m "fix: Fix issue with module"
```

### Workflow 3: Run Audit Pipeline

```bash
# Full audit
python scripts/space_traversal/audit_runner.py run

# Generate dashboard
python scripts/generate_audit_dashboard.py

# Check results
cat audit_artifacts/capabilities_scored.json | jq '.[] | select(.score < 0.85)'
```

### Workflow 4: Update Documentation

```bash
# Edit documentation
vim docs/my-doc.md

# Preview (if using mkdocs)
mkdocs serve

# Commit
git add docs/my-doc.md
git commit -m "docs: Update documentation for feature"
```

---

## Getting Help

### Resources

- **AGENTS.md**: Comprehensive agent guide
- **CONTRIBUTING.md**: Contribution guidelines
- **COMPREHENSIVE_GAP_ANALYSIS.md**: Current priorities
- **agents/prompts/**: Pre-defined workflows

### Asking Questions

1. Check existing documentation first
2. Search closed issues/PRs
3. Open new issue with:
   - Clear problem description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Debugging Tips

See `agents/prompts/debugging/`:
- Test failure debugging
- Merge conflict resolution
- Performance optimization
- Security remediation

---

## Next Steps

Now that you're onboarded:

1. **Explore the codebase**: Browse `src/`, `scripts/`, `tests/`
2. **Run the audit pipeline**: `python scripts/space_traversal/audit_runner.py run`
3. **Read key documentation**: AGENTS.md, COMPREHENSIVE_GAP_ANALYSIS.md
4. **Find your first issue**: Check good-first-issue labels
5. **Join the community**: Engage with other contributors

### Suggested First Contributions

- Add tests for uncovered code
- Improve documentation
- Fix small bugs
- Enhance AI Agent prompts
- Optimize performance bottlenecks

---

## Conclusion

Welcome to the Codex project! We're excited to have you as a contributor. This repository is designed to be AI-friendly, well-documented, and maintainable.

**Remember:**
- Start small
- Ask questions
- Follow conventions
- Write tests
- Have fun!

**Happy Contributing! 🚀**

---

## Appendix: Useful Commands

```bash
# Development
python -m codex.cli --help
python scripts/space_traversal/audit_runner.py --help

# Testing
pytest tests/ -v
pytest -k "pattern" -v
pytest --collect-only

# Linting
ruff check .
black --check .
isort --check .

# Type Checking
mypy src/codex_ml/

# Git
git status
git log --oneline -10
git diff main..HEAD

# Dependencies
pip list
pip freeze > requirements.txt
```

---

**Last Updated**: Previous Cycle-12-11  
**Version**: 1.0.0  
**Maintainer**: Codex Team
