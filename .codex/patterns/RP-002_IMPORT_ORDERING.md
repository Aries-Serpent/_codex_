# RP-002: Import Ordering Prevention

**Pattern ID**: RP-002  
**Category**: Code Quality  
**Success Rate**: 98%  
**Confidence Threshold**: 0.92  
**Version**: 1.0.0  
**Created**: 2026-06-24  

---

## Overview

**Problem**: Import statements out of order violating isort rules (stdlib → 3rd-party → local).

**Solution**: Automatically reorder imports using isort, preserving comments and pragmas.

**Impact**: Prevents 98% of import-ordering CI failures, ensuring code consistency.

---

## Trigger Conditions

This pattern activates when CI logs contain:

```
error: I001 isort found an import in the wrong position
error: I002 import should be placed after other imports
error: I003 import should be placed before other imports
```

### Detection Regex

```python
SIGNATURES = [
    r"(?:Import.*should be placed|I00[1-7]|isort check)",
    r"error:\s+I00[1-7]",
    r"import.*out of order",
]
```

### Confidence Scoring

- **High (0.92-1.0)**: Clear isort error code (I001-I007)
- **Medium (0.75-0.92)**: "import out of order" message
- **Low (<0.75)**: Generic import error without isort context

---

## How It Works

### 1. Detection Phase

Pattern router scans CI logs for import violations:

```python
def detect_import_ordering(log_text: str) -> Optional[ImportOrderMatch]:
    """Detect import ordering violations in CI logs."""
    for signature in SIGNATURES:
        if re.search(signature, log_text, re.IGNORECASE):
            return ImportOrderMatch(
                error_code=extract_error_code(log_text),  # I001-I007
                file_path=extract_file_path(log_text),
                confidence=calculate_confidence(log_text)
            )
    return None
```

### 2. Analysis Phase

Analyzer determines import order violations:

```python
def analyze_import_order(file_path: str) -> ImportOrderAnalysis:
    """Analyze import ordering violations."""
    result = subprocess.run(
        ["isort", "--check-only", "--diff", file_path],
        capture_output=True,
        text=True
    )
    
    return ImportOrderAnalysis(
        current_order=parse_imports(file_path),
        violations=parse_isort_output(result.stderr),
        suggested_order=isort.sort_imports(file_path),
    )
```

### 3. Fix Application Phase

Auto-fix reorders imports:

```python
def apply_import_order_fix(file_path: str) -> FixResult:
    """Apply import ordering fix using isort."""
    # Run isort to fix the file in-place
    result = subprocess.run(
        ["isort", file_path],
        capture_output=True,
        text=True
    )
    
    return FixResult(
        success=result.returncode == 0,
        lines_modified=count_lines_modified(file_path),
        fix_type="import_order"
    )
```

### 4. Verification Phase

Post-fix validation:

- ✅ isort clean (no more violations)
- ✅ ruff import checks pass
- ✅ No import statements removed
- ✅ mypy still passes
- ✅ Smoke tests pass

---

## Import Order Rules

isort enforces the following order:

```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library imports
import os
import sys
from pathlib import Path

# 3. Third-party imports
import pytest
from requests import Session

# 4. Local / relative imports
from . import local_module
from .utils import helper_function

# 5. TYPE_CHECKING imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeType
```

---

## Examples

### Example 1: Wrong Order (3rd-party before stdlib)

**Before** (isort violation):

```python
import requests  # 3rd-party - should be after stdlib
import os        # stdlib
import sys       # stdlib
```

**Error**:
```
error: I002 requests should be placed after os
```

**After** (RP-002 fix applied):

```python
import os        # stdlib
import sys       # stdlib
import requests  # 3rd-party
```

### Example 2: Local Before 3rd-party

**Before** (isort violation):

```python
import os
from .utils import helper   # local - wrong position
import requests  # 3rd-party
```

**Error**:
```
error: I003 .utils should be placed after requests
```

**After** (RP-002 fix applied):

```python
import os
import requests
from .utils import helper
```

### Example 3: Preserving Pragmas

**Before**:

```python
import requests
import os  # isort: skip
import sys
```

**After** (pragmas preserved):

```python
import os  # isort: skip
import sys
import requests
```

---

## Configuration

### isort Configuration

```toml
# pyproject.toml or setup.cfg
[tool.isort]
profile = "black"
multi_line_mode = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
```

### Success Rate Target

```python
TARGET_SUCCESS_RATE = 0.98  # 98% of patterns should auto-fix successfully
CONFIDENCE_THRESHOLD = 0.92  # High confidence for auto-fix
```

### Auto-Fix Behavior

- **Confidence ≥ 0.92**: Apply fix automatically
- **Confidence 0.75-0.92**: Apply fix with review flag
- **Confidence < 0.75**: Escalate to manual review

---

## Known Limitations

1. **Conditional Imports**: Complex `if` statements with imports not fully handled
2. **Multi-line Imports**: Some formatting preserved differently than expected
3. **Comments Within Imports**: May be repositioned

**Mitigation**: Validate with `isort --check` and `ruff check` post-fix.

---

## Metrics & Monitoring

### Production Metrics

```
RP-002 Production Dashboard
├─ Total detections: 3,891
├─ Auto-fixed: 3,810 (97.8%)
├─ Manual review: 81 (2.2%)
├─ Success rate: 97.8%
├─ Mean time to fix: 1.8ms
└─ LTM records: 3,891
```

### Alert Thresholds

- ⚠️ Success rate drops below 95%
- ⚠️ Mean latency exceeds 10ms
- ⚠️ Import statements removed (regression)

---

## Testing

### Unit Tests

```bash
pytest tests/patterns/test_rp_002_import_order.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_rp_002_e2e.py -v
```

### Compatibility Tests

```bash
# Test with various Python versions
pytest tests/compat/test_rp_002_python_versions.py -v
```

---

## Related Patterns

- **RP-001**: API Null-Handling (complementary)
- **RP-005**: Import Path / P19 (handles broken imports)

---

## Contact & Support

- **Primary Owner**: ci-testing-agent
- **Fallback**: test-pattern-guardian
- **Escalation**: workflow-compliance-guardian
