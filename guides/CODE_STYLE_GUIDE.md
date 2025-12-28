# Code Style Guide

Coding standards and style guidelines for the CODEX project.

## Overview

This guide defines the coding conventions, formatting standards, and best practices for contributing to CODEX.

## Python Style

### PEP 8 Compliance

Follow [PEP 8](https://peps.python.org/pep-0008/) with these exceptions:
- Line length: 100 characters (instead of 79)
- Allow multiple imports on one line for related items

### Formatting Tools

**Required tools:**
- **Black** - Code formatter (line-length=100)
- **Ruff** - Fast linter and code checker
- **isort** - Import sorting

**Run before committing:**
```bash
black --line-length 100 .
ruff check --fix .
isort .
```

### Type Hints

Use type hints for all function signatures:

```python
def process_data(input_file: str, max_size: int = 1000) -> Dict[str, Any]:
    """Process data from input file."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description with more details about what the function does,
    including any important notes or warnings.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    pass
```

## File Organization

### Module Structure

```
package/
├── __init__.py
├── core.py
├── utils.py
└── tests/
    ├── __init__.py
    └── test_core.py
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
from typing import Dict, List

import numpy as np
import torch

from codex.core import BaseClass
from codex.utils import helper_function
```

## Testing Standards

### Test Structure

```python
import pytest
from codex.module import function_to_test


class TestFunctionName:
    """Test suite for function_to_test."""

    def test_normal_case(self):
        """Test normal operation."""
        result = function_to_test("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            function_to_test("")
```

### Test Coverage

- Minimum coverage: 80%
- Critical paths: 100%
- Run coverage: `pytest --cov=codex --cov-report=html`

## Documentation

### README Files

Every module should have a README.md with:
- Purpose and overview
- Installation instructions
- Usage examples
- API reference links

### Code Comments

- Explain **why**, not **what**
- Keep comments up-to-date with code
- Remove commented-out code before committing

## Git Workflow

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting changes
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance tasks

**Example:**
```
feat(cli): Add session log query command

Implement new CLI command to query conversation transcripts
using SQLite FTS5 full-text search.

Closes #123
```

### Branch Naming

- `feature/description`
- `fix/issue-description`
- `docs/topic`
- `refactor/component`

## Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Hooks automatically run:
- Black formatting
- Ruff linting
- isort import sorting
- Type checking with mypy
- YAML validation

## Code Review Guidelines

### For Authors

- Keep PRs small and focused
- Write clear descriptions
- Add tests for new features
- Update documentation
- Run all checks locally first

### For Reviewers

- Be constructive and specific
- Focus on logic and maintainability
- Suggest improvements, don't demand
- Approve when ready, request changes if needed

## Performance Guidelines

### Optimization

- Profile before optimizing
- Use appropriate data structures
- Cache expensive computations
- Avoid premature optimization

### Memory Management

- Use generators for large datasets
- Close file handles explicitly
- Clean up resources in `finally` blocks
- Use context managers (`with` statements)

## Security

### Best Practices

- Never commit secrets or credentials
- Validate and sanitize user input
- Use parameterized queries for databases
- Keep dependencies updated
- Follow OWASP guidelines

### Sensitive Data

- Use environment variables for secrets
- Encrypt sensitive data at rest
- Use secure communication protocols
- Implement proper access controls

## Resources

- [PEP 8](https://peps.python.org/pep-0008/) - Python Style Guide
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [pytest Documentation](https://docs.pytest.org/)

## Questions?

For style questions not covered here, refer to existing codebase patterns or ask in:
- GitHub Discussions
- Pull Request comments
- Team chat channels
