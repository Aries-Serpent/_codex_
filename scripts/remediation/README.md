# Remediation Scripts

This directory contains scripts for addressing "Split Brain" architecture and import shadowing issues in the _codex_ repository.

## Scripts

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

### verify_conflicts.py
**Purpose**: Detect import shadowing and split-brain conflicts.

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
