# AI-Assisted Test Generation Guide

## Overview

This guide explains how to use the test generation framework to create comprehensive unit tests for orchestration flows with minimal manual effort.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Generation Framework](#test-generation-framework)
3. [Flow Specifications](#flow-specifications)
4. [Creating Custom Specifications](#creating-custom-specifications)
5. [CLI Usage](#cli-usage)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Generate Tests for a Specific Flow

```bash
python scripts/generate_tests.py --spec physics_orchestration --output-dir tests/agents
```

### Generate Tests for All Pre-Defined Flows

```bash
python scripts/generate_tests.py --spec all --output-dir tests/generated
```

### Available Flow Specifications

- `physics_orchestration` - PhysicsInspiredOrchestrator.orchestrate()
- `diffusion_flow` - DiffusionFlowModel.simulate_flow()
- `quantum_game` - BlueRedTeamSimulator.run_simulation()
- `mental_mapping` - MentalMappingModel.think_through_problem()

## Test Generation Framework

The framework consists of two main components:

### 1. OrchestrationFlowSpec

A dataclass that defines the characteristics of an orchestration flow:

```python
from tests.framework.test_generator import OrchestrationFlowSpec

spec = OrchestrationFlowSpec(
    module_path="agents.my_module",
    class_name="MyOrchestrator",
    method_name="my_method",
    stages=["STAGE1", "STAGE2", "STAGE3"],
    decision_points=["branch1", "branch2"],
    inputs={"param1": "Type1", "param2": "Type2"},
    outputs={"result": "ResultType"},
    line_range=(100, 200),
    branch_paths=["success", "failure"],
    edge_cases=["empty_input", "max_value"],
    fixtures_needed=["fixture1", "fixture2"],
    mocks_needed=["mock1"]
)
```

### 2. UnitTestGenerator

Generates comprehensive test suites from specifications:

```python
from tests.framework.test_generator import UnitTestGenerator

generator = UnitTestGenerator(spec)

# Generate complete test suite
test_code = generator.generate_complete_test_suite()

# Get test summary
summary = generator.generate_test_summary()
```

## Flow Specifications

Pre-defined specifications are located in `tests/specs/flow_specifications.py`.

### Physics Orchestration Spec

```python
physics_orchestration_spec = OrchestrationFlowSpec(
    module_path="agents.physics_orchestrator",
    class_name="PhysicsInspiredOrchestrator",
    method_name="orchestrate",
    stages=["ASSESS", "DELIBERATE", "OPTIMIZE", "ACT"],
    decision_points=[
        "no_paths_meet_constraints",
        "multiple_optimal_paths",
        "energy_budget_exceeded"
    ],
    # ... full specification in file
)
```

**Coverage Target:** Lines 427-460 in `agents/physics_orchestrator.py`

**Test Categories Generated:**
- Happy path execution (1 test)
- Edge cases (4 tests): empty_action_list, all_actions_exceed_budget, ties, negative_values
- Failure scenarios (2 tests): invalid_input, exception_handling

## Creating Custom Specifications

### Step 1: Identify the Flow

Determine the following:
- Module path (e.g., `agents.my_module`)
- Class name (e.g., `MyOrchestrator`)
- Method name (e.g., `process_data`)
- Flow stages (e.g., `["VALIDATE", "TRANSFORM", "STORE"]`)

### Step 2: Define Decision Points

Identify where the flow can branch:
- Conditional logic
- Error handling paths
- Resource availability checks
- Timeout scenarios

### Step 3: List Edge Cases

Common edge cases to consider:
- Empty inputs
- Maximum/minimum values
- Null/None values
- Very large datasets
- Concurrent access
- Resource exhaustion

### Step 4: Create the Specification

```python
from tests.framework.test_generator import OrchestrationFlowSpec

my_flow_spec = OrchestrationFlowSpec(
    module_path="agents.data_processor",
    class_name="DataOrchestrator",
    method_name="process_batch",
    stages=["VALIDATE", "TRANSFORM", "AGGREGATE", "STORE"],
    decision_points=[
        "validation_failure",
        "transformation_error",
        "storage_timeout"
    ],
    inputs={
        "data_batch": "List[Dict]",
        "config": "ProcessingConfig"
    },
    outputs={
        "processed_count": "int",
        "errors": "List[str]",
        "success": "bool"
    },
    line_range=(150, 280),
    branch_paths=[
        "all_valid",
        "partial_valid",
        "all_invalid"
    ],
    edge_cases=[
        "empty_batch",
        "single_item",
        "very_large_batch",
        "malformed_data",
        "timeout_during_storage"
    ],
    fixtures_needed=[
        "sample_data",
        "processing_config",
        "orchestrator"
    ],
    mocks_needed=[
        "storage_backend",
        "transformation_engine"
    ]
)
```

### Step 5: Generate Tests

```python
from tests.framework.test_generator import UnitTestGenerator

generator = UnitTestGenerator(my_flow_spec)
test_code = generator.generate_complete_test_suite()

# Write to file
output_path = "tests/agents/test_data_orchestrator_process_batch.py"
with open(output_path, 'w') as f:
    f.write(test_code)
```

## CLI Usage

### Basic Commands

```bash
# Generate tests for a single flow
python scripts/generate_tests.py --spec physics_orchestration

# Generate tests for all flows
python scripts/generate_tests.py --spec all

# Specify custom output directory
python scripts/generate_tests.py --spec quantum_game --output-dir tests/custom

# Analyze a module (future feature)
python scripts/generate_tests.py --module agents.physics_orchestrator --analyze
```

### CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--spec SPEC` | Specification name or "all" | `--spec physics_orchestration` |
| `--output-dir DIR` | Output directory for generated tests | `--output-dir tests/generated` |
| `--analyze` | Analyze module for flows (not yet implemented) | `--analyze` |
| `--module MODULE` | Module to analyze | `--module agents.my_module` |

### Example Output

```
$ python scripts/generate_tests.py --spec physics_orchestration

✓ Generated: tests/generated/test_physicsinspiredorchestrator_orchestrate.py
  Target coverage: Lines 427-460
  Test categories: 7

Test Generation Summary for PhysicsInspiredOrchestrator.orchestrate
================================================================================

Coverage Target: Lines 427-460
Stages: ASSESS, DELIBERATE, OPTIMIZE, ACT
Decision Points: 3
Branch Paths: 3
Edge Cases: 4

Test Categories:
  - Happy Path: 1 test
  - Edge Cases: 4 tests
  - Failure Scenarios: 2 tests
  
Total Estimated Tests: 7
```

## Best Practices

### 1. One Test Per Behavior

Each test should verify a single behavior or outcome:

```python
def test_orchestrate_with_empty_action_list(self):
    """Test orchestration behavior when no actions are available."""
    # Test only the empty action list scenario
```

### 2. Descriptive Test Names

Use the pattern: `test_<method>_<scenario>_<expected_outcome>`

```python
def test_orchestrate_high_energy_paths_returns_wait(self):
    """When all paths exceed energy budget, orchestrate should return wait action."""
```

### 3. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
def test_example(self):
    """Test description."""
    # Arrange - Setup test data and mocks
    orchestrator = MyOrchestrator()
    input_data = create_test_data()
    
    # Act - Execute the method under test
    result = orchestrator.process(input_data)
    
    # Assert - Verify the outcome
    assert result['success'] is True
    assert len(result['items']) == 10
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
def orchestrator():
    """Provide a configured orchestrator instance."""
    return MyOrchestrator(config={'timeout': 30})

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        'items': [1, 2, 3],
        'metadata': {'source': 'test'}
    }

def test_with_fixtures(orchestrator, sample_data):
    """Use fixtures to reduce duplication."""
    result = orchestrator.process(sample_data)
    assert result is not None
```

### 5. Mock External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mocked_storage(self):
    """Test orchestration with mocked storage backend."""
    with patch('agents.storage.StorageBackend') as MockStorage:
        mock_backend = MockStorage.return_value
        mock_backend.save.return_value = True
        
        orchestrator = MyOrchestrator(storage=mock_backend)
        result = orchestrator.save_data({'key': 'value'})
        
        assert result is True
        mock_backend.save.assert_called_once()
```

### 6. Test Edge Cases Comprehensively

```python
def test_orchestrate_edge_cases(self):
    """Collection of edge case tests."""
    orchestrator = MyOrchestrator()
    
    # Empty input
    assert orchestrator.process([]) == {'success': True, 'count': 0}
    
    # Single item
    assert orchestrator.process([1])['count'] == 1
    
    # Maximum allowed items
    large_input = list(range(10000))
    result = orchestrator.process(large_input)
    assert result['success'] is True
```

### 7. Verify Exception Handling

```python
def test_orchestrate_invalid_input_raises_error(self):
    """Verify proper exception handling for invalid input."""
    orchestrator = MyOrchestrator()
    
    with pytest.raises(ValueError, match="Input must be a list"):
        orchestrator.process("not a list")
```

### 8. Keep Tests Fast

```python
# Good - Use mocks for expensive operations
def test_fast(self):
    with patch('agents.expensive_operation') as mock_op:
        mock_op.return_value = {'result': 'value'}
        # Test runs in milliseconds

# Avoid - Real expensive operations
def test_slow(self):
    # Calls actual database, network, or heavy computation
    # Test runs in seconds
```

### 9. Make Tests Deterministic

```python
# Good - Fixed seed for randomness
def test_with_randomness(self):
    import random
    random.seed(42)
    result = generate_random_data()
    assert result == expected_deterministic_output

# Avoid - Non-deterministic behavior
def test_flaky(self):
    result = generate_random_data()  # Different each run
    assert result  # Might pass or fail randomly
```

### 10. Document Test Intent

```python
def test_orchestrate_complex_scenario(self):
    """
    Test orchestration with complex multi-stage scenario.
    
    This test verifies that when the orchestrator receives:
    1. A high-priority task
    2. With limited resources
    3. And multiple possible paths
    
    It should:
    1. Assess the situation correctly
    2. Prioritize high-impact paths
    3. Select the optimal path within constraints
    4. Execute successfully
    """
    # Implementation...
```

## Troubleshooting

### Generated Tests Don't Import

**Problem:** Import errors when running generated tests.

**Solution:** Verify module paths are correct in the specification:

```python
# Correct
module_path="agents.physics_orchestrator"

# Incorrect
module_path="physics_orchestrator"  # Missing 'agents' package
```

### Tests Don't Match Actual API

**Problem:** Generated tests call methods that don't exist or use wrong signatures.

**Solution:** Update the specification's `inputs` and `outputs` to match the actual API:

```python
# Check actual method signature
def orchestrate(self, state: DecisionState, actions: List[ActionPath]) -> Dict:
    ...

# Update specification
inputs={
    "state": "DecisionState",
    "actions": "List[ActionPath]"  # Use correct parameter name
}
```

### Too Many/Few Tests Generated

**Problem:** Generated test suite is too large or too small.

**Solution:** Adjust the specification's `edge_cases` list:

```python
# Add more edge cases for comprehensive coverage
edge_cases=[
    "empty_input",
    "single_item",
    "max_size",
    "invalid_type",
    "concurrent_access",
    "timeout",
    "network_error"
]
```

### Tests Are TODOs

**Problem:** Generated tests contain `# TODO` placeholders.

**Solution:** The generator creates templates. Fill in the implementation:

```python
# Generated
def test_method_edge_case(self):
    """Test method with edge case."""
    # TODO: Implement edge case test
    pass

# Implemented
def test_method_edge_case(self):
    """Test method with edge case."""
    orchestrator = MyOrchestrator()
    result = orchestrator.method(edge_case_input)
    assert result == expected_output
```

### Fixtures Don't Work

**Problem:** Fixtures are not recognized by pytest.

**Solution:** Ensure fixtures are properly decorated:

```python
# Correct
@pytest.fixture
def my_fixture():
    return "value"

# Incorrect (missing decorator)
def my_fixture():
    return "value"
```

## Advanced Usage

### Customizing Test Generation

Extend the `UnitTestGenerator` class:

```python
from tests.framework.test_generator import UnitTestGenerator

class CustomTestGenerator(UnitTestGenerator):
    def _generate_performance_tests(self) -> str:
        """Generate performance benchmark tests."""
        return f'''
    def test_{self.spec.method_name}_performance(self):
        """Benchmark {self.spec.method_name} performance."""
        import time
        start = time.time()
        result = orchestrator.{self.spec.method_name}(...)
        duration = time.time() - start
        assert duration < 1.0  # Should complete in < 1 second
'''
    
    def generate_complete_test_suite(self) -> str:
        """Override to include performance tests."""
        base = super().generate_complete_test_suite()
        perf = self._generate_performance_tests()
        return base + perf
```

### Integration with CI/CD

Add test generation to your CI pipeline:

```yaml
# .github/workflows/test-generation.yml
name: Generate Tests

on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate tests
        run: |
          python scripts/generate_tests.py --spec all
          pytest tests/generated/ -v
```

## Examples

### Example 1: Simple Flow

```python
from tests.framework.test_generator import OrchestrationFlowSpec, UnitTestGenerator

spec = OrchestrationFlowSpec(
    module_path="agents.simple",
    class_name="SimpleProcessor",
    method_name="process",
    stages=["VALIDATE", "EXECUTE"],
    decision_points=["invalid_input"],
    inputs={"data": "str"},
    outputs={"result": "str"},
    line_range=(10, 30),
    branch_paths=["success", "failure"],
    edge_cases=["empty_string", "very_long_string"],
    fixtures_needed=["processor"],
    mocks_needed=[]
)

generator = UnitTestGenerator(spec)
print(generator.generate_test_summary())
```

### Example 2: Complex Multi-Stage Flow

```python
spec = OrchestrationFlowSpec(
    module_path="agents.complex",
    class_name="ComplexOrchestrator",
    method_name="orchestrate_workflow",
    stages=["ANALYZE", "PLAN", "EXECUTE", "VALIDATE", "REPORT"],
    decision_points=[
        "analysis_incomplete",
        "plan_rejected",
        "execution_failed",
        "validation_timeout"
    ],
    inputs={
        "workflow": "WorkflowDefinition",
        "context": "ExecutionContext",
        "config": "OrchestratorConfig"
    },
    outputs={
        "success": "bool",
        "results": "Dict[str, Any]",
        "metrics": "ExecutionMetrics"
    },
    line_range=(100, 500),
    branch_paths=[
        "full_success",
        "partial_success",
        "rollback_required",
        "complete_failure"
    ],
    edge_cases=[
        "empty_workflow",
        "circular_dependencies",
        "resource_exhaustion",
        "concurrent_execution",
        "timeout_during_validation"
    ],
    fixtures_needed=[
        "workflow_definition",
        "execution_context",
        "orchestrator_config",
        "orchestrator"
    ],
    mocks_needed=[
        "resource_manager",
        "validation_service",
        "reporting_backend"
    ]
)
```

## Reference

### OrchestrationFlowSpec Fields

| Field | Type | Description |
|-------|------|-------------|
| `module_path` | str | Python module path (e.g., "agents.module") |
| `class_name` | str | Class name to test |
| `method_name` | str | Method name to test |
| `stages` | List[str] | Flow stages in order |
| `decision_points` | List[str] | Branch/decision points |
| `inputs` | Dict[str, str] | Method inputs (name -> type) |
| `outputs` | Dict[str, str] | Method outputs (name -> type) |
| `line_range` | Tuple[int, int] | Source code line range |
| `branch_paths` | List[str] | Execution branch paths |
| `edge_cases` | List[str] | Edge cases to test |
| `fixtures_needed` | List[str] | pytest fixtures required |
| `mocks_needed` | List[str] | Mocks required |

### UnitTestGenerator Methods

| Method | Description |
|--------|-------------|
| `generate_complete_test_suite()` | Generate full test file |
| `generate_test_summary()` | Generate summary report |
| `_generate_fixtures()` | Generate pytest fixtures |
| `_generate_happy_path_test()` | Generate success case test |
| `_generate_edge_case_tests()` | Generate edge case tests |
| `_generate_failure_tests()` | Generate failure tests |

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review generated test code for TODOs
3. Examine flow specifications in `tests/specs/`
4. Review example tests in `tests/agents/test_*_core_flows.py`

## Version History

- **v1.0.0** (Previous Cycle-12-16): Initial release
  - Basic test generation
  - CLI tool
  - 4 pre-defined flow specifications
  - Comprehensive documentation
