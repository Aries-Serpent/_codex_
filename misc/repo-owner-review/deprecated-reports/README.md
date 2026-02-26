# Deprecated Reports

**Purpose**: Historical reports superseded by `.codex/` structure  
**Retention**: 180 iterations (deletion eligible after)  
**Original Location**: `_codex_reports/` directory

## Contents

This directory contains reports from the legacy `_codex_reports/` structure that have been superseded by the new `.codex/` organization. These are preserved temporarily for reference during the transition period.

### Files

- `audit_requirement_mapping.md` - Legacy audit mapping
  - **Superseded by**: `.codex/qa_walkthrough/dependency_audit.json`

- `errors_2025-10-19.md` - Historical error report (Oct 19, 2025)
  - **Superseded by**: Current error tracking in `logs/error_captures.log`

- `errors_2025-11-05.md` - Historical error report (Nov 5, 2025)
  - **Superseded by**: Current error tracking

- `errors_2025-11-12.md` - Historical error report (Nov 12, 2025)
  - **Superseded by**: Current error tracking

- `metric_plugin_duplicates_resolution.md` - Plugin duplicates resolution
  - **Superseded by**: `.codex/decisions/` documentation

- `status_update_2025-10-19.md` - Historical status update
  - **Superseded by**: `.codex/change_log.md` and `.codex/results.md`

## Usage

### For Historical Reference
Review legacy reports to understand past issues:
```bash
# View historical errors
cat errors_2025-*.md

# Compare with current status
diff status_update_2025-10-19.md ../../.codex/results.md
```

### For Migration Verification
Verify all content from legacy reports has been migrated to new structure.

## Migration Status

| Legacy File | New Location | Status |
|------------|--------------|---------|
| `audit_requirement_mapping.md` | `.codex/qa_walkthrough/dependency_audit.json` | ✅ Migrated |
| `errors_*.md` | `logs/error_captures.log` | ✅ Active tracking |
| `metric_plugin_duplicates_resolution.md` | `.codex/decisions/` | ✅ Documented |
| `status_update_*.md` | `.codex/change_log.md` | ✅ Consolidated |

## Cleanup Schedule

- **Review Date**: 2026-07-26 (180 days after offload)
- **Action**: Delete if migration verified complete
- **Process**: Confirm no unique content before deletion

## Notes

- All content has been migrated to new `.codex/` structure
- Preserved for reference during transition period only
- Deletion eligible after 180 iterations

---
**Offloaded**: 2026-01-26  
**Deletion Eligible**: 2026-07-26  
**Maintained by**: QA Walkthrough Agent
