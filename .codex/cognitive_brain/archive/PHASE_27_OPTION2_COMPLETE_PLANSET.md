# Phase 27.1 Option 2: Complete Autonomous PlanSet for 39 High-Quality Tests

**Status**: Complete autonomous execution strategy  
**Scope**: 39 tests (25 CLI + 14 Training)  
**Timeline**: 6-8 hours focused development  
**Automation**: 100%  
**Policy**: AI Agency Policy v1.1.0 compliant

---

## 📊 Realistic Assessment

### Complexity Analysis

**CLI Tests (25 tests)**:
- **Difficulty**: High
- **Dependencies**: typer.testing.CliRunner, signal mocking, I/O redirection
- **Mock Objects Required**: ~30 mocks
- **Average Assertions per Test**: 4-5
- **Estimated Time**: 3-4 hours

**Training Tests (14 tests)**:
- **Difficulty**: Very High
- **Dependencies**: PyTorch, tensor operations, gradient simulation
- **Mock Objects Required**: ~20 mocks
- **Average Assertions per Test**: 3-4
- **Estimated Time**: 2-3 hours

**Validation & Quality** (1 hour):
- Test execution validation
- Coverage analysis
- Code quality checks
- Documentation updates

---

## 🎯 Complete Execution Plan

### Phase A: CLI Edge Case Tests (25 tests)

#### Sub-batch A1: Command Execution Edge Cases (8 tests)
**File**: `tests/cli/test_cli_edge_cases_phase26.py`  
**Duration**: 60-75 minutes

**Tests to Implement**:
1. `test_cli_invalid_command_execution`
   - Mock: `subprocess.run`
   - Assertions: Exit code, error message, stderr content

2. `test_cli_command_with_special_characters`
   - Mock: Command parser
   - Assertions: Escape handling, injection prevention

3. `test_cli_command_timeout`
   - Mock: `time.time`, `subprocess.Popen`
   - Assertions: Timeout triggers, cleanup, error message

4. `test_cli_command_with_env_variables`
   - Mock: `os.environ`
   - Assertions: Variable expansion, precedence

5. `test_cli_command_with_stdin_redirect`
   - Mock: `sys.stdin`
   - Assertions: Input reading, EOF handling

6. `test_cli_command_with_stdout_redirect`
   - Mock: `sys.stdout`
   - Assertions: Output capture, buffering

7. `test_cli_command_with_stderr_redirect`
   - Mock: `sys.stderr`
   - Assertions: Error capture, separation

8. `test_cli_command_chain_execution`
   - Mock: Multiple command runners
   - Assertions: Pipeline, error propagation

**Fixture Template**:
```python
@pytest.fixture
def cli_runner():
    """Typer CLI test runner with mocked environment."""
    from typer.testing import CliRunner
    runner = CliRunner(mix_stderr=False)
    return runner

@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess for command execution tests."""
    return mocker.patch('subprocess.run')
```

#### Sub-batch A2: Signal Handling (6 tests)
**Duration**: 45-60 minutes

**Tests to Implement**:
1. `test_cli_sigint_handling`
   - Mock: `signal.signal`, `os.kill`
   - Assertions: Graceful shutdown, cleanup

2. `test_cli_sigterm_handling`
   - Mock: `signal.signal`
   - Assertions: Termination, resource release

3. `test_cli_sighup_handling`
   - Mock: `signal.signal`
   - Assertions: Reload behavior

4. `test_cli_signal_during_subprocess`
   - Mock: `subprocess.Popen`, `signal`
   - Assertions: Child process termination

5. `test_cli_signal_race_condition`
   - Mock: `threading.Event`, `signal`
   - Assertions: Thread safety, no deadlock

6. `test_cli_multiple_signals_sequence`
   - Mock: `signal.signal`
   - Assertions: Signal queuing, order

**Fixture Template**:
```python
@pytest.fixture
def mock_signal_handler(mocker):
    """Mock signal handling for CLI tests."""
    original_signal = signal.signal
    mock = mocker.patch('signal.signal')
    mock.side_effect = lambda sig, handler: original_signal(sig, handler)
    return mock
```

#### Sub-batch A3: I/O Operations (6 tests)
**Duration**: 45-60 minutes

**Tests to Implement**:
1. `test_cli_large_input_handling`
   - Mock: `sys.stdin`
   - Assertions: Streaming, memory usage

2. `test_cli_binary_input_handling`
   - Mock: `sys.stdin.buffer`
   - Assertions: Binary mode, encoding

3. `test_cli_output_to_closed_pipe`
   - Mock: `sys.stdout`
   - Assertions: BrokenPipeError handling

4. `test_cli_input_from_closed_pipe`
   - Mock: `sys.stdin`
   - Assertions: EOF handling

