Agent completed. agent_id: phase-5-root-organizer-audit, agent_type: explore, status: completed, description: Phase 5.3: Root Directory Layout Audit, elapsed: 150s, total_turns: 0, duration: 133s

### DVC & MLflow (ML Workflow Tools)
```
Current: dvc.yaml at root, .dvc/ directory, .mlruns/ directory
Target:  Consolidate ML configs to /ml/ or keep at root if active
Action:  VERIFY dvc.yaml and .dvc/ are actively used
         CONSOLIDATE .mlruns/ → /ml/experiments/ (if ongoing)
         DOCUMENT: DVC pipeline structure in /docs/ml/
```

### Semgrep (SAST Analysis)
```
Current: .semgrep/ (32KB), semgrep/ dir, semgrep_rules/ dir (3 locations!)
Target:  /semgrep/ (single directory)
Action:  CONSOLIDATE: .semgrep/ → /semgrep/.internal/
         CONSOLIDATE: semgrep_rules/ → /semgrep/rules/
         CREATE: /semgrep/patterns/ for pattern files
         MERGE: .semgrepignore into /semgrep/.semgrepignore
```

### CodeQL (GitHub SAST)
```
Current: .codeql/ directory at root
Target:  Keep in place (GitHub expects it) OR move to .github/codeql/
Action:  CHECK: If .github/codeql/ exists and is redundant
         CONSIDER: Moving .codeql/ → .github/codeql-custom/
         DOCUMENT: CodeQL configuration in /docs/security/
```

### Import-Linter (Python Imports)
```
Current: .importlinter file at root (hidden)
Target:  /config/.importlinter
Action:  MOVE: .importlinter → /config/.importlinter
         UPDATE: Setup.py or build tools to new location
         VERIFY: import-linter still finds the config
```

### Requirements Management
```
Current: 10 files at root (requirements*.txt)
Target:  /requirements/ directory with:
         - pyproject.toml with [project.optional-dependencies]
         - OR /requirements/ with index and variant files
         
Action:  OPTION A (Recommended): Use pyproject.toml extras
         [project.optional-dependencies]
         dev = ["pytest>=7.0", "black", ...]
         ml-cpu = ["torch[cpu]>=2.0", ...]
         notebook = ["jupyter>=1.0", ...]
         
         OPTION B: Directory structure
         /requirements/
           base.txt (from requirements.txt)
           dev.txt
           ml-cpu.txt
           ml-lite.txt
           notebook.txt
           ... etc
           
         UPDATE: All pip install commands
         UPDATE: GitHub Actions workflows
         UPDATE: Development docs
```

---

## 10. CONFIGURATION VALIDATION CHECKLIST

Before implementing any consolidation, verify with this checklist:

### Config Dependency Verification:

```
□ .bandit.yaml
  - Verify .bandit.yml and bandit.yaml are NOT different
  - Test: bandit scan works with only .bandit.yaml
  - Check: CI/CD uses the correct file

□ .pre-commit-config.yaml
  - Compare: .pre-commit-hybrid.yaml vs .pre-commit-ruff.yaml
  - Identify: Which hooks are in each
  - Create: Merged .pre-commit-config.yaml with all hooks
  - Test: pre-commit run --all-files works

□ pytest.ini
  - Compare: pytest.ini vs pytest_mutation_override.ini vs pytest_mutmut_override.ini
  - Identify: Conflicting settings
  - Create: Single pytest.ini with [mutmut] and [mutation] sections
  - Test: pytest, pytest with mutmut both work

□ .mutmut.ini
  - Review: .mutmut-*.ini files for unique settings
  - Consolidate: All unique settings into .mutmut.ini
  - Test: mutmut test works with consolidated config
  - Delete: All variant files

□ mypy.ini
  - Extract: Baseline from .mypy-baseline.txt and .mypy_baseline
  - Merge: Into mypy.ini as [mypy] section
  - Test: mypy --config-file=mypy.ini works

□ Lock files (Cargo.lock, uv.lock, package-lock.json)
  - Verify: Each is actively maintained
  - Identify: Can any be removed safely?
  - Decision: Keep as-is (needed for reproducibility)

□ Environment files (.env, .env.docker.example)
  - Review: What variables are actually needed
  - Consolidate: Into single .env.template at /config/
  - Test: Application loads with new template
```

