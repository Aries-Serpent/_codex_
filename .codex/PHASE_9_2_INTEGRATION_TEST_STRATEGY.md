# PHASE 9.2 TASK 9.2.5: INTEGRATION TESTING STRATEGY

**Document:** PHASE_9_2_INTEGRATION_TEST_STRATEGY.md  
**Generated:** 2026-06-22T11:12:24Z  
**Target Date:** 2026-07-04 (TASK 9.2.5 Execution)  
**Status:** 📋 STRATEGY DOCUMENT (Ready for Execution)

---

## OBJECTIVE

Execute comprehensive integration testing of the cascade orchestrator on 100+ real and synthetic CI failure logs. Validate that:

1. ✅ **50%+ auto-fix rate** (50+ of 100 failures fixed)
2. ✅ **<2% false positive rate** (max 2 broken fixes per 100)
3. ✅ **<5 second classification latency** (99th percentile)
4. ✅ **>95% rollback success** (failed fixes recovered)
5. ✅ **All success criteria met**

---

## TEST CORPUS GENERATION

### Tier 1: Real Historical CI Logs (40 tests)

**Source:** Last 90 days of GitHub Actions workflow logs

**Collection Method:**
```bash
gh run list --repo Aries-Serpent/_codex_ \
  --created ">2026-03-22" \
  --status failure \
  --limit 100 \
  | jq -r '.[] | .id' \
  | xargs -I {} gh run view {} --log > ci_logs/{}.txt
```

**Pattern Distribution (target):**
- RP-001 (Unused Imports): 6 logs
- RP-002 (Import Ordering): 5 logs
- RP-003 (YAML Indentation): 5 logs
- RP-004 (Coverage): 5 logs
- RP-005 (P19 Imports): 5 logs
- RP-006 (Dependency): 4 logs
- RP-007 (Workflow): 3 logs
- RP-008 (CodeQL): 2 logs

### Tier 2: Synthetic Test Cases (40 tests)

**Purpose:** Cover edge cases and stress scenarios

**Generation:**
```python
# tests/conftest.py
SYNTHETIC_CASES = [
    # RP-001 edge cases
    {'pattern': 'RP-001', 'variant': 'duplicate_import', 'count': 3},
    {'pattern': 'RP-001', 'variant': 'conditional_unused', 'count': 2},
    {'pattern': 'RP-001', 'variant': 'type_annotation', 'count': 2},
    # ... 34 more synthetic cases
]
```

**Synthetic Generation:**
- Multiple patterns per test (RP-001 + RP-002)
- Cascading failures (fix reveals new error)
- False positive traps (valid suppressions)
- Boundary conditions (edge cases)

### Tier 3: Stress & Performance Tests (20 tests)

**Load Test:**
```
1. Sequential: 100 failures one-by-one (baseline)
2. Concurrent: 10 failures simultaneously (stress)
3. Large Logs: Single log 10MB+ (scalability)
4. Complex Cascade: All 8 patterns in one log (complexity)
5. Rapid Fire: 100 failures in 1 minute (throughput)
```

---

## TEST EXECUTION PLAN

### Phase 1: Classification Testing (15 tests)

**Goal:** Validate pattern router accuracy

```python
# tests/integration/test_phase_9_2_cascade.py::test_classify_patterns
@pytest.mark.integration
def test_classify_patterns():
    router = PatternRouter()
    
    for case in TEST_CASES[:15]:
        result = router.classify(case.log_text)
        
        assert result.primary_pattern == case.expected_pattern
        assert result.confidence >= 0.75  # Min confidence for auto_fix
        assert result.processing_time_ms < 5000  # <5 seconds
        
        # Verify no false positives
        for alt_pattern in case.false_positive_patterns:
            scores = [s for s in result.all_scores if s.pattern_id == alt_pattern]
            assert not scores or scores[0].final_confidence < 0.60
```

**Success Criteria:**
- 95%+ classification accuracy
- <5s per classification
- <2% false positives

