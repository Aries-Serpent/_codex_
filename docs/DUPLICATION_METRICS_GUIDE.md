# Duplication Metrics Guide

## Overview

The Duplication Metrics system provides automated detection, measurement, and tracking of code duplication in Python projects. It includes token-based detection via pylint integration, dual storage (JSON + SQLite), and comprehensive CLI commands for CI/CD integration.

## Features

- **Automated Detection**: Token-based duplication detection using pylint
- **Accurate Metrics**: Overlap-aware ratio calculation with file-level tracking
- **Dual Storage**: JSON files for human readability + SQLite for historical queries
- **CLI Integration**: Three commands (check, report, compare) for various workflows
- **CI/CD Ready**: Exit codes, thresholds, and baseline comparison
- **Configurable**: Adjustable minimum lines, trivial pattern filtering, severity levels

## Quick Start

### Basic Duplication Check

```bash
# Check current directory
codex duplication check

# Check specific directory
codex duplication check src/

# Check with custom threshold (fail if > 15%)
codex duplication check --threshold=0.15

# Save results to file
codex duplication check --output=duplication.json
```text

### Generate Detailed Report

```bash
# Generate JSON report
codex duplication report --output=report.json

# Generate text report
codex duplication report --format=text --output=report.txt

# Save to database
codex duplication report --save-db --output=report.json
```text

### Compare Against Baseline

```bash
# Compare with baseline
codex duplication compare current.json --baseline=baseline.json

# Fail if increased by more than 10%
codex duplication compare current.json --baseline=baseline.json --threshold-increase=0.10
```text

## Installation

### Dependencies

```bash
# Required for duplication detection
pip install pylint

# Already included in codex
pip install click
```text

### Verification

```bash
# Test CLI availability
codex duplication --help

# Run a quick check
codex duplication check --help
```text

## CLI Commands

### `codex duplication check`

Check code for duplicates and calculate duplication ratio.

**Usage:**
```bash
codex duplication check [PATH] [OPTIONS]
```text

**Arguments:**
- `PATH`: Directory to scan (default: current directory)

**Options:**
- `--min-lines INTEGER`: Minimum lines to consider as duplicate (default: 4)
- `--threshold FLOAT`: Fail if ratio exceeds this value (default: 0.1)
- `--output PATH`: Save results to JSON file

**Examples:**
```bash
# Basic check with defaults
codex duplication check

# Check specific directory
codex duplication check src/codex

# Higher minimum lines threshold
codex duplication check --min-lines=6

# Strict threshold (fail if > 5%)
codex duplication check --threshold=0.05

# Save results
codex duplication check --output=results.json

# All options combined
codex duplication check src/ --min-lines=6 --threshold=0.15 --output=scan.json
```text

**Exit Codes:**
- `0`: Success (ratio within threshold)
- `1`: Failure (ratio exceeds threshold or error occurred)

**Output:**
```text
🔍 Scanning /home/user/project for duplicates...

📊 Duplication Report:
  Total lines: 15,234
  Duplicate lines: 1,523
  Duplication ratio: 10.00%
  Files scanned: 45
  Files with duplicates: 12
  Duplicate blocks: 8

✅ Duplication ratio 10.00% is within threshold 10.00%
```text

---

### `codex duplication report`

Generate detailed duplication report with full block information.

**Usage:**
```bash
codex duplication report [PATH] [OPTIONS]
```text

**Arguments:**
- `PATH`: Directory to scan (default: current directory)

**Options:**
- `--min-lines INTEGER`: Minimum lines to consider as duplicate (default: 4)
- `--format [json|text]`: Output format (default: text)
- `--output PATH`: Output file path (required)
- `--save-db`: Also save to SQLite database

**Examples:**
```bash
# JSON report
codex duplication report --output=report.json

# Text report
codex duplication report --format=text --output=report.txt

# Save to both file and database
codex duplication report --save-db --output=report.json

# Custom scan path
codex duplication report src/ --output=src-report.json
```text

