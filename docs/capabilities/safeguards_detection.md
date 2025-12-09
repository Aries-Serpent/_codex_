# Safeguards Detection and Validation

## Overview

The safeguards detection system identifies defensive programming patterns, security measures, and robustness indicators throughout the codebase. It combines keyword matching with context-aware pattern detection to provide comprehensive analysis of safeguard coverage.

## Purpose

Safeguards are critical for:
- **Security**: Input validation, sanitization, authentication
- **Robustness**: Error handling, bounds checking, timeout management
- **Maintainability**: Defensive programming, explicit error handling
- **Determinism**: Reproducible behavior, offline-first design

The safeguards_keywords capability measures how well the codebase implements these defensive practices.

## Detection Methods

### Method 1: Keyword Detection

Scans code for safeguard-related keywords across multiple categories:

**Security & Cryptography:**
- `sha256`, `checksum` - Data integrity
- `validate`, `validation` - Input validation
- `sanitize`, `sanitization` - Input sanitization
- `authenticate`, `authorization` - Access control

**Determinism & Reproducibility:**
- `rng`, `seed` - Random number generation control
- `deterministic`, `reproducible` - Predictable behavior
- `offline` - Network-independent operation

**Rate Limiting & Bounds:**
- `rate_limit`, `ratelimit` - Request throttling
- `bounds_check`, `bounded` - Value range validation
- `timeout` - Operation time limits
- `max_retries` - Retry attempt limits

**Error Handling & Safety:**
- `try_except`, `error_handling` - Exception management
- `rollback`, `cleanup` - State restoration
- `safeguard`, `defensive`, `robust` - General defensive patterns

### Method 2: Context-Aware Pattern Detection

Detects defensive programming patterns using regex:

**Try-Except Blocks:**
```python
try:
    risky_operation()
except SpecificError as e:
    handle_error(e)
```

**Null Checks:**
```python
if value is None:
    return default_value
```

**Assertions:**
```python
assert input_valid(data), "Input must be valid"
```

**Explicit Error Raising:**
```python
raise ValueError("Invalid configuration")
```

**Input Sanitization:**
```python
clean_input = user_input.strip().lower()
```

## Usage

### Running Detection

#### Via Audit Pipeline

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain safeguards_keywords
```

Results appear in `audit_artifacts/capabilities_scored.json`.

#### Standalone Detection

```python
from scripts.space_traversal.detectors.detector_safeguards import detect

# Create context index
context_index = {
    "files": [
        {"path": "src/auth.py"},
        {"path": "src/validation.py"},
    ]
}

# Run detection
result = detect(context_index)

print(f"Total safeguards: {result['total_hits']}")
print(f"Files with safeguards: {result['unique_files']}")
print(f"Safeguard density: {result['safeguard_density']:.2%}")
print(f"Found patterns: {result['found_patterns']}")
```

## Interpreting Results

### Safeguard Density

Density = (Files with safeguards) / (Total files analyzed)

- **0.0 - 0.2**: Low coverage (improvement needed)
- **0.2 - 0.4**: Moderate coverage (acceptable)
- **0.4 - 0.6**: Good coverage (recommended)
- **0.6 - 1.0**: Excellent coverage (best practice)

### Total Hits

Count of all safeguard occurrences across the codebase.

- Higher is generally better
- Target: 2-5 safeguards per file on average

### Pattern Detections

Context-aware patterns detected per file:
```json
{
  "src/secure_api.py": ["try_except", "null_check", "assertion"],
  "src/validator.py": ["explicit_error", "input_sanitization"]
}
```

## Best Practices

### Writing Detectable Safeguards

#### 1. Input Validation

```python
def process_user_input(data: str) -> str:
    """Process with validation safeguard."""
    # Validate input type and bounds
    if not isinstance(data, str):
        raise TypeError("Input must be string")
    if len(data) > MAX_LENGTH:  # bounded check
        raise ValueError(f"Input exceeds {MAX_LENGTH} chars")
    
    # Sanitize input
    return data.strip().lower()