---

## 11. IMPLEMENTATION SCRIPTS & HELPERS

### Script 1: Root File Inventory Report
```bash
#!/bin/bash
# Generate comprehensive inventory of root-level files

echo "=== ROOT DIRECTORY BLOAT ANALYSIS ===" > root-audit.txt
echo "Generated: $(date)" >> root-audit.txt
echo "" >> root-audit.txt

# Count files by type
echo "## FILE COUNTS BY TYPE:" >> root-audit.txt
echo "Config files: $(find . -maxdepth 1 -type f \( -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o -name '*.ini' -o -name '*.json' \) | wc -l)" >> root-audit.txt
echo "Documentation: $(find . -maxdepth 1 -type f -name '*.md' | wc -l)" >> root-audit.txt
echo "Requirements: $(find . -maxdepth 1 -type f -name 'requirements*.txt' | wc -l)" >> root-audit.txt
echo "Test configs: $(find . -maxdepth 1 -type f -name 'pytest*.ini' -o -name '*mutmut*.ini' | wc -l)" >> root-audit.txt
echo "Reports: $(find . -maxdepth 1 -type f -name 'PHASE_*' -o -name '*REPORT*' -o -name '*SUMMARY*' | wc -l)" >> root-audit.txt
echo "Total files: $(find . -maxdepth 1 -type f | wc -l)" >> root-audit.txt
```

### Script 2: Config Consolidation Validator
```bash
#!/bin/bash
# Validate that consolidated configs work correctly

echo "Testing Bandit consolidation..."
bandit -c .bandit.yaml -r src/ > /dev/null && echo "✓ .bandit.yaml works"

echo "Testing Pytest consolidation..."
pytest --collect-only > /dev/null && echo "✓ pytest.ini works"

echo "Testing MutMut consolidation..."
mutmut run --version > /dev/null && echo "✓ .mutmut.ini works"

echo "Testing Pre-commit..."
pre-commit run --all-files > /dev/null && echo "✓ pre-commit-config works"

echo "Testing Mypy..."
mypy --config-file=mypy.ini src/ > /dev/null && echo "✓ mypy.ini works"
```

### Script 3: Safe File Migration
```bash
#!/bin/bash
# Safely migrate files with backup

ARCHIVE_DIR=".archive/$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

# Function to safely move files
safe_move() {
    local source=$1
    local target=$2
    if [ -f "$source" ]; then
        cp "$source" "$ARCHIVE_DIR/$(basename $source)"
        mv "$source" "$target"
        echo "Moved $source → $target (backup in $ARCHIVE_DIR)"
    fi
}

# Example usage:
safe_move "requirements-dev.txt" "requirements/dev.txt"
safe_move ".bandit.yml" ".bandit.yaml.old"
```

---

## 12. DOCUMENTATION UPDATES NEEDED

After consolidation, update these documents:

### /docs/getting-started/setup.md
```
Update paths for:
- requirement installation (new /requirements/ location)
- configuration files (new /config/ location)
- scripts (new /scripts/ location)
```

### /docs/development/configuration.md
```
ADD:
- Configuration consolidation overview
- Each tool's new config location
- How to modify each config type
```

### /docs/contributing/development-setup.md
```
UPDATE:
- Virtual environment setup (with new requirement paths)
- Tool configuration (with new locations)
- Pre-commit hook installation (with new script locations)
```

### README.md
```
UPDATE:
- Root directory structure section
- Quick start configuration
- Configuration file locations
```

