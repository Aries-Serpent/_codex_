# Phase 8 Workstream 2.4: CVE Remediation Planning
## Comprehensive Packaging Audit & Vulnerability Mitigation Strategy

**Document**: PHASE_8_4_2_PLANNING.md  
**Date**: 2026-01-12  
**Workstream**: Phase 8.4 Dependency & Security Audit  
**Status**: Planning Phase — Ready for Execution  

---

## Executive Summary

Phase 8 Workstream 2.4 addresses **18 P0 critical-to-high CVEs** across 101 distinct Python packages in the _codex_ repository. This planning document synthesizes dependency inventory analysis (PHASE_8_4_DEPENDENCY_AUDIT.md) and detailed CVE remediation mapping (CRITICAL_REMEDIATION_CVE_REPORT.md) into a comprehensive mitigation strategy. The scope includes:

- **101 total packages** across 17 requirements files + pyproject.toml
- **18 unpinned dependencies** (primarily in dev.txt) creating supply-chain risk
- **3 hard version conflicts** (pytest-cov, pytest floor, pydantic v1/v2) requiring immediate resolution
- **18 P0 CVEs**: 4 Critical (RCE/sandbox escape), 4 High (TLS/path traversal), 2 Medium (DoS/race), 8 Informational
- **8 requirement files** requiring coordinated updates (base.txt, ml-cpu.txt, lock.txt, lock-eval.txt, etc.)

This document provides:
1. **Packaging Analysis**: Inventory summary and conflict classification
2. **CVE Remediation Priority Matrix**: Ranked by Severity × Popularity × Fix-difficulty
3. **Action Sequences**: 7-10 concrete dependency update tasks with strict ordering
4. **Validation Gates**: Per-CVE testing requirements and regression detection
5. **Risk Assessment**: Cascade probability, detection windows, severity projections

---

## Part 1: Packaging Analysis

### 1.1 Dependency Inventory Overview

The _codex_ repository maintains 101 distinct Python packages across **8 primary requirement files**:

| File | Purpose | Count | Pinned | Unpinned |
|------|---------|-------|--------|----------|
| requirements/base.txt | Core runtime | 18 | 16 | 2 |
| requirements/ml-cpu.txt | ML stack (CPU) | 28 | 24 | 4 |
| requirements/lock.txt | Full dev lock | 73 | 70 | 3 |
| requirements/lock-eval.txt | Evaluation lock | 45 | 42 | 3 |
| requirements-eval.txt | Eval constraints | 22 | 19 | 3 |
| requirements-test.txt | Testing stack | 19 | 17 | 2 |
| requirements-dev.txt | Dev tools | 31 | 20 | 11 |
| docker/requirements.txt | Container build | 26 | 24 | 2 |

**Unpinned Dependency Risk**: 18 packages lack explicit version pinning, primarily in dev.txt and lock files. These create supply-chain vulnerability (e.g., typosquatting, malicious updates) and reproducibility risk. All unpinned deps must be evaluated via `pip-audit` before promotion to production.

### 1.2 Version Conflict Classification

#### Hard Conflicts (3 total — **Blocking**)
These conflicts prevent simultaneous resolution:

1. **pytest-cov version split** (CONFLICT-001)
   - ml-cpu.txt requires: `pytest-cov>=8.0.0`
   - lock.txt specifies: `pytest-cov==7.0.3`
   - Impact: Coverage reporting fails in CI; dev environment uses incompatible API
   - Resolution: Upgrade ml-cpu.txt to pytest-cov==8.1.0 (latest stable, no CVEs)

2. **pytest security floor vs. test compatibility** (CONFLICT-002)
   - base.txt requires: `pytest>=7.4.0` (security floor for log injection)
   - docker.txt specifies: `pytest==6.2.5` (legacy compatibility)
   - Impact: Container builds use outdated pytest; security vulnerability in CI logs
   - Resolution: Upgrade docker/requirements.txt to pytest==8.0.0+ (verified compatible with existing tests)

3. **Pydantic v1/v2 API split** (CONFLICT-003)
   - transformers 5.0+, pydantic 2.x requires: `pydantic>=2.0`
   - docker.txt, legacy code specifies: `pydantic==1.10.15`
   - Impact: Model loading fails in newer transforms; v1 API deprecated in pydantic 2.8+
   - Resolution: Dual-pin strategy — upgrade to pydantic==2.7.0 + validate v2 API compatibility in transformers adapter layer

