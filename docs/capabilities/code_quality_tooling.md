# Code Quality Tooling

> **Navigation**: [📖 Main README](../../README.md#-capabilities-documentation) | [💾 Checkpointing](checkpointing.md) | [🔄 Training Loops](train_loop.md) | [🎯 PEFT Techniques](peft_hooks.md) | [🔧 GitHub CLI Guide](../../.github/docs/GH_CLI_Resolution_Copilot.md)

## Overview

**Status**: ✅ Complete - Comprehensive code quality tooling guide with configurations and examples

This capability covers comprehensive code quality tooling for the _codex_ repository, including linting, formatting, type checking, and static analysis tools.

## Planned Content

This document will cover:
- **Linting**: Ruff, pylint configuration and usage
- **Formatting**: Black, isort integration
- **Type Checking**: mypy configuration and best practices
- **Static Analysis**: Security scanning and code analysis tools
- **CI Integration**: Automated quality checks in workflows

## Current Implementation

The _codex_ repository uses a modern Python code quality stack configured in `pyproject.toml`:

### Tools Overview

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Fast Python linter (replaces flake8, pylint, isort) | `pyproject.toml` |
| **Black** | Opinionated code formatter | `pyproject.toml` |
| **mypy** | Static type checker | `pyproject.toml` |
| **pytest** | Testing framework with coverage | `pyproject.toml` |
| **pre-commit** | Git hooks for quality checks | `.pre-commit-config.yaml` |

### pyproject.toml Configuration

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "S",   # flake8-bandit (security)
]
ignore = [
    "E501",  # Line too long (handled by Black)
    "S101",  # Use of assert (acceptable in tests)
]

