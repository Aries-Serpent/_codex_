# Root Folder Organization Guide

**Last Updated:** 2026-02-17 | **Campaign:** Root Folder Cleanup (Stage 4) | **Status:** ✅ Complete

## Overview

This document describes the organized root folder structure for the `_codex_` repository after the root folder cleanup campaign. The reorganization improves discoverability, reduces root clutter, and creates a clear archive structure for historical phase reports.

---

## Root Folder Structure (Post-Cleanup)

```
_codex_/
├── .codex/                          # Codex infrastructure & archived docs
│   ├── ROOT_FOLDER_ORGANIZATION.md  # This document
│   ├── archive/
│   │   ├── README.md
│   │   ├── ARCHIVE_INDEX.md
│   │   └── phases/
│   │       ├── INDEX.md              # Comprehensive phase report index
│   │       ├── PHASE_1_*.md
│   │       ├── PHASE_2_*.md
│   │       ├── PHASE_3_*.md
│   │       ├── PHASE_5_*.md
│   │       ├── PHASE_6_*.md
│   │       ├── PHASE_7A_*.md
│   │       ├── PHASE_8_*.md
│   │       ├── PHASE_9_*.md
│   │       ├── PHASE_B_*.md
│   │       ├── PHASE_D_*.md
│   │       └── WAVE_4_*.md
│   ├── [other infrastructure files]
│   └── [subdirectories by function]
├── docs/                            # Public documentation
│   ├── README.md
│   ├── accountability/
│   ├── archive/
│   ├── cognitive_brain/
│   ├── configuration/
│   ├── phase-9/
│   ├── plans/
│   ├── production/
│   ├── runbooks/
│   └── [26+ subdirectories]
├── README.md                        # Primary project README
├── CONTRIBUTING.md                  # Contributing guide
├── CHANGELOG.md                     # Change history
├── LICENSE                          # License file
├── [Source code directories]        # src/, tests/, etc.
├── [Configuration files]            # pyproject.toml, Dockerfile, etc.
└── [Build artifacts]                # Ignored by .gitignore
```

---

## File Organization Rationale

### Root Folder (Top-Level)

**What stays in root:**
- `README.md` - Project entry point and overview
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Release history and changes
- `LICENSE` - License file
- `pyproject.toml`, `setup.cfg`, `Dockerfile` - Build/config essentials
- Source directories: `src/`, `tests/`, `scripts/`
- Infrastructure-as-code: `.github/`, `.codex/`

**Why this structure:**
- Minimal, essential information at the entry point
- Clear navigation to source code and contribution guidelines
- Historical phase reports moved to `.codex/archive/phases/`
- Reduces cognitive load when exploring the repository

### `.codex/` Directory

**Purpose:** Infrastructure, configuration, and archived documentation for internal operations

**Key subdirectories:**
- `archive/` - Historical documents, completed phases, superseded docs
- `sessions/` - Session logs and session-related artifacts
- `CI_INCIDENTS/` - CI failure tracking and resolution notes
- Configuration files for cognitive brain, agent setup, policies
- Historical notes and deprecated configurations

### `docs/` Directory

**Purpose:** Public-facing documentation for users, developers, and operators

**Key subdirectories:**
- `accountability/` - Reports on work completion and agent performance
- `archive/` - Archived docs superseded by newer versions
- `cognitive_brain/` - Cognitive brain system documentation
- `configuration/` - Configuration guides (Hydra, Omegaconf)
- `phase-9/` - Phase 9 documentation and coordination
- `plans/` - Strategic plans and project roadmaps
- `production/` - Production deployment and operations
- `runbooks/` - Operational runbooks and troubleshooting

---

## Phase Report Archive Structure

### Location

All phase reports are archived in `.codex/archive/phases/` with a comprehensive index.

```
.codex/archive/phases/
├── INDEX.md                                    # Central index (this document)
├── PHASE_1_AGENTS_AUDIT.md
├── PHASE_1_AGENTS_AUDIT.json
├── PHASE_2_TRACK_4_EXECUTION_COMPLETE.md
├── PHASE_2_TRACK_4_QUICK_REFERENCE.md
├── PHASE_2_TRACK_4_REMEDIATION_REPORT.md
├── PHASE_2_TRACK_5_EXECUTION_SUMMARY.txt
├── PHASE_3_REMEDIATION_SUMMARY.md
├── PHASE_3_SECURITY_COMPLETION.md
├── PHASE_3_TEAM_4_*.md (6 files)
├── PHASE_3_TEAM_5_CACHING_GUIDE.md
├── PHASE_3_TEAM_5_WEEK1_SUMMARY.md
├── PHASE_3_TEAM_6_WEEK1_SUMMARY.md
├── PHASE_5_LANE_5.2B_EXECUTION_COMPLETE.md
├── PHASE_6_DELIVERABLES_SUMMARY.md
├── PHASE_6_FILE_MANIFEST.md
├── PHASE_6_FINAL_REPORT.md
├── PHASE_6_WAVE_4_STAGING_COMPLETE.md
├── PHASE_7A_LANE_4_COMPLETION_SUMMARY.txt
├── PHASE_7A_TASK3_FINAL_SUMMARY.txt
├── PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt
├── PHASE_7A_WAVE3_LANE31_COMPLETION_REPORT.md
├── PHASE_8_1_FINAL_VERIFICATION_REPORT.txt
├── PHASE_9_GITHUB_PAGES_SYNC_REPORT.md
├── PHASE_B_LANE_4_DELIVERABLES.txt
├── PHASE_B_LANE_4_EXECUTIVE_SUMMARY.md
├── PHASE_B_LANE_4_REPORT.md
├── PHASE_B_TRACK_1_COMPLETION.txt
├── PHASE_D_LANE_11_ML_VALIDATION_REPORT.md
├── PHASE_D_LANE_11_ML_VALIDATION_RESULTS.json
├── MUTATION_TESTING_PHASE_B_DAY3_SUMMARY.md
└── WAVE_4_*.md (2 files)
```

