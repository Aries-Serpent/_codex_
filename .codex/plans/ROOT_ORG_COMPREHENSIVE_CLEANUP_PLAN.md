# Root Folder Comprehensive Cleanup & Organization Plan

**Version:** 2.0.0  
**Date:** 2026-02-06  
**Status:** 🔄 Ready for Execution  
**Physics Model:** Energy=5 (Zero-break guarantee)

---

## Executive Summary

This plan provides a comprehensive strategy for organizing the repository root folder, reducing clutter from **92 files and 86 directories** to a clean, maintainable structure. The plan prioritizes safety, validation, and zero downstream impact through incremental execution with automated rollback capabilities.

### Current State
- **92 files** in root (43 documentation, 29 config/build, 20 core files)
- **86 directories** in root
- Existing relocation plan shows **144 files already moved**, **12 remaining**
- Infrastructure already in place: `scripts/root_org/` with validation tools

### Goals
1. **Maintain only essential files in root** (≤15 files)
2. **Consolidate session reports** → `archive/sessions/`
3. **Organize documentation** → `docs/` with proper structure
4. **Move configuration** → appropriate config directories
5. **Ensure zero broken links** or downstream impact

---

## Phase 1: Current State Analysis ✅ COMPLETE

### Root Files Inventory (92 total)

#### Core Project Files (7) - ✅ KEEP IN ROOT
These are standard repository files that **MUST** stay in root:
- `README.md` - Main project documentation
- `LICENSE` - License file
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community standards
- `SECURITY.md` - Security policy
- `CITATION.cff` - Citation metadata

**Action:** No changes needed

---

#### Configuration Files (11) - ✅ KEEP IN ROOT (with validation)
These are standard tool configuration files that conventionally remain in root:
- `pyproject.toml` - Python project configuration
- `setup.cfg` - Python setup configuration
- `pytest.ini` - Pytest configuration
- `mypy.ini` - MyPy type checker config
- `mkdocs.yml` - Documentation build config
- `conftest.py` - Pytest configuration module
- `deny.toml` - Rust deny configuration
- `commitlint.config.mjs` - Commit lint config
- `package.json` - Node.js package definition
- `package-lock.json` - Node.js lock file
- `uv.lock` - Python uv lock file

**Action:** Keep in root (standard practice)
**Risk:** LOW (these files must be in root for tools to find them)

---

#### Build/Deploy Files (8) - ✅ KEEP IN ROOT
Standard build and deployment configuration files:
- `Makefile` - Build automation
- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-container config
- `dvc.yaml` - Data version control
- `noxfile.py` - Nox test automation
- `Cargo.toml` - Rust package manifest
- `Cargo.lock` - Rust lock file
- `MANIFEST.in` - Python package manifest

**Action:** Keep in root (standard practice)
**Risk:** LOW (tools expect these in root)

---

#### Requirements Files (9) - ⚠️ EVALUATE

Current structure:
- `requirements.txt` - Base requirements
- `requirements-dev.txt` - Development dependencies
- `requirements-test.txt` - Test dependencies
- `requirements-eval.txt` - Evaluation dependencies
- `requirements-minimal.txt` - Minimal installation
- `requirements-ml-cpu.txt` - ML CPU-only
- `requirements-ml-lite.txt` - ML lite version
- `requirements-notebook.txt` - Notebook dependencies
- `requirements-optional.txt` - Optional dependencies

**Options:**
1. **Keep in root** (common practice)
2. **Move to `requirements/`** directory (cleaner, but less standard)

**Recommendation:** Keep in root (standard Python practice)
**Action:** No changes
**Risk:** LOW

---

#### Session/Status Reports (27) - 🔴 MOVE TO ARCHIVE

These are temporary session tracking files that should be archived:

