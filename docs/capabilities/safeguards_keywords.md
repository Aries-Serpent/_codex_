# Safeguards Keywords Detection

## Overview

The safeguards keywords capability detects defensive programming patterns, validation checks, and security safeguards in the codebase through keyword analysis, providing metrics for code safety and robustness assessment.

**Keywords**: safeguard, validation, security, defensive, robust, sanitize, bounds-check, rate-limit, timeout, error-handling, safety

## Purpose

Provides safeguard detection through:
- **Keyword Detection**: Identify safeguard keywords in code and comments
- **Pattern Recognition**: Detect defensive programming patterns
- **Density Metrics**: Calculate safeguard density per file/module
- **Coverage Analysis**: Track which modules have safeguards
- **Security Scoring**: Rate code security posture

## Architecture

### Detection Layers

```
┌─────────────────────────────────────┐
│   Source Code                       │
│   (Python, YAML, Markdown files)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Keyword Scanner                   │
│   (Regex patterns, AST analysis)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Context Analyzer                  │
│   (Filter false positives)          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Metrics Calculator                │
│   (Density, coverage, scoring)      │
└─────────────────────────────────────┘
```

## Keyword Categories

### Core Safeguard Keywords

| Category | Keywords | Description |
|----------|----------|-------------|
| **Validation** | validate, verify, check, assert, ensure | Input/output validation |
| **Sanitization** | sanitize, escape, clean, filter, normalize | Data cleaning |
| **Bounds** | bounds, limit, max, min, threshold, range | Range checking |
| **Error Handling** | try, except, catch, handle, recover, fallback | Error management |
| **Security** | secure, protect, guard, defense, safe | Security measures |
| **Rate Limiting** | rate, limit, throttle, quota, backoff | Request limiting |
| **Timeout** | timeout, deadline, expire, ttl | Time limits |

### Extended Keywords

```python
SAFEGUARD_KEYWORDS = {
    # Validation keywords
    "validation": [
        "validate", "verify", "check", "assert", "ensure",
        "is_valid", "validate_input", "validate_output"
    ],
    
    # Sanitization keywords
    "sanitization": [
        "sanitize", "escape", "clean", "filter", "normalize",
        "html_escape", "sql_escape", "strip", "purify"
    ],
    
    # Bounds checking
    "bounds": [
        "bounds", "limit", "max", "min", "threshold", "range",
        "clamp", "constrain", "bounded", "overflow"
    ],
    
    # Error handling
    "error_handling": [
        "try", "except", "catch", "handle", "recover",
        "fallback", "retry", "graceful", "safe_"
    ],
    
    # Security
    "security": [
        "secure", "protect", "guard", "defense", "safe",
        "auth", "encrypt", "hash", "token"
    ],
    
    # Rate limiting
    "rate_limiting": [
        "rate", "limit", "throttle", "quota", "backoff",
        "rate_limit", "request_limit", "cooldown"
    ],
    
    # Timeouts
    "timeout": [
        "timeout", "deadline", "expire", "ttl", "max_time",
        "time_limit", "duration", "wait"
    ],
    
    # Defensive patterns
    "defensive": [
        "defensive", "robust", "resilient", "fault_tolerant",
        "fail_safe", "circuit_breaker", "bulkhead"
    ]
}
```

## Configuration

### Detector Configuration

```yaml
# safeguards_config.yaml
safeguards:
  enabled: true
  
  # Minimum keyword count for passing
  min_keywords: 3
  
  # Keyword categories to check
  categories:
    - validation
    - sanitization
    - bounds
    - error_handling
    - security
  
  # Files to include
  include_patterns:
    - "*.py"
    - "*.yaml"
    - "*.yml"
  
  # Files to exclude
  exclude_patterns:
    - "test_*.py"
    - "*_test.py"
    - "conftest.py"
  
  # Context filtering
  context:
    require_comment: false
    require_function: true
    max_distance: 5  # lines from code
```

## Usage Examples

### Example 1: Basic Safeguard Detection

