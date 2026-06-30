# ROOT FOLDER REORGANIZATION — EXECUTION CHECKLIST

**Status:** PLANNING COMPLETE  
**Plan Document:** `.codex/ROOT_FOLDER_REORGANIZATION_PLAN.md`  
**Created:** 2026-06-30T16:15:44Z

---

## PHASE 0: ANALYSIS & CATEGORIZATION — STATUS ✅ COMPLETE

### Deliverables

- [x] File inventory completed: **285+ files catalogued**
- [x] 8+ categories identified
- [x] Files designated for root: **6-7 core files** (vs. 285+ current)
- [x] Target folder structure designed
- [x] Risk assessment completed for each file group

### Files Designated to REMAIN in Root

```
✅ KEEP (6 files):
   1. README.md
   2. LICENSE
   3. CITATION.cff
   4. CODE_OF_CONDUCT.md
   5. SECURITY.md
   6. CONTRIBUTING.md
   7. pyproject.toml
```

### Files to Move by Category

| Category | Count | Target Folder | Risk |
|----------|-------|---|---|
| **Configuration** | 41 | `.config/` | HIGH |
| **Environment** | 7 | `.env/` | LOW |
| **Build Artifacts** | 18 | `.build/` | LOW |
| **Documentation** | 52 | `.docs/` | MEDIUM |
| **Workflow Reports** | 78 | `.codex/phase-reports/` | LOW |
| **Mutation Testing** | 14 | `.codex/mutation-testing/` | LOW |
| **Security Reports** | 21 | `.codex/security-reports/` | LOW |
| **Python Scripts** | 8 | `scripts/utilities/` | MEDIUM |
| **Temporary/Session** | 42 | `.codex/temp/` or `.codex/sessions/` | LOW |
| **TOTAL RELOCATIONS** | **281 files** | **8+ target folders** | **See matrix** |

---

## PHASE 1: PRE-MIGRATION VALIDATION — READY FOR EXECUTION

### Pre-Migration Validation Tasks

- [ ] **Step 1.1: Link Inventory Audit**
  - [ ] Search Python code for root file references
  - [ ] Search GitHub Actions workflows for root file references
  - [ ] Search documentation for hard-coded references
  - [ ] Search shell scripts for root file dependencies
  - **Output:** Link dependency matrix (store in `.codex/validation/link_dependencies.json`)

