# Troubleshooting Guide v1.4.0

**Version**: 1.4.0  
**Last Updated**: Previous Cycle-12-09

---

## Overview

This guide addresses common issues when using audit pipeline v1.4.0, with a focus on new features:
- Coverage augmentation
- Token-similarity detection

---

## Coverage Augmentation Issues

### Issue: coverage_map.json Not Generated

**Symptoms**:
- File missing: `audit_artifacts/coverage_map.json`
- Test scores unchanged after enabling coverage
- No coverage data in capabilities_scored.json

**Possible Causes**:
1. coverage.xml not found
2. xml_patterns don't match your coverage file location
3. `coverage.enabled` is false in workflow.yaml
4. Coverage XML is empty or invalid

**Solutions**:

**Step 1**: Verify coverage XML exists
```bash
ls -lh coverage.xml
# Should show a file with size > 0
```

**Step 2**: Check coverage XML has data
```bash
grep "line-rate" coverage.xml
# Should show line-rate > 0
```

**Step 3**: Verify workflow.yaml configuration
```bash
cat workflow.yaml | grep -A 5 "coverage:"
# Should show enabled: true
```

**Step 4**: Check xml_patterns match
```bash
# If your coverage file is in a different location
# Update workflow.yaml:
scoring:
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
      - "build/coverage.xml"  # Add your path
      - "**/coverage.xml"
```

**Step 5**: Manually generate coverage_map.json
```bash
python scripts/space_traversal/coverage_ingest.py coverage.xml

# Verify output
ls -lh audit_artifacts/coverage_map.json
cat audit_artifacts/coverage_map.json | jq 'keys | length'
```

**Step 6**: Check for errors in audit logs
```bash
python scripts/space_traversal/audit_runner.py run --verbose 2>&1 | grep -i coverage
```

---

### Issue: Test Scores Unchanged After Enabling Coverage

**Symptoms**:
- coverage_map.json exists but test scores are same as before
- No improvement in test component scores

**Possible Causes**:
1. All files have 0% coverage
2. `augment_tests_score` is false
3. Baseline test score already higher than coverage
4. Coverage map doesn't match source files

**Solutions**:

**Step 1**: Check coverage data
```bash
cat audit_artifacts/coverage_map.json | jq '.[] | select(.percent > 0) | {percent}'
# Should show files with >0% coverage
```

**Step 2**: Verify augment_tests_score setting
```bash
cat workflow.yaml | grep -A 3 "coverage:"
# Should show augment_tests_score: true
```

**Step 3**: Compare test scores
```bash
# Check if coverage percent > baseline
cat audit_artifacts/capabilities_scored.json | jq '.capabilities[] | select(.tests.score > 0) | {id, tests: .tests.score}'
```

**Step 4**: Check file path matching
```bash
# Coverage map uses relative paths from repo root
# Verify paths match your source structure
cat audit_artifacts/coverage_map.json | jq 'keys[]' | head -10
```

---

### Issue: Coverage XML Parse Error

**Symptoms**:
- Error: "Failed to parse coverage XML"
- Empty coverage_map.json

**Possible Causes**:
- Invalid XML format
- Corrupted coverage file
- Unsupported coverage format

**Solutions**:

**Step 1**: Validate XML syntax
```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('coverage.xml')"
# Should complete without errors
```

**Step 2**: Check coverage format
```bash
# Should be Cobertura or coverage.py format
head -5 coverage.xml
# Look for <coverage> root element
```

**Step 3**: Regenerate coverage with correct format
```bash
# Using pytest-cov (Cobertura format)
pytest --cov=src --cov-report=xml

# Using coverage.py directly
coverage run -m pytest tests/
coverage xml
```

---

## Token-Similarity Issues

### Issue: Token-Similarity Very Slow

**Symptoms**:
- Audit takes >5 minutes
- Stage S4 (scoring) appears to hang
- High CPU usage during duplication detection

**Possible Causes**:
- `max_pairwise` too high
- Too many evidence files per capability (>100)
- `max_tokens_per_file` too high
- Large files being tokenized

**Solutions**:

**Step 1**: Reduce max_pairwise
```yaml
# In workflow.yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7
    max_pairwise: 500      # Reduced from 1000
    max_tokens_per_file: 500  # Reduced from 1000
```

**Step 2**: Check capability evidence file counts
```bash
cat audit_artifacts/capabilities_raw.json | jq '.capabilities[] | {id, count: (.evidence_files | length)} | select(.count > 100)'
```

**Step 3**: Use simple heuristic for problematic capabilities
```yaml
# Fallback to fast mode
scoring:
  dup:
    heuristic: "simple"
```

**Step 4**: Profile performance
```bash
time python scripts/space_traversal/audit_runner.py stage S4
# Identify which stage is slow
```

---

### Issue: Scores Decreased Significantly After v1.4.0

**Symptoms**:
- Overall scores lower than v1.3.x
- Consistency scores dropped by >0.2
- Multiple capabilities affected

**Possible Causes**:
- Token-similarity is more accurate (detects actual duplicates)
- Coverage data shows lower coverage than estimated
- This is often **correct behavior** revealing real issues

**Solutions**:

**Step 1**: Review which capabilities decreased
```bash
python scripts/space_traversal/audit_runner.py diff \
  audit_artifacts.v1.3.backup/capabilities_scored.json \
  audit_artifacts/capabilities_scored.json
```

**Step 2**: Check if duplication detection is accurate
```bash
# Review duplicate file groups
cat audit_artifacts/capabilities_scored.json | jq '.capabilities[] | select(.consistency.score < 0.5) | {id, consistency}'
```

**Step 3**: If token-similarity is too strict, adjust threshold
```yaml
scoring:
  dup:
    threshold: 0.5  # Lower = less strict (more lenient)
```