### .gitignore
```
VERIFY/UPDATE:
- No hardcoded paths to old config locations
- Ensure new /config/ paths are ignored appropriately
- Ensure /archive/ is properly ignored
```

---

## 13. MIGRATION TIMELINE WITH DEPENDENCIES

### Week 1: Preparation & Quick Wins
```
Day 1-2: Audit & Dependency Verification
  □ Run dependency validation checklist
  □ Identify any hidden dependencies
  □ Update team documentation

Day 3: Quick Wins (Safe Deletions)
  □ Delete 8 obsolete MutMut configs
  □ Delete 3 empty files
  □ Delete 2 backup files
  - Tests should still pass: verify

Day 4-5: Archive & Consolidate Duplicates
  □ Create /archive/audits/ directory
  □ Move 63 phase/audit reports
  □ Consolidate Bandit configs (2 deleted)
  □ Consolidate Pytest configs (2 deleted)
  □ Consolidate Pre-commit (1 unified)
  - Tests should still pass: verify
  - CI/CD workflows should still work: verify

Result: 75+ files removed from root
```

### Week 2: Configuration Directory Refactor
```
Day 1-2: Create /config/ consolidation
  □ Create /config/ directory structure
  □ Move all config files to /config/
  □ Create /config/.legacy/ for legacy configs
  □ Ensure tools can find configs at new location
  - Symlinks at root if needed for backward compatibility
  - Tests should still pass: verify

Day 3-4: Requirements migration
  □ Create /requirements/ directory (or use pyproject.toml)
  □ Move all requirements-*.txt files
  □ Update all pip install commands in CI/CD
  □ Update development documentation
  - Tests should still pass: verify
  - CI/CD workflows should work with new paths: verify

Day 5: Script consolidation
  □ Consolidate scripts/, .scripts/, .pre-commit-scripts/
  □ Create scripts/internal/ and scripts/pre-commit/
  □ Update .pre-commit-config.yaml with new paths
  - Tests should still pass: verify

Result: Major root-level cleanup, 20+ additional files consolidated
```

### Week 3: Documentation & Secondary Consolidation
```
Day 1-2: Docs migration
  □ Create /docs/agents/, /docs/security/, /docs/remediation/
  □ Move supplementary documentation
  □ Update README.md with new structure
  □ Update internal doc links
  - Verify all doc links still work: verify

Day 3-4: Directory consolidation
  □ Consolidate conf/ → config/
  □ Consolidate config_legacy/ → config/.legacy/
  □ Consolidate config_experiments/ → config/experiments/
  □ Consolidate semgrep/ directories
  □ Consolidate copilot/ configuration
  - Tests should still pass: verify
  - Tools should find all configs: verify

Day 5: Testing & QA
  □ Full test suite execution
  □ CI/CD workflow testing
  □ Manual smoke tests
  □ Verify developer setup still works

Result: Clean, organized directory structure, all documentation updated
```

### Week 4: Environment & Validation
```
Day 1: Environment cleanup
  □ Remove .venv_ci from repo (should be CI artifact)
  □ Create /config/.env.template
  □ Document environment setup
  □ Remove venv_test (use ephemeral environments)
  - CI/CD should work: verify
  - Local development should work: verify

Day 2-3: Final validation & testing
  □ Run all test suites
  □ Verify CI/CD workflows
  □ Verify developer onboarding works
  □ Check for any broken tool integrations
  □ Performance benchmarking (should be no change)

Day 4: Documentation & Knowledge Transfer
  □ Create /docs/migration/ directory with:
     - Before/after structure diagram
     - Tool-by-tool location changes
     - Troubleshooting guide
  □ Update contributing guide
  □ Brief team on changes

Day 5: Prevention & Monitoring
  □ Add pre-commit hook: max root files = 30
  □ Add GitHub Actions: block PRs adding to root
  □ Add guidelines to CONTRIBUTING.md
  □ Schedule post-migration audit (2 weeks)

Result: Complete migration, clean repo, prevention measures in place
```

