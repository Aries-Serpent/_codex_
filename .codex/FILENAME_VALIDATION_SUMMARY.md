# Cross-Platform Filename Validation Summary

**Date**: 2026-01-23
**Status**: ✅ **VALIDATION COMPLETE**
**Report**: `.codex/audit-phase2-filenames.md`

---

## Quick Reference

### Windows-Illegal Characters
| Character | Name | Example |
|-----------|------|---------|
| `<` | Less than | `file<name>` |
| `>` | Greater than | `file<name>` |
| `:` | Colon | `file:name` |
| `"` | Quote | `file"name` |
| `/` | Slash | `file/name` |
| `\` | Backslash | `file\name` |
| `\|` | Pipe | `file\|name` |
| `?` | Question mark | `file?name` |
| `*` | Asterisk | `file*name` |

### ✅ SAFE Characters for Filenames
- Hyphens: `file-name`
- Underscores: `file_name`
- Dots: `file.name`
- Numbers: `file123`
- Parentheses: `file(name)` — **ACTUALLY NOT SAFE** - Don't use!
- Brackets: `file[name]` — **ACTUALLY NOT SAFE** - Don't use!

---

## Critical Finding

### 🔴 One file uses parentheses (Windows-illegal on some systems)
```
reports/_codex_status_update-(2025-12-06).md
```
**Action**: Rename to `_codex_status_update_2025-12-06.md`

---

## Key Issues Summary

### Issue 1: `.isoformat()` in Code (1,394 instances)
**Severity**: ⚠️ Medium (when used in filenames)

**Problem**: 
```python
datetime.now().isoformat()  
# → 2026-01-23T14:30:45.123456+00:00  (contains : and +)
```

**Solution**:
```python
from codex.utils.path_utils import windows_safe_timestamp
windows_safe_timestamp(fmt='iso')  
# → 2026-01-21T14-30-45Z  (safe!)
```

### Issue 2: `strftime('%H:%M:%S')` (255 instances)
**Severity**: 🔴 High (always unsafe)

**Problem**:
```python
datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
# → 2026-01-23T14:30:45Z  (contains colons)
```

**Solution**: 
```python
# Option A: Use utility
from codex.utils.path_utils import windows_safe_timestamp
windows_safe_timestamp(fmt='iso')
# → 2026-01-21T14-30-45Z

# Option B: Replace colons
datetime.now().strftime('%Y-%m-%dT%H-%M-%SZ')
# → 2026-01-23T14-30-45Z

# Option C: Use compact format
datetime.now().strftime('%Y%m%d_%H%M%S')
# → 20260123_143045
```

---

## Available Utilities

### `src/codex/utils/path_utils.py`

#### `windows_safe_timestamp(dt=None, fmt='iso', include_seconds=True)`
```python
# Three safe formats:
windows_safe_timestamp(fmt='iso')        # → 2026-01-21T14-30-45Z
windows_safe_timestamp(fmt='compact')    # → 20260121_143045
windows_safe_timestamp(fmt='readable')   # → 2026-01-21-14-30-45-UTC
```

#### `sanitize_filename(filename: str) -> str`
```python
# Replaces < > : " / \ | ? * with underscores
sanitize_filename("report<2026-01-23>.json")
# → "report_2026-01-23_.json"
```

---

## Validation Scripts

### 1. Pre-Commit Hook
```bash
scripts/remediation/fix_windows_filenames_phase1.sh
```
**Purpose**: Rename files with problematic characters
**Run**: `bash scripts/remediation/fix_windows_filenames_phase1.sh`

### 2. Validation Script
```bash
scripts/remediation/validate_windows_filenames.py
```
**Purpose**: Check repository for compliance
**Run**: `python scripts/remediation/validate_windows_filenames.py`

---

## Implementation Roadmap

### Phase 1 (24h SLA) - CRITICAL
- [ ] Rename file with parentheses
- [ ] Commit and push to main
- [ ] Verify Windows CI passes

### Phase 2 (1 week) - HIGH PRIORITY
- [ ] Audit 10+ file generation scripts
- [ ] Replace `.isoformat()` with `windows_safe_timestamp()`
- [ ] Replace `%H:%M:%S` patterns
- [ ] Add unit tests

### Phase 3 (2 weeks) - AUTOMATION
- [ ] Install pre-commit hook globally
- [ ] Add to CI/CD pipeline
- [ ] Document in CONTRIBUTING.md

---

## Code Review Checklist

When reviewing code that handles filenames:
- [ ] No `.isoformat()` in filename contexts
- [ ] No `%H:%M:%S` in strftime for filenames
- [ ] No Windows-illegal characters in hardcoded names
- [ ] Uses `windows_safe_timestamp()` or safe format
- [ ] Uses `sanitize_filename()` for user input

---

## References

- **Full Audit Report**: `.codex/audit-phase2-filenames.md`
- **Utilities**: `src/codex/utils/path_utils.py`
- **Tests**: `tests/utils/test_path_utils.py`
- **Microsoft Docs**: [Windows Filename Restrictions](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)

---

## Questions?

Contact: Copilot Cross-Platform Filename Validator
Last Updated: 2026-01-23

