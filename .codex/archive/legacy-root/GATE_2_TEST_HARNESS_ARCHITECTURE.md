# Agent Test Harness Architecture and Framework Design

## Overview

This document outlines the comprehensive test harness framework for Aries-Serpent custom agents. The framework provides a scalable, reusable infrastructure for testing all 162+ custom agents (147 active, 15 archived) with consistent patterns and comprehensive coverage.

**Deliverable Status:** ✅ Phase 4A Complete  
**Framework Version:** 1.0.0  
**Last Updated:** 2026-07-03

---

## Architecture

### Directory Structure

```
tests/agents/
├── conftest.py                    # Shared pytest fixtures and configuration
├── test_harness.py               # Base AgentTestHarness class and patterns
├── fixtures/
│   ├── __init__.py
│   ├── sample_inputs.py          # Test input data templates
│   ├── output_templates.py       # Expected output formats
│   └── mock_data_generators.py   # Dynamic test data creation
├── data/
│   └── (test artifacts and results)
│
├── test_control_flow.py          # Phase 4B: Control flow tests
├── test_integration.py            # Phase 4B: Integration tests
├── test_quality.py               # Phase 4B: Quality and performance tests
├── test_regression.py            # Phase 4B: Regression and known issues
└── test_custom_agents.py         # Custom agent-specific tests
```

### Core Components

#### 1. **conftest.py** - Pytest Configuration & Fixtures

Provides reusable fixtures for all agent tests:

**Database Fixtures:**
- `temp_db`: Temporary SQLite database for test isolation
- `db_connection`: Database connection with row factory

**Mock Fixtures:**
- `mock_env`: Mocked environment variables
- `mock_github_api`: GitHub API client mock
- `mock_logger`: Logger mock for output capture

**Builder Fixtures:**
- `agent_context_builder`: Fluent builder for test contexts
- `execution_context_builder`: Builder for execution states

**Data Fixtures:**
- `sample_agent_config`: Sample agent configuration
- `sample_test_inputs`: Common test inputs
- `sample_agent_outputs`: Expected outputs

**Helper Fixtures:**
- `assert_valid_json()`: JSON validation helper
- `assert_valid_agent_output()`: Output format validator
- `measure_execution_time()`: Performance measurement context manager
- `assert_callback_called()`: Mock callback verification

#### 2. **test_harness.py** - Base Test Framework

Provides `AgentTestHarness` abstract base class:

**Key Classes:**
- `ExecutionStatus`: Enum for execution states (pending, running, success, partial, failed, timeout, cancelled)
- `TestPhase`: Enum for test phases (initialization, setup, execution, validation, cleanup)
- `ExecutionMetrics`: Dataclass for performance metrics
- `TestResult`: Dataclass for individual test results
- `ExecutionContext`: Dataclass for test execution context

**AgentTestHarness Methods:**

*Lifecycle:*
- `setup(context)`: Initialize test environment (abstract)
- `teardown()`: Cleanup (abstract)
- `execute_agent(inputs)`: Run agent (abstract)

*Test Execution:*
- `run_test()`: Execute test with timing and exception handling
- `test_initialization()`: Verify agent setup
- `test_basic_execution()`: Test basic functionality
- `test_output_format()`: Validate output structure
- `test_error_handling()`: Test error paths

*Output Validation:*
- `validate_output_status()`: Check status field
- `validate_output_structure()`: Verify required fields
- `validate_output_types()`: Type checking

*Performance:*
- `benchmark_execution()`: Performance testing (iterations, min/max/avg times)

*Integration:*
- `test_multi_step_execution()`: Multi-step workflows
- `test_state_preservation()`: State consistency across calls

*Reporting:*
- `get_summary()`: Test execution summary
- `report_results()`: Generate text/JSON report

**AgentTestPattern - Common Patterns:**
- `happy_path_test()`: Standard success flow
- `error_recovery_test()`: Error handling validation
- `idempotency_test()`: Result consistency
- `performance_test()`: Performance requirements

---

## Usage Guide

### Basic Agent Test Implementation

