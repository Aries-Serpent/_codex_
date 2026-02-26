# Archive Files

**Purpose**: Consolidated storage for legacy application archives  
**Retention**: Permanent (historical reference)  
**Original Locations**: Various directories in main repository

## Contents

This directory contains archive packages (.zip, .tar.gz) that have been consolidated from various locations in the repository. These represent completed projects, legacy tools, or deprecated applications.

### Files

- `audio_cleaner_beta_v1.zip` - Legacy audio cleaner tool (Beta v1)
  - **Original**: `misc/audio_cleaner_beta_v1.zip`
  - **Status**: Deprecated, replaced by current implementation

- `cognitivecodex-main.zip` - Legacy cognitive codex application
  - **Original**: `misc/cognitivecodex-main.zip`
  - **Status**: Deprecated, functionality integrated into main codebase

- `implement_dependency.zip` - Old dependency implementation archive
  - **Original**: `docs/plans/implement_dependency.zip`
  - **Status**: Completed implementation, archive for reference only

## Usage

### For Historical Reference
Extract and examine legacy implementations:
```bash
# Extract archive
unzip audio_cleaner_beta_v1.zip -d /tmp/review/

# Compare with current implementation
diff -r /tmp/review/ ../../src/[current_location]/
```

### For Recovery
If a legacy feature needs to be restored or referenced:
1. Extract the relevant archive
2. Review implementation
3. Adapt to current codebase standards if needed

## Notes

- Archives in this directory are **read-only** historical references
- Do not add new archives without updating `OFFLOAD_INDEX.md`
- For active archives, see `archive/` in main repository

---
**Offloaded**: 2026-01-26  
**Maintained by**: QA Walkthrough Agent