**Files to move to `archive/sessions/`:**
- `DELIVERABLES_SUMMARY.txt`
- `FINAL_VERIFICATION.md`
- `GEM_INSTRUCTIONS.md`
- `IMPLEMENTATION_PROGRESS_PHASE1.md`
- `IMPLEMENTATION_PROGRESS_PHASE2.md`
- `IMPLEMENTATION_PROGRESS_PHASE3.md`
- `NEXT_SESSION_INSTRUCTIONS.md`
- `PROJECT_COMPLETE_SUMMARY.md`
- `archive/sessions/2026-01/QUICK_REFERENCE.md`
- `QUICK_REFERENCE_SESSION_LOG_RETRIEVER.md`
- `SESSION_COMPLETE_PHASE1.md`
- `SESSION_COMPLETE_SUMMARY.md`
- `SESSION_DELIVERABLES_SUMMARY.md`
- `SKELETON_TEST_ENHANCEMENTS.md`
- `TEST_ENHANCEMENT_SUMMARY.txt`

**Files to move to `archive/reports/workflows/`:**
- `README_WORKFLOW_FIXES.md`
- `WORKFLOW_ANALYSIS_REPORT.md`
- `WORKFLOW_FAILURE_ANALYSIS.md`
- `WORKFLOW_FIXES_8be6870.md`
- `WORKFLOW_FIXES_APPLICATION_CHECKLIST.md`
- `WORKFLOW_FIXES_DIFF.md`
- `WORKFLOW_FIXES_INDEX.md`
- `archive/reports/workflows/WORKFLOW_FIXES_SUMMARY.md`
- `WORKFLOW_MONITORING_REPORT.md`
- `WORKFLOW_MONITORING_SESSION_2026_02_06.md`
- `WORKFLOW_STATUS_SUMMARY.md`
- `WORKFLOW_VERIFICATION_ANALYSIS.md`

**Risk Assessment:**
- Need to validate references before moving
- Most likely have 0-2 references (LOW risk)
- Some may be referenced from `.codex/` documentation

**Action:** Run validation → Move in batches of 10

---

#### Documentation Files - Special Cases

**.codex/archive/deprecated/AGENTS.md** - 🔴 HIGH RISK (293 references)
- **Current:** Root
- **Proposed:** `.github/agents/docs/.codex/archive/deprecated/AGENTS.md` OR `docs/agents/.codex/archive/deprecated/AGENTS.md`
- **Risk:** HIGH (293 references across codebase)
- **Action:**
  1. Run full reference scan
  2. Create automated update script for all 293 references
  3. Validate in staging before production
  4. Consider creating redirect/symlink for transition period

**docs/analysis/PR_3133_ANALYSIS.md** - ⚠️ MOVE
- **Current:** Root
- **Proposed:** `docs/analysis/PR_3133_ANALYSIS.md`
- **Risk:** LOW-MEDIUM (likely 1-5 references)
- **Action:** Validate → Move → Update references

---

#### Other Files (29) - Configuration & Tool Files