```python
from tests.agents.test_harness import AgentTestHarness, ExecutionContext

class MyAgentTestHarness(AgentTestHarness):
    def setup(self, context: ExecutionContext) -> None:
        """Initialize test environment."""
        self.mock_api = MagicMock()
        self.agent = MyAgent(config=context.config)

    def teardown(self) -> None:
        """Clean up test environment."""
        self.agent = None

    def execute_agent(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent."""
        return self.agent.process(inputs)


def test_my_agent():
    """Test my agent."""
    harness = MyAgentTestHarness("my-agent", "specialist")
    
    # Setup
    context = ExecutionContext(
        agent_id="my-agent",
        agent_type="specialist",
        session_id="test-session"
    )
    harness.setup(context)
    
    # Run tests
    harness.test_initialization()
    harness.test_basic_execution({"input": "test"})
    
    # Cleanup
    harness.teardown()
    
    # Report
    print(harness.report_results())
```

### Using Fixtures in Pytest

```python
def test_with_fixtures(
    agent_context_builder,
    sample_test_inputs,
    assert_valid_agent_output,
    measure_execution_time
):
    """Test agent using fixtures."""
    # Build context
    context = agent_context_builder\
        .with_agent_id("my-agent")\
        .with_input("data", [1, 2, 3])\
        .build()
    
    # Execute with timing
    with measure_execution_time() as timer:
        result = agent.execute(context)
    
    timer.assert_under(1000)  # Assert < 1 second
    
    # Validate output
    assert_valid_agent_output(result)
    assert result["status"] == "success"
```

### Common Test Patterns

#### 1. Control Flow Tests
```python
def test_agent_control_flow(harness):
    """Test initialization, execution, and cleanup."""
    # Test initialization
    harness.test_initialization()
    
    # Test execution
    harness.test_basic_execution({"input": "test"})
    
    # Test output format
    harness.test_output_format(
        {"input": "test"},
        expected_keys=["status", "data"]
    )
```

#### 2. Error Handling Tests
```python
def test_error_handling(harness):
    """Test error paths."""
    harness.test_error_handling({
        "invalid_field": "should cause error"
    })
```

#### 3. Integration Tests
```python
def test_multi_agent_workflow(harness1, harness2):
    """Test multi-agent orchestration."""
    # Agent 1 produces output
    result1 = harness1.execute_agent({"input": "data"})
    
    # Agent 2 consumes output
    result2 = harness2.execute_agent(result1["data"])
    
    assert result2["status"] == "success"
```

#### 4. Performance Tests
```python
def test_performance(harness):
    """Test performance requirements."""
    benchmark = harness.benchmark_execution(
        {"input": "test"},
        iterations=100,
        max_duration_ms=1000
    )
    
    assert benchmark["avg_duration_ms"] < 1000
```

---

## Test Categories

### 1. Control Flow Tests (Phase 4B)
**Purpose:** Validate basic agent initialization and execution flow

**Coverage:**
- Agent initialization and configuration
- Basic execution with valid inputs
- Output format validation
- Error handling for invalid inputs
- Cleanup and resource release

**File:** `tests/agents/test_control_flow.py`

**Expected Coverage:** 40-50% of agent code

### 2. Integration Tests (Phase 4B)
**Purpose:** Validate multi-agent orchestration and data flow

**Coverage:**
- Multi-agent workflows
- Handoff between agents
- Data passing and transformation
- State preservation across calls
- Orchestration patterns

**File:** `tests/agents/test_integration.py`

**Expected Coverage:** 20-30% of agent code

### 3. Quality Tests (Phase 4B)
**Purpose:** Validate output quality, performance, and resource usage

**Coverage:**
- Output format validation (JSON, structure, types)
- Performance benchmarks
- Resource usage (memory, CPU)
- Coverage calculations
- Metric collection

**File:** `tests/agents/test_quality.py`

**Expected Coverage:** 15-25% of agent code

### 4. Regression Tests (Phase 4B)
**Purpose:** Prevent regressions in known issues and edge cases

**Coverage:**
- Previously reported bugs
- Known edge cases
- Boundary conditions
- Platform-specific issues
- Historical failure patterns

**File:** `tests/agents/test_regression.py`

**Expected Coverage:** 10-15% of agent code

---

## Test Markers and Organization

```python
# Pytest markers for test organization

@pytest.mark.agent
def test_agent_basic():
    """Test is an agent test."""
    pass

@pytest.mark.integration
def test_multi_agent_workflow():
    """Test is an integration test."""
    pass

@pytest.mark.control_flow
def test_initialization():
    """Test is control flow test."""
    pass

@pytest.mark.quality
def test_performance():
    """Test is quality test."""
    pass

@pytest.mark.regression
def test_known_issue():
    """Test is regression test."""
    pass

@pytest.mark.slow
def test_long_running():
    """Test takes >5 seconds."""
    pass

@pytest.mark.requires_auth
def test_with_authentication():
    """Test requires GitHub authentication."""
    pass
```

