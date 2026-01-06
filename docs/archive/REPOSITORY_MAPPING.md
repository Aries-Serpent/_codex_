# Codex Repository File Mapping (v1.4.0)

**Generated**: Previous Cycle-12-09  
**Purpose**: Quick reference for navigating the _codex_ repository structure  
**Audience**: AI agents, contributors, maintainers

## 📊 Quick Navigation Matrix

### Core Entry Points
| File | Purpose | Dependencies | Updates |
|------|---------|--------------|---------|
| `README.md` | Repository overview | None | Monthly |
| `AGENTS.md` | Agent operations guide | README | Per release |
| `Traversal_Workflow.md` | Audit pipeline spec | None | Per version |
| `status_update_YYYY-MM-DD.md` | Iteration report | Audit artifacts | Per iteration |

### Configuration Files
| File | Purpose | Format | Validation |
|------|---------|--------|-----------|
| `pyproject.toml` | Package metadata | TOML | setuptools |
| `pytest.ini` | Test configuration | INI | pytest |
| `noxfile.py` | Automation sessions | Python | nox |
| `.pre-commit-config.yaml` | Pre-commit hooks | YAML | pre-commit |
| `.copilot-space/workflow.yaml` | Audit pipeline config | YAML | audit_runner.py |
| `configs/*.yaml` | Hydra configs | YAML | tools/validate_configs.py |

### Source Code Structure
```
src/codex_ml/
├── tokenization/
│   ├── base.py                    # ByteLevelTokenizer (max_length validation)
│   └── __init__.py
├── reproducibility/
│   ├── seed_manager.py            # SeedManager (PYTHONHASHSEED warning)
│   └── __init__.py
├── tracking/
│   ├── writers.py                 # MLflow integration (_flatten_dict escaping)
│   └── __init__.py
├── config/
│   ├── deprecation.py             # Legacy config warnings
│   └── __init__.py
└── ...
```

### Test Structure
```
tests/
├── tokenization/
│   └── test_base.py               # Tokenizer validation tests
├── reproducibility/
│   └── test_seed_manager.py       # Seed manager tests
├── tracking/
│   └── test_enhanced_writers.py   # MLflow writer tests (tmp_path fixture)
├── config/
│   └── test_deprecation.py        # Deprecation warning tests
└── ...
```

### Audit Pipeline Files
```
.copilot-space/
└── workflow.yaml                  # Pipeline configuration (v1.4.0)

scripts/space_traversal/
├── audit_runner.py                # Main orchestrator (S1-S7)
├── detectors/
│   ├── ml_serving.py              # ML serving detector
│   ├── status_reporting.py        # Status reporting detector
│   ├── archival_bundling.py       # Archival detector
│   └── ...                        # 36 more detectors
└── templates/
    └── audit/
        └── capability_matrix.md.j2 # Report template

audit_artifacts/
├── context_index.json             # S1 output: file inventory
├── facets.json                    # S2 output: domain clusters
├── capabilities_raw.json          # S3 output: detected capabilities
├── capabilities_scored.json       # S4 output: scored capabilities
├── gaps.json                      # S5 output: low-maturity items
└── _scoring_warnings.json         # Validation warnings

reports/
├── capability_matrix_<ts>.md      # S6 output: human-readable
├── capability_matrix_<ts>.json    # S6 output: machine-readable
└── codex_status_update_<date>.md  # S6 output: daily status

audit_run_manifest.json            # S7 output: integrity manifest
```

### Documentation Structure
```
docs/
├── SPACE_TRAVERSAL_GUIDE.md       # Complete audit pipeline guide
├── DUPLICATE_DETECTION.md         # Duplicate detection system
├── QUALITY_GATES.md               # Quality gate documentation
├── CLI.md                         # CLI usage guide
├── INFERENCE_SERVING_GUIDE.md     # Inference serving guide
├── api/                           # API reference (auto-generated)
├── architecture/                  # Architecture diagrams
└── diagrams/
    ├── audit_pipeline_v1.4.0.mmd  # Audit pipeline flowchart
    └── architecture.mmd           # System architecture
```

