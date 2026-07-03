# Phase 7A Lane 1: Prioritized Test Roadmap & Gap-Fill Specifications

**Document ID:** PHASE_7A_L1_TEST_ROADMAP  
**Status:** 🟢 SPECIFICATIONS COMPLETE  
**Generated:** 2026-06-26  
**Target Coverage**: 18% → 24% (+6pp, Phase 7A Quick Wins)

---

## Test Implementation Priorities (Week 1-3)

### Week 1: Critical Foundation (12-15 dev-hours, 60 tests)

#### Day 1-2: Audio/Speech Module (5 hours)
**Module**: `src/services/audio/workflow/transcription_workflow.py` (389 lines)

```yaml
Test File: tests/services/audio/test_transcription_workflow.py
Effort: 5 hours | Tests: 15 | Coverage Target: 50%+ (195 lines)

Tests:
  1. test_transcription_workflow_init()
     - Verify initialization with default config
     - Assert workflow state == READY
     - Check dependencies injected
     Effort: 15 min

  2. test_audio_ingestion_pipeline()
     - Load test audio file
     - Verify ingestion step
     - Check format detection
     Effort: 20 min

  3-4. test_transcription_format_support()
     - MP3, WAV, FLAC, OGG support
     - Parametrized test: @pytest.mark.parametrize('format', [...])
     Effort: 30 min

  5. test_transcription_accuracy_validation()
     - Mock transcriber output
     - Verify accuracy metrics
     - Check confidence scores
     Effort: 20 min

  6. test_concurrent_transcription()
     - Submit 5 concurrent jobs
     - Verify parallel execution
     - Check queue management
     Effort: 25 min

  7-8. test_error_handling()
     - Invalid audio file
     - Timeout handling
     - Resource exhaustion
     Effort: 30 min

  9. test_workflow_state_machine()
     - Verify state transitions (INIT → PROCESSING → DONE)
     - Test invalid transitions rejected
     Effort: 15 min

  10. test_pipeline_cancellation()
     - Start transcription
     - Cancel mid-process
     - Verify cleanup
     Effort: 20 min

  11-15. Integration scenarios (5 tests, 40 min total)
     - E2E with mock audio service
     - Multi-format pipeline
     - Error recovery
     - Resource limits
     - Performance regression

Mocks Required:
  - audio_codec.load_audio() → synthetic PCM data
  - transcriber_backend.transcribe() → mock transcript
  - s3_storage.upload() → mock upload
  - queue.submit() → immediate execution (no real queuing)

Test Fixtures:
  - @pytest.fixture def test_audio_file(tmp_path): → WAV file
  - @pytest.fixture def mock_transcriber(): → Mock backend
  - @pytest.fixture def workflow_instance(): → Initialized workflow
```

**Verification Checklist**:
- [ ] All 15 tests pass locally
- [ ] Coverage report shows 50%+ (≥195 lines covered)
- [ ] No external API calls in test suite
- [ ] Execution time: <30 seconds for full test module

---

#### Day 2-3: Cognitive Brain - Workflow Optimizer (5 hours)
**Module**: `src/codex/cognitive/workflow_optimizer.py` (324 lines)

