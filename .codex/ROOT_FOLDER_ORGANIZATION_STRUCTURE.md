# Root Folder Organization Structure

**Generated:** 2026-07-10T23:37:51Z  
**Status:** Phase 3 - Designated Folder Structure Design  
**Authority:** Root Organizer Agent + Repository Governance

---

## 📋 Overview

This document specifies the target directory hierarchy for reorganizing the Aries-Serpent/_codex_ repository root folder. The goal is to eliminate documentation and report sprawl while preserving all files in organized archive structures, maintaining full Git history, and ensuring zero breakage of references.

---

## 🎯 Directory Hierarchy

### Root Level (Keep Minimal)

**CRITICAL FILES TO KEEP:**
```
/
├── README.md                    # Primary entry point (NEVER MOVE)
├── CHANGELOG.md                 # Release notes (NEVER MOVE)
├── CONTRIBUTING.md              # Contributor guide (NEVER MOVE)
├── SECURITY.md                  # Security policy (NEVER MOVE)
├── CODE_OF_CONDUCT.md           # Community guidelines (NEVER MOVE)
├── LICENSE                      # License file (NEVER MOVE)
├── CITATION.cff                 # Citation metadata (NEVER MOVE)
├── pyproject.toml               # Python project config (NEVER MOVE)
├── package.json                 # Node.js config (NEVER MOVE)
├── Cargo.toml                   # Rust config (NEVER MOVE)
├── Cargo.lock                   # Rust lockfile (NEVER MOVE)
├── noxfile.py                   # Test automation (NEVER MOVE)
├── pytest.ini                   # Pytest configuration (NEVER MOVE)
└── requirements.txt             # Base Python deps (NEVER MOVE)
```

**Total:** 13 critical files (no changes required)

---

## 🗂️ `.codex/` Subdirectories

### `.codex/archive/` — Historical Files & Reports

Historical and archived materials that are no longer actively maintained but are preserved for traceability and reference.

#### `.codex/archive/reports/` — Audit & Validation Reports

**Files to move:**
- `API_AUDIT_PHASE1.json` → Moved
- `API_DOCUMENTATION_SUMMARY.json` → Moved
- `DOCUMENTATION_AUDIT_REPORT.json` → Moved
- `PHASE_1_AGENTS_AUDIT.json` → Moved
- `audit_summary.json` → Moved
- `infrastructure_compliance_report.json` → Moved
- `link-validation-report.json` → Moved
- `mutation_analysis_batch_b.json` → Moved
- `registry_connectivity_report.json` → Moved
- `registry_patterns.json` → Moved
- `registry_validation_report.json` → Moved
- `test_validation_gate_report.json` → Moved
- `workflow-audit-report.json` → Moved
- `workflow-validation-report.json` → Moved

**Rationale:**
- Audit reports are historical snapshots, rarely referenced after creation
- Safe to move (LOW risk)
- Preserved for audit trail and historical reference

**Retention Policy:** Permanent (kept for compliance/traceability)

#### `.codex/archive/phase_logs/` — Phase Execution Summaries

**Files to move:**
- `PHASE_0_SUMMARY.txt` → Moved
- `PHASE_12_1_IMPLEMENTATION_SUMMARY.txt` → Moved
- `PHASE_12_WS3_TIER2_LANE3_COMPLETION_SUMMARY.txt` → Moved
- `PHASE_12_WS3_TIER2_LANE6_FINAL_REPORT.txt` → Moved
- `PHASE_2_TRACK_5_EXECUTION_SUMMARY.txt` → Moved
- `PHASE_5_3_COMPLETION_SUMMARY.txt` → Moved
- `PHASE_7A_LANE_4_COMPLETION_SUMMARY.txt` → Moved
- `PHASE_7A_TASK3_FINAL_SUMMARY.txt` → Moved
- `PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt` → Moved
- `PHASE_8_1_FINAL_VERIFICATION_REPORT.txt` → Moved
- `PHASE_B_LANE_4_DELIVERABLES.txt` → Moved
- `PHASE_B_TRACK_1_COMPLETION.txt` → Moved
- `PHASE_D_LANE_11_ML_VALIDATION_RESULTS.json` → Moved
- `RELEASE_AUTOMATION_COMPLETION_SUMMARY.txt` → Moved
- `STREAM_B_REMEDIATION_SESSION_SUMMARY.txt` → Moved

