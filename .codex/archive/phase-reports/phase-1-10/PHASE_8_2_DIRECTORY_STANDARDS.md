# 📋 PHASE 8.2 — DIRECTORY STRUCTURE STANDARDS (Post-Cleanup)

**Workstream:** 8.2.2 — Directory Standards & Architecture  
**Track:** 8.2 (Repository Cleanup & Organization)  
**Track Lead:** repository-organization-agent  
**Generated:** 2026-07-03  
**Status:** Template + Specification

---

## 1. EXECUTIVE SUMMARY

This document defines the **canonical directory structure** for the Aries-Serpent/_codex_ repository post-cleanup (after PHASE 8 completion). It serves as:

1. **Normative spec** for directory placement (where does code/config/docs belong?)
2. **Validation checklist** for cleanup batches (did we follow the standard?)
3. **Navigation guide** for developers (how do I find what I need?)
4. **Archival taxonomy** (what goes into `.codex/archive/`?)

---

## 2. TOP-LEVEL DIRECTORY STRUCTURE

### 2.1 Repository Root (≤20 loose files)

**Allowed at repo root:**

```
/
├── README.md                           ← Project overview (MUST)
├── LICENSE                             ← License text (MUST)
├── SECURITY.md                         ← Security policy (MUST)
├── CONTRIBUTING.md                     ← Contributor guide (SHOULD)
├── CHANGELOG.md                        ← Version history (SHOULD)
├── CITATION.cff                        ← Citation metadata (OPTIONAL)
├── pyproject.toml                      ← Python project config (MUST)
├── setup.py                            ← Legacy setup (if needed)
├── setup.cfg                           ← Setup config (if needed)
├── Cargo.toml                          ← Rust project config (if present)
├── Makefile                            ← Build automation (OPTIONAL)
├── mkdocs.yml                          ← Docs build config (MUST)
├── pytest.ini                          ← Test config (MUST)
├── .gitignore                          ← Git ignore rules (MUST)
├── .gitattributes                      ← Git attributes (MUST)
├── .codex/archive/deprecated/CLAUDE.md                           ← Claude model spec (OPTIONAL)
├── .codex/archive/deprecated/GEMINI.md                           ← Gemini model spec (OPTIONAL)
├── uv.lock                             ← Lock file (MUST if uv used)
├── Cargo.lock                          ← Lock file (MUST if Rust)
└── .env.example                        ← Env template (OPTIONAL)
```

**Forbidden at repo root (MUST be archived or removed):**
- Phase reports (`PHASE_*.md`, `PHASE_*.txt`)
- Status/summary files (from root consolidation Batch 2)
- Session/scratch files (`sess_001`, `cost_estimate.json`)
- Log/output files (`*.log`, `*_output.txt`)
- Backup/superseded files (`.bak`, `.orig`, `.pr5000`)

---

### 2.2 Core Source Code & Build Directories

| Directory | Purpose | Max Files | Ownership | Standards |
|-----------|---------|-----------|-----------|-----------|
| `src/` | Primary source code (Python, Rust, etc.) | ~1,500 | Dev team | Source-layout (`src/codex/...`) |
| `tests/` | Test suite (pytest, unit/integration/E2E) | ~3,000 | Test team | Mirror `src/` structure |
| `scripts/` | Automation/CI/build scripts | ~800 | DevOps/Dev | Categorized by purpose (see 2.2.1) |
| `tools/` | Developer/CI utility modules | ~300 | Dev team | Utility-specific (no duplication with `scripts/`) |
| `docs/` | Project documentation (mkdocs) | ~1,800 | Doc team (8.1) | Hierarchical nav, **not** reports |
| `.github/` | GitHub Actions, workflows, agent defs | ~2,000 | DevOps | Out of scope for 8.2 |

### 2.2.1 Scripts Directory Subcategorization

```
scripts/
├── ci/                    ← CI/CD helper scripts
│   ├── run_tests.sh
│   ├── build_docker.sh
│   └── ...
├── maintenance/           ← Maintenance & cleanup
│   ├── check_imports.py
│   ├── cleanup_artifacts.sh
│   └── ...
├── dev/                   ← Development utilities
│   ├── setup_env.sh
│   ├── format_code.py
│   └── ...
├── utils/                 ← Generic utilities (if large)
│   └── ...
└── README.md              ← Scripts index
```

---

### 2.3 Configuration & Data Directories

