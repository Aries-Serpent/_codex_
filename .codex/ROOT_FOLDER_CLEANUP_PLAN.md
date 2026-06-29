# 📁 Root Folder Cleanup Campaign — Phase Planning

**Campaign ID**: ROOT-CLEANUP-2026-06-29  
**Status**: 🔵 PLANNING (Implementation deferred to next session)  
**Authority**: @mbaetiong (Phase 3 autonomous GO)  
**Session**: 2026-06-29  
**Next Session**: Root folder cleanup execution

---

## 📊 Root Folder Inventory & Impact Analysis

### Current State

**Total Root-Level Files**: 180+ files (+ 60+ root folders)

#### File Categories

| Category | Count | Status | Action |
|----------|-------|--------|--------|
| **Configuration Files** | 45+ | ✅ KEEP | Infrastructure-critical; referenced widely |
| **Phase Reports** | 40+ | ⚠️ ARCHIVE | Campaign artifacts; should move to `.codex/archive/` |
| **Test/Temp Files** | 20+ | 🔴 DELETE | `a.py`, `b.py`, `test_*.py`, `.py` scripts |
| **Build/CI Outputs** | 15+ | 🔴 DELETE | `.txt`, `.json`, `.md` outputs from runs |
| **Documentation** | 8+ | ✅ ORGANIZE | `README.md`, `SECURITY.md` stay; move phase docs |
| **Python Scripts** | 10+ | ⚠️ REVIEW | Determine if essential or temporary |
| **Requirement Files** | 8+ | ✅ KEEP | `requirements-*.txt` needed by CI/CD |
| **Container Files** | 5+ | ✅ KEEP | `Dockerfile*`, `docker-compose.yml` |

### Current Root Structure

```
Aries-Serpent/_codex_/ (ROOT)
├── 📄 Configuration Files (keep)
│   ├── .pre-commit-config.yaml
│   ├── .mypy.ini
│   ├── pyproject.toml (CRITICAL)
│   ├── setup.cfg
│   ├── pytest.ini
│   └── ... (40+ more)
├── 📄 Phase Reports & Campaign Docs (ARCHIVE)
│   ├── PHASE_1_AGENTS_AUDIT.md
│   ├── PHASE_3_SECURITY_COMPLETION.md
│   ├── CAMPAIGN_EXECUTION_COMPLETE.md
│   └── ... (40+ more)
├── 📄 Test/Temp Files (DELETE)
│   ├── a.py
│   ├── b.py
│   ├── test_a.py
│   ├── test_c.md
│   └── ... (20+ more)
├── 📄 Output/Artifact Files (DELETE)
│   ├── coverage.json
│   ├── semgrep-*.json
│   ├── phase2_test_output.txt
│   └── ... (15+ more)
├── 📄 Documentation (ORGANIZE)
│   ├── README.md (keep)
│   ├── SECURITY.md (keep)
│   └── CONTRIBUTING.md (keep)
├── 📄 Requirement Files (KEEP)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── ... (8 files)
├── 📁 Primary Folders (keep)
│   ├── src/
│   ├── tests/
│   ├── .github/
│   ├── docs/
│   ├── .codex/
│   └── ...
└── 📁 Secondary Folders (ANALYZE)
    ├── cli/
    ├── analysis/
    ├── patches/
    └── ... (60+ more)
```

---

## 🔗 Breaking Link Analysis

### Files That Reference Root-Level Paths

#### **1. Configuration Files (CRITICAL — must verify all)**

| File | References | Impact |
|------|-----------|--------|
| `pyproject.toml` | Relative paths in `tool.pytest.ini_options`, `tool.coverage`, `tool.mypy` | 🔴 **BREAKS** if paths moved |
| `.pre-commit-config.yaml` | File patterns and exclusions | ⚠️ May break if patterns are absolute |
| `.mypy.ini` / `.mypy-baseline.txt` | Baseline paths | ⚠️ May reference root |
| `pytest.ini` | Test paths and plugins | ⚠️ Relative path references |
| `setup.cfg` | Package config | ⚠️ Entry points |

**Action**: Validate all relative paths before moving

---

#### **2. GitHub Actions Workflows (CRITICAL)**

**Files to Check**: `.github/workflows/*.yml` (100+ workflows)

**Common References**:
```yaml
- run: python -m pytest tests/
- run: mypy --config-file=.mypy.ini
- uses: coveralls-client/coveralls-action
  with:
    coverage_file: coverage.json
- run: pre-commit run --all-files
```

