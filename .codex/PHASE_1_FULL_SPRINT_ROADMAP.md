# Phase 1 Full Sprint Roadmap: 120 Tests, 24-Hour Execution

**Status:** 📋 Ready for Execution  
**Duration:** 24 hours (parallel execution)  
**Target Tests:** 120 new unit & integration tests  
**Coverage Target:** 34% → 37–42% (3–8 percentage point gain)  
**Confidence:** 90% (HIGH)  
**Anti-Regression:** `fail_under = 34` baseline PROTECTED (never lowers)

---

## 📊 Executive Summary

Following the Phase 4 quick-win sprint (codex_plans: 0% → 30%), Phase 1 executes a **full-scale parallel gap-fill** across four high-impact modules:

| Module | Current Coverage | Target | Estimated Tests | Test Density |
|--------|------------------|--------|-----------------|---|
| `src/codex_ml` | 10.54% | 25% | 30 | ~0.31/100 LOC |
| `src/services` | 7.41% | 20% | 20 | ~3.43/100 LOC |
| `src/codex` | 20.08% | 35% | 40 | ~2.72/100 LOC |
| `src/mcp` | 16.67% | 30% | 30 | ~4.66/100 LOC |
| **TOTAL** | **~13.8%** | **~27%** | **120** | **~1.49/100 LOC** |

---

## 🎯 Phase 1 Objectives

| # | Objective | Difficulty | Priority | Effort |
|---|-----------|------------|----------|--------|
| O1 | Gap-fill `src/codex_ml` (30 tests, ML/torch focus) | HIGH | CRITICAL | 12h |
| O2 | Gap-fill `src/services` (20 tests, API/integration) | MEDIUM | HIGH | 6h |
| O3 | Gap-fill `src/codex` (40 tests, core logic) | HIGH | CRITICAL | 10h |
| O4 | Gap-fill `src/mcp` (30 tests, protocol/IPC) | MEDIUM | HIGH | 8h |
| O5 | Run mutation testing (identify weak assertions) | MEDIUM | MEDIUM | 2h |
| O6 | Validate threshold raise (34% → 40%) | LOW | CRITICAL | 1h |
| O7 | Generate detailed test-cycle analysis | LOW | MEDIUM | 1h |
| **TOTAL ESTIMATED** | | | | **~40h** |
| **Parallel Execution** (with 4 lanes) | | | | **~10h** |

---

## 🏗️ Test Architecture: Module-by-Module Breakdown

### 1. `src/codex_ml` — Machine Learning Core (98.3k LOC, 472 files)

**Current State:**
- Coverage: 10.54% (1,036 lines of 9,831)
- Test Files: 6 existing
- Total Test LOC: ~2,500
- Estimated Untested Lines: 8,795

**Coverage Gaps:**
- Model initialization & validation: ~40% untested
- Training loop edge cases: ~70% untested
- Loss computation & gradients: ~60% untested
- Checkpointing & serialization: ~80% untested

**Test Strategy (30 tests, ~3,600 LOC):**

| Test Class | Count | Focus | Estimated LOC |
|-----------|-------|-------|---|
| `TestModelInitialization` | 5 | Constructor args, device placement, state dict | 300 |
| `TestTrainingLoops` | 8 | Forward/backward pass, gradient flow, loss tracking | 800 |
| `TestLossComputation` | 5 | Multi-task loss, weighting, NaN handling | 400 |
| `TestCheckpointing` | 4 | Save/load state, version compatibility | 300 |
| `TestInferenceMode` | 4 | eval mode, batch processing, memory efficiency | 400 |
| `TestTorchIntegration` | 4 | Device handling, dtype casting, autograd hooks | 400 |

**High-Risk Areas:**
- ⚠️ P19 shadow imports from transformers/torch (use explicit imports)
- ⚠️ GPU/CPU device handling (mock torch.device)
- ⚠️ Stochastic behaviors (set seeds in setup)

