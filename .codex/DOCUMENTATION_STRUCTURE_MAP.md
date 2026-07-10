# Documentation Structure Map (P2.1.2)

**Task**: Map documentation structure across categories and identify consolidation opportunities
**Timeline**: Days 43-50 (Week 1)
**Status**: ACTIVE
**Last Updated**: 2026-07-07T13:06:54Z

---

## Executive Summary

The _codex_ repository maintains **~7,820 markdown files** (976 MB) distributed across:
- **Root Level**: 48 files (critical entry points)
- **`docs/` Directory**: 1,200 files (user-facing documentation)
- **`.codex/` Directory**: 6,620 files (planning, reports, and internal documentation)

This structure reveals significant **fragmentation**: multiple sources of truth for the same topics (offline setup, deployment, quickstart) scattered across the filesystem.

**Recommended 2-Level Hierarchy**:
1. **Level 1**: Category folders (quickstart, api, architecture, deployment, operations, etc.)
2. **Level 2**: Specific topics within categories with clear canonical document

---

## I. QUICKSTART & GETTING STARTED

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Root Quickstart | 1 | `docs/quickstart/QUICKSTART_BY_PROFILE.md` | ⚠️ Duplicate in docs/ |
| Docs Quickstart | 4 | `docs/quickstart_*.md`, `docs/onboarding/` | ⚠️ Scattered |
| Old Phase Quickstart | 1 | `PHASE_13_3_QUICK_START.md` | ⚠️ Outdated |
| **TOTAL** | **34** | **Various locations** | **CRITICAL: Consolidate** |

### Issues Identified
- **Duplication**: Root `docs/quickstart/QUICKSTART_BY_PROFILE.md` and `docs/docs/quickstart/QUICKSTART_BY_PROFILE.md` are mirrors
- **Inconsistency**: Different quickstarts for different profiles (core, runtime, full)
- **Scattered onboarding**: `docs/onboarding/` has separate QUICK_START.md
- **Obsolete content**: `PHASE_13_3_QUICK_START.md` references old phase structure

### Proposed Consolidation
```
docs/quickstart/
├── README.md                    (Primary: all profiles, common setup)
├── profiles/
│   ├── core.md                  (Minimal profile)
│   ├── runtime.md               (Runtime profile)
│   └── full.md                  (Full development profile)
├── common/
│   ├── prerequisites.md          (System requirements, dependencies)
│   ├── installation.md           (Standard install procedure)
│   └── verify-installation.md    (Post-install verification)
└── next-steps.md                (Links to deeper documentation)

# Archive/Redirect
ROOT → docs/quickstart/QUICKSTART_BY_PROFILE.md: Redirect to docs/quickstart/README.md
docs/onboarding/QUICK_START.md: Redirect to docs/quickstart/README.md
PHASE_13_3_QUICK_START.md: Archive to .codex/archive/phases/
```

### Acceptance Criteria
- [ ] Single canonical quickstart in `docs/quickstart/README.md`
- [ ] Users can go from zero to working setup in < 30 minutes
- [ ] All three profiles (core, runtime, full) covered
- [ ] Copy-paste examples for each profile
- [ ] System requirements clearly stated
- [ ] Post-install verification script included

---

## II. API REFERENCE

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Main API Docs | 4 | `docs/api/*.md` | ⚠️ Incomplete |
| Config APIs | 14 | `docs/configuration/*.md` | ⚠️ Hydra-specific |
| Zendesk API | 1 | `docs/zendesk_api_reference.md` | ⚠️ External |
| Question Handling | 1 | `docs/question_handling_reference.md` | ⚠️ Specific |
| Physics Reference | 1 | `docs/PHYSICS_TECHNICAL_REFERENCE.md` | ⚠️ Isolated |
| **TOTAL** | **103** | **Various locations** | **CRITICAL: Consolidate** |