```yaml
Test File: tests/codex/cognitive/test_workflow_optimizer.py
Effort: 5 hours | Tests: 20 | Coverage Target: 50%+ (162 lines)

Tests:
  1. test_optimizer_initialization()
     - Create optimizer with config
     - Assert config stored correctly
     - Verify cost calculator ready
     Effort: 10 min

  2. test_simple_workflow_optimization()
     - Create DAG: A → B → C
     - Optimize for latency
     - Verify optimization improves latency
     Effort: 20 min

  3. test_complex_workflow_optimization()
     - 10-task DAG with dependencies
     - Multi-objective optimization (latency + cost)
     - Verify Pareto frontier
     Effort: 30 min

  4. test_cost_calculation_accuracy()
     - Known workflow → expected cost
     - Compare against manual calculation
     - Allow ±5% tolerance
     Effort: 20 min

  5. test_constraint_satisfaction()
     - Latency constraint: ≤ 100ms
     - Cost constraint: ≤ $5.00
     - Verify optimized solution satisfies both
     Effort: 20 min

  6. test_optimizer_caching()
     - Optimize same workflow twice
     - Verify cache hit on second run
     - Check response time improvement
     Effort: 15 min

  7-8. test_edge_cases()
     - Empty workflow (0 tasks)
     - Single task
     - Disconnected components
     Effort: 25 min

  9. test_optimization_performance()
     - 50-task workflow
     - Measure optimization time
     - Assert < 1 second
     Effort: 20 min

  10-15. Error handling (6 tests, 45 min)
     - Invalid workflow structure
     - Missing cost data
     - Timeout handling
     - Invalid constraints
     - Resource exhaustion
     - Concurrent optimization conflicts

  16-20. Integration tests (5 tests, 35 min)
     - Optimizer + retriever integration
     - Real-world workflow patterns
     - Performance regression benchmarks

Mocks Required:
  - CostCalculator.estimate() → deterministic costs
  - DAG.build() → in-memory DAG structure
  - PerformanceMetrics.collect() → mock metrics
  - WorkflowValidator.validate() → always pass for valid inputs

Test Fixtures:
  - @pytest.fixture def simple_dag(): → 3-task DAG
  - @pytest.fixture def complex_dag(): → 10-task DAG
  - @pytest.fixture def optimizer(): → Initialized optimizer
  - @pytest.fixture def cost_model(): → Mock cost calculator
```

---

#### Day 3: Utilities - Hash Table (3.5 hours)
**Module**: `src/codex/utils/hash_table.py` (233 lines)

```yaml
Test File: tests/codex/utils/test_hash_table.py
Effort: 3.5 hours | Tests: 18 | Coverage Target: 60%+ (140 lines)

Tests (TDD approach):
  1. test_empty_table_creation()
     - Create HashTable(capacity=16)
     - Assert len(ht) == 0
     - Assert ht.capacity == 16
     Effort: 10 min

  2-4. test_basic_operations()
     - Insert key-value pairs
     - Get values
     - Delete values
     - Parametrized over [10, 100, 1000] items
     Effort: 25 min

  5-6. test_collision_resolution()
     - Force hash collisions (same hash, different keys)
     - Verify both stored correctly
     - Verify retrieval works
     Effort: 20 min

  7-8. test_resizing()
     - Fill table > 75% capacity
     - Assert resize triggered
     - Verify all items still accessible post-resize
     Effort: 20 min

  9. test_overwrite_existing_key()
     - Insert key='x', value=1
     - Insert key='x', value=2
     - Assert ht['x'] == 2 (not 1)
     Effort: 10 min

  10. test_delete_operations()
     - Insert 5 items
     - Delete 3
     - Verify remaining accessible
     - Verify deleted not accessible
     Effort: 15 min

  11-13. test_stress_scenarios()
     - 10,000 random inserts
     - Random deletes
     - Random lookups
     - Verify correctness
     Effort: 30 min

  14-18. Edge cases & error handling (15 min)
     - None keys/values
     - Negative numbers
     - Large numbers (>2^31)
     - Unicode keys
     - Empty string key

Assertion Patterns (Quality):
  ✅ STRONG ASSERTIONS:
     assert ht[key] == expected_value
     assert len(ht) == expected_count
     assert key in ht
     assert ht.capacity_utilization < 0.9

  ❌ WEAK ASSERTIONS (avoid):
     assert ht is not None
     assert result  # too vague
     assert len(ht) > 0  # too loose

Mocks Required:
  - None (core data structure, no external deps)

Test Fixtures:
  - @pytest.fixture def empty_table(): → HashTable(16)
  - @pytest.fixture def filled_table(): → HashTable with 100 items
```

**Expected Metrics After Week 1**:
- ✅ 53 tests written
- ✅ 3 critical modules covered (Audio, Optimizer, Hash Table)
- ✅ Coverage +2.5pp (18% → 20.5%)

---

### Week 2: ML Pipeline & Integration (18-20 dev-hours, 85 tests)

#### Day 4-5: ML CLI Tools (8 hours, 40 tests)

**4a. Hydra Audit CLI** (3.5 hours, 15 tests)
- Module: `src/codex_ml/cli/hydra_audit.py` (259 lines)
- Tests: Command parsing, config validation, report generation, error handling
- Fixtures: Hydra config files, mock audit backends
- Mocks: `hydra.instantiate()`, file I/O