**Test Patterns:**
```python
# Pattern 1: Model lifecycle
@pytest.fixture
def model(tmp_path):
    return CodexMLModel.from_pretrained("gpt2", cache_dir=str(tmp_path))

# Pattern 2: Training step
def test_training_step_updates_params():
    model = CodexMLModel(dim=512)
    optim = torch.optim.Adam(model.parameters())
    
    loss = model.forward(input_ids=torch.randn(2, 128, dtype=torch.long))
    loss.backward()
    optim.step()
    
    assert model.training

# Pattern 3: Device handling (NO GPU in tests)
def test_device_handling_cpu_only():
    model = CodexMLModel(device='cpu')
    output = model.inference(torch.randn(1, 512))
    assert output.device.type == 'cpu'
```

---

### 2. `src/services` — API & Integration Services (5.8k LOC, 28 files)

**Current State:**
- Coverage: 7.41% (431 lines of 5,829)
- Test Files: 3 existing
- Total Test LOC: ~800
- Estimated Untested Lines: 5,398

**Coverage Gaps:**
- API endpoint handlers: ~85% untested
- Error handling & HTTP status codes: ~90% untested
- Authentication & authorization: ~80% untested
- Database query composition: ~75% untested

**Test Strategy (20 tests, ~2,400 LOC):**

| Test Class | Count | Focus | Estimated LOC |
|-----------|-------|-------|---|
| `TestAPIEndpoints` | 7 | GET/POST/PUT/DELETE, status codes, response formats | 700 |
| `TestErrorHandling` | 4 | 404/500 errors, validation failures, timeouts | 400 |
| `TestAuthN_AuthZ` | 4 | Token validation, role-based access, JWT refresh | 500 | <!-- pragma: allowlist secret -->
| `TestDatabaseQueries` | 3 | Query composition, filtering, pagination | 400 |
| `TestServiceIntegration` | 2 | End-to-end workflows, dependency injection | 400 |

**High-Risk Areas:**
- ⚠️ Mock database connections (use pytest fixtures + monkeypatch)
- ⚠️ Async/await handlers (use pytest-asyncio)
- ⚠️ HTTP request/response mocking (use responses or httpx mock)

**Test Patterns:**
```python
# Pattern 1: API endpoint
@pytest.mark.asyncio
async def test_get_user_endpoint():
    client = AsyncTestClient(app)
    response = await client.get("/api/users/123")
    assert response.status_code == 200
    assert response.json()["id"] == "123"

# Pattern 2: Error handling
def test_invalid_request_returns_400():
    client = TestClient(app)
    response = client.post("/api/users", json={"name": ""})  # invalid
    assert response.status_code == 400

# Pattern 3: Auth guard
def test_endpoint_requires_token():  # pragma: allowlist secret
    client = TestClient(app)
    response = client.get("/api/admin/users")
    assert response.status_code == 401
```

---

### 3. `src/codex` — Core Logic (14.7k LOC, 47 files)

**Current State:**
- Coverage: 20.08% (2,941 lines of 14,693)
- Test Files: 28 existing
- Total Test LOC: ~8,000
- Estimated Untested Lines: 11,752

**Coverage Gaps:**
- Configuration loading & validation: ~60% untested
- State machine transitions: ~50% untested
- Event handling & callbacks: ~70% untested
- Utility functions & helpers: ~40% untested

**Test Strategy (40 tests, ~4,800 LOC):**

| Test Class | Count | Focus | Estimated LOC |
|-----------|-------|-------|---|
| `TestConfiguration` | 8 | YAML parsing, defaults, override logic, validation | 800 |
| `TestStateMachine` | 10 | State transitions, invalid moves, event sequences | 1,200 |
| `TestCallbacks` | 8 | Hook registration, callback ordering, exception handling | 800 |
| `TestUtilities` | 7 | String formatting, path handling, data transformations | 700 |
| `TestIntegration` | 7 | Config→StateMachine→Callbacks workflows | 1,300 |

**High-Risk Areas:**
- ⚠️ YAML parsing edge cases (use pytest parametrize for variants)
- ⚠️ State machine deadlocks (add timeout fixtures)
- ⚠️ Callback exception propagation (test both sync & async)

