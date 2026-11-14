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

### ML workflow shards

The [ML workflow](../../.github/workflows/ml-tests.yml) runs four independent
integration shards and four non-integration coverage shards after the component
jobs. Tests within a file stay together; SHA-256 of the relative file path
selects the shard, independent of collection order or `pytest-randomly` seeds.
No durations file, pytest-split or xdist is required.
ML jobs install `.[runtime,test-ml-integrations]` and run `pip check`; the
test-only extra does not expand production runtime requirements. Scanner/dev
dependencies resolve separately rather than forcing their OpenTelemetry API
constraint into the ML runtime environment. Supported-runner installation and
imports must pass on Ubuntu/glibc; cross-platform resolution or downloaded
wheels alone do not qualify the runtime. Preflight rejects the repository's
optional Torch stub and requires a real CPU tensor round trip.
Two coverage shards both exceeded their 18-minute test budgets in the first
hosted run, so the coverage partition was increased to four without changing
the selection or threshold.
The four-way trial still timed out (one shard reached 95%), and the latest run
timed out at 61% after 30 minutes. Coverage test steps now allow 50 minutes
inside a 60-minute job budget for setup and reporting. The 300-second per-test
timeout is unchanged.

From the repository root, reproduce an integration shard:

```bash
PYTHONPATH="$PWD/scripts/ci:$PWD/src" pytest tests/integration/ \
  -p ml_pytest_shards -m integration -rfE --durations=30 --timeout=600 \
  --ml-shards=4 --ml-shard=1 --ml-shard-report=reports/selection.json \
  --junitxml=reports/junit.xml
```

Coverage shards run **exactly** `tests/ -m "not slow and not integration"`,
with `--cov=src --cov=training`. Their individual coverage thresholds are
disabled because each sees only a subset. The single `ml-slow-aggregate`
check combines only `.coverage.unit-*` from `unit-cov-*` artifacts and enforces
the ratchet floor described below (target **70%**). Component and integration coverage never
enter that gate. Integration pass/fail remains independently required.
Module-level collection skips are not selected test items. The aggregate
counts them once across shard reports without hiding missing selected tests
or collection errors.
Failures are also appended to the test step summary as they occur, before
final JUnit generation, so a later timeout does not erase the first failures.

Every shard records JUnit, its selected IDs and a digest of the entire eligible
collection. The aggregate rejects differing collections, overlap, missing
collection. Each JUnit test case carries its canonical pytest node ID; matching
counts alone cannot substitute different tests. Manifests also record completion,
pytest exit status, and the repository, SHA, workflow run and attempt. The aggregate
rejects collect-only/incomplete/failed producers and evidence from another context.
After a workflow rerun, rerun all shard producers rather than mixing artifacts
from previous attempts.
selections/reports/data, and failed/cancelled/skipped upstream jobs. It writes
merged JUnit, coverage HTML and readable failure summaries; shards also write
summaries to GitHub's job summary. Empty or unavailable evidence is failure,
not successful skipped acceptance.

#### Quarantine manifest and coverage floor (ratchet gate)

Pre-existing unit failures are tracked, not ignored. Coverage shards pass
`--ml-quarantine .codex/baselines/ml_unit_quarantine.json`; each listed test
item (`{"version": 1, "entries": [{"nodeid", "cluster", "issue", "owner",
"reason", "added_sha"}]}`, `issue` is an https URL or `#<n>`) runs as
`xfail(strict=True)`, prepended so it overrides any `xfail` the test declares
itself. A quarantined test whose body passes (XPASS) fails the run, and the
shard report's `quarantine_results` lets the aggregate reject an XPASS even if
JUnit shows a plain pass, so fixed tests must leave the manifest. Only a failure
of the test body is quarantined: setup/teardown (fixture) errors stay errors
(`setup-error`/`teardown-error`), because they signal broken environment or
fixtures rather than the tracked failure. Collection errors have no item ID and
are never quarantinable. Shards record their pytest exit code and only fail the job
for infrastructure problems (no JUnit, timeout, exit codes other than 0/1);
`ml-slow-aggregate` is the gate and fails on any non-quarantined failure/error,
any collection error, or any manifest entry that no shard collected (stale).

Combined unit coverage must not drop below `floor` in
`.codex/baselines/ml_unit_coverage_floor.json` (initially 54, from 54.51% at
`2865b571ab`; floor = ⌊measured − 0.5⌋). When coverage is at least one point
above the floor the aggregate prints a notice suggesting a raise; nothing is
committed automatically. On pull requests the aggregate also compares both
files with the PR base (`HEAD^1` of the merge commit,
`ml_slow_aggregate.py ratchet`): adding manifest entries or lowering the floor
fails unless the PR carries the `quarantine-approved` label
(`ML_QUARANTINE_GROWTH_APPROVED=1`). Labels are read from the event payload, so
push a new commit after adding the label. Pushes are compared with
`github.event.before` (checked out by SHA, `--no-approval`: approval never
applies on push); a push with no previous commit (new branch) skips with a
notice. Pushes touching only `.codex/baselines/ml_unit_*.json` still trigger the
workflow. A base without the files imposes no constraint.

Use `--durations=30` output to identify expensive files before changing timeouts
or introducing xdist. No quick-subset selection or component-coverage reuse is
enabled. Push/nightly runs are not automatically cancelled; superseded PR
runs still are.

The follow-up is stacked on #5783. `copilot/session-*` PR bases are included so
stacked repairs can run this workflow. A repository administrator must replace
any required `test-integration-slow` check with **`ml-slow-aggregate`** only
after verifying its published check name and fresh hosted results. This code
does not change branch protection or configure required checks.

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
