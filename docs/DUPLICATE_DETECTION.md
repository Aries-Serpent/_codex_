# Duplicate Detection Inventory

Comprehensive duplicate detection system for identifying and managing code duplication across the entire codebase.

## Features

### Detection Modes

1. **Exact Detection** (SHA256-based)
   - Finds byte-for-byte identical files
   - Fast and reliable
   - Useful for identifying true duplicates

2. **Normalized Detection** (Comment/whitespace-agnostic)
   - Removes comments and normalizes whitespace
   - Detects structural duplicates
   - Language-specific normalizers (Python, JavaScript)

3. **AST Detection** (Function/class level)
   - Analyzes code at AST level
   - Identifies duplicate functions and methods
   - Reports exact line numbers
   - Cross-file detection

4. **Semantic Detection** (MinHash fuzzy matching)
   - Finds semantically similar code
   - Token-based similarity
   - Adjustable threshold
   - Clusters similar files

### Integration Features

- **SHIM Inventory Cross-Reference**: Identifies which duplicates are tracked in `.github/SHIM_INVENTORY.yaml`
- **Git Metadata**: Enriches results with git blame and churn metrics
- **Multiple Output Formats**: YAML, JSON, CSV, and Markdown reports

## Installation

```bash
# The tool is part of the repository
# No additional installation needed
```

## Usage

### Basic Scan

```bash
# Scan current directory with all modes
python tools/duplicate_inventory.py .
```

### Specific Detection Modes

```bash
# Exact duplicates only
python tools/duplicate_inventory.py . --modes exact

# Multiple modes
python tools/duplicate_inventory.py . --modes exact,normalized,ast

# All modes
python tools/duplicate_inventory.py . --modes exact,normalized,ast,semantic
```

### Output Options

```bash
# Specify output directory
python tools/duplicate_inventory.py . --output-dir ./dup_analysis

# Specific output formats
python tools/duplicate_inventory.py . --formats yaml,json,markdown
```

### Configuration

```bash
# Use configuration file
python tools/duplicate_inventory.py . --config .dupinv.yaml
```

## Output Files

After running, the following files are generated:

- `SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml` - Complete machine-readable inventory
- `supplemental_duplicates.json` - JSON format
- `supplemental_duplicates.csv` - Flat summary table
- `supplemental_duplicates.md` - Human-readable report with:
  - Executive summary
  - SHIM inventory status
  - High-priority duplicates NOT in SHIM inventory
  - Detailed duplicate groups with recommendations

## Report Sections

### Executive Summary
- Total files scanned
- Duplicate groups found
- Detection modes used
- Scan duration

### SHIM Inventory Status
- Duplicates in SHIM inventory
- Whitelisted duplicates
- **High Priority**: Duplicates NOT in SHIM inventory ⚠️

### Duplicate Groups
- Grouped by detection type
- Confidence level (high/medium/low)
- Suggested actions (refactor/consolidate/whitelist)
- File paths and line numbers
- Similarity scores
- Git metadata (author, churn)
- SHIM recommendations

## Integration with SHIM Inventory

The tool automatically cross-references detected duplicates with `.github/SHIM_INVENTORY.yaml`:

- ✅ **In Inventory & Whitelisted**: These are tracked and approved
- ⚠️ **In Inventory but Not Whitelisted**: Need attention
- 🚨 **NOT in Inventory**: High priority - should be reviewed immediately

## Configuration File

Create `.dupinv.yaml` in your repository:

```yaml
# Exclusion patterns
exclude_patterns:
  - "*/vendor/*"
  - "*/node_modules/*"
  - "*/test_fixtures/*"

# Respect .gitignore
respect_gitignore: true

# Detection thresholds
ast_similarity_threshold: 0.85
semantic_threshold: 0.75

# Normalization options
normalize_identifiers: false
```

## Examples

### Find All Exact Duplicates

```bash
python tools/duplicate_inventory.py . \
  --modes exact \
  --output-dir ./exact_dups
```

### Deep Analysis (All Modes)

```bash
python tools/duplicate_inventory.py . \
  --modes exact,normalized,ast,semantic \
  --output-dir ./full_analysis \
  --formats all
```

### Quick SHIM Check

```bash
python tools/duplicate_inventory.py . \
  --modes exact \
  --formats markdown
  
# Check supplemental_duplicates.md for SHIM status
```

## Understanding the Output

### Confidence Levels

- **High**: Strong evidence of duplication (exact match, identical AST)
- **Medium**: Likely duplication (similar structure, same function names)
- **Low**: Possible duplication (semantic similarity below threshold)

### Suggested Actions

- **refactor**: Extract to shared module/function
- **consolidate**: Merge duplicate files
- **whitelist**: Add to SHIM_INVENTORY.yaml if intentional
- **vendorize**: Mark as vendored/third-party code
- **ignore**: False positive or acceptable duplication

## Git Metadata

When available, each duplicate includes:

- **Top Author**: Primary contributor (via git blame)
- **Author Email**: Contact information
- **Churn (90 days)**: Number of recent commits
- **File Age**: Days since first commit (optional)

This helps prioritize refactoring efforts based on:
- Code ownership
- Active development areas
- Stability of duplicates

## Performance

- **Exact detection**: Very fast (seconds for large repos)
- **Normalized detection**: Fast (handles comments/whitespace)
- **AST detection**: Moderate (parses Python AST)
- **Semantic detection**: Slower (MinHash computation)

For large repositories (>10,000 files), consider:
- Running specific modes separately
- Using exclude patterns
- Increasing similarity thresholds

## Troubleshooting

### "No duplicates found"

- Check exclude patterns
- Lower similarity thresholds
- Try different detection modes

### "Git metadata not available"

- Ensure you're in a git repository
- Check that `git` command is available
- Git operations Phase 5 timeout for large files

### "Performance issues"

- Use `--modes exact` for quick scans
- Add exclusion patterns for large directories
- Increase similarity thresholds

## Contributing

To add new detection modes:

1. Create detector in `tools/dupinv/`
2. Implement `scan()` method returning `List[DuplicateGroup]`
3. Register in `tools/dupinv/core.py`
4. Add tests
5. Update documentation

## License

Part of the _codex_ repository. See repository LICENSE for details.

## Support

For issues or questions:
- Open an issue in the repository
- Check existing SHIM_INVENTORY.yaml for examples
- Review generated markdown reports for guidance
