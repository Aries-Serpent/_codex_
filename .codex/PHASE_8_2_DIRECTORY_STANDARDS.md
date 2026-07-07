# 📁 PHASE 8.2 DIRECTORY STANDARDS
## Workstream 8.2.2 — Target Repository Structure Design

**Track:** 8.2 (Repository Cleanup & Organization)  
**Authority:** @mbaetiong (D-tier autonomous)  
**Input:** PHASE_8_2_CLEANUP_STRATEGY.md + PHASE_8_2_STRUCTURE_AUDIT.md  
**Status:** Planning Phase  
**Generated:** 2026-07-07T14:26Z  
**Deliverable:** Structural Standards → Guides WS3 Execution

---

## 1. EXECUTIVE SUMMARY

This document defines the **target root-level repository structure** after Phase 8.2 cleanup completion. Currently, the repo has **107 top-level directories** with significant clutter. The target is **~85 top-level directories** with clear categorization, reduced duplication, and improved navigation.

### Current vs. Target State

| Aspect | Current | Target | Reduction |
|--------|---------|--------|-----------|
| **Top-level directories** | 107 | ~85 | 20% reduction |
| **Root-level loose files** | 205 | ~20 | 90% reduction |
| **Committed venvs** | 715 files | 0 (tracked) | 100% untrack |
| **Unorganized reports** | 500+ at root + `.codex/` | 0 at root, organized in `.codex/reports/` | Centralized |
| **Config roots** | 7 overlapping | 2 canonical + archived | Consolidated |

---

## 2. TARGET REPOSITORY STRUCTURE

### 2.1 Core Categories (Ordered by Priority & Navigation)