---

## 14. BEFORE/AFTER STRUCTURE COMPARISON

### CURRENT STATE (205 root files, 51 directories):
```
/home/runner/work/_codex_/_codex_/
├── [Config files scattered everywhere]
│   ├── .bandit.yaml, .bandit.yml, bandit.yaml
│   ├── .pre-commit-hybrid.yaml, .pre-commit-ruff.yaml
│   ├── pytest.ini, pytest_mutation_override.ini, pytest_mutmut_override.ini
│   ├── .mutmut.ini + 8 variant files
│   ├── mypy.ini, .mypy-baseline.txt, .mypy_baseline
│   ├── .yamllint.yml, .markdownlintrc, .fencefixer.yml
│   ├── .gitleaks.toml, .importlinter, deny.toml
│   ├── .coveragerc, .statusrc.json
│   ├── dvc.yaml, params.yaml
│   ├── pyproject.toml, Cargo.toml, package.json
│   ├── mkdocs.yml, commitlint.config.mjs
│   └── ...
├── [Requirements files at root]
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── requirements-test.txt
│   ├── requirements-eval.txt
│   ├── requirements-optional.txt
│   ├── requirements-minimal.txt
│   ├── requirements-ml-cpu.txt
│   ├── requirements-ml-lite.txt
│   ├── requirements-notebook.txt
│   └── requirements-audio-transcription.txt
├── [Phase & Audit Reports at root - 63 files]
│   ├── PHASE_1_AGENTS_AUDIT.md
│   ├── PHASE_2_TRACK_4_*.md
│   ├── PHASE_3_TEAM_4_*.md
│   ├── ... [45+ more phase files]
│   ├── AGENT_ACCOUNTABILITY_REPORT.md
│   ├── AUDIT_COMPLETION_SUMMARY.txt
│   ├── DOCUMENTATION_AUDIT_*.md
│   └── ...
├── [Documentation files at root - 83 md files]
│   ├── README.md ✓ (keep)
│   ├── AGENTS.md → move to /docs/agents/
│   ├── CLAUDE.md → move to /docs/ai-models/
│   ├── GEMINI.md → move to /docs/ai-models/
│   ├── SECURITY.md ✓ (keep)
│   ├── SECURITY_REMEDIATION_GUIDE.md → move to /docs/security/
│   └── [20+ more supplementary docs]
├── [Directories with duplicates]
│   ├── scripts/
│   ├── .scripts/ (DUPLICATE)
│   ├── .pre-commit-scripts/ (DUPLICATE)
│   ├── conf/
│   ├── config/
│   ├── configs/ (DUPLICATE)
│   ├── config_legacy/
│   ├── .config/
│   ├── .config.legacy/
│   ├── config_experiments/
│   ├── .semgrep/
│   ├── semgrep/
│   ├── semgrep_rules/
│   ├── .copilot-space/
│   ├── copilot/
│   └── ...
└── [Source & Test]
    ├── src/
    └── tests/
```

