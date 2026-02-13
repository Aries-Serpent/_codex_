# Phase 2: Relocated File References - Action Items

**Status:** 🟡 PARTIALLY COMPLETE (45% done)  
**Last Updated:** 2026-02-13

---

## ✅ Completed

### Phase 2A - High Priority Files (107 fixes)
- [x] CODEBASE_DASHBOARD.md → docs/system/ (18 fixes)
- [x] CODEBASE_COGNITIVE_MAP.md → docs/system/ (8 fixes)
- [x] CODEBASE_AGENCY_POLICY.md → .codex/ (17 fixes)
- [x] ROADMAP.md → docs/ (43 fixes)
- [x] GENESIS_SETUP_GUIDE.md → docs/admin/ (10 fixes)
- [x] OPERATIONAL_GUIDELINES.md → docs/agent/ (11 fixes)

### Phase 2B - Additional Files (6 fixes)
- [x] guides/examples.md → docs/guides/examples.md (2 fixes)
- [x] guides/reasoning_overview.md → docs/status_updates/guides/ (4 fixes)

### Deliverables
- [x] Automated fix scripts created
- [x] Comprehensive reports generated
- [x] 100% validation completed
- [x] Zero-break guarantee maintained

---

## 🔄 Remaining Work (~134 references)

### Category 1: Documentation Files (High Value)

#### Evolution & Planning
- [ ] **EVOLUTION_TIMELINE.md** → docs/evolution/ (7 references)
- [ ] **PLANSET_REGISTRY.md** → docs/evolution/ (7 references)

#### Development Guides  
- [ ] **CODE_STYLE_GUIDE.md** → docs/dev/ (6 references)
- [ ] **TESTING_GUIDE.md** → docs/guides/ (6 references)

#### MCP Integration
- [ ] **PACKAGING_GUIDE.md** → docs/mcp/ (7 references)
- [ ] **QUICK_START.md** → docs/mcp/ (6 references)

#### Architecture
- [ ] **ARCHITECTURE.md** → docs/ARCHITECTURE.md (7 references)
  - Note: Multiple ARCHITECTURE.md files exist; need careful disambiguation

### Category 2: Wiki Files (Medium Value)

- [ ] **Agent-Operations.md** → .codex/wiki/ (9 references)
- [ ] **Genesis-Protocol.md** → .codex/wiki/ (8 references)  
- [ ] **Home.md** → .codex/wiki/ (8 references)

### Category 3: Release Documentation (Medium Value)

- [ ] **RELEASE_RUNBOOK.md** → .codex/release/ (8 references)
- [ ] **PACKAGE_PUBLISHING_GUIDE.md** → .codex/release/ (8 references)

### Category 4: Technical Capabilities (Low-Medium Value)

- [ ] **checkpointing.md** → docs/capabilities/ (10 references)
- [ ] **train_loop.md** → docs/capabilities/ (8 references)
- [ ] **experiment_management.md** → docs/capabilities/ (8 references)

### Category 5: Zendesk Documentation (Low-Medium Value)

- [ ] **ZENDESK_NEWCOMER_GUIDE.md** → docs/zendesk/ (12 references)

### Category 6: Complex Cases (Needs Manual Review)

#### Multiple README.md Files
- [ ] **README.md** disambiguation (30+ broken references)
  - Problem: Many README.md files in different directories
  - Solution: Need to analyze context to determine correct target
  - Locations: config_legacy/, docs/, scripts/, etc.

#### Multiple INDEX.md Files  
- [ ] **INDEX.md** rationalization (6+ references)
  - Multiple INDEX.md files across archive/, docs/, etc.
  - Need context-aware updates

---

## 📋 Recommended Next Steps

### Option A: Complete Phase 2 (Recommended)
**Time:** ~30-45 minutes  
**Impact:** Full resolution of relocated file references

1. **Batch 3:** Process Categories 1-3 (evolution, dev guides, MCP, wiki, release)
   - Estimated: 15-20 files, 60-70 references
   - Risk: Low (clear target locations)

2. **Batch 4:** Process Category 4-5 (capabilities, zendesk)
   - Estimated: 4-5 files, 38 references
   - Risk: Low

3. **Manual Review:** Category 6 (README.md, INDEX.md)
   - Estimated: 30+ references
   - Risk: Medium (requires context analysis)
   - Strategy: Review each reference individually

