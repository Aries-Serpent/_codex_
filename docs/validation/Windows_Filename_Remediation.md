# [Docs]: Windows Filename Compatibility Remediation

> **Generated:** 2026-01-21 | **Author:** mbaetiong  
> 🧠 **Roles:** [Primary: Platform Validator], [Secondary: CI Orchestrator] ⚡ **Energy:** 5

## Problem Statement

Windows filesystems prohibit certain characters in filenames, including colons (`:`). ISO-8601 timestamps like `2026-01-21T14:30:45Z` contain colons and cause Git checkout failures on Windows runners.

**Root Cause:** Colons in ISO-8601 timestamps (e.g., `22:25Z`) are illegal on Windows filesystems.

**Impact:** `git checkout` fails on Windows runners during CI/CD, blocking the multi-platform pipeline.

**Failing Job:** [Performance Regression Detection #60974199331](https://github.com/Aries-Serpent/_codex_/actions/runs/21196037604/job/60974199331)

## Solution Summary

1. **Utility Function:** `codex.utils.path_utils.windows_safe_timestamp()`
2. **Sanitization:** `codex.utils.path_utils.sanitize_filename()`
3. **Migration Script:** `scripts/remediation/rename_windows_incompatible_files.py`
4. **Validation:** Pre-commit hook + integration tests

## Quick Start

### For New Code

```python
from codex.utils.path_utils import windows_safe_timestamp

# Generate timestamp for filename
timestamp = windows_safe_timestamp(fmt="compact")
filepath = Path(f"reports/status_{timestamp}.json")
```

### For Existing Files

```bash
# Find problematic files
python scripts/remediation/rename_windows_incompatible_files.py --dry-run

# Rename them
python scripts/remediation/rename_windows_incompatible_files.py --execute
```

## Migration Checklist

- [x] Phase 1: Audit completed - all timestamp functions identified
- [x] Phase 2: Utility functions implemented and tested
- [x] Phase 3: Codebase migrated - all functions updated
- [x] Phase 4: Existing files renamed
- [x] Phase 5: Validation passing - tests green, pre-commit active
- [x] Phase 6: Documentation updated

## Testing

```bash
# Run unit tests
pytest tests/utils/test_path_utils.py -v

# Run integration tests
pytest tests/integration/test_cross_platform_filenames.py -v

# Check pre-commit hook
pre-commit run check-windows-filenames --all-files
```

## Timestamp Format Guide

### Available Formats

1. **ISO Format** (`fmt="iso"`):
   - Pattern: `2026-01-21T14-30-45Z`
   - Use case: Log files, audit trails, version tags
   - Example: `audit_2026-01-21T14-30-45Z.json`

2. **Compact Format** (`fmt="compact"`):
   - Pattern: `20260121_143045`
   - Use case: Report files, data exports, backups
   - Example: `report_20260121_143045.csv`

3. **Readable Format** (`fmt="readable"`):
   - Pattern: `2026-01-21-14-30-45-UTC`
   - Use case: Human-readable status updates, debug files
   - Example: `status_2026-01-21-14-30-45-UTC.md`

### Migration Examples

#### Before (❌ Unsafe)
```python
# Creates colons - fails on Windows
timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
filepath = Path(f"reports/status_{timestamp}.json")
# Result: reports/status_2026-01-21T14:30:45Z.json ⚠️ INVALID ON WINDOWS
```

#### After (✅ Safe)
```python
from codex.utils.path_utils import windows_safe_timestamp

# No colons - works on all platforms
timestamp = windows_safe_timestamp(fmt="iso")
filepath = Path(f"reports/status_{timestamp}.json")
# Result: reports/status_2026-01-21T14-30-45Z.json ✅ VALID EVERYWHERE
```

## Rollback Plan

If issues arise, temporarily disable pre-commit hook:

```yaml
# .pre-commit-config.yaml
- id: check-windows-filenames
  # Temporarily disabled - investigating false positives
  exclude: '.*'
```

## Success Criteria

- ✅ All timestamp generation functions use safe patterns
- ✅ No existing files with Windows-illegal characters
- ✅ CI/CD passes on Windows runners
- ✅ Pre-commit hook prevents future violations
- ✅ Integration tests validate end-to-end flow

## Files Modified

### Core Utilities
- `src/codex/utils/path_utils.py` - New utility module
- `tests/utils/test_path_utils.py` - Unit tests

### Migrated Timestamp Functions
- `tools/selection_report.py`
- `tools/generate_status_update.py`
- `tools/codex_seq_runner.py`
- `tools/apply_codex_audit_tasks.py`
- `scripts/codex_ready_task_runner.py`
- `scripts/refresh_requirements_lock.py`

### Remediation Tools
- `scripts/remediation/rename_windows_incompatible_files.py`
- `scripts/remediation/check_windows_filenames.py`

### Integration Tests
- `tests/integration/test_cross_platform_filenames.py`

### Configuration
- `.pre-commit-config.yaml` - Added Windows filename check hook
- `.github/workflows/rust_swarm_ci.yml` - Fixed invalid action version

### Documentation
- `AGENTS.md` - Added cross-platform guidelines
- `docs/validation/Windows_Filename_Remediation.md` - This document

## References

- [Failing CI Job](https://github.com/Aries-Serpent/_codex_/actions/runs/21196037604/job/60974199331)
- [Windows Filename Restrictions (Microsoft Docs)](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
- [AGENTS.md - Cross-Platform Guidelines](../../AGENTS.md#cross-platform-filename-requirements)

## Support

For questions or issues:
- **Critical:** @mbaetiong
- **General:** GitHub Issues
- **Features:** Discussions

---

**Document Status:** ✅ COMPLETE  
**Last Updated:** 2026-01-21  
**Version:** 1.0.0
