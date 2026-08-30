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

### Temporary Outputs (historical + active bundle archive)
- `DAY_3_QA_VALIDATION_READY.txt` — Session marker file
- Session/temporary artifacts
- Active sandbox patch bundles live under `.codex/sandbox-bundles/sandbox-transfer/` and are treated as the canonical repo-owned transfer directory

**Location**: historical content remains in `temp-outputs/`; active transfer bundles use `.codex/sandbox-bundles/sandbox-transfer/`

## Archive Statistics
- **Total files moved**: 55+
- **Archive date**: 2026-01-26
- **Retention**: Permanent (reference only)

## Classification Decisions for Follow-Up Migration

The first-wave root hygiene pass intentionally preserves canonical repository metadata at the root while relocating non-canonical generated and historical artifacts into a structured archive.

| Classification | Decision | Examples | Target |
|---|---|---|---|
| Root canonical metadata | Keep at root | `README.md`, `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, `CODEX_MANIFEST.json`, `pyproject*.toml`, `requirements*.txt`, `package.json`, `mkdocs.yml`, `Cargo.toml` | repository root |
| History / phase artifacts | Archive | `PHASE_*.md`, `*_REPORT.md`, `*_SUMMARY.md`, gate/compliance notes | `.codex/archive/root-consolidation/phase-history/` |
| Generated validation & security payloads | Archive | `workflow-*.json`, `telemetry_report.json`, `sbom*.json`, `semgrep-*.json`, checksum files | `.codex/reports/` |
| Temporary / scratch outputs | Archive | `fix_*.py`, `phase_7_*_test*.py`, session markers, draft reports | `.codex/archive/root-consolidation/temp-outputs/` (historical) and `.codex/sandbox-bundles/sandbox-transfer/` (active transfer bundle root) |
| Structured operational code | Relocate to domain folders | validation runners, metrics scripts, bootstrap scripts | `scripts/validation/`, `scripts/ops/`, `scripts/bootstrap/` |
| Manual review / deferred | Hold for follow-up | `secrets.txt`, any ad hoc `json/` data, isolated test harnesses that may still be referenced by CI | follow-up migration review |

### Canonical root guardrail
This pass does not relocate repository identity files or project metadata. Only generated history, temporary scratch files, and non-canonical reporting artifacts were moved to archive destinations.

### Retrieval
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
