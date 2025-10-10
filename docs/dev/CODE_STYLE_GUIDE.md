# Code Style Guide

## Philosophy
- Clarity over cleverness
- Explicit over implicit
- Testable over terse

## Python Standards
- **Formatting**: Black (line-length=100)
- **Linting**: Ruff (pycodestyle, pyflakes, pep8-naming, bugbear, simplify)
- **Type Checking**: mypy strict mode
- **Import Sorting**: isort (compatible with Black)
- **Docstrings**: Google style

## Naming Conventions
| Element | Pattern | Example |
|---------|---------|---------|
| Modules | snake_case | `model_loader.py` |
| Classes | PascalCase | `TokenizerWrapper` |
| Functions | snake_case | `train_model()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _leading_underscore | `_internal_helper()` |

## Type Annotations
```python
def process_batch(
    data: list[dict[str, str]],
    batch_size: int = 32,
    *,
    shuffle: bool = False,
) -> list[list[dict[str, str]]]:
    """Process data in batches."""
    ...
```

## Pre-Commit Checks
All code must pass:
1. Black formatting
2. Ruff linting
3. mypy strict mode
4. isort import sorting
5. Semgrep security rules
6. Secret detection
7. pytest smoke tests

## Code Review Checklist
- [ ] Type hints on all public functions
- [ ] Docstrings for modules, classes, and functions
- [ ] Tests cover new functionality
- [ ] No `print()` statements (use structured logging)
- [ ] No hard-coded secrets or tokens
- [ ] Specific exceptions instead of bare `except`