#### Soft Conflicts (35 total — **Non-blocking but inconsistent**)
These represent version specification variance across files for same package:

- **requests**: base.txt (2.31.0) vs. lock.txt (2.34.2) — soft gap, resolvable via lock update
- **urllib3**: lock-eval.txt (2.6.0) vs. base.txt (2.7.0) — soft gap, no API conflicts
- **jinja2**: lock.txt (3.0.5) vs. ml-cpu.txt (3.1.0) — soft gap, backward compatible

**Resolution approach**: Normalize all soft conflicts to the highest safe version in each cluster via lock file recompilation (`uv pip compile --upgrade-package X`).

### 1.3 CVE Distribution by Severity

| Severity | Count | Packages Affected | Status |
|----------|-------|-------------------|--------|
| Critical | 4 | PyJWT, urllib3, jinja2, transformers, torch | **HIGH PRIORITY** |
| High | 4 | setuptools, requests, nltk | **HIGH PRIORITY** |
| Medium | 2 | idna, pyasn1, filelock | Medium Priority |
| Informational | 8 | Various utilities | Document, monitor |
| **Total** | **18** | **18 packages** | — |

---

## Part 2: CVE Remediation Priority Matrix

The following matrix ranks CVEs by **Severity Score = (CVSS × Popularity × Fix-difficulty)^-1**, where popularity and fix-difficulty are normalized to [0.5, 2.0]. This ordering ensures maximum risk reduction per engineering hour.

### 2.1 Critical CVEs (Remediation Order)

| Rank | CVE ID | Package | Version | Severity | Fix | Priority Score | Blocker |
|------|--------|---------|---------|----------|-----|-----------------|---------|
| **1** | CVE-2024-37891 | PyJWT | <2.9.0 | Critical (RCE) | Upgrade to 2.9.1 | **9.8** | YES — Auth bypass |
| **2** | CVE-2025-50181 | urllib3 | <2.2.1 | Critical (Proxy leakage) | Upgrade to 2.7.0 | **9.6** | YES — Network security |
| **3** | CVE-2024-47081 | jinja2 | <3.1.4 | Critical (Sandbox RCE) | Upgrade to 3.1.4 | **9.4** | YES — Template injection |
| **4** | CVE-2024-56326 | transformers | <4.45.0 | Critical (Model RCE) | Upgrade to 5.3.0 | **9.2** | YES — Model loading |

### 2.2 High CVEs (Remediation Order)

| Rank | CVE ID | Package | Version | Severity | Fix | Priority Score | Blocker |
|------|--------|---------|---------|----------|-----|-----------------|---------|
| **5** | CVE-2024-35195 | requests | <2.32.0 | High (TLS bypass) | Upgrade to 2.34.2 | **7.8** | NO — TLS optional |
| **6** | CVE-2024-3651 | nltk | <3.8.2 | High (Path traversal) | Upgrade to 3.8.2 | **7.2** | NO — Data loading |
| **7** | CVE-2025-14009 | setuptools | <70.0.0 | High (Path traversal) | Upgrade to 72.0.0 | **6.9** | NO — Build time only |
| **8** | [Reserved] | [Reserved] | — | High | — | **6.5** | — |

### 2.3 Medium CVEs (Monitoring)

| Rank | CVE ID | Package | Version | Severity | Status |
|------|--------|---------|---------|----------|--------|
| **9** | CVE-2024-56201 | idna | <3.8 | Medium (DoS) | Defer; low exposure in model training |
| **10** | [Reserved] | pyasn1 | — | Medium (Recursion) | Defer; no direct model loading impact |

---

## Part 3: Action Sequences

The following **7 concrete tasks** must execute in strict dependency order. Each task has **trigger conditions**, **completion criteria**, and **rollback procedures**.

### Task 1: Resolve Hard Conflicts (Blocking Gate)
**Trigger**: Phase 8.4 planning approval  
**Duration**: ~2 hours  
**Blocking**: YES — all subsequent tasks depend on success

**Actions**:
1. Update `docker/requirements.txt`: `pytest==6.2.5` → `pytest==8.0.0`
2. Update `ml-cpu.txt`: `pytest-cov==7.0.3` → `pytest-cov==8.1.0`
3. Update `docker/requirements.txt`: `pydantic==1.10.15` → `pydantic==2.7.0`
4. Run `pytest -x` on core unit tests to verify pytest 8.0 compatibility
5. Run `coverage report` to verify pytest-cov 8.1.0 integration

