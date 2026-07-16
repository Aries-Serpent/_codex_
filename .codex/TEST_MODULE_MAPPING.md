# Test Module Mapping: Quick-Win Sprint & Phase 1

**Document:** Strategic test allocation across modules  
**Date:** 2026-07-16  
**Scope:** Phase 4 Quick-Win + Phase 1 Full Sprint (128 total tests)  
**Maintainer:** Unified Coverage Agent

---

## 📊 Quick-Reference Summary

```
PHASE 4 QUICK-WIN SPRINT (1-2 hours)
├─ Module: src/codex_plans
│  ├─ Current Coverage: 0%
│  ├─ Target Tests: 8
│  ├─ Test File: tests/test_codex_plans_gap_fill.py (NEW, 500 LOC)
│  └─ Coverage Gain: 30 percentage points
│
└─ TOTAL QUICK-WIN: 8 tests in 1 test file


PHASE 1 FULL SPRINT (24 hours, 4 parallel lanes)
├─ LANE 1 (codex_ml): 30 tests → ~12 hours
├─ LANE 2 (services): 20 tests → ~6 hours
├─ LANE 3 (codex): 40 tests → ~10 hours
├─ LANE 4 (mcp): 30 tests → ~8 hours
└─ TOTAL PHASE 1: 120 tests in 10 test files
```

---

## 🎯 Phase 4 Quick-Win: Module Mapping

### Target Module: `src/codex_plans`

| Metric | Value |
|--------|-------|
| **Python Files** | 2 |
| **Total LOC** | 34 |
| **Public API** | `list_plan_documents(base_dir: Path \| None) -> list[Path]` |
| **Current Coverage** | 0% (0/34 lines) |
| **Target Coverage** | 30% (10+ lines) |
| **Test Gap** | 34 uncovered lines |

### Existing Tests

| File | Tests | LOC | Pass Rate | Issues |
|------|-------|-----|-----------|--------|
| `tests/test_codex_plans.py` | 30 | 398 | 93% | 2 failing |
| `tests/test_codex_plans_api.py` | N/A | 396 | ? | Not analyzed |
| `tests/test_codex_plans_comprehensive.py` | N/A | 461 | ? | Not analyzed |
| `tests/test_codex_plans_extended.py` | N/A | 333 | ? | Not analyzed |
| **TOTAL** | **30+** | **1,588** | **93%** | **2 failures** |

### Gap-Fill Test Plan (8 new tests)

**Test File:** `tests/test_codex_plans_gap_fill.py` (NEW, ~500 LOC)

| Test # | Test Name | Focus Area | Coverage Target | Priority |
|--------|-----------|-----------|---|---|
| 1 | `test_custom_base_dir_with_md_files` | Line 30 (glob filtering) | List filtering | CRITICAL |
| 2 | `test_custom_base_dir_empty_directory` | Line 30 (None glob) | Empty dir handling | CRITICAL |
| 3 | `test_list_plan_documents_sorted_output` | Line 31 (sorted()) | Sorting validation | HIGH |
| 4 | `test_none_base_dir_equals_default` | Line 30 (or operator) | None behavior | CRITICAL |
| 5 | `test_returns_path_objects` | Line 29-31 (return) | Type verification | HIGH |
| 6 | `test_markdown_file_filter` | Line 31 (glob pattern) | File filtering | HIGH |
| 7 | `test_glob_integration` | Lines 30-31 (glob chain) | Integration | MEDIUM |
| 8 | `test_path_resolve_behavior` | Line 30 (resolve) | Path resolution | MEDIUM |

**Expected Coverage Increase:** 30 percentage points (0% → 30%)

---

## 🚀 Phase 1 Full Sprint: Module Mapping (120 tests)

### Module 1: `src/codex_ml` — Machine Learning Core

#### Overview
| Metric | Value |
|--------|-------|
| **Directory** | `src/codex_ml/` |
| **Python Files** | 472 |
| **Total LOC** | 98,314 |
| **Current Coverage** | 10.54% |
| **Target Coverage** | 25% |
| **Test Files (Current)** | 6 |
| **Test File (NEW)** | 2 (Lane 1) |

#### Test File 1: `test_codex_ml_gap_fill_lane1.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestModelInitialization` | 5 | Constructor, device, state dict | 300 | CRITICAL |
| `TestTrainingLoops` | 8 | Forward/backward, gradients | 800 | CRITICAL |
| `TestLossComputation` | 5 | Multi-task, NaN handling | 400 | HIGH |
| **SUBTOTAL** | **18** | | **1,500** | |