**4b. Repo Map CLI** (2.5 hours, 12 tests)
- Module: `src/codex_ml/cli/repo_map.py` (190 lines)
- Tests: Dependency resolution, caching, performance
- Fixtures: Repository structures
- Mocks: Git operations, file system

**4c. Feature Store CLI** (2 hours, 13 tests)
- Module: `src/codex_ml/cli/feature_store.py` (165 lines)
- Tests: Feature registration, retrieval, versioning
- Fixtures: Feature definitions
- Mocks: Storage backend

#### Day 5-6: Retrieval Optimizer (4 hours, 18 tests)
- Module: `src/codex/cognitive/retrieval_optimizer.py` (256 lines)
- Similar structure to Workflow Optimizer
- Tests: Ranking algorithms, vector similarity, deduplication
- Fixtures: Mock embeddings, search results

#### Day 6-7: Integration Tests (4 hours, 20 tests)
- CLI → Optimizer workflow
- ML Training → FSDP integration
- Plugin System → Registry interaction
- Cross-module data flow validation

**Expected Metrics After Week 2**:
- ✅ 138 total tests (53 + 85)
- ✅ 6+ critical modules covered
- ✅ Coverage +4.5pp (18% → 22.5%)

---

### Week 3: Validation & Low-Coverage Gap-Fill (15-18 dev-hours, 52 tests)

#### Day 8-9: Low-Coverage Gap-Fill (12 hours, 35 tests)

**Priority Low-Coverage Modules** (target: <50% coverage, >500 lines):
1. `src/codex_ml/train_loop.py` (1330L, 7.3%) — 4h, 12 tests
2. `src/codex/cli.py` (1018L, 19.8%) — 3h, 8 tests
3. `src/codex_ml/training/legacy_api.py` (923L, 9.1%) — 3h, 8 tests
4. Other high-value modules (2h, 7 tests)

#### Day 9-10: CI Integration & Validation (3-6 hours, 17 tests)

```yaml
Tasks:
  - Run full test suite in CI
  - Generate coverage report
  - Validate no regressions
  - Documentation/roadmap update
  - Phase 7A completion sign-off
```

**Expected Metrics After Week 3**:
- ✅ 190 total new tests
- ✅ Coverage 24%+ (18% → 24%, +6pp target)
- ✅ Zero regressions
- ✅ Phase 7A complete

---

## Test Architecture & Patterns

### Test File Structure

```
tests/
├── unit/
│   ├── test_hash_table.py          # Data structures
│   ├── test_optimizer.py            # Algorithms
│   └── test_cli_commands.py         # CLI parsing
├── integration/
│   ├── test_workflow_pipeline.py    # E2E workflows
│   ├── test_ml_training_flow.py     # Training pipelines
│   └── test_cross_module_flows.py   # System interactions
├── fixtures/
│   ├── audio_fixtures.py            # Audio mocks
│   ├── dag_fixtures.py              # Workflow DAGs
│   ├── config_fixtures.py           # Configs
│   └── storage_fixtures.py          # Storage mocks
└── conftest.py                      # Pytest configuration
```

### Fixture Patterns (DRY)

```python
# conftest.py - Reusable fixtures
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_external_service():
    """Mock any external API/service call"""
    with patch('module.external_service') as mock:
        mock.call.return_value = {'status': 'success'}
        yield mock

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory"""
    config_dir = tmp_path / 'configs'
    config_dir.mkdir()
    (config_dir / 'test.yaml').write_text('version: 1.0')
    return config_dir

@pytest.fixture(params=[100, 1000, 10000])
def large_dataset(request):
    """Parametrized fixture for stress testing"""
    return generate_dataset(request.param)
```

### Mocking Strategy

```python
# Pattern: Mock external dependencies
from unittest.mock import Mock, MagicMock, patch

def test_with_mocked_service():
    with patch('src.module.external_service') as mock_service:
        mock_service.call.return_value = {'data': 'value'}
        
        result = function_under_test()
        
        assert mock_service.called
        assert result == expected
```

### Assertion Patterns (Quality)