| Directory | Purpose | Max Files | Ownership | Notes |
|-----------|---------|-----------|-----------|-------|
| `configs/` | Hydra project configs (YAML/TOML) | ~200 | Config team | **Primary** config root |
| `conf/` | Additional config root (secondary) | ~40 | Config team | Supplement if needed |
| `data/` | Data files (datasets, samples, etc.) | ~20 | Data team | Exclude large binary data |
| `schemas/` | Data/API schemas (JSON, proto, etc.) | ~20 | Dev team | Shared schemas |
| `manifests/` | K8s manifests, deployment specs | ~30 | DevOps | Infrastructure-as-code |

**Forbidden:**
- `config_legacy/`, `config_experiments/`, `.config/`, `.config.legacy/`, `yaml_legacy/` (→ archive)

---

### 2.4 Documentation & Knowledge Directories

| Directory | Purpose | Max Files | Ownership | Allowed Subcategories |
|-----------|---------|-----------|-----------|----------------------|
| `docs/` | Project docs (mkdocs) | ~1,800 | Track 8.1 | User guides, API docs, tutorials |
| `docs-data/` | Generated doc indexes (regenerable) | gitignored | Build system | `docs.sqlite`, `*.jsonl`, etc. |
| `.codex/` | Agent operational store | <2,500 | Agent team | See 2.5 below |
| `archive/` | Long-term archive (non-operational) | ~200 | Archive mgr | Older project archives |

**Forbidden in docs:**
- Phase reports (→ `.codex/archive/`)
- Temporary scratch (→ `.codex/archive/temporary/`)
- Build artifacts (→ gitignore)

---

### 2.5 Agent Operational Store (`.codex/`)

**Post-cleanup structure:**

```
.codex/
├── INDEX.md                                  ← Master metadata index
├── archive/
│   ├── INDEX.md                             ← Archive master index
│   ├── phase-history/
│   │   ├── PHASE_1/
│   │   ├── PHASE_2/
│   │   └── ... PHASE_12/
│   │   ├── INVENTORY.jsonl
│   │   └── RETRIEVAL_GUIDE.md
│   ├── root-consolidation/
│   │   ├── PHASE_CLUSTER.md
│   │   ├── SECURITY_CLUSTER.md
│   │   ├── REMEDIATION_CLUSTER.md
│   │   ├── AUDIT_CLUSTER.md
│   │   └── ...
│   ├── config-legacy/
│   │   ├── config_legacy/
│   │   ├── config_experiments/
│   │   └── ...
│   └── temporary/                           ← Time-scoped cleanup (90d purge)
│       └── SESSION_ARTIFACTS_2026Q2.md
├── reports/                                 ← Active reports (non-historical)
│   ├── DASHBOARD.md
│   ├── health/
│   └── ...
├── cognitive_brain/                         ← Agent brain operational data
│   ├── status/
│   ├── skills/
│   └── ...
├── plans/                                   ← Strategic/operational plans
├── sessions/                                ← Session transcripts (active)
├── accountability/                          ← Agent accountability tracking
├── evidence/                                ← Evidence artifacts
├── validation/                              ← Validation reports
├── qa_walkthrough/                          ← QA walkthrough data
├── templates/                               ← Agent templates
├── pending_ops/                             ← Pending operations queue
├── action_log.ndjson                        ← All operations audit log
└── PHASE_8_* (active phases only)          ← Phase 8+ reports kept at top level
```

**Key constraints:**
- **Phase reports:** Phases 1–7 archived to `phase-history/`; Phase 8+ at top level
- **Max top-level `.md` files:** ~20 (for active phases only)
- **Total `.codex/` files:** ≤2,500 (was 4,362; 43% reduction target)
- **Archive index accuracy:** 100% (searchable, up-to-date)

---

### 2.6 Specialized Application Directories

| Directory | Purpose | Max Files | Status | Owner |
|-----------|---------|-----------|--------|-------|
| `cognitive_app/` | Cognitive Brain UI/backend | ~200 | Keep | Agent team |
| `agents/` | Agent definitions & specs | ~60 | Keep | Agent team |
| `k8s/` | Kubernetes manifests (if present) | ~20 | Keep | DevOps |
| `deploy/` | Deployment scripts/configs | ~20 | Keep | DevOps |
| `docker/` | Docker build contexts | ~20 | Keep | DevOps |
| `examples/` | Usage examples | ~60 | Keep | Dev team |
| `training/` | ML training scripts/data | ~20 | Keep | ML team |