**JSON Output Format:**
```json
{
  "ratio": 0.15,
  "total_lines": 10000,
  "duplicate_lines": 1500,
  "files_scanned": 50,
  "files_with_duplicates": 15,
  "duplicate_blocks": [
    {
      "hash": "abc123...",
      "lines": [100, 110],
      "occurrences": [
        {"file": "module1.py", "start": 100, "end": 110},
        {"file": "module2.py", "start": 200, "end": 210}
      ],
      "severity": "medium",
      "clone_type": "Type-1"
    }
  ],
  "summary": {
    "num_blocks": 8,
    "avg_block_size": 12.5
  }
}
```text

**Text Output Format:**
```text
============================================================
DUPLICATION REPORT
============================================================
Scan path: /home/user/project
Generated: 2025-11-17T14:00:00.000000

SUMMARY
------------------------------------------------------------
Total lines: 10,000
Duplicate lines: 1,500
Duplication ratio: 15.00%
Files scanned: 50
Files with duplicates: 15
Duplicate blocks: 8

DUPLICATE BLOCKS
------------------------------------------------------------

#1 MEDIUM - Type-1
  Lines: 100-110
  Occurrences: 2
    - module1.py:100
    - module2.py:200

#2 HIGH - Type-1
  Lines: 50-65
  Occurrences: 3
    - utils1.py:50
    - utils2.py:75
    - helpers.py:120
```text

---

### `codex duplication compare`

Compare current duplication metrics against baseline.

**Usage:**
```bash
codex duplication compare CURRENT [OPTIONS]
```text

**Arguments:**
- `CURRENT`: Path to current metrics JSON file

**Options:**
- `--baseline PATH`: Baseline JSON file to compare against
- `--threshold-increase FLOAT`: Fail if ratio increased by more than this (default: 0.05)

**Examples:**
```bash
# Compare with baseline
codex duplication compare current.json --baseline=baseline.json

# Custom threshold (fail if increased by > 10%)
codex duplication compare current.json --baseline=baseline.json --threshold-increase=0.10

# Show current metrics only (no baseline)
codex duplication compare current.json
```text

**Exit Codes:**
- `0`: Success (decrease or within threshold increase)
- `1`: Failure (increase exceeds threshold)

**Output with Baseline:**
```text
📊 Duplication Comparison
  Baseline: 12.00%
  Current:  15.00%
  Change:   +3.00% (+25.0%)

❌ Duplication increased by 3.00%, exceeds threshold 2.00%
```text

**Output without Baseline:**
```text
📊 Current Duplication Metrics
  Ratio: 15.00%
  Total lines: 10,000
  Duplicate lines: 1,500

💡 Use --baseline to compare against a previous report
```text

## Python API

### Basic Usage

```python
from pathlib import Path
from codex.metrics.duplication import detect_duplicates, calculate_duplication_ratio
from codex.metrics.storage import MetricStorage

# Detect duplicates
duplicates = detect_duplicates(Path("src/"), min_lines=4)

# Calculate ratio
total_lines = 10000  # Your line counting logic
ratio = calculate_duplication_ratio(duplicates, total_lines)

print(f"Duplication ratio: {ratio.ratio:.2%}")
print(f"Duplicate blocks: {len(ratio.duplicate_blocks)}")

# Save to storage
storage = MetricStorage()
result = storage.save(ratio, commit_sha="abc123")
print(f"Saved with ID: {result['sqlite_id']}")
```text

### Advanced Detection

