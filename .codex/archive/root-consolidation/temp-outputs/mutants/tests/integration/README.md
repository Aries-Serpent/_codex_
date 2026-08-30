# Integration Test Suite

**Created:** 2025-12-26  
**PR:** #2622  
**Purpose:** End-to-end integration testing for Genesis Protocol workflows

---

## Overview

This directory contains integration tests that validate the Genesis Protocol workflow execution, artifact handling, and error recovery mechanisms. Unlike unit tests that test individual components in isolation, these tests verify that multiple components work together correctly in realistic scenarios.

---

## Test Organization

### Test Files

- `test_genesis_workflow.py` - End-to-end Genesis workflow validation
- `test_workflow_execution.py` - Workflow step execution and coordination
- `test_artifact_validation.py` - Output artifact checking and validation
- `test_error_recovery.py` - Error handling and recovery mechanisms
- `test_safety_guards.py` - Safety mechanism validation

### Fixtures

Located in `fixtures/` directory:
- `mock_secrets.yaml` - Test secrets (non-sensitive)
- `test_config.yaml` - Test configuration
- `sample_workflow_results.json` - Sample workflow outputs
- `mock_repository_state.json` - Mock repository state for testing

---

## Running Integration Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-timeout

# Ensure you're in the repository root
cd /home/runner/work/_codex_/_codex_
```

### Run All Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=.codex --cov=scripts -v

# Run specific test file
pytest tests/integration/test_genesis_workflow.py -v
```

### Run Specific Test Scenarios

```bash
# Genesis workflow tests only
pytest tests/integration/ -k "genesis" -v

# Safety guard tests only  
pytest tests/integration/ -k "safety" -v

# Error recovery tests only
pytest tests/integration/ -k "error" -v
```

### Run in CI/CD

These tests are designed to run in GitHub Actions. See `.github/workflows/integration-tests.yml` for CI configuration.

---

## Test Scenarios

### 1. Genesis Workflow Execution

**File:** `test_genesis_workflow.py`

Tests complete Genesis Protocol workflow from start to finish:
- Configuration loading
- Secret validation
- Workflow step execution  
- Artifact generation
- Status reporting

**Key Test Cases:**
- `test_genesis_workflow_complete()` - Full workflow execution
- `test_genesis_workflow_with_mock_secrets()` - Using test secrets
- `test_genesis_workflow_dry_run()` - Dry-run mode validation

### 2. Workflow Execution

**File:** `test_workflow_execution.py`

Tests individual workflow steps and coordination:
- Step initialization
- Step execution order
- Step interdependencies
- Step output validation

**Key Test Cases:**
- `test_workflow_step_execution()` - Single step execution
- `test_workflow_step_order()` - Execution order validation
- `test_workflow_step_dependencies()` - Dependency resolution

### 3. Artifact Validation

**File:** `test_artifact_validation.py`

Tests output artifact generation and validation:
- Artifact creation
- Artifact format validation
- Artifact content verification
- Artifact persistence

**Key Test Cases:**
- `test_artifact_generation()` - Artifact creation
- `test_artifact_format()` - Format validation
- `test_artifact_content()` - Content verification

### 4. Error Recovery

**File:** `test_error_recovery.py`

Tests error handling and recovery mechanisms:
- Graceful degradation
- Error reporting
- Rollback procedures
- Recovery strategies

**Key Test Cases:**
- `test_error_handling()` - Error detection and handling
- `test_rollback_mechanism()` - Rollback validation
- `test_recovery_procedures()` - Recovery validation

### 5. Safety Guards

**File:** `test_safety_guards.py`

Tests safety mechanisms and guardrails:
- Configuration validation
- Permission checks
- Rate limiting
- Autonomous action prevention

**Key Test Cases:**
- `test_autonomous_actions_disabled()` - Verify autonomous_actions_enabled=false
- `test_safety_guard_enforcement()` - Guard validation
- `test_permission_checks()` - Permission validation

---

## Test Coverage Goals

- **Target Coverage:** >80% for Genesis components
- **Current Coverage:** TBD (run `pytest --cov` to measure)

### Key Components to Cover

- `.codex/autonomous_agent.yaml` configuration loading
- `scripts/autonomous_agent.py` agent orchestration
- `.github/workflows/genesis-bootstrap.yml` workflow execution
- `scripts/genesis_rollback.sh` rollback procedures

---

## Writing New Integration Tests

### Test Template

```python
import pytest
from pathlib import Path

class TestNewIntegrationScenario:
    """Test description"""

    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        """Setup test environment with mock data"""
        # Create test fixtures
        test_config = tmp_path / "test_config.yaml"
        test_config.write_text("test: configuration")
        return {"config_path": test_config}

    def test_scenario(self, setup_test_environment):
        """Test specific scenario"""
        # Arrange
        config = setup_test_environment["config_path"]

        # Act
        result = execute_workflow(config)

        # Assert
        assert result.success is True
        assert result.artifacts_generated > 0
```

### Best Practices

1. **Use fixtures for setup/teardown**
2. **Mock external dependencies**
3. **Test realistic scenarios**
4. **Include both happy path and error cases**
5. **Document test purpose clearly**
6. **Keep tests independent**
7. **Use descriptive test names**

---

## Troubleshooting

### Common Issues

**Issue:** Tests fail with "FileNotFoundError"
- **Solution:** Ensure fixtures directory exists and contains required files

**Issue:** Tests timeout
- **Solution:** Use `@pytest.mark.timeout(60)` decorator to set appropriate timeout

**Issue:** Tests fail in CI but pass locally
- **Solution:** Check environment differences, ensure CI has required dependencies

### Getting Help

- Review test logs: `.codex/pytest.log`
- Check lessons learned: `.codex/lessons_learned.md`
- Use toolkit: `python .codex/ai_agent_toolkit.py`
- Escalate to human admin if unresolvable

---

## CI/CD Integration

### GitHub Actions Workflow

Integration tests run automatically on:
- Pull requests touching `.codex/` or `scripts/`
- Pushes to main branch
- Manual workflow dispatch

### Workflow Configuration

See `.github/workflows/integration-tests.yml` for:
- Test matrix configuration
- Python version testing
- Artifact upload
- Results reporting

---

## Maintenance

### Regular Tasks

- [ ] Review test coverage monthly
- [ ] Update fixtures as needed
- [ ] Add tests for new features
- [ ] Remove obsolete tests
- [ ] Update documentation

### Adding New Tests

1. Create test file in `tests/integration/`
2. Follow naming convention: `test_*.py`
3. Add test scenarios
4. Update this README with new scenarios
5. Run tests locally to verify
6. Submit PR with changes

---

## References

- **Toolkit:** `.codex/ai_agent_toolkit.py` - Reusable test utilities
- **Lessons Learned:** `.codex/lessons_learned.md` - Known issues and solutions
- **Roadmap:** `docs/admin/CONTINUATION_ROADMAP.md` - Phase 2 integration test plan
- **Agent Docs:** `.codex/archive/deprecated/AGENTS.md` - Agent operational guidelines

---

**Last Updated:** 2025-12-26  
**Maintainer:** AI Agent (ai_org_repo_admin)  
**Status:** Initial framework created, awaiting test implementation