```
_codex_/                                     # Root

## 📚 PRIMARY DOCUMENTATION & GOVERNANCE
├── README.md                                # Project overview (KEEP)
├── CHANGELOG.md                             # Version history (KEEP)
├── LICENSE                                  # Licensing (KEEP)
├── CODE_OF_CONDUCT.md                       # Community standards (KEEP)
├── CONTRIBUTING.md                          # Contribution guide (KEEP)
├── SECURITY.md                              # Security policy (KEEP)
├── INSTALL.md                               # Installation (KEEP)
├── INTEGRATION.md                           # Integration guide (KEEP)
├── CITATION.cff                             # Citation metadata (KEEP)
├── GEMINI.md                                # Gemini-specific guide (KEEP)
├── CLAUDE.md                                # Claude-specific guide (KEEP)
├── QUICKSTART_BY_PROFILE.md                 # Quick start variants (KEEP)

## 🔬 PRIMARY SOURCE CODE & TESTS
├── src/                                     # Main source code (src-layout)
│   └── codex/                               # Primary package
├── tests/                                   # Test suite (pytest)
├── benches/                                 # Benchmarks
├── examples/                                # Usage examples

## 📖 PROJECT DOCUMENTATION & CONTENT
├── docs/                                    # Project documentation (mkdocs)
├── docs-data/                               # Generated docs index (gitignore'd)

## ⚙️ CONFIGURATION & DEPLOYMENT
├── configs/                                 # PRIMARY: Hydra configs (203 files) ⭐
├── conf/                                    # SECONDARY: Supplementary configs (41 files)
├── pyproject.toml                           # Python project configuration
├── setup.py / setup.cfg                     # Legacy setup config (if present)
├── requirements*.txt                        # Dependency specifications
├── .github/                                 # GitHub Actions & automation
├── .devcontainer/                           # Dev container config
├── docker/                                  # Docker configurations
├── k8s/                                     # Kubernetes manifests
├── manifests/                               # Deployment manifests
├── .dvc/                                    # DVC configuration

## 🤖 COGNITIVE & AGENT SYSTEMS
├── cognitive_app/                           # Cognitive Brain application (frontend/backend)
├── cognitive/                               # Cognitive brain modules
├── agents/                                  # Agent definitions/specifications
├── .copilot-space/                          # Copilot configuration

## 📋 OPERATIONAL & PLANNING
├── .codex/                                  # Agent operational store ⭐
│   ├── PHASE_8_2_CLEANUP_STRATEGY.md        # This workstream's strategy
│   ├── PHASE_8_2_DIRECTORY_STANDARDS.md     # This workstream's structure
│   ├── PHASE_8_2_CLEANUP_PHASES.md          # Week-by-week execution
│   ├── reports/                             # Root-level reports moved here
│   │   ├── phase-history/                   # Phase reports (phases 0-13)
│   │   ├── security/                        # Security reports
│   │   ├── remediation/                     # Remediation reports
│   │   ├── audit/                           # Audit reports
│   │   ├── documentation/                   # Documentation reports
│   │   └── INDEX.md                         # Navigation index
│   ├── archive/                             # Archival store
│   │   ├── phase-reports/                   # Historical phase reports
│   │   │   ├── phase-1-10/                  # Phases 1-10 (completed)
│   │   │   ├── phase-11-13/                 # Phases 11-13
│   │   │   ├── phase-maintenance/           # Operational reports
│   │   │   └── ARCHIVE_README.md            # Archive navigation
│   │   └── [other archived dirs]
│   ├── cognitive_brain/                     # Cognitive brain operational store
│   ├── sessions/                            # Session logs & checkpoints
│   ├── plans/                               # Planning documents
│   ├── validation/                          # Validation & QA artifacts
│   ├── qa_walkthrough/                      # QA walkthrough documentation
│   └── [existing operational subdirs]

## 🛠️ DEVELOPMENT TOOLING & AUTOMATION
├── scripts/                                 # Automation & maintenance scripts
├── tools/                                   # Developer/CI tooling utilities
├── cli/                                     # CLI tools
├── deploy/                                  # Deployment scripts
├── patches/                                 # Patch files & fixes

## 📊 ANALYSIS & TESTING INFRASTRUCTURE
├── analysis/                                # Analysis & analytics modules
├── testing_infrastructure/                  # Test utilities & fixtures
├── benchmarks/                              # Benchmark suites
├── pytest.ini                               # Pytest configuration
├── conftest.py                              # Pytest configuration (root)

## 📦 DATA, MODELS & ARTIFACTS
├── data/                                    # Dataset files
├── models/                                  # Model definitions/weights
├── artifacts/                               # Build/generated artifacts
├── reports/                                 # Generated reports
├── audit_artifacts/                         # Audit output
├── security-suite-artifacts/                # Security scan outputs

## 🔐 SECURITY & COMPLIANCE
├── semgrep/                                 # Semgrep rules
├── policies/                                # Security policies
├── deny.toml                                # Dependency deny rules
├── .codeql/                                 # CodeQL configuration

## 📚 LIBRARIES & DEPENDENCIES
├── codex_core.pyi                           # Type stubs
├── codex_ml/                                # ML subpackage
├── codex_digest/                            # Digest utilities
├── codex_utils/                             # Utilities
├── codex_regression/                        # Regression testing
├── codex_addons/                            # Addon modules
├── sentencepiece.pyi / sentencepiece/       # Tokenizer stubs
├── transformers.pyi / transformers/         # Transformer stubs

## 🔬 SPECIALIZED MODULES & SYSTEMS
├── tokenization/                            # Tokenization module
├── training/                                # Training utilities
├── monitoring/                              # Monitoring & observability
├── infrastructure/                          # Infrastructure-as-code
├── services/                                # Service modules
├── detectors/                               # Detection modules
├── interfaces/                              # Interface definitions

## 📁 WORKSPACE & EXPERIMENTAL
├── workbench/                               # Experimental/scratch working area
├── notebooks/                               # Jupyter notebooks
├── samples/                                 # Sample data/configs

## 🔍 MISCELLANEOUS & LOW-PRIORITY
├── misc/                                    # Miscellaneous (repo-owner-review, etc.)
├── templates/                               # Document/code templates
├── schemas/                                 # Data schemas
├── mappings/                                # Data mappings
├── databases/                               # Database definitions
├── db/                                      # Database files/scripts
├── memory/                                  # Memory storage (semantic, episodic)
├── coverage_tests/                          # Coverage-related tests
├── mp_pool/                                 # Multiprocessing utilities
├── prompts/                                 # Prompt templates (canonical)
├── omegaconf/ / omegaconf.pyi               # OmegaConf stubs

## 🗂️ ARCHIVED / DEPRECATED (CANDIDATES FOR WS3 OR FUTURE CLEANUP)
├── .codex/archive/                          # Primary archive (see above)
└── [legacy shims checked via D.2 import audit]
```

### 2.2 Files NOT to Create/Move (Out of Scope)

- `.github/workflows/` and `.github/` — Owned by workflow track, not 8.2
- `.disabled` workflow files — Flagged for workflow track, not touched by 8.2
- `src/`, `tests/`, `docs/` core content — Owned by respective tracks

---

## 3. ROOT-LEVEL CLEAN STATE SPECIFICATION

### 3.1 Canonical Root Files (12 files)

These files belong at repository root and should **never be moved**:

```
README.md                    # Project intro
CHANGELOG.md                 # Version history
LICENSE                      # Licensing
CODE_OF_CONDUCT.md          # Community standards
CONTRIBUTING.md              # Contribution guide
SECURITY.md                  # Security policy
INSTALL.md                   # Installation guide
INTEGRATION.md              # Integration guidance
CITATION.cff                # Citation metadata
GEMINI.md                   # Gemini-specific docs
CLAUDE.md                   # Claude-specific docs
QUICKSTART_BY_PROFILE.md    # Quick start variants
```