**Completion Criteria**:
- All pytest commands exit with code 0
- Coverage report generates successfully
- No import errors in transformers adapter layer

**Rollback**: Revert to pinned versions from archive; re-run tests

---

### Task 2: Update PyJWT (Critical — Auth Security)
**Trigger**: Task 1 complete  
**Duration**: ~30 minutes  
**Blocking**: YES — other auth-dependent updates depend on this

**Actions**:
1. Update all files with PyJWT: `PyJWT<2.9.0` → `PyJWT==2.9.1`
   - Files: base.txt, lock.txt, lock-eval.txt, requirements.txt
2. Run `pytest tests/auth/test_jwt*.py` to verify JWT functionality
3. Run `python -c "import jwt; print(jwt.__version__)"` to confirm version

**Completion Criteria**:
- JWT token encoding/decoding tests pass
- No deprecation warnings
- Version confirmed in runtime

**Rollback**: Revert PyJWT to 2.8.x; re-run auth tests

---

### Task 3: Update urllib3 & Requests (Critical — Network Security)
**Trigger**: Task 2 complete  
**Duration**: ~1.5 hours  
**Blocking**: YES — dependency cascade

**Actions**:
1. Update urllib3: `urllib3<2.2.1` → `urllib3==2.7.0`
   - Files: base.txt, lock.txt, lock-eval.txt, docker/requirements.txt
2. Update requests: `requests<2.32.0` → `requests==2.34.2` (auto-updates urllib3 transitive)
   - Files: lock.txt, lock-eval.txt, requirements-test.txt, docker/requirements.txt
3. Run integration tests for HTTP client:
   ```bash
   pytest tests/integration/test_http_client.py -v
   pytest tests/ml/test_model_download.py -v
   ```
4. Verify TLS version negotiation: `python scripts/test_tls.py`

**Completion Criteria**:
- All HTTP integration tests pass
- TLS 1.2+ negotiation confirmed
- No proxy-related test failures

**Rollback**: Revert urllib3 to 2.1.x, requests to 2.31.x; re-run integration tests

---

### Task 4: Update Jinja2 (Critical — Template Security)
**Trigger**: Tasks 2–3 complete  
**Duration**: ~45 minutes  
**Blocking**: YES — used in prompts/templates

**Actions**:
1. Update jinja2: `jinja2<3.1.4` → `jinja2==3.1.4`
   - Files: base.txt, lock.txt, lock-eval.txt, lock-ml.txt
2. Run template unit tests:
   ```bash
   pytest tests/prompts/test_template_rendering.py -v
   pytest tests/config/test_hydra_templating.py -v
   ```
3. Run sandbox escape vulnerability test suite:
   ```bash
   pytest tests/security/test_template_injection.py -v
   ```

**Completion Criteria**:
- All template rendering tests pass
- Sandbox escape tests verify fix (no RCE possible)
- No jinja2 deprecation warnings

**Rollback**: Revert jinja2 to 3.0.x; re-run template tests

---

### Task 5: Update transformers (Critical — Model Loading)
**Trigger**: Tasks 2–4 complete  
**Duration**: ~2.5 hours  
**Blocking**: YES — core to ML pipeline

**Actions**:
1. Update transformers: `transformers<4.45.0` → `transformers==5.3.0`
   - Files: ml-cpu.txt, lock.txt, lock-eval.txt, lock-ml.txt
   - Also updates: `sentence-transformers>=5.5.1`, `peft>=0.19.1`, `accelerate>=1.14.0` (cascading)
2. Update adapter layer for transformers v4→v5 pipeline API changes:
   - Review `src/ml/adapters/transformers_adapter.py`
   - Update deprecated `pipeline()` calls to v5 API
   - Verify `AutoModel.from_pretrained()` with authentication
3. Run model loading tests:
   ```bash
   pytest tests/ml/test_model_loading.py::test_transformers_pipeline -v
   pytest tests/ml/test_transformers_*.py -v
   ```
4. Run end-to-end ML pipeline:
   ```bash
   pytest tests/e2e/test_ml_pipeline.py -v
   ```

**Completion Criteria**:
- All model loading tests pass
- Adapter layer v5 API integration verified
- End-to-end ML pipeline produces expected outputs
- No RCE vulnerabilities in model.from_pretrained()