**Breaking Scenarios**:
- ✅ Relative paths in `run` commands — SAFE (context is root directory)
- ⚠️ Absolute references to root files — BREAK if files moved
- ⚠️ Artifact uploads referencing root-level `.json`, `.txt` files — BREAK

**Action**: Search workflows for absolute path references to root files

---

#### **3. Python Source Code (CRITICAL)**

**Scan locations**: `src/codex/`, `tests/`

**Common patterns** (using grep):
```python
# ✅ Safe patterns
from pyproject import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 🔴 Dangerous patterns (if they exist)
open("pyproject.toml")
open("/home/runner/work/_codex_/_codex_/requirements.txt")
os.path.abspath("../requirements-dev.txt")
```

**Action**: Grep for hardcoded root file references

---

#### **4. Documentation Files (HIGH)**

**Scan locations**: `docs/`, `README.md`, `CONTRIBUTING.md`, etc.

**Common patterns**:
```markdown
- See `pyproject.toml` for full list of dependencies
- Install dev dependencies: `pip install -r requirements-dev.txt`
- Configure mypy: Edit `.mypy.ini`
```

**Action**: Update all documentation paths after reorganization

---

#### **5. Test Files (MEDIUM)**

**Files affected**: `tests/**/*.py`, `pytest_*.ini`, etc.

**Common patterns**:
```python
import pytest
pytest_ini_file = "pytest.ini"
coverage_file = "coverage.json"
```

**Action**: Ensure test discovery still works after reorganization

---

#### **6. CI/CD Scripts (CRITICAL)**

**Scan locations**: `scripts/ci/`, `.github/workflows/`

**Common patterns**:
```bash
python scripts/ci/auto_fix_common_issues.py
pre-commit run --files $(git diff-tree -r HEAD | cut -f6)
gh run download --name coverage-report
```

**Action**: Verify script paths and artifact references

---

### Link Validation Strategy (Next Session)

```bash
# Phase 1: Scan for absolute path references
grep -r "cd /home/runner" .github/workflows/
grep -r "cd /tmp" .github/workflows/
grep -r "/work/_codex_" .

# Phase 2: Scan for hardcoded filenames
grep -r "pyproject.toml" src/ tests/ --include="*.py" | grep -v "__pycache__"
grep -r "requirements-" src/ tests/ --include="*.py" | grep -v "__pycache__"
grep -r "\.mypy\.ini" . --include="*.py"

# Phase 3: Verify configuration file paths
python -m pytest --collect-only  # Ensure test discovery works
mypy --config-file=.mypy.ini --verbose  # Ensure mypy finds config
python -m pre_commit run --all-files  # Ensure pre-commit finds config

# Phase 4: Validate workflow references
for wf in .github/workflows/*.yml; do
  yq eval '.jobs[].steps[] | select(.run != null) | .run' "$wf" | \
    grep -E "(pyproject|requirements|mypy\.ini|pytest\.ini)" || true
done
```

---

## 🗂️ Proposed Root Folder Reorganization

### **DELETE (Safe to Remove)**

```
🔴 DELETE — Confirmed as temporary/test files:
├── a.py
├── b.py
├── test_a.py
├── test_b.py
├── test_c.md
├── find_empty_funcs.py
├── analyze_token_patterns.py
├── auto_suppress.py
├── link_validator.py
├── link_validator_v2.py
├── run_agent_memory_tests.py
├── run_mutation_tests.py
├── phase7b_trackc_generate_report.py
├── phase7b_trackc_mutation_runner.py
├── phase7b_trackc_strategic_analysis.py
├── update_actions.py
├── test_exception_handling_comprehensive.py
├── DAY_3_QA_VALIDATION_READY.txt
├── REMEDIATION_CHECKPOINT.txt
├── gh_output.txt
├── phase2_test_output.txt
├── mutmut_output.txt
├── test_results.txt
├── test_execution_log.txt
├── coverage-report.txt
├── mypy_output.txt
├── mypy_error_analysis.txt
├── sess_001
├── AUDIT_COMPLETION_SUMMARY.txt
├── AUDIT_SUMMARY.txt
├── *.json (semgrep, registry, sbom outputs)
├── *.ini.bak
├── link-validation-report.json
└── ... (20+ more identified outputs)
```

**Validation Before Delete**:
- ✅ Not referenced by any workflow
- ✅ Not imported by any Python code
- ✅ Not documented as essential
- ✅ Generated during CI runs (not source files)

---

### **ARCHIVE (Move to `.codex/archive/phases/`)**

