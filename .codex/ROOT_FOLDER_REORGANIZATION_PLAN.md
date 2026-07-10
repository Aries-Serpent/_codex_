# ROOT FOLDER REORGANIZATION IMPLEMENTATION PLAN

**Version:** 1.0  
**Created:** 2026-06-30T16:15:44Z  
**Status:** PLANNING PHASE (Not yet executed)  
**Scope:** Strategic reorganization of 285+ loose root files into appropriate folders  
**Risk Level:** HIGH (potential link breakage, process disruption)

---

## EXECUTIVE SUMMARY

The repository root contains **285+ files** across 8+ categories with no organization structure. This creates:
- **Navigation chaos** — difficult to locate project files vs. configuration vs. reports
- **Link fragility** — hard-coded root references that break when files move
- **CI complexity** — workflows must search root for configuration files
- **Maintenance burden** — unclear which files are critical vs. temporary

**Goal:** Reorganize into logical folders while maintaining **100% link integrity** and **zero process disruption**.

**Expected Timeline:** 3-4 phases over 2-3 sessions  
**Rollback Strategy:** Git history preserved; each phase independently reversible  

---

## PHASE 0: ANALYSIS & CATEGORIZATION

### Step 0.1: File Inventory & Classification

**Current Root File Count:** 285+ files

**Categories Identified:**

| Category | Count | Purpose | Planned Destination |
|----------|-------|---------|-------------------|
| **Core Project** | 4 | Project identity & governance | **KEEP IN ROOT** |
| **Documentation** | 52 | User guides, specifications | `.docs/` (new) |
| **Configuration** | 41 | Build, linting, version mgmt | `.config/` (new) |
| **Workflow Reports** | 78 | Phase execution, audit trails | `.codex/phase-reports/` |
| **Mutation Testing** | 14 | Mutation config & output | `.codex/mutation-testing/` |
| **Security Reports** | 21 | Audit, remediation, scanning | `.codex/security-reports/` |
| **Python Scripts** | 8 | Root-level utility scripts | `scripts/utilities/` |
| **Environment Files** | 7 | Docker, DVC, local config | `.env/` (new) |
| **Temporary/Session** | 42 | Session outputs, temp reports | `.codex/sessions/` or `.codex/temp/` |
| **Build Artifacts** | 18 | Lock files, manifests, caches | `.build/` (new) |

### Step 0.2: Files Designated for Root (KEEP ONLY 4-6)

These are **project-critical** and must remain in root:

```
✅ MUST STAY IN ROOT:
├── README.md                 # Project entry point
├── LICENSE                   # Legal requirement
├── CITATION.cff              # Academic citation (GitHub Pages integration)
├── CODE_OF_CONDUCT.md        # Community standards (GitHub auto-detection)
├── SECURITY.md               # Security policy (GitHub auto-detection)
├── CONTRIBUTING.md           # Contribution guidelines (GitHub Pages)
└── pyproject.toml            # Python package root (PEP 517 standard)
```

**Rationale:**
- `README.md`, `LICENSE`: GitHub repository standards (non-negotiable)
- `CODE_OF_CONDUCT.md`, `SECURITY.md`: GitHub auto-detects in root
- `CONTRIBUTING.md`: Community standard location
- `pyproject.toml`: Python packaging standard (root is canonical location)

---

## PHASE 1: PRE-MIGRATION VALIDATION (DRY RUN)

### Step 1.1: Link Inventory Audit

**Objective:** Identify ALL hard-coded root file references before moving files.

**Action Items:**

1. **Search all code for root file references:**
   ```bash
   # Find .py references to root files
   grep -r "^from \|import " src/ tests/ --include="*.py" | grep -E "\.\./" | grep -v "__pycache__"
   
   # Find hard-coded file paths in Python
   grep -r "^\s*open\(|^\s*Path\(" src/ tests/ --include="*.py" | grep -v "\.git"
   ```