## 🔄 Update Cycles

### Daily
- `reports/codex_status_update_<date>.md` - Automated status issue body
- `.codex/sessions/` - Session logs

### Weekly  
- Audit pipeline run (S1-S7)
- `audit_run_manifest.json` - Fresh integrity manifest
- `reports/capability_matrix_<timestamp>.md` - Latest capability scores

### Monthly
- `status_update_YYYY-MM-DD.md` - Comprehensive iteration report
- `README.md` - Latest updates section
- Dependency updates via dependabot

### Per Release
- `AGENTS.md` - Version bump + new features
- `Traversal_Workflow.md` - Specification updates
- `CHANGELOG.md` - Release notes
- Documentation in `docs/`

### On Demand
- `pyproject.toml` - Dependency changes
- `.copilot-space/workflow.yaml` - Weight/threshold tuning
- Test files - Per feature implementation

## 🎯 Critical File Relationships

### Verification Chain (PR #2449)
```
status_update_2025-12-09.md
    ├── references → src/codex_ml/tokenization/base.py (lines 62-66)
    ├── references → src/codex_ml/reproducibility/seed_manager.py (lines 107-115)
    ├── references → tests/tracking/test_enhanced_writers.py (lines 142-162)
    └── references → tests/config/test_deprecation.py (multiple test cases)
```

### Audit Pipeline Chain
```
.copilot-space/workflow.yaml (config)
    ↓
scripts/space_traversal/audit_runner.py (orchestrator)
    ↓
audit_artifacts/*.json (stage outputs S1-S5)
    ↓
templates/audit/capability_matrix.md.j2 (template)
    ↓
reports/capability_matrix_<ts>.md (rendered report)
    ↓
audit_run_manifest.json (integrity manifest)
```

### Configuration Validation Chain
```
configs/*.yaml (Hydra configs)
    ↓
tools/validate_configs.py (validator)
    ↓
noxfile.py (config_validation session)
    ↓
CI/CD (automated check)
```

### Test Execution Chain
```
pytest.ini (configuration)
    ↓
tests/**/*.py (test suites)
    ↓
noxfile.py (test session)
    ↓
CI/CD (GitHub Actions)
```

## 📁 Directory Purposes

| Directory | Purpose | Gitignore | Writable |
|-----------|---------|-----------|----------|
| `.codex/` | Evidence, logs, task mappings | Partial | Yes |
| `.copilot-space/` | Audit pipeline config | No | Yes |
| `audit_artifacts/` | Pipeline outputs (S1-S5) | No | Yes |
| `reports/` | Human-readable reports | No | Yes |
| `src/codex_ml/` | Core library code | No | No* |
| `tests/` | Test suites | No | No* |
| `docs/` | Documentation | No | Yes |
| `configs/` | Hydra configurations | No | Yes |
| `scripts/` | Automation scripts | No | Yes |
| `tools/` | Utility scripts | No | Yes |

*Read-only except during feature development

## 🔗 External Integration Points

### GitHub Actions Workflows
- `.github/workflows/status_validation.yml` → `tools/status/codex_status_cli.py`
- `.github/workflows/security_gates.yml` → `tools/security/scan_repo.py`
- `.github/workflows/nox_gates.yml` → `noxfile.py`

### Pre-commit Hooks
- `.pre-commit-config.yaml` → ruff, black, isort, bandit, detect-secrets

### MLflow Integration
- `src/codex_ml/tracking/writers.py` → MLflow API
- `configs/tracking/*.yaml` → Tracking configuration

### Hydra Configuration
- `configs/` → Application configs
- `hydra/` → Hydra-specific configs
- `src/codex_ml/config/` → Config dataclasses

