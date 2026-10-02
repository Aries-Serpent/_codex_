# BATCH 4: EXPLICIT CONSOLIDATION SPECIFICATIONS

**Created**: 2026-07-03T03:50Z  
**Purpose**: Provide file-by-file consolidation actions for Session 3 restart  
**Authority**: @mbaetiong D-tier autonomy

---

## CATEGORY 1: HYDRA CONFIGURATION CONSOLIDATION

### Current State Analysis

**Files to audit**:
- `configs/` directory (base configurations)
- `configs/**/config.yaml` overrides
- `pyproject.toml` (Hydra CLI settings)

### Consolidation Actions

**Action 1.1**: Consolidate duplicate config entries
- Scan all `configs/**/*.yaml` files
- Identify duplicate keys or values across files
- **If found**: Consolidate to single source of truth in base `configs/config.yaml`
- **Success Gate**: All config keys unique, no duplicate definitions

**Action 1.2**: Validate Hydra override chains
- Test `hydra.run.dir` paths (should be dynamic, not hardcoded)
- Test `hydra.job.chdir` behavior (should be configurable)
- Test all CLI overrides work: `python -m codex.cli <task> config_param=value`
- **Success Gate**: All Hydra override chains load without error

**Action 1.3**: Consolidate CLI entry points
- Verify `src/codex/cli.py` uses Hydra correctly
- Check that all CLI tasks have corresponding Hydra configs
- **Success Gate**: CLI works, all tasks accept config overrides

### Expected Changes
- 0–2 files modified (consolidation only, no new files)
- 1 atomic commit

---

## CATEGORY 2: CI/CD WORKFLOW TEMPLATES CONSOLIDATION

### Current State Analysis

**Files to audit**:
- `.github/workflows/*.yml` (50+ workflows)
- Focus: Session 2 file changes need syncing in artifact references

### Consolidation Actions

**Action 2.1**: Sync Session 2 file renames in workflow artifacts
- Review all workflows that reference Session 2-changed files
- Session 2 changed: hardcoded paths, /tmp refs, symlinks
- **If found**: Update artifact paths to match new file locations
- **Success Gate**: All artifact paths valid, no 404 references

**Action 2.2**: Consolidate duplicate workflow definitions
- Scan for workflows with identical or near-identical job definitions
- **If found**: Extract common job definitions to reusable workflows
- **Success Gate**: No code duplication between workflows

**Action 2.3**: Validate all workflow YAML syntax
- Run `yamllint .github/workflows/*.yml`
- Check for indentation, type, and rule errors
- **Success Gate**: 0 syntax errors, all workflows parse cleanly

### Expected Changes
- 5–10 files modified (artifact path updates, deduplication)
- 1 atomic commit

---

## CATEGORY 3: PYTHON ENVIRONMENT CONSOLIDATION

### Current State Analysis

**Files to audit**:
- `pyproject.toml` (dependencies)
- `requirements*.txt` (variant requirements)
- `setup.cfg` (alternative metadata)
- `setup.py` (legacy, if exists)
- `poetry.lock`, `Pipfile.lock` (lock files)

### Consolidation Actions

**Action 3.1**: Consolidate dependency specifications
- Audit which files define which dependencies
- Identify conflicts between `requirements.txt`, `pyproject.toml`, `setup.cfg`
- **If found**: Designate single source of truth (prefer `pyproject.toml` per PEP 621)
- **Action**: Update all other files to reference or defer to primary source
- **Success Gate**: Single dependency source of truth, no conflicts

**Action 3.2**: Validate dependency versions
- Run: `pip check` (detects version conflicts)
- Verify all required versions still available on PyPI
- **Success Gate**: `pip check` returns 0 conflicts

**Action 3.3**: Consolidate lock files
- Audit `poetry.lock`, `Pipfile.lock`, `uv.lock` (if multiple exist)
- **If multiple exist**: Designate primary lock file (prefer `uv.lock` or `poetry.lock`)
- **Action**: Remove duplicate lock files or document why multiple needed
- **Success Gate**: Single lock file source (or documented reason for multiple)

**Action 3.4**: End-to-end test
- Run: `pip install -e .` from repo root
- Run: `pip install -r requirements-test.txt` (or equivalent)
- **Success Gate**: Both commands complete without error, imports work

### Expected Changes
- 3–5 files modified (consolidation only)
- 1 atomic commit

---

## CATEGORY 4: BUILD SYSTEM CONSOLIDATION

### Current State Analysis

**Files to audit**:
- `Makefile` (if exists)
- `Makefile.restore` (if exists — why?)
- `noxfile.py` or `nox.ini`
- `pytest.ini`
- `setup.py` or `setup.cfg` (build metadata)
- `pyproject.toml` (build backend)