**Test Patterns:**
```python
# Pattern 1: Configuration
@pytest.mark.parametrize("yaml_content,expected_key", [
    ("key: value", "value"),
    ("key: 123", 123),
])
def test_config_parsing(yaml_content, expected_key):
    cfg = Config.from_yaml(yaml_content)
    assert cfg.key == expected_key

# Pattern 2: State machine
def test_valid_state_transition():
    sm = StateMachine(initial_state="IDLE")
    sm.trigger("start")
    assert sm.state == "RUNNING"

def test_invalid_state_transition_raises():
    sm = StateMachine(initial_state="IDLE")
    with pytest.raises(InvalidStateTransition):
        sm.trigger("stop")  # IDLE->STOP is invalid

# Pattern 3: Callbacks
def test_callback_execution_order():
    results = []
    sm = StateMachine()
    sm.on_state_change(lambda s: results.append(f"enter_{s}"))
    
    sm.trigger("start")
    assert results == ["enter_RUNNING"]
```

---

### 4. `src/mcp` — Model Context Protocol (6.4k LOC, 60 files)

**Current State:**
- Coverage: 16.67% (1,071 lines of 6,430)
- Test Files: 3 existing
- Total Test LOC: ~1,200
- Estimated Untested Lines: 5,359

**Coverage Gaps:**
- Protocol message serialization/deserialization: ~80% untested
- IPC bridge communication: ~70% untested
- Resource management & cleanup: ~85% untested
- Error recovery & reconnection: ~90% untested

**Test Strategy (30 tests, ~3,600 LOC):**

| Test Class | Count | Focus | Estimated LOC |
|-----------|-------|-------|---|
| `TestMessageSerialization` | 8 | Encode/decode, schema validation, version compat | 800 |
| `TestIPCBridge` | 7 | Socket communication, message queuing, flow control | 900 |
| `TestResourceManagement` | 8 | Resource allocation, cleanup, leak detection | 900 |
| `TestErrorRecovery` | 5 | Reconnection, exponential backoff, state recovery | 600 |
| `TestProtocolIntegration` | 2 | End-to-end message flow, multi-process sync | 400 |

**High-Risk Areas:**
- ⚠️ Multi-process/threading synchronization (use threading.Event + monkeypatch)
- ⚠️ Socket mocking (use unittest.mock.patch or socket fixtures)
- ⚠️ Timing-dependent behaviors (use freezegun for time mocking)

**Test Patterns:**
```python
# Pattern 1: Message serialization
def test_message_roundtrip():
    msg = MCPMessage(
        id=42,
        method="invoke",
        params={"tool": "search", "query": "test"}
    )
    serialized = msg.serialize()
    deserialized = MCPMessage.deserialize(serialized)
    
    assert deserialized.id == msg.id
    assert deserialized.method == msg.method

# Pattern 2: IPC bridge
@pytest.fixture
def bridge():
    b = MCPBridge(socket_path="/tmp/test_mcp.sock")
    yield b
    b.close()  # cleanup

def test_bridge_send_receive(bridge):
    sent_msg = MCPMessage(id=1, method="test")
    bridge.send(sent_msg)
    
    received = bridge.receive(timeout=1.0)
    assert received.id == sent_msg.id

# Pattern 3: Resource cleanup
def test_resource_cleanup_on_error():
    bridge = MCPBridge()
    try:
        bridge.connect()
        raise RuntimeError("Simulated error")
    except RuntimeError:
        pass
    
    assert not bridge.is_connected
    assert bridge.get_resource_count() == 0
```

---

## 🚀 Parallel Execution Strategy (4-Lane Model)

```
PARALLEL LANES (24-hour execution)
├─ LANE 1 (codex_ml): 30 tests, ~12 hours
├─ LANE 2 (services): 20 tests, ~6 hours
├─ LANE 3 (codex): 40 tests, ~10 hours
└─ LANE 4 (mcp): 30 tests, ~8 hours

ORCHESTRATION
├─ Launch all 4 lanes simultaneously (T=0)
├─ Monitor batch scan status every 4 hours
├─ Auto-fail if any lane regresses fail_under
└─ Converge at T=12h with mutation testing (Phase 2)
```

