# Configuration Guide for v1.4.0 Features

**Version**: 1.4.0  
**Last Updated**: 2025-12-09

---

## Overview

This guide explains how to configure the new features introduced in audit pipeline v1.4.0:
- **Coverage Augmentation**: Enhance test scores with actual code coverage data
- **Token-Similarity Detection**: Advanced duplication detection using content analysis

---

## Coverage Augmentation Configuration

### Overview

Coverage augmentation improves test score accuracy by incorporating actual code coverage percentages from your test suite.

### Enable Coverage Augmentation

**Step 1**: Add configuration to `workflow.yaml`:

```yaml
scoring:
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
      - ".coverage.xml"
      - "**/coverage.xml"
    augment_tests_score: true  # Use max(baseline, coverage_percent)
```

**Step 2**: Generate coverage XML during tests:

```bash
# Using pytest
pytest --cov=src --cov-report=xml

# Using coverage.py directly
coverage run -m pytest tests/
coverage xml
```

**Step 3**: Run audit pipeline:

```bash
make space-audit
```

**Step 4**: Verify coverage_map.json was generated:

```bash
ls -lh audit_artifacts/coverage_map.json
# Should show a file with coverage data for your source files
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | false | Enable/disable coverage augmentation |
| `xml_patterns` | list[str] | `["coverage.xml"]` | Glob patterns to find coverage XML files |
| `augment_tests_score` | boolean | true | Use max(baseline_score, coverage_percent) |

### XML Pattern Examples

**Single file in root**:
```yaml
xml_patterns:
  - "coverage.xml"
```

**Multiple possible locations**:
```yaml
xml_patterns:
  - "coverage.xml"
  - "build/coverage.xml"
  - "test-results/coverage.xml"
```

**Recursive search**:
```yaml
xml_patterns:
  - "**/coverage.xml"
  - "**/.coverage.xml"
```

### Disable Coverage Augmentation

Set `enabled: false` in workflow.yaml:

```yaml
scoring:
  coverage:
    enabled: false
```

Or remove the entire `coverage` section to use defaults (disabled).

---

## Token-Similarity Duplication Detection

### Overview

Token-similarity provides more accurate duplication detection by analyzing actual file content, not just filenames.

### Enable Token-Similarity

**Add configuration to `workflow.yaml`**:

```yaml
scoring:
  dup:
    heuristic: "token_similarity"  # or "simple" for backward compatibility
    threshold: 0.7                 # Jaccard similarity threshold (0.0-1.0)
    max_pairwise: 1000            # Cap pairwise comparisons
    max_tokens_per_file: 1000     # Max tokens to extract per file
```

**Run audit**:

```bash
make space-audit
```

**Verify** in `audit_artifacts/capabilities_scored.json`:
- Consistency scores should reflect content-based duplication

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `heuristic` | string | "simple" | Detection method: "simple" or "token_similarity" |
| `threshold` | float | 0.7 | Jaccard similarity threshold (0.0-1.0) |
| `max_pairwise` | integer | 1000 | Maximum pairwise comparisons |
| `max_tokens_per_file` | integer | 1000 | Maximum tokens per file |

### Tuning the Threshold

The `threshold` parameter controls sensitivity:

**Conservative (0.9 - 1.0)**:
- Only detects near-identical files
- Fewer false positives
- May miss legitimate duplicates

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.9
```

**Balanced (0.7 - 0.8)** - **RECOMMENDED**:
- Good balance of accuracy and detection
- Default setting
- Works well for most codebases

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
```

**Aggressive (0.5 - 0.6)**:
- Detects more potential duplicates
- Higher false positive rate
- Useful for identifying refactoring opportunities

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.5
```

### Performance Tuning

**For large codebases** (>10,000 files):

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 500              # Reduce comparisons
    max_tokens_per_file: 500       # Reduce memory usage
```

**For maximum accuracy** (small/medium codebases):

```yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 5000             # More comparisons
    max_tokens_per_file: 2000      # More tokens analyzed
```

**For fast CI runs**:

```yaml
scoring:
  dup:
    heuristic: "simple"  # Fallback to fast mode
```

### Disable Token-Similarity

Revert to simple (filename-based) detection:

```yaml
scoring:
  dup:
    heuristic: "simple"
```

Or remove the `heuristic` key to use defaults.

---

## Complete Example Configuration

```yaml
# workflow.yaml - Full v1.4.0 configuration example

version: "1.4.0"

# Output directories
output:
  artifacts_dir: "audit_artifacts"
  reports_dir: "reports"

# Scoring weights
weights:
  functionality: 0.25
  consistency: 0.20
  tests: 0.25
  safeguards: 0.15
  documentation: 0.15

# Scoring configuration
scoring:
  # Coverage augmentation (v1.4.0)
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
      - "**/coverage.xml"
    augment_tests_score: true

  # Duplication detection (v1.4.0)
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 1000
    max_tokens_per_file: 1000

  # Scoring thresholds
  thresholds:
    high: 0.85
    medium: 0.70
    low: 0.50

# Capability detection
capability_map:
  dynamic: false
  overrides:
    canonical-capability:
      - alias-capability-1
      - alias-capability-2
```

---

## Validation

### Verify Configuration

```bash
# Check workflow.yaml syntax
python -c "import yaml; yaml.safe_load(open('workflow.yaml'))"

# Test coverage generation
pytest --cov=src --cov-report=xml
python scripts/space_traversal/coverage_ingest.py coverage.xml

# Run audit with new configuration
make space-audit

# Check results
cat audit_artifacts/coverage_map.json | jq 'keys | length'
cat audit_artifacts/capabilities_scored.json | jq '.capabilities[0]'
```

### Common Issues

**Coverage not found**:
- Check xml_patterns match your coverage file location
- Verify coverage.xml exists and is readable
- Check for errors in audit logs

**Scores unchanged**:
- Verify coverage_map.json was generated
- Check that files have >0% coverage
- Confirm augment_tests_score is true

**Slow performance**:
- Reduce max_pairwise (e.g., 500)
- Reduce max_tokens_per_file (e.g., 500)
- Or fallback to heuristic: "simple"

---

## Best Practices

1. **Start with defaults**: Enable features with default settings first
2. **Measure impact**: Compare scores before/after enabling
3. **Tune gradually**: Adjust thresholds based on results
4. **Monitor performance**: Track audit pipeline runtime
5. **Document changes**: Note configuration changes in commits

---

## See Also

- [Migration Guide](./Migration_v1.3_to_v1.4.md) - Upgrading from v1.3.x
- [Troubleshooting Guide](./Troubleshooting_v1.4.0.md) - Common issues
- [API Reference](./API_Reference_v1.4.0.md) - Module documentation
- [Performance Tuning](./Performance_Tuning.md) - Optimization strategies