## 🎨 File Naming Conventions

### Status Reports
- Format: `status_update_YYYY-MM-DD.md`
- Location: Repository root
- Example: `status_update_2025-12-09.md`

### Capability Matrices
- Format: `capability_matrix_<timestamp>.md`
- Location: `reports/`
- Example: `capability_matrix_20251209_143025.md`

### Test Files
- Format: `test_<module>.py`
- Location: `tests/<component>/`
- Example: `tests/tokenization/test_base.py`

### Detectors
- Format: `<capability_id>.py`
- Location: `scripts/space_traversal/detectors/`
- Example: `ml_serving.py`

### Documentation
- Format: `<TOPIC>_<TYPE>.md` or `<TOPIC>.md`
- Location: `docs/`
- Examples: `SPACE_TRAVERSAL_GUIDE.md`, `DUPLICATE_DETECTION.md`

## 🔍 Quick Search Patterns

### Find Implementation
```bash
# Tokenizer implementation
find src -name "base.py" -path "*/tokenization/*"

# Seed manager
find src -name "seed_manager.py" -path "*/reproducibility/*"

# MLflow writers
find src -name "writers.py" -path "*/tracking/*"
```

### Find Tests
```bash
# Tokenizer tests
find tests -name "test_base.py" -path "*/tokenization/*"

# Deprecation tests
find tests -name "test_deprecation.py" -path "*/config/*"
```

### Find Documentation
```bash
# Audit pipeline docs
find docs -name "*TRAVERSAL*" -o -name "*AUDIT*"

# Status reports
ls -1 status_update_*.md

# Capability matrices
ls -1 reports/capability_matrix_*.md
```

## 📊 Dependency Graph (Key Files)

```
pyproject.toml
    ├── defines → console_scripts (CLI entry points)
    ├── defines → dependencies (runtime requirements)
    └── defines → optional-dependencies (extras)

noxfile.py
    ├── uses → pyproject.toml (version info)
    ├── defines → test sessions
    ├── defines → lint sessions
    └── defines → build sessions

.pre-commit-config.yaml
    ├── uses → pyproject.toml (hooks config)
    └── defines → pre-commit hooks

.copilot-space/workflow.yaml
    ├── defines → audit weights
    ├── defines → capability thresholds
    └── defines → detector overrides

scripts/space_traversal/audit_runner.py
    ├── reads → .copilot-space/workflow.yaml
    ├── reads → scripts/space_traversal/detectors/*.py
    ├── writes → audit_artifacts/*.json
    └── writes → audit_run_manifest.json
```

## 🏗️ Build Artifacts

### Generated by Tests
- `.pytest_cache/` - Pytest cache (gitignored)
- `.coverage` - Coverage data (gitignored)
- `htmlcov/` - Coverage HTML report (gitignored)

### Generated by Nox
- `.nox/` - Nox session virtualenvs (gitignored)

### Generated by Audit Pipeline
- `audit_artifacts/*.json` - Stage outputs (tracked)
- `reports/capability_matrix_*.md` - Reports (tracked)
- `audit_run_manifest.json` - Manifest (tracked)

### Generated by Documentation
- `artifacts/docs/api/` - API docs (gitignored)

## 🔄 File Update Triggers

| Trigger | Files to Update |
|---------|-----------------|
| New feature | Source code, tests, docs, CHANGELOG.md |
| Version bump | pyproject.toml, AGENTS.md, Traversal_Workflow.md |
| Config change | configs/*.yaml, tools/validate_configs.py |
| Dependency update | pyproject.toml, requirements*.txt |
| Audit run | audit_artifacts/, reports/, audit_run_manifest.json |
| Documentation | docs/, README.md |
| Status report | status_update_YYYY-MM-DD.md, README.md |

---

**Document Version**: 1.0  
**Last Updated**: Previous Cycle-12-09  
**Maintained By**: Codex Repository Team
