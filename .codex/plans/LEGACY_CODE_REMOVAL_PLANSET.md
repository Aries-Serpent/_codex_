# Legacy Code Removal Implementation Planset

**Created:** 2026-01-16  
**Status:** 📋 Ready for Execution  
**Priority:** MEDIUM (Technical debt reduction)  
**Agent Type:** AI Agent (fully autonomous execution)  
**Policy Compliance:** AI Agency Policy v1.0.0

---

## Executive Summary

This planset provides end-to-end implementation guidance for removing deprecated legacy code and modernizing the codebase. Based on IP-002 audit findings, the repository contains two deprecated shim modules (`config_legacy/` and `yaml_legacy/`) and various unused modules that should be cleaned up for production readiness.

### Scope of Legacy Code

**Identified Legacy Components:**

1. **config_legacy/** - Deprecated Hydra shim (3 files, ~250 lines)
   - Status: ⚠️ DEPRECATED with warnings
   - Purpose: Backward compatibility during Hydra migration
   - Migration: Complete (modern configs in `configs/`)
   - Usage: Minimal (fallback imports only)

2. **yaml_legacy/** - Deprecated PyYAML shim (1 file, ~130 lines)
   - Status: ⚠️ DEPRECATED (fallback only)
   - Purpose: PyYAML compatibility layer
   - Migration: Complete (PyYAML in dependencies)
   - Usage: No direct imports (fallback only)

3. **Unused/Deprecated Modules** (to be identified during cleanup)
   - Archive directories with old implementations
   - Commented-out code blocks
   - Deprecated utility functions
   - Old configuration files

---

## Impact Analysis

### Benefits of Removal

**Code Quality:**
- Reduced codebase size (~500+ lines removed)
- Eliminated maintenance burden
- Clearer code structure
- Reduced confusion for new contributors

**Security:**
- Removed unmaintained code paths
- Eliminated deprecated dependencies
- Reduced attack surface

**Performance:**
- Faster imports (no shim overhead)
- Reduced memory footprint
- Cleaner dependency tree

**Documentation:**
- Clearer architecture docs
- Simplified onboarding
- Reduced documentation maintenance

### Risks and Mitigation

**Risk 1: Breaking Backward Compatibility**
- **Mitigation:** Search entire codebase for imports
- **Mitigation:** Add migration guide
- **Mitigation:** Deprecation warnings in prior release
- **Mitigation:** Comprehensive testing before removal

**Risk 2: Hidden Dependencies**
- **Mitigation:** Static analysis for all imports
- **Mitigation:** Dynamic import testing
- **Mitigation:** Grep for string references
- **Mitigation:** Check test fixtures and mocks

**Risk 3: External User Impact**
- **Mitigation:** Version bump (breaking change)
- **Mitigation:** CHANGELOG with migration guide
- **Mitigation:** Update all documentation
- **Mitigation:** Provide compatibility layer if needed

---

## Human Admin Tasks vs AI Agent Tasks

### Human Admin Planset (Manual Steps Required)

#### Task HA-LEGACY-1: Breaking Change Approval
**Blocker:** Requires approval for backward-incompatible changes
**Best-Effort Alternative:** AI Agent can prepare impact analysis and migration guide

**Manual Steps:**
1. Review impact analysis report
2. Approve breaking changes for next major version
3. Set deprecation timeline
4. Approve version bump strategy
5. Review and approve migration guide

**AI Agent Support:**
- Generate comprehensive impact analysis
- Create migration guide with code examples
- Identify all affected codepaths
- Propose version bump strategy
- Document communication plan

---

### AI Agent Planset (Autonomous Tasks)

#### Phase 1: Legacy Code Discovery and Analysis

**Pre-commit 1-2: Comprehensive Legacy Code Audit**

**Goal:** Identify all legacy, deprecated, and unused code in repository

**Tasks:**
- [ ] Search for all imports of `config_legacy` and `yaml_legacy`
- [ ] Identify archived directories and files
- [ ] Find commented-out code blocks (>10 lines)
- [ ] Detect deprecated function decorators
- [ ] Search for TODO/FIXME/DEPRECATED comments
- [ ] Identify unused imports across codebase
- [ ] Find duplicate utility functions
- [ ] Detect orphaned test files

**Success Criteria:**
- [ ] Complete inventory of legacy code
- [ ] Impact analysis for each component
- [ ] Migration complexity assessment
- [ ] Removal priority ranking

**Discovery Commands:**
```bash
# Find config_legacy imports
rg "from config_legacy|import config_legacy" --type py

# Find yaml_legacy imports
rg "from yaml_legacy|import yaml_legacy" --type py

# Find deprecated decorators
rg "@deprecated|@Deprecated" --type py

# Find large commented blocks
rg "^#.*\n(#.*\n){10,}" --type py

# Find archive directories
find . -type d -name "*archive*" -o -name "*deprecated*" -o -name "*legacy*"

# Analyze import usage
python scripts/analyze_imports.py --unused --report legacy_imports.json
```

**Files to Create:**
- `.codex/reports/LEGACY_CODE_AUDIT.md` (comprehensive report)
- `scripts/analyze_imports.py` (import analysis tool)
- `scripts/detect_legacy_code.py` (detection automation)

**Alternative if Blocked:**
- Manual file-by-file review if automated tools fail
- Start with obvious legacy directories
- Document unclear cases for human review

---

**Pre-commit 3-4: Dependency and Import Analysis**

**Goal:** Map all dependencies and usage patterns for legacy code

**Tasks:**
- [ ] Create dependency graph for legacy modules
- [ ] Identify all direct importers
- [ ] Identify all transitive dependencies
- [ ] Check for dynamic imports (importlib, __import__)
- [ ] Analyze test dependencies on legacy code
- [ ] Check configuration file references
- [ ] Review documentation references
- [ ] Search for string-based module loading

**Success Criteria:**
- [ ] Complete dependency graph generated
- [ ] All import sites identified
- [ ] Test dependencies mapped
- [ ] Configuration references catalogued

**Analysis Tools:**
```bash
# Generate dependency graph
python scripts/generate_dependency_graph.py \
  --modules config_legacy yaml_legacy \
  --output legacy_dependencies.svg

# Find dynamic imports
rg "importlib\.import_module|__import__" --type py

# Check test dependencies
rg "config_legacy|yaml_legacy" tests/ --type py

# Search configs
rg "config_legacy|yaml_legacy" configs/ *.yaml *.yml
```

**Files to Create:**
- `.codex/reports/LEGACY_DEPENDENCIES.md` (dependency analysis)
- `scripts/generate_dependency_graph.py` (graph generation)
- `legacy_dependencies.svg` (visual dependency graph)

**Alternative if Blocked:**
- Manual code review if tooling incomplete
- Focus on direct dependencies first
- Document transitive deps for future cleanup

---

#### Phase 2: Legacy Code Migration and Modernization

**Pre-commit 5-6: Update All Legacy Imports**

**Goal:** Replace all legacy imports with modern equivalents

**Tasks:**
- [ ] Replace `config_legacy` imports with `hydra-core`:
  ```python
  # Before
  from config_legacy import compose, initialize
  
  # After
  from hydra import compose, initialize
  ```
- [ ] Replace `yaml_legacy` imports with `yaml`:
  ```python
  # Before
  from yaml_legacy import safe_load, safe_dump
  
  # After
  from yaml import safe_load, safe_dump
  ```
- [ ] Update all affected files
- [ ] Update test fixtures and mocks
- [ ] Verify all imports resolve correctly

**Success Criteria:**
- [ ] Zero imports of legacy modules remaining
- [ ] All files use modern imports
- [ ] Tests pass with new imports
- [ ] No import errors in any module

**Migration Script:**
```bash
# Automated migration
python scripts/migrate_legacy_imports.py \
  --module config_legacy \
  --replacement hydra \
  --dry-run

# Apply migration
python scripts/migrate_legacy_imports.py \
  --module config_legacy \
  --replacement hydra \
  --apply

# Verify no legacy imports remain
rg "config_legacy|yaml_legacy" --type py
```

**Files to Modify:**
- `src/tokenization/train_tokenizer.py` (1 import)
- All files with fallback imports (identified in Phase 1)
- Test files with legacy references

**Files to Create:**
- `scripts/migrate_legacy_imports.py` (migration automation)

**Alternative if Blocked:**
- Manual find-and-replace if automation fails
- Migrate files in batches
- Keep legacy modules temporarily with deprecation errors

---

**Pre-commit 7-8: Update Dependencies in Requirements**

**Goal:** Ensure modern dependencies are properly specified

**Tasks:**
- [ ] Verify `hydra-core>=1.3` in `pyproject.toml`
- [ ] Verify `pyyaml>=6.0` in `pyproject.toml`
- [ ] Remove any legacy package references
- [ ] Update dependency documentation
- [ ] Run dependency resolver to check conflicts
- [ ] Update lock files (uv.lock, if present)

**Success Criteria:**
- [ ] Modern dependencies explicitly listed
- [ ] No legacy package references
- [ ] Dependency resolution successful
- [ ] Lock files updated

**Files to Modify:**
- `pyproject.toml` (verify dependencies section)
- `requirements.txt` (verify modern packages)
- `uv.lock` (regenerate if present)

**Verification:**
```bash
# Check dependency installation
pip install -e .

# Verify imports work
python -c "import hydra; import yaml; print('OK')"

# Run dependency resolver
pip-compile pyproject.toml --resolver=backtracking
```

**Alternative if Blocked:**
- Add legacy dependencies as optional if needed
- Document migration path for users
- Keep backward compatibility layer temporarily

---

**Pre-commit 9-10: Comprehensive Testing After Migration**

**Goal:** Validate all functionality with modern imports

**Tasks:**
- [ ] Run complete test suite (1700+ tests)
- [ ] Execute integration tests
- [ ] Run Hydra configuration tests
- [ ] Test YAML loading/dumping
- [ ] Verify CLI commands work
- [ ] Test example scripts and notebooks
- [ ] Check documentation code examples
- [ ] Validate import performance

**Success Criteria:**
- [ ] 100% test pass rate maintained
- [ ] No import errors in any test
- [ ] Configuration loading works
- [ ] Example scripts run successfully

**Testing Commands:**
```bash
# Complete test suite
pytest tests/ -v --cov=src

# Integration tests
pytest tests/integration/ -v

# Hydra tests specifically
pytest tests/ -k "hydra or config" -v

# Test all examples
python examples/rag_workflow.py
python examples/training_pipeline.py

# Verify CLI
codex --help
codex config validate
```

**Alternative if Blocked:**
- Fix test failures incrementally
- Document any known issues
- Create regression test suite for legacy behavior

---

#### Phase 3: Legacy Code Removal

**Pre-commit 11-12: Remove Legacy Directories**

**Goal:** Delete deprecated shim modules and archived code

**Tasks:**
- [ ] Remove `config_legacy/` directory and all contents
- [ ] Remove `yaml_legacy/` directory and all contents
- [ ] Remove identified archive directories
- [ ] Remove commented-out code blocks
- [ ] Remove deprecated utility functions
- [ ] Update `.gitignore` if needed
- [ ] Clean up any remaining references

**Success Criteria:**
- [ ] All legacy directories deleted
- [ ] No broken references remaining
- [ ] Tests still pass after deletion
- [ ] Repository size reduced

**Directories to Remove:**
```
config_legacy/
  ├── __init__.py (248 lines)
  ├── errors.py (50 lines)
  └── README.md (documentation)

yaml_legacy/
  └── __init__.py (133 lines)

archive/ (selected subdirectories)
  └── [identify during audit]
```

**Removal Commands:**
```bash
# Safety check first
python scripts/verify_safe_to_remove.py --dir config_legacy

# Remove directories
git rm -r config_legacy/
git rm -r yaml_legacy/

# Remove archive directories
git rm -r archive/old_implementations/
git rm -r archive/deprecated_modules/

# Verify no broken imports
python scripts/check_imports.py
```

**Alternative if Blocked:**
- Keep directories but add clear deprecation errors
- Remove in stages over multiple releases
- Create compatibility package if needed

---

**Pre-commit 13-14: Update Documentation**

**Goal:** Remove all references to legacy code from documentation

**Tasks:**
- [ ] Update `CHANGELOG.md` with breaking changes
- [ ] Update `README.md` to remove legacy references
- [ ] Update `docs/CONFIGURATION.md` for modern Hydra
- [ ] Remove legacy code sections from guides
- [ ] Add migration guide for users
- [ ] Update API documentation
- [ ] Update troubleshooting guides
- [ ] Remove deprecated code examples

**Success Criteria:**
- [ ] No documentation references to legacy modules
- [ ] Migration guide complete and tested
- [ ] All code examples use modern imports
- [ ] Troubleshooting updated for new code

**Files to Update:**
- `CHANGELOG.md` (add breaking changes section)
- `README.md` (remove legacy references)
- `docs/CONFIGURATION.md` (update for modern Hydra)
- `docs/MIGRATION_GUIDE_V1_TO_V2.md` (new file)
- All documentation in `docs/` directory

**Migration Guide Template:**
```markdown
# Migration Guide: Legacy Code Removal

## Breaking Changes in v2.0.0

### config_legacy Removal
**Before:**
\`\`\`python
from config_legacy import compose
\`\`\`

**After:**
\`\`\`python
from hydra import compose
\`\`\`

### yaml_legacy Removal
**Before:**
\`\`\`python
from yaml_legacy import safe_load
\`\`\`

**After:**
\`\`\`python
from yaml import safe_load
\`\`\`

## Updated Dependencies
Ensure you have:
- hydra-core>=1.3.2
- pyyaml>=6.0

## Troubleshooting
[Common issues and solutions]
```

**Alternative if Blocked:**
- Update critical docs first, comprehensive later
- Link to external migration resources
- Provide automated migration script for users

---

**Pre-commit 15-16: Code Quality and Security Scan**

**Goal:** Verify removal didn't introduce issues

**Tasks:**
- [ ] Run linters (ruff, black, isort, mypy)
- [ ] Execute security scans (CodeQL, bandit, pip-audit)
- [ ] Check for unused imports
- [ ] Verify no dead code remaining
- [ ] Run code complexity analysis
- [ ] Check test coverage maintained
- [ ] Verify no security regressions

**Success Criteria:**
- [ ] Zero linting errors
- [ ] No new security vulnerabilities
- [ ] Test coverage maintained ≥72%
- [ ] Code complexity metrics improved

**Quality Commands:**
```bash
# Linting
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
mypy src/

# Security
codeql database analyze --format=sarif-latest
bandit -r src/ -f json -o security_report.json
pip-audit

# Coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Complexity
radon cc src/ -a -nc
```

**Alternative if Blocked:**
- Fix linting issues incrementally
- Document security scan exceptions
- Improve coverage in follow-up commits

---

**Pre-commit 17-18: Final Validation and Release Preparation**

**Goal:** Complete validation before release

**Tasks:**
- [ ] Run full CI/CD pipeline locally
- [ ] Execute all tests in clean environment
- [ ] Build package and verify contents
- [ ] Test package installation
- [ ] Verify example workflows
- [ ] Update version number (breaking change)
- [ ] Tag release candidate
- [ ] Generate release notes

**Success Criteria:**
- [ ] All CI checks passing
- [ ] Package builds successfully
- [ ] Clean installation verified
- [ ] Release notes complete

**Release Validation:**
```bash
# Clean environment test
python -m venv /tmp/test_env
source /tmp/test_env/bin/activate
pip install dist/codex_ml-2.0.0-py3-none-any.whl
python -c "import codex; print(codex.__version__)"
deactivate

# Run examples in clean env
cd /tmp/test_env
python -m codex.examples.rag_workflow

# Version bump (breaking change)
# Increment major version: 1.x.x -> 2.0.0

# Generate release notes
python scripts/generate_release_notes.py \
  --version 2.0.0 \
  --breaking-changes \
  --output RELEASE_NOTES_V2.md
```

**Files to Update:**
- `pyproject.toml` (version = "2.0.0")
- `src/codex/__init__.py` (__version__ = "2.0.0")
- `CHANGELOG.md` (add v2.0.0 section)
- `RELEASE_NOTES_V2.md` (new file)

**Alternative if Blocked:**
- Create release candidate first (v2.0.0-rc1)
- Extended testing period before final release
- Phased rollout if possible

---

### Review, Verify, Commit

**Final Checklist:**
- [ ] All 18 pre-commits completed
- [ ] Zero legacy code remaining
- [ ] All tests passing (1700+)
- [ ] Documentation updated
- [ ] Migration guide complete
- [ ] Security scans clean
- [ ] Version bumped appropriately
- [ ] Release notes prepared

---

## AI Agency Policy Compliance

### Comprehensive Issue Resolution
✅ Complete legacy code removal (not partial)
✅ Root cause addressed (deprecated shims removed)
✅ Prevention strategy (better dependency management)

### Planning Before Execution
✅ 3 phases with 18 pre-commits
✅ Clear success criteria for each step
✅ Dependencies and ordering documented

### No Deferral Without Plan
✅ All blockers identified (breaking change approval)
✅ Best-effort alternatives documented
✅ Minimum 5 iterations met (18 pre-commits)

### Timeline Terminology
✅ Uses pre-commit/commit cycles
✅ Organized into Phases
✅ No time-based estimates

---

## Blocker Documentation and Alternatives

### Known Blockers

1. **Breaking Change Approval**
   - **Task:** HA-LEGACY-1
   - **Blocker:** Requires human decision for backward incompatibility
   - **AI Agent Alternative:** Generate impact analysis, propose mitigation strategies

2. **Hidden Dynamic Imports**
   - **Task:** Phase 1-2 (discovery, migration)
   - **Blocker:** Runtime imports may not be statically detectable
   - **AI Agent Alternative:** Comprehensive testing, runtime instrumentation

3. **External User Compatibility**
   - **Task:** Phase 3 (removal)
   - **Blocker:** Unknown external usage patterns
   - **AI Agent Alternative:** Provide compatibility layer, detailed migration guide

---

## Success Metrics

### Quantitative
- Code reduction: ~500+ lines removed
- Repository size: -5% after cleanup
- Import time: -10% (no shim overhead)
- Test pass rate: 100% maintained
- Coverage: ≥72% maintained

### Qualitative
- Cleaner architecture
- Reduced maintenance burden
- Improved documentation clarity
- Better onboarding experience
- Eliminated technical debt

---

## Cognitive Brain Context

This planset is designed for autonomous execution with the following understanding:

1. **Breaking Change:** Major version bump required
2. **Comprehensive Testing:** Validate everything after removal
3. **User Impact:** Migration guide is critical
4. **Documentation:** Update all references
5. **Safety First:** Multiple validation checkpoints

The cognitive brain should approach this work with:
- **Caution:** Breaking changes require extra care
- **Thoroughness:** Find all references before removing
- **User empathy:** Provide excellent migration guide
- **Quality focus:** No regressions tolerated

---

## Estimated Effort

- **AI Agent Autonomous Work:** 18 pre-commits (3 phases)
- **Human Admin Manual Tasks:** 1 task (breaking change approval)
- **Total Phases:** 3 phases
- **Complexity:** Medium (requires careful testing)

---

## Version Upgrade Strategy

### Semantic Versioning

**Current Version:** 1.x.x (assuming)
**Target Version:** 2.0.0 (breaking changes)

**Versioning Rationale:**
- Removal of public modules (`config_legacy`, `yaml_legacy`) = BREAKING
- Changed import paths = BREAKING
- Major version bump required per semver

### Release Timeline

**Phase 1:** Deprecation warnings (if not already present)
- Add warnings to legacy modules
- Update documentation with deprecation notice
- Announce planned removal

**Phase 2:** Release candidate
- Create v2.0.0-rc1 with legacy code removed
- Extended testing period
- Gather user feedback

**Phase 3:** Final release
- Release v2.0.0 with complete removal
- Publish migration guide
- Announce breaking changes

---

## Next Steps

For AI Agent to begin autonomous execution:

```markdown
@copilot Begin Legacy Code Removal implementation following `.codex/plans/LEGACY_CODE_REMOVAL_PLANSET.md`.

Start with Phase 1: Legacy Code Discovery and Analysis.

**Policy Compliance:**
- Follow `.codex/CODEBASE_AGENCY_POLICY.md`
- Use pre-commit/commit terminology
- 5+ self-review iterations
- Address ALL issues discovered
- Test comprehensively before removal

**Success Criteria:**
- ✅ All legacy code removed (config_legacy/, yaml_legacy/)
- ✅ 100% test pass rate maintained
- ✅ Complete migration guide provided
- ✅ Documentation updated
- ✅ Version bumped to 2.0.0
```

---

**Status:** Ready for autonomous AI Agent execution with documented Human Admin checkpoint (breaking change approval)