```python
# scripts/detect_safeguards.py
"""
Detect safeguard keywords in codebase.

Safeguard: Validates file paths before reading.
Bounded: Limits file read size to prevent memory issues.
"""
import re
from pathlib import Path
from typing import Dict, List

SAFEGUARD_PATTERNS = [
    r'\bvalidate\b',
    r'\bsanitize\b', 
    r'\bbounds\b',
    r'\btimeout\b',
    r'\brate.?limit\b',
    r'\bsafeguard\b',
]

def detect_safeguards(file_path: Path, max_bytes: int = 100000) -> List[str]:
    """
    Detect safeguard keywords in a file.
    
    Safeguard: Bounded read to prevent memory issues.
    Validation: Checks file exists before reading.
    """
    if not file_path.exists():
        return []
    
    try:
        content = file_path.read_text()[:max_bytes]
    except UnicodeDecodeError:
        return []
    
    found = []
    for pattern in SAFEGUARD_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        found.extend(matches)
    
    return found

# Example usage
if __name__ == "__main__":
    src_dir = Path("src")
    for py_file in src_dir.glob("**/*.py"):
        safeguards = detect_safeguards(py_file)
        if safeguards:
            print(f"{py_file}: {len(safeguards)} safeguards found")
```

### Example 2: Safeguard Density Calculation

```python
def calculate_safeguard_density(file_path: Path) -> float:
    """
    Calculate safeguard density (keywords per 100 lines).
    
    Safeguard: Validates input path.
    Bounds: Returns 0.0 for empty files.
    """
    if not file_path.exists():
        return 0.0
    
    content = file_path.read_text()
    lines = content.split('\n')
    
    if len(lines) == 0:
        return 0.0
    
    safeguards = detect_safeguards(file_path)
    density = (len(safeguards) / len(lines)) * 100
    
    return round(density, 2)

# Example: Calculate density for all Python files
densities = {}
for py_file in Path("src").glob("**/*.py"):
    densities[str(py_file)] = calculate_safeguard_density(py_file)

# Files with low density need improvement
low_density = {k: v for k, v in densities.items() if v < 1.0}
print(f"Files needing safeguard improvements: {len(low_density)}")
```

### Example 3: Context-Aware Detection

```python
import ast
from typing import Tuple, List

def detect_safeguards_with_context(file_path: Path) -> List[Tuple[str, str, int]]:
    """
    Detect safeguards with their context (function name, line number).
    
    Safeguard: Uses AST for accurate parsing.
    Validation: Handles syntax errors gracefully.
    """
    try:
        content = file_path.read_text()[:100000]  # Bounded
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []
    
    results = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check docstring for safeguard keywords
            docstring = ast.get_docstring(node) or ""
            for keyword in SAFEGUARD_KEYWORDS["validation"]:
                if keyword in docstring.lower():
                    results.append((keyword, node.name, node.lineno))
    
    return results
```

### Example 4: Integration with Audit System

```python
# scripts/space_traversal/detectors/detector_safeguards.py
"""
Safeguards keyword detector for audit system.

Detects defensive programming patterns and security keywords.
"""

def detect(file_index: dict) -> dict:
    """
    Detect safeguard keywords across the codebase.
    
    Safeguard: Bounded reads on all files.
    Validation: Input validation on file_index.
    """
    files = file_index.get("files", [])
    evidence = []
    found_keywords = set()
    keyword_counts = {}
    
    required_keywords = [
        "validate", "sanitize", "bounds", "timeout",
        "safeguard", "error", "check", "limit"
    ]
    
    for meta in files:
        path = meta.get("path", "")
        if not path.endswith(".py"):
            continue
        
        # Read with bounds
        try:
            content = Path(path).read_text()[:100000]
        except (OSError, UnicodeDecodeError):
            continue
        
        # Scan for keywords
        file_keywords = []
        for keyword in required_keywords:
            if keyword in content.lower():
                file_keywords.append(keyword)
                found_keywords.add(keyword)
        
        if file_keywords:
            evidence.append(path)
            for kw in file_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
    
    return {
        "id": "safeguards-keywords",
        "evidence_files": sorted(evidence),
        "found_patterns": sorted(found_keywords),
        "required_patterns": required_keywords,
        "keyword_counts": keyword_counts,
        "docs_keywords": [
            "safeguard", "validation", "security", "defensive",
            "sanitize", "bounds", "timeout", "error-handling"
        ],
        "meta": {
            "category": "security",
            "safeguards": ["bounded", "validation", "offline"],
            "detector_version": "2.0"
        }
    }
```