**Key Test Patterns:**
```python
# Fixture pattern for model lifecycle
@pytest.fixture
def model():
    torch.manual_seed(42)
    return CodexMLModel(dim=512, device='cpu')

# Training step pattern
def test_training_step_updates_params(model):
    optim = torch.optim.Adam(model.parameters())
    output = model.forward(input_ids=torch.randn(2, 128))
    loss = output.loss
    loss.backward()
    optim.step()
    assert model.training == True

# Device handling (CPU-only, no GPU)
def test_model_device_cpu_only():
    model = CodexMLModel(device='cpu')
    assert str(model.device) == 'cpu'
```

#### Test File 2: `test_codex_ml_gap_fill_lane1_extended.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestCheckpointing` | 4 | Save/load, version compat | 300 | HIGH |
| `TestInferenceMode` | 4 | eval mode, batch processing | 400 | HIGH |
| `TestTorchIntegration` | 4 | Device, dtype, autograd | 400 | MEDIUM |
| **SUBTOTAL** | **12** | | **1,100** | |

**Risk Mitigations:**
- ⚠️ **P19 Shadow Imports:** Use explicit `from transformers import GPT2LMHeadModel` (no wildcards)
- ⚠️ **Stochastic Behaviors:** Set `torch.manual_seed(42)` in every fixture
- ⚠️ **GPU/CUDA:** Force CPU-only in fixtures (`device='cpu'`)

**Lane 1 Total:** 30 tests, ~2,600 LOC

---

### Module 2: `src/services` — API & Integration Services

#### Overview
| Metric | Value |
|--------|-------|
| **Directory** | `src/services/` |
| **Python Files** | 28 |
| **Total LOC** | 5,829 |
| **Current Coverage** | 7.41% |
| **Target Coverage** | 20% |
| **Test Files (Current)** | 3 |
| **Test Files (NEW)** | 2 (Lane 2) |

#### Test File 1: `test_services_gap_fill.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestAPIEndpoints` | 7 | GET/POST/PUT/DELETE | 700 | CRITICAL |
| `TestErrorHandling` | 4 | 404/500, validation | 400 | CRITICAL |
| **SUBTOTAL** | **11** | | **1,100** | |

**Key Test Patterns:**
```python
# Sync API client pattern
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_get_user_endpoint(client):
    response = client.get("/api/users/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"

# Error handling pattern
def test_invalid_input_returns_400(client):
    response = client.post("/api/users", json={"name": ""})
    assert response.status_code == 400
    assert "error" in response.json()
```

#### Test File 2: `test_services_error_handling.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestAuthN_AuthZ` | 4 | Token, roles, JWT | 500 | HIGH |
| `TestDatabaseQueries` | 3 | Query composition, filtering | 400 | HIGH |
| `TestServiceIntegration` | 2 | End-to-end workflows | 400 | MEDIUM |
| **SUBTOTAL** | **9** | | **1,300** | |

**Risk Mitigations:**
- ⚠️ **Async/Await:** Use `@pytest.mark.asyncio` for async endpoints
- ⚠️ **Database Mocking:** Use `unittest.mock.patch` on DB layer
- ⚠️ **HTTP Mocking:** Use `responses` library for external API calls

**Lane 2 Total:** 20 tests, ~2,400 LOC

---

### Module 3: `src/codex` — Core Logic

#### Overview
| Metric | Value |
|--------|-------|
| **Directory** | `src/codex/` |
| **Python Files** | 47 |
| **Total LOC** | 14,693 |
| **Current Coverage** | 20.08% |
| **Target Coverage** | 35% |
| **Test Files (Current)** | 28 |
| **Test Files (NEW)** | 3 (Lane 3) |

#### Test File 1: `test_codex_gap_fill_core.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestConfiguration` | 8 | YAML parsing, validation | 800 | CRITICAL |
| `TestStateMachine` | 6 | Transitions, invalid moves | 700 | CRITICAL |
| **SUBTOTAL** | **14** | | **1,500** | |

**Key Test Patterns:**
```python
# YAML configuration pattern
@pytest.mark.parametrize("yaml_str,expected", [
    ("key: value", "value"),
    ("key: 123", 123),
    ("key: [1, 2, 3]", [1, 2, 3]),
])
def test_config_parsing_variants(yaml_str, expected):
    cfg = Config.from_yaml(yaml_str)
    assert cfg.key == expected

# State machine pattern
def test_valid_state_transition():
    sm = StateMachine(initial_state="IDLE")
    sm.trigger("start")
    assert sm.state == "RUNNING"

def test_invalid_transition_raises():
    sm = StateMachine(initial_state="IDLE")
    with pytest.raises(InvalidStateTransition):
        sm.trigger("stop")  # IDLE->STOP is invalid
```

#### Test File 2: `test_codex_gap_fill_config.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestCallbacks` | 8 | Hook registration, ordering | 800 | HIGH |
| `TestEventHandling` | 5 | Exception propagation | 500 | HIGH |
| **SUBTOTAL** | **13** | | **1,300** | |