**Dotfiles to stay in root:**
Most of these are tool-specific configuration files that **must** remain in root:
- `.bandit`, `.bandit.yaml`, `.bandit.yml` - Security scanning config
- `.codex/archive/misc/.copilot-review-exclusions.md` - Copilot configuration
- `.coveragerc` - Code coverage config
- `.dockerignore` - Docker ignore patterns
- `.dvcignore` - DVC ignore patterns
- `.editorconfig` - Editor configuration
- `.env.docker.example`, `.env.example` - Environment templates
- `.fencefixer.yml` - Fence fixer config
- `.importlinter` - Import linter config
- `.markdown-link-check.json` - Link checker config
- `.mutmut-config.txt` - Mutation testing config
- `.mypy-baseline.txt` - MyPy baseline
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.pre-commit-hybrid.yaml` - Pre-commit alternative
- `.pre-commit-ruff.yaml` - Pre-commit Ruff config
- `.python-version` - Python version specification
- `.ruff.toml` - Ruff linter config
- `.secrets.baseline` - Secrets detection baseline
- `.security-exceptions.md` - Security exceptions
- `.semgrepignore` - Semgrep ignore patterns
- `.statusrc.json` - Status RC config
- `.yamllint.yml` - YAML linter config

**Action:** Keep in root (required by tools)
**Risk:** ZERO (no action taken)

**Data files to move:**
- `coverage_reports/coverage_tokenization.json` → `coverage_reports/coverage_reports/coverage_tokenization.json`
- `.codex/metrics/metrics_fallback.ndjson` → `.codex/metrics/.codex/metrics/metrics_fallback.ndjson`

**Scripts to move:**
- `prepare_notebooklm.sh` → `scripts/prepare_notebooklm.sh`

---

## Phase 2: Directory Analysis (86 total)

### Hidden Directories (keep in root)
- `.codeql` - CodeQL analysis cache
- `.codex` - Project codex (core infrastructure)
- `.copilot-space` - Copilot workspace
- `.github` - GitHub configuration (workflows, actions)
- `.hypothesis` - Hypothesis testing cache
- `.mlruns` - MLflow runs cache
- `.pre-commit-scripts` - Pre-commit hook scripts
- `.reports` - Test reports cache
- `.semgrep` - Semgrep rules
- `.vscode` - VS Code settings

**Action:** Keep (standard practice)

---

### Project Structure Directories (keep in root)
Core application and source directories:
- `src` - Source code
- `tests`, `tests_rust` - Test suites
- `docs` - Documentation
- `scripts` - Automation scripts
- `examples` - Example code
- `notebooks` - Jupyter notebooks

**Action:** Keep (standard project structure)

---

### Package Directories (keep in root)
Python package modules:
- `codex_addons`, `codex_digest`, `codex_ml`, `codex_regression`, `codex_utils`
- `cognitive`, `cognitive_app`
- `cli`

**Action:** Keep (these are likely importable packages)

---

### Questionable Directories - 🔴 EVALUATE

#### Duplicate/Unclear Purpose (17 directories)

**Potential duplicates to consolidate:**
1. `_codex` vs `.codex` vs `_codex_` - ⚠️ 3 similar directories
2. `config` vs `configs` vs `conf` vs `config_legacy` - ⚠️ 4 config directories
3. `agents` vs `.github/agents` (if it exists) - Potential duplication
4. `copilot` vs `.copilot-space` - Potential duplication
5. `analysis` vs `artifacts/analysis` - Potential duplication
6. `archive` - May have duplicated content

**Action Required:** Investigate contents and consolidate

#### Legacy/Deprecated Candidates
These may be outdated or no longer used:
- `audio_cleaner_v1` - Version-specific directory (v1 suggests outdated)
- `config_legacy` - Explicitly marked as legacy
- `yaml_legacy` - Explicitly marked as legacy
- `baseline` - Unclear purpose
- `benches` vs `benchmarks` - Duplication?
- `implementation_completed` - Archive candidate
- `omegaconf` - May be superseded by Hydra
- `patches` - May be outdated

**Action Required:** Validate usage → Archive if unused

#### Domain-Specific Directories
These appear project-specific and may need consolidation:
- `sentencepiece`, `tokenization`, `typer`, `transformers`, `torch` - ML-related
- `great_expectations` - Data validation framework
- `detectors` - Unclear purpose
- `manifests`, `mappings` - Could be consolidated
- `monitoring`, `metrics` (if separate) - Consolidation candidate
- `policies` - Could move to `.codex/policies` or `docs/policies`

**Action Required:** Review and potentially consolidate

---

## Phase 3: Strategic Consolidation Plan

### A. Configuration Consolidation

**Goal:** Unify fragmented configuration directories

**Current State:**
- `config/` (exists)
- `configs/` (exists)
- `conf/` (exists)
- `config_legacy/` (exists)

**Proposed Structure:**
```
config/
├── active/         # Current active configs
├── legacy/         # Deprecated configs (moved from config_legacy/)
├── templates/      # Configuration templates
└── environments/   # Environment-specific configs
```

**Migration Steps:**
1. ✅ Validate which configs are actively used
2. ✅ Merge `configs/` and `conf/` into `config/active/`
3. ✅ Move `config_legacy/` → `config/legacy/`
4. ✅ Update all config imports/references
5. ✅ Remove empty directories

**Risk:** MEDIUM (needs careful validation of imports)

---

### B. Codex Directory Consolidation

**Goal:** Eliminate confusion between `_codex`, `.codex`, `_codex_`

**Current State:**
- `.codex/` - Main codex with plans, reports, documentation
- `_codex/` - Purpose unclear
- `_codex_/` - Purpose unclear

**Proposed Action:**
1. ✅ Investigate contents of `_codex/` and `_codex_/`
2. ✅ Migrate unique content to `.codex/`
3. ✅ Remove duplicate directories
4. ✅ Update any references

**Risk:** LOW-MEDIUM (depends on what's in those directories)

---

### C. Session Reports Archival

**Goal:** Clean up 27 session/status report files

**Proposed Structure:**
```
archive/
├── sessions/
│   ├── 2026-01/
│   │   ├── IMPLEMENTATION_PROGRESS_PHASE1.md
│   │   ├── SESSION_COMPLETE_PHASE1.md
│   │   └── ...
│   └── 2026-02/
│       └── WORKFLOW_MONITORING_SESSION_2026_02_06.md
└── reports/
    └── workflows/
        ├── WORKFLOW_ANALYSIS_REPORT.md
        └── ...
