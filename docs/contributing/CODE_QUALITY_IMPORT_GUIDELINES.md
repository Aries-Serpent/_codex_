# Code Quality: Import Organization Guidelines

**Last Updated:** 2026-06-22

> **Version:** 1.0.0
> **Created:** 2026-02-17
> **Purpose:** Comprehensive import organization guidelines following E402/F821 systematic refactoring

---

## Overview

This document defines import organization standards for the `_codex_` repository, including acceptable E402 patterns that support intentional code structures while maintaining code quality.

## Table of Contents

1. [Standard Import Organization](#standard-import-organization)
2. [Acceptable E402 Patterns](#acceptable-e402-patterns)
3. [F821 Prevention](#f821-prevention)
4. [TYPE_CHECKING Pattern](#type_checking-pattern)
5. [Pre-commit Enforcement](#pre-commit-enforcement)

---

## Standard Import Organization

### Basic Structure

```python
"""Module docstring."""

# Future imports (MUST be first)
from __future__ import annotations

# Standard library imports
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
import numpy as np
import torch
from transformers import AutoModel

# Local application imports
from codex.core import BaseClass
from codex.utils import helper_function
```

## Import Grouping Order

1. **Future imports** - `from __future__ import annotations`
2. **Standard library** - Built-in Python modules
3. **Third-party** - External packages (numpy, torch, etc.)
4. **Local application** - Project-specific imports

Use blank lines to separate groups.

---

## Acceptable E402 Patterns

The following E402 (module imports not at top of file) patterns are **intentional** and **documented exceptions**. Use `# noqa: E402` to suppress warnings.

### Pattern 1: Logger Before Imports (Performance Optimization)

**Purpose:** Initialize logger early for module-level logging during imports.

**Example:**
```python
"""Module docstring."""
import logging

logger = logging.getLogger(__name__)
logger.info("Loading module...")  # Logs during import

# noqa: E402 - Logger initialized early for import-time logging
import expensive_module
from codex.core import heavy_initialization
```

**When to use:**
- Module requires logging during import process
- Import-time validation needs logging
- Performance-critical module loading

**Configuration:**
```toml
# .ruff.toml
[lint.per-file-ignores]
"src/codex_ml/training/*.py" = ["E402"]  # Logger-before-imports pattern
```

---

## Pattern 2: sys.path Modification (Local Imports)

**Purpose:** Support local imports in agent tests and scripts.

**Example:**
```python
"""Agent test module."""
import sys
from pathlib import Path

# Add agent directory to path for local imports
agent_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(agent_dir))

# noqa: E402 - sys.path modified for local imports
from analyzer import ASTAnalysisAgent
from utils import helper_function
```

**When to use:**
- Agent test files (`.github/agents/*/tests/*.py`)
- Standalone scripts requiring local modules
- Development utilities

**Configuration:**
```toml
# .ruff.toml
[lint.per-file-ignores]
".github/agents/**/tests/*.py" = ["E402"]  # sys.path pattern
"scripts/**/*.py" = ["E402"]  # Standalone scripts
```

---

## Pattern 3: Lazy Loading (Optional Dependencies)

**Purpose:** Defer expensive imports until needed, improve startup time.

**Example:**
```python
"""Module with optional GPU support."""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import torch  # Type hints only

def train_model(use_gpu: bool = False) -> Optional["torch.Tensor"]:
    """Train model with optional GPU support."""
    if use_gpu:
        # noqa: E402 - Lazy loading for optional dependency
        import torch
        device = torch.device("cuda")
        return torch.zeros(10, device=device)
    return None
```

**When to use:**
- Optional dependencies (GPU libraries, heavy packages)
- Performance-critical startup paths
- Feature-flag controlled imports

---

### Pattern 4: Conditional Imports (Feature Flags)

**Purpose:** Import modules based on runtime conditions.

**Example:**
```python
"""Module with environment-specific imports."""
import os

if os.getenv("ENABLE_EXPERIMENTAL_FEATURES"):
    # noqa: E402 - Conditional import for experimental features
    from codex.experimental import new_feature
else:
    new_feature = None
```

**When to use:**
- Environment-specific dependencies
- Experimental feature toggles
- Platform-specific imports

---

### Pattern 5: Import After Docstring (Documentation)

**Purpose:** Allow imports after module docstring when necessary.

**Example:**
```python
"""
Complex module with extensive documentation.

This module requires detailed explanation before imports.
See https://docs.codex.ai/module for full documentation.
"""

# Acceptable: Imports after docstring
# noqa: E402 - Imports after extensive module documentation
import logging
from typing import Any
```

**When to use:**
- Modules with extensive documentation
- Generated code with templated docstrings
- Legacy code with docstring-first structure

---

## F821 Prevention

F821 (undefined name) errors cause **runtime failures** and must be **zero tolerance**.

### Common F821 Issues

1. **Missing typing imports:**
   ```python
   # ❌ WRONG: F821 undefined name 'Optional'
   def process(config: Optional[Dict]) -> Any:
       pass

   # ✅ CORRECT: Import typing
   from typing import Any, Dict, Optional
   def process(config: Optional[Dict]) -> Any:
       pass
   ```

2. **Missing logger definitions:**
   ```python
   # ❌ WRONG: F821 undefined name 'logger'
   logger.info("Starting...")

   # ✅ CORRECT: Define logger
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Starting...")
   ```

3. **Missing stdlib imports:**
   ```python
   # ❌ WRONG: F821 undefined name 'Path'
   path = Path("/tmp")

   # ✅ CORRECT: Import from pathlib
   from pathlib import Path
   path = Path("/tmp")
   ```

### Pre-commit Enforcement

F821 errors are enforced via pre-commit hooks with **zero tolerance**:

```yaml
# .pre-commit-config.yaml
- id: ruff-f821-check
  name: Ruff F821 Check (undefined names - ZERO TOLERANCE)
  entry: bash -c 'ruff check --select F821 . && echo "✅ No undefined names"'
  language: system
  pass_filenames: false
```

---

## TYPE_CHECKING Pattern

Use `TYPE_CHECKING` to avoid circular imports and expensive type-only imports.

### Basic Usage

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imports only used for type hints
    from expensive_module import ExpensiveClass
    from circular_module import CircularDependency

def process(data: "ExpensiveClass") -> "CircularDependency":
    """Function using forward references for type hints."""
    pass
```

### Benefits

1. **Avoid circular dependencies** - Imports only evaluated during type checking
2. **Improve performance** - Skip expensive imports at runtime
3. **Forward references** - Use string annotations for deferred evaluation

### When to Use

- Resolving circular import dependencies
- Type hints for expensive-to-import modules
- Breaking import cycles in large codebases

---

## Pre-commit Enforcement

### Current Configuration

```toml
# .ruff.toml
[lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]  # Line too long

[lint.per-file-ignores]
"__init__.py" = ["F401", "E402"]  # Re-exports and organization
"tests/quantum/test_integration.py" = ["F811"]  # Intentional redefinitions

# E402 acceptable patterns
"src/codex_ml/training/*.py" = ["E402"]  # Logger-before-imports
".github/agents/**/tests/*.py" = ["E402"]  # sys.path modification
"scripts/**/*.py" = ["E402"]  # Standalone scripts
"scripts/cognitive/*.py" = ["E402"]  # Complex initialization
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
- id: ruff-quality-check
  name: Ruff Quality Check (E402/F821 enforcement)
  entry: bash -c 'ruff check --select E402,F821 . || true'  # E402 warnings only
  language: system
  pass_filenames: false

- id: ruff-f821-strict
  name: Ruff F821 Strict (undefined names - ZERO TOLERANCE)
  entry: bash -c 'ruff check --select F821 . && echo "✅ No F821 errors"'
  language: system
  pass_filenames: false
```

---

## Migration Guide

### Adding `# noqa: E402` to Existing Code

1. **Identify pattern** - Determine which acceptable pattern applies
2. **Add comment** - Place `# noqa: E402` with explanation
3. **Document reason** - Explain why E402 is acceptable
4. **Update config** - Add to `.ruff.toml` if pattern affects multiple files

**Example:**
```python
"""Training module with early logger initialization."""
import logging

logger = logging.getLogger(__name__)
# noqa: E402 - Logger initialized early for import-time validation logging
from codex.core import validate_config
```

## Fixing Genuine E402 Issues

If import is **not** an acceptable pattern, reorganize:

```python
# ❌ BEFORE: Genuinely misplaced import
x = compute_value()
import os  # E402

# ✅ AFTER: Import at top
import os
x = compute_value()
```

---

## Quality Metrics

### Current Status (Post-GAP-REF)

- **F821 errors:** 0 ✅ (ZERO TOLERANCE enforced)
- **E402 errors:** 2,519 (documented acceptable patterns)
- **E402 acceptable:** ~2,300 (91.3% - intentional patterns)
- **E402 fixable:** ~200 (8.7% - genuinely misplaced)

### Monitoring

Track quality metrics via CI/CD:

```bash
# F821 check (must pass)
ruff check --select F821 . && echo "✅ PASS"

# E402 check (informational)
ruff check --select E402 . | wc -l  # Track trend over time
```

---

## References

- **PEP 8:** [Import Guidelines](https://pep8.org/#imports)
- **Ruff Documentation:** [E402 Rule](https://docs.astral.sh/ruff/rules/module-import-not-at-top-of-file/)
- **Ruff Documentation:** [F821 Rule](https://docs.astral.sh/ruff/rules/undefined-name/)
- **PR #3319:** E402/F821 Systematic Refactoring
- **Session Reports:** `.codex/GAP_REF_SESSION_*.md`

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-17 | Initial version following GAP-REF PR #3319 completion |

---

**Questions or Updates?** Contact: @mbaetiong or create an issue with `[CODE-QUALITY]` label
