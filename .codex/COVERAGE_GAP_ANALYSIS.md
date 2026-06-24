# PRODUCTION READINESS PHASE 2: COVERAGE GAP ANALYSIS
**Session**: production-readiness-phase1-3-orchestration  
**Turn**: 15–20  
**Date**: 2024-06-13  
**Status**: IN PROGRESS

---

## 1. BASELINE ASSESSMENT

### Current Coverage State
- **Overall Coverage**: 10.7% (statement coverage, src/codex_ml)
- **Fail-Under Threshold**: 35% (pyproject.toml)
- **Target This Phase**: 12%+ (1.3 percentage point gain)
- **Focus Modules**:
  - `src/codex_ml/training/`
  - `src/codex_ml/checkpointing/`
  - `src/codex_ml/continuous_learning/`

### Coverage Configuration (pyproject.toml)
```toml
[tool.coverage.run]
branch = true
source = ["src", "agents", "training"]

[tool.coverage.report]
fail_under = 35
skip_covered = false
precision = 2
```

---

## 2. HIGH-PRIORITY GAPS IDENTIFIED

### 2.1 Training Module (src/codex_ml/training/)
**Total Lines**: ~6,500 LOC across 28 files  
**Current Coverage**: ~5% (estimated)

#### Zero/Near-Zero Coverage Files (Priority 1)
| Module | Lines | Critical? | Reason | Test Strategy |
|--------|-------|-----------|--------|--------------|
| `training/callbacks.py` | 44 | Medium | Event integration lifecycle | Unit: callback registration, teardown |
| `training/determinism.py` | 159 | High | RNG seed control, reproducibility | Unit: seed setting, checkpoint restore |
| `training/device_strategy.py` | 285 | High | Device mapping, multi-GPU orchestration | Unit: device config, edge cases |
| `training/distributed_setup.py` | 300 | High | DDP initialization, FSDP config | Unit: setup validation, error paths |
| `training/event_integration.py` | 185 | High | Event emission, callback integration | Integration: event flow, handler cleanup |
| `training/continuous_learning.py` | 318 | Medium | Incremental learning, curriculum | Unit: curriculum updates, edge cases |
| `training/early_stopping.py` | 479 | High | Stop condition evaluation, patience | Unit: improvement detection, boundary conditions |
| `training/engine.py` | 230 | High | Training loop orchestration | Integration: full training cycle, error recovery |
| `training/ray_distributed.py` | ~250 | High | Ray cluster setup, fault tolerance | Unit: ray config validation, error handling |

#### Error Path Coverage Gaps
- **Device fallback logic**: No tests for CPU fallback when CUDA unavailable
- **OOM handling**: No tests for out-of-memory error recovery
- **Checkpoint corruption**: No tests for corrupted checkpoint detection
- **Distributed timeout**: No tests for multi-node timeout scenarios

---

### 2.2 Checkpointing Module (src/codex_ml/checkpointing/)
**Total Lines**: ~931 LOC across 8 files  
**Current Coverage**: ~2% (estimated)

#### Zero/Near-Zero Coverage Files (Priority 1)
| Module | Lines | Critical? | Reason | Test Strategy |
|--------|-------|-----------|--------|--------------|
| `checkpointing/best_k_retention.py` | 259 | High | Top-K checkpoint persistence | Unit: retention policy, cleanup, ordering |
| `checkpointing/atomic_io.py` | 81 | High | Atomic write/read, corruption prevention | Unit: partial write recovery, race conditions |
| `checkpointing/checkpoint_core.py` | 158 | High | Core checkpoint I/O | Unit: serialization, deserialization, versioning |
| `checkpointing/schema_v2.py` | 174 | High | Schema migration, backward compat | Unit: schema validation, version detection |

#### Resume Path Coverage Gaps
- **Checkpoint resume after pause**: No integration test
- **Schema migration (v1 → v2)**: No upgrade path test
- **Partial checkpoint recovery**: No test for corrupted state recovery
- **State dict alignment**: No test for size/shape mismatch detection

---

### 2.3 Continuous Learning Module (src/codex_ml/continuous_learning/)
**Total Lines**: ~600 LOC across 4 files  
**Current Coverage**: ~1% (estimated)