### Issues Identified
- **Scattered across domains**: API docs live in different places (api/, configuration/, root)
- **Incomplete coverage**: Not all 10 stable APIs documented consistently
- **Duplicate structure**: Multiple API reference formats
- **Cross-reference gaps**: No central index or discovery mechanism

### 10 Stable APIs to Document
1. **Planner API** - Task planning and OODA execution
2. **MemoryInterface** - STM/LTM access and management
3. **MemoryPattern** - Pattern registration and retrieval
4. **AgentRegistry** - Agent discovery and metadata
5. **ConfigManager** - Configuration loading and validation
6. **Logger** - Structured logging interface
7. **EventBus** - Event publishing and subscription
8. **CacheManager** - Multi-layer cache operations
9. **MetricsCollector** - Telemetry and metrics collection
10. **SkillsRegistry** - Skill registration and execution

### Proposed Consolidation
```
docs/api/
├── README.md                    (Index and discovery)
├── QUICK_START.md               (Getting started with APIs)
├── planner.md                   (Planner API reference)
├── memory.md                    (Memory interface + patterns)
├── agents.md                    (Agent registry reference)
├── configuration.md             (Config management API)
├── logging.md                   (Logger API reference)
├── events.md                    (Event bus reference)
├── caching.md                   (Cache management API)
├── metrics.md                   (Metrics collector API)
├── skills.md                    (Skills registry API)
└── examples/                    (Runnable code examples)
    ├── basic-planner.py
    ├── memory-usage.py
    ├── agent-discovery.py
    └── ...

# Archive/Consolidate
docs/zendesk_api_reference.md → docs/api/integrations/zendesk.md
docs/question_handling_reference.md → docs/api/integrations/question-handling.md
docs/PHYSICS_TECHNICAL_REFERENCE.md → docs/reference/physics-model.md
docs/configuration/*.md → Merge into docs/api/configuration.md + keep as reference
```

### Acceptance Criteria
- [ ] All 10 stable APIs documented with consistent structure
- [ ] Each API has: description, usage example, parameter reference, error handling
- [ ] All examples are executable and tested
- [ ] Central README with discovery and cross-references
- [ ] Links from architecture docs to API reference
- [ ] .codex/archive/deprecated/AGENTS.md references API docs where applicable

---

## III. ARCHITECTURE & DESIGN

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Architecture Index | 2 | `docs/ARCHITECTURE_*.md` | ⚠️ Duplicate |
| Architecture Docs | 22 | `docs/architecture/` | ⚠️ Scattered |
| Design Docs | 32 | `docs/arch/` + mirrors | ⚠️ Fragmented |
| .codex Mirrors | 90 | `.codex/docs/architecture/` | ⚠️ Duplicate |
| Diagrams | Multiple | Various locations | ⚠️ Hard to find |
| **TOTAL** | **130** | **Multiple trees** | **HIGH: Consolidate** |

### Issues Identified
- **Duplication**: `docs/ARCHITECTURE_DIAGRAMS_INDEX.md` and `docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md`
- **Mirror copies**: `.codex/docs/architecture/` duplicates `docs/architecture/`
- **Scattered design docs**: Design patterns split between `docs/arch/` and `docs/architecture/`
- **Diagram locations**: Diagrams in multiple places (hard to maintain)
- **Inconsistent depth**: Some docs are tutorial-style, others are reference