**Rationale:** These are discoverable, referenced in GitHub default files, and stable across phases.

### 3.2 Root Configuration Files (Non-Negotiable)

```
pyproject.toml              # Python package definition
setup.py / setup.cfg        # Legacy setup (legacy)
pytest.ini                  # Pytest configuration
conftest.py                 # Pytest root fixtures
.gitignore                  # Git ignore rules (hardened with venv entries)
.gitattributes             # Git attributes
.editorconfig              # Editor configuration
Makefile                   # Build automation (if present)
tox.ini                    # Tox testing config (if present)
```

### 3.3 Root Files to Remove (No longer at root after cleanup)

```
# PHASE reports → .codex/reports/phase-history/
PHASE_*.md, PHASE_*.txt                              (44 files)

# Security reports → .codex/reports/security/
SECURITY_FIXES_SUMMARY.txt, SECURITY_MONITORING_PLAN.md, etc.  (4 files)

# Remediation reports → .codex/reports/remediation/
REMEDIATION_*.md, remediation_plan_*.md              (5 files)

# Audit reports → .codex/reports/audit/
AUDIT_*.md, AUDIT_*.txt                              (3 files)

# Documentation reports → .codex/reports/documentation/
DOCUMENTATION_*.md, TERMINOLOGY_*.md                 (9 files)

# Build/Semgrep reports → .codex/reports/security/
SEMGREP_*.md, SEMGREP_*.json                         (3 files)

# Scratch/logs → DELETE
phase_9_2_*.log, gh_output.txt, mutmut_output.txt, mypy_output.txt,
mypy_error_analysis.txt, coverage-report.txt, test_execution_log.txt,
test_results.txt, sess_001, cost_estimate.json, decision_history.json  (15 files)

# Backup/legacy → DELETE (after diff verification)
CHANGELOG.md.pr5000, CODEX_MANIFEST.json.pr5000,
pyproject.toml.backup-day2, .mutmut.ini.bak, etc.  (7 files)

# Total root files removed: ~90 files
```

### 3.4 Top-Level Directory Consolidation

#### Consolidate/Remove (Priority 2)

| From | To | Action | Rationale |
|------|-----|--------|-----------|
| `config/` | `configs/` | Merge if content unique; remove if duplicate | Reduce duplication |
| `config_legacy/` | `.codex/archive/config-legacy/` | Move after import audit (see D.2) | Consolidate legacy |
| `config_experiments/` | `.codex/archive/config-experiments/` | Move after import audit | Consolidate legacy |
| `.config.legacy/` | `.codex/archive/config-legacy-metadata/` | Move after import audit | Consolidate legacy |
| `yaml_legacy/` | `.codex/archive/yaml-legacy/` | Move after import audit | Consolidate legacy |
| `.docs/` | DELETE (empty) | Remove | Empty placeholder |
| `PROMPTS/` | DELETE or merge to `prompts/` | Case-collision fix (Track 8.3) | Normalize naming |
| `.scripts/` | DELETE (near-empty) | Remove | Orphan directory |
| `.reports/` | Merge to `reports/` | Consolidate | Reduce fragmentation |
| `.CODEX/` | Investigate; merge to `.codex/` | Purpose verification | Stray duplicate |
| `XX.codex/` | Investigate; remove if stray | Purpose verification | Stray duplicate |

#### Keep and Refactor (Priority 1)

| Directory | Files | Status | Refactor |
|-----------|------:|--------|----------|
| `reports/` | 133 | 🟢 Keep | Consolidate `.reports/` into this; organize into subdirs |
| `misc/` | 121 | 🟢 Keep | Review for dead code; document purpose |
| `archive/` | 108 | 🟢 Keep | Rename to `.codex/archive/`; coordinate with Track 8.1 |
| `workbench/` | 107 | 🟡 Review | Dead-code scan; plan Phase 9 cleanup |
| `scripts/` | 973 | 🟢 Keep | Review for dead scripts; consolidate overlap with `tools/` |
| `tools/` | 334 | 🟢 Keep | No changes; cross-ref with `scripts/` for deduplication |

#### Single-File / Low-Count Directories (Priority 3)

Review these for purpose; archive or merge if orphaned:

```
assets/ (1), actions/ (1), ops/ (1), experiments/ (1),
detectors/ (1), benches/ (1), implementation_completed/ (1),
mp_pool/ (1), coverage_tests/ (1), ...
```

**Process (WS3.3):** Audit imports/references → Consolidate or archive if no references found.

---

## 4. DIRECTORY STRUCTURE NAVIGATION GUIDE

### For Contributors

After Phase 8.2 cleanup, use this guide to find where to work:

**Adding a feature?**
→ `src/codex/`