```

**Migration Steps:**
1. ✅ Create directory structure
2. ✅ Validate references to each file (expect 0-2 refs)
3. ✅ Move in batches of 10
4. ✅ Update references atomically
5. ✅ Verify no broken links

**Risk:** LOW (most have 0 references)

---

### D. Documentation Structure Enhancement

**Goal:** Improve docs/ organization for archived content

**Current Structure:**
```
docs/
├── ... (existing structure)
└── archive/
    ├── phases/
    ├── sessions/
    └── misc/
```

**Proposed Addition:**
```
docs/
├── agents/           # NEW - Agent documentation
│   └── .codex/archive/deprecated/AGENTS.md     # Relocated from root (HIGH RISK)
├── analysis/         # NEW - Analysis documents
│   └── PR_3133_ANALYSIS.md
└── archive/          # Enhanced archival
    ├── phases/       # Already exists
    ├── sessions/     # Enhanced with recent sessions
    └── workflows/    # NEW - Workflow reports
```

**Risk:** MEDIUM (.codex/archive/deprecated/AGENTS.md has 293 references)

---

## Phase 4: Detailed Relocation Plan

### Priority 1: LOW Risk Moves (0 references)

**Batch 1 - Session Reports (10 files)**
```json
[
  {"source": "DELIVERABLES_SUMMARY.txt", "target": "archive/sessions/2026-01/DELIVERABLES_SUMMARY.txt"},
  {"source": "FINAL_VERIFICATION.md", "target": "archive/sessions/2026-01/FINAL_VERIFICATION.md"},
  {"source": "GEM_INSTRUCTIONS.md", "target": "archive/sessions/2026-01/GEM_INSTRUCTIONS.md"},
  {"source": "IMPLEMENTATION_PROGRESS_PHASE1.md", "target": "archive/sessions/2026-01/IMPLEMENTATION_PROGRESS_PHASE1.md"},
  {"source": "IMPLEMENTATION_PROGRESS_PHASE2.md", "target": "archive/sessions/2026-01/IMPLEMENTATION_PROGRESS_PHASE2.md"},
  {"source": "IMPLEMENTATION_PROGRESS_PHASE3.md", "target": "archive/sessions/2026-01/IMPLEMENTATION_PROGRESS_PHASE3.md"},
  {"source": "NEXT_SESSION_INSTRUCTIONS.md", "target": "archive/sessions/2026-01/NEXT_SESSION_INSTRUCTIONS.md"},
  {"source": "PROJECT_COMPLETE_SUMMARY.md", "target": "archive/sessions/2026-01/PROJECT_COMPLETE_SUMMARY.md"},
  {"source": "SESSION_COMPLETE_PHASE1.md", "target": "archive/sessions/2026-01/SESSION_COMPLETE_PHASE1.md"},
  {"source": "SESSION_COMPLETE_SUMMARY.md", "target": "archive/sessions/2026-01/SESSION_COMPLETE_SUMMARY.md"}
]
```

**Batch 2 - More Session Reports (10 files)**
```json
[
  {"source": "SESSION_DELIVERABLES_SUMMARY.md", "target": "archive/sessions/2026-01/SESSION_DELIVERABLES_SUMMARY.md"},
  {"source": "SKELETON_TEST_ENHANCEMENTS.md", "target": "archive/sessions/2026-01/SKELETON_TEST_ENHANCEMENTS.md"},
  {"source": "TEST_ENHANCEMENT_SUMMARY.txt", "target": "archive/sessions/2026-01/TEST_ENHANCEMENT_SUMMARY.txt"},
  {"source": "archive/sessions/2026-01/QUICK_REFERENCE.md", "target": "archive/sessions/2026-01/archive/sessions/2026-01/QUICK_REFERENCE.md"},
  {"source": "QUICK_REFERENCE_SESSION_LOG_RETRIEVER.md", "target": "archive/sessions/2026-01/QUICK_REFERENCE_SESSION_LOG_RETRIEVER.md"},
  {"source": "coverage_reports/coverage_tokenization.json", "target": "coverage_reports/coverage_reports/coverage_tokenization.json"},
  {"source": ".codex/metrics/metrics_fallback.ndjson", "target": ".codex/metrics/.codex/metrics/metrics_fallback.ndjson"},
  {"source": "prepare_notebooklm.sh", "target": "scripts/prepare_notebooklm.sh"},
  {"source": "README_WORKFLOW_FIXES.md", "target": "archive/reports/workflows/README_WORKFLOW_FIXES.md"},
  {"source": "WORKFLOW_ANALYSIS_REPORT.md", "target": "archive/reports/workflows/WORKFLOW_ANALYSIS_REPORT.md"}
]
```

**Batch 3 - Workflow Reports (10 files)**
```json
[
  {"source": "WORKFLOW_FAILURE_ANALYSIS.md", "target": "archive/reports/workflows/WORKFLOW_FAILURE_ANALYSIS.md"},
  {"source": "WORKFLOW_FIXES_8be6870.md", "target": "archive/reports/workflows/WORKFLOW_FIXES_8be6870.md"},
  {"source": "WORKFLOW_FIXES_APPLICATION_CHECKLIST.md", "target": "archive/reports/workflows/WORKFLOW_FIXES_APPLICATION_CHECKLIST.md"},
  {"source": "WORKFLOW_FIXES_DIFF.md", "target": "archive/reports/workflows/WORKFLOW_FIXES_DIFF.md"},
  {"source": "WORKFLOW_FIXES_INDEX.md", "target": "archive/reports/workflows/WORKFLOW_FIXES_INDEX.md"},
  {"source": "archive/reports/workflows/WORKFLOW_FIXES_SUMMARY.md", "target": "archive/reports/workflows/archive/reports/workflows/WORKFLOW_FIXES_SUMMARY.md"},
  {"source": "WORKFLOW_MONITORING_REPORT.md", "target": "archive/reports/workflows/WORKFLOW_MONITORING_REPORT.md"},
  {"source": "WORKFLOW_MONITORING_SESSION_2026_02_06.md", "target": "archive/reports/workflows/WORKFLOW_MONITORING_SESSION_2026_02_06.md"},
  {"source": "WORKFLOW_STATUS_SUMMARY.md", "target": "archive/reports/workflows/WORKFLOW_STATUS_SUMMARY.md"},
  {"source": "WORKFLOW_VERIFICATION_ANALYSIS.md", "target": "archive/reports/workflows/WORKFLOW_VERIFICATION_ANALYSIS.md"}
]
```

**Execution Command:**
```bash
cd /home/runner/work/_codex_/_codex_
python scripts/root_org/organize_root_incremental.py \
  --plan .codex/plans/ROOT_ORG_CLEANUP_BATCH_1.json \
  --batch 10 \
  --dry-run