### Lane Execution Timeline

```
T=0h    ├─ LANE 1: Start codex_ml gap-fill tests
        ├─ LANE 2: Start services gap-fill tests
        ├─ LANE 3: Start codex gap-fill tests
        └─ LANE 4: Start mcp gap-fill tests

T=4h    ├─ LANE 1: 30% complete, batch scan checkpoint
        ├─ LANE 2: 50% complete
        ├─ LANE 3: 35% complete
        └─ LANE 4: 45% complete

T=8h    ├─ LANE 1: 60% complete
        ├─ LANE 2: 90% complete
        ├─ LANE 3: 75% complete
        └─ LANE 4: 85% complete

T=12h   ├─ All lanes converge
        ├─ Measure total coverage
        ├─ Check fail_under ≥ 40%
        └─ Generate mutation testing report

T=20h   └─ OPTIONAL: Raise fail_under 34% → 40%
        └─ Generate phase completion report

T=24h   └─ PHASE 1 COMPLETE
```

---

## 📊 Test Module Mapping

### Quick Reference: Test File Organization

```
tests/
├─ test_codex_plans.py (existing, 398 LOC)
├─ test_codex_plans_api.py (existing, 396 LOC)
├─ test_codex_plans_comprehensive.py (existing, 461 LOC)
├─ test_codex_plans_extended.py (existing, 333 LOC)
│
├─ [QUICK-WIN SPRINT]
├─ test_codex_plans_gap_fill.py (NEW, 500 LOC) — Phase 4
│
├─ [PHASE 1 FULL SPRINT]
├─ test_codex_ml_gap_fill_lane1.py (NEW, 2,000 LOC) — codex_ml
├─ test_codex_ml_gap_fill_lane1_extended.py (NEW, 1,600 LOC) — codex_ml models
│
├─ test_services_gap_fill.py (NEW, 1,200 LOC) — services APIs
├─ test_services_error_handling.py (NEW, 1,200 LOC) — services errors
│
├─ test_codex_gap_fill_core.py (NEW, 1,800 LOC) — codex core
├─ test_codex_gap_fill_config.py (NEW, 1,500 LOC) — codex config
├─ test_codex_gap_fill_utils.py (NEW, 1,500 LOC) — codex utils
│
├─ test_mcp_gap_fill_bridge.py (NEW, 1,500 LOC) — mcp bridge
├─ test_mcp_gap_fill_protocol.py (NEW, 2,100 LOC) — mcp protocol
│
└─ test_coverage_integration.py (NEW, 800 LOC) — cross-module workflows
```

**Total New Test LOC (Phase 1):** ~19,400 LOC

---

## ✅ Success Criteria

### Coverage Metrics

| Module | Baseline | Target | Success Threshold |
|--------|----------|--------|---|
| src/codex_ml | 10.54% | 25% | ≥22% |
| src/services | 7.41% | 20% | ≥18% |
| src/codex | 20.08% | 35% | ≥32% |
| src/mcp | 16.67% | 30% | ≥28% |
| **WEIGHTED TOTAL** | **~13.8%** | **~27%** | **≥25%** |

### Quality Gates

| Gate | Requirement | Pass/Fail |
|------|-------------|---|
| Test Pass Rate | ≥99% (max 1 flaky) | ✅ PASS if ≤1 failure |
| Regression Check | `fail_under` ≥ 34% (NO decrease) | ✅ PASS if ≥34% |
| Batch Scan Clean | All 4 lanes pass batch scan | ✅ PASS if all green |
| Mutation Score | ≥70% (assertions survive ≥70% mutations) | ✅ PASS if ≥70% |
| Code Review | No anti-patterns, proper mocking | ✅ PASS if approved |

---