### TARGET STATE (After consolidation):
```
/home/runner/work/_codex_/_codex_/
├── [Core documentation only]
│   ├── README.md ✓
│   ├── LICENSE ✓
│   ├── CHANGELOG.md ✓
│   ├── CODE_OF_CONDUCT.md ✓
│   ├── CONTRIBUTING.md ✓
│   ├── SECURITY.md ✓
│   ├── CITATION.cff ✓
│   └── .nojekyll ✓
├── [Source & Tests]
│   ├── src/
│   └── tests/
├── [Consolidated config directory]
│   └── config/
│       ├── .bandit.yaml (consolidated from 3)
│       ├── .pre-commit-config.yaml (consolidated from 2)
│       ├── pytest.ini (consolidated from 3)
│       ├── .mutmut.ini (consolidated from 9)
│       ├── mypy.ini (consolidated from 3)
│       ├── .yamllint.yml
│       ├── .markdownlintrc
│       ├── .fencefixer.yml
│       ├── .gitleaks.toml
│       ├── .importlinter
│       ├── deny.toml
│       ├── .coveragerc
│       ├── dvc.yaml
│       ├── params.yaml
│       ├── .env.template
│       ├── .legacy/ (legacy configs)
│       └── experiments/ (experimental configs)
├── [Consolidated requirements]
│   └── requirements/
│       ├── base.txt
│       ├── dev.txt
│       ├── test.txt
│       ├── eval.txt
│       ├── ml-cpu.txt
│       └── ...
├── [Scripts consolidated]
│   └── scripts/
│       ├── setup.sh
│       ├── validate-config.sh
│       ├── internal/ (from .scripts/)
│       └── pre-commit/ (from .pre-commit-scripts/)
├── [Consolidated docs]
│   └── docs/
│       ├── index.md
│       ├── agents/ (AGENTS.md, CLAUDE.md, GEMINI.md)
│       ├── security/ (SECURITY_*.md)
│       ├── development/ (dev docs)
│       ├── ml/ (ML-specific)
│       ├── api/ (API documentation)
│       ├── migration/ (migration guides)
│       └── phase-documentation/ (reference material)
├── [Archived historical reports]
│   └── archive/
│       ├── audits/
│       │   ├── phase-reports/ (PHASE_*.md - 48 files)
│       │   └── completion-reports/ (audit files - 15 files)
│       └── ...
├── [Output/Reports]
│   └── reports/
│       ├── json/ (*.json outputs)
│       ├── logs/ (*.log files)
│       └── coverage/
├── [Data & ML]
│   ├── data/
│   ├── datasets/
│   ├── models/
│   ├── ml/
│   │   ├── experiments/
│   │   ├── mlflow/
│   │   └── training/
│   └── ...
├── [Core infrastructure]
│   ├── .github/ (workflows, actions)
│   ├── .git/ (version control)
│   ├── .gitignore ✓
│   ├── .devcontainer/ (dev container)
│   ├── docker/ (Docker files)
│   ├── k8s/ (Kubernetes)
│   ├── pyproject.toml ✓
│   ├── Cargo.toml ✓
│   ├── Cargo.lock ✓
│   ├── package.json ✓
│   ├── package-lock.json ✓
│   ├── uv.lock ✓
│   └── mkdocs.yml ✓
└── [Agents & Core Modules]
    ├── agents/
    ├── services/
    ├── tools/
    ├── utils/
    └── ...
```

---

## 15. ROLLBACK PROCEDURES

If any consolidation causes issues:

### Quick Rollback (within 24 hours):
```bash
# If you have backups in .archive/:
git restore <filename>  # Restore from version control
# OR
cp .archive/<date>/filename .  # Restore from backup

# If you need to revert a directory move:
git reset --hard HEAD~1  # Undo last commit
```

### Symlink Fallback:
```bash
# If tools can't find configs at new locations:
ln -s config/.bandit.yaml .bandit.yaml
ln -s config/pytest.ini pytest.ini
ln -s requirements dev-requirements.txt

# This provides backward compatibility while migrating
```

### Test-First Approach:
```bash
# Before committing any change:
1. Run full test suite
2. Run CI/CD pipeline locally
3. Test all affected tools
4. Verify developer experience

# Only commit if all tests pass
git commit -m "Refactor: Consolidate configurations"
```

---

## 16. SUCCESS VALIDATION CHECKLIST

After completing all phases, verify:

```
□ Root-level files reduced to < 30
  Current: 205
  Target: < 30
  After Phases 1-4: ~20-25 files (✓)

□ All config files consolidated to /config/
  ✓ .bandit.yaml (consolidated from 3)
  ✓ .pre-commit-config.yaml (consolidated from 2)
  ✓ pytest.ini (consolidated from 3)
  ✓ .mutmut.ini (consolidated from 9)
  ✓ mypy.ini (consolidated from 3)
  ✓ All other configs in /config/

□ Requirements files migrated to /requirements/
  ✓ base.txt
  ✓ dev.txt
  ✓ test.txt
  ✓ All variants

□ Documentation consolidated to /docs/
  ✓ Core docs at root (README, LICENSE, CODE_OF_CONDUCT, etc.)
  ✓ Supplementary docs in /docs/
  ✓ Internal links updated

□ Phase reports archived to /archive/
  ✓ All PHASE_*.md files moved
  ✓ All audit reports moved
  ✓ Archive accessible for reference

□ Scripts consolidated to /scripts/
  ✓ Primary scripts in /scripts/
  ✓ Internal scripts in /scripts/internal/
  ✓ Pre-commit scripts in /scripts/pre-commit/

□ All tests pass
  ✓ Unit tests pass
  ✓ Integration tests pass
  ✓ CI/CD pipeline succeeds
  ✓ Type checking passes (mypy)
  ✓ Linting passes (ruff, pylint)
  ✓ Security scans pass (bandit, semgrep)

□ No tool regressions
  ✓ Pre-commit hooks work
  ✓ Testing framework works
  ✓ Type checking works
  ✓ Documentation generation works
  ✓ All integrations work

□ Developer experience maintained or improved
  ✓ Setup process still works
  ✓ Development environment loads correctly
  ✓ All IDE integrations work
  ✓ Contributing guide is clear

□ Prevention measures in place
  ✓ Pre-commit hook: max root files = 30
  ✓ GitHub Actions: block root-level config additions
  ✓ Updated CONTRIBUTING.md with guidelines
  ✓ Documentation updated
```

---

## 17. FINAL RECOMMENDATIONS

### Immediate Actions (Next 24 hours):
1. ✅ **Review this audit report** with team
2. ✅ **Get stakeholder approval** for Phase 1 quick wins
3. ✅ **Create backup** of current state
4. ✅ **Schedule cleanup week** (Week 1-4 of next sprint)

### Priority Order:
1. **Week 1 - Phase 1:** Archive reports, delete obsolete configs (75 files)
2. **Week 2 - Phase 2:** Consolidate config & requirements (60 more files)
3. **Week 3 - Phase 3:** Reorganize documentation & directories (20 more files)
4. **Week 4 - Phase 4:** Cleanup, validation, prevention

### Key Success Factors:
- **Test-driven:** Verify every change works
- **Gradual:** Do small, atomic changes
- **Documented:** Update all docs simultaneously
- **Reversible:** Keep git history, use symlinks if needed
- **Communicated:** Keep team informed

### Prevention Going Forward:
- Add pre-commit hook limiting root files to 30
- Document "where things go" in CONTRIBUTING.md
- Review root directory monthly (5-minute audit)
- Block PRs that add to root without justification

---

## CONCLUSION

**Current State:** 205 root-level files = 6.8x over acceptable threshold
- **52 config files** scattered across root
- **63 audit/phase reports** clogging the root
- **83 markdown files** at root level
- **10 requirements files** should be in /requirements/
- **12+ duplicate configurations** (bandit, pre-commit, pytest, mutmut, mypy)

**Target State:** <30 root files with clean organization
- All configs in /config/
- All requirements in /requirements/
- All docs in /docs/
- All reports in /archive/ or /reports/
- Zero duplicate configurations
- Clear directory structure

**Timeline:** 4 weeks, phased approach
**Risk Level:** Low (with proper testing)
**Effort:** 40-50 hours total

**Next Step:** Schedule consolidation work and begin Phase 1.

---

*Audit completed: Root Directory Organization Analysis*
*Status: Complete - Ready for implementation*
*Recommendation: Proceed with Phase 1 (Quick Wins) immediately*