### Phase 2: Cascade Execution Testing (50 tests)

**Goal:** Validate end-to-end cascade execution

```python
# tests/integration/test_phase_9_2_cascade.py::test_cascade_execution
@pytest.mark.integration
@pytest.mark.parametrize("test_case", TEST_CASES[15:65])
async def test_cascade_execution(test_case):
    orchestrator = CascadeOrchestrator()
    
    session = await orchestrator.execute_cascade(
        session_id=f"test_{test_case.id}",
        failure_logs=test_case.log_text,
        dry_run=False,
    )
    
    # Validate session state
    assert session.final_state in [FixState.DONE, FixState.ESCALATED]
    assert session.total_duration < 120  # <2 minutes
    
    # Validate fix execution
    assert len(session.fix_executions) > 0
    successful = [f for f in session.fix_executions if f.success]
    
    # Calculate auto-fix rate
    fix_rate = len(successful) / len(session.fix_executions)
    assert fix_rate >= test_case.expected_min_rate  # Per-case expectation
```

**Success Criteria:**
- 50%+ auto-fix rate (50+ of 100 fixed)
- All rollbacks successful (>95%)
- No cascading failures

### Phase 3: Rollback & Recovery Testing (20 tests)

**Goal:** Validate failure handling and recovery

```python
# tests/integration/test_phase_9_2_cascade.py::test_cascade_rollback
@pytest.mark.integration
@pytest.mark.parametrize("test_case", TEST_CASES[65:85])
async def test_cascade_rollback(test_case):
    orchestrator = CascadeOrchestrator()
    
    # Simulate failure scenario
    with patch.object(orchestrator, '_simulate_agent_execution') as mock_exec:
        mock_exec.side_effect = Exception("Simulated failure")
        
        session = await orchestrator.execute_cascade(
            session_id=f"test_rollback_{test_case.id}",
            failure_logs=test_case.log_text,
        )
    
    # Verify rollback occurred
    rolled_back = [f for f in session.fix_executions if f.rollback_attempted]
    assert len(rolled_back) > 0
    
    # Verify state is clean
    assert session.final_state in [FixState.ROLLED_BACK, FixState.ESCALATED]
    assert not session.overall_success  # Expected failure
```

**Success Criteria:**
- >95% rollback success rate
- No data corruption on rollback
- Clean state after recovery

### Phase 4: Stress & Performance Testing (15 tests)

**Goal:** Validate system under load

```python
# tests/integration/test_phase_9_2_cascade.py::test_cascade_performance
@pytest.mark.integration
@pytest.mark.stress
async def test_cascade_performance():
    orchestrator = CascadeOrchestrator(max_parallel=3)
    
    # Sequential baseline
    start = time.time()
    for log in TEST_LOGS[:10]:
        await orchestrator.execute_cascade(f"seq_{log.id}", log.text)
    sequential_time = time.time() - start
    
    # Concurrent stress
    start = time.time()
    tasks = [
        orchestrator.execute_cascade(f"concurrent_{log.id}", log.text)
        for log in TEST_LOGS[:10]
    ]
    await asyncio.gather(*tasks)
    concurrent_time = time.time() - start
    
    # Verify concurrent is faster (not blocked)
    parallelization_factor = sequential_time / concurrent_time
    assert parallelization_factor > 1.5  # At least 1.5x faster
```

**Success Criteria:**
- 1.5x+ speedup with parallelization
- <120s cascade latency (max)
- <1% error rate under load

---

## SUCCESS CRITERIA & GO/NO-GO GATES

### Gate 1: Classification Accuracy (Tests 1-15)
```
✅ 95%+ classification accuracy
✅ <5 seconds per classification (99th percentile)
✅ <2% false positives
```

### Gate 2: Cascade Auto-Fix Coverage (Tests 16-65)
```
✅ 50%+ auto-fix rate (50+ of 100 failures fixed)
✅ >95% rollback success rate
✅ <2% broken fixes (false positives)
✅ No cascading failures detected
```