2. **Search all workflows for root file references:**
   ```bash
   # GitHub Actions workflow dependencies on root files
   grep -r "working-directory\|with:" .github/workflows/ --include="*.yml" | grep -v ".github"
   ```

3. **Search all documentation for hard-coded references:**
   ```bash
   # Markdown links to root files
   grep -r "\[.*\](\./" docs/ .codex/ --include="*.md" | head -100
   ```

4. **Search shell scripts for root dependencies:**
   ```bash
   # Shell script dependencies
   grep -r "^\s*source.*\.|^\s*\.\s" scripts/ --include="*.sh"
   ```

**Expected Output:** Link dependency matrix documenting:
- File path
- Referenced location
- Type (code, workflow, docs, script)
- Update strategy

### Step 1.2: Process Dependency Analysis

**Objective:** Identify CI/CD processes that depend on root file locations.

**Critical Workflows to Audit:**

1. **Build Pipeline**
   - `noxfile.py` → pytest discovery → requires `pytest.ini` in root?
   - `pyproject.toml` usage across tools
   - `.pre-commit-config.yaml` → pre-commit hooks (root detection?)

2. **CI Workflows**
   - `.github/workflows/*.yml` — scan for file path assumptions
   - Look for: `ls -la .`, `find . -maxdepth 1`, hardcoded `./conftest.py`

3. **Package Installation**
   - `pip install -e .` → reads `pyproject.toml` from root
   - Docker builds → `COPY . /app` assumes root structure

4. **Testing**
   - `pytest` discovery → `conftest.py` in root (convention)
   - Coverage config → `.coveragerc` location

**Output:** Process dependency matrix listing:
- Process name
- Root file dependencies
- Likelihood of breakage
- Mitigation strategy

### Step 1.3: Reference Update Strategy

**For each identified reference, create update plan:**

| Reference Type | Current Pattern | New Pattern | Tool |
|---|---|---|---|
| Python imports | `from scripts import ...` | `from scripts.utilities import ...` | Manual + tests |
| Workflow paths | `./conftest.py` | `.github/workflows/runner-setup/conftest.py` | sed/perl |
| Doc links | `[ref](./CHANGELOG.md)` | `[ref](./docs/archive/CHANGELOG.md)` | script + validation |
| Config files | `pytest --config=pytest.ini` | `pytest --config=.config/pytest.ini` | workflow edit |

---

## PHASE 2: FOLDER STRUCTURE DESIGN

### Step 2.1: Target Folder Architecture