**Writing tests?**
→ `tests/`

**Updating documentation?**
→ `docs/`

**Adding a script for CI/automation?**
→ `scripts/` (preferred) or `tools/`

**Viewing phase reports or planning docs?**
→ `.codex/` (operational store)

**Looking for historical phase reports?**
→ `.codex/archive/phase-reports/phase-1-10/` (completed phases)

**Configuring Hydra?**
→ `configs/` (primary) or `conf/` (supplementary)

**Deploying code?**
→ `deploy/`, `docker/`, `k8s/`, `manifests/`

### For Repository Maintainers

**Git repo size concerns?**
→ `.codex/archive/` contains consolidated historical reports; can be pruned in Phase 9 if no references exist.

**New agent/workflow?**
→ Register in `.github/agents/` and `.copilot-space/`; document in `.codex/`

**Configuration consolidation?**
→ Use `configs/` as canonical root; archive alternatives.

---

## 5. STRUCTURAL COMPLIANCE CHECKLIST (Post-Cleanup)

Use this checklist to verify Phase 8.2 cleanup completion:

### Root Level (Post-Cleanup Verification)

- [ ] Root-level directories ≤ 90 (currently 107)
- [ ] Root-level loose files ≤ 20 (currently 205)
  - [ ] Only 12 canonical docs remain
  - [ ] No PHASE_*, SECURITY_*, REMEDIATION_*, AUDIT_* reports at root
  - [ ] No tool-generated logs (gh_output.txt, mypy_output.txt, etc.)
  - [ ] No session scratch files (sess_001, cost_estimate.json, etc.)
- [ ] Venvs untracked from git
  - [ ] `venv_test/` shows as untracked (not deleted)
  - [ ] `.venv_ci/` shows as untracked (not deleted)
  - [ ] `.gitignore` hardened with venv patterns

### `.codex/` Directory (Post-Cleanup Verification)

- [ ] Root `.codex/` PHASE_*.md files = remaining active phases only
  - [ ] Phases 1-7 moved to `.codex/archive/phase-reports/phase-1-10/`
  - [ ] Phases 8-10 moved to `.codex/archive/phase-reports/phase-1-10/` (if archived)
  - [ ] Phases 11+ remain at `.codex/` root (active reference)
- [ ] New subdirectories created
  - [ ] `.codex/reports/` with phase-history/, security/, remediation/, audit/, documentation/ subdirs
  - [ ] `.codex/archive/phase-reports/` with organized phase directories
  - [ ] `.codex/archive/phase-reports/ARCHIVE_README.md` created

### Configuration Consolidation (Post-Cleanup Verification)

- [ ] `configs/` identified as primary Hydra root (203 files)
- [ ] `conf/` identified as secondary supplementary root (41 files)
- [ ] Legacy config directories archived or removed
  - [ ] `config_legacy/` → `.codex/archive/config-legacy/` (if no imports found)
  - [ ] `config_experiments/` → `.codex/archive/config-experiments/` (if no imports found)
  - [ ] `.config.legacy/` → `.codex/archive/config-legacy-metadata/` (if no imports found)
  - [ ] `yaml_legacy/` → `.codex/archive/yaml-legacy/` (if no imports found)
- [ ] `.config/CONFIG_CONSOLIDATION_STATUS.md` documents decision

---

## 6. DIRECTORY SIZE TARGETS (Post-Cleanup)

Use these as validation goals to verify cleanup effectiveness:

| Directory | Current Size | Target Size | Reduction |
|-----------|-------------:|------------:|-----------|
| Total repo (git-tracked files) | 17,081 files | ~16,000 files | 6-7% |
| `.codex/` | 4,362 files | ~4,200 files | 3% (reports consolidated, not removed) |
| Root-level loose files | 205 files | ~20 files | 90% |
| Committed venvs | 715 files (tracked) | 0 (untracked) | 100% |
| **Total reduction** | — | **~1,200 files removed from tracking** | — |
| **Size reduction** | ~300 MB | ~250 MB | ~15-20% (venvs + generated data) |

---

## 7. NEXT STEPS (STANDARDS → PHASES)

Once this document is approved:

1. **Create PHASE_8_2_CLEANUP_PHASES.md** — Detailed week-by-week execution schedule
2. **Submit for go/no-go** on WS3 (Execution phase)
3. **If approved:** Begin WS3.1 (venv untracking) → WS3.2-3.4 (reports + configs) → Validation

---

**Status:** ✅ Planning Complete  
**Deliverable:** PHASE_8_2_DIRECTORY_STANDARDS.md (this document)  
**Next Deliverable:** PHASE_8_2_CLEANUP_PHASES.md (detailed execution schedule)  
**Authority:** @mbaetiong (D-tier, GO CONTINUE)

---

*End of Directory Standards Document.*
