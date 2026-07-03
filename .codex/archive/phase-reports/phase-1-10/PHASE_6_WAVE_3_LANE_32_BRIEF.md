# 💻 Lane 3.2: ML CLI Interface Coverage Remediation Brief

**Date:** 2026-06-27T22:22:23Z  
**Status:** ✅ Ready for Execution  
**Lane Owner:** unified-coverage-agent  
**Lane Scope:** `src/codex_ml/cli/`  
**Campaign:** Phase 6 Wave 3 — ML Systems Coverage Gap Remediation  

---

## Lane 3.2 Executive Summary

Lane 3.2 addresses comprehensive coverage gaps in the ML CLI interface, focusing on **argument parsing, output validation, error handling, and user-facing functionality**. This lane targets **50-70 new tests** to improve coverage from **10% → 60-80%**.

### Coverage Baseline
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Lines of Code** | 10,146 | N/A | N/A |
| **Line Coverage** | 10.0% | 60-80% | 50-70 pp |
| **Commands** | 40-50 | Fully tested | Many untested |
| **Tests** | ~20 | 50-70 | +30-50 tests |
| **Critical Gaps** | 7 | 0 | 7 to close |

### Lane 3.2 Success Criteria
- ✅ **50-70 new tests** written and passing
- ✅ **Coverage:** 10.0% → ≥60%
- ✅ **Pass Rate:** 100% (all tests green)
- ✅ **Zero Regressions:** Existing tests still pass
- ✅ **Timeline:** 18-22 hours (fits Wave 3 schedule)
- ✅ **Ready for Wave 4:** Integration with security scanning

---

## Critical Gaps Analysis

### GAP-3.2.1: CLI Argument Parsing (CRITICAL)
**Risk Level:** 🔴 CRITICAL  
**Coverage Impact:** 3-4%  
**Effort Estimate:** 15-20 tests, 5-6 hours  

**Current State:**
- 40-50 CLI commands have minimal argument validation
- No tests for invalid argument combinations
- Type coercion untested
- Required argument enforcement untested

**Target State:**
- Test valid argument combinations
- Test invalid arguments rejected with helpful message
- Test type coercion (string → int, bool, etc.)
- Test required vs optional arguments

**Test Patterns:**
```python
def test_train_command_valid_arguments():
    """Train command accepts valid arguments."""
    # --config, --output-dir, --epochs all valid
    # Result: exit code 0
    
def test_train_command_invalid_learning_rate():
    """Invalid learning rate rejected."""
    # --learning-rate "invalid"
    # Result: exit code 1, message about parsing
    
def test_required_argument_missing():
    """Missing required argument caught."""
    # train command without --config
    # Result: exit code 2, help text shown
    
def test_argument_type_coercion():
    """Numeric arguments coerced correctly."""
    # --epochs "10" (string) → 10 (int)
    # Verify: int(10) passed to trainer
```

**Success Criteria:**
- [ ] 15-20 tests written
- [ ] All tests passing
- [ ] Coverage increase: +3-4%

---

### GAP-3.2.2: Output Formatting & Validation (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 2-2.5%  
**Effort Estimate:** 10-12 tests, 4 hours  

**Current State:**
- Output format not validated
- JSON/table formatting not tested
- Progress indicators not tested
- Output truncation/overflow not handled

**Target State:**
- Test output format correctness
- Test progress indicator behavior
- Test output with very long strings
- Test JSON output is valid JSON

**Test Patterns:**
```python
def test_evaluate_command_json_output():
    """Evaluate command outputs valid JSON."""
    result = cli_runner.invoke(evaluate_command, ['--format', 'json'])
    json_data = json.loads(result.output)
    assert 'accuracy' in json_data
    
def test_evaluate_command_table_output():
    """Evaluate command outputs formatted table."""
    result = cli_runner.invoke(evaluate_command, ['--format', 'table'])
    assert '|' in result.output or '+' in result.output
    
def test_progress_indicator_output():
    """Progress indicator shown during training."""
    # Mock trainer with progress callback
    result = cli_runner.invoke(train_command, [...])
    assert 'Epoch' in result.output or '%' in result.output
    
def test_very_long_output_truncation():
    """Very long outputs truncated to avoid display issues."""
    # Generate very long model name
    # Verify: truncated with ellipsis or similar
```