```
Aries-Serpent/_codex_/
│
├── [ROOT — Project Essential Files]
│   ├── README.md
│   ├── LICENSE
│   ├── CITATION.cff
│   ├── CODE_OF_CONDUCT.md
│   ├── SECURITY.md
│   ├── CONTRIBUTING.md
│   └── pyproject.toml
│
├── .config/                          [NEW — Build & Tool Configuration]
│   ├── pytest.ini
│   ├── mypy.ini
│   ├── .coveragerc
│   ├── .ruff.toml
│   ├── .bandit.yaml
│   ├── .pre-commit-config.yaml
│   ├── .markdownlintrc
│   ├── .yamllint.yml
│   ├── .editorcofig
│   ├── .semgrepignore
│   ├── mkdocs.yml
│   ├── conftest.py (if generic)
│   └── docker/
│       ├── Dockerfile
│       ├── Dockerfile.optimized
│       ├── docker-compose.yml
│       └── .dockerignore
│
├── .env/                              [NEW — Environment & Secrets]
│   ├── .env.example
│   ├── .env.docker.example
│   ├── .secrets.baseline
│   ├── .secrets.new.baseline
│   └── security_allowlist.json
│
├── .build/                            [NEW — Build Artifacts & Locks]
│   ├── package-lock.json
│   ├── uv.lock
│   ├── Cargo.lock
│   ├── dvc.yaml
│   ├── params.yaml
│   ├── sbom.json
│   ├── sbom-security-packages.json
│   └── manifests/
│       ├── CODEX_MANIFEST.json
│       ├── CODEX_MANIFEST.json.pr5000
│       └── *_MANIFEST.json
│
├── .docs/                             [NEW — Documentation Archive]
│   ├── archive/
│   │   ├── CHANGELOG.md
│   │   ├── CHANGELOG.md.pr5000
│   │   ├── .codex/archive/deprecated/AGENTS.md
│   │   └── .codex/archive/deprecated/CLAUDE.md (removed)
│   ├── guides/
│   │   └── [existing docs/ content moves here]
│   ├── specifications/
│   │   ├── .codex/archive/misc/DEPENDENCY_CONSTRAINTS.md
│   │   └── [spec docs]
│   └── reports/
│       ├── audit/
│       ├── security/
│       └── phase-completion/
│
├── .codex/                            [EXISTING — Enhanced]
│   ├── phase-reports/                 [NEW — Phase Execution Reports]
│   │   ├── phase1/
│   │   ├── phase3/
│   │   ├── phase5/
│   │   ├── phase6/
│   │   ├── phase7/
│   │   ├── phase8/
│   │   ├── phase9/
│   │   └── phase_b_d/
│   │
│   ├── security-reports/              [NEW — Security Audits]
│   │   ├── codeql/
│   │   ├── semgrep/
│   │   ├── bandit/
│   │   ├── remediation-plans/
│   │   └── compliance/
│   │
│   ├── mutation-testing/              [NEW — Mutation Testing Config]
│   │   ├── configs/
│   │   │   ├── .mutmut.ini
│   │   │   ├── .mutmut-comprehensive.ini
│   │   │   └── [other .mutmut-*.ini]
│   │   ├── output/
│   │   │   └── mutmut_output.txt
│   │   └── baselines/
│   │       ├── .mutmut-day1-baseline.ini
│   │       └── [other baselines]
│   │
│   ├── temp/                          [NEW — Temporary Session Files]
│   │   ├── .accountability_entry.txt
│   │   ├── .changelog_entry.txt
│   │   └── [session-specific outputs]
│   │
│   └── [existing .codex content]
│
├── scripts/
│   ├── utilities/                     [NEW — Root Utility Scripts]
│   │   ├── auto_suppress.py
│   │   ├── run_updates.sh
│   │   ├── find_empty_funcs.py
│   │   ├── generate_phase5_validation.py
│   │   └── [other utility scripts]
│   │
│   ├── phase-automation/              [NEW — Phase Execution]
│   │   ├── phase7b_trackc_generate_report.py
│   │   ├── phase7b_trackc_mutation_runner.py
│   │   └── phase7b_trackc_strategic_analysis.py
│   │
│   └── [existing scripts/ content]
│
└── [existing directories]
    ├── src/
    ├── tests/
    ├── docs/
    ├── .github/
    └── ...
```

### Step 2.2: Critical Files Reorganization Map

| Current Location | New Location | Type | Reason | Risk |
|---|---|---|---|---|
| `README.md` | **KEEP** | Essential | GitHub auto-detection | ❌ NONE |
| `LICENSE` | **KEEP** | Essential | GitHub auto-detection | ❌ NONE |
| `CONTRIBUTING.md` | **KEEP** | Essential | GitHub Pages + workflows | ⚠️ MEDIUM |
| `SECURITY.md` | **KEEP** | Essential | GitHub auto-detection | ❌ NONE |
| `CODE_OF_CONDUCT.md` | **KEEP** | Essential | GitHub auto-detection | ❌ NONE |
| `pyproject.toml` | **KEEP** | Essential | PEP 517 standard location | ❌ NONE |
| `.codex/archive/deprecated/AGENTS.md` | `.docs/archive/.codex/archive/deprecated/AGENTS.md` | Legacy Doc | Rarely updated | ✅ LOW |
| `CHANGELOG.md` | `.docs/archive/CHANGELOG.md` | Essential Doc | Workflows read via `gh` | ⚠️ MEDIUM |
| `PHASE_*_*.md` | `.codex/phase-reports/` | Report | Session-specific | ✅ LOW |
| `conftest.py` | `.config/conftest.py` | Config | Pytest discovery | 🔴 HIGH |
| `pytest.ini` | `.config/pytest.ini` | Config | Pytest override | 🔴 HIGH |
| `.mutmut*.ini` | `.codex/mutation-testing/configs/` | Config | Mutation tool | ✅ LOW |
| `noxfile.py` | **KEEP? / Move?** | Build | Core dependency runner | 🔴 HIGH |
| `.pre-commit-config.yaml` | `.config/.pre-commit-config.yaml` | Config | Pre-commit hook | ⚠️ MEDIUM |

