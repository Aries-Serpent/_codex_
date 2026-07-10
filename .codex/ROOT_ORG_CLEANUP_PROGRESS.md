# ROOT FOLDER ORGANIZATION CLEANUP CAMPAIGN — Progress Tracker

**Campaign:** ROOT_ORG_CLEANUP_v1.0  
**Started:** 2026-07-10T23:12:34Z  
**Status:** PHASE 1 COMPLETE ✅

---

## 📊 Campaign Overview

| Metric | Value |
|--------|-------|
| **Total root files** | 86 markdown + config files |
| **Files to relocate** | 81 |
| **Essential files (keep)** | 6 (README.md, CONTRIBUTING.md, LICENSE, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md) |
| **LOW-risk files (0-1 refs)** | 48 |
| **MEDIUM-risk files (1-5 refs)** | 28 |
| **HIGH-risk files (5+ refs)** | 5 ⚠️ |
| **Expected duration** | ~2-3 weeks |
| **Campaign authorization** | D-mode autonomous, @mbaetiong full stakeholder approval |

---

## 🔄 Phase Progress

### ✅ Phase 1: Pre-Move Validation & Risk Assessment (COMPLETE)

**Duration:** 2026-07-10T23:12:34Z — 2026-07-10T23:15:00Z  
**Status:** ✅ COMPLETE

**Deliverables:**
1. ✅ `.codex/reports/ROOT_ORG_REFERENCE_AUDIT.json` - 81 files categorized by risk level
2. ✅ `.codex/plans/ROOT_ORG_RELOCATION_PLAN.json` - Three-phase relocation strategy
3. ✅ `.codex/ROOT_ORG_CLEANUP_PROGRESS.md` - This tracking document

**Key Findings:**
- 48 LOW-risk files ready for immediate batch move (0 expected references)
- 28 MEDIUM-risk files requiring atomic link updates (1-5 references)
- 5 HIGH-risk files requiring manual review (5+ references)
- Archive locations: `.codex/archive/` (internal) and `docs/archive/` (public)

**Validation Completed:**
- ✅ File categorization by purpose (campaign, report, deployment, API, quickstart, etc.)
- ✅ Risk assessment by filename patterns
- ✅ Target location assignment per file
- ✅ Rollback strategy reviewed

---

### ⏳ Phase 2: LOW-Risk Batch Moves (READY TO START)

**Estimated Duration:** 2026-07-10 — 2026-07-12 (3-5 days)  
**Status:** QUEUED  
**Files to move:** 48  
**Batch strategy:** 10 files per batch × 5 batches  
**Expected risk:** LOW (0 references per file)

**Files to Move (by category):**
- **CAMPAIGN** (28 files): PHASE_*, WAVE_*, TRACK_* reports → `.codex/archive/phases/`
- **COVERAGE** (8 files): COVERAGE_*.md → `.codex/archive/reports/coverage/`
- **TEMP** (2 files): test_*.md, CLEANUP_*.md → `.codex/archive/misc/`
- **IMPLEMENTATION** (1 file): WORKFLOW_CLEANUP_*.md → `.codex/archive/implementations/`

**Pre-execution Checklist:**
- [ ] All LOW-risk files confirmed in relocation plan
- [ ] Archive directories created in `.codex/` and `docs/`
- [ ] `.codex/archive/README.md` and `docs/archive/README.md` navigation stubs created
- [ ] Phase 2 batch 1 ready for execution

**Next Steps:**
1. Create archive directory structure
2. Execute batch 1 (10 files) with dry-run validation
3. Verify batch 1 completion
4. Continue with batches 2-5 (auto-advance on success)

---

### ⏳ Phase 3: MEDIUM-Risk Atomic Updates (PENDING)

**Estimated Duration:** 2026-07-13 — 2026-07-15 (6-8 days)  
**Status:** PENDING  
**Files to move:** 28  
**Batch strategy:** 1 file per batch (atomic link updates)  
**Expected risk:** MEDIUM (1-5 references per file)