**Success Criteria:**
- [ ] 10-12 tests written
- [ ] All tests passing
- [ ] Coverage increase: +2-2.5%

---

### GAP-3.2.3: Error Message Consistency (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 1.5-2%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- Error messages inconsistent across commands
- Error context not provided
- Error codes not standardized
- User-facing errors mixed with technical errors

**Target State:**
- All errors follow consistent format
- Error messages include context
- Error codes standardized
- User-friendly error text

**Test Patterns:**
```python
def test_error_message_format():
    """Error messages follow standard format."""
    result = cli_runner.invoke(train_command, ['--config', 'missing.yaml'])
    # Format: "ERROR: Description of what went wrong. Hint: try..."
    assert result.output.startswith('ERROR:') or 'error' in result.output.lower()
    
def test_file_not_found_error():
    """File not found errors are user-friendly."""
    result = cli_runner.invoke(train_command, ['--config', '/nonexistent/path.yaml'])
    assert 'File not found' in result.output or 'not found' in result.output
    assert '/nonexistent/path.yaml' in result.output  # Include path
    
def test_permission_error_message():
    """Permission denied shows clear message."""
    with patch('os.access', return_value=False):
        result = cli_runner.invoke(deploy_command, [...])
        assert 'permission' in result.output.lower() or 'access' in result.output.lower()
        
def test_error_code_consistency():
    """Error codes are consistent across similar errors."""
    # FileNotFoundError → exit code 1
    # PermissionError → exit code 1
    # Invalid argument → exit code 2
    pass
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1.5-2%

---

### GAP-3.2.4: Subcommand Routing (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1.5-2%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- Subcommand dispatch not tested
- Unknown subcommands not handled
- Subcommand aliases not validated

**Target State:**
- Test each subcommand routes correctly
- Test unknown subcommand error
- Test subcommand aliases work

**Test Patterns:**
```python
def test_train_subcommand_routes_correctly():
    """Train subcommand invokes trainer."""
    # Mock trainer
    with patch('src.codex_ml.cli.Trainer') as mock_trainer:
        result = cli_runner.invoke(cli_group, ['train', '--config', 'test.yaml'])
        assert mock_trainer.called
        
def test_evaluate_subcommand_routes_correctly():
    """Evaluate subcommand invokes evaluator."""
    # Similar to train
    
def test_unknown_subcommand_error():
    """Unknown subcommand shows error and help."""
    result = cli_runner.invoke(cli_group, ['unknown_command'])
    assert result.exit_code != 0
    assert 'No such command' in result.output or 'unknown' in result.output.lower()
    
def test_subcommand_alias():
    """Subcommand aliases work (e.g., 'tr' for 'train')."""
    # If aliases defined, test they work
    result = cli_runner.invoke(cli_group, ['tr', '--config', 'test.yaml'])
    assert result.exit_code == 0 or 'alias' in result.output.lower()
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1.5-2%

---

### GAP-3.2.5: Help Text & Documentation (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 6-8 tests, 2-3 hours  

**Current State:**
- Help text incomplete for many commands
- Examples not provided
- Option descriptions vague

**Target State:**
- Help text complete for all commands
- Examples included in help
- Option descriptions clear and actionable

**Test Patterns:**
```python
def test_main_help_shows_all_subcommands():
    """Main help lists all available subcommands."""
    result = cli_runner.invoke(cli_group, ['--help'])
    assert 'train' in result.output
    assert 'evaluate' in result.output
    assert 'deploy' in result.output
    
def test_train_help_complete():
    """Train command help includes all important options."""
    result = cli_runner.invoke(train_command, ['--help'])
    assert '--config' in result.output
    assert '--output-dir' in result.output
    assert '--epochs' in result.output
    assert 'configuration file' in result.output.lower()
    
def test_option_descriptions_are_helpful():
    """Option descriptions explain what they do."""
    result = cli_runner.invoke(train_command, ['--help'])
    # Descriptions should not be empty or placeholder text
    assert 'optional arguments:' in result.output or '-' in result.output
    
def test_help_shows_examples():
    """Help text includes usage examples."""
    result = cli_runner.invoke(train_command, ['--help'])
    # Examples section or at least one example in description
    assert 'example' in result.output.lower() or 'Usage:' in result.output
```