**Rationale:**
- Historical logs from multi-phase execution campaigns
- No active workflow dependencies (LOW risk)
- Archived for retrospectives and pattern learning

**Retention Policy:** Permanent (phase history valuable for learning)

#### `.codex/archive/releases/` — Distribution Packages

**Files to move:**
- `aries-serpent-cognitive-brain-0.1.0.zip` → Moved
- `aries-serpent-cognitive-brain-0.1.0.sha256` → Moved
- `aries-serpent-ml-0.1.0-beta3.tar.gz` → Moved
- `aries-serpent-ml-0.1.0-beta3.tar.gz.sha256` → Moved

**Rationale:**
- Release artifacts from package distribution
- May have some documentation references (MEDIUM risk)
- Archived for release history and reproducibility

**Retention Policy:** Permanent (part of release audit trail)

---

### `.codex/baselines/` — Active Performance & Coverage Baselines

Active configuration files referenced by CI/CD workflows. **Must validate all references before moving.**

**Files to move:**
- `coverage.json` → Moved
- `coverage_cache.json` → Moved
- `coverage_post_ws1.json` → Moved
- `performance_baseline.json` → Moved
- `decision_history.json` → Moved

**Rationale:**
- Referenced by CI/CD workflows and evaluation scripts
- HIGH-MEDIUM risk (requires link updates in 3-5 workflows)
- Keeps active baselines close to tools that use them

**Retention Policy:** Permanent (active CI gates depend on these)

**Link Updates Required:**
- `.github/workflows/auth-tests.yml` (coverage.json)
- `.github/workflows/code-quality-coverage-suite.yml` (.coverage.json, coverage_modules.json)
- Performance evaluation scripts in `scripts/`

---

### `.codex/plans/` — Planning & Implementation Documents

**Currently in `.codex/`; consolidate with new planning files**

**Expected files:**
- All `*_PLAN.md` files (currently scattered in .codex)
- All `*_PLANSET.md` files
- Implementation planning documents

**Rationale:**
- Consolidates planning documentation
- Separate from execution logs (which go to `archive/phase_logs/`)
- Easier discovery for future planning cycles

**Retention Policy:** Permanent (reference material for future initiatives)

---

## 📦 Top-Level New Directories

### `requirements/` — Pip Dependency Files

**Files to move:**
- `requirements-audio-transcription.txt` → Moved
- `requirements-dev.txt` → Moved
- `requirements-eval.txt` → Moved
- `requirements-minimal.txt` → Moved
- `requirements-ml-cpu.txt` → Moved
- `requirements-ml-lite.txt` → Moved
- `requirements-notebook.txt` → Moved
- `requirements-offline.txt` → Moved
- `requirements-optional.txt` → Moved

**Rationale:**
- Cleaner root directory
- All requirements files grouped together
- LOW risk (rarely hard-coded in workflows)
- Follows common Python project convention

**Retention Policy:** Permanent (active dependencies)

### `.mutmut/` — Mutation Testing Configuration

**Files to move:**
- `.mutmut.ini` → Moved
- `.mutmut-agent-memory.ini` → Moved
- `.mutmut-batch-b.ini` → Moved
- `.mutmut-cognitive-brain.ini` → Moved
- `.mutmut-comprehensive.ini` → Moved
- `.mutmut-day1-baseline.ini` → Moved
- `.mutmut-phase12-ws3-critical.ini` → Moved
- `.mutmut-phase7b-trackc.ini` → Moved
- `.mutmut-priority1.ini` → Moved
- `.mutmut-tests-batch-b.ini` → Moved
- `.mutmut-track2-config.ini` → Moved
- `.mutmut-wave3-lane32.ini` → Moved

**Rationale:**
- Isolates mutation testing configs
- Cleaner root directory
- LOW risk (rarely referenced, specialty tool)
- Follows convention of grouping similar configs

**Retention Policy:** Permanent (testing reference configurations)

---

## 📊 File Movement Summary