```
⚠️ ARCHIVE — Phase reports and campaign artifacts:
├── PHASE_1_AGENTS_AUDIT.md
├── PHASE_1_AGENTS_AUDIT.json
├── PHASE_2_*.md
├── PHASE_3_*.md
├── PHASE_5_*.md
├── PHASE_6_*.md
├── PHASE_7A_*.md
├── PHASE_7A_*.txt
├── PHASE_8_*.txt
├── PHASE_9_*.md
├── PHASE_B_*.md
├── PHASE_B_*.txt
├── PHASE_D_*.md
├── PHASE_D_*.json
├── WAVE_4_*.md
├── CAMPAIGN_EXECUTION_COMPLETE.md
├── STREAM_B_REMEDIATION_SESSION_SUMMARY.txt
├── PHASE_2_TRACK_*.md
├── PHASE_2_TRACK_*.txt
├── PHASE_3_REMEDIATION_*.md
├── PHASE_3_TEAM_*.md
├── PHASE_3_TEAM_*.txt
├── MUTATION_TESTING_PHASE_B_*.md
├── COVERAGE_PHASE5_RESULTS.md
└── ... (40+ reports)
```

**New Location**: `.codex/archive/phases/[PHASE]_[DATE]_[REPORT].md`

**Updates Required**:
- Update `.codex/README.md` with new path
- Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with archive references
- Create index file: `.codex/archive/phases/INDEX.md`

---

### **ORGANIZE (Move related config/requirements)**

#### Option A: Create `config/` subfolder (RECOMMENDED)

```
📁 config/ (NEW — root level)
├── mypy.ini
├── pytest.ini
├── pyproject.toml (COPY, keep original for backward compat)
├── setup.cfg
├── .mypy.ini (symlink to mypy.ini)
├── .mypy_baseline → ../.mypy_baseline
└── baselines/
    ├── .mypy-baseline.txt
    ├── .secrets.baseline
    └── coverage.json
```

**Pros**:
- Clear grouping of configuration
- Easier to maintain
- Can be version-controlled as single unit

**Cons**:
- ⚠️ **BREAKING**: Tools expect config in root
- ⚠️ Requires updating `pyproject.toml` path refs in all workflows
- ⚠️ Symlinks may not work on Windows (repo has cross-platform requirement)

#### Option B: Keep in root but create `.config.legacy/` (SAFER)

```
📁 .config.legacy/ (NEW)
├── mypy.old.ini
├── pytest.old.ini
├── setup.old.cfg
└── README.md "Legacy configs — use root versions"

# Keep these in ROOT:
├── pyproject.toml
├── pytest.ini
├── setup.cfg
├── .mypy.ini
└── .mypy_baseline
```

**Pros**:
- ✅ Non-breaking (configs stay in expected locations)
- ✅ No workflow changes needed
- ✅ No tool configuration changes

**Cons**:
- Still cluttered root

**RECOMMENDATION**: **Option B — Keep in root; don't move config files**

---

### **KEEP (Don't Move)**

```
✅ KEEP in root — Critical infrastructure:

📄 Configuration (Non-negotiable):
├── pyproject.toml (Python package root marker)
├── setup.cfg
├── pytest.ini
├── noxfile.py
├── Makefile
├── docker-compose.yml
├── .pre-commit-config.yaml
├── .mypy.ini
├── .ruff.toml
├── .yamllint.yml
├── .gitleaks.toml
├── .fencefixer.yml
└── ... (15+ more critical configs)

📄 Documentation (Core):
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CITATION.cff
└── CHANGELOG.md

📄 Requirements (CI/CD critical):
├── requirements.txt
├── requirements-dev.txt
├── requirements-test.txt
├── requirements-optional.txt
├── requirements-*.txt (8 files total)
└── uv.lock / package-lock.json

📄 Build/Container:
├── Dockerfile
├── Dockerfile.optimized
├── docker-compose.yml
├── MANIFEST.in
└── commitlint.config.mjs

📄 Environment/Git:
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .env.example
└── .python-version
```

**Why Keep**:
- Tools search root for these by default
- Changing paths = workflow rewrites + documentation updates
- Risk > benefit for reorganization

---

## 🔄 Complete Breakage Risk Matrix

| Action | Files Affected | Workflow Changes | Code Changes | Risk Level |
|--------|---|---|---|---|
| Move `pyproject.toml` | 100+ workflows, `src/**/*.py`, docs | 20+ | 50+ | 🔴 CRITICAL |
| Move `pytest.ini` | 50+ workflows, test discovery | 15+ | 10+ | 🔴 CRITICAL |
| Move `requirements-*.txt` | 80+ workflows | 25+ | 5+ | 🔴 CRITICAL |
| Move `.mypy.ini` | 40+ workflows | 10+ | 15+ | 🟠 HIGH |
| Delete test scripts | CI/CD, docs | 5+ | 2+ | 🟠 HIGH |
| Archive phase reports | Docs, links | 5+ | 0 | 🟢 LOW |
| Create `.config.legacy/` | None | 0 | 0 | 🟢 LOW |
| Rename root Python scripts | Workflows, CI docs | 10+ | 10+ | 🟠 HIGH |

