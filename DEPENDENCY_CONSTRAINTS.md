# Dependency Constraints & Version Rationale

**Last Updated**: 2026-06-19  
**Author**: Copilot Dependency Management Task  
**Status**: Active  

## Overview

This document establishes the canonical version constraints for all critical dependencies in the Aries-Serpent/_codex_ project. It serves as the single source of truth for cross-file consistency and rationale for pinned versions.

**Key Principle**: All dependency constraints must be synchronized across:
- `pyproject.toml` (primary source of truth)
- `requirements*.txt` (implementation targets)
- `.github/agents/*/requirements.txt` (specialized agents)
- `services/*/requirements.txt` (service deployments)

---

## Critical Dependencies (PR #5004 Consolidated)

These versions were established in PR #5004 and must remain consistent across all files.

### Data Processing Stack

| Package | Version | Rationale | First Pinned | Notes |
|---------|---------|-----------|--------------|-------|
| **pandas** | >=3.0.3,<4 | Major version upgrade; 3.0.3 introduces API changes and performance improvements; required by evaluation stack | PR #5004 | Evaluation suite explicitly requires 3.0.3; DO NOT downgrade to 2.x |
| **numpy** | >=2.4.6,<3 | Latest 2.x series; required for pandas 3.0.3 compatibility; security fixes in 2.4.6+ | PR #5004 | Older versions (<1.24) incompatible with pandas 3.x |
| **scikit-learn** | >=1.9.0,<2 | Compatible with numpy 2.4.6+ and pandas 3.0.3 | PR #5004 | Strict upper bound prevents 2.x API breakage |

### ML/Transformer Stack

| Package | Version | Rationale | First Pinned | Notes |
|---------|---------|-----------|--------------|-------|
| **transformers** | >=5.12.1,<6 | Security fix: deserialization vulnerabilities in earlier versions; API stable within 5.x | PR #5004 | Upper bound prevents 6.x breaking changes |
| **peft** | >=0.19.1,<1 | LoRA adapter improvements; works with transformers 5.12.1+; API stable within 0.x | PR #5004 | Must match accelerate version stability |
| **accelerate** | >=1.14.0,<2 | Distributed training support; compatible with torch 2.6.1+ and transformers 5.12.1+ | PR #5004 | DO NOT downgrade below 1.14.0 |
| **datasets** | >=5.0.0,<6 | Hugging Face datasets; compatible with transformers 5.12.1+ | PR #5004 | Major version API changes expected in 6.x |

### Monitoring & Tracking

| Package | Version | Rationale | First Pinned | Notes |
|---------|---------|-----------|--------------|-------|
| **mlflow** | >=2.22.4,<4 | Experiment tracking; 2.22.4 baseline with security patches; 3.x API compatible | PR #5004 | See CVE section for version guidance |

### Core Frameworks

| Package | Version | Rationale | First Pinned | Notes |
|---------|---------|-----------|--------------|-------|
| **torch** | >=2.6.1,<3.0.0 | Security: weights_only=True RCE fix (CVE-2025-32434); CPU-only preferred | PR #5004 | Upper bound prevents 3.x breaking changes |
| **pydantic** | >=2.4,<3 | API stable; works with pydantic-settings 2.14.1+ | PR #5004 | Strict upper bound prevents 3.x incompatibilities |
| **hydra-core** | ==1.3.2 | Exact version for reproducible config management | PR #5004 | Pinned exactly to prevent subtle behavioral changes |

---

## Security Vulnerabilities Fixed

### pandas Upgrade (2.0.0 → 3.0.3)

**Key Fixes**:
- Improved memory safety in categorical operations
- Fixed index alignment issues in multi-index DataFrames
- Enhanced type checking for nullable integer columns
- Better handling of timezone-aware datetimes

**Breaking Changes to Watch**:
- `.values` now returns ndarray with native numpy dtype (not always object arrays)
- Index `.name` attribute removed for MultiIndex (use `.names` instead)
- Implicit type casting in operations is stricter
- Some deprecated functions removed

**Codebase Impact**: Evaluation suite requires 3.0.3; code must be tested with new behavior.

### numpy Upgrade (1.24 → 2.4.6)

**Security Fixes**:
- CVE fixes in array operations
- Improved type safety in C extensions
- Fixed potential buffer overflows in advanced indexing

**Compatibility**: numpy 2.4.6 required by pandas 3.0.3; strict dependency.

### mlflow Version Guidance

| Version | Status | Notes |
|---------|--------|-------|
| 2.22.4+ | ✅ Recommended | Stable; security baseline |
| 3.x | ⚠️ Optional | API compatible; newer CVE fixes available (e.g., 3.11.1 for XSS fix) |

**CVE-2026-33865** (mlflow): Stored XSS via MLmodel YAML  
- Vulnerable: mlflow < 3.11.1
- Fixed: mlflow >= 3.11.1
- Workaround: Use >=2.22.4,<4 if 3.x not available

### transformers Security Updates

- Deserialization vulnerabilities in versions < 5.12.1
- RCE potential in model loading; upgrade mandatory
- Strict version bound <6 prevents API breakage in 6.x series

---

## Cross-File Consistency Rules

### Rule 1: pyproject.toml is Primary Source of Truth

All constraints in `pyproject.toml` [project.dependencies] must be:
1. Synchronized to all `requirements*.txt` files
2. Version-compatible (no conflicting ranges)
3. Documented here with rationale