**Success Criteria:**
- [ ] 6-8 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.2.6: Role-Based Access Control (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 6-8 tests, 2-3 hours  

**Current State:**
- No authorization checks in commands
- Deploy/admin commands not protected
- User roles not validated

**Target State:**
- Commands check user authorization
- Unauthorized users get clear error
- Admin-only commands protected

**Test Patterns:**
```python
def test_deploy_command_requires_admin_role(mocker):
    """Deploy command checks admin authorization."""
    mocker.patch('src.codex_ml.cli.get_current_user',
                 return_value={'role': 'viewer'})
    
    result = cli_runner.invoke(deploy_command, ['--model', 'test.pt'])
    assert result.exit_code != 0
    assert 'permission' in result.output.lower()
    
def test_deploy_command_allowed_for_admin(mocker):
    """Admin user can deploy."""
    mocker.patch('src.codex_ml.cli.get_current_user',
                 return_value={'role': 'admin'})
    
    result = cli_runner.invoke(deploy_command, ['--model', 'test.pt'])
    # Should not fail due to permissions
    assert 'permission' not in result.output.lower()
    
def test_train_command_requires_trainer_role_or_higher(mocker):
    """Train command requires trainer role."""
    mocker.patch('src.codex_ml.cli.get_current_user',
                 return_value={'role': 'viewer'})
    
    result = cli_runner.invoke(train_command, ['--config', 'test.yaml'])
    assert result.exit_code != 0 or 'permission' in result.output.lower()
```

**Success Criteria:**
- [ ] 6-8 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.2.7: Configuration File Handling (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 0.5-1%  
**Effort Estimate:** 4-6 tests, 2 hours  

**Current State:**
- Config file parsing not error-tested
- Invalid YAML not handled
- Missing required fields not checked

**Target State:**
- Graceful error handling for invalid config
- Helpful error messages
- Config validation before use

**Test Patterns:**
```python
def test_missing_config_file_error():
    """Missing config file shows helpful error."""
    result = cli_runner.invoke(train_command, ['--config', '/missing.yaml'])
    assert result.exit_code != 0
    assert 'config' in result.output.lower()
    
def test_invalid_yaml_config():
    """Invalid YAML in config file handled."""
    with patch('yaml.safe_load', side_effect=yaml.YAMLError("Invalid YAML")):
        result = cli_runner.invoke(train_command, ['--config', 'bad.yaml'])
        assert result.exit_code != 0
        assert 'parse' in result.output.lower() or 'yaml' in result.output.lower()
        
def test_missing_required_config_field():
    """Missing required config field detected."""
    # Load config missing 'learning_rate'
    # Verify: error about missing field
    
def test_config_field_type_validation():
    """Config field types validated."""
    # learning_rate: "invalid" (string instead of number)
    # Verify: error about type mismatch
```

**Success Criteria:**
- [ ] 4-6 tests written
- [ ] All tests passing
- [ ] Coverage increase: +0.5-1%

---

## Test Generation Implementation Guide

### Step 1: Set Up Test File Structure

```python
# tests/codex_ml/test_cli_comprehensive.py
"""Comprehensive tests for ML CLI interface (Lane 3.2)."""

import pytest
import json
import yaml
from click.testing import CliRunner
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Imports from CLI module
from src.codex_ml.cli import (
    cli_group,
    train_command,
    evaluate_command,
    deploy_command
)

# ============================================================================
# Fixtures (Shared test setup)
# ============================================================================

@pytest.fixture
def cli_runner():
    """CLI test runner."""
    return CliRunner()

@pytest.fixture
def mock_trainer(mocker):
    """Mock trainer for CLI commands."""
    trainer = MagicMock()
    trainer.train.return_value = {'loss': 0.1}
    mocker.patch('src.codex_ml.cli.Trainer', return_value=trainer)
    return trainer

@pytest.fixture
def mock_config(tmp_path):
    """Mock training config file."""
    config = {
        'epochs': 10,
        'batch_size': 32,
        'learning_rate': 0.001,
    }
    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config, f)
    return config_file

@pytest.fixture
def mock_model(tmp_path):
    """Mock model file."""
    model_file = tmp_path / 'model.pt'
    model_file.write_text('mock model')
    return model_file

# ============================================================================
# GAP-3.2.1 Tests: Argument Parsing
# ============================================================================

class TestArgumentParsing:
    """Tests for CLI argument parsing."""
    
    def test_train_with_valid_arguments(self, cli_runner, mock_config):
        """Train command accepts valid arguments."""
        result = cli_runner.invoke(train_command, [
            '--config', str(mock_config),
            '--output-dir', '/tmp/output'
        ])
        assert result.exit_code == 0
    
    def test_train_invalid_learning_rate_type(self, cli_runner, mock_config):
        """Invalid learning rate type rejected."""
        result = cli_runner.invoke(train_command, [
            '--config', str(mock_config),
            '--learning-rate', 'invalid'
        ])
        assert result.exit_code != 0
    
    def test_required_config_argument_missing(self, cli_runner):
        """Missing required config argument caught."""
        result = cli_runner.invoke(train_command, [])
        assert result.exit_code != 0

# Continue with remaining gap tests...
```

### Step 2: Implement Gap Tests

For each GAP section above, implement corresponding test class. Follow this structure:

```python
class TestGAPName:
    """Tests for specific coverage gap."""
    
    def test_core_functionality(self):
        """Core behavior works."""
        # Setup, invoke, assert
        pass
    
    def test_edge_case_1(self):
        """Edge case 1 handled."""
        pass
```

### Step 3: Run & Validate

```bash
# Run tests locally
pytest tests/codex_ml/test_cli_comprehensive.py -v --tb=short

# Check coverage
pytest tests/codex_ml/test_cli_comprehensive.py \
    --cov=src/codex_ml/cli --cov-report=term

# Expect: Coverage 10% → 60%+
```

---

## Lane 3.2 Success Metrics

### Coverage Metrics
| Module | Baseline | Target | Success |
|--------|----------|--------|---------|
| `src/codex_ml/cli/__init__.py` | 5% | 60% | ✅ if ≥60% |
| `src/codex_ml/cli/commands.py` | 12% | 60% | ✅ if ≥60% |
| `src/codex_ml/cli/parsers.py` | 8% | 60% | ✅ if ≥60% |
| `src/codex_ml/cli/formatters.py` | 6% | 60% | ✅ if ≥60% |
| **Overall** | **10.0%** | **60%** | ✅ if ≥60% |

### Test Metrics
| Metric | Target | Status |
|--------|--------|--------|
| **Tests Written** | 50-70 | ⏳ in_progress |
| **Tests Passing** | 100% | ⏳ in_progress |
| **Pass Rate** | ≥95% | ⏳ in_progress |
| **Execution Time** | <3 min | ⏳ in_progress |

---

## Timeline & Milestones

| Phase | Start | Duration | Tasks | Owner |
|-------|-------|----------|-------|-------|
| **Setup** | T+0h | 1-2h | Fixture setup, CliRunner config | agent |
| **Development Phase 1** | T+2h | 7h | GAP-3.2.1 through GAP-3.2.4 | agent |
| **Checkpoint 1** | T+9h | 2h | Local validation | agent |
| **Development Phase 2** | T+11h | 7h | GAP-3.2.5 through GAP-3.2.7 | agent |
| **CI Validation** | T+18h | 3h | Full test suite, coverage report | CI |
| **Sign-off** | T+21h | 1h | Documentation, metrics | agent |

**Total Duration:** 18-22 hours  
**Parallel with:** Lane 3.1 & Lane 3.3  
**Ready for:** Phase 6 Wave 4  

---

## Integration Notes

### Dependencies Within Lane
- ✅ No inter-test dependencies
- ✅ Each GAP independent
- ✅ Fixtures fully isolated

### Parallel Execution
- ✅ Can run in parallel with Lane 3.1 & 3.3
- ✅ No shared resources
- ✅ Separate test files

---

## Activation Checklist

- [ ] Phase 6 Wave 1 promoted to main
- [ ] Phase 5 Lane 5.1 report reviewed
- [ ] Test file template created
- [ ] CliRunner fixtures validated
- [ ] Mock objects prepared
- [ ] CI gates configured
- [ ] Ready for execution

---

**Lane Owner:** unified-coverage-agent  
**Status:** ✅ READY FOR EXECUTION  
**Estimated Completion:** 2026-06-30  

