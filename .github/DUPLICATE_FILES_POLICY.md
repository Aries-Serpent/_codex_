# Duplicate Files Policy

This document describes the policy for handling duplicate files in the repository. Some duplicates are intentional and expected (e.g., Python package markers), while others Phase 5 require investigation.

## Intentional Duplicates

The following duplicate files are intentional and should be ignored in duplicate detection:

<details>
<summary>📁 Empty __init__.py files (54 files)</summary>

These are Python package markers and are intentionally empty or minimal:

- `./agents/codex_client/__init__.py`
- `./agents/config/__init__.py`
- `./analysis/__init__.py`
- `./interfaces/__init__.py`
- `./models/lora/__init__.py`
- `./src/codex/__init__.py`
- `./src/codex/security/__init__.py`
- `./tests/security/__init__.py`
- And other similar `__init__.py` files throughout the package structure

**Rationale**: Python requires `__init__.py` files to designate directories as packages. Many of these files are intentionally empty or contain only minimal imports.

</details>

<details>
<summary>📁 pytest conftest.py files (3 files)</summary>

Test configuration files with shared fixtures:

- `./tests/eval/conftest.py`
- `./tests/gates/conftest.py`
- `./tests/interfaces/conftest.py`

**Rationale**: Each test directory Phase 5 have its own `conftest.py` file to define pytest fixtures and configuration specific to that test suite. This is a standard pytest pattern.

</details>

## Non-Intentional Duplicates

These files appear to be duplicated and require investigation:

<details>
<summary>⚠️ tokenization/loader.py (2 files)</summary>

- `./src/tokenization/loader.py`
- `./tokenization/loader.py`

**Action Required**: Consolidate to a single location or document the reason for duplication. Having the same module in both locations can lead to confusion and maintenance issues.

**Recommendation**: 
1. Determine which location is the canonical source
2. Remove or redirect the duplicate
3. Update imports throughout the codebase if necessary

</details>

## Detection Guidelines

When running duplicate file detection tools, use the following patterns:

### Files to Ignore
- `**/__init__.py` - Python package markers
- `**/conftest.py` - Pytest configuration files
- `**/.gitkeep` - Directory placeholder files

### Files Requiring Review
Any duplicate files not matching the above patterns should be reviewed to determine if they are:
1. Intentional and should be documented here
2. Unintentional and should be consolidated
3. Legacy files that should be removed

## Updating This Policy

When adding new intentional duplicates:
1. Document the reason in the appropriate section
2. Add detection ignore patterns to `.github/SHIM_INVENTORY.yaml`
3. Ensure the duplication serves a clear purpose

## Related Documentation

- `.github/SHIM_INVENTORY.yaml` - Automated ignore patterns
- `CONTRIBUTING.md` - General contribution guidelines
