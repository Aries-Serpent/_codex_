# Duplication Detection and Analysis

## Overview

The duplication detection system analyzes code duplication across the repository to support consistency scoring in the capability audit pipeline. It provides two complementary methods for detecting duplication: stem-based analysis and token-similarity analysis.

## Purpose

Code duplication can indicate:
- **Maintenance burden**: Changes need to be applied in multiple places
- **Consistency issues**: Similar functionality implemented differently
- **Refactoring opportunities**: Common code that should be extracted
- **Architecture concerns**: Potential design problems

The duplication ratio is a key component of the consistency score in capability assessments.

## Detection Methods

### Method 1: Stem-Based Detection (Default)

**How it works:**
- Extracts the file stem (filename without extension) from each file
- Counts occurrences of each stem across the repository
- Calculates ratio: (duplicate count) / (total files)

**Example:**
```
Files:
- tests/test_feature.py
- docs/test_feature.md
- src/test_feature.py

Stem "test_feature" appears 3 times
Duplication ratio: 2/3 = 0.67 (67%)
```

**Advantages:**
- Fast and lightweight
- No content analysis required
- Deterministic and reproducible
- Identifies naming patterns

**Use when:**
- Quick analysis needed
- File naming conventions are important
- Memory constraints exist

### Method 2: Token-Similarity Analysis (Advanced)

**How it works:**
- Tokenizes file content into normalized tokens
- Compares files using Jaccard similarity
- Identifies semantic duplication beyond naming
- Bounded pairwise comparisons for scalability

**Example:**
```python
from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

ratio = duplication_ratio_token_similarity(
    evidence_files=["file1.py", "file2.py"],
    file_cache={"file1.py": content1, "file2.py": content2},
    threshold=0.7,
    max_pairwise=1000,
    max_tokens_per_file=1000
)
```

**Advantages:**
- Content-aware detection
- Finds copy-paste code
- Configurable similarity threshold
- More accurate than stem-based

**Use when:**
- Detailed analysis needed
- Content duplication suspected
- Refactoring prioritization required

## Usage

### Running Detection

#### Via Audit Pipeline

The duplication detector runs automatically as part of the audit pipeline:

```bash
python scripts/space_traversal/audit_runner.py run
```

Results are included in `audit_artifacts/capabilities_scored.json` as part of the consistency score.

#### Standalone Detection

```python
from scripts.space_traversal.detectors.detector_duplication import detect

# Create context index
context_index = {
    "files": [
        {"path": "src/module_a.py"},
        {"path": "src/module_b.py"},
        {"path": "tests/test_module_a.py"},
    ]
}

# Run detection
result = detect(context_index)

print(f"Duplication ratio: {result['dup_ratio']:.2%}")
print(f"Duplicate groups: {result['duplicate_groups']}")
print(f"Metrics: {result['metrics']}")
```

### Configuration

#### Stem-Based (Default)

```yaml
# .copilot-space/workflow.yaml
scoring:
  dup:
    heuristic: simple  # Default
```

#### Token-Similarity

```yaml
scoring:
  dup:
    heuristic: token_similarity
    threshold: 0.7              # Jaccard similarity threshold
    max_pairwise: 1000          # Max comparisons
    max_tokens_per_file: 1000   # Tokens per file limit
```

## Interpreting Results

### Duplication Ratio

- **0.0 - 0.2**: Low duplication (good)
- **0.2 - 0.4**: Moderate duplication (acceptable)
- **0.4 - 0.6**: High duplication (review needed)
- **0.6 - 1.0**: Very high duplication (action required)

### Consistency Score

The consistency score is calculated as:
```
consistency = 1.0 - duplication_ratio
```

Higher consistency scores indicate better code organization.

### Duplicate Groups

The detector identifies groups of files with duplicate stems:

```python
{
  "test_feature": [
    "src/test_feature.py",
    "tests/test_feature.py",
    "docs/test_feature.md"
  ],
  "config": [
    "src/config.py",
    "tests/config.py"
  ]
}
```

## Analysis Workflow

### Step 1: Run Detection

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain duplication_ratio
```

### Step 2: Review Results

Check the duplication ratio and identify duplicate groups:

```bash
python -c "
import json
with open('audit_artifacts/capabilities_raw.json') as f:
    data = json.load(f)
for cap in data['capabilities']:
    if cap['id'] == 'duplication_ratio':
        print('Ratio:', cap.get('dup_ratio'))
        print('Groups:', cap.get('duplicate_groups'))