```

#### 2. Error Handling

```python
def fetch_remote_data(url: str, timeout: int = 30) -> dict:
    """Fetch with timeout and error handling safeguards."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.error(f"Request timeout after {timeout}s")
        raise
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        # rollback or cleanup if needed
        raise
```

#### 3. Deterministic Behavior

```python
def generate_samples(count: int, seed: int = 42) -> list:
    """Generate with deterministic seed safeguard."""
    rng = np.random.RandomState(seed)  # deterministic
    return rng.normal(size=count).tolist()
```

#### 4. Defensive Checks

```python
def safe_divide(a: float, b: float) -> float:
    """Divide with defensive null and bounds checks."""
    # Null checks
    if a is None or b is None:
        raise ValueError("Arguments cannot be None")
    
    # Bounds check - avoid division by zero
    if abs(b) < 1e-10:  # bounded threshold
        raise ZeroDivisionError("Divisor too close to zero")
    
    return a / b
```

#### 5. Rate Limiting

```python
@rate_limit(max_calls=100, period=60)  # rate_limit decorator
def api_endpoint(request):
    """API with rate limiting safeguard."""
    # Process request with bounds
    if len(request.data) > MAX_REQUEST_SIZE:  # bounded
        return {"error": "Request too large"}, 413
    
    return process_request(request)
```

## Configuration

### Expanding Keyword List

Edit `scripts/space_traversal/detectors/detector_safeguards.py`:

```python
SAFEGUARD_KEYWORDS = {
    # Add your custom keywords
    "circuit_breaker",
    "health_check",
    "graceful_degradation",
    # ...existing keywords...
}
```

### Adding Custom Patterns

```python
DEFENSIVE_PATTERNS = [
    # Add custom regex patterns
    (r'with\s+lock:', "lock_usage"),
    (r'@retry\(', "retry_decorator"),
    # ...existing patterns...
]
```

## Metrics and Scoring

### Component Scores

The safeguards_keywords capability is scored on:

1. **Functionality (25%)**: Pattern detection accuracy
2. **Tests (25%)**: Test coverage of detector
3. **Documentation (15%)**: Quality of this guide
4. **Safeguards (15%)**: Safeguards in detector itself
5. **Consistency (20%)**: Code quality

### Improving Your Score

**To Increase Safeguard Density:**
1. Add input validation to all public APIs
2. Implement error handling with try-except
3. Add bounds checking for arrays and loops
4. Use timeouts for network operations
5. Add defensive null checks

**Example Refactoring:**

Before (no safeguards):
```python
def process(data):
    result = data["value"] * 2
    return result
```

After (with safeguards):
```python
def process(data):
    """Process with validation and error handling."""
    # Validation safeguard
    if not isinstance(data, dict):
        raise TypeError("Data must be dict")
    
    # Null check safeguard
    if "value" not in data or data["value"] is None:
        return 0  # defensive default
    
    try:
        # Bounds check for multiplication
        value = float(data["value"])
        if abs(value) > MAX_VALUE:  # bounded
            raise ValueError(f"Value exceeds {MAX_VALUE}")
        
        result = value * 2
        return result
    except (TypeError, ValueError) as e:
        # Error handling safeguard
        logger.error(f"Processing failed: {e}")
        raise
```

## Analysis Workflow

### Step 1: Run Baseline Detection

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain safeguards_keywords
```

Note the current scores and density.

### Step 2: Identify Files Without Safeguards

```python
import json

with open('audit_artifacts/capabilities_raw.json') as f:
    data = json.load(f)

for cap in data['capabilities']:
    if cap['id'] == 'safeguards_keywords':
        all_files = set(cap.get('all_analyzed_files', []))
        safeguard_files = set(cap.get('evidence_files', []))
        missing = all_files - safeguard_files
        
        print(f"Files without safeguards ({len(missing)}):")
        for f in sorted(missing)[:10]:
            print(f"  - {f}")
```

### Step 3: Add Safeguards

Focus on:
- Public API functions (add validation)
- Network operations (add timeouts)
- File operations (add error handling)
- Data processing (add bounds checks)

### Step 4: Re-run and Verify

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain safeguards_keywords
```

Check for improvement in density and total hits.

## Examples

### Example 1: Security Validation

```python
from typing import Optional

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate with validation and sanitization safeguards."""
    # Input validation
    if not username or not password:
        raise ValueError("Username and password required")
    
    # Sanitize inputs
    username = username.strip().lower()
    
    # Bounds check
    if len(username) > 50 or len(password) > 100:  # bounded
        raise ValueError("Input exceeds maximum length")
    
    # Hash password (sha256 safeguard)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        # Timeout for database query
        user = db.query(User).filter_by(
            username=username,
            password_hash=password_hash
        ).first(timeout=5)  # timeout safeguard
        
        return user.to_dict() if user else None
    except DatabaseError as e:
        logger.error(f"Authentication failed: {e}")
        return None  # defensive fallback