**Run tests by marker:**
```bash
pytest -m agent                 # All agent tests
pytest -m integration           # Integration tests only
pytest -m "not slow"            # Exclude slow tests
pytest -m "control_flow or quality"  # Multiple markers
```

---

## Execution Flow

### Phase 4A: Architecture (COMPLETE ✅)
1. ✅ Created `conftest.py` with fixtures
2. ✅ Created `test_harness.py` with base class
3. ✅ Created `fixtures/` directory with templates
4. ✅ Created architecture documentation

### Phase 4B: Test Coverage (IN PROGRESS)
1. Build control flow tests for all 147 active agents
2. Build integration tests for delegation agents
3. Build quality and performance tests
4. Build regression test suite
5. Target: 50%+ coverage

### Phase 4C: Validation (PENDING)
1. Run complete test suite: `nox -s agent-tests`
2. Generate coverage report
3. Verify 50%+ coverage threshold
4. Create validation report
5. Archive results

---

## Configuration and Settings

### Pytest Configuration

```ini
[pytest]
testpaths = tests/agents
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    agent: Agent test
    integration: Integration test
    control_flow: Control flow test
    quality: Quality test
    regression: Regression test
    slow: Slow test (>5s)
    requires_auth: Requires authentication
timeout = 300
log_cli = true
log_cli_level = DEBUG
```

### Coverage Configuration

```ini
[coverage:run]
source = agents/
omit = */tests/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## Performance Benchmarks

Expected performance metrics for agent execution:

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Avg Execution Time** | < 500ms | < 1000ms |
| **P95 Execution Time** | < 2000ms | < 5000ms |
| **Memory Peak** | < 100MB | < 500MB |
| **Throughput** | > 2 ops/s | > 1 op/s |
| **Error Rate** | < 0.1% | < 1% |

---

## Known Issues and Limitations

1. **Mock API Compatibility**
   - GitHub API mocks may not match all endpoints
   - Recommend using VCR cassettes for complex workflows

2. **Database Testing**
   - Temporary databases are SQLite, not production DB
   - Some database-specific features not available

3. **Async Agent Testing**
   - Async agents may require additional pytest plugins
   - Currently using synchronous execution paths

4. **Large Data Sets**
   - Performance tests with very large inputs (>10MB) may be slow
   - Consider using sampling for benchmarks

---

## Future Enhancements

### Phase 4B+
1. **Automated Test Generation**
   - Generate skeleton tests from AGENT_REGISTRY.yaml
   - Auto-discover test patterns

2. **Advanced Metrics**
   - Code coverage per agent
   - Mutation testing integration
   - Property-based testing (Hypothesis)

3. **Parallel Execution**
   - pytest-xdist for parallel test execution
   - Reduced total test time

4. **Continuous Monitoring**
   - Integration with CI/CD pipeline
   - Performance regression detection
   - Automated alerting on failures

### Phase 5+
1. **AI-Powered Test Generation**
   - LLM-based test case generation
   - Auto-identification of edge cases

2. **Visual Test Reporting**
   - HTML reports with graphs
   - Trend analysis over time
   - Agent health dashboard

3. **Multi-Framework Support**
   - Support for unittest, nose, etc.
   - Agent framework abstraction layer

---

## Quick Reference

### Run All Tests
```bash
pytest tests/agents/ -v
```

### Run Specific Test Category
```bash
pytest tests/agents/ -m control_flow -v
pytest tests/agents/ -m integration -v
```

### Generate Coverage Report
```bash
pytest tests/agents/ --cov=agents --cov-report=html
```

### Run with Detailed Logging
```bash
pytest tests/agents/ -v --log-cli-level=DEBUG
```

### Run Single Test
```bash
pytest tests/agents/test_control_flow.py::test_agent_init -v
```

### Benchmark Performance
```python
harness = MyAgentTestHarness("my-agent", "type")
results = harness.benchmark_execution(inputs, iterations=100)
```

---

## Support and Contributions

**Maintainer:** @mbaetiong  
**Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml`  
**Framework Version:** 1.0.0  
**Last Updated:** 2026-07-03  

**Contact for:**
- Test framework questions: See `conftest.py` and `test_harness.py`
- Agent-specific tests: See corresponding agent documentation
- Coverage gaps: Check Phase 4B deliverables

---

**Status:** ✅ Phase 4A Architecture Complete - Ready for Phase 4B Test Implementation