```

---

### Priority 2: MEDIUM Risk Moves (1-5 references)

**File:** `docs/analysis/PR_3133_ANALYSIS.md`
- **Target:** `docs/analysis/PR_3133_ANALYSIS.md`
- **Expected Refs:** 1-3
- **Validation:** Run reference scan first
- **Action:** Automated move + reference update

**Execution Steps:**
1. Validate references: `python scripts/root_org/validate_references.py docs/analysis/PR_3133_ANALYSIS.md`
2. Execute move: `python scripts/root_org/organize_root_incremental.py --file docs/analysis/PR_3133_ANALYSIS.md --target docs/analysis/PR_3133_ANALYSIS.md`
3. Verify: Check all updated files

---

### Priority 3: HIGH Risk Moves (>5 references)

**File:** `.codex/archive/deprecated/AGENTS.md` - ⚠️ EXTREME CAUTION
- **Current:** Root
- **Target:** `docs/agents/.codex/archive/deprecated/AGENTS.md` (or `.github/agents/docs/.codex/archive/deprecated/AGENTS.md`)
- **References:** 293 (!!!)
- **Risk:** CRITICAL

**Special Handling Required:**

1. **Full Reference Audit**
   ```bash
   python scripts/root_org/validate_references.py .codex/archive/deprecated/AGENTS.md --json > agents_refs.json
   ```

2. **Create Update Script**
   - Build comprehensive reference map
   - Identify all link patterns
   - Plan atomic update strategy

3. **Testing Strategy**
   - Test on branch first
   - Validate build succeeds
   - Check documentation site
   - Verify all links work

4. **Phased Execution**
   - Phase 1: Create target file (copy, not move)
   - Phase 2: Update first 50% of references
   - Phase 3: Validate
   - Phase 4: Update remaining 50%
   - Phase 5: Remove source file
   - Phase 6: Final validation

5. **Rollback Plan**
   - Keep backup of all modified files
   - Document all changes
   - Have rollback script ready

**Alternative Approach: Symlink Transition**
```bash
# Phase 1: Copy file to new location
cp .codex/archive/deprecated/AGENTS.md docs/agents/.codex/archive/deprecated/AGENTS.md