5. `test_cli_concurrent_io_operations`
   - Mock: `threading.Lock`, I/O streams
   - Assertions: Thread safety, no corruption

6. `test_cli_io_encoding_errors`
   - Mock: Encoded streams
   - Assertions: Error handling, fallback

#### Sub-batch A4: CLI Edge Cases (5 tests)
**Duration**: 30-45 minutes

**Tests to Implement**:
1. `test_cli_extremely_long_arguments`
   - Assertions: Argument truncation, validation

2. `test_cli_unicode_arguments`
   - Assertions: Unicode handling, normalization

3. `test_cli_path_traversal_prevention`
   - Assertions: Security, sanitization

4. `test_cli_resource_cleanup_on_error`
   - Assertions: No leaks, proper cleanup

5. `test_cli_concurrent_command_execution`
   - Assertions: Isolation, no interference

---

### Phase B: Training Pipeline Tests (14 tests)

#### Sub-batch B1: Dataset Edge Cases (5 tests)
**File**: `tests/training/test_training_edge_cases_phase26.py`  
**Duration**: 45-60 minutes

**Tests to Implement**:
1. `test_training_empty_dataset_handling`
   - Mock: `torch.utils.data.DataLoader`
   - Assertions: Error detection, graceful handling

2. `test_training_single_sample_batch`
   - Mock: Dataset, batch sampler
   - Assertions: Batch norm behavior, statistics

3. `test_training_uneven_batch_sizes`
   - Mock: DataLoader with drop_last=False
   - Assertions: Padding, masking, loss calculation

4. `test_training_corrupted_data_samples`
   - Mock: Dataset with bad samples
   - Assertions: Error handling, skipping, logging

5. `test_training_extremely_large_batch`
   - Mock: Memory allocator
   - Assertions: OOM prevention, chunking

**Fixture Template**:
```python
@pytest.fixture
def mock_dataloader(mocker):
    """Mock PyTorch DataLoader for training tests."""
    import torch
    mock = mocker.patch('torch.utils.data.DataLoader')
    mock.return_value = iter([torch.randn(32, 10)])
    return mock

@pytest.fixture
def mock_model(mocker):
    """Mock PyTorch model for training tests."""
    import torch.nn as nn
    model = mocker.MagicMock(spec=nn.Module)
    model.parameters.return_value = [torch.randn(10, 10, requires_grad=True)]
    return model
```

#### Sub-batch B2: Loss & Gradient Issues (5 tests)
**Duration**: 60-75 minutes

**Tests to Implement**:
1. `test_training_nan_loss_detection`
   - Mock: Loss function returning NaN
   - Assertions: Early stopping, logging, rollback

2. `test_training_inf_loss_detection`
   - Mock: Loss function returning Inf
   - Assertions: Clipping, warning, recovery

3. `test_training_gradient_explosion`
   - Mock: Gradients with large values
   - Assertions: Gradient clipping, norm calculation

4. `test_training_gradient_vanishing`
   - Mock: Gradients near zero
   - Assertions: Detection, warning, strategy

5. `test_training_gradient_accumulation_edge`
   - Mock: Accumulation steps
   - Assertions: Correct averaging, update timing

**Fixture Template**:
```python
@pytest.fixture
def mock_loss_function(mocker):
    """Mock loss function for gradient tests."""
    import torch
    def loss_fn(pred, target):
        return torch.tensor(1.0, requires_grad=True)
    return mocker.MagicMock(side_effect=loss_fn)

@pytest.fixture
def mock_optimizer(mocker):
    """Mock optimizer for training tests."""
    import torch.optim as optim
    mock = mocker.MagicMock(spec=optim.Adam)
    return mock
```

#### Sub-batch B3: Resource Constraints (4 tests)
**Duration**: 45-60 minutes

**Tests to Implement**:
1. `test_training_oom_handling`
   - Mock: `torch.cuda.OutOfMemoryError`
   - Assertions: Batch size reduction, recovery

2. `test_training_disk_space_full`
   - Mock: `OSError` on checkpoint save
   - Assertions: Error handling, cleanup

3. `test_training_gpu_memory_fragmentation`
   - Mock: Memory allocator
   - Assertions: Garbage collection, defragmentation

4. `test_training_checkpoint_corruption`
   - Mock: Corrupted checkpoint file
   - Assertions: Validation, fallback, recovery

---

## 🔧 Implementation Guidelines

### Mocking Best Practices

**1. Use pytest-mock for cleaner mocks**:
```python
def test_example(mocker):
    mock_obj = mocker.patch('module.function')
    mock_obj.return_value = expected_value
```

**2. Use context managers for temporary mocks**:
```python
with patch('module.function') as mock:
    mock.return_value = value
    # Test code
```

**3. Mock at the right level**:
- Mock external dependencies (subprocess, network, file I/O)
- Don't mock internal logic (defeats purpose of testing)
- Mock expensive operations (GPU, large computations)