### Option B: Pivot to Phase 3 (Alternative)
**Rationale:** High-priority relocated files are fixed; move to deleted files

- Remaining relocated refs are lower priority
- Phase 3 has 581 deleted file issues (higher impact)
- Can return to Phase 2 remaining work later

---

## 🛠️ Tools Available

### Scripts Created
1. `.codex/fix_relocated_references.py` - Main fixer script
2. `.codex/fix_relocated_references_phase2b.py` - Extended fixer
3. `/tmp/find_more_relocations.py` - Discovery script (temporary)

### Usage
```bash
# Extend RELOCATED_FILES dict in script
# Add new mappings like:
RELOCATED_FILES_PHASE2C = {
    "EVOLUTION_TIMELINE.md": "docs/evolution/EVOLUTION_TIMELINE.md",
    "PLANSET_REGISTRY.md": "docs/evolution/PLANSET_REGISTRY.md",
    # ... more files
}

# Run script
python3 .codex/fix_relocated_references_phase2c.py
```

---

## 📊 Progress Tracking

### Overall Phase 2 Status
- **Total Identified:** 247 relocated file references
- **Fixed (Phase 2A+2B):** 113 references (45%)
- **Remaining:** ~134 references (55%)

### By Category Status
| Category | Total | Fixed | Remaining | % Complete |
|----------|-------|-------|-----------|------------|
| **High Priority (6 files)** | 107 | 107 | 0 | ✅ 100% |
| **Additional (Phase 2B)** | 6 | 6 | 0 | ✅ 100% |
| **Evolution & Planning** | 14 | 0 | 14 | ⏳ 0% |
| **Dev Guides** | 12 | 0 | 12 | ⏳ 0% |
| **MCP** | 13 | 0 | 13 | ⏳ 0% |
| **Wiki** | 25 | 0 | 25 | ⏳ 0% |
| **Release** | 16 | 0 | 16 | ⏳ 0% |
| **Capabilities** | 26 | 0 | 26 | ⏳ 0% |
| **Zendesk** | 12 | 0 | 12 | ⏳ 0% |
| **Complex (README/INDEX)** | 36 | 0 | 36 | ⏳ 0% |

---

## 🎯 Decision Point

### Recommendation: **Complete Phase 2** ✅

**Reasons:**
1. Momentum is high - keep going
2. Scripts are ready to use
3. Categories 1-5 are straightforward (no manual review needed)
4. Only Category 6 needs careful handling
5. Finishing Phase 2 provides clean slate for Phase 3

**Estimated Total Time:** 45-60 minutes to complete Phase 2 fully

### Alternative: **Pivot to Phase 3** ⚠️

**Reasons:**
1. High-priority refs are fixed (critical docs working)
2. Phase 3 has 581 issues (bigger impact potential)  
3. Can return to Phase 2 remaining work later
4. Avoid diminishing returns on less-critical refs

**Trade-off:** Leave 134 lower-priority refs for later

---

## 📝 Notes

### What We Learned
- Top 6 files accounted for 107/247 references (43%)
- Batch processing by file is highly efficient
- Automated validation prevents regression
- Relative path calculation is critical
- README.md and INDEX.md need special handling

### Automation Success
- 100% success rate on automated fixes
- Zero manual interventions required
- Full validation coverage
- Reusable scripts for future phases

### Quality Assurance
- ✅ Zero-break guarantee maintained
- ✅ All fixes validated
- ✅ Pre-existing broken links identified separately
- ✅ Comprehensive documentation produced

---

## 🚀 Ready to Execute?

**To continue Phase 2:**
1. Create Phase 2C script with Categories 1-5 mappings
2. Run automation for straightforward cases
3. Manually review Category 6 (README/INDEX)
4. Generate final Phase 2 complete report

**To pivot to Phase 3:**
1. Review Phase 2 completion (45% done)
2. Document remaining work for future session
3. Begin Phase 3: Deleted Files (581 issues)

---

**Decision Required:** Choose Option A (Complete Phase 2) or Option B (Pivot to Phase 3)

**Recommended:** Option A (Complete Phase 2) - finish what we started, clean break point for Phase 3

---

**Last Updated:** 2026-02-13  
**Status:** Awaiting decision on next steps
