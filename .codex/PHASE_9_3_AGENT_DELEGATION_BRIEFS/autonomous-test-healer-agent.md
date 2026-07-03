# 🧪 AUTONOMOUS-TEST-HEALER-AGENT DELEGATION BRIEF
**Phase 9.3 → Phase 10 Handoff Document**

**Generated:** 2026-07-03T17:50:00Z  
**Authority:** Skills Master Agent  
**Target Agent:** autonomous-test-healer-agent  
**Status:** READY FOR ACTIVATION (2026-07-04T08:00:00Z)  
**Priority:** 🔴 **CRITICAL PATH**

---

## 📋 MISSION STATEMENT

You are the **Test Stability Guardian** for Phase 10. Your primary mission is to:

1. **Stabilize tests post-dependency-upgrade** (Ray, NLTK, Sentencepiece, Starlette, Wandb)
2. **Eliminate flaky tests** introduced by version changes
3. **Validate test reliability** across all 2,667+ test cases
4. **Maintain ≥90% code coverage** throughout Phase 10 execution
5. **Coordinate with ci-auto-healer-agent** on upgrade timing and conflict resolution

**Success Metric:** 100% test pass rate with 0 flaky tests and ≥90% coverage by Phase 10 EOD.

---

## 🎯 PHASE 10 OBJECTIVES

### Primary Objectives (Must Complete)

#### OBJ-1: Ray 2.52.0+ Test Stabilization
**Context from Phase 9 Audit:** Ray upgraded from 2.9.x to fix 8 critical RCE/ACE CVEs

**Your Actions:**
1. Monitor CI execution with Ray 2.52.0+ (ci-auto-healer-agent deploys)
2. Detect flaky tests introduced by version change
3. Focus areas:
   - **Distributed computing tests:** Ray workers may have different behavior
   - **ML training tests:** Distributed training orchestration changed
   - **Parallel test execution:** Ray job submission API may affect test scheduling
   - **Serialization tests:** Object serialization format may differ
4. For each flaky test found:
   - Identify root cause (API change vs. timeout vs. resource contention)
   - Apply @pytest.mark.flaky if intermittent by design
   - Add retry logic with exponential backoff if timing-sensitive
   - Increase timeout if resource-constrained
5. Run 5+ passes of full test suite to confirm stability

**Expected Flaky Tests:**
- ~5-10 tests likely to be timing-sensitive post-upgrade
- ~2-3 tests may need Ray API migration
- ~1-2 tests may have serialization issues

**Success Criteria:**
- All Ray-dependent tests pass consistently (5/5 passes)
- No @pytest.mark.flaky without documented reasoning
- Test execution time within 10% of baseline

**Timeline:** Week 1, MON-WED (Parallel with NLTK/Sentencepiece)

---

#### OBJ-2: NLTK 3.10.0+ Test Stabilization
**Context from Phase 9 Audit:** NLTK upgraded from 3.9.4 to fix path traversal vulnerability

**Your Actions:**
1. Monitor NLTK-dependent tests (ci-auto-healer-agent deploys)
2. Detect flaky tests from version change
3. Focus areas:
   - **Tokenization tests:** Ensure token boundaries unchanged
   - **Corpus loading:** Path validation in new version may behave differently
   - **NLP pipeline tests:** Entity recognition, POS tagging, parsing
   - **Language model tests:** Model loading and inference accuracy