- [ ] **Step 1.2: Process Dependency Analysis**
  - [ ] Audit build pipeline (noxfile, pyproject.toml, pytest)
  - [ ] Audit CI workflows (.github/workflows/*.yml)
  - [ ] Audit package installation (pip install -e .)
  - [ ] Audit testing infrastructure (pytest, conftest.py, coverage)
  - **Output:** Process dependency matrix (store in `.codex/validation/process_dependencies.json`)

- [ ] **Step 1.3: Reference Update Strategy**
  - [ ] Document all reference update patterns
  - [ ] Create migration scripts for automatic updates
  - [ ] Plan manual updates (if needed)
  - **Output:** Reference patterns map (store in `.codex/validation/reference_patterns.md`)

### Pre-Execution Validation

- [ ] Establish baseline metrics:
  - [ ] Count of root files: **285+**
  - [ ] Test discovery count: `pytest --collect-only -q | wc -l`
  - [ ] Import test: `python -c "from codex import *"` passes
  - [ ] Workflow lint: `yamllint .github/workflows/*.yml` passes
  - [ ] Coverage baseline: `pytest --cov=src --cov-report=term | grep TOTAL`

---

## PHASE 2: FOLDER STRUCTURE DESIGN — COMPLETE

### Target Folder Architecture Finalized

```
✅ .config/                  [41 files → configuration tools]
✅ .env/                     [7 files → secrets & environment]
✅ .build/                   [18 files → locks & manifests]
✅ .docs/                    [52 files → documentation archive]
✅ .codex/phase-reports/     [78 files → phase execution]
✅ .codex/security-reports/  [21 files → security audits]
✅ .codex/mutation-testing/  [14 files → mutation configs]
✅ .codex/temp/              [42 files → session artifacts]
✅ scripts/utilities/        [8 files → utility scripts]
```

### Configuration Complete

- [x] Folder creation order determined (bottom-up: .config/ first, `.codex/*` last)
- [x] File move order determined (low-risk → medium-risk → high-risk)
- [x] Symlink strategy defined (if needed for pytest/pre-commit compatibility)
- [x] Fallback plan documented for each risk level

---

## PHASE 3A: EXECUTION — LOW-RISK FILES (Configuration & Build)

### Phase 3A Target: 66 files (`.config/`, `.env/`, `.build/`)

**Status:** ⏳ READY TO EXECUTE (Session 2 or later)

#### Configuration Files (41 files → `.config/`)

- [ ] Create `.config/` folder and git-track it
- [ ] Move pytest configuration:
  - [ ] `pytest.ini` → `.config/pytest.ini`
  - [ ] `conftest.py` → `.config/conftest.py` (if no test-specific imports)
- [ ] Move mypy configuration:
  - [ ] `mypy.ini` → `.config/mypy.ini`
  - [ ] `.mypy_baseline` → `.config/.mypy_baseline` (optional)
  - [ ] `.mypy-baseline.txt` → `.config/.mypy-baseline.txt` (optional)
- [ ] Move coverage configuration:
  - [ ] `.coveragerc` → `.config/.coveragerc`
- [ ] Move linting configuration:
  - [ ] `.ruff.toml` → `.config/.ruff.toml`
  - [ ] `.bandit*` → `.config/security/`
- [ ] Move pre-commit configuration:
  - [ ] `.pre-commit-config.yaml` → `.config/.pre-commit-config.yaml`
  - [ ] `.pre-commit-*.yaml` → `.config/`
- [ ] Move linting configuration:
  - [ ] `.markdownlintrc` → `.config/.markdownlintrc`
  - [ ] `.yamllint.yml` → `.config/.yamllint.yml`
- [ ] Move editor configuration:
  - [ ] `.editorconfig` → `.config/.editorconfig`
- [ ] Move semantic analysis:
  - [ ] `.semgrepignore` → `.config/.semgrepignore`
- [ ] Move documentation configuration:
  - [ ] `mkdocs.yml` → `.config/mkdocs.yml`
- [ ] Move Docker configuration:
  - [ ] `Dockerfile` → `.config/docker/Dockerfile`
  - [ ] `Dockerfile.optimized` → `.config/docker/Dockerfile.optimized`
  - [ ] `Dockerfile.preview` → `.config/docker/Dockerfile.preview`
  - [ ] `Dockerfile.restore` → `.config/docker/Dockerfile.restore`
  - [ ] `docker-compose.yml` → `.config/docker/docker-compose.yml`
  - [ ] `.dockerignore` → `.config/docker/.dockerignore`
- [ ] Move other configuration:
  - [ ] `.importlinter` → `.config/.importlinter`
  - [ ] `.fencefixer.yml` → `.config/.fencefixer.yml`
  - [ ] `.markdown-link-check.json` → `.config/.markdown-link-check.json`
  - [ ] `.statusrc.json` → `.config/.statusrc.json`

#### Environment & Secrets (7 files → `.env/`)

- [ ] Create `.env/` folder
- [ ] Move environment examples:
  - [ ] `.env.example` → `.env/.env.example`
  - [ ] `.env.docker.example` → `.env/.env.docker.example`
- [ ] Move secrets baseline:
  - [ ] `.secrets.baseline` → `.env/.secrets.baseline`
  - [ ] `.secrets.new.baseline` → `.env/.secrets.new.baseline`
- [ ] Move security allowlist:
  - [ ] `security_allowlist.json` → `.env/security_allowlist.json`

#### Build Artifacts & Locks (18 files → `.build/`)

- [ ] Create `.build/` folder
- [ ] Move package locks:
  - [ ] `package-lock.json` → `.build/package-lock.json`
  - [ ] `uv.lock` → `.build/uv.lock`
  - [ ] `Cargo.lock` → `.build/Cargo.lock`
- [ ] Move DVC & params:
  - [ ] `dvc.yaml` → `.build/dvc.yaml`
  - [ ] `params.yaml` → `.build/params.yaml`
- [ ] Move manifests:
  - [ ] `CODEX_MANIFEST.json` → `.build/manifests/CODEX_MANIFEST.json`
  - [ ] `CODEX_MANIFEST.json.pr5000` → `.build/manifests/CODEX_MANIFEST.json.pr5000`
- [ ] Move SBOM:
  - [ ] `sbom.json` → `.build/sbom.json`
  - [ ] `sbom-security-packages.json` → `.build/sbom-security-packages.json`

#### Phase 3A Validation

- [ ] **All files moved successfully**
  - [ ] `git status` shows clean working directory
  - [ ] `.config/`, `.env/`, `.build/` all exist with expected files

- [ ] **Update all references** (use scripts from Phase 1.3)
  - [ ] Python imports validated
  - [ ] Workflow YAML paths updated
  - [ ] Config file paths updated in workflows

- [ ] **Run validation suite**
  - [ ] `python -m py_compile src/ tests/` — no syntax errors
  - [ ] `pytest --collect-only -q | wc -l` — matches baseline count
  - [ ] `python -c "from codex import *"` — imports work
  - [ ] `yamllint .github/workflows/*.yml` — workflow syntax valid
  - [ ] `pip install -e . --dry-run` — package installation OK

- [ ] **Commit Phase 3A**
  - [ ] Commit message: `Relocate: Configuration, environment, and build files to dedicated folders`
  - [ ] All Phase 3A files in single commit (or grouped by subfolder)

---

## PHASE 3B: EXECUTION — MEDIUM-RISK FILES (Reports & Security)

### Phase 3B Target: 99 files (`.codex/phase-reports/`, `.codex/security-reports/`, `.codex/mutation-testing/`)

**Status:** ⏳ READY TO EXECUTE (Session 3 or later)

#### Workflow Reports (78 files → `.codex/phase-reports/`)

- [ ] Create `.codex/phase-reports/` with subfolders:
  - [ ] `phase1/`, `phase3/`, `phase5/`, `phase6/`, `phase7/`, `phase8/`, `phase9/`, `phase_b_d/`
- [ ] Move files:
  - [ ] `PHASE_*_*.md` → `.codex/phase-reports/phase*/`
  - [ ] `WAVE_*.md` → `.codex/phase-reports/`
  - [ ] `AUDIT_*.md` → `.codex/phase-reports/audit/`
  - [ ] `*_EXECUTION_SUMMARY.md` → `.codex/phase-reports/`

#### Security Reports (21 files → `.codex/security-reports/`)

- [ ] Create `.codex/security-reports/` with subfolders:
  - [ ] `codeql/`, `semgrep/`, `bandit/`, `remediation-plans/`, `compliance/`
- [ ] Move files:
  - [ ] `SECURITY_*.md` → `.codex/security-reports/`
  - [ ] `SEMGREP_*.md` → `.codex/security-reports/semgrep/`
  - [ ] `remediation_plan_*.md` → `.codex/security-reports/remediation-plans/`
  - [ ] `auth-security-report.json` → `.codex/security-reports/auth/`
  - [ ] `infrastructure_compliance_report.json` → `.codex/security-reports/compliance/`

#### Mutation Testing (14 files → `.codex/mutation-testing/`)

- [ ] Create `.codex/mutation-testing/` with subfolders:
  - [ ] `configs/`, `output/`, `baselines/`
- [ ] Move files:
  - [ ] `.mutmut.ini` → `.codex/mutation-testing/configs/.mutmut.ini`
  - [ ] `.mutmut*.ini` → `.codex/mutation-testing/configs/`
  - [ ] `mutmut_output.txt` → `.codex/mutation-testing/output/mutmut_output.txt`
  - [ ] `.mutmut-*-baseline.ini` → `.codex/mutation-testing/baselines/`

#### Phase 3B Validation

- [ ] **All files moved successfully**
- [ ] **Cross-references checked**
  - [ ] No broken links in moved `.md` files
  - [ ] References to reports still valid
- [ ] **Full test suite passes**
  - [ ] `pytest -x --tb=short` passes
  - [ ] No regressions in test count or coverage
- [ ] **Commit Phase 3B**
  - [ ] Commit message: `Relocate: Phase reports, security audits, and mutation testing configs`

---

## PHASE 3C: EXECUTION — HIGH-RISK FILES

### Phase 3C Target: ~35 files (`.codex/temp/`, `scripts/utilities/`, critical moves)

**Status:** ⏳ READY TO EXECUTE (Session 4 or later)

#### Temporary/Session Files (42 files → `.codex/temp/`)

- [ ] Create `.codex/temp/` folder
- [ ] Move session artifacts:
  - [ ] `.accountability_entry.txt` → `.codex/temp/.accountability_entry.txt`
  - [ ] `.changelog_entry.txt` → `.codex/temp/.changelog_entry.txt`
  - [ ] `sess_001` → `.codex/temp/sess_001`
  - [ ] `test_execution_log.txt` → `.codex/temp/test_execution_log.txt`
  - [ ] `test_results.txt` → `.codex/temp/test_results.txt`
  - [ ] `*.txt` (temporary reports) → `.codex/temp/`

#### Utility Scripts (8 files → `scripts/utilities/`)

- [ ] Create `scripts/utilities/` folder
- [ ] Move scripts:
  - [ ] `auto_suppress.py` → `scripts/utilities/auto_suppress.py`
  - [ ] `run_updates.sh` → `scripts/utilities/run_updates.sh`
  - [ ] `find_empty_funcs.py` → `scripts/utilities/find_empty_funcs.py`
  - [ ] `generate_*.py` → `scripts/utilities/`
  - [ ] `run_mutation_tests.py` → `scripts/utilities/run_mutation_tests.py`
  - [ ] `run_agent_memory_tests.py` → `scripts/utilities/run_agent_memory_tests.py`

#### Critical Moves (if applicable)

- [ ] **noxfile.py decision:**
  - [ ] IF: Keep in root — DECISION MADE ✅
  - [ ] IF: Move to `.config/` — Update import paths
- [ ] **conftest.py decision:**
  - [ ] IF: Moved to `.config/` in Phase 3A — Verify pytest discovery
  - [ ] IF: Stays in root — No action needed
- [ ] **Makefile decision:**
  - [ ] IF: Move to `.config/` — Update make invocations
  - [ ] IF: Delete (use noxfile) — Remove from git

#### Phase 3C Validation

- [ ] **pytest discovery still works**
  - [ ] `pytest --collect-only -q` returns expected count
  - [ ] `conftest.py` fixtures load correctly
- [ ] **All imports resolve**
  - [ ] `python -c "from codex import *"`
  - [ ] All modules importable from new locations
- [ ] **CI workflows pass**
  - [ ] `yamllint .github/workflows/*.yml` valid
  - [ ] Workflow runs on test commit
- [ ] **Commit Phase 3C**
  - [ ] Commit message: `Relocate: Session artifacts, utility scripts, and finalize root structure`

---

## PHASE 4: POST-MIGRATION VALIDATION & ISSUE RESOLUTION

### Comprehensive Validation (After Each Phase)

- [ ] **Code Quality Checks**
  - [ ] `python -m ruff check src/ tests/ --fix` — passes
  - [ ] `python -m mypy src/ tests/` — passes
  - [ ] `pre-commit run --all-files` — passes

- [ ] **Import Integrity**
  - [ ] `python -c "from codex import *"` — success
  - [ ] All submodules importable
  - [ ] No circular imports

- [ ] **Test Execution**
  - [ ] `pytest --collect-only -q | wc -l` — matches baseline
  - [ ] `pytest -x --tb=short` — all pass
  - [ ] Coverage maintained (if checked)

- [ ] **Workflow Validation**
  - [ ] `yamllint .github/workflows/*.yml` — valid
  - [ ] Workflow test on PR — passes

- [ ] **Git Integrity**
  - [ ] `git status` — clean
  - [ ] `git log --oneline` — commit chain intact
  - [ ] `git diff HEAD~1 HEAD` — expected changes only

### Common Issues & Immediate Resolutions

| Issue | Symptom | Resolution |
|---|---|---|
| pytest can't find conftest | `error: cannot collect tests` | Symlink or use `--confcutdir` |
| Import path broken | `ModuleNotFoundError` | Update PYTHONPATH in pytest.ini |
| Workflow can't find config | `file not found` | Update workflow working-directory |
| Link broken in docs | `[ref] → 404` | Run link validator + fix |
| pre-commit skipped | `hook skipped` | Update .pre-commit-config.yaml paths |
| Docker build fails | `COPY conftest.py: file not found` | Update Dockerfile |

### Issue Resolution Procedures

- [ ] **For Python Import Failures**
  - [ ] Run `python -m py_compile src/`
  - [ ] Identify module name conflicts
  - [ ] Update `sys.path` or imports
  - [ ] Re-run: `python -c "from codex import *"`

- [ ] **For Workflow Path Issues**
  - [ ] Search `.github/workflows/` for hardcoded paths
  - [ ] Update paths to use `.config/`, `.build/`, etc.
  - [ ] Run `yamllint` for syntax validation
  - [ ] Test on PR branch

- [ ] **For Documentation Links**
  - [ ] Run `python scripts/ci/link_validator.py --fix`
  - [ ] Manually verify important links
  - [ ] Preview on GitHub Pages (if applicable)

- [ ] **For pytest Discovery**
  - [ ] Check `conftest.py` location
  - [ ] Verify `pytest.ini` path configuration
  - [ ] Use `pytest --collect-only -q` to debug
  - [ ] Add `confcutdir=.config` if needed

---

## CRITICAL SAFEGUARDS

### Before Phase 3A Execution

- [ ] ⚠️ All Phase 1 validation complete (link inventory, process deps)
- [ ] ⚠️ All reference update scripts tested on dry run
- [ ] ⚠️ Git branch is clean (no uncommitted changes)
- [ ] ⚠️ Latest main branch merged in (if needed)
- [ ] ⚠️ Baseline metrics captured (test count, coverage, etc.)

### During Phase Execution

- [ ] ⚠️ Each file group gets single commit
- [ ] ⚠️ Commit message clearly states what moved
- [ ] ⚠️ No mixed "move" and "edit" in same commit
- [ ] ⚠️ Validation runs BEFORE commit
- [ ] ⚠️ If any validation fails → STOP, troubleshoot, commit fix

### After Each Phase

- [ ] ⚠️ Full validation suite passes
- [ ] ⚠️ All metrics match or exceed baseline
- [ ] ⚠️ CI workflows green (GitHub Actions pass)
- [ ] ⚠️ Document any issues found + fixes applied
- [ ] ⚠️ If critical issue found → git revert & replan

---

## SUCCESS CRITERIA

### Quantitative Targets

| Metric | Baseline | Target | Pass? |
|---|---|---|---|
| Root files | 285+ | 6-8 | ✅ |
| Broken links | 0 | 0 | ✅ |
| Tests discovered | 1500+ | 1500+ | ✅ |
| Coverage % | 90%+ | 90%+ | ✅ |
| CI pass rate | 95%+ | 95%+ | ✅ |
| Build time | baseline | ±5% baseline | ✅ |

### Qualitative Targets

- [ ] Root folder is "clean" (6-8 files visible)
- [ ] Folder structure is "self-documenting"
- [ ] Zero breaking changes to functionality
- [ ] All processes work seamlessly post-migration
- [ ] Documentation reflects new structure

---

## APPROVAL & EXECUTION AUTHORIZATION

- [ ] **Plan APPROVED by:** @mbaetiong (pending)
- [ ] **Execution AUTHORIZED:** (pending approval)
- [ ] **Phase 3A START DATE:** (to be scheduled)
- [ ] **Estimated Completion:** 3-4 sessions from Phase 3A start

**Current Status:** ✅ PLANNING COMPLETE, AWAITING APPROVAL

---

**Document Location:** `.codex/ROOT_FOLDER_REORGANIZATION_PLAN.md`  
**Execution Checklist:** `.codex/ROOT_FOLDER_REORGANIZATION_CHECKLIST.md` (this file)