**Key Test Patterns:**
```python
# Callback registration pattern
def test_callback_execution_order():
    results = []
    sm = StateMachine()
    sm.on_state_change(lambda s: results.append(f"enter_{s}"))
    
    sm.trigger("start")
    assert results == ["enter_RUNNING"]

# Exception handling in callbacks
def test_callback_exception_propagates():
    sm = StateMachine()
    
    def bad_callback(state):
        raise ValueError("Intentional error")
    
    sm.on_state_change(bad_callback)
    
    with pytest.raises(ValueError):
        sm.trigger("start")
```

#### Test File 3: `test_codex_gap_fill_utils.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestUtilities` | 7 | String, path, transformation | 700 | MEDIUM |
| `TestIntegration` | 6 | Config→SM→Callbacks | 800 | HIGH |
| **SUBTOTAL** | **13** | | **1,500** | |

**Risk Mitigations:**
- ⚠️ **YAML Edge Cases:** Use `pytest.mark.parametrize` for variant testing
- ⚠️ **State Machine Deadlocks:** Add timeout fixtures (`pytest-timeout`)
- ⚠️ **Callback Async:** Support both sync & async callbacks (use `asyncio.run()`)

**Lane 3 Total:** 40 tests, ~4,300 LOC

---

### Module 4: `src/mcp` — Model Context Protocol

#### Overview
| Metric | Value |
|--------|-------|
| **Directory** | `src/mcp/` |
| **Python Files** | 60 |
| **Total LOC** | 6,430 |
| **Current Coverage** | 16.67% |
| **Target Coverage** | 30% |
| **Test Files (Current)** | 3 |
| **Test Files (NEW)** | 2 (Lane 4) |

#### Test File 1: `test_mcp_gap_fill_bridge.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestMessageSerialization` | 8 | Encode/decode, schema | 800 | CRITICAL |
| `TestIPCBridge` | 7 | Socket communication | 900 | CRITICAL |
| **SUBTOTAL** | **15** | | **1,700** | |

**Key Test Patterns:**
```python
# Message serialization pattern
def test_message_roundtrip():
    msg = MCPMessage(
        id=42,
        method="invoke",
        params={"tool": "search"}
    )
    serialized = msg.serialize()
    deserialized = MCPMessage.deserialize(serialized)
    assert deserialized == msg

# Socket fixture with cleanup
@pytest.fixture
def mock_socket(mocker):
    sock = mocker.MagicMock()
    mocker.patch("socket.socket", return_value=sock)
    yield sock

def test_bridge_send_receive(mock_socket):
    bridge = MCPBridge(socket_path="/tmp/test.sock")
    bridge.send(MCPMessage(id=1, method="test"))
    
    # Verify socket.send was called
    assert mock_socket.send.called
```

#### Test File 2: `test_mcp_gap_fill_protocol.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestResourceManagement` | 8 | Allocation, cleanup | 900 | HIGH |
| `TestErrorRecovery` | 5 | Reconnection, backoff | 600 | HIGH |
| `TestProtocolIntegration` | 2 | End-to-end sync | 400 | MEDIUM |
| **SUBTOTAL** | **15** | | **1,900** | |

**Key Test Patterns:**
```python
# Resource cleanup pattern
def test_resource_cleanup_on_error():
    bridge = MCPBridge()
    bridge.connect()
    
    try:
        raise RuntimeError("Simulated error")
    except RuntimeError:
        bridge.close()  # cleanup
    
    assert bridge.get_resource_count() == 0

# Reconnection with exponential backoff
def test_exponential_backoff_timing(mocker):
    bridge = MCPBridge()
    mock_time = mocker.patch("time.sleep")
    
    for attempt in range(3):
        expected_delay = 2 ** attempt  # 1, 2, 4 seconds
        bridge._backoff_and_retry(attempt)
        mock_time.assert_called_with(expected_delay)
```

**Risk Mitigations:**
- ⚠️ **Socket Mocking Complexity:** Use `unittest.mock.MagicMock` with side effects
- ⚠️ **Multi-Process Synchronization:** Use `threading.Event` + monkeypatch
- ⚠️ **Timing-Dependent Behaviors:** Use `freezegun` for time mocking

**Lane 4 Total:** 30 tests, ~3,600 LOC

---

### Additional Integration Test File

#### Test File: `test_coverage_integration.py`

| Test Class | Count | Focus | LOC | Priority |
|-----------|-------|-------|-----|---|
| `TestCrossModuleWorkflows` | 5 | codex_ml→services→codex | 400 | MEDIUM |
| `TestMCPIntegration` | 3 | mcp bridge with services | 300 | MEDIUM |
| `TestEndToEndScenarios` | 2 | Full user workflows | 200 | LOW |
| **TOTAL** | **10** | | **900** | |