### Example 5: Adding Safeguards to Code

```python
# Before: No safeguards
def process_data(data):
    result = data * 2
    return result

# After: With safeguards
def process_data(data: float, max_value: float = 1e6) -> float:
    """
    Process data with safety bounds.
    
    Safeguard: Validates input range.
    Bounds: Limits output to max_value.
    Timeout: Uses default timeout for long operations.
    
    Args:
        data: Input value to process.
        max_value: Maximum allowed output value.
    
    Returns:
        Processed value, clamped to max_value.
    
    Raises:
        ValueError: If data is not a number.
    """
    # Validation safeguard
    if not isinstance(data, (int, float)):
        raise ValueError(f"Expected number, got {type(data)}")
    
    # Bounds check safeguard
    if data < 0:
        data = 0  # Clamp to minimum
    
    result = data * 2
    
    # Upper bounds safeguard
    if result > max_value:
        result = max_value
    
    return result
```

## Safeguard Patterns Reference

### Validation Pattern

```python
def validate_input(value: str, pattern: str) -> bool:
    """
    Validate input against pattern.
    
    Safeguard: Prevents invalid data from processing.
    """
    import re
    if not isinstance(value, str):
        raise TypeError("Value must be string")
    return bool(re.match(pattern, value))
```

### Sanitization Pattern

```python
def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS.
    
    Safeguard: Escapes dangerous characters.
    Security: Prevents cross-site scripting.
    """
    import html
    return html.escape(text)
```

### Bounds Check Pattern

```python
def bounded_read(file_path: Path, max_bytes: int = 100000) -> str:
    """
    Read file with size limit.
    
    Safeguard: Prevents memory exhaustion.
    Bounds: Limits read to max_bytes.
    """
    if not file_path.exists():
        return ""
    
    size = file_path.stat().st_size
    if size > max_bytes:
        return file_path.read_text()[:max_bytes]
    return file_path.read_text()
```

### Timeout Pattern

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """
    Context manager for operation timeout.
    
    Safeguard: Prevents hanging operations.
    Timeout: Raises after seconds.
    """
    def handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds}s")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
```

### Rate Limiting Pattern

```python
from time import time
from collections import defaultdict

class RateLimiter:
    """
    Rate limiter for API endpoints.
    
    Safeguard: Prevents abuse.
    Rate-limit: Enforces request limits.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = time()
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True
```

## Best Practices

1. **Document Safeguards**: Include "Safeguard:" in docstrings
2. **Use Type Hints**: Validate types at runtime when needed
3. **Bounds Check All Inputs**: Especially file reads and user input
4. **Set Timeouts**: All network and I/O operations
5. **Rate Limit APIs**: Prevent abuse and overload
6. **Log Security Events**: Track validation failures
7. **Fail Safely**: Default to secure behavior on errors
8. **Defense in Depth**: Multiple layers of safeguards

## Troubleshooting

### Low Safeguard Score

```bash
# Find files missing safeguards
python -c "
from pathlib import Path
for f in Path('src').glob('**/*.py'):
    content = f.read_text()
    if 'safeguard' not in content.lower() and 'validate' not in content.lower():
        print(f'Missing safeguards: {f}')
"
```

### False Positives

```python
# Filter out test files and comments
EXCLUDE_PATTERNS = [
    r'test_\w+\.py',
    r'\w+_test\.py',
    r'conftest\.py',
]
```

## Integration

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-safeguards
        name: Check Safeguards
        entry: python scripts/check_safeguards.py
        language: python
        types: [python]
```

### CI Integration

```yaml
# .github/workflows/safeguards.yml
- name: Check Safeguard Coverage
  run: |
    python scripts/space_traversal/audit_runner.py run
    python scripts/check_safeguard_score.py --min-score 0.85
```

## Related Capabilities

- [MCP Security Safeguards](mcp_security_safeguards.md) - MCP-specific safeguards
- [Code Quality Tooling](code_quality_tooling.md) - Static analysis
- [Structural Integrity](structural_integrity.md) - Code structure validation

## References

- OWASP Security Guidelines: https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/
- Python Security Best Practices: https://docs.python.org/3/library/security_warnings.html