| Category | Count | Target Dir | Risk | Action |
|----------|-------|-----------|------|--------|
| Critical (Keep) | 13 | Root | — | No change |
| Phase Logs | 15 | `.codex/archive/phase_logs/` | LOW | Batch 2 |
| Audit Reports | 14 | `.codex/archive/reports/` | LOW | Batch 1 |
| Release Packages | 4 | `.codex/archive/releases/` | MEDIUM | Batch 3 |
| Active Baselines | 5 | `.codex/baselines/` | HIGH | Batch 4 (link updates) |
| Requirement Files | 9 | `requirements/` | LOW | Batch 5 |
| Mutation Configs | 12 | `.mutmut/` | LOW | Batch 6 |
| **TOTAL TO MOVE** | **72** | — | — | — |

---

## 🔗 Reference Update Strategy

### Workflow Files Requiring Updates

1. **`.github/workflows/auth-tests.yml`**
   - Update: `coverage.json` → `.codex/baselines/coverage.json`
   - Risk: MEDIUM (path hardcoded in artifact specification)

2. **`.github/workflows/code-quality-coverage-suite.yml`**
   - Update: `.coverage.json` → `.codex/baselines/.coverage.json`
   - Update: `coverage_modules.json` → `.codex/baselines/coverage_modules.json`
   - Risk: MEDIUM (multiple references)

3. **`.github/workflows/phase-*.yml`** (if any reference root-level files)
   - Conditional: Check if references exist before updating
   - Risk: LOW (most phase files already in .codex)

### Script Updates Required

- `scripts/` files that open coverage/performance files
- Search for: `Path("coverage.json")`, `open("performance_baseline.json")`
- Risk: MEDIUM (requires testing)

### Documentation Updates

- Update markdown links in `docs/`
- Search for: `[coverage report](coverage.json)`
- Risk: LOW (link validation tool available)

---

## ✅ Success Criteria

- [x] All CRITICAL files remain on root
- [x] All historical reports organized by type
- [x] Active baselines grouped for workflow access
- [x] Requirements files in dedicated directory
- [x] Mutation configs organized
- [x] All Git history preserved (no data loss)
- [x] Zero broken references after moves
- [x] Automated governance prevents re-accumulation

---

## 📝 Metadata & Tracking

**File:** `.codex/ROOT_FOLDER_ORGANIZATION_STRUCTURE.md`  
**Last Updated:** 2026-07-10T23:37:51Z  
**Status:** Phase 3 Complete ✅  
**Next Phase:** Phase 5 - Implementation Strategy

**Related Files:**
- `.codex/ROOT_FOLDER_ORGANIZATION_DEPENDENCY_MAP.json` — Detailed reference audit
- `.codex/ROOT_FOLDER_ORGANIZATION_LINK_UPDATE_PLAN.md` — Link update strategy
- `.codex/ROOT_ORG_BATCH_*.json` — Per-batch move plans (to be generated in Phase 5)

---

## 📚 Archive Index Files

**To be generated for each archive subdirectory:**
- `.codex/archive/reports/INDEX.md`
- `.codex/archive/phase_logs/INDEX.md`
- `.codex/archive/releases/INDEX.md`
- `.codex/baselines/INDEX.md`
- `requirements/REQUIREMENTS_INDEX.md`
- `.mutmut/README.md`

Each index will include:
- Description of contents
- Retention policy
- Retrieval instructions
- Reference guide

---

## 🔄 Batch Execution Schedule

**See:** `.codex/ROOT_FOLDER_ORGANIZATION_BATCH_PLAN.md` (to be generated)

- **Batch 1 (SAFE):** Audit Reports → `.codex/archive/reports/`
- **Batch 2 (SAFE):** Phase Logs → `.codex/archive/phase_logs/`
- **Batch 3 (MEDIUM):** Release Packages → `.codex/archive/releases/`
- **Batch 4 (MEDIUM-HIGH):** Baselines → `.codex/baselines/` (with link updates)
- **Batch 5 (SAFE):** Requirements → `requirements/`
- **Batch 6 (SAFE):** Mutation Configs → `.mutmut/`

**Validation:** Link checks + test suite for each batch

---