[tool.ruff.per-file-ignores]
# Allow asserts and hardcoded secrets in tests
"tests/**/*.py" = ["S101", "S105", "S106"]
# Allow print statements in scripts
"scripts/**/*.py" = ["T201"]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  | archive
  | .hypothesis
  | .nox
)/
'''

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false  # Less strict for tests

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --cov=agents --cov-report=term-missing"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.coverage.run]
source = ["agents"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == \"__main__\":",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

### Running Quality Checks Locally

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all checks with nox
nox

# Run individual checks
nox -s lint      # Ruff linting
nox -s format    # Black formatting
nox -s typecheck # mypy type checking
nox -s tests     # pytest with coverage

# Quick checks before commit
pre-commit run --all-files

# Auto-fix issues
ruff check --fix .
black .
```

### noxfile.py Sessions

```python
import nox

@nox.session(python=["3.11", "3.12"])
def tests(session):
    """Run the test suite with pytest."""
    session.install("-e", ".[test]")
    session.run("pytest", "-v", "--cov=agents", "--cov-report=term-missing")

@nox.session
def lint(session):
    """Run linting with ruff."""
    session.install("ruff")
    session.run("ruff", "check", ".")

@nox.session
def format(session):
    """Check code formatting with black."""
    session.install("black")
    session.run("black", "--check", ".")

@nox.session
def typecheck(session):
    """Run type checking with mypy."""
    session.install("mypy", "-e", ".[dev]")
    session.run("mypy", "agents")

@nox.session
def security(session):
    """Run security scanning with bandit."""
    session.install("bandit[toml]")
    session.run("bandit", "-r", "agents", "-c", "pyproject.toml")
```

### Pre-commit Configuration

```.pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### CI Integration

The `.github/workflows/code-quality.yml` workflow runs all quality checks on every push and PR:

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install nox
      
      - name: Run linting
        run: nox -s lint
      
      - name: Check formatting
        run: nox -s format
      
      - name: Type checking
        run: nox -s typecheck
      
      - name: Run tests
        run: nox -s tests
      
      - name: Security scan
        run: nox -s security
```

## Related Capabilities

- **ci-cd-pipeline**: CI/CD integration
- **safeguards-detection**: Code safety analysis
- **documentation-system**: Documentation quality

## Best Practices

1. **Run Checks Before Committing**
   ```bash
   # Install pre-commit hooks
   pre-commit install
   
   # Hooks will run automatically on git commit
   # Or run manually:
   pre-commit run --all-files
   ```

2. **Fix Issues Automatically**
   ```bash
   # Auto-fix linting issues
   ruff check --fix .
   
   # Auto-format code
   black .
   
   # Both together
   ruff check --fix . && black .
   ```

3. **Ignore Specific Issues Sparingly**
   ```python
   # Inline ignore (use only when necessary)
   result = eval(user_input)  # noqa: S307
   
   # Type ignore (document why)
   value = some_untyped_library()  # type: ignore[no-untyped-call]
   ```

4. **Configure Per-File Rules**
   ```toml
   [tool.ruff.per-file-ignores]
   "tests/*.py" = ["S101"]  # Allow asserts in tests
   "scripts/*.py" = ["T201"]  # Allow prints in scripts
   ```

5. **Monitor Coverage Trends**
   ```bash
   # Generate HTML coverage report
   pytest --cov=agents --cov-report=html
   
   # View in browser
   open htmlcov/index.html
   ```

## Integration with Development Workflow

### Local Development Loop

```bash
# 1. Write code
vim agents/new_feature.py

# 2. Run quick checks
ruff check agents/new_feature.py
black agents/new_feature.py

# 3. Run tests
pytest tests/test_new_feature.py -v

# 4. Full quality check before commit
nox

# 5. Commit (pre-commit hooks run automatically)
git add agents/new_feature.py tests/test_new_feature.py
git commit -m "feat: add new feature"
```

### CI/CD Pipeline Integration

```
┌─────────────┐
│ Push/PR     │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Lint (Ruff) │ ← Fast feedback (seconds)
└──────┬──────┘
       │
       v
┌─────────────┐
│ Format      │ ← Code style check
│ (Black)     │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Type Check  │ ← Static analysis
│ (mypy)      │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Tests       │ ← Unit + integration
│ (pytest)    │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Security    │ ← Vulnerability scan
│ (bandit)    │
└──────┬──────┘
       │
       v
    Success!
```

## Tool Comparison

| Feature | Ruff | Black | mypy | pytest |
|---------|------|-------|------|--------|
| Speed | ⚡⚡⚡ (100x faster) | ⚡⚡ | ⚡ | ⚡⚡ |
| Auto-fix | ✅ | ✅ | ❌ | N/A |
| Customizable | ✅ High | ⚠️ Limited | ✅ High | ✅ High |
| Error Messages | ✅ Clear | N/A | ⚠️ Can be cryptic | ✅ Clear |

## Troubleshooting

### Common Issues

1. **Ruff conflicts with Black**
   - Solution: Ruff's `E501` (line too long) is ignored by default
   - Let Black handle formatting, Ruff handles linting logic

2. **mypy type errors in third-party libraries**
   ```python
   # Add type stubs
   pip install types-requests types-pyyaml
   
   # Or ignore module
   # mypy.ini or pyproject.toml
   [[tool.mypy.overrides]]
   module = "untyped_library.*"
   ignore_missing_imports = true
   ```

3. **Pre-commit hooks too slow**
   ```bash
   # Skip hooks temporarily
   git commit --no-verify -m "WIP: skip hooks"
   
   # Or run specific hooks
   pre-commit run ruff --all-files
   ```

4. **Coverage not reflecting changes**
   ```bash
   # Clear cache and re-run
   rm -rf .coverage htmlcov/
   pytest --cov=agents --cov-report=html
   ```

## Future Enhancements

1. **Automated Dependency Updates**: Dependabot or Renovate for dependency management
2. **Complexity Metrics**: Track cyclomatic complexity and enforce limits
3. **Documentation Linting**: Vale or doc8 for documentation quality
4. **Performance Profiling**: py-spy or scalene for performance monitoring
5. **License Compliance**: Check open-source license compatibility

## Related Capabilities

- **CI/CD Pipeline**: Integration with GitHub Actions (see [ci_cd_pipeline.md](ci_cd_pipeline.md))
- **Safeguards Detection**: Security analysis patterns (see [safeguards_detection.md](safeguards_detection.md))
- **Documentation System**: Documentation quality tools (see [documentation_system.md](documentation_system.md))

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
- [nox Documentation](https://nox.thea.codes/)
- [Code Quality Workflow](../../.github/workflows/code-quality.yml)
- [Project Configuration](../../pyproject.toml)

---

**Last Updated**: 2025-12-27  
**Maintainer**: Code Quality Team
