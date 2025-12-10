# Space Traversal Audit Pipeline

This directory contains the Copilot Space audit pipeline implementation with enhanced roadmap features.

## Overview

The audit pipeline analyzes repository capabilities and generates maturity scores. It consists of:

1. **audit_runner.py** - Main orchestrator for capability auditing
2. **dup_similarity.py** - Token-similarity duplication detection
3. **coverage_ingest.py** - Coverage XML parsing and ingestion
4. **trend_aggregator.py** - Trend analysis across audit runs

## Recent Enhancements (v1.4.0)

### 1. Token-Similarity Duplication Heuristic

An alternative to the simple stem-based duplication detection using content-aware token similarity.

**Configuration** (in `.copilot-space/workflow.yaml`):

```yaml
scoring:
  dup:
    heuristic: token_similarity  # or "simple" (default)
    threshold: 0.7               # Jaccard similarity threshold
    max_pairwise: 1000           # Cap pairwise comparisons
    max_tokens_per_file: 1000    # Max tokens per file
```

**Features**:
- Deterministic tokenization of file content
- Pairwise Jaccard similarity with configurable threshold
- Bounded comparisons via deterministic sampling
- Backward compatible (defaults to "simple" heuristic)

**API**:

```python
from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

ratio = duplication_ratio_token_similarity(
    evidence_files=["path/to/file1.py", "path/to/file2.py"],
    file_cache={"path/to/file1.py": "content...", "path/to/file2.py": "content..."},
    threshold=0.7,
    max_pairwise=1000,
    max_tokens_per_file=1000
)
```

### 2. Coverage XML Ingestion

Auto-discovers and parses coverage XML files (Cobertura format) to augment test scores.

**Configuration**:

```yaml
scoring:
  coverage:
    enabled: false  # Disabled by default
    xml_patterns:   # Search patterns for coverage files
      - "coverage.xml"
      - ".coverage.xml"
      - "**/coverage.xml"
```

**Features**:
- Auto-discovery of coverage XML files based on patterns
- Robust parsing supporting multiple XML formats
- Generates `coverage_map.json` in artifacts directory
- Integrates with S4 scoring stage to boost test scores

**API**:

```python
from scripts.space_traversal.coverage_ingest import discover_and_parse_coverage

coverage_map = discover_and_parse_coverage(cfg, artifacts_dir)
# Returns: {"path/to/file.py": {"percent": 0.85, "covered_lines": [...], "total_lines": 100}}
```

**CLI Usage**:

```bash
# Standalone usage
python scripts/space_traversal/coverage_ingest.py <coverage.xml>
```

### 3. Trend Aggregation

Aggregates capability scores across multiple audit runs to identify trends.

**Configuration**:

```yaml
trends:
  enabled: false      # Disabled by default
  lookback_days: 30   # Optional: only analyze last N days
```

**Features**:
- Aggregates scores from multiple audit runs
- Identifies improving, declining, and stable capabilities
- Generates markdown and JSON trend reports
- Supports time-based filtering via lookback_days

**CLI Usage**:

```bash
# Generate trend report
python scripts/space_traversal/trend_aggregator.py \
  --artifacts-dir audit_artifacts \
  --reports-dir reports \
  --lookback-days 30 \
  --output audit_artifacts/trends/trend_report.md

# Or via audit_runner stage
python scripts/space_traversal/audit_runner.py stage TRENDS
```

**API**:

```python
from scripts.space_traversal.trend_aggregator import aggregate_trends

trend_data = aggregate_trends(
    artifacts_dir=Path("audit_artifacts"),
    reports_dir=Path("reports"),
    lookback_days=30,
    manifest_paths=None  # Optional explicit manifest paths
)
```

## Backward Compatibility

All new features are **disabled by default** to maintain backward compatibility:

- **Duplication heuristic**: Defaults to `"simple"` (original behavior)
- **Coverage ingestion**: Disabled unless `scoring.coverage.enabled: true`
- **Trend aggregation**: Disabled unless `trends.enabled: true`

Existing audit runs will produce identical results with the default configuration.

## Determinism Guarantees

All features maintain deterministic behavior:

1. **Token similarity**: Deterministic tokenization, sorted ordering, hash-based sampling
2. **Coverage parsing**: Consistent XML traversal, sorted line numbers
3. **Trend aggregation**: Sorted timestamps, stable capability ordering

No randomness, no network calls, bounded reads (MAX_READ_BYTES = 200,000).

## Testing

Comprehensive test coverage is provided:

```bash
# Run all space_traversal tests
pytest tests/space_traversal/ -v

# Individual test suites
pytest tests/space_traversal/test_token_similarity.py -v
pytest tests/space_traversal/test_coverage_enhanced.py -v
pytest tests/space_traversal/test_trend_aggregator.py -v
pytest tests/space_traversal/test_audit_runner_integration.py -v
```

Test coverage:
- 9 tests for token similarity
- 7 tests for coverage ingestion
- 8 tests for trend aggregation
- 6 integration tests

## Usage Examples

### Enable All Features

Update `.copilot-space/workflow.yaml`:

```yaml
scoring:
  dup:
    heuristic: token_similarity
    threshold: 0.7
  coverage:
    enabled: true
    xml_patterns: ["coverage.xml", "htmlcov/coverage.xml"]

trends:
  enabled: true
  lookback_days: 30
```

Then run:

```bash
# Full pipeline with all features
python scripts/space_traversal/audit_runner.py run

# Individual stages
python scripts/space_traversal/audit_runner.py stage S4   # Includes coverage if enabled
python scripts/space_traversal/audit_runner.py stage TRENDS  # Trend analysis
```

### Programmatic Usage

```python
from pathlib import Path
from scripts.space_traversal import audit_runner

# Load config
cfg = audit_runner.load_config()

# Enable features
cfg["scoring"]["dup"] = {"heuristic": "token_similarity"}
cfg["scoring"]["coverage"] = {"enabled": True}
cfg["trends"] = {"enabled": True, "lookback_days": 30}

# Run full pipeline
audit_runner.run_full(cfg)
```

## File Outputs

- `audit_artifacts/coverage_map.json` - Coverage data by file
- `audit_artifacts/trends/trend_report_<timestamp>.md` - Trend analysis (markdown)
- `audit_artifacts/trends/trend_report_<timestamp>.json` - Trend data (JSON)

## Security & Safety

- Offline-only operation (no network calls)
- Bounded file reads (MAX_READ_BYTES = 200KB)
- Deterministic sampling prevents DoS
- No temporary files written outside artifacts_dir/reports_dir

## Future Enhancements

Potential improvements noted for future versions:

- MinHash/LSH for large-scale similarity detection
- Additional coverage formats (e.g., JaCoCo)
- Interactive trend dashboard with charts
- Configurable trend metrics beyond score deltas