### Proposed Consolidation
```
docs/architecture/
├── README.md                    (Index: overview + quick links)
├── OODA_LOOP.md                 (Primary OODA design)
├── PACKAGING.md                 (Packaging architecture)
├── PROFILES.md                  (Core/Runtime/Full profiles)
├── CACHE_ARCHITECTURE.md        (4-layer cache design)
├── MEMORY_HIERARCHY.md          (STM/LTM memory model)
├── AGENT_REGISTRY.md            (Agent discovery system)
├── COGNITIVE_BRAIN.md           (Cognitive brain subsystem)
├── SKILLS_FRAMEWORK.md          (Skills registration framework)
├── PHYSICS_MODEL.md             (Physics foundation)
├── PATTERNS/
│   ├── async-patterns.md
│   ├── state-management.md
│   ├── error-handling.md
│   └── ...
├── DIAGRAMS/
│   ├── ooda-loop.mermaid
│   ├── cache-hierarchy.mermaid
│   ├── memory-model.mermaid
│   └── ...
└── DEEP_DIVES/                  (Detailed analysis)
    ├── quantum-integration.md
    ├── performance-model.md
    └── ...

# Archive/Consolidate
docs/ARCHITECTURE_DIAGRAMS_INDEX.md → docs/architecture/README.md
docs/REPOSITORY_ARCHITECTURE_DIAGRAMS.md → docs/architecture/DIAGRAMS/
docs/arch/ → Merge into docs/architecture/ (redirect old links)
.codex/docs/architecture/ → Keep as internal reference only
```

### Acceptance Criteria
- [ ] Single canonical architecture entry point: `docs/architecture/README.md`
- [ ] All major subsystems documented (OODA, Memory, Agents, Cache, Skills)
- [ ] All diagrams in one location with consistent naming
- [ ] Cross-references to source code and related docs
- [ ] No mirrors in `.codex/docs/` (move to `.codex/archive/`)
- [ ] Diagrams are Mermaid or SVG (maintainable formats)

---

## IV. DEPLOYMENT & OPERATIONS

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Root Install | 1 | `.codex/archive/misc/INSTALL.md` | ⚠️ Minimal |
| Offline Deploy | 5 | `OFFLINE_*.md`, `ISOLATED_*.md` | ⚠️ Duplicate |
| Online Deploy | 4 | `docs/deployment/`, `docs/deploy/` | ⚠️ Scattered |
| Docker Deploy | Multiple | Various `docker/*.md` files | ⚠️ Fragmented |
| Scripts Docs | Multiple | `scripts/README_*.md` | ⚠️ Procedural |
| Operations Guides | 14 | `docs/operations/` | ⚠️ Mixed with planning |
| CRM/Admin Runbooks | 5 | `docs/crm/admin-runbooks/` | ⚠️ Specialized |
| Release/Rollback | Multiple | `docs/release/`, `docs/releasing.md` | ⚠️ Incomplete |
| **TOTAL** | **126** | **Multiple trees** | **CRITICAL: Consolidate** |

### Issues Identified
- **OFFLINE SETUP FRAGMENTATION** (5+ sources):
  - `docs/release/OFFLINE_DEPLOYMENT.md` (root)
  - `docs/release/ISOLATED_DEPLOYMENT.md` (root)
  - `docs/offline_quickstart.md`
  - `docs/OFFLINE_QUICKSTART.md` (duplicate)
  - `docs/docs/release/ISOLATED_DEPLOYMENT.md` (duplicate)
  
- **CONFLICTING INSTRUCTIONS**: Different deployment guides may have different setup steps
- **Scattered Docker setup**: Docker deployment instructions scattered across files
- **Release procedure unclear**: Multiple release-related docs without clear sequence
- **Operations not linked**: Operations guides not linked from main deployment docs