---

## PHASE 3: EXECUTION (File Migration)

### Step 3.1: Safe Migration Process

**Each file migration follows this pattern:**

```
FOR EACH FILE GROUP:

1. CREATE TARGET FOLDER (if new)
   mkdir -p .config/
   git add -A  # track folder creation

2. IDENTIFY ALL REFERENCES
   Use Step 1.1-1.3 results

3. UPDATE ALL REFERENCES (dry run first)
   find . -type f \( -name "*.py" -o -name "*.yml" -o -name "*.md" -o -name "*.sh" \) \
     -exec sed -i 's|path/to/old|path/to/new|g' {} +

4. MOVE FILE WITH GIT
   git mv ./old_file .config/new_file

5. VERIFY FUNCTIONALITY
   Run targeted tests/checks

6. COMMIT SINGLE GROUP
   git commit -m "Relocate: Group name files to .config/"

7. VALIDATE LINKS (see Step 3.2)
   Run full validation suite
```

### Step 3.2: Link Validation Procedures

**Before each commit, run validation:**

```bash
# 1. Check for broken Python imports
python -m py_compile src/**/*.py tests/**/*.py

# 2. Verify pytest discovery
pytest --collect-only -q | head -20

# 3. Check for hard-coded root references
grep -r "\./" src/ tests/ .github/ | grep -v ".git" | grep -E "\.(py|yml|sh):" > /tmp/refs.txt
# Should be empty or expected

# 4. Verify workflow syntax
python -m yamllint .github/workflows/*.yml

# 5. Test package installation
pip install -e . --dry-run 2>&1 | grep -i "error" && exit 1 || echo "OK"
```

### Step 3.3: Migration Phases

**Phase 3A: Low-Risk Files (Session 1)**
- Move: Configuration files (`.config/` folder)
  - `pytest.ini`, `.coveragerc`, `.ruff.toml`, `.markdownlintrc`, `.yamllint.yml`, `.bandit.yaml`
  - `mkdocs.yml`, `.editorcofig`
- Move: Environment files (`.env/` folder)
  - `.env.example`, `.env.docker.example`, `.secrets.baseline`, `.secrets.new.baseline`
- Move: Build artifacts (`.build/` folder)
  - `package-lock.json`, `uv.lock`, `Cargo.lock`, `dvc.yaml`, `params.yaml`, manifests

**Expected Issues:** Workflow `working-directory` references, pytest discovery  
**Rollback:** Single `git revert` per commit

**Phase 3B: Medium-Risk Files (Session 2)**
- Move: Report files to `.codex/phase-reports/`
  - `PHASE_*.md`, `AUDIT_*.md`, `DOCUMENTATION_*.md`
- Move: Security reports to `.codex/security-reports/`
  - `SECURITY_*.md`, `SEMGREP_*.md`, `remediation_plan_*.md`, `auth-security-report.json`
- Move: Mutation testing to `.codex/mutation-testing/`
  - All `.mutmut*.ini`, `mutmut_output.txt`

**Expected Issues:** Cross-references in markdown, CI artifact collection  
**Rollback:** Group commit with easy revert

**Phase 3C: High-Risk Files (Session 3)**
- Move: `conftest.py` to `.config/conftest.py` (if test-independent)
- Move: Root utility scripts to `scripts/utilities/`
  - `auto_suppress.py`, `find_empty_funcs.py`, `generate_*.py`