## ⚠️ Risk Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---|
| P19 shadow imports (torch/transformers) | Medium (30%) | High | Use explicit imports, test on CPU-only |
| Flaky async tests | Medium (25%) | High | Use pytest-asyncio, set fixed seeds |
| Batch scan timeout (120+ test files) | Low (10%) | High | Run incremental scans, use `--fail-fast` |
| Mock socket/IPC complexity | High (40%) | Medium | Use pre-built socket fixtures, document patterns |
| Test interdependencies | Low (5%) | High | Ensure each test is self-contained |
| Stochastic ML behaviors | Medium (30%) | Medium | Set `torch.manual_seed()` in fixtures |
| Async HTTP timeouts | Low (15%) | Medium | Increase timeout in test env, use fixed delays |

**Overall Risk Level:** 🟡 MEDIUM

---

## 🔧 Execution Commands

### Pre-Sprint Checklist

```bash
#!/bin/bash
set -e

echo "=== Phase 1 Full Sprint Pre-Flight Check ==="

# 1. Verify batch scan script exists
if [ ! -f "scripts/ci/rvs_preflight.py" ]; then
    echo "❌ Batch scan script not found!"
    exit 1
fi

# 2. Verify pytest config
grep -q "fail_under = 34" pyproject.toml || {
    echo "❌ fail_under not set to 34"
    exit 1
}

# 3. Check available workers
WORKERS=$(python3 -c "import os; print(min(4, os.cpu_count() or 2))")
echo "✅ Detected $WORKERS workers available"

# 4. Quick sanity run
python3 -m pytest tests/test_codex_plans.py::TestListPlanDocuments -q --tb=no

echo "✅ Pre-flight checks PASSED"
echo ""
echo "Ready to launch Phase 1 Full Sprint (4 lanes)"
```

### Lane 1 Execution (codex_ml)

```bash
#!/bin/bash
echo "[LANE 1] Starting codex_ml gap-fill tests..."
python3 -m pytest tests/test_codex_ml_gap_fill_lane1.py \
    tests/test_codex_ml_gap_fill_lane1_extended.py \
    -v --tb=short -n 4 --dist=loadfile
```

### Lane 2 Execution (services)

```bash
#!/bin/bash
echo "[LANE 2] Starting services gap-fill tests..."
python3 -m pytest tests/test_services_gap_fill.py \
    tests/test_services_error_handling.py \
    -v --tb=short -n 4 --dist=loadfile
```

### Lane 3 Execution (codex)

```bash
#!/bin/bash
echo "[LANE 3] Starting codex gap-fill tests..."
python3 -m pytest tests/test_codex_gap_fill_*.py \
    -v --tb=short -n 4 --dist=loadfile
```

### Lane 4 Execution (mcp)

```bash
#!/bin/bash
echo "[LANE 4] Starting mcp gap-fill tests..."
python3 -m pytest tests/test_mcp_gap_fill_*.py \
    tests/test_mcp_protocol.py \
    -v --tb=short -n 4 --dist=loadfile
```

### Convergence & Measurement (T=12h)

```bash
#!/bin/bash
set -e

echo "=== Phase 1 Convergence & Measurement ==="

# Wait for all lanes to complete (assume parallel execution)
wait

# Run batch scan on all new tests
echo "Running batch scan on 120 new tests..."
python3 scripts/ci/rvs_preflight.py \
    --group quick \
    --workers 4 \
    --report artifacts/phase1_coverage_report.json

# Extract coverage metrics
python3 << 'EOF'
import json

with open('artifacts/phase1_coverage_report.json', 'r') as f:
    report = json.load(f)

print("\n=== PHASE 1 COVERAGE RESULTS ===")
print(f"Total Tests Run: {report.get('test_count', 'N/A')}")
print(f"Pass Rate: {report.get('pass_rate', 'N/A')}%")
print(f"Total Coverage: {report.get('coverage_total', 'N/A')}%")
print(f"Regression Risk: {report.get('regression_detected', 'N/A')}")

if report.get('ok'):
    print("\n✅ PHASE 1 PASSED")
else:
    print("\n❌ PHASE 1 FAILED")
    for err in report.get('errors', [])[:5]:
        print(f"  - {err}")
EOF

# Mutation testing (optional, Phase 2)
echo ""
echo "Running mutation testing (Phase 2 optional)..."
python3 -m mutmut run --tests-dir=tests --paths-to-mutate=src/codex_ml,src/services
```

