# Repository Archive & Offload Index

**Last Updated**: 2026-06-22  
**Total Archived Files**: 109  
**Storage Reduction**: 1.5 MB moved from docs/archive/

---

## Archive Categories

### Historical Phases (docs/archive/phases/)
Archived phase completion reports and session summaries from Phases 1-20.
- **Files**: 30+
- **Size**: ~500 KB
- **Retention**: Permanent
- **Access**: Historical reference only

**Files**:
- PHASE_*.md - Phase completion reports
- SESSION_COMPLETION_*.md - Session summaries
- CONTINUATION_PROMPT_*.md - Phase handoff prompts

### Pull Request Reports (docs/archive/pr_reports/)
Archived PR completion reports and analysis summaries.
- **Files**: 7
- **Size**: ~200 KB
- **Retention**: Permanent
- **Access**: PR reference and historical tracking

**Files**:
- PR_*.md - PR-specific reports
- CHANGELOG_PR*.md - Changelog extracts

### Validation & Analysis (docs/archive/validation/)
CI/CD failure analysis, validation reports, and resolution summaries.
- **Files**: 5
- **Size**: ~150 KB
- **Retention**: Permanent
- **Access**: CI troubleshooting reference

**Files**:
- CI_CD_*.md - CI/CD analysis and fixes
- PR_*.md - PR validation reports
- INDEX.md - Category index

### Session Reports (docs/archive/session_reports/)
Archived session completion and status reports.
- **Files**: 6
- **Size**: ~100 KB
- **Retention**: Permanent
- **Access**: Historical session tracking

**Files**:
- COMPLETION_SUMMARY.md
- FINAL_STATUS_REPORT*.md
- SESSION_*.md

### Prompts & Continuations (docs/archive/prompts/)
Archived Copilot continuation prompts and session handoff documents.
- **Files**: 5
- **Size**: ~80 KB
- **Retention**: Permanent
- **Access**: Session history and continuation patterns

**Files**:
- COPILOT_CONTINUATION_*.md
- PR_CONTINUATION_*.md

### Project Completion (docs/archive/completion/)
Project and security work completion summaries.
- **Files**: 3
- **Size**: ~50 KB
- **Retention**: Permanent
- **Access**: Work completion verification

**Files**:
- AUDIT_COMPLETION_SUMMARY.md
- PR_*.md
- SECURITY_*.md

### Merged READMEs (docs/archive/merged_readmes/)
Archived merged or consolidated README files.
- **Files**: 3
- **Size**: ~30 KB
- **Retention**: Archive
- **Access**: Historical documentation versions

### Root-Level Archive (docs/archive/)
Core planning and analysis documents.
- **Files**: 22+
- **Size**: ~600 KB
- **Key Documents**:
  - INDEX.md - Archive index
  - README.md - Archive guide
  - MASTER_IMPLEMENTATION_PLAN.md
  - COMPREHENSIVE_GAP_ANALYSIS.md
  - PRODUCTION_READINESS_CERTIFICATION.md

---

## How to Access Archived Files

### Quick Reference
```bash
# List all archived files by category
ls -la docs/archive/phases/
ls -la docs/archive/pr_reports/
ls -la docs/archive/validation/

# Search for specific archived document
grep -r "search-term" docs/archive/ --include="*.md"

# View archived plan phase
cat docs/plans/archive/PHASE2_COMPLETE_SESSION_SUMMARY_FINAL.md
```

### Finding Specific Content

1. **By Phase**: Check `docs/archive/phases/`
2. **By PR**: Check `docs/archive/pr_reports/`
3. **By Session**: Check `docs/archive/session_reports/`
4. **By Topic**: Use grep across categories

---

## Restoration Policy

All archived files are **read-only** and available for reference. To restore an archived file to active use:

1. Copy from `docs/archive/` to appropriate active directory
2. Update all cross-references
3. Add to active index/README
4. Create PR for review

---

## Size Breakdown

| Category | Files | Size | Status |
|----------|-------|------|--------|
| Phases | 30+ | 500 KB | ✅ Archived |
| PR Reports | 7 | 200 KB | ✅ Archived |
| Validation | 5 | 150 KB | ✅ Archived |
| Session Reports | 6 | 100 KB | ✅ Archived |
| Prompts | 5 | 80 KB | ✅ Archived |
| Completion | 3 | 50 KB | ✅ Archived |
| Merged READMEs | 3 | 30 KB | ✅ Archived |
| Root Docs | 22+ | 600 KB | ✅ Archived |
| Misc | 6+ | 100 KB | ✅ Archived |
| **TOTAL** | **109** | **1.5 MB** | **✅ Complete** |

---

## Maintenance Schedule

- **Review Frequency**: Quarterly
- **Cleanup**: Remove files >2 years old or marked for deletion
- **Updates**: Add new completed phase/PR reports monthly
- **Verification**: Check links and integrity monthly

---

## Related Documentation

- [Plans Archive](../docs/plans/archive/) - Completed project plans
- [Archive Index](../docs/archive/INDEX.md) - Detailed archive index
- [Repository Health Dashboard](.codex/repository_health/DASHBOARD.md) - Current metrics