# Phase 2: Update references gradually over time
# ...

# Phase 3: Once all refs updated, replace source with symlink
rm .codex/archive/deprecated/AGENTS.md
ln -s docs/agents/.codex/archive/deprecated/AGENTS.md .codex/archive/deprecated/AGENTS.md

# Phase 4: After transition period, remove symlink
rm .codex/archive/deprecated/AGENTS.md
```

---

## Phase 5: Validation & Testing Strategy

### Pre-Move Validation
For each file before moving:
1. ✅ Run reference scanner: `validate_references.py <file>`
2. ✅ Check if file is in git: `git ls-files <file>`
3. ✅ Verify target directory structure
4. ✅ Assess risk level (LOW/MEDIUM/HIGH)
5. ✅ Get approval if HIGH risk

### Post-Move Validation
For each file after moving:
1. ✅ Verify file exists at target: `test -f <target>`
2. ✅ Verify file removed from source: `! test -f <source>`
3. ✅ Check git status: `git status`
4. ✅ Run reference validator again
5. ✅ Validate no broken links: `scripts/validate_links.sh` (if exists)
6. ✅ Check documentation builds: `mkdocs build --strict`

### Batch Validation
After each batch of 10 files:
1. ✅ Run full link checker
2. ✅ Execute test suite (if critical files moved)
3. ✅ Verify documentation builds
4. ✅ Check CI passes
5. ✅ Review action log: `cat .codex/action_log.ndjson | tail -20`

### Final Validation
After all moves complete:
1. ✅ Full repository link check
2. ✅ Run all tests: `pytest`
3. ✅ Build documentation: `mkdocs build --strict`
4. ✅ Verify GitHub Actions workflows
5. ✅ Check import statements (Python)
6. ✅ Validate configuration files still found

---

## Phase 6: Rollback & Recovery

### Automatic Rollback Triggers
Rollback automatically if:
- Any git mv command fails
- Reference update fails
- Post-move validation fails
- Link checker finds broken links
- Build fails after move

### Manual Rollback
If issues detected later:
```bash
# Rollback last operation
python scripts/root_org/rollback_move.py --last-operation