### Proposed Consolidation
```
docs/deployment/
├── README.md                    (Index: all deployment types)
├── QUICK_START.md               (Fast track to basic setup)
├── PREREQUISITES.md             (System requirements, dependencies)
├── online/
│   ├── README.md                (Online deployment overview)
│   ├── pip-install.md           (PyPI installation)
│   ├── docker.md                (Docker setup)
│   └── docker-compose.md        (Docker Compose setup)
├── offline/
│   ├── README.md                (Offline overview + common approach)
│   ├── air-gap-setup.md         (Complete air-gap procedure)
│   ├── isolated-environment.md  (Isolated network setup)
│   └── bootstrap-bundle.md      (Offline bootstrap bundle)
├── configuration.md             (Post-deployment configuration)
├── verification.md              (Post-install verification)
└── troubleshooting.md           (Common deployment issues)

docs/operations/
├── README.md                    (Index: operational tasks)
├── monitoring.md                (Health monitoring)
├── logging.md                   (Log collection and analysis)
├── scaling.md                   (Horizontal/vertical scaling)
├── backup-restore.md            (Backup and recovery procedures)
└── incident-response.md         (Incident handling procedures)

docs/release/
├── README.md                    (Release procedure overview)
├── release-process.md           (Step-by-step release guide)
├── rollback.md                  (Rollback procedures)
├── changelog.md                 (Link to root CHANGELOG.md)
└── deprecation.md               (Deprecation policy)

# Archive/Consolidate
docs/release/OFFLINE_DEPLOYMENT.md → Redirect to docs/deployment/offline/README.md
docs/release/ISOLATED_DEPLOYMENT.md → Redirect to docs/deployment/offline/isolated-environment.md
.codex/archive/misc/INSTALL.md → Redirect to docs/deployment/README.md
docs/deploying.md → docs/deployment/online/
docs/releasing.md → docs/release/release-process.md
docs/crm/admin-runbooks/ → docs/operations/integrations/crm.md
```

### Acceptance Criteria
- [ ] Users can deploy online via pip in < 5 minutes
- [ ] Users can deploy online via Docker in < 10 minutes
- [ ] Air-gap deployment documented with step-by-step guide
- [ ] No duplicate deployment docs (only canonical versions)
- [ ] Operations guides clearly linked from deployment docs
- [ ] Release procedure clear and follows one canonical path
- [ ] Rollback procedures documented and tested
- [ ] All root-level `OFFLINE_*` and `ISOLATED_*` docs redirect to canonical locations

---

## V. CONFIGURATION & HYDRA

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Hydra Guides | 8 | `docs/configuration/HYDRA_*.md` | ⚠️ Multiple |
| Config Docs | 14 | `docs/configuration/` | ⚠️ Scattered |
| Config Index | 3 | Multiple `INDEX.md` files | ⚠️ Duplicate |
| Migration Guides | 3 | `*MIGRATION*.md` files | ⚠️ Legacy-focused |
| Root Config Docs | 1 | `configs/CONFIGURATION_STRUCTURE.md` | ⚠️ Isolated |
| Environment Vars | 1 | `docs/configuration/ENVIRONMENT_VARIABLES.md` | ✅ Specific |
| **TOTAL** | **60** | **Multiple trees** | **HIGH: Consolidate** |

### Issues Identified
- **Multiple Hydra guides**: `HYDRA_GUIDE.md`, `HYDRA_MIGRATION_GUIDE.md`, `hydra_defaults_and_sweeps.md`
- **Duplicate index files**: Multiple `INDEX.md` and `INDEX_*.md` files
- **Config location confusion**: Configs are in `configs/`, `docs/configuration/`, and elsewhere
- **Outdated migration docs**: References to old configuration systems

### Proposed Consolidation
```
docs/configuration/
├── README.md                    (Index: all config topics)
├── QUICK_START.md               (5-minute Hydra intro)
├── hydra/
│   ├── README.md                (Hydra overview)
│   ├── basics.md                (Basic Hydra concepts)
│   ├── advanced.md              (Advanced patterns)
│   ├── migration.md             (Upgrade/migration guide)
│   └── troubleshooting.md       (Common issues)
├── profiles.md                  (Core/Runtime/Full profile configs)
├── environment-variables.md     (Env var configuration)
├── secrets.md                   (Secret management)
├── examples/
│   ├── basic-config.yaml
│   ├── multi-env-setup.yaml
│   └── ...
└── schema.md                    (Configuration schema reference)

# Archive/Consolidate
configs/CONFIGURATION_STRUCTURE.md → Redirect to docs/configuration/schema.md
docs/configuration/HYDRA_GUIDE.md → Merge into docs/configuration/hydra/basics.md
docs/configuration/HYDRA_MIGRATION_GUIDE.md → docs/configuration/hydra/migration.md
docs/configuration/hydra_defaults_and_sweeps.md → docs/configuration/hydra/advanced.md
Multiple INDEX*.md → Single docs/configuration/README.md
```