**Purpose:** Validate that gap-fill tests don't break cross-module interactions

---

## 📈 Consolidated Test File Inventory

### Quick-Win Sprint (8 tests, 500 LOC)

```
tests/test_codex_plans_gap_fill.py              500 LOC    8 tests    PHASE 4
```

### Phase 1 Full Sprint (120 tests, 18,800 LOC)

```
LANE 1 (codex_ml)
├─ test_codex_ml_gap_fill_lane1.py             1,500 LOC   18 tests   LANE 1
└─ test_codex_ml_gap_fill_lane1_extended.py    1,100 LOC   12 tests   LANE 1

LANE 2 (services)
├─ test_services_gap_fill.py                   1,100 LOC   11 tests   LANE 2
└─ test_services_error_handling.py             1,300 LOC    9 tests   LANE 2

LANE 3 (codex)
├─ test_codex_gap_fill_core.py                 1,500 LOC   14 tests   LANE 3
├─ test_codex_gap_fill_config.py               1,300 LOC   13 tests   LANE 3
└─ test_codex_gap_fill_utils.py                1,500 LOC   13 tests   LANE 3

LANE 4 (mcp)
├─ test_mcp_gap_fill_bridge.py                 1,700 LOC   15 tests   LANE 4
└─ test_mcp_gap_fill_protocol.py               1,900 LOC   15 tests   LANE 4

INTEGRATION
└─ test_coverage_integration.py                  900 LOC   10 tests   SHARED

TOTAL PHASE 1:                                 18,800 LOC  120 tests
```

---

## 🔄 Test Execution Sequence

### Quick-Win Sprint (Sequential, T=0-2h)

```
T=0:00  → Run test_codex_plans_gap_fill.py (8 tests)
T=0:15  → Fix failing tests in test_codex_plans.py (2 failures)
T=0:30  → Re-run test_codex_plans*.py (validate pass rate ≥93%)
T=1:00  → Coverage measurement & gap analysis
T=1:30  → Commit gap-fill tests to feature branch
T=2:00  → Quick-Win Sprint COMPLETE ✅
```

### Phase 1 Full Sprint (Parallel, T=0-12h)

```
T=0:00  ├─ LANE 1: Start test_codex_ml_gap_fill_lane1*.py (18+12 tests)
        ├─ LANE 2: Start test_services_gap_fill*.py (11+9 tests)
        ├─ LANE 3: Start test_codex_gap_fill_*.py (14+13+13 tests)
        └─ LANE 4: Start test_mcp_gap_fill_*.py (15+15 tests)

T=4:00  ├─ Checkpoint: Batch scan report (20% of tests complete)
        └─ Status: All lanes green or yellow

T=8:00  ├─ Checkpoint: Batch scan report (60% of tests complete)
        └─ Status: All lanes ready for convergence

T=12:00 ├─ ALL LANES CONVERGE
        ├─ Run test_coverage_integration.py (10 tests)
        ├─ Generate combined coverage report
        ├─ Check threshold progression (34% → ≥40%)
        └─ Phase 1 MEASUREMENT COMPLETE ✅

T=12:00-24:00  → Optional mutation testing (Phase 2)
T=24:00        → Final approval & threshold raise (if eligible)
```

---

## 📊 Coverage Target Validation

### Pre-Sprint Baseline

```
src/codex_plans    0.00% → TARGET 30% (QUICK-WIN)
src/codex_ml      10.54% → TARGET 25% (PHASE 1)
src/services       7.41% → TARGET 20% (PHASE 1)
src/codex         20.08% → TARGET 35% (PHASE 1)
src/mcp           16.67% → TARGET 30% (PHASE 1)
─────────────────────────────────────────────────
WEIGHTED AVERAGE  13.78% → TARGET 27% (PHASE 1)
```

### Success Thresholds

| Module | Minimum Pass | Preferred | Stretch |
|--------|---|---|---|
| codex_plans (quick-win) | 25% | 30% | 35% |
| codex_ml | 20% | 25% | 30% |
| services | 15% | 20% | 25% |
| codex | 30% | 35% | 40% |
| mcp | 25% | 30% | 35% |

---

## ✅ Validation Checklist

- [ ] All 8 quick-win tests written & passing
- [ ] All 120 phase 1 tests written & passing
- [ ] Coverage targets met for each module
- [ ] Batch scan passes all 4 lanes
- [ ] No regression in `fail_under` (≥34%)
- [ ] Code review approved (no anti-patterns)
- [ ] Mutation score ≥70%
- [ ] Test-cycle analysis generated
- [ ] Threshold raise approved (34% → 40%)

---

**Document Owner:** Unified Coverage Agent  
**Last Updated:** 2026-07-16  
**Status:** ✅ Ready for Distribution