### Consolidation Actions

**Action 4.1**: Consolidate Makefiles
- Check if both `Makefile` and `Makefile.restore` exist
- **If both exist**: Determine which is authoritative
  - If `Makefile` is primary: Delete `Makefile.restore`
  - If `Makefile.restore` should be primary: Rename to `Makefile`, remove old
  - If both needed: Document why in `Makefile` comments
- **Success Gate**: Single authoritative Makefile

**Action 4.2**: Consolidate nox configuration
- Check if `noxfile.py` and `nox.ini` both exist
- **If both exist**: Consolidate to single format
  - Prefer `noxfile.py` for complex logic
  - Prefer `nox.ini` for simple configs
  - Document decision in code
- **Success Gate**: Single nox config source

**Action 4.3**: Consolidate build metadata
- Check `setup.py`, `setup.cfg`, `pyproject.toml` for duplicate metadata
- **If duplicates found**: Consolidate to single source (prefer `pyproject.toml`)
- **Action**: Remove or deprecate legacy files
- **Success Gate**: Single build metadata source, build system works

**Action 4.4**: End-to-end build test
- Run: `make` (or `nox -s build` if no Makefile)
- Run: `make test` (or `nox -s tests`)
- Run: `make lint` (or equivalent)
- **Success Gate**: All standard targets pass

### Expected Changes
- 2–4 files modified (consolidation only)
- 1 atomic commit

---

## CATEGORY 5: CROSS-TOOL VALIDATION

### Purpose
After Categories 1–4 consolidations complete, verify no consolidations broke any workflows.

### Validation Actions

**Action 5.1**: Run full CI/CD simulation locally
- Run: `pre-commit run --all-files` (format, lint, type checks)
- Run: `nox -s tests` (test suite)
- Run: `nox -s coverage` (coverage check)
- **Success Gate**: All pre-commit hooks pass, all tests pass, coverage meets threshold

**Action 5.2**: Verify no regressions
- Audit git diff to ensure consolidations are backwards-compatible
- Check that no existing tests fail
- **Success Gate**: All existing tests still pass

**Action 5.3**: Documentation validation
- Verify all documentation still references correct file paths
- Check that all code examples still work
- **Success Gate**: All docs links valid, all examples work

---

## EXECUTION PLAN

**Timeline**: 60–90 minutes (5 categories, ~15 min per category)

1. **0–15 min**: Category 1 (Hydra) complete + 1 commit
2. **15–30 min**: Category 2 (CI/CD workflows) complete + 1 commit
3. **30–45 min**: Category 3 (Python environment) complete + 1 commit
4. **45–60 min**: Category 4 (Build system) complete + 1 commit
5. **60–75 min**: Category 5 (Cross-tool validation) complete
6. **75–90 min**: All consolidation reports generated

### Success Criteria (All must PASS)

✅ **Category 1**: Hydra configs load, CLI overrides work  
✅ **Category 2**: Workflows syntax valid, artifact paths correct  
✅ **Category 3**: `pip install -e .` works, no conflicts  
✅ **Category 4**: `make` and `nox` targets pass  
✅ **Category 5**: `pre-commit run`, `nox -s tests`, `nox -s coverage` all pass  

---

## ARTIFACT GENERATION

After consolidation, create:

**Completion Reports**:
- `.codex/BATCH_4_CATEGORY_1_HYDRA_CONSOLIDATION.md`
- `.codex/BATCH_4_CATEGORY_2_CI_CONSOLIDATION.md`
- `.codex/BATCH_4_CATEGORY_3_PYTHON_CONSOLIDATION.md`
- `.codex/BATCH_4_CATEGORY_4_BUILD_CONSOLIDATION.md`
- `.codex/BATCH_4_CATEGORY_5_VALIDATION_REPORT.md`

**Summary Report**:
- `.codex/BATCH_4_CONSOLIDATION_COMPLETE.md`
- Include metrics: files touched, commits made, time elapsed
- Include validation results: all tests passed/failed
- Include next steps: ready for Session 4 (optional full validation)

**Git Commits** (5 total):
- 1 per category (commits 1–4)
- 1 for final reports (commit 5)

---

## ACTIVATION CHECKLIST

- [x] Explicit file-by-file consolidation specifications provided
- [x] Success criteria clearly defined per category
- [x] Validation procedures documented
- [x] Artifact generation requirements specified
- [x] Authority confirmed (@mbaetiong D-tier autonomy)
- [x] GO CONTINUE gate activated

**STATUS**: 🟢 **READY TO RESTART SESSION 3 IMMEDIATELY**