# Rollback specific file
python scripts/root_org/rollback_move.py --file docs/sessions/SESSION_COMPLETE.md

# Rollback entire batch
python scripts/root_org/rollback_move.py --batch --commits rollback_batch_1.txt
```

### Recovery Verification
After rollback:
1. ✅ Verify files restored to original location
2. ✅ Check references are intact
3. ✅ Run validation suite
4. ✅ Review what went wrong
5. ✅ Update plan based on findings

---

## Phase 7: Execution Timeline

### Week 1: Preparation & LOW Risk
- **Day 1:** Review plan, validate tools
- **Day 2:** Execute Batch 1 (10 LOW risk files)
- **Day 3:** Validate, then Batch 2 (10 LOW risk files)
- **Day 4:** Validate, then Batch 3 (10 LOW risk files)
- **Day 5:** Final validation, commit

### Week 2: MEDIUM Risk & Directory Consolidation
- **Day 1:** Evaluate `_codex/` and `_codex_/` directories
- **Day 2:** Consolidate config directories
- **Day 3:** Move MEDIUM risk documentation files
- **Day 4:** Validate, fix any issues
- **Day 5:** Commit batch 2

### Week 3: HIGH Risk (if approved)
- **Day 1-2:** .codex/archive/deprecated/AGENTS.md reference audit
- **Day 3:** Create update script & test
- **Day 4:** Execute phased update
- **Day 5:** Final validation

---

## Phase 8: Success Metrics

### Quantitative Goals
- ✅ Reduce root files from 92 → ≤20
- ✅ Consolidate duplicate directories (4 config dirs → 1)
- ✅ Archive 27+ session report files
- ✅ Zero broken links after migration
- ✅ Zero failing tests after migration
- ✅ Documentation builds successfully

### Qualitative Goals
- ✅ Clear, intuitive root structure
- ✅ Easy for new contributors to navigate
- ✅ Consistent directory naming
- ✅ Well-documented archive structure
- ✅ All files in logical locations

### Health Metrics
Track these throughout:
- Link check pass rate: 100%
- Test pass rate: 100%
- Build success rate: 100%
- CI workflow pass rate: 100%
- Reference update success rate: ≥95%

---

## Phase 9: Risk Assessment Summary

### Overall Risk: MEDIUM

**Risk Factors:**
1. ✅ HIGH: .codex/archive/deprecated/AGENTS.md has 293 references (requires special handling)
2. ⚠️ MEDIUM: Config directory consolidation (import updates needed)
3. ⚠️ MEDIUM: Unknown directory contents (`_codex`, `_codex_`)
4. ✅ LOW: Most files have 0 references
5. ✅ LOW: Infrastructure already exists and tested

**Mitigation Strategies:**
1. ✅ Incremental execution (10 files at a time)
2. ✅ Automated validation before/after each move
3. ✅ Automatic rollback on failure
4. ✅ Dry-run mode for all operations
5. ✅ Comprehensive logging to NDJSON
6. ✅ Manual approval for HIGH risk moves
7. ✅ Phased execution for .codex/archive/deprecated/AGENTS.md

**Confidence Level:** HIGH
- Existing tools are production-ready
- Physics Model compliance (Energy=5)
- Prior successful execution (144 files already moved)
- Clear rollback procedures

---

## Phase 10: Next Steps

### Immediate Actions (This Session)
1. ✅ Review and approve this plan
2. ✅ Validate reference scanner works: Test on 3 files
3. ✅ Execute Batch 1 (dry-run first)
4. ✅ If successful, execute Batch 1 (real)
5. ✅ Validate results

### Follow-up Actions (Next Session)
1. ⏳ Execute Batch 2 and 3
2. ⏳ Directory consolidation investigation
3. ⏳ MEDIUM risk file moves
4. ⏳ Prepare .codex/archive/deprecated/AGENTS.md migration plan

### Future Enhancements
1. 💡 Automated reference update in CI
2. 💡 Link checker in pre-commit hooks
3. 💡 Regular root cleanup audits
4. 💡 Documentation structure governance

---

## Appendix A: Tool Commands Reference

### Validation
```bash
# Validate single file
python scripts/root_org/validate_references.py <file> [--dry-run] [--json]