```python
# ✅ STRONG: Specific, comprehensive assertions
def test_optimization():
    result = optimizer.optimize(workflow)
    
    assert result is not None
    assert isinstance(result, OptimizationResult)
    assert result.latency <= workflow.latency  # Validates improvement
    assert result.cost <= max_cost              # Validates constraint
    assert len(result.plan) == len(workflow)    # Validates completeness
    assert all(task.start_time < task.end_time for task in result.plan)

# ❌ WEAK: Vague, insufficient assertions
def test_optimization():
    result = optimizer.optimize(workflow)
    
    assert result is not None  # Too loose
    assert result  # Doesn't validate correctness
```

---

## Test Execution & CI Integration

### Local Test Running

```bash
# Run specific module tests
pytest tests/codex/cognitive/test_workflow_optimizer.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run fast tests only (exclude slow/integration)
pytest tests/ -m "not slow" -n 4  # 4 workers

# Run with failure output
pytest tests/ --tb=short -vv
```

### CI Pipeline Integration

```yaml
# .github/workflows/test.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-test.txt
      
      # Phase 7A tests (primary)
      - run: pytest tests/ -v --cov=src
      
      # Coverage gate
      - run: |
          coverage report --fail-under=24
          coverage report > coverage.txt
      
      # Upload artifacts
      - uses: actions/upload-artifact@v3
        with:
          name: coverage-reports
          path: coverage.*
```

---

## Success Metrics & Validation

### Phase 7A Completion Gates

| Metric | Target | Validation |
|--------|--------|-----------|
| **Line Coverage** | ≥24% | `coverage report` shows 24%+ |
| **New Tests** | ≥190 | `git diff tests/ | grep "^+" | wc -l` |
| **Test Pass Rate** | 100% | `pytest tests/ -v` shows all passing |
| **Regression** | 0 | No reduction in existing coverage |
| **Performance** | <15 min | Full test suite runs < 15 minutes |

### Code Quality Checks

```bash
# Verify test quality
pytest tests/ -v --tb=short

# Check for weak assertions
grep -r "assert.*is not None" tests/ | wc -l  # Flag if > 10%

# Verify mocking completeness
grep -r "patch\|Mock" tests/ | wc -l  # Should be > 100

# Check coverage details
coverage report --include=src/ | grep -E "^src/.*\s0%"  # Should be 0 lines
```

---

## Known Test Challenges & Workarounds

| Challenge | Module | Workaround |
|-----------|--------|-----------|
| Audio library unavailable | Audio tests | Mock `librosa.load()`, use synthetic PCM |
| CUDA not available | ML tests | `CUDA_VISIBLE_DEVICES='' pytest ...` |
| Network calls in code | Integration tests | Mock all HTTP/RPC calls with responses |
| Non-deterministic behavior | Cognitive brain | Use `random.seed(42)`, parametrized tests |
| Large file dependencies | Training tests | Use tiny models, mock file loading |
| Long-running tests | Stress tests | Mark with `@pytest.mark.slow`, exclude from fast suite |

---

## Phase 7B Preview (Main Push, Weeks 4-7)

**Additional Coverage Areas**:
- [ ] Cognitive brain extended (4h, 20 tests)
- [ ] Plugin system boundary (3h, 15 tests)
- [ ] Training pipelines (6h, 35 tests)
- [ ] Error path coverage (5h, 30 tests)
- [ ] E2E workflows (4h, 25 tests)

**Target**: 24% → 27% (+3pp, 285 tests, 70-80 dev-hours)

---

## References & Templates

**Test Templates** (Copy & Adapt):
- [CLI Test Template](# CLI Module Testing Pattern) — above
- [Algorithm Test Template](#Core Algorithm Testing Pattern) — above
- [Integration Test Template](#Integration Testing Pattern) — above

**Related Documents**:
- `.codex/PHASE_7A_LANE_1_COVERAGE_ANALYSIS.md` — Coverage baseline & gap analysis
- `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md` — Repository testing patterns
- `pytest.ini` — Local test configuration

---

**Document Status**: 🟢 READY FOR EXECUTION  
**Phase**: Phase 7A Lane 1 (Quick Wins)  
**Timeline**: 3 weeks, 190 tests, +6pp coverage  
**Generated**: 2026-06-26