### Acceptance Criteria
- [ ] Single quickstart for Hydra: `docs/configuration/hydra/README.md`
- [ ] All configuration options documented with examples
- [ ] Environment variable configuration explained
- [ ] Profile-specific configurations clearly shown
- [ ] Migration guide from old to new config system
- [ ] All examples are copy-paste ready

---

## VI. DEVELOPMENT & CONTRIBUTING

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Contributing Guide | 1 | `CONTRIBUTING.md` | ✅ Comprehensive |
| Development Setup | Multiple | Various dev docs | ⚠️ Scattered |
| Testing Guide | 32 | `docs/testing/` | ⚠️ Fragmented |
| Development Profiles | 6 | Various dev setup docs | ⚠️ Incomplete |
| **TOTAL** | **40+** | **Multiple trees** | **MEDIUM: Organize** |

### Issues Identified
- **Testing docs fragmented**: 32 files in `docs/testing/` with unclear organization
- **Development setup incomplete**: Not all profiles have clear dev setup
- **CONTRIBUTING.md not linked**: Central guide not clearly linked to detailed docs

### Proposed Consolidation
```
docs/development/
├── README.md                    (Overview: links to all dev topics)
├── setup.md                     (Development environment setup)
├── running-tests.md             (How to run the test suite)
├── writing-tests.md             (How to write new tests)
├── debugging.md                 (Debugging techniques)
├── code-style.md                (Code style and conventions)
└── ci-cd.md                     (CI/CD pipeline overview)

# Keep as-is (comprehensive)
CONTRIBUTING.md → Link to docs/development/ for detailed guides
```

### Acceptance Criteria
- [ ] New developers can set up dev environment from docs/development/setup.md
- [ ] Testing procedures clearly documented
- [ ] Code style conventions enforced
- [ ] CI/CD pipeline documented

---