**Files to Move (by category):**
- **REPORT** (6 files): *_REPORT*.md, *_AUDIT*.md → `.codex/archive/reports/`
- **ARCHIVED** (3 files): .codex/archive/deprecated/AGENTS.md, .codex/archive/deprecated/CLAUDE.md, .codex/archive/deprecated/GEMINI.md → `.codex/archive/deprecated/`
- **DEPRECATED** (2 files): *_DEPRECATION.md → `.codex/archive/deprecated/`
- **MISC** (11 files): Various misc files → `.codex/archive/misc/`
- **DEPLOYMENT** (2 files): docs/release/RELEASE_NOTES.md, docs/release/ISOLATED_DEPLOYMENT.md → `docs/release/`
- **API_DOC** (4 files): *_INTEGRATION*, *_GOVERNANCE*, etc. → `docs/api/reference/`

**Atomic Reference Update Strategy:**
- For each file: scan → update references → validate → commit → verify

**Approval Gate:**
- Phase 2 must complete with 0 broken links
- All tests must pass post-Phase 2
- Manual approval recommended from @mbaetiong before Phase 3 start

---

### ⏳ Phase 4: HIGH-Risk Consolidation (PENDING)

**Estimated Duration:** 2026-07-16 — 2026-07-19 (9-12 days)  
**Status:** PENDING  
**Files to move:** 5  
**Batch strategy:** 1 file per batch (manual approval required)  
**Expected risk:** HIGH (5+ references per file)

**Files to Move:**
1. **docs/quickstart/QUICKSTART_BY_PROFILE.md** → `docs/quickstart/` (HIGH refs expected)
2. **docs/quickstart/QUICK_START_COGNITIVE_BRAIN.md** → `docs/quickstart/` (HIGH refs expected)
3. **docs/quickstart/QUICK_START_ML.md** → `docs/quickstart/` (HIGH refs expected)
4. **docs/api/reference/INTEGRATION.md** → `docs/api/reference/` (HIGH refs expected)
5. **docs/api/reference/QUANTUM_COMPLIANCE_TUNING_AGENT_INTEGRATION_GUIDE.md** → `docs/api/reference/` (HIGH refs expected)

**Manual Review Required:**
- ⚠️ Each file requires comprehensive reference scan
- ⚠️ Each file requires workflow dependency check
- ⚠️ Each file requires manual approval before move

**Approval Gate:**
- @mbaetiong must review and approve each HIGH-risk move
- Phase 3 must complete with 0 broken links
- Comprehensive reference documentation required

---

### ⏳ Phase 5: Validation & Hardening (PENDING)

**Estimated Duration:** 2026-07-20 — 2026-07-21 (13-14 days)  
**Status:** PENDING

**Validation Checklist:**
- [ ] Link validation: 0 broken links (run `python scripts/validate-links.py --full`)
- [ ] Reference validation: No dangling references (run `python scripts/root_org/validate_references.py --check-all`)
- [ ] Workflow validation: All workflows pass
- [ ] Build & test: `nox -s tests` passes
- [ ] Documentation build: No errors

**Deliverables:**
- `.codex/reports/ROOT_ORG_FINAL_VALIDATION_REPORT.md`
- `.codex/ROOT_ORG_COMPLETION_SUMMARY.md`

**Approval Gate:**
- All validation checks must pass
- All tests must pass
- @mbaetiong final sign-off required

---

## 📁 Archive Directory Structure (To Be Created)

