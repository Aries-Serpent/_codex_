# Remediation Scripts

This directory contains scripts for addressing "Split Brain" architecture, import shadowing, and duplicate detection issues in the _codex_ repository.

## Scripts

### verify_conflicts.py
**Purpose**: Detect import shadowing, split-brain conflicts, and enforce SHIM inventory compliance.

**Status**: ✅ **Fixed and Enhanced** (December 2025)
- Fixed whitelist parsing bug (was causing false positives)
- Added comprehensive test suite (3 tests, all passing)
- Enhanced strict mode with proper SHIM inventory integration

**Usage**:
```bash
# Basic check (legacy mode)
python scripts/remediation/verify_conflicts.py

# Enforce hydra from site-packages
python scripts/remediation/verify_conflicts.py --expect-site-packages

# Allow shadowing without exit code (warn only)
python scripts/remediation/verify_conflicts.py --allow-shadow

# Strict mode: Fail on non-whitelisted duplicates (used by nightly audit)
python scripts/remediation/verify_conflicts.py --mode strict --output audit_artifacts/conflicts.json

# Shim-aware mode: Warn only for whitelisted duplicates
python scripts/remediation/verify_conflicts.py --mode shim-aware
```

**Modes**:
- `legacy` (default): Original behavior - checks for library shadowing and split-brain ambiguity
- `strict`: Fail on any non-whitelisted duplicate module paths (uses `.github/SHIM_INVENTORY.yaml`)
- `shim-aware`: Warn only for whitelisted duplicates from inventory

**Checks** (legacy mode):
1. Hydra library shadowing (critical)
2. Split-brain architecture detection
3. Module path conflicts

**Checks** (strict mode):
1. Duplicate module paths
2. SHIM inventory whitelist validation
3. Returns exit code 0 only if all duplicates are whitelisted

### consolidate_configs.py ✨ NEW
**Purpose**: Consolidate duplicate configuration files following canonical structure.

**Usage**:
```bash
# Dry-run (preview changes)
python scripts/remediation/consolidate_configs.py --dry-run

# Verify files exist
python scripts/remediation/consolidate_configs.py --verify-only

# Generate SHIM inventory entries
python scripts/remediation/consolidate_configs.py --generate-shim

# Generate migration guide
python scripts/remediation/consolidate_configs.py --generate-guide

# Execute consolidation
python scripts/remediation/consolidate_configs.py --execute
```

**Features**:
- Consolidates flat `conf/` to hierarchical `conf/{training,data,experiment}/`
- Consolidates `configs/` to singular `config/`
- Validates file identity before removal
- Generates SHIM inventory entries for migration tracking
- Creates detailed migration guide

### consolidate_modules.py ✨ NEW
**Purpose**: Consolidate duplicate Python modules by removing duplicates and updating imports.

**Status**: ✅ **Executed Successfully**
- Removed `scripts/analysis/` (consolidated to `tools/dupinv/`)
- Removed `tools/revert_or_restore(other).py`
- Removed `codex_ml/_package_main.py` (kept src/ version)

**Usage**:
```bash
# Dry-run (preview changes)
python scripts/remediation/consolidate_modules.py --dry-run

# Execute consolidation
python scripts/remediation/consolidate_modules.py --execute
```

**Features**:
- Finds all import references using safe pathlib operations
- Updates imports automatically
- Removes duplicate directories/files
- Validates no broken references

### cleanup_root.py
**Purpose**: Sanitize repository root by moving report clutter to archive.

**Usage**:
```bash
# Dry-run (preview only)
python scripts/remediation/cleanup_root.py --dry-run

# Execute cleanup
python scripts/remediation/cleanup_root.py --yes
```

**Targets**: `*_REPORT.md`, `*_SUMMARY.md`

**Destination**: `reports/archive/`

## Duplicate Detection System ✨ NEW

See **[docs/DUPLICATE_DETECTION.md](../../docs/DUPLICATE_DETECTION.md)** for complete documentation.

### Quick Start
```bash
# Run duplicate detection scan
python tools/duplicate_inventory.py . --modes exact,normalized,ast,semantic

# Scan with specific modes
python tools/duplicate_inventory.py . --modes exact --output-dir ./results

# Generate all output formats
python tools/duplicate_inventory.py . --formats yaml,json,csv,markdown
```

### Detection Modes
1. **Exact**: SHA256-based file duplicate detection
2. **Normalized**: Comment/whitespace-agnostic matching
3. **AST**: Function and class level duplicate detection
4. **Semantic**: MinHash-based fuzzy matching with clustering

### Integration Features
- **SHIM Cross-Reference**: Identifies duplicates NOT in `.github/SHIM_INVENTORY.yaml`
- **Git Metadata**: Enriches findings with blame, churn, and age metrics
- **Multi-Format Output**: YAML, JSON, CSV, and Markdown reports

### Continuous Monitoring
Weekly GitHub Actions workflow available at:
`.github/workflows/duplicate-detection-weekly.yml`

## Related Documentation