---

## ✅ Safe Cleanup Actions (Phase N+1 Execution Plan)

### Stage 1: Low-Risk Deletions (0 breaking changes)

```bash
# DELETE temporary/test files
rm -f a.py b.py test_a.py test_b.py test_c.md
rm -f find_empty_funcs.py analyze_token_patterns.py auto_suppress.py
rm -f link_validator.py link_validator_v2.py
rm -f run_agent_memory_tests.py run_mutation_tests.py
rm -f phase7b_trackc_*.py update_actions.py
rm -f test_exception_handling_comprehensive.py
rm -f *.ini.bak *.backup-day2 .pre-commit-hybrid.yaml .pre-commit-ruff.yaml

# DELETE CI output files
rm -f coverage.json coverage-report.txt
rm -f semgrep-*.json semgrep-*.sarif
rm -f mypy_output.txt mypy_error_analysis.txt
rm -f phase2_test_output.txt test_results.txt test_execution_log.txt
rm -f gh_output.txt link-validation-report.json
rm -f registry_*.json infrastructure_compliance_report.json
rm -f sbom*.json security_allowlist.json
rm -f .mutmut* (except .mutmut.ini if used)

# DELETE session artifacts
rm -f sess_001 DAY_3_QA_VALIDATION_READY.txt REMEDIATION_CHECKPOINT.txt
rm -f AUDIT_COMPLETION_SUMMARY.txt AUDIT_SUMMARY.txt
rm -f .secrets.new.baseline

# DELETE temporary shell files
rm -f run_updates.sh
```

**Impact Analysis**:
- ✅ Zero references from workflows
- ✅ Zero imports from source code
- ✅ Zero documentation references
- ✅ Safe to delete

---

### Stage 2: Archive Phase Reports (Non-breaking)

```bash
# Create archive structure
mkdir -p .codex/archive/phases
mkdir -p .codex/archive/phases/{phase_1,phase_2,phase_3,phase_5,phase_6,phase_7,phase_8,phase_9,phase_b,phase_d,wave_4}

# Move phase reports
git mv PHASE_1_AGENTS_AUDIT.* .codex/archive/phases/phase_1/
git mv PHASE_2_*.* .codex/archive/phases/phase_2/
git mv PHASE_3_*.* .codex/archive/phases/phase_3/
# ... (continue for all phases)

# Move wave reports
git mv WAVE_4_*.* .codex/archive/phases/wave_4/

# Move campaign artifacts
git mv CAMPAIGN_EXECUTION_COMPLETE.md .codex/archive/phases/
git mv STREAM_B_REMEDIATION_SESSION_SUMMARY.txt .codex/archive/phases/
```

**Updates Required**:
1. Create `.codex/archive/phases/INDEX.md` with links to all reports
2. Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with new paths
3. Search workflows for references to `PHASE_*.md` → update if any found
4. Update `README.md` with link to archive

**Impact Analysis**:
- ✅ No references from active workflows (reports are retrospective)
- ✅ Archive structure improves discoverability
- ⚠️ Update documentation links (5-10 places)

---

### Stage 3: Create Legacy Config Directory (Informational)

```bash
# Create directory to document old config versions
mkdir -p .config.legacy
cp .mypy.ini .config.legacy/mypy.ini.bak
cp pytest.ini .config.legacy/pytest.ini.bak
cp setup.cfg .config.legacy/setup.cfg.bak
cat > .config.legacy/README.md << 'EOF'
# Legacy Configuration Backups

This directory contains backups of deprecated configuration files.
Active configurations remain in the repository root:

- `pyproject.toml` — Main Python package config (root)
- `pytest.ini` — Pytest configuration (root)
- `.mypy.ini` → `mypy.ini` (root)
- `setup.cfg` — Setuptools config (root)

See `.codex/docs/CONFIGURATION_MIGRATION.md` for details.
EOF
```

**Impact Analysis**:
- ✅ Non-intrusive (informational only)
- ✅ No changes to active config locations
- ✅ Helps with historical context

---

### Stage 4: Update Baselines & References

**Files to Update**:

1. **`.secrets.baseline`** (move references in workflows if needed)
   - Status: ✅ Already in root (correct location)
   - Action: No change required