- Evaluate: `noxfile.py` → Keep or move?

**Expected Issues:** Pytest discovery, test collection, CI runner paths  
**Rollback:** Detailed reversal plan (see Step 3.4)

---

## PHASE 4: POST-MIGRATION VALIDATION & ISSUE RESOLUTION

### Step 4.1: Comprehensive Validation

**After each phase, run full validation suite:**

```bash
# 1. Code quality checks
python -m ruff check src/ tests/ --fix
python -m mypy src/ tests/ --no-error-summary 2>&1 | grep "error:" | head -10

# 2. Import integrity
python -c "from codex import *; print('✅ Imports OK')"

# 3. Test discovery & execution
pytest --collect-only -q | wc -l  # Should match baseline
pytest -x --tb=short 2>&1 | tail -20

# 4. Workflow YAML validation
python -m yamllint .github/workflows/*.yml

# 5. Link validation in docs
python scripts/ci/link_validator.py docs/ .docs/ --strict

# 6. Git history integrity
git log --oneline -10  # Verify commit chain
git status  # Should be clean

# 7. Comparison with baseline
diff <(git show HEAD~1:.gitignore) <(cat .gitignore) | head -20
```

### Step 4.2: Common Issues & Immediate Resolutions

| Issue | Symptom | Root Cause | Resolution |
|---|---|---|---|
| **pytest discovery fails** | `error: cannot collect test_*.py` | `conftest.py` moved; pytest can't find setup | `pytest --co-init` or symlink `conftest.py` to root temporarily |
| **Import path broken** | `ModuleNotFoundError: No module named 'config'` | Relative imports assume root structure | Update PYTHONPATH in `.config/pytest.ini` or update imports |
| **Workflow can't find file** | `file not found: ./pytest.ini` | Workflow hardcodes root path | Update workflow `working-directory` or path references |
| **pre-commit skipped** | `hook skipped (file not found)` | `.pre-commit-config.yaml` moved | Update `.pre-commit-config.yaml` hook path refs |
| **Docker build fails** | `COPY conftest.py: file not found` | Dockerfile assumes root layout | Update Dockerfile COPY commands |
| **Link breaks in docs** | `[ref](./CHANGELOG.md) → 404` | Doc links point to old root paths | Run link validator + mass-update with script |
| **CI artifact collection** | `artifact not found: ./pytest-report.json` | Workflow assumes root collection point | Update `.github/workflows/` output path specs |

### Step 4.3: Immediate Resolution Procedures

**For each issue category:**

1. **Python Import Failures**
   - Run: `python -m py_compile src/` (compile-check all)
   - If fails: Identify module name conflict
   - Fix: Update `sys.path` in `conftest.py` OR update import statements
   - Validate: Re-run import tests

2. **Workflow Path Issues**
   - Search: `.github/workflows/*.yml` for hardcoded paths
   - Fix: Use `${GITHUB_WORKSPACE}` or relative paths from workflow `working-directory`
   - Validate: `yamllint` + test on PR

3. **Documentation Link Breakage**
   - Run: `python scripts/ci/link_validator.py` with `--fix` flag
   - Manual check: `.docs/archive/CHANGELOG.md` references
   - Validate: Links resolve in GitHub Pages preview

4. **pytest Discovery**
   - Root cause: Usually `conftest.py` location or `pytest.ini` path
   - Quick fix: Symlink `conftest.py` to root as fallback (temporary)
   - Permanent: Update pytest invocation to include `--confcutdir=.config`

---

## VALIDATION CHECKLIST

### Pre-Migration Validation

- [ ] **Link Inventory Complete** (Step 1.1)
  - [ ] All Python imports catalogued
  - [ ] All workflow references catalogued
  - [ ] All doc links catalogued
  - [ ] All shell script deps catalogued
  - [ ] Update strategy documented for each

