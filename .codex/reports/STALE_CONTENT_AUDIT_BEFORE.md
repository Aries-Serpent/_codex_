# STALE CONTENT AUDIT - BEFORE REMEDIATION
**Date**: 2026-07-17  
**Campaign**: GitHub Pages v0.2.0 Production Readiness  
**Lane**: REMEDIATION LANE B - Stale Content Removal

## Executive Summary

**Total Stale Markers Found**: 121 instances across 69 documentation files

### Marker Breakdown
| Marker Type | Count | Status |
|-------------|-------|--------|
| PLACEHOLDER marker | 59 | Remove from templates, ignore in placeholder files |
| under construction | 49 | Remove markers and move files to roadmap |
| coming soon | 6 | Remove or move to roadmap |
| work in progress | 4 | Remove markers |
| WIP marker | 1 | Remove |
| DRAFT marker | 2 | Remove |
| **TOTAL** | **121** | |

## Critical Files (Production Documentation)

### API Documentation - MUST COMPLETE or REMOVE

**Status: Placeholder Documents (4 files)**
- `docs/api/PYTHON_SDK.md` - Incomplete SDK reference
- `docs/api/TRAINING_API.md` - Incomplete API docs
- `docs/api/SERVING_API.md` - Incomplete API docs  
- `docs/api/TROUBLESHOOTING.md` - Incomplete solutions

**Decision**: These files should be REMOVED for v0.2.0 (not in critical path)

### Admin Documentation - MOVE to ROADMAP

**Status: Placeholder Documents (3 files)**
- `docs/admin/CLOUD_DEPLOYMENT.md` - Planned for v0.3.0
- `docs/admin/DISASTER_RECOVERY.md` - Planned for v0.3.0
- `docs/admin/KUBERNETES_DEPLOYMENT.md` - Planned for v0.3.0

**Decision**: MOVE to docs/roadmap/ with v0.3.0 label

### Guide Files - BATCH REMOVAL

**Status: 28 Advanced Guide Files with "under construction"**
- All prefixed with `ADVANCED_*` (22 files)
- Plus: `ENSEMBLE_GUIDE.md`, `FINE_TUNING_GUIDE.md`, `FINOPS_GUIDE.md`, `PERFORMANCE_OPTIMIZATION.md`

**Decision**: MOVE to docs/roadmap/ with v0.3.0 label

### Template Files - KEEP (instructional, not user-facing)

**Status: 47 PLACEHOLDER markers in templates (59 total, 47 in templates)**
- `docs/templates/Migration_CLIHardening.md` (12 PLACEHOLDERs)
- `docs/templates/Migration_PythonFileRelocation.md` (18 PLACEHOLDERs)
- `docs/templates/Planning_IntentValidation.md` (17 PLACEHOLDERs)

**Decision**: KEEP these - PLACEHOLDERs are instructional markers for template users

## Files to DELETE (Empty After Marker Removal)

Based on review, the following files are primarily placeholder markers:
1. `docs/api/PYTHON_SDK.md`
2. `docs/api/TRAINING_API.md`
3. `docs/api/SERVING_API.md`
4. `docs/api/TROUBLESHOOTING.md`
5. `docs/tutorials/WEB_DASHBOARD_TUTORIAL.md`
6. `docs/business/BUSINESS_VALUE_GUIDE.md`
7. `docs/examples/SDK_EXAMPLES.md`
8. All 28 "under construction" guide files

**Total**: ~35 files to delete

## Files to MOVE to Roadmap (30+ files)

All "under construction" guide and admin files planned for future releases.

## Files to EDIT (Remove Markers Only)

Approximately 20 files with markers in meaningful content:
- `docs/CONTRIBUTING.md` (4 PLACEHOLDERs)
- `docs/MCP_SETUP_GUIDE.md` (1 "coming soon")
- `docs/INTERPRETABILITY_GUIDE.md` (1 "coming soon")
- `docs/index.md` (1 PLACEHOLDER in guidance)
- Status update and planning files (keep content, remove markers)

## Remediation Strategy

### Phase 1: Template Files (KEEP)
- Do NOT remove PLACEHOLDERs from template files
- These are instructional for users following the template

### Phase 2: Production Files - DELETE (8 files)
- Remove completely empty "under construction" placeholder documents
- Files: `PYTHON_SDK.md`, `TRAINING_API.md`, `SERVING_API.md`, `TROUBLESHOOTING.md`, `WEB_DASHBOARD_TUTORIAL.md`, `BUSINESS_VALUE_GUIDE.md`, `SDK_EXAMPLES.md`, + 1 more

### Phase 3: Production Files - MOVE to ROADMAP (30+ files)
- Create `docs/roadmap/` directory
- Create `docs/roadmap/v0.3.0-planned.md` index
- Move all "under construction" advanced guides
- Move admin deployment guides
- Move example section placeholders

### Phase 4: Production Files - EDIT (20 files)
- Remove stale markers from meaningful content
- Keep the content, just remove the status markers
- Examples: `CONTRIBUTING.md`, `MCP_SETUP_GUIDE.md`, etc.

### Phase 5: Navigation Updates
- Update `mkdocs.yml` to remove deleted files
- Add new "Roadmap" section if files moved
- Verify all nav entries point to existing files

## Expected Outcomes

| Metric | Target | Notes |
|--------|--------|-------|
| Stale markers removed | 121 → 0 | (47 template placeholders remain) |
| Files deleted | ~8 | Empty placeholder documents |
| Files moved to roadmap | ~30 | Under construction advanced guides |
| Files edited | ~20 | Marker removal from content |
| Production doc status | ✅ Clean | All stale markers removed |
| Navigation status | ✅ Verified | mkdocs.yml updated |

## Next Steps

1. Review this audit with team
2. Approve deletion/move strategy
3. Execute Phase 2-5 removals
4. Verify mkdocs.yml navigation
5. Generate REMOVAL_LOG and VERIFICATION reports
6. Commit changes with audit trail

---
**Status**: BLOCKING → Ready for Phase 2 execution