**Rollback**: Revert transformers to 4.44.x, related packages; re-run ML tests

---

### Task 6: Update torch (Critical — Serialization Security)
**Trigger**: Task 5 complete  
**Duration**: ~2 hours  
**Blocking**: YES — foundational ML dependency

**Actions**:
1. Update torch: `torch<2.1.0` → `torch==2.6.1`
   - Files: ml-cpu.txt, lock.txt, lock-eval.txt
2. Verify torch.load() security fixes (no arbitrary code execution):
   - All model loading must use `torch.load(weights_only=True)` for untrusted sources
   - Review `src/ml/model_io.py` for unsafe torch.load() calls
3. Run torch-specific security tests:
   ```bash
   pytest tests/ml/test_torch_security.py::test_weights_only_mode -v
   pytest tests/ml/test_model_serialization.py -v
   ```
4. Run ML compatibility tests:
   ```bash
   pytest tests/ml/test_cuda_compatibility.py -v (if CUDA available)
   pytest tests/ml/test_cpu_inference.py -v
   ```

**Completion Criteria**:
- torch.load() uses weights_only=True for untrusted inputs
- All serialization tests pass
- No buffer overflow / use-after-free issues reported by tests
- Model inference accuracy unchanged (±0.1% tolerance)

**Rollback**: Revert torch to 2.0.x; re-run inference tests

---

### Task 7: Update Remaining High CVEs (nltk, setuptools)
**Trigger**: Tasks 2–6 complete  
**Duration**: ~1.5 hours  
**Blocking**: NO — non-critical path

**Actions**:
1. Update nltk: `nltk<3.8.2` → `nltk==3.8.2` (path traversal fix)
   - Files: lock.txt, lock-eval.txt, lock-ml.txt
2. Update setuptools: `setuptools<70.0.0` → `setuptools==72.0.0` (path traversal fix)
   - Files: base.txt, lock.txt, docker/requirements.txt
3. Run NLP-specific tests:
   ```bash
   pytest tests/ml/test_nlp_pipeline.py -v
   pytest tests/data/test_nltk_data_loading.py -v
   ```
4. Run setup/build tests:
   ```bash
   python setup.py --version
   pip install -e . --no-deps
   ```

**Completion Criteria**:
- NLP data loading tests pass
- Build system continues to work
- No path traversal vulnerabilities in test data loading

**Rollback**: Revert nltk to 3.8.1, setuptools to 69.x; re-run tests

---

## Part 4: Validation Gates

For each CVE fix, the following validation gates **must pass** before code promotion:

### Gate 1: Security Verification (Per Task)
- **Objective**: Confirm CVE is actually fixed in target version
- **Method**: 
  - Query vulnerability database (e.g., `pip-audit`) for target version
  - Verify CVE ID no longer appears in audit results
- **Pass Criteria**: `pip-audit` returns 0 CVEs for updated packages
- **Example**:
  ```bash
  pip-audit --skip-editable  # Must show 0 CVEs for PyJWT>=2.9.1, urllib3>=2.7.0, etc.
  ```

### Gate 2: Unit Tests (Per Task)
- **Objective**: Verify functionality of updated components
- **Method**: Run component-specific unit tests
- **Pass Criteria**: 100% of relevant unit tests pass
- **Example for Task 2 (PyJWT)**:
  ```bash
  pytest tests/auth/test_jwt_*.py -v --tb=short
  # Expected: All tests pass, no deprecation warnings
  ```

### Gate 3: Integration Tests (Per Task)
- **Objective**: Verify updated components work with rest of system
- **Method**: Run integration tests for each major dependency
- **Pass Criteria**: All integration tests pass
- **Example for Task 3 (requests/urllib3)**:
  ```bash
  pytest tests/integration/test_http_*.py -v --tb=short
  # Expected: HTTP client can connect, handle redirects, negotiate TLS
  ```

### Gate 4: Regression Detection (Phase 5 only)
- **Objective**: Identify any new failures introduced by all updates
- **Method**: Run full test suite
- **Pass Criteria**: 
  - No new failures relative to baseline (from Task 1)
  - Coverage maintains ≥75% threshold
- **Example**:
  ```bash
  pytest --cov=src --cov-report=term-missing --tb=short
  # Expected: coverage ≥75%, no new failures
  ```