**Step 4**: If coverage revealed gaps, this is accurate feedback
```bash
# Check actual coverage vs test scores
cat audit_artifacts/coverage_map.json | jq '.[] | select(.percent < 0.5) | {percent}'
```

**Step 5**: Validate findings manually
```bash
# Spot-check files flagged as duplicates
# Verify they are actually similar
```

---

### Issue: High Duplication Ratio Despite Unique Files

**Symptoms**:
- Duplication ratio > 0.8 but files are different
- False positives in duplicate detection

**Possible Causes**:
- Threshold too low (catching dissimilar files)
- Boilerplate code counted as duplication
- Short files with common patterns

**Solutions**:

**Step 1**: Increase threshold
```yaml
scoring:
  dup:
    threshold: 0.9  # Higher = more strict (fewer duplicates)
```

**Step 2**: Review tokenization
```bash
# Check which files are flagged as similar
# Manually review pairs
```

**Step 3**: Fallback to simple heuristic if needed
```yaml
scoring:
  dup:
    heuristic: "simple"
```

---

## General Pipeline Issues

### Issue: Import Errors When Running Audit

**Symptoms**:
- `ModuleNotFoundError: No module named 'dup_similarity'`
- `ModuleNotFoundError: No module named 'coverage_ingest'`
- `ImportError: cannot import name 'discover_and_parse_coverage'`

**Possible Causes**:
- Modules not in Python path
- Running from wrong directory
- Incorrect Python environment

**Solutions**:

**Step 1**: Ensure you're in repository root
```bash
cd /path/to/_codex_
pwd  # Should show repository root
```

**Step 2**: Add to Python path
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Step 3**: Or use make command (sets path automatically)
```bash
make space-audit
```

**Step 4**: Verify modules exist
```bash
ls -lh scripts/space_traversal/coverage_ingest.py
ls -lh scripts/space_traversal/dup_similarity.py
```

---

### Issue: Type Errors in mypy

**Symptoms**:
- mypy reports errors in coverage_ingest.py
- mypy reports errors in dup_similarity.py
- Type checking fails in CI

**Possible Causes**:
- Strict type checking enabled
- Modified files without type annotations

**Solutions**:

**Already fixed in v1.4.0** - Files have proper type ignores

If you modified files:
```python
# Add type ignores where needed
data["percent"] = 0.85  # type: ignore[assignment]
```

---

### Issue: Audit Pipeline Hangs

**Symptoms**:
- Pipeline appears to freeze
- No output for several minutes
- CPU at 100%

**Possible Causes**:
- Token-similarity on large evidence sets
- Infinite loop in custom detector
- Large files being processed

**Solutions**:

**Step 1**: Run with verbose mode
```bash
python scripts/space_traversal/audit_runner.py run --verbose
```

**Step 2**: Run stages individually
```bash
# Run each stage to identify which hangs
python scripts/space_traversal/audit_runner.py stage S1
python scripts/space_traversal/audit_runner.py stage S2
python scripts/space_traversal/audit_runner.py stage S3
python scripts/space_traversal/audit_runner.py stage S4  # Often this one
```

**Step 3**: Disable token-similarity temporarily
```yaml
scoring:
  dup:
    heuristic: "simple"
```

**Step 4**: Check for custom detector issues
```bash
# Review custom detectors for infinite loops
ls scripts/space_traversal/detectors/detector_*.py
```

---

### Issue: Configuration Not Applied

**Symptoms**:
- Changes to workflow.yaml have no effect
- Features still disabled despite configuration

**Possible Causes**:
- YAML syntax error
- Using wrong workflow.yaml file
- Cached configuration

**Solutions**:

**Step 1**: Validate YAML syntax
```bash
python -c "import yaml; print(yaml.safe_load(open('workflow.yaml')))"
```

**Step 2**: Verify correct file is being used
```bash
# Check which workflow.yaml is loaded
python -c "from pathlib import Path; print(Path('workflow.yaml').resolve())"
```

**Step 3**: Clear any cached data
```bash
rm -rf audit_artifacts/
make space-audit
```

---

## Performance Issues

### Issue: Audit Takes Too Long

**Symptoms**:
- Audit takes >10 minutes
- Unacceptable for CI/pre-commit

**Solutions**:

**Use fast path**:
```bash
make space-audit-fast  # Skips S2, S5, S7
```

**Disable expensive features**:
```yaml
scoring:
  coverage:
    enabled: false  # Skip coverage if not needed
  dup:
    heuristic: "simple"  # Use fast mode
```

**Tune parameters**:
```yaml
scoring:
  dup:
    max_pairwise: 100  # Minimal comparisons
    max_tokens_per_file: 500
```

---

## Getting More Help

### Enable Debug Logging

```bash
python scripts/space_traversal/audit_runner.py run --verbose 2>&1 | tee audit.log
```

### Check Audit Manifest

```bash
cat audit_artifacts/audit_run_manifest.json | jq '.'
# Look for warnings or errors
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.12+

# Check dependencies
pip install pyyaml jinja2 pytest pytest-cov

# Verify modules
python -c "from scripts.space_traversal import coverage_ingest, dup_similarity"
```

### Report Issues

If problems persist:
1. Gather audit.log
2. Save workflow.yaml
3. Note Python version and OS
4. Include error messages
5. Create issue with details

---

## See Also

- [Configuration Guide](./Configuration_v1.4.0.md) - Configuration options
- [Migration Guide](./Migration_v1.3_to_v1.4.md) - Upgrading from v1.3.x
- [API Reference](./API_Reference_v1.4.0.md) - Module documentation
- [Performance Tuning](./Performance_Tuning.md) - Optimization strategies