### Gate 3: Cascade Latency & Performance (Tests 66-80)
```
✅ <120 seconds per cascade (full end-to-end)
✅ <5 seconds per pattern classification
✅ <3 seconds per fix execution (average)
✅ 1.5x+ parallelization speedup
```

### Gate 4: Reliability & Stress (Tests 81-100)
```
✅ 100 concurrent failures: <1% error rate
✅ 10MB+ log files: <10 seconds classification
✅ All 8 patterns: >50% combined auto-fix rate
```

---

## METRICS & REPORTING

### Real-Time Dashboard
```
Classification Performance:
  ├─ Accuracy: XX.X%
  ├─ Latency: XXXms (avg)
  └─ False Positive Rate: X.X%

Cascade Performance:
  ├─ Auto-Fix Rate: XX%
  ├─ Rollback Success: XX%
  ├─ Failed Cascades: X
  └─ Average Latency: Xs

Pattern Distribution:
  ├─ RP-001: XX% coverage
  ├─ RP-002: XX% coverage
  ├─ RP-003: XX% coverage
  ├─ RP-004: XX% coverage
  ├─ RP-005: XX% coverage
  ├─ RP-006: XX% coverage
  ├─ RP-007: XX% coverage
  └─ RP-008: XX% coverage
```

### Test Report (JSON)
```json
{
  "timestamp": "2026-07-04T12:00:00Z",
  "total_tests": 100,
  "passed": 95,
  "failed": 5,
  "gates": {
    "gate_1_classification": "PASS",
    "gate_2_autofix_coverage": "PASS",
    "gate_3_latency": "PASS",
    "gate_4_stress": "PASS"
  },
  "coverage_by_pattern": {
    "RP-001": 0.99,
    "RP-002": 0.98,
    ...
  },
  "overall_result": "GO"
}
```

---

## FAILURE HANDLING

### If Classification Accuracy <95%
1. Identify failing patterns
2. Add more training examples
3. Adjust regex signatures
4. Re-run classification tests
5. Escalate to ML path if needed

### If Auto-Fix Coverage <50%
1. Review agent logs
2. Identify patterns with low success
3. Adjust cascade ordering
4. Increase concurrent limits
5. Consider fallback agents

### If False Positive Rate >2%
1. Review broken fixes
2. Adjust confidence thresholds
3. Add more FP detection
4. Tighten validation rules
5. Escalate to manual review

---

## TIMELINE

**Date:** 2026-07-04 (1 full day)

| Time | Phase | Tests | Target |
|------|-------|-------|--------|
| 06:00-08:00 | Prepare test corpus | - | 100 logs ready |
| 08:00-10:00 | Phase 1: Classification | 15 | 95%+ accuracy |
| 10:00-14:00 | Phase 2: Cascade | 50 | 50%+ auto-fix |
| 14:00-16:00 | Phase 3: Rollback | 20 | 95%+ recovery |
| 16:00-18:00 | Phase 4: Stress | 15 | 1.5x speedup |
| 18:00-20:00 | Analysis & reporting | - | Final report |

---

## NEXT MILESTONE: TASK 9.2.6 (Deployment)

**Date:** 2026-07-05 (0.5 days)

Once TASK 9.2.5 succeeds (all 4 gates PASS):

1. Create deployment plan
2. Prepare canary configuration (10% traffic)
3. Set up monitoring dashboards
4. Document rollback procedures
5. Brief SRE team on deployment

---

## AUTHORITY

**Track Lead:** self-healing-orchestrator-agent  
**Campaign Authority:** @mbaetiong (D-tier)  
**Go/No-Go Authority:** @mbaetiong  

---

**Status:** 🟡 READY FOR EXECUTION  
**Timeline:** 2026-07-04 (1 day from now)  
**Next:** Execute TASK 9.2.5 integration tests