# Get risk assessment
python scripts/root_org/validate_references.py <file>
# Exit code: 0=LOW, 1=MEDIUM, 2=HIGH
```

### Moving Files
```bash
# Single file move (with validation)
python scripts/root_org/organize_root_incremental.py \
  --file <source> \
  --target <target> \
  [--dry-run]

# Batch move from plan
python scripts/root_org/organize_root_incremental.py \
  --plan <plan.json> \
  --batch <n> \
  [--risk LOW|MEDIUM|HIGH] \
  [--dry-run]
```

### Reference Updates
```bash
# Update references (standalone)
python scripts/root_org/update_links_atomic.py \
  --old <old_path> \
  --new <new_path> \
  [--dry-run]
```

### Rollback
```bash
# Rollback last operation
python scripts/root_org/rollback_move.py --last-operation

# Rollback specific file
python scripts/root_org/rollback_move.py --file <file> [--commit <sha>]
```

### Logging
```bash
# View recent operations
tail -20 .codex/action_log.ndjson | jq .

# Filter by action type
grep "organize_root_incremental" .codex/action_log.ndjson | jq .
```

---

## Appendix B: File Relocation Index

### Files to Keep in Root (≤20)

**Essential (7):**
- README.md
- LICENSE
- CHANGELOG.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- CITATION.cff

**Configuration (11):**
- pyproject.toml, setup.cfg, pytest.ini, mypy.ini
- mkdocs.yml, conftest.py, deny.toml
- commitlint.config.mjs
- package.json, package-lock.json, uv.lock

**Build (8):**
- Makefile, Dockerfile, docker-compose.yml
- dvc.yaml, noxfile.py
- Cargo.toml, Cargo.lock, MANIFEST.in

**Requirements (9):**
- requirements*.txt (9 files)

**Total:** 35 files (target: reduce by finding consolidation opportunities)

### Files to Move (30+)

**Session Reports → archive/sessions/2026-01/ (15 files)**
**Workflow Reports → archive/reports/workflows/ (12 files)**
**Documentation → docs/analysis/ (1 file)**
**Data → appropriate dirs (3 files)**

---

## Appendix C: Directory Consolidation Map

### Config Consolidation
```
Before:
  /config
  /configs
  /conf
  /config_legacy

After:
  /config
    /active     (merged from configs, conf)
    /legacy     (from config_legacy)
    /templates
```

### Codex Consolidation
```
Before:
  /.codex     (main)
  /_codex     (unclear)
  /_codex_    (unclear)

After:
  /.codex     (unified)
```

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-21 | Initial plan | Prior session |
| 2.0.0 | 2026-02-06 | Complete rewrite with current state | Root Org Agent |

---

**Status:** 🟢 Ready for execution  
**Next Action:** Validate 3 files, then execute Batch 1 (dry-run)  
**Approval Required:** HIGH risk moves (.codex/archive/deprecated/AGENTS.md)  
**Physics Model:** ⚖️ Balance - Zero-break guarantee paramount
