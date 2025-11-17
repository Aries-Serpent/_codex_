# Duplication Analyzer - User Guide

## Overview

The Duplication Analyzer provides actionable insights into code duplication across your codebase. It detects duplicate files, identifies refactoring opportunities, and generates comprehensive reports.

## Features

- **Stem-based Detection**: Find files with duplicate names
- **Content-based Detection**: Identify files with identical content (SHA-256)
- **Severity Assessment**: Classify duplication as acceptable/warning/high/critical
- **Actionable Recommendations**: Get specific suggestions for each duplicate group
- **Refactoring Candidates**: Prioritize files for consolidation
- **Multiple Output Formats**: Markdown reports or JSON data

## Installation

No additional dependencies required - uses Python standard library.

## Quick Start

### Command Line Usage

```bash
# Analyze current directory
python tools/duplication_analyzer.py

# Analyze specific directory
python tools/duplication_analyzer.py --root /path/to/project

# Generate report file
python tools/duplication_analyzer.py --output dup_report.md

# JSON output
python tools/duplication_analyzer.py --json --output dup_data.json

# Custom threshold
python tools/duplication_analyzer.py --threshold 0.15
```text

### Programmatic Usage

```python
from pathlib import Path
from tools.duplication_analyzer import DuplicationAnalyzer

# Initialize analyzer
analyzer = DuplicationAnalyzer(
    root_path=Path("."),
    acceptable_ratio=0.10  # 10% acceptable
)

# Run analysis
analysis = analyzer.analyze()

# Print statistics
print(f"Total files: {analysis['stats']['total_files']}")
print(f"Duplication ratio: {analysis['stats']['duplication_ratio']:.2%}")
print(f"Severity: {analysis['stats']['severity']}")

# Get duplicate groups
for group in analysis['duplicate_groups'][:5]:
    print(f"\n{group['stem']}: {group['count']} files")
    print(f"Recommendation: {group['recommendation']}")

# Generate report
report = analyzer.generate_report(Path("report.md"))
```text

## Configuration

### Thresholds

```python
from tools.duplication_analyzer import (
    ACCEPTABLE_DUP_RATIO,  # 0.10 (10%)
    WARNING_DUP_RATIO,     # 0.20 (20%)
    CRITICAL_DUP_RATIO,    # 0.30 (30%)
)

# Custom threshold
analyzer = DuplicationAnalyzer(
    root_path=Path("."),
    acceptable_ratio=0.05  # Stricter: 5%
)
```text

### File Extensions

```python
# Default extensions
extensions = ['.py', '.md', '.yaml', '.yml', '.json', '.txt']

# Analyze only Python files
analysis = analyzer.analyze(extensions=['.py'])

# Analyze all text files
analysis = analyzer.analyze(extensions=['.py', '.md', '.rst', '.txt', '.yaml'])
```text

## API Reference

### DuplicationAnalyzer

#### `__init__(root_path, acceptable_ratio)`

Initialize analyzer.

**Parameters:**
- `root_path` (Path): Root directory to analyze
- `acceptable_ratio` (float): Acceptable duplication ratio (default: 0.10)

#### `analyze(extensions)`

Perform comprehensive analysis.

**Parameters:**
- `extensions` (list[str], optional): File extensions to analyze

**Returns:**
- `dict`: Analysis results with keys:
  - `stats`: Metrics (total_files, duplicate_count, duplication_ratio, severity)
  - `duplicate_groups`: List of duplicate file groups
  - `content_duplicates`: Files with identical content
  - `recommendations`: Actionable recommendations

#### `generate_report(output_path)`

Generate markdown report.

**Parameters:**
- `output_path` (Path, optional): Path to save report

**Returns:**
- `str`: Markdown formatted report

#### `find_refactoring_candidates(min_duplicates)`

Find high-priority refactoring targets.

**Parameters:**
- `min_duplicates` (int): Minimum duplicates to consider (default: 3)

**Returns:**
- `list[dict]`: Refactoring candidates with priority and suggestions

## Understanding Results

### Severity Levels

| Ratio | Severity | Action |
|-------|----------|--------|
| < 10% | Acceptable | Monitor |
| 10-20% | Warning | Review top duplicates |
| 20-30% | High | Plan refactoring |
| > 30% | Critical | Immediate action required |

### Duplicate Groups

Each duplicate group includes:
- `stem`: Filename stem (without extension)
- `count`: Number of duplicate files
- `paths`: List of file paths
- `recommendation`: Specific action to take

### Content Duplicates

Files with identical content (byte-for-byte):
- `hash`: SHA-256 hash (truncated)
- `count`: Number of identical files
- `paths`: List of file paths
- `recommendation`: Deduplication strategy

## Real-World Example

Analyzing the _codex_ repository:

```bash
$ python tools/duplication_analyzer.py --root . --output codex_dup_report.md

# Results:
Total Files: 3,348
Duplicate Count: 718
Duplication Ratio: 21.45% (HIGH)
Duplicate Groups: 248
Content Duplicates: 28
```text

Top duplicate groups:
1. `__init__`: 189 files (package markers - acceptable)
2. `config`: 15 files (different configs - review)
3. `utils`: 8 files (likely candidates for consolidation)

## Refactoring Workflow

### 1. Identify Candidates

```python
candidates = analyzer.find_refactoring_candidates(min_duplicates=3)

for candidate in candidates[:10]:
    print(f"{candidate['stem']}: {candidate['count']} files")
    print(f"Priority: {candidate['priority']}")
    print(f"Suggestion: {candidate['suggestion']}\n")
```text

### 2. Review Duplicates

```bash
# Get detailed report
python tools/duplication_analyzer.py --output review.md

# Review top 10 groups
head -100 review.md
```text

### 3. Consolidate

For Python files:
```python
# Before: 3 separate utils.py files
module1/utils.py
module2/utils.py
module3/utils.py

# After: Single shared module
common/utils.py
# Update imports in module1, module2, module3
```text

For config files:
```yaml
# Before: Duplicate configs
config/dev.yaml
config/staging.yaml
config/prod.yaml  # Much duplication

# After: Use YAML anchors
config/base.yaml    # Shared config
config/dev.yaml     # Extends base
config/staging.yaml # Extends base
config/prod.yaml    # Extends base
```text

### 4. Verify Reduction

```bash
# Re-run analysis
python tools/duplication_analyzer.py

# Compare ratios
# Before: 21.45%
# After: 15.20% (improved!)
```text

## Best Practices

1. **Regular Monitoring**: Run analysis periodically
   ```bash
   # Add to CI/CD
   python tools/duplication_analyzer.py --threshold 0.20 || echo "Warning: High duplication"
   ```

2. **Exclude Expected Duplicates**: Ignore package markers
   ```python
   # Filter __init__ files from results
   real_dups = [
       g for g in analysis['duplicate_groups']
       if g['stem'] != '__init__'
   ]
   ```

3. **Prioritize by Impact**: Focus on high-count duplicates
   ```python
   # Sort by count
   sorted_groups = sorted(
       analysis['duplicate_groups'],
       key=lambda x: -x['count']
   )
   ```

4. **Document Decisions**: Track why duplicates exist
   ```python
   # Add comments explaining legitimate duplicates
   # e.g., "config.py duplicated per-service for isolation"
   ```

5. **Track Over Time**: Monitor trends
   ```bash
   # Save historical data
   python tools/duplication_analyzer.py --json > data/dup_$(date +%Y%m%d).json
   ```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Duplication Check
on: [pull_request]

jobs:
  check-duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Analyze Duplication
        run: |
          python tools/duplication_analyzer.py --threshold 0.25
          if [ $? -ne 0 ]; then
            echo "::warning::Duplication ratio exceeds threshold"
          fi
      - name: Generate Report
        run: python tools/duplication_analyzer.py --output $GITHUB_STEP_SUMMARY
```text

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python tools/duplication_analyzer.py --threshold 0.30
if [ $? -ne 0 ]; then
    echo "Warning: High duplication detected. Consider refactoring."
    echo "Run: python tools/duplication_analyzer.py --output dup_report.md"
fi
```text

## Troubleshooting

### High Duplication in __init__.py

This is normal - Python packages require `__init__.py` files:
```python
# Filter them out
analysis = analyzer.analyze()
real_duplicates = [
    g for g in analysis['duplicate_groups']
    if g['stem'] not in ['__init__', '__pycache__']
]
```text

### Content Duplicates in Tests

Test fixtures may legitimately duplicate:
```python
# Review context before removing
for dup in analysis['content_duplicates']:
    if any('test' in path for path in dup['paths']):
        print(f"Test duplicate: {dup['paths']}")
        # Verify if consolidation makes sense
```text

### Large Codebases

For very large projects, analyze incrementally:
```python
# Analyze by directory
for subdir in ['src', 'tests', 'tools']:
    analyzer = DuplicationAnalyzer(Path(subdir))
    result = analyzer.analyze()
    print(f"{subdir}: {result['stats']['duplication_ratio']:.2%}")
```text

## Examples

See `tests/tools/test_duplication_analyzer.py` for comprehensive examples.

## Related Tools

- **dup_similarity.py**: Token-based similarity (future integration)
- **detector_duplication.py**: Audit detector for duplication ratio

## Exit Codes

- `0`: Success, duplication within threshold
- `1`: Duplication exceeds threshold

## Support

For issues or questions:
- Check test suite: `tests/tools/test_duplication_analyzer.py`
- Review source: `tools/duplication_analyzer.py`
- Run with `--help` for CLI options
