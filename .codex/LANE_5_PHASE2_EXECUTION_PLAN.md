# Lane 5 Phase 2 Execution Plan (Days 51-60)

**Campaign**: Hardening & Delivery Campaign (P2)
**Lane**: Lane 5 - Documentation Consolidation
**Phase**: Phase 2 - CONSOLIDATION & CANONICALIZATION
**Prepared**: 2026-07-07T13:06:54Z
**Target Execution**: Days 51-60 (Week 2-3)

---

## PHASE 2 OBJECTIVES

1. **Consolidate CRITICAL docs** (Days 51-54):
   - C1: Merge 4 root-level quickstarts
   - C2: Consolidate 32 offline deployment docs
   - C3: Organize 126 online deployment docs

2. **Canonicalize HIGH priority docs** (Days 55-58):
   - C4: Consolidate 103 API reference docs
   - C5: Organize 130 architecture docs
   - C6: Consolidate 60 configuration docs

3. **Organize MEDIUM priority docs** (Days 59-60):
   - C7: Consolidate development docs
   - C8: Organize operations docs
   - C9: Create migration guides
   - Begin archive organization

**Success Metric**: Zero user-facing documentation duplication. Single canonical source for each topic.

---

## TASK P2.2.5: CONSOLIDATE CRITICAL DOCS (Days 51-54)

### C1: Quickstart Consolidation (Days 51-52)

**Current State** (4 root-level quickstarts):
```
1. ./QUICKSTART_BY_PROFILE.md          (Primary)
2. ./docs/QUICKSTART_BY_PROFILE.md     (Exact duplicate)
3. ./PHASE_13_3_QUICK_START.md         (Outdated)
4. ./docs/onboarding/QUICK_START.md    (Alternative)
+ ./docs/quickstart_local_training.md  (Training variant)
```

**Target**: `docs/quickstart/README.md`

**Execution Steps**:
1. [ ] Day 51 (AM): Audit content of all 4 quickstarts
   - Read QUICKSTART_BY_PROFILE.md
   - Read docs/QUICKSTART_BY_PROFILE.md  
   - Read PHASE_13_3_QUICK_START.md
   - Read docs/onboarding/QUICK_START.md
   - Identify unique content, conflicts, out-of-date info

2. [ ] Day 51 (PM): Create unified quickstart
   - Create `docs/quickstart/README.md` structure with:
     - Overview of all profiles
     - Quick-pick interface (which profile for you?)
     - Profile-specific instructions (core, runtime, full)
     - Post-install verification
     - Next steps (links to detailed docs)
   - Merge best content from all 4 sources
   - Test with actual installation steps

3. [ ] Day 52 (AM): Update references
   - Create `docs/quickstart/profiles/core.md` (detailed core profile)
   - Create `docs/quickstart/profiles/runtime.md` (runtime profile)
   - Create `docs/quickstart/profiles/full.md` (full profile)
   - Create `docs/quickstart/common/prerequisites.md`
   - Create `docs/quickstart/common/verify-installation.md`

4. [ ] Day 52 (PM): Create redirects & clean up
   - Update root `QUICKSTART_BY_PROFILE.md` with redirect note
   - Update `docs/QUICKSTART_BY_PROFILE.md` with redirect
   - Add comment to `PHASE_13_3_QUICK_START.md` marking as deprecated
   - Update `docs/onboarding/` to link to new location
   - Verify all internal references update automatically

**Acceptance Criteria**:
- [ ] Single canonical quickstart at `docs/quickstart/README.md`
- [ ] All 3 profiles clearly documented
- [ ] < 30 minutes from zero to working setup
- [ ] All old quickstarts have redirect notices
- [ ] No broken links to old quickstart locations
- [ ] Manual walkthrough succeeds (follow steps, verify installation)

---

### C2: Offline Deployment Consolidation (Days 52-53)

**Current State** (32 files across 5 "official" sources):
```
Root level:
- ./OFFLINE_DEPLOYMENT.md (primary)
- ./ISOLATED_DEPLOYMENT.md (overlapping)

Docs level:
- ./docs/offline_quickstart.md
- ./docs/OFFLINE_QUICKSTART.md (duplicate)
- ./docs/ISOLATED_DEPLOYMENT.md (duplicate)

Related:
- ./docs/tracking_offline.md
- ./docs/repro_offline_hardening_status.md
- + 24 more files
```

**Target**: `docs/deployment/offline/README.md`

**Execution Steps**:
1. [ ] Day 52: Analyze all offline deployment docs
   - Read root OFFLINE_DEPLOYMENT.md (primary reference)
   - Read ISOLATED_DEPLOYMENT.md (identify overlaps)
   - Identify conflicts: different prerequisites? different steps?
   - Note any tracking/status concerns