---

## 📈 Phase 2: Mutation Testing & Assertion Quality

**Timeline:** After Phase 1 convergence (T=12-24h)

| Task | Duration | Deliverable |
|------|----------|---|
| Run mutmut on all new tests | 3h | `artifacts/mutation_report.json` |
| Identify weak assertions | 1h | List of 20–30 weak assertions |
| Add assertion strengtheners | 2h | Enhanced test assertions |
| Re-run mutation testing | 2h | Improved mutation score (≥75%) |

---

## 🎯 Success Definition

**Phase 1 is SUCCESSFUL when:**

1. ✅ All 120 gap-fill tests pass (≥99% success rate)
2. ✅ Coverage increases: 13.8% → ≥25% (target domain)
3. ✅ Batch scan reports zero regressions
4. ✅ `fail_under` stays ≥34% (no decrease)
5. ✅ Mutation score ≥70%
6. ✅ Code review approved (anti-patterns cleared)
7. ✅ Threshold raise approved (34% → 40%)

**Phase 1 is UNSUCCESSFUL if:**
- ❌ Test pass rate <99% (>1 failure, not flaky)
- ❌ Coverage decreases from baseline
- ❌ Batch scan detects regressions
- ❌ `fail_under` would need to lower
- ❌ Mutation score <50% (weak assertions)

---

## 📝 Deliverables Checklist

- [ ] `tests/test_codex_ml_gap_fill_lane1.py` (2,000 LOC)
- [ ] `tests/test_codex_ml_gap_fill_lane1_extended.py` (1,600 LOC)
- [ ] `tests/test_services_gap_fill.py` (1,200 LOC)
- [ ] `tests/test_services_error_handling.py` (1,200 LOC)
- [ ] `tests/test_codex_gap_fill_core.py` (1,800 LOC)
- [ ] `tests/test_codex_gap_fill_config.py` (1,500 LOC)
- [ ] `tests/test_codex_gap_fill_utils.py` (1,500 LOC)
- [ ] `tests/test_mcp_gap_fill_bridge.py` (1,500 LOC)
- [ ] `tests/test_mcp_gap_fill_protocol.py` (2,100 LOC)
- [ ] `tests/test_coverage_integration.py` (800 LOC)
- [ ] `artifacts/phase1_coverage_report.json` (metrics)
- [ ] `artifacts/mutation_report.json` (mutation testing)
- [ ] Phase 1 Completion Report (markdown)
- [ ] Test-cycle Analysis Mermaid Diagram

---

## 🔗 Integration with Automation Agents

### Autonomous Test Healer Agent

Use for:
- Auto-fixing failing tests (up to 3 iterations)
- Detecting P19 shadow import issues
- Adjusting mock/fixture complexity

### CI Testing Agent

Use for:
- Batch scan orchestration
- Batch scan failure triage
- Regression detection

### Mutation Testing Agent

Use for:
- Mutation testing execution & analysis
- Weak assertion detection
- Assertion enhancement recommendations

---

## 📞 Support & Escalation

| Issue | Contact | Escalation |
|-------|---------|---|
| Test framework errors | autonomous-test-healer-agent | ci-emergency-response-agent |
| Coverage regression | unified-coverage-agent | ci-health-alert-agent |
| Batch scan timeouts | ci-testing-agent | workflow-optimization-agent |
| P19 shadow imports | ci-importerror-agent | ci-emergency-response-agent |

---

**Phase 1 Owner:** Unified Coverage Agent + Autonomous Test Healer Agent  
**Date:** 2026-07-16  
**Confidence:** 90% (HIGH)  
**Status:** ✅ Ready for Execution