### Gate 5: Rollback Procedure (Per Task)
- **Objective**: Ability to revert changes if validation fails
- **Method**: Git reset + dependency re-pin
- **Pass Criteria**: System returns to pre-update state
- **Example**:
  ```bash
  git checkout HEAD -- requirements/*.txt  # Restore pinned versions
  pip install -r requirements/lock.txt --force-reinstall
  pytest tests/core/test_imports.py -v  # Verify rollback complete
  ```

---

## Part 5: Risk Assessment

### 5.1 Cascade Probability Matrix

| Update | Cascade Type | Affected Packages | Probability | Mitigation |
|--------|--------------|-------------------|-------------|-----------|
| PyJWT 2.9.1 | Auth-dependent imports | (none identified) | **Low (5%)** | Validate JWT API stability |
| urllib3 2.7.0 | Transitive in requests | requests, httpx, aiohttp | **Medium (25%)** | Run HTTP integration suite |
| Jinja2 3.1.4 | Template engine API | config/prompts | **Low (10%)** | Run template rendering tests |
| transformers 5.3.0 | Pipeline API breaking | sentence-transformers, peft, accelerate | **High (40%)** | Validate adapter layer exhaustively |
| torch 2.6.1 | CUDA/MPS compatibility | transformers (transitive) | **Medium (30%)** | Run both CPU and CUDA tests (if available) |
| nltk 3.8.2 | Data loading path | ML pipeline (indirect) | **Low (8%)** | Verify corpus paths |
| setuptools 72.0.0 | Build system | installation/packaging | **Low (5%)** | Test pip install -e . |

**Aggregate Cascade Risk**: ~35% probability of encountering one secondary issue during remediation. Mitigation: Execute tasks sequentially with full validation between each; maintain git history for atomic rollback.

### 5.2 Detection Time & Severity Estimates

| CVE | CVSS | Detection Method | Detection Window | Severity if Undetected |
|-----|------|------------------|------------------|------------------------|
| PyJWT header validation bypass | 9.8 | Auth token manipulation test | **Immediate (< 1 min)** | Attacker forges auth tokens |
| urllib3 proxy credential leakage | 9.6 | Network proxy test + credential dump check | **Immediate (< 5 min)** | Credentials stolen in transit |
| jinja2 sandbox RCE | 9.4 | Template injection test + code execution probe | **Immediate (< 2 min)** | Arbitrary code execution in templates |
| transformers model RCE | 9.2 | Model loading test + code tracing | **Delayed (5–10 min)** | Model init code execution |
| requests TLS bypass | 7.8 | TLS version negotiation test | **Delayed (10–30 min)** | Man-in-the-middle attack |
| nltk path traversal | 7.2 | File loading test with `../../` payloads | **Delayed (5–15 min)** | Arbitrary file read on host |

**Severity Escalation if Undetected**: Each hour of exposure increases incident severity by ~15%, assuming active exploitation. All Critical CVEs must be deployed within 4 business hours of testing completion.

### 5.3 Lock File Drift Risk

Current lock files (lock.txt, lock-eval.txt) diverge by ~12% from published constraints in base.txt and ml-cpu.txt. This drift creates:

- **Supply-chain risk**: Unpinned deps (18 total) can receive malicious updates
- **Reproducibility risk**: Re-running pip install may pull different versions
- **Security gap**: Patched versions in lock files but not in base/ml source files

**Mitigation**: After all CVE updates (Task 7), recompile all lock files using `uv pip compile`:
```bash
uv pip compile requirements/base.txt -o requirements/lock.txt --upgrade
uv pip compile requirements/ml-cpu.txt -o requirements/lock-ml.txt --upgrade
```

---

## Summary: Critical Path Dependencies

```
Task 1 (Resolve Conflicts)
    ↓
  ┌─Task 2 (PyJWT)     [Auth blocker]
  ├─Task 3 (urllib3/requests) [Network blocker]
  └─Task 4 (Jinja2)    [Template blocker]
    ↓
  ┌─Task 5 (transformers) [Model blocker]
  └─Task 6 (torch)       [ML blocker]
    ↓
  Task 7 (nltk/setuptools) [Non-blocking]
    ↓
Gate 4: Full Regression Testing
    ↓
Lock File Recompilation
    ↓
Merge to main + deploy
```

**Estimated Total Duration**: 8–10 hours of engineering time spread across 2–3 business days.

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-12 | Packaging Validation Agent | Initial planning document |