---

### 2.7 Build & Generated Artifacts (GITIGNORED, not tracked)

**These should NEVER be in git; enforce via `.gitignore`:**

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
node_modules/
.venv_ci/
venv_test/
.venv/
*.tmp
*.log
docs-data/generated/
```

---

### 2.8 Catch-All Directories (Review Before Cleanup)

| Directory | Current Size | Decision |
|-----------|-------------|----------|
| `misc/` | ~120 files | Retain as catch-all; index in `.codex/INDEX.md` |
| `workbench/` | ~100 files | Mark as experimental; review for dead code in 8.2.3 |
| `reports/` | ~130 files | Consolidate active reports into `.codex/reports/`; archive old ones |
| `services/` | ~60 files | Verify no orphaned services; document in architecture |
| `apps/` | ~15 files | Verify ownership; consolidate into relevant roots |

---

## 3. FILE ORGANIZATION RULES

### 3.1 Naming Conventions

**Directories:**
- All lowercase with hyphens: `my-module/`, `test-utils/`
- No underscores at top level (except hidden dirs: `.codex/`, `.github/`)
- No case variants (PROMPTS/ and prompts/ cannot both exist)

**Configuration Files:**
- YAML/TOML: `config.yaml`, `pyproject.toml` (not `.config` or `CONFIG`)
- Hidden configs: `.env`, `.gitignore` (only for VCS/system files)

**Documentation:**
- Root level: `README.md`, `CONTRIBUTING.md`, `SECURITY.md` (UPPER)
- In-directory: `readme.md`, `index.md` (lowercase)
- Archives: `PHASE_7A_SUMMARY.md` (preserved name in archive)

**Reports (deprecated from root):**
- Never at repo root anymore
- Archive location: `.codex/archive/root-consolidation/`

### 3.2 Module/Package Layout

**Python (src-layout):**
```
src/
├── codex/
│   ├── __init__.py
│   ├── module_a/
│   │   ├── __init__.py
│   │   └── impl.py
│   └── module_b/
└── ...
```

**Tests (mirror structure):**
```
tests/
├── test_module_a/
│   └── test_impl.py
├── test_module_b/
└── ...
```

---

## 4. ARCHIVAL TAXONOMY (`.codex/archive/`)

### 4.1 Archive Categories

| Category | Destination | Retention | Searchable | Purpose |
|----------|-------------|-----------|-----------|---------|
| **Phase History** | `phase-history/PHASE_*/` | Permanent | Yes (NDJSON inventory) | Historical reference, phase audit trail |
| **Root Consolidation** | `root-consolidation/` | Permanent | Yes (cluster index) | Root cleanup documentation |
| **Config Legacy** | `config-legacy/` | Permanent | Index only | Legacy configuration reference |
| **Session Artifacts** | `temporary/` | 90 days | Index only | Time-scoped cleanup of scratch files |
| **Build Artifacts** | gitignore (not archived) | Regenerable | N/A | Never archived, always gitignored |

### 4.2 Archive Inventory Format

**File:** `.codex/archive/INVENTORY.jsonl` (one object per line)

```json
{
  "archived_at": "2026-07-03T14:00Z",
  "category": "phase-history",
  "original_path": ".codex/PHASE_7A_WAVE2_SUMMARY.md",
  "archive_path": ".codex/archive/phase-history/PHASE_7A/PHASE_7A_WAVE2_SUMMARY.md",
  "phase_family": "PHASE_7A",
  "file_size_kb": 42,
  "purpose": "Wave 2 completion summary and lane status",
  "keywords": ["wave2", "completion", "lane", "status"],
  "references": [".codex/PHASE_7A_INDEX.md"],
  "git_commit": "abc123def456"
}
```

### 4.3 Retrieval Guide

**Location:** `.codex/archive/RETRIEVAL_GUIDE.md`

```markdown
# Archive Retrieval Guide

## How to find an archived file

### Option 1: Browse by phase
cd .codex/archive/phase-history/PHASE_7A/
ls -la

### Option 2: Search the inventory
jq 'select(.phase_family == "PHASE_7A")' .codex/archive/INVENTORY.jsonl

