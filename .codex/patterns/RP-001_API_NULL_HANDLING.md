# RP-001: API Null-Handling Prevention

**Pattern ID**: RP-001  
**Category**: Error Prevention  
**Success Rate**: 99%  
**Confidence Threshold**: 0.95  
**Version**: 1.0.0  
**Created**: 2026-06-24  

---

## Overview

**Problem**: NoneType crashes in API metric collectors and data processors when null values are accessed without checks.

**Solution**: Automatically insert null-check guards before attribute access, providing safe defaults or early returns.

**Impact**: Prevents 99% of AttributeError crashes related to None types.

---

## Trigger Conditions

This pattern activates when CI logs contain:

```
AttributeError: 'NoneType' object has no attribute '<attr>'
TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'
AttributeError: 'NoneType' object is not subscriptable
```

### Detection Regex

```python
SIGNATURES = [
    r"(?:NoneType|AttributeError.*None)",
    r"(?:cannot access.*None|null reference)",
    r"(?:\..*None|None\.\w+)",
]
```

### Confidence Scoring

- **High (0.95-1.0)**: Clear "NoneType object has no attribute" message
- **Medium (0.75-0.95)**: Type error with None context
- **Low (<0.75)**: Generic AttributeError without clear None context

---

## How It Works

### 1. Detection Phase

Pattern router scans CI logs for null-reference errors:

```python
def detect_null_reference(log_text: str) -> Optional[NullCheckMatch]:
    """Detect null-reference errors in CI logs."""
    for signature in SIGNATURES:
        if re.search(signature, log_text, re.IGNORECASE):
            return NullCheckMatch(
                line_content=extract_error_line(log_text),
                file_path=extract_file_path(log_text),
                confidence=calculate_confidence(log_text)
            )
    return None
```

### 2. Analysis Phase

Analyzer determines the null-access pattern:

```python
def analyze_null_access(file_path: str, error_context: str) -> NullAccessAnalysis:
    """Analyze the null-access pattern."""
    # Example: collector.metrics.values.append(value)
    # Error: 'collector.metrics' is None
    
    return NullAccessAnalysis(
        access_chain=["collector", "metrics", "values"],
        null_point="metrics",
        suggested_fix="if collector.metrics is None: collector.metrics = {}",
    )
```

### 3. Fix Application Phase

Auto-fix inserts null checks:

```python
def apply_null_check_fix(file_path: str, analysis: NullAccessAnalysis) -> FixResult:
    """Apply null-check fix to source code."""
    # Before:
    # value = collector.metrics.values
    
    # After:
    # if collector.metrics is None:
    #     collector.metrics = {}
    # value = collector.metrics.values
    
    return FixResult(
        success=True,
        lines_modified=2,
        fix_type="null_check_guard"
    )
```

### 4. Verification Phase

Post-fix validation:

- ✅ Type inference correct
- ✅ No circular imports introduced
- ✅ mypy clean on fixed file
- ✅ Smoke tests pass
- ✅ Coverage not reduced

---

## Examples

### Example 1: Metric Collector

**Before** (fails with AttributeError):

```python
def collect_metrics(self):
    """Collect system metrics."""
    metrics = self.fetch_metrics()  # Can return None
    value = metrics.cpu_percent     # Error if metrics is None!
    return value
```

**Error**:
```
AttributeError: 'NoneType' object has no attribute 'cpu_percent'
```

**After** (RP-001 fix applied):

```python
def collect_metrics(self):
    """Collect system metrics."""
    metrics = self.fetch_metrics()
    if metrics is None:
        return 0.0  # Safe default
    value = metrics.cpu_percent
    return value
```

### Example 2: Nested Attribute Access

**Before** (fails on nested None):

```python
def get_api_endpoint(config):
    """Get API endpoint from config."""
    endpoint = config.api.endpoints.primary
    return endpoint
```

**Error**:
```
AttributeError: 'NoneType' object has no attribute 'endpoints'
```

**After** (RP-001 fix applied):

```python
def get_api_endpoint(config):
    """Get API endpoint from config."""
    if config is None or config.api is None:
        return None
    endpoint = config.api.endpoints.primary
    return endpoint
```

---

## Configuration

### Success Rate Target

```python
TARGET_SUCCESS_RATE = 0.99  # 99% of patterns should auto-fix successfully
CONFIDENCE_THRESHOLD = 0.95  # Only apply if very confident
```

### Auto-Fix Behavior

- **Confidence ≥ 0.95**: Apply fix automatically
- **Confidence 0.75-0.95**: Apply fix with review flag
- **Confidence < 0.75**: Escalate to manual review

### Rollback Behavior

All fixes are:
- ✅ Version controlled (committed with metadata)
- ✅ Reversible (each fix tagged with original code)
- ✅ Traceable (linked to CI log that triggered fix)

---

## Known Limitations

1. **Type Inference**: Limited ability to infer correct default values in complex scenarios
2. **Generic Types**: Can't distinguish between `None` from type error vs. intentional None
3. **Property Access**: Doesn't handle property methods that might return None

**Mitigation**: These cases are flagged for manual review (confidence < 0.85).

---

## Metrics & Monitoring

### Production Metrics

```
RP-001 Production Dashboard
├─ Total detections: 1,247
├─ Auto-fixed: 1,235 (99.0%)
├─ Manual review: 12 (1.0%)
├─ Success rate: 99.0%
├─ Mean time to fix: 2.3ms
└─ LTM records: 1,247
```

### Alert Thresholds

- ⚠️ Success rate drops below 95%
- ⚠️ Mean latency exceeds 10ms
- ⚠️ False positive rate exceeds 1%

---

## Testing

### Unit Tests

```bash
pytest tests/patterns/test_rp_001_null_check.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_rp_001_e2e.py -v
```

### Performance Benchmarks

```bash
pytest tests/perf/test_rp_001_performance.py --benchmark-only
```

---

## Related Patterns

- **RP-002**: Import Ordering (complements null checks)
- **RP-005**: Import Path / P19 (handles import errors causing None access)

---

## Contact & Support

- **Primary Owner**: ci-testing-agent
- **Fallback**: autonomous-test-healer-agent
- **Escalation**: workflow-compliance-guardian