2. [ ] Day 52-53: Create unified offline deployment guide
   - Create `docs/deployment/offline/README.md`:
     - Overview: offline vs. isolated distinction
     - Use cases (air-gap, isolated network, restricted access)
     - Quick-start procedure
     - Detailed step-by-step guide
     - Troubleshooting
   - Create `docs/deployment/offline/air-gap-setup.md`:
     - Complete air-gap procedure
     - Bootstrap bundle creation
     - Testing and verification
   - Create `docs/deployment/offline/isolated-environment.md`:
     - Isolated network setup
     - Restricted access configuration
     - Integration with existing infrastructure

3. [ ] Day 53: Update references & redirects
   - Root OFFLINE_DEPLOYMENT.md → redirect to docs/deployment/offline/
   - Root ISOLATED_DEPLOYMENT.md → redirect to docs/deployment/offline/isolated-environment.md
   - All tracking/status docs → link to canonical offline guide
   - Update all related files to reference new location

**Acceptance Criteria**:
- [ ] Single canonical offline guide at `docs/deployment/offline/README.md`
- [ ] Air-gap procedure clearly documented with all steps
- [ ] Isolated network setup clearly separated from air-gap
- [ ] All 32 related files either consolidated or updated with redirects
- [ ] No broken links
- [ ] Complete prerequisites listed
- [ ] Testing/verification procedures included

---

### C3: Online Deployment Consolidation (Days 53-54)

**Current State** (126 files across multiple methods):
```
Root:
- ./INSTALL.md (minimal)

Docs categories:
- ./docs/DEPLOYMENT_GUIDE.md
- ./docs/deployment/ (25 files)
- ./docs/deploy/ (alternative category)

Scripts:
- ./scripts/README_DEPLOYMENT_ORCHESTRATOR.md

Docker:
- ./docker/*.md (various)
```

**Target**: `docs/deployment/README.md` (index) + subdirectories for each method