### Why Archive Phases?

1. **Reduces Root Clutter** - 36 phase report files moved from root to organized structure
2. **Improves Discoverability** - Centralized index makes finding reports easier
3. **Maintains Accessibility** - All files remain easily accessible via `.codex/archive/phases/INDEX.md`
4. **Preserves History** - Complete audit trail and historical context maintained
5. **Follows Best Practices** - Infrastructure files live in `.codex/`

---

## Migration Notes

### What Was Moved

- **36 phase/wave report files** from root to `.codex/archive/phases/`
- Files include: Phase 1-9, B, D, Wave 4 completion reports and summaries
- File types: `.md` (Markdown), `.txt` (Text), `.json` (JSON)

### What Stayed in Root

- `CHANGELOG.md` - Release history (not phase-specific)
- `CITATION.cff` - Citation metadata
- `CODEX_MANIFEST.json` - Package manifest
- `README.md` - Primary documentation
- Configuration and build files

### Breaking Changes

**None.** All links have been updated to reference the new locations.

### How to Find Old Phase Reports

1. **Quick Reference:** Use `.codex/archive/phases/INDEX.md` to find any phase report
2. **Search:** `grep -r "PHASE_X" .codex/archive/phases/`
3. **Direct Access:** `.codex/archive/phases/[FILENAME]`

---

## File Location Reference Guide

### Common Task: Find Phase X Report

**Example: Find Phase 3 Team 4 reports**

```bash
# Option 1: Browse the index
cat .codex/archive/phases/INDEX.md

# Option 2: List all Phase 3 files
ls .codex/archive/phases/PHASE_3_*

# Option 3: Search for specific topic
grep -r "Team 4" .codex/archive/phases/
```

### Documentation Links

**Path update pattern:**
```
Old: /PHASE_X_*.md → New: /.codex/archive/phases/PHASE_X_*.md
```

**Examples:**
- Old: `../PHASE_3_REMEDIATION_SUMMARY.md` 
- New: `../../.codex/archive/phases/PHASE_3_REMEDIATION_SUMMARY.md`

Or use absolute references from root:
- Better: `.codex/archive/phases/PHASE_3_REMEDIATION_SUMMARY.md`

### Key Directories

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `docs/` | Public documentation | API refs, user guides, developer docs |
| `docs/accountability/` | Agent accountability reports | AGENT_ACCOUNTABILITY_REPORT.md |
| `docs/archive/` | Superseded/historical docs | Old versions, deprecated guidance |
| `docs/phase-9/` | Phase 9 coordination docs | Standups, dashboards, action plans |
| `docs/cognitive_brain/` | Cognitive brain system | System design, prompts, status |
| `.codex/` | Infrastructure & internal docs | Agent config, internal guidance |
| `.codex/archive/` | Internal historical docs | Old accountability reports, versions |
| `.codex/archive/phases/` | Phase completion reports | All phase 1-9, B, D, Wave 4 reports |

---

## Accessing Files from Different Locations

### From `docs/` markdown files:

```markdown
<!-- Reference to phase archive -->
See [Phase 3 Remediation](../../.codex/archive/phases/PHASE_3_REMEDIATION_SUMMARY.md)

<!-- Or use absolute path from repo root -->
See [Phase 3 Remediation](.codex/archive/phases/PHASE_3_REMEDIATION_SUMMARY.md)
```

### From README.md or root-level files:

```markdown
<!-- Use relative path to .codex -->
See [Phase Reports](.codex/archive/phases/INDEX.md)
```

### In Python/shell scripts:

```python
# From repository root
phase_reports_dir = pathlib.Path(".codex/archive/phases")
phase_3_report = phase_reports_dir / "PHASE_3_REMEDIATION_SUMMARY.md"
```

---

## Related Documentation

- **Phase Reports Index:** [`.codex/archive/phases/INDEX.md`](.codex/archive/phases/INDEX.md)
- **Archive Overview:** [`.codex/archive/README.md`](.codex/archive/README.md)
- **Main Documentation:** [`docs/`](../../docs/)
- **Contribution Guidelines:** [`CONTRIBUTING.md`](../../CONTRIBUTING.md)

---

## Campaign Details

**Campaign Name:** Root Folder Cleanup

**Stage:** 4 - Update References

**Objective:** Reorganize root folder by moving phase reports to structured archive

**Files Moved:** 36 phase/wave report files

**Files Affected:** ~15 documentation files with path updates

**Impact:** Non-breaking (all links updated)

**Status:** ✅ Complete

---

## Questions & Support

For questions about file locations or the new organization:

1. Check the [Phase Reports Index](.codex/archive/phases/INDEX.md)
2. Review this guide's File Location Reference section
3. Check `.codex/archive/README.md` for general archive info
4. Open an issue in the repository

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-17  
**Maintained By:** Root Folder Cleanup Campaign Team