"
```

### Step 3: Prioritize Refactoring

Focus on:
1. High-count duplicate groups (most instances)
2. Core functionality modules
3. Frequently changed files

### Step 4: Refactor

Common refactoring patterns:
- Extract common functionality to shared modules
- Use inheritance or composition
- Create utility functions
- Implement design patterns

## Tuning and Optimization

### Reducing False Positives

**Stem-based method:**
- Some duplication is intentional (e.g., `test_X.py` and `X.py`)
- Consider file paths, not just stems
- Use token-similarity for deeper analysis

**Token-similarity method:**
- Adjust threshold (lower = more sensitive)
- Increase max_tokens_per_file for better accuracy
- Review duplicate groups manually

### Performance Considerations

**Stem-based:**
- O(n) time complexity
- Minimal memory usage
- Suitable for large repositories

**Token-similarity:**
- O(n²) worst case, bounded by max_pairwise
- Higher memory usage
- Best for focused analysis

### Determinism Guarantees

Both methods ensure:
- Stable ordering of results
- Reproducible metrics
- No randomness or network calls
- Bounded operations (no infinite loops)

## Integration with Audit Pipeline

### Automatic Integration

The detector integrates with the audit pipeline through:

1. **S1 (Indexing)**: Files are indexed
2. **S3 (Capabilities)**: Detector runs on index
3. **S4 (Scoring)**: Results feed consistency score
4. **S6 (Reporting)**: Included in capability reports

### Consistency Component

```python
# In audit_runner.py scoring stage
consistency = 1.0 - duplication_ratio(evidence_files, file_cache, cfg)
```

### Evidence Files

The detector uses all repository files as evidence:
- Python files (`.py`)
- Documentation (`.md`)
- Configuration (`.yml`, `.json`)
- Scripts and tools

## Examples

### Example 1: Basic Analysis

```python
from scripts.space_traversal.detectors.detector_duplication import detect

files = [
    {"path": "src/auth.py"},
    {"path": "tests/test_auth.py"},
    {"path": "docs/auth.md"},
    {"path": "src/config.py"},
]

result = detect({"files": files})

print(f"Duplication: {result['dup_ratio']:.2%}")
print(f"Total files: {result['evidence_count']}")
print(f"Unique stems: {result['metrics']['unique_stems']}")
```

Output:
```
Duplication: 33.33%
Total files: 4
Unique stems: 3
```

### Example 2: Identifying Duplicates

```python
result = detect({"files": files})

for stem, paths in result['duplicate_groups'].items():
    print(f"\nStem '{stem}' appears in:")
    for path in paths:
        print(f"  - {path}")
```

Output:
```
Stem 'auth' appears in:
  - docs/auth.md
  - src/auth.py
  - tests/test_auth.py
```

### Example 3: Monitoring Over Time

```bash
# Run audit at different points
python scripts/space_traversal/audit_runner.py run

# Track trends
python scripts/space_traversal/trend_aggregator.py --lookback-days 30

# Check duplication_ratio trends in report
cat audit_artifacts/trends/trend_report_*.md
```

## Keywords

For audit detection, the following keywords are used:
- **duplication**: Core concept being measured
- **similarity**: Comparison method
- **analysis**: Detection process
- **detection**: Pattern identification
- **consistency**: Scoring component
- **deterministic**: Reproducible results
- **bounded**: Performance guarantee
- **offline**: No network dependency

## Best Practices

1. **Monitor Regularly**: Track duplication trends over time
2. **Set Thresholds**: Define acceptable duplication levels for your project
3. **Refactor Gradually**: Address high-impact duplicates first
4. **Document Intentional Duplication**: Comment when duplication is by design
5. **Use Both Methods**: Stem-based for quick checks, token-similarity for deep analysis
6. **Integrate with CI**: Fail builds if duplication exceeds threshold

## Troubleshooting

### High False Positive Rate

**Problem**: Many files flagged as duplicates that aren't really similar.

**Solution**:
- Review stem naming conventions
- Use token-similarity for content analysis
- Adjust similarity threshold
- Consider path-based filtering

### Low Detection Rate

**Problem**: Known duplicates not being detected.

**Solution**:
- Check file extensions are included in index
- Verify files are not excluded by .gitignore
- Use token-similarity for better content matching
- Review detection logic for edge cases

### Performance Issues

**Problem**: Detection takes too long.

**Solution**:
- Use stem-based method for large repositories
- Reduce max_pairwise for token-similarity
- Run detection on subsets of files
- Cache results and run incrementally

## Related Capabilities

- **dup_similarity**: Token-based similarity detection
- **code-quality-tooling**: Linting and code analysis
- **testing-infrastructure**: Test coverage and quality
- **structure-integrity**: Repository organization

## See Also

- [Token Similarity Documentation](https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/README.md)
- [Audit Pipeline Guide](../SPACE_TRAVERSAL_GUIDE.md)
- [Capability Scoring Guide](../templates/status/capability_scoring_guide_v1.2.md)