```python
from codex.metrics.duplication import DuplicationDetector

# Create detector with custom settings
detector = DuplicationDetector(
    min_lines=6,           # Higher threshold
    min_tokens=100,        # Token-based minimum
    ignore_trivial=True,   # Filter imports, empty classes
)

# Detect with pylint
duplicates = detector.detect_with_pylint(
    Path("src/"),
    min_similarity_lines=6,
)

# Inspect results
for block in duplicates:
    print(f"Severity: {block.severity}")
    print(f"Clone type: {block.clone_type}")
    print(f"Occurrences: {len(block.occurrences)}")
    for occ in block.occurrences:
        print(f"  - {occ['file']}:{occ['start']}-{occ['end']}")
```text

### Storage Operations

```python
from codex.metrics.storage import MetricStorage

# Initialize with custom paths
storage = MetricStorage(
    json_dir=Path(".metrics/json"),
    sqlite_path=Path(".metrics/db.sqlite"),
    enable_json=True,
    enable_sqlite=True,
)

# Save metrics
result = storage.save(ratio, commit_sha="def456")
# Returns: {"json_path": "...", "sqlite_id": 123}

# Load latest
latest = storage.load_latest()
print(f"Latest ratio: {latest['ratio']:.2%}")

# Query history
history = storage.query_history(limit=10)
for metric in history:
    print(f"{metric['timestamp']}: {metric['ratio']:.2%}")

# Filter by time
recent = storage.query_history(
    since="2025-01-01T00:00:00Z",
    limit=5,
)
```text

## CI/CD Integration

### GitHub Actions

```yaml
name: Duplication Check

on: [push, pull_request]

jobs:
  duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pylint
      
      - name: Check duplication
        run: |
          codex duplication check --threshold=0.10 --output=duplication.json
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: duplication-report
          path: duplication.json
```text

### GitLab CI

```yaml
duplication_check:
  stage: test
  script:
    - pip install -e .
    - pip install pylint
    - codex duplication check --threshold=0.10 --output=duplication.json
  artifacts:
    paths:
      - duplication.json
    when: always
```text

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: duplication-check
        name: Check code duplication
        entry: codex duplication check --threshold=0.15
        language: system
        always_run: true
        pass_filenames: false
```text

### Baseline Tracking

```bash
#!/bin/bash
# Track duplication over time

# Generate current report
codex duplication report --output=current.json --save-db

# Compare with baseline
if [ -f baseline.json ]; then
    codex duplication compare current.json \
        --baseline=baseline.json \
        --threshold-increase=0.05
fi

# Update baseline if current is better
CURRENT_RATIO=$(jq -r '.ratio' current.json)
BASELINE_RATIO=$(jq -r '.ratio' baseline.json 2>/dev/null || echo "1.0")

if (( $(echo "$CURRENT_RATIO < $BASELINE_RATIO" | bc -l) )); then
    echo "✅ New baseline: $CURRENT_RATIO (was $BASELINE_RATIO)"
    cp current.json baseline.json
fi
```text

## Configuration

### Environment Variables

```bash
# Storage locations
export CODEX_METRICS_JSON_DIR=".metrics/json"
export CODEX_METRICS_SQLITE_PATH=".metrics/duplication.db"

# Detection settings
export CODEX_DUPLICATION_MIN_LINES=4
export CODEX_DUPLICATION_THRESHOLD=0.10
```text

### .codex/config.yaml (future)

```yaml
duplication:
  min_lines: 4
  min_tokens: 50
  ignore_trivial: true
  threshold: 0.10
  storage:
    json_dir: .codex/metrics/json
    sqlite_path: .codex/metrics/duplication.db
