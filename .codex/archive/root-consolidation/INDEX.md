# Root Consolidation Archive Index

**Created**: 2026-01-26  
**Purpose**: Consolidate phase history, reports, and temporary files from repository root

## Contents

### Phase History (52+ files)
- `PHASE_*.md` — Phase tracking and execution documents
- `GATE_*.md` — Gate completion reports
- Summary and report files from phase lifecycle

**Location**: `phase-history/`

### Deprecated/Governance (2+ files)
- `.codex/archive/deprecated/ENERGY_CONVERSION_AGENT_DEPRECATION.md` — Deprecated agent archive documentation
- `.codex/archive/deprecated/GOOGLE_HOME_SCRIPT_AGENT_DEPRECATION.md` — Deprecated agent archive documentation

**Location**: `deprecated-reports/`

### Temporary Outputs (1+ files)
- `DAY_3_QA_VALIDATION_READY.txt` — Session marker file
- Session/temporary artifacts

**Location**: `temp-outputs/`

## Archive Statistics
- **Total files moved**: 55+
- **Archive date**: 2026-01-26
- **Retention**: Permanent (reference only)

## Retrieval
To find archived files:
```bash
# Browse by category
ls -la .codex/archive/root-consolidation/phase-history/

# Search archive
grep -r "pattern" .codex/archive/root-consolidation/

# Restore from git history
git log --follow -- <original_path>
```

## See Also
- `.codex/PHASE_8_2_CLEANUP_STRATEGY.md` — Cleanup rationale
- `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` — Archive structure standards
