# API Reference v1.4.0

**Version**: 1.4.0  
**Last Updated**: 2025-12-09

---

## Overview

This document provides API reference for v1.4.0 modules:
- `coverage_ingest` - Coverage augmentation
- `dup_similarity` - Token-similarity duplication detection

---

## coverage_ingest Module

**Location**: `scripts/space_traversal/coverage_ingest.py`

### Functions

#### `discover_and_parse_coverage(cfg, artifacts_dir)`

Auto-discovers and parses coverage XML files based on configuration.

**Parameters**:
- `cfg` (dict): Workflow configuration dictionary
  - Must contain `scoring.coverage.enabled` (bool)
  - Must contain `scoring.coverage.xml_patterns` (list[str])
- `artifacts_dir` (Path): Directory to write coverage_map.json

**Returns**:
- `dict | None`: Coverage map dictionary, or None if:
  - Coverage is disabled
  - No coverage files found
  - Parse error occurred

**Raises**:
- No exceptions (errors logged and returns None)

**Example**:
```python
from pathlib import Path
import yaml
from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

# Load configuration
with open("workflow.yaml") as f:
    cfg = yaml.safe_load(f)

# Discover and parse
artifacts_dir = Path("audit_artifacts")
cov_map = discover_and_parse_coverage(cfg, artifacts_dir)

if cov_map:
    print(f"Coverage data for {len(cov_map)} files")
    # coverage_map.json written to artifacts_dir
else:
    print("No coverage data found or disabled")
```

---

#### `parse_coverage_xml_to_map(xml_path, root=None)`

Parse a coverage XML file to coverage map format.

**Parameters**:
- `xml_path` (Path): Path to coverage XML file (Cobertura or coverage.py format)
- `root` (Path, optional): Repository root path (default: auto-detect from xml_path)

**Returns**:
- `dict`: Coverage map with structure:
  ```python
  {
      "relative/path/file.py": {
          "covered_lines": [1, 2, 5, 10],  # Line numbers with hits > 0
          "percent": 0.75  # Coverage percentage [0.0, 1.0]
      },
      ...
  }
  ```

**Raises**:
- `FileNotFoundError`: If xml_path doesn't exist
- `ET.ParseError`: If XML is invalid

**Example**:
```python
from pathlib import Path
from scripts.space_traversal.coverage_ingest import parse_coverage_xml_to_map

# Parse coverage file
xml_path = Path("coverage.xml")
cov_map = parse_coverage_xml_to_map(xml_path)

# Access coverage data
for file, data in cov_map.items():
    print(f"{file}: {data['percent']:.1%} coverage")
    print(f"  Covered lines: {len(data['covered_lines'])}")

# Get specific file coverage
if "src/example.py" in cov_map:
    percent = cov_map["src/example.py"]["percent"]
    print(f"example.py has {percent:.1%} coverage")
```

---

#### `write_coverage_map(out_path, cov_map)`

Write coverage map to JSON file.

**Parameters**:
- `out_path` (Path): Output file path
- `cov_map` (dict): Coverage map dictionary

**Returns**:
- None

**Side Effects**:
- Creates parent directories if needed
- Writes JSON file with indent=2

**Example**:
```python
from pathlib import Path
from scripts.space_traversal.coverage_ingest import (
    parse_coverage_xml_to_map,
    write_coverage_map
)

# Parse and write
cov_map = parse_coverage_xml_to_map(Path("coverage.xml"))
write_coverage_map(Path("audit_artifacts/coverage_map.json"), cov_map)
```

---

## dup_similarity Module

**Location**: `scripts/space_traversal/dup_similarity.py`

### Functions

#### `duplication_ratio_token_similarity(evidence_files, file_cache, threshold=0.7, max_pairwise=1000, max_tokens_per_file=1000)`

Compute duplication ratio using token-based Jaccard similarity.

**Parameters**:
- `evidence_files` (list[str]): List of file paths to compare
- `file_cache` (dict[str, str]): Mapping of file paths to content strings
- `threshold` (float, optional): Similarity threshold [0.0, 1.0] (default: 0.7)
  - Files with Jaccard similarity ≥ threshold are considered duplicates
- `max_pairwise` (int, optional): Maximum pairwise comparisons (default: 1000)
  - Deterministically samples pairs if evidence_files > sqrt(max_pairwise)
- `max_tokens_per_file` (int, optional): Maximum tokens per file (default: 1000)
  - Truncates token sets if file has more tokens

**Returns**:
- `float`: Duplication ratio in [0.0, 1.0]
  - 0.0 = no duplicates
  - 1.0 = all files are duplicates
  - Ratio = (number of duplicate pairs) / (total pairs checked)

**Algorithm**:
1. Tokenize each file (normalize, split, truncate)
2. Compute Jaccard similarity for pairs: J(A,B) = |A ∩ B| / |A ∪ B|
3. Mark pairs with J ≥ threshold as duplicates
4. Return duplicate_pairs / total_pairs