## VII. CAMPAIGN PLANNING & REPORTS

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| Campaign Docs | 1834 | `.codex/` root and subdirs | ℹ️ Active |
| Phase Reports | 250+ | `.codex/archive/phase-reports/` | ℹ️ Historical |
| Campaign Plans | 174 | `.codex/plans/` | ℹ️ Active |
| Campaign Reports | 5 | `.codex/campaign_artifacts/` | ℹ️ Active |
| **TOTAL** | **2400+** | **.codex/** | **ARCHIVE: Move** |

### Proposed Consolidation
```
# Keep in Git tracking for active development
.codex/plans/                   (Active campaign planning)
.codex/cognitive_brain/         (Subsystem status)
.codex/reports/                 (Campaign reports)

# Move to archive
.codex/archive/campaigns/       (Campaign artifacts)
.codex/archive/phases/          (Phase reports 1-30+)
.codex/archive/sessions/        (Session logs)

# Create index
.codex/DOCUMENTATION_ARCHIVE_INDEX.md
```

### Acceptance Criteria
- [ ] Active planning docs remain in `.codex/` root
- [ ] Historical docs clearly organized in `.codex/archive/`
- [ ] Archive index created with navigation
- [ ] Clear guidance on when to restore from archive

---

## VIII. ARCHIVE & HISTORICAL

### Current State
| Source | Count | Path | Status |
|--------|-------|------|--------|
| docs archive | 28 | `docs/archive/` | ℹ️ Documentation |
| .codex archive | 1300+ | `.codex/archive/` | ℹ️ Historical |
| Deprecated docs | Multiple | Various deprecation markers | ⚠️ Unclear |
| **TOTAL** | **1300+** | **Archive dirs** | **ORGANIZE** |

### Issues Identified
- **Unclear archive policies**: What to archive and when?
- **Poor navigation**: Archive is hard to explore
- **Missing index**: No central archive index

### Proposed Consolidation
```
docs/archive/
├── README.md                    (Archive overview and policies)
├── api-v1/                      (Old API versions)
├── configuration-legacy/        (Old config systems)
└── deployment-legacy/           (Old deployment methods)

.codex/archive/
├── README.md                    (This is INDEX)
├── campaigns/                   (Campaign artifacts)
├── phases/                      (Phase reports, organized by number)
├── sessions/                    (Session logs and outputs)
├── deprecated-docs/             (Removed documentation)
└── INDEX.md                     (Complete archive index)

# Create comprehensive
.codex/DOCUMENTATION_ARCHIVE_INDEX.md
```

### Acceptance Criteria
- [ ] Archive is clearly organized by type
- [ ] Complete index of all archived items
- [ ] Clear guidance on what each section contains
- [ ] Links to related current documentation
- [ ] Policy document on archival procedures

---

## IX. SUMMARY: RECOMMENDED 2-LEVEL HIERARCHY

### Level 1: Categories
```
docs/
├── quickstart/              (Getting started, all profiles)
├── api/                     (All 10 stable APIs)
├── architecture/            (Design, patterns, diagrams)
├── deployment/              (Online and offline deployment)
├── operations/              (Operational procedures)
├── configuration/           (Hydra and config management)
├── development/             (Dev setup, testing, contributing)
├── reference/               (API, CLI, environment variables)
├── troubleshooting/         (FAQ, common issues, debugging)
└── archive/                 (Legacy documentation)

.codex/
├── plans/                   (Active campaign planning)
├── cognitive_brain/         (Subsystem documentation)
├── reports/                 (Campaign execution reports)
├── docs/                    (Internal documentation mirrors - TO BE ARCHIVED)
└── archive/                 (Historical documents)
```

### Level 2: Specific Topics
- Each category has `README.md` as entry point
- Specific topics as sibling files or subdirectories
- Clear cross-references between categories

---

## X. CONSOLIDATION PRIORITY MATRIX

| Topic | Duplication | Fragmentation | Priority | Target Files | Target Date |
|-------|-------------|----------------|----------|--------------|-------------|
| Quickstart | CRITICAL | CRITICAL | 🔴 P0 | 34 files | Day 52 |
| Deployment | CRITICAL | CRITICAL | 🔴 P0 | 126 files | Day 54 |
| API Reference | HIGH | HIGH | 🟠 P1 | 103 files | Day 56 |
| Architecture | HIGH | HIGH | 🟠 P1 | 130 files | Day 57 |
| Configuration | HIGH | MEDIUM | 🟠 P1 | 60 files | Day 58 |
| Operations | MEDIUM | MEDIUM | 🟡 P2 | 14 files | Day 60 |
| Development | MEDIUM | LOW | 🟡 P2 | 40 files | Day 60 |
| Archive | N/A | HIGH | 🟡 P2 | 1300 files | Day 65 |

---

## XI. SUCCESS METRICS

- ✅ **Single canonical source** for each major topic
- ✅ **Zero duplicate docs** in user-facing documentation
- ✅ **Cross-linked architecture**: Docs reference each other clearly
- ✅ **Organized archive**: Historical docs indexed and navigable
- ✅ **User feedback**: Users can find information in < 2 clicks
- ✅ **Automated validation**: CI checks for broken links and orphaned docs

---

## XII. NEXT PHASE

**P2.1.3: Consolidation Opportunities**
- Detailed list of 20+ specific consolidation actions
- For each: current files, conflicts identified, merge strategy
- Output: `DOCUMENTATION_CONSOLIDATION_OPPORTUNITIES.md`

**P2.1.4: Link Validation**
- Comprehensive check of all internal/external links
- Output: Link validation report with broken/external/relative categories
- Ready for Phase 2 fixes
