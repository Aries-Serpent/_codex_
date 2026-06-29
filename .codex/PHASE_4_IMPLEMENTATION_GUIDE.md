# PHASE 4.1: Token Utility Refactoring - Implementation Guide

**Campaign**: CODEX_MASTER_KEY  
**Phase**: PHASE 4.1  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Last Updated**: 2026-01-24

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Refactoring Patterns](#refactoring-patterns)
4. [Sample Implementations](#sample-implementations)
5. [Automated Refactoring Scripts](#automated-refactoring-scripts)
6. [Validation & Testing](#validation--testing)
7. [Rollback Procedures](#rollback-procedures)

---

## Overview

### What is Phase 4.1?

Phase 4.1 refactors all Python scripts in the Codex repository to use the centralized token utility library (`scripts/ci/_token_resolver.py`) instead of directly accessing environment variables for token management.

### Why Phase 4.1?

- **Consistency**: All scripts use the same token resolution logic
- **Maintainability**: Single source of truth for token handling
- **Security**: Centralized token scope validation and audit logging
- **Efficiency**: Reduced code duplication across 136+ scripts

### Phase 4.1 Scope

| Metric | Value |
|--------|-------|
| **Total Scripts Analyzed** | 6,432 |
| **Scripts to Refactor** | 136 |
| **Total Lines to Change** | 185 |
| **Estimated Effort** | 68 hours |
| **Refactoring Patterns** | 4 types |

---

## Quick Start

### For Script Maintainers

1. **Find your scripts** in `.codex/PHASE_4_SCRIPT_REFACTORING.json`
2. **Identify the refactoring type** (basic, elevated, inline chain, or hardcoded)
3. **Apply the transformation** using the pattern templates below
4. **Run validation** to ensure functionality preserved
5. **Commit changes** with reference to PHASE_4_SCRIPT_REFACTORING

### For Automated Execution

```bash
# Generate refactoring patches
python3 scripts/ci/phase4_generate_patches.py

# Apply patches (dry-run first!)
python3 scripts/ci/phase4_apply_patches.py --dry-run

# Apply patches (production)
python3 scripts/ci/phase4_apply_patches.py --execute

# Validate all changes
python3 scripts/ci/phase4_validate.py
```

---

## Refactoring Patterns

### Pattern 1: Add Utility Basic (90 scripts)

**When to Use**: Script directly accesses `os.environ.get()` or `os.getenv()` for token without fallback chain

**Before Pattern**:
```python
import os
import subprocess

token = os.getenv('GITHUB_TOKEN')
if not token:
    raise ValueError("GITHUB_TOKEN not set")

result = subprocess.run(
    ['gh', 'api', 'repos/myorg/myrepo'],
    env={**os.environ, 'GH_TOKEN': token},
    capture_output=True
)
```

**After Pattern**:
```python
import os
import subprocess
from scripts.ci._token_resolver import get_token

token, source = get_token()

result = subprocess.run(
    ['gh', 'api', 'repos/myorg/myrepo'],
    env={**os.environ, 'GH_TOKEN': token},
    capture_output=True
)
```

**Implementation Steps**:

1. Add import at top of file:
   ```python
   from scripts.ci._token_resolver import get_token
   ```

2. Replace token retrieval:
   ```python
   # OLD
   token = os.getenv('GITHUB_TOKEN')
   if not token:
       raise ValueError("Token not set")
   
   # NEW
   token, source = get_token()
   ```

3. (Optional) Use token source for logging:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   token, source = get_token()
   logger.info(f"Using token from: {source}")
   ```

### Pattern 2: Replace Inline Chains (44 scripts)

**When to Use**: Script uses `os.environ.get() or os.environ.get() or ...` fallback chains

**Before Pattern**:
```python
import os

# Manual fallback chain
token = (
    os.environ.get('CODEX_MASTER_KEY')
    or os.environ.get('CODEX_BACKUP_KEY')
    or os.environ.get('GH_TOKEN')
    or os.environ.get('GITHUB_TOKEN')
)

if not token:
    raise ValueError("No token available")
```

**After Pattern**:
```python
from scripts.ci._token_resolver import get_token

# Centralized fallback chain
token, source = get_token()
```

**Implementation Steps**:

1. Identify the fallback chain (look for multiple `or` operators)

2. Replace entire chain with single call:
   ```python
   # BEFORE
   token = os.getenv('VAR1') or os.getenv('VAR2') or os.getenv('VAR3') or ''
   
   # AFTER
   token, source = get_token()
   ```

3. Remove manual error handling if redundant:
   ```python
   # REMOVED (utility already validates)
   if not token:
       raise ValueError("No token")
   ```

### Pattern 3: Replace Hardcoded (2 scripts)

**When to Use**: Script contains hardcoded `github.token` or string literal references

**Before Pattern**:
```python
import os
import requests

# Hardcoded token reference
auth_header = f"Authorization: token {os.environ.get('GITHUB_TOKEN', 'github.token')}"

response = requests.get(
    'https://api.github.com/user',
    headers={'Authorization': auth_header}
)
```

**After Pattern**:
```python
import requests
from scripts.ci._token_resolver import get_auth_header

# Use centralized header formatting
response = requests.get(
    'https://api.github.com/user',
    headers={'Authorization': get_auth_header()}
)
```

**Implementation Steps**:

1. Add import:
   ```python
   from scripts.ci._token_resolver import get_auth_header
   ```

2. Replace header construction:
   ```python
   # OLD
   headers = {'Authorization': f'token {token}'}
   
   # NEW
   headers = {'Authorization': get_auth_header(token)}
   ```

---

## Sample Implementations

### Example 1: Basic Script Refactoring

**Original File**: `.codex/ai_agent_toolkit.py`

```python
# BEFORE
import os
import sys

def get_github_token():
    """Get GitHub token from environment."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("ERROR: GITHUB_TOKEN not set")
        sys.exit(1)
    return token

def main():
    token = get_github_token()
    # ... use token ...

if __name__ == '__main__':
    main()
```

```python
# AFTER
import sys
from scripts.ci._token_resolver import get_token, TokenResolutionError

def get_github_token():
    """Get GitHub token from centralized utility."""
    try:
        token, source = get_token()
        return token
    except TokenResolutionError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

def main():
    token = get_github_token()
    # ... use token ...

if __name__ == '__main__':
    main()
```

**Changes**:
- ✅ Import from utility
- ✅ Use `get_token()` instead of `os.getenv()`
- ✅ Handle `TokenResolutionError` properly
- ✅ Maintain existing error handling

### Example 2: Inline Chain Refactoring

**Original File**: `scripts/ci/auto_fix_common_issues.py`

```python
# BEFORE
import os

token = (
    os.environ.get('CODEX_MASTER_KEY')
    or os.environ.get('CODEX_BACKUP_KEY')
    or os.environ.get('GH_TOKEN')
    or None
)

if not token:
    raise RuntimeError("No GitHub token available")

# ... rest of script ...
```

```python
# AFTER
from scripts.ci._token_resolver import get_token

token, source = get_token()

# ... rest of script ...
```

**Changes**:
- ✅ Removed 4-line fallback chain
- ✅ Single centralized call
- ✅ Error handling included in `get_token()`
- ✅ Can optionally log token source: `print(f"Using token from: {source}")`

---

## Automated Refactoring Scripts

### Script 1: Generate Patches

```bash
python3 scripts/ci/phase4_generate_patches.py \
  --input .codex/PHASE_4_SCRIPT_REFACTORING.json \
  --output .codex/PHASE_4_PATCHES/ \
  --type [basic|elevated|chains|hardcoded]
```

### Script 2: Apply Patches (Dry-Run)

```bash
python3 scripts/ci/phase4_apply_patches.py \
  --patches .codex/PHASE_4_PATCHES/ \
  --dry-run
```

### Script 3: Validate Changes

```bash
python3 scripts/ci/phase4_validate.py \
  --files [file1,file2,...] \
  --check-imports \
  --check-functionality \
  --check-tests
```

---

## Validation & Testing

### Pre-Refactoring Checklist

- [ ] All 136 target scripts identified
- [ ] Backups created in `.codex/PHASE_4_BACKUPS/`
- [ ] Test suite runs successfully before changes
- [ ] Token utility library works in current environment

### Post-Refactoring Checklist

- [ ] All imports added correctly
- [ ] All patterns replaced
- [ ] No syntax errors
- [ ] All tests still pass
- [ ] Token resolution works in CI
- [ ] No secrets logged
- [ ] Code review passed

### Validation Script

```bash
# Full validation suite
python3 scripts/ci/phase4_validate.py --full

# Check individual script
python3 scripts/ci/phase4_validate.py --file "scripts/ci/auto_fix_common_issues.py"

# Check all tests pass
pytest tests/ -v
```

---

## Rollback Procedures

### If Something Goes Wrong

1. **Identify failed scripts**:
   ```bash
   python3 scripts/ci/phase4_validate.py --full --show-failures
   ```

2. **Restore from backup**:
   ```bash
   bash scripts/ci/phase4_restore.sh --scripts [list]
   ```

3. **Re-apply with fixes**:
   ```bash
   python3 scripts/ci/phase4_apply_patches.py \
     --files [list] \
     --fix-errors
   ```

4. **Validate again**:
   ```bash
   python3 scripts/ci/phase4_validate.py --full
   ```

---

## Integration with Token Utility

### Available Functions

| Function | Purpose | Usage |
|----------|---------|-------|
| `get_token()` | Get current token with fallback | `token, source = get_token()` |
| `get_token(required_elevated=True)` | Get elevated token only | `token, src = get_token(required_elevated=True)` |
| `get_token_scope(token)` | Detect token scope level | `scope = get_token_scope(token)` |
| `validate_token_scope()` | Check if token has required scopes | `is_valid, msg = validate_token_scope(token, ['repo'])` |
| `get_auth_header()` | Get formatted Authorization header | `header = get_auth_header(token)` |
| `log_token_usage()` | Log token usage for audit | `log_token_usage("Writing repo var")` |

### Error Handling

```python
from scripts.ci._token_resolver import get_token, TokenResolutionError

try:
    token, source = get_token()
except TokenResolutionError as e:
    logger.error(f"Failed to get token: {e}")
    # Fallback or exit
```

---

## Metrics & Reporting

### Track During Refactoring

- Scripts refactored: ___/136
- Lines changed: ___/185
- Errors encountered: ___
- Rollbacks needed: ___
- Tests passing: ___%

### Report After Completion

```bash
python3 scripts/ci/phase4_metrics.py --output .codex/PHASE_4_COMPLETION_REPORT.json
```

---

## FAQ

**Q: Will this break my script?**
A: No. The utility provides the same fallback chain and error handling as the original patterns.

**Q: How do I handle elevated operations?**
A: Use `get_token(required_elevated=True)` and `validate_token_scope()` for scope checking.

**Q: Can I revert individual scripts?**
A: Yes. Backups are stored in `.codex/PHASE_4_BACKUPS/` per script.

**Q: How do I test the changes?**
A: Run the validation script and full test suite before committing.

**Q: Where are the full file lists?**
A: See `.codex/PHASE_4_SCRIPT_REFACTORING.json` for complete categorization.

---

## Next Steps

1. ✅ **Analysis Complete** - All 6,432 scripts analyzed
2. ⏳ **Patches Generated** - Ready for review
3. ⏳ **Apply Patches** - Execute refactoring
4. ⏳ **Validate Changes** - Run test suite
5. ⏳ **Code Review** - Human review of changes
6. ⏳ **Merge to Main** - Promote to production

---

## Contact & Support

For questions about Phase 4.1, refer to:
- `.codex/PHASE_4_SCRIPT_REFACTORING.json` - Detailed analysis
- `.codex/PHASE_4_SCRIPT_REFACTORING.md` - High-level overview
- `scripts/ci/_token_resolver.py` - Token utility library
- GitHub Issues tagged `PHASE_4_REFACTORING`

---

**Report Generated**: 2026-01-24  
**Phase**: PHASE 4.1  
**Campaign**: CODEX_MASTER_KEY