- [ ] **Process Dependencies Mapped** (Step 1.2)
  - [ ] Build pipeline reviewed
  - [ ] CI workflows audited
  - [ ] Package install tested
  - [ ] Testing pipeline verified
  - [ ] Fallback plan for each critical process

- [ ] **Reference Update Strategy Finalized** (Step 1.3)
  - [ ] Python import patterns identified
  - [ ] Workflow path patterns identified
  - [ ] Doc link patterns identified
  - [ ] Config file patterns identified
  - [ ] Rollback plan for each pattern

### Phase 3A Validation (Low-Risk)

- [ ] **Configuration Files**
  - [ ] Target folders created (git-tracked)
  - [ ] All `.config/` files moved & validated
  - [ ] All `.env/` files moved & validated
  - [ ] All `.build/` files moved & validated
  - [ ] pytest discovered tests: baseline = result
  - [ ] ruff check passes
  - [ ] mypy clean
  - [ ] Workflows pass yamllint

- [ ] **Reference Updates Applied**
  - [ ] Python imports verified
  - [ ] Workflow paths verified
  - [ ] Doc links verified
  - [ ] 0 broken references found

- [ ] **Commit Integrity**
  - [ ] Each group has single commit
  - [ ] Commit message clear (e.g., "Relocate: Configuration files to .config/")
  - [ ] git history intact
  - [ ] All files tracked by git

### Phase 3B Validation (Medium-Risk)

- [ ] **Report Files**
  - [ ] `.codex/phase-reports/` structure created
  - [ ] All `PHASE_*.md` files moved
  - [ ] All `AUDIT_*.md` files moved
  - [ ] Cross-references in reports still valid (no broken links)

- [ ] **Security Reports**
  - [ ] `.codex/security-reports/` structure created
  - [ ] All security-related files moved
  - [ ] Remediation plan references updated

- [ ] **Mutation Testing**
  - [ ] `.codex/mutation-testing/` structure created
  - [ ] All `.mutmut*.ini` files moved to `configs/`
  - [ ] All outputs moved to `output/`
  - [ ] All baselines moved to `baselines/`

- [ ] **Full Test Suite**
  - [ ] `pytest -x` passes
  - [ ] 0 collection errors
  - [ ] Test count matches baseline
  - [ ] Coverage % maintained

### Phase 3C Validation (High-Risk)

- [ ] **Critical File Moves**
  - [ ] `conftest.py` tests still discover & run
  - [ ] `noxfile.py` location finalized
  - [ ] All utility scripts functional

- [ ] **Full System Test**
  - [ ] `pip install -e .` succeeds
  - [ ] Import all modules: `from codex import *`
  - [ ] Run full test suite: `pytest`
  - [ ] All CI workflows pass (e.g., GitHub Actions lint)

- [ ] **Link Integrity**
  - [ ] No broken .md links
  - [ ] No broken imports
  - [ ] No broken workflow paths
  - [ ] GitHub Pages build succeeds (if applicable)

### Post-Migration (All Phases)

- [ ] **Documentation Updated**
  - [ ] README.md links point to new locations (if needed)
  - [ ] Contributing guide updated with new structure
  - [ ] Developer docs explain folder layout

- [ ] **CI Workflows Updated** (if needed)
  - [ ] All `.github/workflows/*.yml` validated
  - [ ] Artifact collection paths updated
  - [ ] Working-directory paths updated

- [ ] **Team Communication** (if applicable)
  - [ ] Commit message summarizes changes
  - [ ] PR description explains rationale
  - [ ] Links provided to Phase plans

---

## ROLLBACK PROCEDURES

### Phase 3A Rollback (Configuration & Build)
```bash
# Single commit revert
git revert <commit-hash> --no-edit

# Multi-commit squash revert
git revert <oldest-commit-hash>..<newest-commit-hash> --no-edit

# Full revert (if all Phase 3A commits)
git reset --hard HEAD~<number-of-commits>
```