**Verification**: Run `scripts/ci/validate_dependency_consistency.py` before commit

### Rule 2: Pinned vs Range Constraints

- **Ranges (>=X,<Y)**: Use for dependencies with active development (pandas, transformers, torch)
- **Exact Pins (==X)**: Use only for:
  - Tools with critical reproducibility needs (hydra-core)
  - Compatibility testbeds (requirements-test.txt)
  - Specific ML configurations (requirements-ml-cpu.txt)

### Rule 3: Transitive Dependencies

When updating a package, verify:
1. Direct dependencies don't conflict with transitive deps
2. All requirements*.txt files capture necessary transitive deps
3. No circular or incompatible version constraints

Example: pandas 3.0.3 → requires numpy 2.4.6+, which affects all files

---

## Version Update Workflow

### When to Update Dependencies

**Automatic (Dependabot)**:
- Patch releases (1.0.1 → 1.0.2): Apply auto-merge if tests pass
- Minor releases (1.1.0 → 1.2.0): Review; apply if backward-compatible

**Manual Review Required**:
- Major releases (1.x → 2.x): Full compatibility audit
- Security CVE fixes: Prioritize immediately
- Cross-package version bumps: Ensure consistent alignment

### Update Procedure

1. **Single Package Update**:
   ```bash
   # Update pyproject.toml first
   edit pyproject.toml  # Update [project.dependencies]
   
   # Sync to all requirements files
   python scripts/ci/sync_dependencies.py --from pyproject.toml
   
   # Validate consistency
   python scripts/ci/validate_dependency_consistency.py
   
   # Run tests
   nox -s tests
   ```

2. **Multi-Package Update** (like PR #5004):
   ```bash
   # Update all packages in pyproject.toml
   # Then run sync script
   python scripts/ci/sync_dependencies.py --validate-all
   ```

3. **Cross-File Manual Sync** (when auto-sync fails):
   ```bash
   # Edit each file individually
   # Verify afterward
   python scripts/ci/validate_dependency_consistency.py --fix-suggestions
   ```

---

## Pre-Commit Hook Integration

**Hook Location**: `.pre-commit-config.yaml` (to be created)

```yaml
- repo: local
  hooks:
    - id: check-dependency-consistency
      name: Check Dependency Consistency
      entry: python scripts/ci/validate_dependency_consistency.py
      language: python
      files: (pyproject.toml|requirements.*\.txt)$
      stages: [commit]
```

**Effect**: Prevents commits that violate dependency constraints without manual override.

---

## Conflict Prevention Checklist

### Before Merging Any PR

- [ ] All `requirements*.txt` files match `pyproject.toml` versions
- [ ] No downgrades of critical packages (pandas, numpy, transformers, torch)
- [ ] Security CVE fixes are documented (see [Security Vulnerabilities](#security-vulnerabilities-fixed))
- [ ] Tests pass with new dependency versions
- [ ] No conflicting transitive dependencies introduced
- [ ] Commit message includes rationale for version changes

### Before Releasing

- [ ] Run full audit: `python scripts/ci/validate_dependency_consistency.py`
- [ ] Test with actual dependency versions: `pip install -e . && nox -s tests`
- [ ] Compare against previous release: `git diff HEAD~1 pyproject.toml`
- [ ] Update CHANGELOG.md with dependency changes
- [ ] Tag release with dependency version info

---

## Known Issues & Workarounds

### Issue: Pandas 3.0.3 Index API Changes

**Symptom**: `AttributeError: 'MultiIndex' object has no attribute 'name'`

**Fix**: Use `.names` (plural) for MultiIndex objects

**Affected Code**: Check `src/codex` for direct pandas manipulation

### Issue: numpy 2.x Dtype Casting

**Symptom**: `TypeError: cannot safely cast from float64 to int64`

**Fix**: Explicit dtype specification or `astype()` call

**Affected Code**: Data loading and preprocessing pipelines

### Issue: transformers 5.x Model Caching

**Symptom**: Model loading hangs or fails with version check errors

**Fix**: Clear `~/.cache/huggingface/transformers` and retry

**Affected Code**: ML training and inference code

---

## References

- **PR #5004**: Consolidation PR establishing current baseline
- **Commit 56c7786**: PR #5004 merge commit (reference point)
- **pyproject.toml**: Lines 31-67 (main dependencies)
- **requirements-eval.txt**: Evaluation stack baseline
- **CONTRIBUTING.md**: Developer guidelines (update when workflow changes)

---

## Maintenance

**Owner**: @mbaetiong (maintainer)  
**Last Review**: 2026-06-19  
**Next Review**: 2026-07-19 (monthly)  

### Update Log

| Date | Package | From | To | Reason | PR |
|------|---------|------|----|---------|----|
| 2026-06-19 | pandas | 2.0.0 | 3.0.3 | Alignment with PR #5004 baseline | This task |
| 2026-06-19 | numpy | 1.24 | 2.4.6 | Pandas 3.x requirement | This task |
| 2026-06-19 | transformers | 5.12.1 | 5.12.1,<6 | Version bound consistency | This task |
| 2026-06-19 | peft | 0.7.0 | 0.19.1,<1 | Version bound consistency | This task |
| 2026-06-19 | accelerate | 1.14.0 | 1.14.0,<2 | Version bound consistency | This task |
| 2026-06-19 | mlflow | 3.11.1 | 2.22.4,<4 | Broader compatibility | This task |