### Assertion Patterns

**1. Multiple assertions per test**:
```python
assert result.exit_code == 0
assert "expected" in result.output
assert result.stderr == ""
```

**2. Use pytest.raises for exceptions**:
```python
with pytest.raises(ValueError, match="expected message"):
    function_under_test()
```

**3. Use pytest.approx for floats**:
```python
assert loss_value == pytest.approx(1.0, abs=1e-6)
```

---

## 📋 Autonomous Execution Prompts

### Prompt 1: CLI Tests Sub-batch A1
```markdown
@copilot Implement CLI command execution tests (Sub-batch A1, 8 tests)

**File**: tests/cli/test_cli_edge_cases_phase26.py
**Tests**:
1. test_cli_invalid_command_execution
2. test_cli_command_with_special_characters
3. test_cli_command_timeout
4. test_cli_command_with_env_variables
5. test_cli_command_with_stdin_redirect
6. test_cli_command_with_stdout_redirect
7. test_cli_command_with_stderr_redirect
8. test_cli_command_chain_execution

**Requirements**:
- Use typer.testing.CliRunner
- Mock subprocess.run, sys.stdin/out/err
- 4-5 assertions per test
- Follow existing patterns in tests/cli/

**Validation**: Run pytest tests/cli/test_cli_edge_cases_phase26.py::test_cli_* -v
```

### Prompt 2: CLI Tests Sub-batch A2
```markdown
@copilot Implement CLI signal handling tests (Sub-batch A2, 6 tests)

**Tests**:
1. test_cli_sigint_handling
2. test_cli_sigterm_handling  
3. test_cli_sighup_handling
4. test_cli_signal_during_subprocess
5. test_cli_signal_race_condition
6. test_cli_multiple_signals_sequence

**Requirements**:
- Mock signal.signal, os.kill
- Test graceful shutdown, cleanup
- Thread safety assertions
- 3-4 assertions per test

**Validation**: Run tests and check signal handling behavior
```

### Prompt 3: Training Tests Sub-batch B1
```markdown
@copilot Implement training dataset edge case tests (Sub-batch B1, 5 tests)

**File**: tests/training/test_training_edge_cases_phase26.py
**Tests**:
1. test_training_empty_dataset_handling
2. test_training_single_sample_batch
3. test_training_uneven_batch_sizes
4. test_training_corrupted_data_samples
5. test_training_extremely_large_batch

**Requirements**:
- Mock torch.utils.data.DataLoader
- Use PyTorch fixtures
- Test error handling, edge cases
- 3-4 assertions per test

**Validation**: Run pytest tests/training/test_training_edge_cases_phase26.py::test_training_* -v
```

---

## 🎯 Success Criteria

**Per Sub-batch**:
- ✅ All tests implemented with meaningful assertions
- ✅ All tests passing
- ✅ No code quality issues
- ✅ Proper mocking (no actual I/O, subprocess, GPU)
- ✅ Documentation strings clear

**Overall (39 tests)**:
- ✅ All 39 tests passing
- ✅ Coverage increase to 73-75%
- ✅ Zero new linting/type issues
- ✅ All fixtures reusable
- ✅ Cognitive brain updated

---

## 📝 Quality Checklist

**Before Each Commit**:
- [ ] Run pytest on new tests
- [ ] Check for unused imports/variables
- [ ] Verify mock objects released
- [ ] Validate assertion coverage
- [ ] Update test count in documentation

**After All Tests**:
- [ ] Run full coverage analysis
- [ ] Execute 14 quality gates
- [ ] Update PHASE_27_EXECUTION_SUMMARY.md
- [ ] Verify no test isolation issues
- [ ] Confirm memory leaks addressed

---

## 🚀 Estimated Timeline

| Phase | Duration | Tests | Cumulative |
|-------|----------|-------|------------|
| Sub-batch A1 | 60-75 min | 8 CLI | 8 |
| Sub-batch A2 | 45-60 min | 6 CLI | 14 |
| Sub-batch A3 | 45-60 min | 6 CLI | 20 |
| Sub-batch A4 | 30-45 min | 5 CLI | 25 |
| Sub-batch B1 | 45-60 min | 5 Training | 30 |
| Sub-batch B2 | 60-75 min | 5 Training | 35 |
| Sub-batch B3 | 45-60 min | 4 Training | 39 |
| **Validation** | 60 min | Coverage, QA | 39 ✅ |
| **TOTAL** | **6-8 hours** | **39 tests** | **Complete** |

---

**Status**: Complete autonomous planset ready for execution  
**Policy**: 100% AI Agency Policy v1.1.0 compliant  
**Next**: Execute Option 1 (incremental) or Option 2 (full batch) as directed
