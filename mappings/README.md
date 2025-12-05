# Import Refactor Mappings

This directory contains mapping configurations for the AST-based import refactor tool.

## Shared Mapping (All Batches)

All batches use the same core mapping defined in `shared_mappings.json`:
- `training` → `src.training`
- `tokenization` → `src.tokenization`
- `models` → `src.modeling`
- `hydra` → `config_legacy`

## Batch Strategy

Batches are differentiated by:
1. **File selection** (via dry-run analysis and priority)
2. **Batch size** (number of files per commit: 5-20)
3. **Target directories** (scripts/ vs cli/ vs tests/)

Rather than different mappings, batches focus on different subsets of files to:
- Keep changes reviewable (small commits)
- Enable rollback per batch
- Validate incrementally

## Usage

```bash
# All batches can use the shared mapping
python scripts/remediation/refactor_imports.py \
  --mapping mappings/shared_mappings.json \
  --dry-run --limit 200

# Apply with batch size control
python scripts/remediation/refactor_imports.py \
  --mapping mappings/shared_mappings.json \
  --apply --batch-size 10 --limit 50
```

## Historical Note

`batch1_mappings.json` and `batch2_mappings.json` were created as separate files for documentation purposes but contain identical mappings. They can be consolidated to `shared_mappings.json` for maintainability.