```
.codex/archive/
├── README.md                     # Navigation guide
├── phases/                       # Campaign/phase reports
│   ├── PHASE_*.md               # (45 files)
│   ├── WAVE_*.md                # Campaign wave reports
│   └── ARCHIVE_INDEX.md          # Index of all archived phases
├── reports/                      # Audit and analysis reports
│   ├── *_REPORT*.md             # General reports
│   ├── *_AUDIT*.md              # Audit reports
│   ├── coverage/                # Coverage-related
│   │   └── COVERAGE_*.md        # (8 files)
│   └── REPORT_INDEX.md
├── implementations/              # Implementation completion records
│   └── *_IMPLEMENTATION*.md     # (1-2 files)
├── deprecated/                   # Deprecation notices & archived configs
│   ├── *_DEPRECATION.md         # (2 files)
│   ├── .codex/archive/deprecated/AGENTS.md                # Archived agent reference
│   ├── .codex/archive/deprecated/CLAUDE.md                # Archived model reference
│   └── .codex/archive/deprecated/GEMINI.md                # Archived model reference
├── plans/                        # Archived planning documents
│   └── *_PLAN*.md               # Planning documents
└── misc/                         # Temporary & miscellaneous
    └── [various temp files]     # (20+ files)

docs/archive/
├── README.md                     # Navigation guide
├── quickstart/                   # Old quickstart guides
│   ├── docs/quickstart/QUICKSTART_BY_PROFILE.md  # Archived
│   └── QUICK_START_*.md          # (2-3 files)
├── api/                          # Previous API reference versions
│   └── *.md                      # (4-5 files)
├── architecture/                 # Archived design documentation
│   └── *.md
└── phases/                       # Historical phase documentation
    └── *.md
```

---

## 🚀 How to Execute Next Phase

**To start Phase 2 (LOW-risk batch moves):**

```bash
# Run this to execute Phase 2:
@copilot Use root-organizer-agent to execute Phase 2 LOW-risk batch moves
  --plan .codex/plans/ROOT_ORG_RELOCATION_PLAN.json
  --risk LOW
  --batch 10
  --dry-run-first
```

**To check progress:**
```bash
cat .codex/ROOT_ORG_CLEANUP_PROGRESS.md
```

**To check audit results:**
```bash
cat .codex/reports/ROOT_ORG_REFERENCE_AUDIT.json | jq '.files | sort_by(.risk_level)'
```

---

## 📝 Notes & Decisions

### Phase 1 Decisions:
- ✅ Decided to keep CHANGELOG.md in root (essential for release workflow)
- ✅ Decided to archive .codex/archive/deprecated/AGENTS.md reference (duplicate of `.github/agents/.codex/archive/deprecated/AGENTS.md`)
- ✅ Decided to consolidate QUICKSTART files in Phase 4 (HIGH-risk, requires manual review)
- ✅ Risk categorization based on filename patterns (PHASE_*, REPORT*, etc.)

### Outstanding Decisions (for later phases):
- ⏳ Whether to create redirect placeholders for moved files (e.g., "See `docs/archive/...`")
- ⏳ Which workflows need updates after file moves (TBD during Phase 2-3)
- ⏳ Final destination for .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md (currently in docs/accountability/, consider keeping)

---

## 🔧 Troubleshooting

### If reference counting shows unexpected results:
1. Run: `python scripts/root_org/validate_references.py <filename> --json`
2. Check: `.codex/action_log.ndjson` for operation logs
3. Report: Issue to Phase lead with filename and actual ref count

### If file move fails:
1. Automatic rollback: `python scripts/root_org/rollback_move.py --last-operation`
2. Check git status: `git status`
3. Verify file exists: `ls -la <file>`

### If tests fail post-move:
1. Check broken links: `python scripts/validate-links.py <file>`
2. Run tests: `nox -s tests`
3. Check `.github/workflows/` for hardcoded file path references

---

## 📞 Contact & Escalation

- **Campaign Lead:** root-organizer-agent (primary orchestrator)
- **Backup Agents:** repository-hygiene-agent, repository-organization-agent
- **Escalation:** @mbaetiong for HIGH-risk decisions and final approval
- **Documentation:** `.codex/ROOT_FOLDER_ORGANIZATION.md`

---

**Last Updated:** 2026-07-10T23:15:00Z  
**Next Review:** Phase 2 completion checkpoint  
**Status:** ✅ PHASE 1 COMPLETE — READY FOR PHASE 2 EXECUTION