- **Duplicate Detection**: [docs/DUPLICATE_DETECTION.md](../../docs/DUPLICATE_DETECTION.md)
- **SHIM Inventory**: [.github/SHIM_INVENTORY.yaml](../../.github/SHIM_INVENTORY.yaml)
- **Remediation Plans**: [.codex/duplicate_analysis_full/](../../.codex/duplicate_analysis_full/)
- **Implementation Status**: [.github/prompts/duplicate_detection_inventory/](../../.github/prompts/duplicate_detection_inventory/)

## Testing

Run remediation script tests:
```bash
# Test verify_conflicts.py
python -m pytest tests/scripts/test_verify_conflicts.py -v

# Test duplicate detection system
python -m pytest tests/test_exact_detection.py tests/test_normalize.py tests/test_ast_detection.py tests/test_semantic_detection.py tests/test_shim_integration.py -v
```

## Recent Updates (December 2025)

### Whitelist Parsing Fix ✅
- Fixed bug causing 8 false positive violations in nightly audit
- Whitelist now correctly parsed from `.github/SHIM_INVENTORY.yaml`
- Added comprehensive test suite (3 tests)
- Script returns exit code 0 when all duplicates are whitelisted

### Module Consolidation ✅
- Removed `scripts/analysis/` duplicate modules
- Consolidated to `tools/dupinv/` as canonical location
- All imports validated, no broken references
- 6 duplicate files eliminated total

### Configuration Audit ✅
- Identified 12 duplicate configuration files
- Created consolidation script with migration plan
- SHIM entries prepared for migration tracking

### Duplicate Detection System ✅
- Complete 4-mode detection system operational
- 1,332 duplicate groups identified in baseline scan
- 217 refactoring tickets created with detailed plans
- Continuous monitoring workflow configured

## Support

For issues or questions:
- Check [docs/DUPLICATE_DETECTION.md](../../docs/DUPLICATE_DETECTION.md) for troubleshooting
- Review SHIM inventory for whitelist guidance
- See remediation tickets in `.codex/duplicate_analysis_full/`
2. Training module split-brain
3. Tokenization module split-brain
4. Models module split-brain

**Checks** (strict/shim-aware modes):
1. Duplicate module paths (legacy vs canonical)
2. Whitelist validation against `.github/SHIM_INVENTORY.yaml`
3. Library shadowing (yaml, hydra)

**Exit Codes**:
- 0: Pass
- 1: Structural risks detected (legacy) or non-whitelisted duplicates found (strict)
- 2: Import check failed

**Output**:
When using `--output`, generates a JSON file with findings:
```json
{
  "duplicates": [...],
  "whitelisted": [...],
  "violations": [...],
  "mode": "strict",
  "library_shadowing": {...}
}
```

### analyze_legacy_usage.py
**Purpose**: Scan codebase for legacy imports that should be refactored.

**Usage**:
```bash
# Scan all relevant directories
python scripts/remediation/analyze_legacy_usage.py

# Scan only repository root
python scripts/remediation/analyze_legacy_usage.py --root-only

# Include tests directory (default: included)
python scripts/remediation/analyze_legacy_usage.py --include-tests
```

**Output**: `reports/legacy_import_usage.csv`

**CSV Format**:
```csv
module,full_import,file,line
hydra,hydra.core,src/module.py,42
training,training.engine,src/app.py,15
```

## Integration

These scripts integrate with the audit workflow:

```bash
# Full remediation workflow
make space-remediation  # Preview cleanup
make space-verify       # Verify conflicts and generate import report
make space-test         # Run validation tests
```

## Makefile Targets

- `make space-remediation`: Dry-run cleanup
- `make space-verify`: Run verify_conflicts.py and analyze_legacy_usage.py
- `make space-test`: Run validation test suite

## CI Integration

The CI workflow (`.github/workflows/space-audit.yml`) runs these scripts automatically:

- **On PR**: Fast audit + conflict verification + legacy import report
- **On push to main**: Full audit + all verifications

## Acceptance Criteria

**Zero Root Imports**: No imports from root modules in `src/` code
**Test Parity**: CI passes with PYTHONPATH restricted to `src/`
**Shadowing Resolution**: `hydra` resolves to site-packages
**Split-Brain Elimination**: Only one version of each module importable

## Troubleshooting

### Hydra Shadowing

**Issue**: Local `hydra/` directory shadows PyPI package

**Solution**:
```bash
# Option 1: Rename
git mv hydra config_legacy

# Option 2: Move to src
git mv hydra src/codex_conf
```

### Split-Brain Ambiguity

**Issue**: Both `training` and `src.training` are importable

**Solution**:
1. Review `reports/legacy_import_usage.csv`
2. Refactor imports to use `src.` prefix
3. Add deprecation warnings to root modules
4. Eventually remove root modules

### High Legacy Import Count

**Issue**: Many legacy imports found

**Solution**:
1. Prioritize refactoring by usage count
2. Start with critical modules (hydra)
3. Use automated refactoring tools where possible
4. Update documentation and examples

## Documentation

- **Convergence_Runbook.md**: Step-by-step remediation procedures
- **Usage_Guide.md**: Audit workflow integration
- **Traversal_Workflow.md**: Pipeline architecture

## See Also

- `scripts/space_traversal/detectors/structure_integrity.py`: Detector for split-brain issues
- `tests/validation/test_shadowing.py`: Automated shadowing test
- `.copilot-space/workflow.yaml`: Audit pipeline configuration