```

Safeguards detected: validate, sanitize, bounded, sha256, timeout, defensive

### Example 2: Robust Data Processing

```python
def process_batch(items: list, max_items: int = 1000) -> list:
    """Process with comprehensive safeguards."""
    # Validation
    if not isinstance(items, list):
        raise TypeError("Items must be a list")
    
    # Bounds check (bounded safeguard)
    if len(items) > max_items:
        raise ValueError(f"Batch size {len(items)} exceeds {max_items}")
    
    results = []
    errors = []
    
    for i, item in enumerate(items):
        try:
            # Null check (defensive)
            if item is None:
                errors.append(f"Item {i} is None")
                continue
            
            # Process with validation
            validated = validate(item)
            result = transform(validated)
            results.append(result)
            
        except Exception as e:
            # Error handling safeguard
            errors.append(f"Item {i} failed: {e}")
            # Continue processing remaining items (robust)
    
    if errors:
        logger.warning(f"Processed {len(results)}/{len(items)}, errors: {len(errors)}")
    
    return results
```

Safeguards detected: validation, bounded, defensive, robust

### Example 3: Deterministic Algorithm

```python
import random

def generate_dataset(size: int, seed: int = 42, offline: bool = True) -> list:
    """Generate with deterministic and offline safeguards."""
    # Validation
    if size <= 0:
        raise ValueError("Size must be positive")
    
    # Bounds check
    if size > 1_000_000:  # bounded
        raise ValueError("Size too large")
    
    # Deterministic seed
    random.seed(seed)  # deterministic, reproducible
    
    # Offline generation (no network calls)
    # offline mode ensures reproducibility
    data = [random.gauss(0, 1) for _ in range(size)]
    
    return data
```

Safeguards detected: validation, bounded, deterministic, reproducible, seed, offline

## Integration with CI/CD

### Quality Gate

```yaml
# .github/workflows/quality.yml
- name: Check Safeguard Coverage
  run: |
    python scripts/space_traversal/audit_runner.py run
    python -c "
    import json
    with open('audit_artifacts/capabilities_scored.json') as f:
        data = json.load(f)
    for cap in data['capabilities']:
        if cap['id'] == 'safeguards_keywords':
            density = cap.get('safeguard_density', 0)
            if density < 0.4:
                print(f'❌ Safeguard density {density:.2%} below 40%')
                exit(1)
            print(f'✓ Safeguard density {density:.2%}')
    "
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run safeguard detection on staged files
python scripts/space_traversal/audit_runner.py run --incremental

# Check if new files lack safeguards
python scripts/check_safeguards.py --staged
```

## Troubleshooting

### Low Detection Rate

**Problem**: Expected safeguards not being detected.

**Solutions**:
1. Check keyword spelling matches `SAFEGUARD_KEYWORDS`
2. Ensure files have allowed extensions (.py, .md, .sh, .txt, .yml, .yaml, .json)
3. Verify files aren't excluded by `.gitignore`
4. Check file size doesn't exceed `MAX_READ_BYTES` (200KB)

### False Positives

**Problem**: Keywords detected in unrelated contexts.

**Solutions**:
- Keywords in comments and docstrings count (by design)
- Consider this intentional - documentation of safeguards is valuable
- Use context-aware patterns for more precision

### Performance Issues

**Problem**: Detection takes too long on large codebases.

**Solutions**:
1. Bounded reads already implemented (`MAX_READ_BYTES`)
2. Run incrementally on changed files only
3. Cache results and run differentially

## Related Capabilities

- **testing-infrastructure**: Test coverage validation
- **code-quality-tooling**: Linting and style checks
- **mcp-security-safeguards**: MCP-specific security
- **reproducibility**: Deterministic behavior

## Keywords

For audit detection, these keywords indicate safeguard practices:
- **safeguard**: General protective measures
- **validation**: Input/output validation
- **security**: Security measures
- **defensive**: Defensive programming
- **robust**: Error-tolerant design
- **sanitize**: Input sanitization
- **bounded**: Bounded operations
- **deterministic**: Reproducible behavior
- **timeout**: Time-limited operations
- **offline**: Network-independent

## See Also

- [Detector Implementation](../../scripts/space_traversal/detectors/detector_safeguards.py)
- [Test Suite](../../tests/safeguards/test_keyword_detection.py)
- [Audit Pipeline Guide](../../docs/SPACE_TRAVERSAL_GUIDE.md)