### Option 3: Restore from git history
git log --follow -- <original_path>
git show <commit>:<original_path>
```

---

## 5. CONFIGURATION ROOT CONSOLIDATION

### 5.1 Primary vs Secondary Config Roots

**Active (primary):**
- `configs/` ← Hydra project configs (203 files max)

**Active (secondary):**
- `conf/` ← Additional/supplementary configs (40 files max)

**Archived (legacy):**
- `config_legacy/` → `.codex/archive/config-legacy/config_legacy/`
- `config_experiments/` → `.codex/archive/config-legacy/config_experiments/`
- `.config/` → investigate; archive or merge if no live imports
- `.config.legacy/` → `.codex/archive/config-legacy/.config.legacy/`
- `yaml_legacy/` → `.codex/archive/config-legacy/yaml_legacy/` (if no imports)

### 5.2 Import Validation (Pre-Archive)

Before archiving legacy configs, verify no live imports:

```bash
# Check all active source code
grep -r "from config_legacy import" src/ tests/
grep -r "from yaml_legacy import" src/ tests/
grep -r "import config_legacy" src/ tests/
```

**If no imports found:** Archive is safe.  
**If imports found:** Keep in-place, document as "legacy shim" in `DIRECTORY_STANDARDS.md`.

---

## 6. CASE CONSISTENCY RULES (Coordination with 8.3)

**After 8.3 case-collision de-duplication completes:**

| Pair | Rule | Preferred |
|------|------|-----------|
| `PROMPTS/` vs `prompts/` | Consolidate | `prompts/` (lowercase) |
| `PROMPTS/` → `prompts/` | Single source | `prompts/` |
| `.scripts/` vs `scripts/` | Merge | `scripts/` (main) |
| `.reports/` vs `reports/` | Merge | `reports/` (main) |
| `docs/` vs `.docs/` | Keep | `docs/` (remove `.docs/`) |

**Rule:** Top-level directories are **lowercase** with hyphens; hidden dirs (`.`) reserved for VCS/system.

---

## 7. DIRECTORY NAVIGATION & DISCOVERY

### 7.1 Directory Index (→ include in root README.md)

```markdown
## Directory Structure

- **`src/`** — Source code (Python, Rust)
- **`tests/`** — Test suite
- **`docs/`** — Project documentation (mkdocs)
- **`scripts/`** — Automation scripts (CI, maintenance, dev)
- **`configs/`** — Hydra project configuration
- **`tools/`** — Developer utilities
- **`cognitive_app/`** — Cognitive Brain UI/backend
- **`.codex/`** — Agent operational store (reports, plans, sessions)
- **`.github/`** — GitHub Actions and workflows