### Phase 3B Rollback (Reports)
```bash
# Same as Phase 3A — each group is independently revertible
git revert <report-commit-hash> --no-edit
```

### Phase 3C Rollback (High-Risk)
```bash
# If critical issues found, revert entire Phase 3C
git reset --hard <phase-3b-final-commit-hash>

# Re-plan and re-attempt with adjusted strategy
```

---

## SUCCESS CRITERIA

### Quantitative Metrics

| Metric | Baseline | Target | Pass Criteria |
|---|---|---|---|
| Root files (after) | 285+ | 6-8 | ✅ >95% reduction |
| Broken links | 0 | 0 | ✅ 0 detected post-migration |
| Test discovery | 1500+ tests | 1500+ tests | ✅ Exact match |
| Coverage % | 90%+ | 90%+ | ✅ No regression |
| CI pass rate | 95%+ | 95%+ | ✅ No regression |
| Build time | baseline | baseline ±5% | ✅ <5% change |

### Qualitative Criteria

- [ ] Root folder is **"clean"** — only essential project files visible
- [ ] Folder structure is **"self-documenting"** — developers understand layout immediately
- [ ] Migration required **zero breaking changes** to functionality
- [ ] All processes (build, test, CI) **continue to work seamlessly**
- [ ] Documentation **reflects new structure** clearly

---

## DECISION MATRIX: Files to Keep vs. Move

### Must Stay in Root

```
✅ README.md           → GitHub detection, first touchpoint
✅ LICENSE             → GitHub detection, legal requirement  
✅ CITATION.cff        → GitHub detection, academic standard
✅ CODE_OF_CONDUCT.md  → GitHub detection, community standard
✅ SECURITY.md         → GitHub detection, security policy
✅ CONTRIBUTING.md     → Contributing workflow, often linked
✅ pyproject.toml      → Python packaging standard (PEP 517)
```

### Candidates for Movement (to be debated)

```
? noxfile.py          
  Pros: Central to dev workflow, should stay visible
  Cons: Could move to scripts/ for organization
  Decision: **KEEP IN ROOT** — too central to move without friction

? Dockerfile           
  Pros: Central to build
  Cons: Multiple Dockerfiles (.optimized, .preview, .restore)
  Decision: **MOVE TO .config/docker/** — consolidate variants

? .pre-commit-config.yaml
  Pros: Part of git workflow
  Cons: Just config
  Decision: **MOVE TO .config/** — pre-commit looks for file in .git/hooks, not impacted

? Makefile
  Pros: `make` discovery convention
  Cons: Alternative to noxfile
  Decision: **MOVE TO .config/** or **DELETE** (noxfile primary)
```

---

## TIMELINE ESTIMATE

| Phase | Tasks | Duration | Session |
|---|---|---|---|
| **Phase 0** | Analysis, categorization, link audit | 2-3 hours | Immediate |
| **Phase 1** | Pre-migration validation (dry run) | 3-4 hours | Session 1 |
| **Phase 2** | Design folder structure, finalize strategy | 2 hours | Session 1 (concurrent with Phase 1) |
| **Phase 3A** | Migrate config + env + build (~80 files) | 2-3 hours | Session 2 |
| **Phase 3B** | Migrate reports + security (~100 files) | 2-3 hours | Session 2-3 |
| **Phase 3C** | Migrate high-risk files (~30 files) | 3-4 hours | Session 3 |
| **Phase 4** | Full validation + issue resolution | 2-3 hours | Each session end |

**Total Estimated Time:** 16-22 hours across 3-4 sessions

---

## NEXT STEPS

1. **This session:** Approve this plan
2. **Session 2:** Execute Phase 0, Phase 1, Phase 2
3. **Session 3:** Execute Phase 3A + Phase 4 validation
4. **Session 4:** Execute Phase 3B + Phase 4 validation  
5. **Session 5:** Execute Phase 3C + Phase 4 validation + final verification

**AWAITING APPROVAL BEFORE PROCEEDING**

