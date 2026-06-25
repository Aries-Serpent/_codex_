# Post-Merge Missing Dependencies Install Playbook

**Created**: 2026-06-25T22:26:00Z
**Purpose**: Guide for installing missing optional dependencies when post-merge test collection reveals gaps
**Trigger**: Use after POST_MERGE_COPILOT_SETUP_VALIDATION.md Gate 6 reveals import errors
**Scope**: Addresses known pre-existing missing dependencies (zstandard, sqlalchemy)

---

## Quick Fix (If You Know Test Collection Will Fail)

If you know the test environment is minimal and will miss zstandard/sqlalchemy:

```bash
# Install both missing optional dependencies
pip install zstandard sqlalchemy

# Verify installation
python3 -c "import zstandard; import sqlalchemy; print('✅ Both installed')"

# Re-run test collection
pytest --collect-only --tb=no 2>&1 | tee .codex/post-merge-collection-status.txt
```

---

## Detailed Diagnostic Procedure

### Step 1: Baseline Test Collection (Minimal Environment)
Run this FIRST to see what collection errors exist with minimal deps:

```bash
cd /home/runner/work/_codex_/_codex_

# Collection in current environment (may have missing deps)
echo "=== TEST COLLECTION (Current Environment) ===" >> /tmp/collection_diagnostic.log
pytest --collect-only --tb=short 2>&1 | tee -a /tmp/collection_diagnostic.log

# Count errors
COLLECTION_ERRORS=$(pytest --collect-only --tb=no 2>&1 | grep -c "ERROR\|ImportError\|ModuleNotFoundError" || echo "0")
echo "Collection Errors: $COLLECTION_ERRORS" | tee -a /tmp/collection_diagnostic.log
```

### Step 2: Identify Specific Missing Imports

```bash
# Extract import errors
pytest --collect-only --tb=short 2>&1 | grep -E "ModuleNotFoundError|ImportError" | sort -u | tee .codex/collection-import-errors.txt

# This will show:
# - ModuleNotFoundError: No module named 'zstandard'
# - ModuleNotFoundError: No module named 'sqlalchemy'
# - Or other specific imports
```

### Step 3: Map Errors to Dependencies

Use this table to understand which dependency to install:

| Error Message | Dependency | Install Command | Why It Happens |
|---------------|------------|-----------------|----------------|
| `ModuleNotFoundError: No module named 'zstandard'` | zstandard | `pip install zstandard` | Package in requirements/dev.txt but not core deps |
| `ModuleNotFoundError: No module named 'sqlalchemy'` | sqlalchemy | `pip install sqlalchemy` | Transitive dependency not explicitly installed |
| `ModuleNotFoundError: No module named 'X'` (other) | X | `pip install X` | Unknown optional dep - escalate to team |

### Step 4: Install Missing Dependencies

```bash
# Option A: Install the specific missing package
# If only zstandard is missing:
pip install zstandard

# If only sqlalchemy is missing:
pip install sqlalchemy

# If both are missing:
pip install zstandard sqlalchemy

# Option B: Install full dev environment (all optional deps)
# If many deps are missing, it's faster to install dev extras:
pip install -e '.[dev]'
# This installs everything in [project.optional-dependencies] dev section
```

### Step 5: Verify Installation

```bash
# Test each package independently
python3 -c "import zstandard; print('✅ zstandard OK')" || echo "❌ zstandard FAILED"
python3 -c "import sqlalchemy; print('✅ sqlalchemy OK')" || echo "❌ sqlalchemy FAILED"

# Check versions
python3 -c "import zstandard; print(f'zstandard: {zstandard.__version__}')"
python3 -c "import sqlalchemy; print(f'sqlalchemy: {sqlalchemy.__version__}')"
```

### Step 6: Re-run Test Collection

```bash
# Re-run collection after installing deps
echo "=== TEST COLLECTION (After Installing Missing Deps) ===" >> /tmp/collection_diagnostic.log
pytest --collect-only --tb=short 2>&1 | tee -a /tmp/collection_diagnostic.log

# Count errors again
NEW_COLLECTION_ERRORS=$(pytest --collect-only --tb=no 2>&1 | grep -c "ERROR\|ImportError\|ModuleNotFoundError" || echo "0")
echo "Collection Errors After: $NEW_COLLECTION_ERRORS" | tee -a /tmp/collection_diagnostic.log

# Compare
if [ "$NEW_COLLECTION_ERRORS" -lt "$COLLECTION_ERRORS" ]; then
  echo "✅ IMPROVEMENT: Errors reduced from $COLLECTION_ERRORS to $NEW_COLLECTION_ERRORS"
elif [ "$NEW_COLLECTION_ERRORS" -eq "$COLLECTION_ERRORS" ]; then
  echo "⚠️ UNCHANGED: Still $NEW_COLLECTION_ERRORS errors (not just missing deps)"
else
  echo "❌ REGRESSION: Errors increased from $COLLECTION_ERRORS to $NEW_COLLECTION_ERRORS"
fi
```

### Step 7: Document Results

Create `.codex/POST_MERGE_MISSING_DEPS_RESOLUTION.md` documenting:

```markdown
# Post-Merge Missing Dependencies Resolution

**Date**: [ISO timestamp]
**Environment**: [Python version, pip version]

## Initial Collection Errors
- Count: [X errors]
- Import errors:
  - zstandard: [present/missing]
  - sqlalchemy: [present/missing]
  - [others]: [details]

## Action Taken
- Installed: [package list]
- Command: [exact pip install command]

## After-Installation Collection
- Count: [Y errors]
- Import errors: [list remaining]

## Conclusion
[Installation resolved the missing deps / Errors persist for other reasons / Escalation needed]
```

---