See [DIRECTORY_STANDARDS.md](.codex/PHASE_8_2_DIRECTORY_STANDARDS.md) for full structure.
```

### 7.2 Search / Discovery

**For developers:**
- `grep -r <pattern> src/` — Search source code
- `find . -name "*pattern*" -type f` — Find files by name
- `jq '.references[]' .codex/archive/INVENTORY.jsonl` — Search archived file references

**For agents:**
- `.codex/INDEX.md` — Master metadata index (agent-friendly)
- `.codex/archive/INVENTORY.jsonl` — Searchable archive inventory

---

## 8. VALIDATION CHECKLIST (For Cleanup Batches)

After each batch, validate:

- [ ] No files deleted; all moves tracked as git renames
- [ ] Archive destination exists and index is updated
- [ ] Directory hierarchy respects naming rules (lowercase, hyphens)
- [ ] `.gitignore` correctly excludes build artifacts
- [ ] Active phase reports remain at `.codex/` top level
- [ ] Archived phase reports are in `phase-history/` subdirs
- [ ] Root-level files (post-cleanup) ≤20 and canonical only
- [ ] Config roots consolidated (2 active + archive)
- [ ] Case consistency applied (lowercase top-level dirs)
- [ ] Archive index (NDJSON) is complete and searchable
- [ ] Retrieval guide is accurate

---

## 9. TRANSITION TIMELINE

| Phase | Milestone | Status |
|-------|-----------|--------|
| **WS 8.2.1** | Audit complete; structure mapped | ✅ Complete |
| **WS 8.2.2** | Standards defined (this doc) | ⏳ In progress |
| **WS 8.2.2** | Cleanup batches 0–4 planned | ⏳ In progress |
| **WS 8.2.3** | Batches executed; archival completed | ⏳ Pending |
| **8.3** | Case-collision de-duplication (coordinated) | ⏳ Pending |
| **Post-cleanup** | Directory standards live; navigability improved | ⏳ Target Q3 2026 |

---

## 10. GOVERNANCE & MAINTENANCE

### 10.1 Change Control

**Adding new top-level directories:**
1. Document purpose in this file (Section 2)
2. Update `.codex/INDEX.md`
3. Submit PR with rationale
4. Approval required from repo maintainers

**Archiving existing directories:**
1. Validate no live imports (Section 5.2)
2. Plan archive destination (Section 4)
3. Execute as tracked git moves
4. Update archive inventory
5. Document in `.codex/archive/RETRIEVAL_GUIDE.md`

### 10.2 Periodic Review

**Quarterly:**
- Review `.codex/archive/temporary/` for time-scoped purge (>90 days)
- Check directory growth against limits (Table 2.2, 2.3, etc.)
- Validate archive inventory accuracy

---

## 11. SUCCESS CRITERIA (Post-Cleanup Validation)

| Criterion | Target | Owner | Validation |
|-----------|--------|-------|-----------|
| ✅ Top-level directories | ≤60 (was 107) | repo-org-agent | `ls -1d */ \| wc -l` |
| ✅ Loose root files | ≤20 (was 205) | repo-org-agent | `ls -1 /` + manual count |
| ✅ `.codex/` files | ≤2,500 (was 4,362) | repo-org-agent | `find .codex -type f \| wc -l` |
| ✅ Committed venvs | 0 (was 715) | repo-org-agent | `find venv* .venv* -type f \| wc -l` |
| ✅ Build artifacts tracked | 0 (was ~150) | repo-org-agent | `git ls-files --cached \| grep -E "(\.pyc\|__pycache__)` |
| ✅ Archive indexes complete | 100% | repo-org-agent | `jq '.' .codex/archive/INVENTORY.jsonl \| wc -l` |
| ✅ Case consistency | 100% | repo-org-agent | No CAPS-variant pairs |
| ✅ Import validation | All checked | Multi-agent (8.2.2-A) | Cross-ref report |

---

## 12. EXCEPTIONS & SPECIAL CASES

### 12.1 `.CODEX/` and `XX.codex/` Orphans

**Current:** Two stray directories (likely merge artifacts):
- `.CODEX/` → contains only `AGENT_MEMORY.DB`
- `XX.codex/` → contains only `agent_memory.dbXX`

**Plan:**
1. Investigate purpose (likely duplicate memory stores)
2. If abandoned: remove or consolidate into `.codex/cognitive_brain/`
3. If active: document ownership + consolidation rationale

### 12.2 Single-File Orphan Directories

**Current:** ~19 dirs with exactly 1 file each (e.g., `sentencepiece/`, `transformers/`, `omegaconf/`)

**Plan:**
1. Document purpose in `.codex/INDEX.md` (are they stubs? shims? legit?)
2. If legit shims: mark as such; document import path
3. If stray: move to `.codex/archive/temporary/` for 90-day review before removal

---

## 13. QUICK REFERENCE

### Post-Cleanup Directory Stats

| Metric | Pre | Target | Status |
|--------|-----|--------|--------|
| Total files | 17,081 | ≤12,000 | ⏳ TBD |
| Top-level dirs | 107 | ≤60 | ⏳ TBD |
| Root loose files | 205 | ≤20 | ⏳ TBD |
| `.codex/` files | 4,362 | ≤2,500 | ⏳ TBD |
| Venv files | 715 | 0 | ⏳ TBD |
| Archive index records | N/A | ~1,000 | ⏳ TBD |

---

## 14. RELATED DOCUMENTS

- **PHASE_8_2_CLEANUP_STRATEGY.md** — Cleanup approach & phased execution
- **PHASE_8_2_CLEANUP_PHASES.md** — Batch-by-batch execution plan
- **PHASE_8_1_*` (Track 8.1 docs)** — Documentation consolidation (parallel track)
- **PHASE_8_3_*` (Track 8.3 docs)** — Case-collision de-duplication (sequential track)
- **.codex/INDEX.md** — Master metadata index (live doc)
- **.codex/archive/RETRIEVAL_GUIDE.md** — Archive retrieval (post-cleanup)

---

*Standards document generated 2026-07-03 by repository-organization-agent (Track 8.2 lead). Feeds WS 8.2.3 (Execution & Validation). Updates this document as cleanup progresses.*
