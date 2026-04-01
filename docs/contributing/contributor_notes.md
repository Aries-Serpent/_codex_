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
```text

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
```text

### Code Quality

```bash
# Run linting
nox -s lint

# Run type checking
nox -s typecheck

# Run all quality gates
nox -s gates
```text

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
```text

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

---

## Import Conventions

### Relative Imports Within `src/` Packages

**Rule**: Any module inside `src/X/` **must** use relative imports (`from .module import name`)
when importing from sibling modules in the same package. Never route intra-package imports
through root-level shim files.

**Why**: Root-level shims (e.g. `training/engine_hf_trainer.py`) often re-export via
`from src.training.engine_hf_trainer import *` (star import). Mypy **cannot resolve
specific attributes across a star-import boundary**, producing `[attr-defined]` errors
and `[unused-ignore]` cascades.

**Example (correct)**:
```python
# Inside src/training/functional_training.py
from .engine_hf_trainer import get_hf_revision  # ✅ relative — mypy resolves directly
```

**Example (incorrect)**:
```python
# Inside src/training/functional_training.py
from training.engine_hf_trainer import get_hf_revision  # ❌ routes through root shim
```

**Enforcement**: CI runs `scripts/ci/mypy_baseline.py --require-baseline`; routing through
a shim will produce `[attr-defined]` errors that exceed the baseline threshold, blocking
the PR. The shim/star-import pattern is tracked in the cognitive brain as pattern
`mypy_shim_star_import_attr_not_found` (added S216, PR #3843).

### `type: ignore` Hygiene

**Rule**: Do **not** add `# type: ignore` to bare import statements of packages that ship
bundled type stubs (numpy ≥ 1.20, torch ≥ 1.8, transformers, etc.) or that are already
handled by `ignore_missing_imports = True` in `mypy.ini`. Such comments become
`[unused-ignore]` errors in CI's isolated-venv mypy run.

**Acceptable patterns**:
- `# type: ignore[assignment]` on `x = None` where `x` previously held a typed package
  (needed when the package IS installed)
- `# type: ignore[override]` / `# type: ignore[misc]` on class/method definitions that
  structurally override a method from a missing base class

**Unacceptable**:
```python
import numpy as np  # type: ignore        ❌ numpy has bundled stubs
import torch  # type: ignore               ❌ torch has bundled stubs
from peft import LoraConfig  # type: ignore  ❌ --ignore-missing-imports covers this
```