```text

## Troubleshooting

### pylint not found

**Problem:**
```text
Failed to check duplicates: pylint not found
```text

**Solution:**
```bash
pip install pylint
```text

### Timeout on large codebases

**Problem:**
```text
pylint timed out scanning /path/to/large/repo
```text

**Solution:**
Scan subdirectories separately:
```bash
for dir in src/*/; do
    codex duplication check "$dir" --output="${dir//\//-}.json"
done
```text

### High false positive rate

**Problem:**
Many trivial code patterns flagged as duplicates.

**Solution:**
1. Increase minimum lines: `--min-lines=6`
2. Trivial filtering is enabled by default (imports, empty classes)
3. Manually exclude generated code directories

### Database locked error

**Problem:**
```text
database is locked
```text

**Solution:**
```bash
# Close other connections to the database
# Or use JSON-only mode
codex duplication report --output=report.json  # Doesn't use --save-db
```text

### Inconsistent results between runs

**Problem:**
Duplication ratio varies slightly between runs.

**Solution:**
This can happen if:
- Files were modified between runs
- Different Python file sets were scanned
- pylint version changed

Ensure consistent environment and file state for reproducible results.

## Best Practices

### 1. Set Realistic Thresholds

```bash
# Start with current state
codex duplication check --output=baseline.json

# Extract ratio
CURRENT=$(jq -r '.ratio' baseline.json)

# Set threshold slightly above current
THRESHOLD=$(echo "$CURRENT + 0.02" | bc)
codex duplication check --threshold=$THRESHOLD
```text

### 2. Track Trends

```bash
# Weekly cron job
0 0 * * 0 codex duplication report --save-db --output=/var/metrics/weekly-$(date +\%Y\%m\%d).json
```text

Query trends:
```python
from codex.metrics.storage import MetricStorage

storage = MetricStorage()
history = storage.query_history(limit=52)  # Last year

for metric in history:
    print(f"{metric['timestamp']}: {metric['ratio']:.2%}")
```text

### 3. Exclude Generated Code

Create `.duplicationignore`:
```text
*_pb2.py
**/migrations/**
**/node_modules/**
**/__pycache__/**
```text

### 4. Focus on High-Severity Blocks

```python
high_severity_blocks = [
    block for block in ratio.duplicate_blocks
    if block.severity == "high"
]

print(f"High-severity duplicates: {len(high_severity_blocks)}")
```text

### 5. CI/CD Gates

```yaml
# Only fail on significant increases
- name: Check duplication
  run: |
    codex duplication check --threshold=0.15  # Absolute limit
    codex duplication compare current.json \
        --baseline=baseline.json \
        --threshold-increase=0.03  # Max 3% increase
```text

## Metrics Explanation

### Duplication Ratio

```text
Duplication Ratio = Duplicate Lines / Total Lines
```text

Where:
- **Duplicate Lines**: Count of lines that appear in duplicate blocks (overlap-aware)
- **Total Lines**: Total lines in all scanned Python files

### Clone Types

- **Type-1**: Exact copies (except whitespace/comments)
- **Type-2**: Syntactic copies (renamed variables/functions)
- **Type-3**: Structural copies (with modifications)
- **Type-4**: Semantic copies (different syntax, same behavior)

Current implementation detects Type-1 clones via pylint.

### Severity Levels

- **Low**: 2 occurrences
- **Medium**: 3-4 occurrences
- **High**: 5+ occurrences

## Limitations

### Current Implementation

- **Python only**: Only scans `.py` files
- **Type-1 clones**: Only detects exact matches (via pylint)
- **No AST-based detection**: Variable renaming not detected
- **No metadata filtering**: Can't filter duplicates by file type or directory

### Future Enhancements

- Multi-language support (JavaScript, Java, etc.)
- AST-based detection for Type-2 and Type-3 clones
- Semantic detection for Type-4 clones (ML-based)
- Metadata filtering and custom ignore patterns
- Visual diff viewer for duplicate blocks
- Integration with code review tools

## Related Documentation

- [Acceptance Criteria Verification](../ACCEPTANCE_CRITERIA_VERIFICATION.md) - Implementation research
- [CLI Documentation](cli.md) - General CLI usage (if exists)
- [Metrics API](api/metrics.md) - API reference (if exists)

## Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Review test examples in `tests/metrics/` and `tests/cli/`
3. Open an issue in the repository

---

**Last Updated:** 2025-11-17  
**Version:** 1.0.0  
**Maintainer:** Codex Team