#### Zero/Near-Zero Coverage Files (Priority 2)
| Module | Lines | Critical? | Reason | Test Strategy |
|--------|-------|-----------|--------|--------------|
| `continuous_learning/trigger.py` | ~120 | Medium | Trigger evaluation, scheduling | Unit: trigger conditions, edge cases |
| `continuous_learning/eval_gate.py` | ~140 | Medium | Quality gate enforcement | Unit: gate criteria, threshold validation |
| `continuous_learning/pipeline.py` | ~200 | High | Full CL pipeline orchestration | Integration: end-to-end CL workflow |

#### Edge Cases Not Covered
- **Trigger misfires**: No test for false-positive triggers
- **Quality gate bypass**: No test for gate enforcement logic
- **Pipeline state recovery**: No test for mid-pipeline failure recovery

---

## 3. TOKENIZATION EDGE CASES (Bonus Coverage)

### Module: src/codex_ml/tokenization/
**Lines**: ~400 LOC  
**Current Coverage**: ~3%

#### Uncovered Edge Cases
| Edge Case | Risk | Test Type |
|-----------|------|-----------|
| Empty sequence tokenization | Data corruption | Unit | <!-- pragma: allowlist secret -->
| Very long sequence (>2M tokens) | OOM/truncation | Unit | <!-- pragma: allowlist secret -->
| Special character handling (BOM, null bytes) | Silent failures | Unit |
| Token ID collisions in custom vocabularies | Index errors | Unit | <!-- pragma: allowlist secret -->
| Encoding format mismatch (UTF-8 vs UTF-16) | Data loss | Unit |

---

## 4. TEST ANTI-PATTERNS TO ADDRESS

### Current Issues in Codebase
1. **Overly broad exception handlers**
   ```python
   # ❌ BAD: Catches all exceptions
   try:
       result = checkpoint_load(path)
   except:
       return None
   ```
   → Tests should verify specific exception types

2. **Missing cleanup in fixtures**
   - Temporary directories not deleted
   - Mock patches not reverted
   - File handles left open

3. **Tests without error messages**
   ```python
   # ❌ BAD: No context on failure
   assert result == expected
   ```
   → All assertions should include messages

4. **Flaky sleep-based tests**
   - Tests using fixed `time.sleep()` durations
   - Race condition susceptibility
   → Replace with deterministic mocking

---

## 5. PRIORITIZED TEST TARGETS

### Phase A (Turns 21–26): Foundation Tests (60% of effort)
**Goal**: 10.7% → 11.0% (+0.3%)

1. **Checkpoint Resume Logic** (testable without heavy deps)
   - Test: atomic I/O success path
   - Test: schema v2 validation
   - Test: backward compatibility with v1 checkpoints
   - Files: `tests/unit/test_checkpoint_core_resume.py`

2. **Training Callbacks** (event system baseline)
   - Test: callback registration/deregistration
   - Test: event emission on milestone
   - Test: cleanup after training end
   - Files: `tests/unit/test_training_callbacks.py`

3. **Tokenization Edge Cases** (high-value, low-dependency)
   - Test: empty sequence handling
   - Test: long sequence truncation
   - Test: special character preservation
   - Files: `tests/unit/test_tokenization_edges.py`

### Phase B (Turns 27–32): Integration Tests (40% of effort)
**Goal**: 11.0% → 12.0%+ (+1.0%)

1. **Device Strategy Integration**
   - Test: device fallback logic
   - Test: multi-GPU detection
   - Files: `tests/integration/test_device_strategy_fallback.py`

2. **Event Integration End-to-End**
   - Test: event flow during training simulation
   - Test: callback chain execution
   - Files: `tests/integration/test_event_integration_e2e.py`

3. **Checkpoint Restore with Resume**
   - Test: full resume workflow
   - Test: partial checkpoint recovery
   - Files: `tests/integration/test_checkpoint_resume_e2e.py`

---

## 6. TEST PATTERN TEMPLATES (Use Existing Patterns)