**Example**:
```python
from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

# File evidence
evidence = ["file1.py", "file2.py", "file3.py"]

# File content cache
cache = {
    "file1.py": "def foo(): pass\ndef bar(): pass",
    "file2.py": "def foo(): return 42",  # Similar to file1
    "file3.py": "class Baz: pass"       # Different
}

# Compute duplication
ratio = duplication_ratio_token_similarity(
    evidence,
    cache,
    threshold=0.7,
    max_pairwise=1000,
    max_tokens_per_file=1000
)

print(f"Duplication ratio: {ratio:.2%}")  # e.g., "33.33%"
# 1 pair (file1, file2) out of 3 pairs checked

# Adjust sensitivity
ratio_strict = duplication_ratio_token_similarity(
    evidence, cache, threshold=0.9  # More strict
)
ratio_lenient = duplication_ratio_token_similarity(
    evidence, cache, threshold=0.5  # More lenient
)
```

---

#### `estimate(evidence_files, repo_root)`

Simple estimate of duplication using path-based heuristic (fallback).

**Parameters**:
- `evidence_files` (list[str]): List of file paths
- `repo_root` (Path): Repository root path

**Returns**:
- `float`: Duplication ratio in [0.0, 1.0]

**Note**: This is a simplified estimator. Use `duplication_ratio_token_similarity` for accurate results.

**Example**:
```python
from pathlib import Path
from scripts.space_traversal.dup_similarity import estimate

evidence = ["tests/test_a.py", "src/a.py", "tests/test_b.py"]
repo_root = Path("/path/to/repo")

ratio = estimate(evidence, repo_root)
print(f"Estimated duplication: {ratio:.2%}")
```

---

## Integration with Audit Pipeline

### Coverage Augmentation Integration

**audit_runner.py** calls `discover_and_parse_coverage` in Stage S4:

```python
# In audit_runner.py, stage_scoring()
from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

# Discover and parse coverage
cov_map = discover_and_parse_coverage(cfg, artifacts_dir)

# Use in scoring
if cov_map and file in cov_map:
    coverage_percent = cov_map[file]["percent"]
    test_score = max(baseline_score, coverage_percent)
```

### Token-Similarity Integration

**audit_runner.py** uses `duplication_ratio_token_similarity` for consistency scoring:

```python
# In audit_runner.py, compute_consistency_score()
from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

heuristic = cfg.get("scoring", {}).get("dup", {}).get("heuristic", "simple")

if heuristic == "token_similarity":
    dup_ratio = duplication_ratio_token_similarity(
        evidence_files,
        file_cache,
        threshold=cfg.get("scoring", {}).get("dup", {}).get("threshold", 0.7),
        max_pairwise=cfg.get("scoring", {}).get("dup", {}).get("max_pairwise", 1000),
        max_tokens_per_file=cfg.get("scoring", {}).get("dup", {}).get("max_tokens_per_file", 1000)
    )
else:
    # Simple heuristic (backward compatible)
    dup_ratio = compute_simple_dup_ratio(evidence_files)

consistency_score = 1.0 - dup_ratio
```

---

## Data Structures

### Coverage Map Schema

```python
{
    "file/path.py": {
        "covered_lines": [1, 2, 3, 10, 15],  # list[int]
        "percent": 0.65                       # float [0.0, 1.0]
    },
    ...
}
```

### Configuration Schema (workflow.yaml)

```yaml
scoring:
  coverage:
    enabled: bool              # Enable coverage augmentation
    xml_patterns: list[str]    # Glob patterns for coverage files
    augment_tests_score: bool  # Use max(baseline, coverage)
  
  dup:
    heuristic: str            # "simple" or "token_similarity"
    threshold: float          # Jaccard threshold [0.0, 1.0]
    max_pairwise: int         # Max comparisons
    max_tokens_per_file: int  # Max tokens per file
```

---

## Error Handling

### coverage_ingest

- Returns `None` on errors (doesn't raise)
- Logs errors to stderr
- Safe to call even if files missing

### dup_similarity

- Returns `0.0` if insufficient data
- Handles empty file content gracefully
- Deterministic sampling for scalability

---

## Performance Characteristics

| Function | Time Complexity | Space Complexity |
|----------|----------------|------------------|
| `parse_coverage_xml_to_map` | O(n) where n = lines in XML | O(m) where m = source files |
| `duplication_ratio_token_similarity` | O(k²) where k = min(files, √max_pairwise) | O(k * tokens_per_file) |

### Performance Tips

1. **Coverage**: Use smaller xml_patterns for faster discovery
2. **Token-similarity**: Reduce max_pairwise for large evidence sets
3. **Memory**: Reduce max_tokens_per_file if memory constrained

---

## See Also

- [Configuration Guide](./Configuration_v1.4.0.md) - How to configure features
- [Troubleshooting Guide](./Troubleshooting_v1.4.0.md) - Common issues
- [Performance Tuning](./Performance_Tuning.md) - Optimization strategies
- [Integration Examples](./Integration_Examples.md) - Usage patterns
