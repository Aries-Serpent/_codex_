# Deployment Guide - codex-ml v0.2.1

**Last Updated**: 2026-07-11  
**Version**: 2.0  
**Package**: codex-ml  
**Audience**: Maintainers, DevOps engineers, production operators, users deploying the Cognitive Brain package

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Release Checklist](#pre-release-checklist)
3. [Release Process](#release-process)
4. [Post-Release Verification](#post-release-verification)
5. [Profile Selection Guide](#profile-selection-guide)
6. [Monitoring & Observability](#monitoring--observability)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive deployment procedures for the Cognitive Brain package (`codex-ml`). The package is distributed in three profiles:

| Profile | Size | Use Case | Dependencies | Installation Time |
|---------|------|----------|--------------|-------------------|
| **core** | 8-15 MB | Lightweight, offline, edge devices | Minimal (stdlib + hydra, pydantic) | < 2 min |
| **runtime** | 20-35 MB | Production ML inference, APIs | torch, transformers, ray[serve], fastapi | 5-8 min |
| **full** | 100+ MB | Development, testing, experimentation | All (core + runtime + dev tools) | 10-15 min |

### Key Guarantees

- ✅ **Reproducible**: All dependencies locked in `uv.lock`
- ✅ **Offline-Capable**: Core profile works without network
- ✅ **Verified**: Hash-checked manifests and SBOMs included
- ✅ **Secure**: CVE governance and network policy enforcement
- ✅ **Tested**: Smoke tests for all profile combinations

---

## Pre-Release Checklist

**Timeline**: 1-2 days before release  
**Owner**: Release manager or maintainer with PyPI credentials

### ✅ Governance Gates (Auto-verified)

- [ ] **P0 Gate**: Lock/profile alignment verified
  - Confirm `.codex/PROFILE_DRIFT_AUDIT.json` exists
  - Confirm `.codex/PROFILE_DEPENDENCY_MANIFEST.md` exists
  - Command: `python scripts/ci/check_profile_drift.py`

- [ ] **P1 Gate**: Meta-tensor safety and SBOM verified
  - Confirm `sbom.json` or `.codex/sbom.json` exists
  - Confirm no meta-tensor initialization errors in tests
  - Command: `pytest tests/test_meta_tensor_safety.py`

- [ ] **P2 Gate**: Deployment automation ready
  - Confirm `.github/workflows/release-to-pypi.yml` exists
  - Confirm `.github/workflows/smoke-tests-deployment.yml` exists
  - Confirm `.github/workflows/pre-release-validation.yml` exists

### ✅ Code Quality Gates

- [ ] **All tests passing**: `pytest tests/ -x`
- [ ] **No type errors**: `mypy src/`
- [ ] **No security alerts**: `bandit -r src/`
- [ ] **No new CVEs**: `pip-audit`

### ✅ Release Preparation

- [ ] **Version bumped** in `pyproject.toml`
  ```toml
  [project]
  version = "0.1.0"  # Bump from previous
  ```

- [ ] **CHANGELOG.md updated** with release notes
  ```markdown
  ## [0.1.0] - 2026-07-07
  
  ### Added
  - Initial release of Cognitive Brain ecosystem
  - Three-profile packaging (core/runtime/full)
  - OODA loop framework
  
  ### Security
  - Fixed CVE-XXXX: [description]
  - Added network policy enforcement
  ```

- [ ] **Release notes prepared** (for GitHub release)
  - Create file: `release-notes-0.1.0.md`
  - Include: Features, security fixes, installation instructions, known issues

- [ ] **git tag prepared** (not yet pushed)
  ```bash
  # Draft the tag locally (don't push yet)
  git tag -a v0.1.0 -m "Release v0.1.0 - Cognitive Brain"
  # Don't push yet - pre-release validation will trigger this
  ```

### ✅ Infrastructure Ready

- [ ] **PyPI credentials configured** in GitHub Secrets
  - Secret: `PYPI_API_TOKEN`
  - Test: `twine check` on a test build
  
- [ ] **Build environment validated**
  ```bash
  python -m pip install build
  python -m build --wheel
  # Should produce 3 wheels (core, runtime, full compatible)
  ```

- [ ] **Offline install tested** (on all three profiles)
  ```bash
  # Simulate offline environment
  scripts/prepare_offline_env.sh core
  scripts/deploy/bootstrap_offline.py wheelhouse_core/
  ```

### ✅ Documentation Ready

- [ ] **Deployment guide reviewed** (this document)
- [ ] **Rollback procedures documented** (see below)
- [ ] **Known issues captured** in release notes
- [ ] **Migration guide prepared** (if breaking changes)

---

## Release Process

**Timeline**: ~15-20 minutes  
**Owner**: Release manager  
**Prerequisites**: All pre-release checklist items complete

### Step 1: Create Pre-Release Validation PR (5 min)

1. Create branch: `release/v0.1.0-prepare`
2. Commit changes:
   ```bash
   git checkout -b release/v0.1.0-prepare
   
   # Bump version
   sed -i 's/version = "[^"]*"/version = "0.1.0"/' pyproject.toml
   
   # Update changelog (already done, but verify)
   # Edit CHANGELOG.md
   
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: Prepare v0.1.0 release"
   git push origin release/v0.1.0-prepare
   ```

3. Open PR: `release/v0.1.0-prepare` → `main`
4. Wait for **pre-release-validation.yml** to verify:
   - Version bumped ✅
   - CHANGELOG updated ✅
   - All gates passing ✅

5. Get code review and merge

### Step 2: Create and Push Release Tag (5 min)

Once PR merged to main:

```bash
# Fetch latest main
git fetch origin
git checkout origin/main

# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0 - Cognitive Brain v0.1.0-final"

# Push tag - this triggers release-to-pypi.yml
git push origin v0.1.0
```

### Step 3: Monitor Release Workflow (10 min)

In GitHub Actions, monitor: **Release to PyPI** workflow

Watch for these steps:

1. **Pre-release checks** (1-2 min)
   - Gate verification: P0, P1, P2
   - Version validation
   - Expected output: ✅ All gates verified

2. **Build wheels** (3-5 min)
   - Multi-platform build
   - Expected output: 3 wheels × 3 platforms = 9 artifacts

3. **Generate manifest** (1-2 min)
   - Hash calculation
   - Expected output: `RELEASE_MANIFEST.json` with SHA256 hashes

4. **Generate SBOM** (1-2 min)
   - Software bill of materials
   - Expected output: SBOM files for each profile

5. **Verify manifest** (1 min)
   - Hash verification
   - Expected output: ✅ Manifest verified

6. **Publish to PyPI** (2-3 min)
   - Upload wheels
   - Expected output: "Successfully uploaded codex-ml-0.1.0-py3-none-any.whl"

7. **Create GitHub release** (1 min)
   - Release notes
   - Asset upload
   - Expected output: GitHub release created with wheels, manifest, SBOM

**Failure scenarios**:

- ❌ **Pre-release checks fail**: Gates not met
  - Action: Resolve missing gates, update version, push new tag
  
- ❌ **Build fails**: Platform-specific issue
  - Action: Review build logs, fix issue, delete tag, push new tag
  
- ❌ **PyPI upload fails**: Credentials or network issue
  - Action: Verify `PYPI_API_TOKEN` secret, retry release workflow
  
- ❌ **Smoke tests fail**: Package doesn't install correctly
  - Action: See [Rollback Procedures](#rollback-procedures)

---

## Post-Release Verification

**Timeline**: 5-10 minutes after release  
**Owner**: Release manager

### Immediate Verification (< 1 min)

```bash
# Verify package on PyPI
curl -s https://pypi.org/pypi/codex-ml/0.1.0/json | jq .info.version

# Should output: "0.1.0"
```

### Installation Test (2-3 min per profile)

Test on clean machine or in docker:

```bash
# Test core profile
python -m venv test-core
source test-core/bin/activate
pip install codex-ml[core]==0.1.0
python -c "from cognitive_brain.ooda import OODALoop; print('✅ Core profile works')"

# Test runtime profile
python -m venv test-runtime
source test-runtime/bin/activate
pip install codex-ml[runtime]==0.1.0
python -c "import torch; print('✅ Runtime profile works')"

# Test full profile
python -m venv test-full
source test-full/bin/activate
pip install codex-ml[full]==0.1.0
python -c "import pytest; print('✅ Full profile works')"
```

### Smoke Test Verification (< 2 min)

Check GitHub Actions: **Smoke Tests - Deployment Verification** workflow

All 12 test combinations should pass:
- ✅ Python 3.12, core, with-ml
- ✅ Python 3.12, core, without-ml
- ✅ Python 3.12, runtime, with-ml
- ✅ Python 3.12, runtime, without-ml
- ✅ Python 3.12, full, with-ml
- ✅ Python 3.12, full, without-ml
- ✅ Python 3.13, [same 6 combinations]

### Monitoring Setup (5-10 min)

1. **Enable download statistics**:
   - Visit: https://pypi.org/project/codex-ml/#history
   - Monitor daily downloads over next 7 days

2. **Setup alerts**:
   ```bash
   # Log to monitoring dashboard
   scripts/deploy/log_release_metrics.py \
     --version 0.1.0 \
     --deployment-time 15m \
     --smoke-test-status all-passed
   ```

3. **Create monitoring dashboard**:
   - Location: `.codex/RELEASE_METRICS_v0.1.0.json`
   - Contents: Build duration, sizes, test results, download stats

---

## Profile Selection Guide

### Profile: Core

**When to use**:
- ✅ Lightweight deployments (< 50 MB total)
- ✅ Offline environments or air-gapped networks
- ✅ Edge devices with limited resources
- ✅ CI/CD pipelines that only need OODA loop
- ✅ Containers where size matters

**Installation**:
```bash
pip install codex-ml[core]==0.1.0
```

**What's included**:
- Essential OODA loop APIs
- Configuration management (hydra, omegaconf)
- Data validation (pydantic)
- CLI tools
- Offline-first design

**What's NOT included**:
- ML libraries (torch, transformers)
- ML inference capabilities
- Development tools (pytest, mypy)
- Optional extras

**Performance**:
- Installation: < 2 minutes
- Startup: < 500 ms
- Memory footprint: < 100 MB
- Network calls: None (if used correctly)

**Verification**:
```bash
python -c "from cognitive_brain.ooda import OODALoop; ooda = OODALoop(); print('✅ Core works')"
```

---

### Profile: Runtime

**When to use**:
- ✅ Production ML inference services
- ✅ API deployments (FastAPI, Flask)
- ✅ Pattern recognition in production
- ✅ Ray serve workers
- ✅ AWS Lambda / GCP Cloud Functions

**Installation**:
```bash
pip install codex-ml[runtime]==0.1.0
```

**What's included**:
- Core profile + all of:
- PyTorch (torch)
- Transformers (HuggingFace)
- Datasets library
- Ray[serve] for distributed inference
- FastAPI for REST APIs
- Network-enabled APIs

**What's NOT included**:
- Development tools (pytest, mypy, notebooks)
- Experimental features
- Debug utilities

**Performance**:
- Installation: 5-8 minutes
- Startup: 2-5 seconds (first load slower due to model loading)
- Memory footprint: 2-4 GB (with loaded models)
- Network calls: Required (downloads models, connects to inference servers)

**Verification**:
```bash
python -c "import torch; from cognitive_brain.runtime import MLInference; print('✅ Runtime works')"
```

---

### Profile: Full

**When to use**:
- ✅ Local development
- ✅ Testing and QA
- ✅ Building custom extensions
- ✅ Contributing to the project
- ✅ Research and experimentation

**Installation**:
```bash
pip install codex-ml[full]==0.1.0
```

**What's included**:
- Runtime profile + all of:
- pytest (test runner)
- mypy (type checking)
- black (code formatter)
- ruff (linter)
- sphinx (documentation)
- jupyter (notebooks)
- All development dependencies

**What's NOT included**:
- CI/CD tools (typically installed separately)
- Documentation build dependencies (optional)

**Performance**:
- Installation: 10-15 minutes
- Startup: 5-10 seconds
- Memory footprint: 4-6 GB
- Network calls: Yes (model downloads, online docs)

**Verification**:
```bash
python -c "import pytest; from cognitive_brain.full import DevEnvironment; print('✅ Full works')"
```

---

## Phase Objects (Planned Execution Tracks)

### What Are Phase Objects?

**Phase Objects** are planned execution tracks included in the `codex-ml` package. They define multi-track deployment plans for complex operations:

- **Track A-G**: Sequential execution phases (A → B → C → D → E → F → G)
- **Tasks PR**: Comprehensive task roadmap (99.6 KB, 3,193 lines)
- **Batch Segments**: Segmented data batches for parallel processing

### Accessing Phase Objects

Phase objects are automatically included in all installation profiles (`core`, `runtime`, `full`) and can be accessed via the `codex_plans` module:

```python
# List all available plans
from codex_plans import list_plan_documents

plans = list_plan_documents()
for plan in plans:
    print(f"  📄 {plan.name} ({plan.stat().st_size} bytes)")
```

Expected output:
```
📄 Tasks_PR_2459.md (99647 bytes)
📄 track_A.md (1587 bytes)
📄 track_B.md (1462 bytes)
📄 track_C.md (1979 bytes)
📄 track_D.md (1695 bytes)
📄 track_E.md (2494 bytes)
📄 track_F.md (2902 bytes)
📄 track_G.md (3673 bytes)
```

### Reading a Phase Plan

```python
from pathlib import Path
from codex_plans import list_plan_documents

plans = list_plan_documents()
with open(plans[0]) as f:
    content = f.read()
    print(f"Plan: {plans[0].name}")
    print(f"Lines: {len(content.splitlines())}")
    print("\n" + content[:500] + "...")
```

### Use Cases

**Development**:
- Reference implementation roadmaps
- Understand deployment phasing strategy
- Track multi-phase execution plans

**CI/CD Integration**:
- Programmatically read phase definitions
- Trigger phase-based workflows
- Track execution state across phases

**Documentation**:
- Generate deployment timelines
- Create phase execution reports
- Publish guidance for multi-phase operations

---

## Monitoring & Observability

### Release Metrics Collection

After release, the workflow automatically creates `.codex/RELEASE_METRICS_v0.1.0.json`:

```json
{
  "version": "0.1.0",
  "released_at": "2026-07-07T15:30:00Z",
  "metrics": {
    "build_duration_seconds": 420,
    "wheel_sizes": {
      "core": 8500000,
      "runtime": 25000000,
      "full": 105000000
    },
    "smoke_tests": {
      "total": 12,
      "passed": 12,
      "failed": 0,
      "duration_seconds": 180
    },
    "pypi_upload_duration": 45
  },
  "artifacts": {
    "wheels": 9,
    "manifest": 1,
    "sbom": 3
  }
}
```

### Download Statistics

Monitor PyPI downloads:

```bash
# Get last 7 days of downloads
curl -s "https://pypistats.org/api/packages/codex-ml/recent?period=week" | jq .data
```

Expected pattern:
- Day 1-2: Slow (initial adopters)
- Day 3-7: Growth (if announced)
- Week 2+: Steady state

### Key Metrics to Watch

| Metric | Expected | Alert If |
|--------|----------|----------|
| Installation success rate | > 99% | < 98% |
| Core profile installs | 30-40% | < 20% |
| Runtime profile installs | 40-50% | < 30% |
| Full profile installs | 10-20% | > 25% |
| Average install time | 3-5 min | > 10 min |
| Issues reported | 0-2 | > 5 in first week |

### Monitoring Commands

```bash
# Check installation stats
pip show codex-ml | grep Version

# Verify all profiles available
pip index versions codex-ml

# Check for yanked versions
curl -s https://pypi.org/pypi/codex-ml/json | jq .releases
```

---

## Rollback Procedures

**See**: [Rollback Checklist](ROLLBACK_CHECKLIST.md) for detailed step-by-step procedures

### Quick Rollback (< 5 minutes)

If critical issues found in first 2 hours:

```bash
# Quick rollback script
python scripts/deploy/rollback_release.py \
  --version v0.1.0 \
  --reason "Critical bug in runtime profile" \
  --restore-version v0.0.9

# This:
# 1. Marks v0.1.0 as yanked on PyPI
# 2. Deletes the git tag locally and remotely
# 3. Restores v0.0.9 as latest on PyPI
# 4. Creates GitHub release noting rollback
# 5. Sends notifications to maintainers
```

### When to Rollback

- ❌ Core profile doesn't import (immediate)
- ❌ OODA loop crashes on initialization (immediate)
- ❌ Network policy violated in core (immediate)
- ❌ Smoke tests fail for > 1 profile (within 30 min)
- ❌ Critical security vulnerability found (within 24 hours)
- ⚠️ Performance regression > 50% (discuss first)
- ⚠️ Optional dependency issues (non-blocking)

---

## Troubleshooting

### Issue: `pip install codex-ml[core]` fails with network error

**Symptom**: Error like "Could not fetch URL" or "No matching distribution"

**Cause**: PyPI network issue or package not yet indexed

**Solution**:
```bash
# Wait 5 minutes and retry
sleep 300
pip install codex-ml[core]==0.1.0

# Or install from GitHub release directly
pip install https://github.com/Aries-Serpent/_codex_/releases/download/v0.1.0/codex_ml-0.1.0-py3-none-any.whl
```

### Issue: `ImportError: No module named 'cognitive_brain'`

**Symptom**: After install, imports fail

**Cause**: Package not properly installed or wrong profile

**Solution**:
```bash
# Verify installation
pip show codex-ml

# Verify location
python -c "import cognitive_brain; print(cognitive_brain.__file__)"

# Try reinstall
pip uninstall -y codex-ml
pip install codex-ml[core]==0.1.0

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Issue: CLI commands (`codex-ml`, `codex-ml-cli`, `codex-cli`) fail with `ModuleNotFoundError`

**Symptom**: 
```
ModuleNotFoundError: No module named 'aries_serpent_core'
```

**Cause**: The CLI module requires `aries_serpent_core` which wasn't included in older package builds. This was fixed in v0.2.1+.

**Solution**:
```bash
# Upgrade to v0.2.1 or later
pip install --upgrade codex-ml>=0.2.1

# Verify CLI works
codex-ml --help

# Or use the working smoke CLI
codex-smoke --help
```

**If upgrade is not possible**:
```bash
# Install from full profile (includes all dependencies)
pip install codex-ml[full]>=0.2.1
```

### Issue: Runtime profile is 2GB, too large for production

**Symptom**: Storage space issues, slow deployments

**Cause**: Full ML dependencies including models

**Solution**:
```bash
# Use core profile instead
pip uninstall codex-ml
pip install codex-ml[core]==0.1.0

# If ML needed, use Docker with layer caching
# or AWS SageMaker (pre-cached)

# Or use custom lightweight profile (future)
```

### Issue: Offline install fails: "No matching version found"

**Symptom**: Error with wheelhouse, missing transitive deps

**Cause**: Lockfile may be incomplete for offline use

**Solution**:
```bash
# Use the provided offline bootstrap script
scripts/deploy/bootstrap_offline.py \
  --wheelhouse wheelhouse_core/ \
  --profile core \
  --python-version 3.12
```

### Issue: Network calls detected in core profile

**Symptom**: Code makes HTTP requests despite core profile

**Cause**: Code not using `AllowNetworkCalls` context manager

**Solution**:
```bash
# Enable network call detection
export DETECT_NETWORK_CALLS=1

# Run code that imports cognitive_brain
python your_script.py

# Check logs for network call warnings
```

---

## FAQ

**Q: How do I know which profile to use?**

A: Start with core if you only need OODA loop. Upgrade to runtime if you need ML. Use full for development.

**Q: Can I install multiple profiles together?**

A: Yes, they're compatible:
```bash
pip install codex-ml[core,runtime]==0.1.0
```

**Q: What if I accidentally use full in production?**

A: It will work, but wastes 100+ MB of disk space and install time. Consider optimization pass.

**Q: Can I downgrade from runtime to core?**

A: Yes, downgrade is safe:
```bash
pip install --force-reinstall codex-ml[core]==0.1.0
```

**Q: How long is v0.1.0 supported?**

A: Until v0.2.0 is released (typically 6-12 months). See [Support Policy](../../SECURITY.md).

---

## Contacts & Escalation

- **Release Manager**: @mbaetiong
- **DevOps**: @[devops-team]
- **Security Issues**: security@[organization]
- **Incident Response**: [incident-channel]

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-07  
**Next Review**: 2026-08-07