4. For each flaky test:
   - Verify expected vs. actual tokenization (tolerance: 99.9% match)
   - Check corpus file paths (ensure new version's path validation compatible)
   - Add retry logic if corpus download timing-sensitive
5. Validate tokenization accuracy across all supported languages

**Expected Flaky Tests:**
- ~3-5 corpus loading tests (may be timing-sensitive)
- ~2-3 tokenization accuracy tests (if tolerance too strict)
- ~1 language-specific test (model loading variation)

**Success Criteria:**
- All NLP tests pass with >99.9% tokenization accuracy
- Corpus files load consistently
- No intermittent failures over 5 test passes

**Timeline:** Week 1, MON-TUE (Parallel with Ray)

---

#### OBJ-3: Sentencepiece 0.2.1+ Test Stabilization
**Context from Phase 9 Audit:** Sentencepiece upgraded from 0.1.99 to fix heap overflow vulnerability

**Your Actions:**
1. Monitor tokenization tests (ci-auto-healer-agent deploys)
2. Detect flaky tests from version change
3. Focus areas:
   - **BPE tokenization:** Byte-pair encoding algorithm may differ
   - **WordPiece tokenization:** Custom vocabulary handling
   - **Model compatibility:** Old models may not load in new version
   - **Memory usage:** Heap overflow fix may change memory behavior
4. For each flaky test:
   - Check model file format compatibility
   - Verify token accuracy (tolerance: 99.9%)
   - Monitor memory usage during tests
   - Add retry logic if model loading timing-sensitive
5. Benchmark memory usage pre/post-upgrade

**Expected Flaky Tests:**
- ~2-3 model loading tests (version compatibility)
- ~1-2 memory usage tests (threshold changes)
- ~1 tokenization accuracy test (if vocab changed)

**Success Criteria:**
- All tokenization tests pass with >99.9% accuracy
- Models load and serialize correctly
- Memory usage within 10% of baseline
- No out-of-memory errors on stress tests

**Timeline:** Week 1, TUE-WED (Parallel with Ray/NLTK)

---

#### OBJ-4: Starlette 0.31.0+ Test Stabilization
**Context from Phase 9 Audit:** Starlette upgraded to fix DoS/SSRF vulnerabilities

**Your Actions:**
1. Monitor HTTP integration tests (ci-auto-healer-agent deploys)
2. Detect flaky tests from version change
3. Focus areas:
   - **Request handling:** Middleware order may change
   - **Async/await:** Async context handling may differ
   - **Connection pooling:** Starlette's connection pool changed
   - **Error handling:** Error page generation differs
4. For each flaky test:
   - Check request/response timing
   - Verify async context preservation
   - Add retry logic for connection pool tests
   - Adjust timeout for slow endpoints
5. Validate DoS protection (rate limiting, connection limits)

**Expected Flaky Tests:**
- ~2-3 async context tests
- ~1-2 connection pooling tests
- ~1 timeout test (middleware changed)

**Success Criteria:**
- All HTTP tests pass consistently
- Async contexts preserved across requests
- DoS protection engaged correctly
- Connection limits respected

**Timeline:** Week 2, MON-TUE (After critical upgrades)

---

#### OBJ-5: Wandb 0.15.4+ Test Stabilization
**Context from Phase 9 Audit:** Wandb upgraded to fix SSRF vulnerability

**Your Actions:**
1. Monitor experiment tracking tests (ci-auto-healer-agent deploys)
2. Detect flaky tests from version change
3. Focus areas:
   - **Remote logging:** API endpoint handling
   - **Experiment metadata:** Serialization format changes
   - **Network connectivity:** SSRF protection may affect test setup
4. For each flaky test:
   - Check network timeout handling
   - Verify metadata format compatibility
   - Add retry logic for remote logging
5. Validate SSRF protection (no external URL leakage)

**Expected Flaky Tests:**
- ~1-2 network connectivity tests
- ~1 metadata serialization test

**Success Criteria:**
- All Wandb integration tests pass
- Metadata serialization compatible
- SSRF vulnerability confirmed fixed
- Network tests reliable

**Timeline:** Week 2, TUE-WED (After critical upgrades)

---

### Secondary Objectives (Should Complete)

#### OBJ-6: @pytest.mark.flaky Inventory & Documentation
**Your Actions:**
1. Audit all tests marked with @pytest.mark.flaky
2. Document reason for each flaky marker
3. Identify tests that should no longer be flaky post-upgrade
4. Remove obsolete markers
5. Create `.codex/PHASE_10_FLAKY_TEST_INVENTORY.md` documenting:
   - Total flaky tests (target: <5)
   - Reason for each flaky marker
   - Stability score per test (pass rate over 10 runs)
   - Remediation roadmap for each

**Success Criteria:**
- All flaky markers documented
- Pass rate ≥95% for all tests (including flaky)
- No undocumented flaky tests

**Timeline:** Week 1, WED-THU

---

#### OBJ-7: Performance Benchmarking Post-Upgrade
**Your Actions:**
1. Measure test execution time pre/post-upgrade for:
   - Ray tests (compare 2.9.x vs 2.52.0+)
   - NLTK tests (compare 3.9.4 vs 3.10.0+)
   - Sentencepiece tests (compare 0.1.99 vs 0.2.1+)
   - All other affected tests
2. Identify performance regressions (>10% slowdown triggers investigation)
3. Document findings in `.codex/PHASE_10_TEST_PERFORMANCE_REPORT.md`
4. Recommend optimizations if needed

**Success Criteria:**
- <10% average performance regression
- No timeout-induced test failures
- Detailed before/after comparison captured

**Timeline:** Week 1, FRI (After all upgrades)

---

#### OBJ-8: Test Stabilization Report
**Your Actions:**
1. Document all flaky tests detected and fixed
2. Capture stability metrics:
   - Total tests run: 2,667+
   - Flaky tests detected: X
   - Flaky tests fixed: Y
   - Remaining flaky tests: Z (with reasons)
3. Generate `.codex/PHASE_10_TEST_STABILIZATION_REPORT.md`

**Deliverable:** `.codex/PHASE_10_TEST_STABILIZATION_REPORT.md`

**Timeline:** Week 1, FRI

---

## 🧪 FLAKY TEST HEALING PATTERNS

### Pattern 1: Timeout-Induced Flakiness
**Symptom:** Test passes 7/10 times but fails randomly; CI timeout error

**Root Cause:** New dependency version slightly slower; test timeout insufficient

**Healing Strategy:**
1. Measure actual test execution time: `time pytest test_module.py::test_name`
2. Increase timeout by 2x as conservative estimate
3. Run test 10 times to confirm stability
4. If still flaky, investigate algorithmic changes in dependency

**Example:**
```python
# BEFORE
def test_distributed_training():
    # timeout=300s, fails ~30% of time
    train_model(...)

# AFTER
def test_distributed_training():
    # timeout=600s, passes 100% of time
    train_model(...)
```

---

### Pattern 2: API Compatibility Flakiness
**Symptom:** Test fails with `AttributeError` or `ImportError` intermittently

**Root Cause:** Dependency API changed; test expects old behavior

**Healing Strategy:**
1. Detect: Check error traceback for `AttributeError` or `ImportError`
2. Research: Check dependency's changelog for breaking changes
3. Fix: Update test to use new API
4. Validate: Run test 10 times to confirm fix
5. Document: Log API migration step

**Example:**
```python
# BEFORE (Ray 2.9.x API)
from ray.tune import run
result = run(trainable_cls)

# AFTER (Ray 2.52.0+ API)
from ray.train import ScalingConfig, RunConfig
from ray.tune import TuneConfig, Tuner
tuner = Tuner(trainable_cls, tune_config=TuneConfig(...))
result = tuner.fit()
```

---

### Pattern 3: Resource Contention Flakiness
**Symptom:** Test passes with `-n 1` (sequential) but fails with `-n auto` (parallel)

**Root Cause:** Parallel execution with Ray/Sentencepiece causes resource contention

**Healing Strategy:**
1. Detect: Note if test passes sequentially but fails in parallel
2. Add markers: `@pytest.mark.flaky(reruns=3)` for intermittent failures
3. Investigate: Check if test uses shared resources (temp files, ports, memory)
4. Fix: Isolate test resources or add proper cleanup
5. Validate: Test passes with `-n auto` on 5 consecutive runs

**Example:**
```python
# BEFORE (fails ~20% with parallel execution)
def test_model_loading():
    model = load_model("./model")
    assert model is not None

# AFTER (always passes)
def test_model_loading(tmp_path):
    # Use isolated temp path
    model = load_model(str(tmp_path / "model"))
    assert model is not None
```

---

### Pattern 4: Serialization/Deserialization Flakiness
**Symptom:** Test fails intermittently when running serialized tests (Ray/Sentencepiece models)

**Root Cause:** Serialization format changed; model loading/saving incompatible

**Healing Strategy:**
1. Detect: Check if failure involves pickle/serialization operations
2. Verify: Confirm model files compatible with new version
3. Fix: Re-export models with new version if needed
4. Validate: Test serialization/deserialization cycle 10 times
5. Document: Record model re-export steps

**Example:**
```python
# BEFORE (Ray 2.9.x serialization)
pickle.dump(ray_actor, file)
loaded_actor = pickle.load(file)  # Fails with Ray 2.52.0+

# AFTER (Ray 2.52.0+ requires re-serialization)
# Re-export all Ray actors with new version
ray.shutdown()
import ray; ray.init()
# Actors now serialize/deserialize correctly
```

---

### Pattern 5: Dependency Interaction Flakiness
**Symptom:** Test fails when multiple dependencies are upgraded together

**Root Cause:** Ray + NLTK + Sentencepiece have subtle interaction bugs

**Healing Strategy:**
1. Detect: Test fails only when all 3 are upgraded; passes with 1-2 upgraded
2. Isolate: Temporarily downgrade one dependency, re-test
3. Identify: Confirm which dependency pair causes issue
4. Report: Log to orchestrator-agent for escalation
5. Workaround: If necessary, add sentinel check to prevent bad state

**Example:**
```python
# BEFORE (Ray 2.52.0 + Sentencepiece 0.2.1 have subtle interaction)
def test_tokenize_with_ray_workers():
    # Fails due to Ray's new serialization not compatible with Sentencepiece 0.2.1
    pass

# AFTER (After Sentencepiece team releases patch)
def test_tokenize_with_ray_workers():
    # Passes with Ray 2.52.0 + Sentencepiece 0.2.1 + patch
    pass
```

---

## 📊 PRE-PHASE-10 CHECKLIST

Before Phase 10 launch (complete by 2026-07-03 EOD):

- [ ] Review Phase 9 audit findings (no flaky test increases expected)
- [ ] Audit current flaky test inventory (baseline for Phase 10)
- [ ] Document reasoning for each existing @pytest.mark.flaky
- [ ] Prepare test environment (GPU if ML tests require)
- [ ] Stage test suite for rapid execution
- [ ] Review ci-auto-healer-agent briefing (understand upgrade timeline)
- [ ] Confirm orchestrator-agent readiness
- [ ] Set up test metrics collection (baseline before upgrades)
- [ ] Prepare remediation playbooks for known flaky patterns

---

## 🚀 PHASE 10 EXECUTION ROADMAP

### Week 1: CRITICAL DEPENDENCY TEST STABILIZATION

```
MON 2026-07-08:
  09:00 - Kickoff: Understand Ray 2.52.0+ changes
  09:30 - Monitor ci-auto-healer-agent's Ray upgrade
  10:00 - Detect flaky tests from Ray upgrade
  12:00 - Heal flaky tests (timeouts, API changes)
  14:00 - Run Ray test suite 5 times (stability validation)
  17:00 - EOD: Checkpoint with orchestrator-agent

TUE 2026-07-09:
  09:00 - Monitor NLTK 3.10.0+ upgrade
  09:30 - Detect flaky tests from NLTK upgrade
  11:00 - Validate tokenization accuracy (>99.9%)
  12:00 - Heal flaky corpus loading tests
  15:00 - Run NLTK test suite 5 times
  17:00 - EOD: Checkpoint

WED 2026-07-10:
  09:00 - Monitor Sentencepiece 0.2.1+ upgrade
  09:30 - Detect flaky tests from Sentencepiece
  11:00 - Validate model compatibility
  12:00 - Benchmark memory usage
  14:00 - Heal flaky model loading tests
  15:00 - Run tokenization tests 5 times
  17:00 - EOD: Collect metrics + document flaky inventory

THU-FRI 2026-07-11-12:
  - Full test suite validation (all 2,667+ tests)
  - Stability runs (3+ full passes)
  - Performance benchmarking
  - Prepare for Week 2 secondary upgrades
```

### Week 2: SECONDARY UPGRADES & FINAL STABILIZATION

```
MON 2026-07-15:
  - Monitor Starlette 0.31.0+ upgrade
  - Detect flaky HTTP tests
  - Heal async/await compatibility issues

TUE 2026-07-16:
  - Monitor Wandb 0.15.4+ upgrade
  - Detect flaky experiment tracking tests
  - Run integration tests 5 times

WED 2026-07-17:
  - Final full test suite run (all 2,667+ tests)
  - Stability validation (5 passes minimum)
  - Prepare gate review

THU-FRI 2026-07-18-19:
  - Generate final stabilization report
  - Prepare release candidate testing
```

---

## 🔄 CROSS-AGENT COORDINATION

### With ci-auto-healer-agent
- **Upgrade Timing:** They upgrade; you monitor tests simultaneously
- **Flaky Detection:** You report flaky tests; they provide context if dependency-caused
- **Timeout Coordination:** Report timeout increases needed; they may adjust CI timeouts
- **API Changes:** Report import errors; they may need to update source code

### With unified-coverage-agent
- **Coverage Impact:** After each upgrade, they validate coverage maintained ≥90%
- **Gap Detection:** They identify new coverage gaps from test changes
- **Regression Prevention:** They catch if upgrading breaks coverage

### With orchestrator-agent
- **Sequencing:** Confirm upgrade order; report if tests need different sequence
- **Blocking Issues:** Report if test failures block other agents
- **Timeline Adjustment:** Report delays in stabilization; they reschedule others

---

## 📋 DELIVERABLES

| Deliverable | Type | Timeline | Status |
|-------------|------|----------|--------|
| Ray test stabilization (flakies fixed) | Fixes | Week 1, WED | Pending |
| NLTK test stabilization (flakies fixed) | Fixes | Week 1, WED | Pending |
| Sentencepiece test stabilization | Fixes | Week 1, WED | Pending |
| Starlette test stabilization | Fixes | Week 2, TUE | Pending |
| Wandb test stabilization | Fixes | Week 2, TUE | Pending |
| PHASE_10_FLAKY_TEST_INVENTORY.md | Document | Week 1, THU | Pending |
| PHASE_10_TEST_PERFORMANCE_REPORT.md | Document | Week 1, FRI | Pending |
| PHASE_10_TEST_STABILIZATION_REPORT.md | Document | Week 1, FRI | Pending |
| Full test suite passing (2,667+) | Validation | Week 2, FRI | Pending |

---

## ✅ SUCCESS CRITERIA

**By Phase 10 EOD, you will have succeeded if:**

1. ✅ All 2,667+ tests passing (100% pass rate)
2. ✅ <5 flaky tests remaining (with documented reasons)
3. ✅ Zero flaky tests introduced by dependency upgrades
4. ✅ All @pytest.mark.flaky documented and justified
5. ✅ Test execution P95 <5 seconds (no regression)
6. ✅ Memory usage <10% regression post-Sentencepiece upgrade
7. ✅ Tokenization accuracy >99.9% preserved
8. ✅ DoS protection validated (Starlette)
9. ✅ SSRF vulnerability confirmed fixed (Wandb)
10. ✅ Full test stabilization report generated

---

## 📚 REFERENCE DOCUMENTS

- **Primary:** `.codex/PHASE_9_3_AGENT_DELEGATION_BRIEFS/phase-9-to-10-transition-context.md`
- **CI Healer Brief:** `.codex/PHASE_9_3_AGENT_DELEGATION_BRIEFS/ci-auto-healer-agent.md`
- **Security Audit:** `.codex/PHASE_9_GATE2_SECURITY_AUDIT.md`
- **Remediation Plan:** `.codex/PHASE_9_GATE2_REMEDIATION_PLAN.md`
- **Current Test Status:** `.codex/PHASE_9_2_COVERAGE_REPORT.md` (if available)

---

**Status:** ✅ DELEGATION BRIEF COMPLETE  
**Authority:** Skills Master Agent  
**Activation Date:** 2026-07-04T08:00:00Z  
**Review Frequency:** Daily (Phase 10 Week 1), weekly thereafter  
**Escalation Contact:** orchestrator-agent (if blocking issues detected)