## Decision Tree: When to Install vs. When to Escalate

```
Collection has import errors?
│
├─ NO import errors
│  └─ ✅ DONE (collection is clean)
│
├─ YES, errors include "zstandard"
│  ├─ Is this EXPECTED? (Should be in minimal env?)
│  │  ├─ NO (unexpected) → ⚠️ Escalate (zstandard needed but missing)
│  │  └─ YES (expected) → Install with: pip install zstandard
│  │
│  └─ After install, errors gone?
│     ├─ YES → ✅ RESOLVED
│     └─ NO → Continue to sqlalchemy check below
│
├─ YES, errors include "sqlalchemy"
│  ├─ Is this EXPECTED? (Transitive dep, optional?)
│  │  ├─ NO (unexpected) → ⚠️ Escalate (sqlalchemy needed but missing)
│  │  └─ YES (expected) → Install with: pip install sqlalchemy
│  │
│  └─ After install, errors gone?
│     ├─ YES → ✅ RESOLVED
│     └─ NO → Continue below
│
└─ YES, OTHER import errors (not zstandard/sqlalchemy)
   ├─ Count < 5 errors
   │  ├─ These might be pre-existing
   │  └─ Document, PROCEED to work
   │
   ├─ Count 5-10 errors
   │  ├─ These suggest new regression
   │  └─ Investigate, may need targeted fix
   │
   └─ Count > 10 errors
      ├─ This indicates major regression
      └─ ⚠️ Consider REVERT (See POST_MERGE_REVERSION_PROTOCOL.md)
```

---

## Known Pre-Existing Patterns

### Pattern 1: zstandard Not Available in Minimal Environment
**Symptom**: Collection fails with `ModuleNotFoundError: No module named 'zstandard'`
**Root Cause**: zstandard is in requirements/dev.txt but not in [project.dependencies]
**Fix**: `pip install zstandard`
**Is regression?**: NO - this is expected in minimal environments
**Post-action**: Document as pre-existing, PROCEED

### Pattern 2: sqlalchemy As Transitive Dependency
**Symptom**: Collection fails with `ModuleNotFoundError: No module named 'sqlalchemy'`
**Root Cause**: sqlalchemy is in lock.txt as transitive dependency, not explicitly installed
**Fix**: `pip install sqlalchemy` or `pip install -e .[ast]` (if ast extra includes it)
**Is regression?**: NO - depends on environment setup
**Post-action**: Document as pre-existing, PROCEED

### Pattern 3: Import Guard Missing (Not Dependency Issue)
**Symptom**: Collection fails with import error for a module that SHOULD be optional
**Root Cause**: Test file imports module without try/except guard
**Example**: `import zstandard` without `try: ... except ImportError: ...`
**Fix**: Add import guards to test file, OR install dependency
**Is regression?**: MAYBE - investigate if new code added import
**Post-action**: If new code, fix; if pre-existing, document

---

## Automation Script (Optional)

If running this multiple times, use this script:

```bash
#!/bin/bash
# post-merge-deps-install.sh

set -e

echo "=== Post-Merge Missing Dependencies Diagnostic ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Step 1: Baseline collection
echo "Step 1: Baseline test collection..."
BEFORE=$(pytest --collect-only --tb=no 2>&1 | grep -c "ERROR\|ImportError\|ModuleNotFoundError" || echo 0)
echo "  Collection errors before: $BEFORE"
echo ""

# Step 2: Install known missing deps
echo "Step 2: Installing known missing dependencies..."
pip install -q zstandard sqlalchemy
echo "  ✅ Installed zstandard and sqlalchemy"
echo ""

# Step 3: Verify installation
echo "Step 3: Verifying installation..."
python3 -c "import zstandard; import sqlalchemy; print('  ✅ Both packages imported successfully')" || echo "  ❌ Import failed"
echo ""

# Step 4: Re-run collection
echo "Step 4: Re-running test collection..."
AFTER=$(pytest --collect-only --tb=no 2>&1 | grep -c "ERROR\|ImportError\|ModuleNotFoundError" || echo 0)
echo "  Collection errors after: $AFTER"
echo ""

# Step 5: Report
echo "=== Summary ==="
if [ "$AFTER" -lt "$BEFORE" ]; then
  echo "✅ IMPROVEMENT: Errors reduced from $BEFORE to $AFTER"
  REDUCTION=$((BEFORE - AFTER))
  echo "   Resolved: $REDUCTION errors"
elif [ "$AFTER" -eq "$BEFORE" ]; then
  echo "⚠️ UNCHANGED: Still $AFTER errors"
  echo "   → These are likely not dependency-related"
  echo "   → Investigate specific import errors"
else
  echo "❌ REGRESSION: Errors increased from $BEFORE to $AFTER"
fi

echo ""
echo "Next steps:"
echo "  1. Review: pytest --collect-only --tb=short"
echo "  2. Document in: .codex/POST_MERGE_MISSING_DEPS_RESOLUTION.md"
echo "  3. If issues remain, check: .codex/POST_MERGE_REVERSION_PROTOCOL.md"
```

Save as `.codex/scripts/post-merge-deps-install.sh` and make executable:
```bash
chmod +x .codex/scripts/post-merge-deps-install.sh
```

Run with:
```bash
bash .codex/scripts/post-merge-deps-install.sh
```

---

## References

- Pre-existing environment baseline: .codex/POST_MERGE_ENVIRONMENT_BASELINE.md
- Validation checklist: .codex/POST_MERGE_COPILOT_SETUP_VALIDATION.md
- Reversion protocol: .codex/POST_MERGE_REVERSION_PROTOCOL.md
- Session continuation brief: .codex/POST_MERGE_SESSION_CONTINUATION_BRIEF.md