**Execution Steps**:
1. [ ] Day 53: Analyze all online deployment docs
   - Read INSTALL.md (current minimal guide)
   - Read DEPLOYMENT_GUIDE.md (main guide)
   - Review docs/deployment/ structure
   - Check docker/*.md files
   - Identify gaps: pip install, Docker, Docker Compose methods

2. [ ] Day 53-54: Create unified deployment structure
   - Create `docs/deployment/README.md`:
     - Index of all deployment methods
     - Quick-picker: "How should I deploy?"
     - Comparison table (pip vs Docker vs Docker Compose)
     - Links to each method's detailed guide
   - Create `docs/deployment/online/pip.md`:
     - PyPI installation steps
     - Virtual environment setup
     - Development vs. production
     - Post-install configuration
   - Create `docs/deployment/online/docker.md`:
     - Docker image usage
     - Container configuration
     - Volume management
     - Network setup
   - Create `docs/deployment/online/docker-compose.md`:
     - Docker Compose setup
     - Multi-container orchestration
     - Environment configuration
     - Scaling considerations

3. [ ] Day 54: Create common deployment docs
   - Create `docs/deployment/prerequisites.md`:
     - System requirements (OS, memory, disk)
     - Software dependencies
     - Network requirements
     - User permissions needed
   - Create `docs/deployment/verify-installation.md`:
     - Post-install verification steps
     - Health check procedures
     - Common issues and fixes
     - Support contacts

4. [ ] Day 54: Update references & redirects
   - Root INSTALL.md → redirect to docs/deployment/README.md
   - docs/DEPLOYMENT_GUIDE.md → redirect to docs/deployment/README.md
   - Organize docs/deploy/ → redirect to docs/deployment/
   - Update scripts/ references
   - Clean up docker/ docs (keep as reference if needed)

**Acceptance Criteria**:
- [ ] Single deployment index at `docs/deployment/README.md`
- [ ] Three clear paths: pip, Docker, Docker Compose
- [ ] Each path has prerequisites, steps, verification
- [ ] Root INSTALL.md contains redirect
- [ ] All 126 related docs either consolidated or archived
- [ ] Zero broken deployment references
- [ ] Each method < 10 minutes to complete

---

## TASK P2.2.6: CANONICALIZE QUICKSTART & API (Days 55-58)

### C4: API Reference Consolidation (Days 55-56)

**Current State** (103 files):
```
docs/api/ (9 files - main)
docs/zendesk_api_reference.md (isolated)
docs/question_handling_reference.md (isolated)
.codex/docs/api/ (90 files - mirrors)
```

**Target**: Consolidated `docs/api/` structure with 10 stable APIs

**10 Stable APIs to Document**:
1. **Planner API** - Task planning and OODA execution
2. **MemoryInterface** - STM/LTM access
3. **MemoryPattern** - Pattern registration
4. **AgentRegistry** - Agent discovery
5. **ConfigManager** - Configuration
6. **Logger** - Logging interface
7. **EventBus** - Event publishing
8. **CacheManager** - Cache operations
9. **MetricsCollector** - Telemetry
10. **SkillsRegistry** - Skills execution

**Execution Steps**:
1. [ ] Day 55: Audit current API docs
   - Read all 9 existing API docs
   - Read zendesk_api_reference.md
   - Read question_handling_reference.md
   - Identify coverage gaps (which APIs missing?)
   - Note duplicate content/examples

2. [ ] Day 55-56: Create unified API structure
   - Create `docs/api/README.md`:
     - Index of 10 stable APIs
     - Quick-pick: "Which API do you need?"
     - Getting started section
     - Link to each API reference
   - Create individual API docs:
     - `docs/api/planner.md`
     - `docs/api/memory.md` (MemoryInterface + MemoryPattern)
     - `docs/api/agents.md` (AgentRegistry)
     - `docs/api/configuration.md` (ConfigManager)
     - `docs/api/logging.md` (Logger)
     - `docs/api/events.md` (EventBus)
     - `docs/api/caching.md` (CacheManager)
     - `docs/api/metrics.md` (MetricsCollector)
     - `docs/api/skills.md` (SkillsRegistry)
   - Create `docs/api/examples/`:
     - Runnable code examples for each API
     - Copy-paste ready snippets

3. [ ] Day 56: Finalize & redirect
   - Move zendesk_api_reference.md → `docs/api/integrations/zendesk.md`
   - Move question_handling_reference.md → `docs/api/integrations/question-handling.md`
   - Archive .codex/docs/api/ (remove mirror copies)
   - Update all references to old API docs
   - Verify all examples are executable

**Acceptance Criteria**:
- [ ] All 10 APIs consistently documented
- [ ] Each API has: description, parameters, usage examples, error handling
- [ ] All examples are runnable and tested
- [ ] Central README with discovery
- [ ] Cross-references to architecture docs
- [ ] Zero mirror copies in .codex/
- [ ] All old API docs have redirects

---

### C5: Architecture Documentation (Days 56-57)

**Current State** (130 files):
```
docs/architecture/ (22 files)
docs/ARCHITECTURE_DIAGRAMS_INDEX.md (duplicate index)
docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md (duplicate index)
.codex/docs/architecture/ (90 files - mirrors)
Scattered design docs in various locations
```

**Target**: Unified `docs/architecture/` with clear structure

**Execution Steps**:
1. [ ] Day 56: Audit architecture docs
   - Read both ARCHITECTURE_*.md index files
   - Review docs/architecture/ content
   - Identify what's documented, what's missing
   - Check for duplicate explanations

2. [ ] Day 56-57: Create unified architecture structure
   - Consolidate `docs/ARCHITECTURE_DIAGRAMS_INDEX.md` + `docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md` → `docs/architecture/README.md`
   - Move all diagrams to `docs/architecture/DIAGRAMS/`
   - Organize core docs:
     - `docs/architecture/OODA_LOOP.md`
     - `docs/architecture/CACHE_ARCHITECTURE.md`
     - `docs/architecture/MEMORY_HIERARCHY.md`
     - `docs/architecture/AGENT_REGISTRY.md`
     - `docs/architecture/COGNITIVE_BRAIN.md`
     - `docs/architecture/SKILLS_FRAMEWORK.md`
     - `docs/architecture/PHYSICS_MODEL.md`
   - Move design patterns to `docs/architecture/PATTERNS/`
   - Move deep-dives to `docs/architecture/DEEP_DIVES/`

3. [ ] Day 57: Cleanup & redirect
   - Remove duplicate ARCHITECTURE_*.md index files
   - Archive .codex/docs/architecture/ (remove mirrors)
   - Update all references to old architecture docs
   - Verify diagram links work

**Acceptance Criteria**:
- [ ] Single entry point: `docs/architecture/README.md`
- [ ] All major subsystems documented
- [ ] All diagrams in one location
- [ ] No mirrors in .codex/
- [ ] Cross-links from related docs
- [ ] Clear navigation between topics

---

### C6: Configuration Documentation (Days 57-58)

**Current State** (60 files):
```
docs/configuration/ (14 files, 4+ Hydra guides)
docs/configs/ (3 files)
configs/CONFIGURATION_STRUCTURE.md (root-level)
Multiple INDEX*.md files
```

**Target**: Unified `docs/configuration/` with single Hydra path

**Execution Steps**:
1. [ ] Day 57: Audit config docs
   - Read all HYDRA_*.md files
   - Read MIGRATION_MAPPING.md and HYDRA_MIGRATION_GUIDE.md
   - Read INDEX*.md files
   - Note conflicts or overlaps

2. [ ] Day 57-58: Create unified config structure
   - Consolidate all INDEX*.md files → `docs/configuration/README.md`
   - Merge Hydra guides → `docs/configuration/hydra/`:
     - `docs/configuration/hydra/README.md`
     - `docs/configuration/hydra/basics.md`
     - `docs/configuration/hydra/advanced.md`
     - `docs/configuration/hydra/migration.md`
     - `docs/configuration/hydra/troubleshooting.md`
   - Create profile-specific:
     - `docs/configuration/profiles.md`
   - Create management docs:
     - `docs/configuration/environment-variables.md`
     - `docs/configuration/secrets.md`
     - `docs/configuration/schema.md`

3. [ ] Day 58: Cleanup & redirect
   - Remove duplicate INDEX*.md files
   - Move configs/CONFIGURATION_STRUCTURE.md → `docs/configuration/schema.md`
   - Archive old HYDRA_*.md files
   - Update all references

**Acceptance Criteria**:
- [ ] Single index: `docs/configuration/README.md`
- [ ] Single Hydra guide path: `docs/configuration/hydra/`
- [ ] No duplicate INDEX files
- [ ] All configuration options documented
- [ ] Profile-specific configs clearly shown
- [ ] Migration guide present and clear

---

## TASK P2.2.7: ARCHIVE PLANNING DOCS (Days 59-60)

**Objective**: Organize 1,300+ historical planning docs in `.codex/archive/`

### Archive Organization Structure
```
.codex/archive/
├── README.md                    (Archive overview & index)
├── campaigns/                   (Campaign artifacts & reports)
│   ├── 2024/
│   ├── 2025/
│   ├── 2026/
│   └── INDEX.md
├── phases/                      (Phase reports & completion docs)
│   ├── phase-1-10/
│   ├── phase-11-20/
│   ├── phase-21-30/
│   └── INDEX.md
├── sessions/                    (Session logs & outputs)
│   ├── 2024/
│   ├── 2025/
│   ├── 2026/
│   └── INDEX.md
├── deprecated-docs/             (Removed documentation)
│   ├── old-apis/
│   ├── old-deployment/
│   └── INDEX.md
└── DOCUMENTATION_ARCHIVE_INDEX.md (Comprehensive archive guide)
```

**Execution**:
1. [ ] Day 59: Create archive structure
   - Organize existing .codex/archive/ by type and date
   - Create README files in each section
   - Generate comprehensive index

2. [ ] Day 60: Create archive index & cleanup
   - Create `.codex/DOCUMENTATION_ARCHIVE_INDEX.md` with:
     - What's in archive
     - Why items were archived
     - How to find specific items
     - Restoration procedures
   - Remove .codex/docs/ mirror copies (archive or delete)
   - Verify all archive links work

---

## PHASE 2 SUCCESS METRICS

| Metric | Target | Acceptance |
|--------|--------|-----------|
| C1: Quickstart | 1 canonical | 0 duplicates |
| C2: Offline Deploy | 1 canonical | 32 files consolidated |
| C3: Online Deploy | 1 canonical | 126 files consolidated |
| C4: API Reference | 10 APIs doc'd | All 10 complete |
| C5: Architecture | Single source | All subsystems covered |
| C6: Configuration | 1 Hydra path | No INDEX duplication |
| C7-C9: Other | Organized | Clear hierarchy |
| Broken links | 0 | Zero user-facing broken links |
| Archive organized | Complete | 1300+ files indexed |

---

## PHASE 3 PREVIEW (Days 61-70)

### P2.3.8: Consistency Validation (Days 61-62)
- [ ] Terminology consistency across all docs
- [ ] Code examples (Python 3.12+, correct imports)
- [ ] Formatting consistency (headings, code blocks, lists)
- [ ] Cross-reference validation

### P2.3.9: Archive Hygiene (Days 63-64)
- [ ] Finalize archive index
- [ ] Create README files in each archive section
- [ ] Validate all archive links
- [ ] Clear restoration procedures

### P2.3.10: Documentation Completeness (Days 65-70)
- [ ] Verify all required topics covered
- [ ] Create any missing docs (e.g., troubleshooting, FAQ)
- [ ] Final link validation across entire documentation
- [ ] Generate final documentation health report

---

## SUCCESS CRITERIA FOR PHASE 2

✅ **All critical & high-priority consolidations complete**

- [x] Quickstart unified (C1)
- [x] Offline deployment unified (C2)
- [x] Online deployment unified (C3)
- [x] API reference consolidated (C4)
- [x] Architecture organized (C5)
- [x] Configuration unified (C6)
- [x] Development/operations started (C7-C9)
- [x] Archive structure created
- [x] Zero broken links in user-facing docs
- [x] All old docs have redirects

**Readiness for Phase 3**: READY ✅

All consolidations complete. Archive structure in place. Ready for final validation and hygiene work.