### Unit Test Template (from test_checkpointing.py)
```python
class TestCheckpointCore:
    """Test core checkpoint I/O operations."""

    def setup_method(self):
        """Prepare test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.checkpoint_path = Path(self.tmpdir) / "checkpoint.pt"

    def teardown_method(self):
        """Clean up test artifacts."""
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_checkpoint_save_creates_file(self):
        """Test that save operation creates file."""
        # Arrange
        test_state = {"model": {"weight": [1.0, 2.0]}}

        # Act
        save_checkpoint(test_state, self.checkpoint_path)

        # Assert
        assert self.checkpoint_path.exists(), \
            f"Checkpoint not created at {self.checkpoint_path}"
```

### Integration Test Template (from test_training_integration_flags.py)
```python
class TestEventIntegrationE2E:
    """Test event integration across training cycle."""

    def test_event_flow_during_training(self, mocker):
        """Verify events emitted during training."""
        # Arrange
        events_fired = []

        def capture_event(event):
            events_fired.append(event)

        mocker.patch("codex_ml.training.event_integration.emit_event",
                     side_effect=capture_event)

        # Act
        run_training_simulation(max_steps=5)

        # Assert
        assert "training_start" in events_fired, \
            "training_start event not fired"
        assert "training_end" in events_fired, \
            "training_end event not fired"
```

---

## 7. DEPENDENCY MANAGEMENT

### Safe to Test Without Heavy Setup
- ✅ `checkpointing/` modules (file I/O only)
- ✅ `tokenization/` edges (data processing)
- ✅ `callbacks.py` (registration logic)
- ✅ `device_strategy.py` (config validation)

### Requires Minimal Mocking
- ⚠️ `event_integration.py` (mock event system)
- ⚠️ `determinism.py` (mock RNG state)
- ⚠️ `early_stopping.py` (mock metric tracking)

### Complex Dependencies (Schedule for Phase 3)
- ❌ `legacy_api.py` (1,663 LOC, heavy dependencies)
- ❌ `fsdp_wrapper.py` (FSDP initialization)
- ❌ `functional_training.py` (full training loop)
- ❌ `ray_distributed.py` (Ray cluster setup)

---

## 8. SUCCESS CRITERIA

### Coverage Progression
| Checkpoint | Target | Target Date | Status |
|-----------|--------|-------------|--------|
| Current (T15) | 10.7% | — | ✅ Baseline |
| After Phase A (T26) | 11.0% | Turn 26 | Pending |
| After Phase B (T32) | 12.0% | Turn 32 | Pending |
| Final Check (T40) | 12.0%+ | Turn 40 | Pending |

### Test Quality Gates
- ✅ All new tests include explicit assertion messages
- ✅ No catch-all `except:` statements in tests
- ✅ All fixtures include cleanup (teardown_method or context manager)
- ✅ No dependency on hardcoded file paths (/tmp/*, /root/*)
- ✅ No sleep-based synchronization (mock time instead)

### Hygiene Score Calculation
```
Score = (100 - violations) / 100
  where violations = catch-all_count + missing_cleanup_count
                     + missing_assertions_count + hardcoded_paths_count
```
Target: 100% (Score = 1.0)

---

## 9. DELIVERABLES ROADMAP

| Turn | Deliverable | Owner |
|------|-------------|-------|
| 20 | This document: COVERAGE_GAP_ANALYSIS.md | Current |
| 26 | Phase A tests (6 files, ~10 tests) | Current |
| 30 | Coverage progression report (11%+) | Current |
| 32 | Phase B tests (3 files, ~8 tests) | Current |
| 40 | Final coverage report (12%+) | Current |
| 42 | COVERAGE_PHASE2_COMPLETE.md | Current |

---

## 10. RISK MITIGATION

### Potential Blockers
| Risk | Mitigation |
|------|-----------|
| Test dependencies unavailable | Use mocks; fall back to Phase 3 |
| Coverage tool timeout | Use `--changed-only` flag; batch by module |
| Import errors in target modules | Document missing deps; escalate if blocking |
| Flaky tests after commit | Add retry logic; investigate race conditions |

---

## 11. DISCUSSION COORDINATION

**GitHub Discussion**: #4872  
**Progress Posts**:
- Turn 20: Gap analysis complete, targets identified ✅ (This doc)
- Turn 26: Phase A tests written, coverage snapshot
- Turn 32: Phase B tests written, coverage at 12%+
- Turn 40: Final metrics and hygiene report
- Turn 42: Session complete, deliverables summary

---

**Next Steps**: Proceed to Turn 21 (Test Generation Phase A)
