# Contributor Notes

## Quick Start

Welcome to the _codex_ project! This guide helps you get started with contributing.

### Prerequisites

- Python 3.10 or higher (3.12 recommended)
- Git
- Basic familiarity with pytest, nox, and pre-commit

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
nox -s tests

# Run smoke tests only
pytest -m smoke

# Run tests excluding slow tests
pytest -m "not slow"

# Run specific test file
pytest tests/config/test_config_schema.py -v
```

### Code Quality

```bash
# Run linting
nox -s lint

# Run type checking
nox -s typecheck

# Run all quality gates
nox -s gates
```

### Common Tasks

#### Adding a New Test

1. Create test file in appropriate `tests/` subdirectory
2. Use appropriate markers (see `pytest.ini`)
3. Follow existing test naming conventions
4. Run tests to verify: `pytest path/to/test_file.py`

#### Updating Documentation

1. Edit markdown files in `docs/`
2. Run fence fixer: `python tools/fence_fixer.py docs/ --dry-run`
3. Fix any fence issues before committing

#### Working with Configuration

The project uses Hydra for configuration management:
- Config files in `configs/`
- Schema validation via OmegaConf
- See `src/codex_ml/training/unified_training.py` for examples

### Important Notes

**Torch Import**: The repository excludes local `torch/` stubs. Always ensure torch imports from site-packages:

```python
import torch
print(torch.__file__)  # Should show site-packages path
```

**Pytest Markers**: Always use registered markers from `pytest.ini`:
- `smoke` - Quick smoke tests
- `slow` - Long-running tests
- `requires_torch` - Tests needing PyTorch
- `cpu_only` - CPU-only tests
- `distributed` - Distributed/accelerate tests
- `lora` - LoRA-specific tests
- `perf_smoke` - Performance tests

**Code Style**:
- Line length: 100 characters
- Format with Black
- Lint with Ruff
- Sort imports with isort

### Getting Help

- Check existing documentation in `docs/`
- Review tests for examples
- See `NEWCOMER_GUIDE.md` for detailed onboarding
- Open an issue for questions

### Pull Request Checklist

Before submitting a PR:

- [ ] Tests pass locally (`nox -s tests`)
- [ ] Code is formatted (`black .` and `isort .`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy src`)
- [ ] Documentation updated if needed
- [ ] No new syntax warnings (`python -W error::SyntaxWarning -m py_compile`)
- [ ] Commit messages are clear and descriptive

### Resources

- Main README: `README.md`
- Newcomer Guide: `NEWCOMER_GUIDE.md`
- Test Taxonomy: `docs/testing/test_taxonomy.md`
- Modernization Guide: `docs/development/modernization_guide.md`