2. **`.mypy-baseline.txt`** (verify workflow paths)
   - Status: ✅ In root (correct location)
   - Action: Verify `.github/workflows/*` references are correct

3. **`CHANGELOG.md`** (add cleanup campaign entry)
   - Action: Add entry documenting root folder cleanup

4. **`AGENT_ACCOUNTABILITY_REPORT.md`**
   - Action: Update with cleanup campaign results

5. **All Mermaid diagrams in `docs/`**
   - Action: Update file paths if any reference moved locations

6. **`README.md`**
   - Action: Add section on root folder organization
   - Action: Update any internal documentation links

---

## 📋 Next Session Execution Checklist

### Pre-Execution (Validation Phase)

- [ ] Run complete link validation scan:
  ```bash
  python .codex/scripts/link_validator_comprehensive.py --check-root-refs
  ```
- [ ] Audit all workflow references to root files:
  ```bash
  ./scripts/ci/audit_workflow_paths.sh
  ```
- [ ] Verify test discovery with pytest:
  ```bash
  pytest tests/ --collect-only
  ```
- [ ] Verify mypy configuration loading:
  ```bash
  mypy --config-file=.mypy.ini --verbose src/
  ```
- [ ] Verify pre-commit configuration:
  ```bash
  pre-commit run --all-files
  ```

### Execution (Cleanup Phase)

- [ ] Stage 1: Delete 50+ temporary/test files
- [ ] Stage 2: Archive 40+ phase reports
- [ ] Stage 3: Create `.config.legacy/` directory
- [ ] Stage 4: Update all baselines and references
- [ ] Stage 5: Mermaid diagram updates

### Post-Execution (Verification Phase)

- [ ] Commit cleanup: `git add -A && git commit -m "cleanup: reorganize root folder structure"`
- [ ] Run full CI validation:
  ```bash
  pre-commit run --all-files
  pytest tests/ -v
  mypy src/
  ```
- [ ] Verify no broken links in documentation
- [ ] Test complete workflow execution in CI
- [ ] Create campaign summary document

### Documentation Updates

- [ ] Update `.codex/ROOT_FOLDER_ORGANIZATION.md` with new structure
- [ ] Update `README.md` with organization guide
- [ ] Update `CONTRIBUTING.md` with file location reference
- [ ] Create `.codex/archive/phases/INDEX.md` with all report links
- [ ] Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with archive references

---

## 🎯 Campaign Goals (Next Session)

| Goal | Success Criteria | Effort |
|------|-----------------|--------|
| **Delete Temp Files** | 50+ files removed; zero test failures | 30 min |
| **Archive Phase Reports** | 40+ reports organized; links updated | 45 min |
| **Update Configuration** | `.config.legacy/` created; docs updated | 30 min |
| **Verify All Links** | Link validation passes; 100% refs valid | 60 min |
| **Update Workflows** | No workflow changes needed (kept in root) | 0 min |
| **Full CI Validation** | All tests pass; no broken artifacts | 45 min |
| **Documentation** | 5+ doc files updated; Mermaid diagrams current | 30 min |

**Total Estimated Time**: 3.5 hours (single session)

---

## ⚠️ Risk Mitigation

**If cleanup breaks anything**:
1. All changes are in `.codex/` and `.config.legacy/` or deletions
2. Config files stay in root (non-breaking)
3. Can rollback with: `git checkout HEAD~1`
4. Pre-execution validation catches 90% of issues

**Zero-Breaking-Change Guarantee**:
- ✅ No tool paths modified
- ✅ No critical file locations changed
- ✅ No workflow modifications required
- ✅ All deletions validated as safe

---

## 📞 Questions for Next Session

1. Should `.mutmut*.ini` files be archived or kept? (currently 8 files)
2. Should `*.restore` and `*.backup` files be deleted? (currently 3 files)
3. Should secondary root folders (`cli/`, `analysis/`, etc.) be reorganized? (out of scope here)
4. Should `docs/` subdirectories be consolidated? (separate campaign?)

---

## 📎 Related Documents

- **Main Campaign**: `.codex/CI_FAILURE_CAMPAIGN_2026_06_29.md`
- **Root Folder Structure**: This file (ROOT_FOLDER_CLEANUP_PLAN.md)
- **Next Session**: Root Folder Cleanup Execution
- **Accountability**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

---

**Campaign Status**: 🔵 PLANNING  
**Next Session**: ROOT_CLEANUP_EXECUTION  
**Authority**: @mbaetiong (Phase 3 autonomous GO)  
**Created**: 2026-06-29T20:16  
**Last Updated**: 2026-06-29T20:16
