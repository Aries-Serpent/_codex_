# Documentation Link Validation TODO

**Purpose**: Track broken documentation links discovered during Phase 8 consolidation.

**Created**: 2024-12-30  
**Status**: 🟡 Pending Validation  
**Priority**: Medium

---

## 📊 Summary

**Total Links Checked**: ~500+  
**Broken Links Found**: 256  
**Validated**: 0  
**Fixed**: 0

---

## 🔍 Known Broken Links

### Category: Missing Target Files

Many links reference files that don't exist:
- `docs/modules/model_registry.md` (referenced from MODEL_REGISTRY.md)
- `docs/CODE_STYLE.md` (referenced from PR_TEMPLATE_COMPREHENSIVE.md)
- `docs/TESTING.md` (referenced from PR_TEMPLATE_COMPREHENSIVE.md)
- `AGENTS.md` (referenced from PR_TEMPLATE_COMPREHENSIVE.md)
- `../ACCEPTANCE_CRITERIA_VERIFICATION.md` (multiple references)

### Category: Moved/Renamed Files

Links that Phase 5 point to renamed or relocated files:
- `./decision_records/0001-record-architecture-decisions.md`
- `../CODEBASE_AUDIT_2025-08-26_203612.md`
- `./README_ROOT.md`

---

## ✅ Validation Process

### Step 1: Automated Detection
```bash
# Run link checker
python scripts/maintenance/check_doc_links.py

# Output: List of broken links with sources
```

### Step 2: Manual Triage
For each broken link:
1. Determine if target file exists elsewhere (moved/renamed)
2. Check if link is obsolete (can be removed)
3. Verify if target needs to be created

### Step 3: Fix Strategy
- **Moved files**: Update link to new location
- **Obsolete links**: Remove or add deprecation notice
- **Missing files**: Create stub or redirect

### Step 4: Validation
```bash
# Re-run checker
python scripts/maintenance/check_doc_links.py

# Verify all links valid
```

---

## 🎯 Action Plan

### Phase 1: Quick Wins (High-Impact)
- [ ] Fix links in MASTER_INDEX.md
- [ ] Fix links in cognitive brain (Map, Dashboard, Roadmap)
- [ ] Fix links in README files (root, src, agents, scripts, docs)

### Phase 2: Template Fixes
- [ ] Update PR_TEMPLATE_COMPREHENSIVE.md links
- [ ] Fix template references
- [ ] Verify workflow links

### Phase 3: Deep Validation
- [ ] Validate all API documentation links
- [ ] Check all guide cross-references
- [ ] Verify runbook links

### Phase 4: Automated Monitoring
- [ ] Create pre-commit hook for link validation
- [ ] Add CI check for broken links
- [ ] Set up monthly link validation report

---

## 🚧 Blockers

**None currently** - All tooling available, just needs execution time.

---

## 📝 Notes

- Many broken links are in older documentation that may need archiving
- Some links point to files that were intentionally removed
- Consider adding a "deprecated" marker to obsolete docs instead of deleting

---

## 🔗 Related

- [Master Index](../MASTER_INDEX.md)
- [Documentation Standards](../MASTER_INDEX.md#documentation-standards)
- [Maintenance Process](../MASTER_INDEX.md#maintenance)

---

**Next Steps**: Schedule Phase 1 quick wins for next session.
