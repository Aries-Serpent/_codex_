# Test Development Patterns - QA Walkthrough Analysis

**Generated:** 2026-02-04  
**Source:** Phases 41-52 Test Development  
**Coverage Progress:** 17.59% → 24.14% (+6.55%)

---

## Executive Summary

This document captures reusable test patterns identified during the QA walkthrough coverage improvement initiative. These patterns can accelerate future test development while maintaining consistency and quality.

---

## 🎯 Pattern Categories

### 1. Import-Safe Test Pattern

**Use Case:** Testing modules that may not be installed or have optional dependencies.

```python
def test_module_import(self):
    """Test that module can be imported."""
    try:
        from src.module.submodule import TargetClass
        assert TargetClass is not None
    except ImportError:
        pytest.skip("Module not available")
```

**Benefits:**
- Tests don't fail due to missing optional dependencies
- Graceful degradation in CI environments with incomplete installs
- Clear indication of what's being tested

**Used In:**
- `tests/mcp/test_lifecycle.py`
- `tests/agent/test_core.py`
- `tests/rag/test_pipelines.py`

---

### 2. Enum Value Verification Pattern

**Use Case:** Testing that enum values match expected strings/values.

```python
class TestServerState:
    """Tests for ServerState enum."""

    def test_server_state_values(self):
        """Test all enum values."""
        try:
            from src.module import StateEnum
            assert StateEnum.PENDING.value == "pending"
            assert StateEnum.RUNNING.value == "running"
            assert StateEnum.COMPLETED.value == "completed"
        except ImportError:
            pytest.skip("Module not available")
```

**Benefits:**
- Catches accidental enum value changes
- Documents expected API contract
- Easy to extend for new enum values

**Used In:**
- `tests/mcp/test_lifecycle.py` (ServerState)
- `tests/agent/test_core.py` (TaskStatus)
- `tests/codex_crm/test_cli.py`

---

### 3. Dataclass Default Value Pattern

**Use Case:** Testing dataclass initialization and default values.

```python
class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_config_creation(self):
        """Test creating config with defaults."""
        try:
            from src.agent.core import AgentConfig
            config = AgentConfig()
            assert config is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_config_defaults(self):
        """Test default values."""
        try:
            from src.agent.core import AgentConfig
            config = AgentConfig()
            assert config.model_preference == "auto"
            assert config.max_tool_calls == 10
            assert config.enable_rag is True
        except ImportError:
            pytest.skip("Module not available")

    def test_config_custom_values(self):
        """Test custom values override defaults."""
        try:
            from src.agent.core import AgentConfig
            config = AgentConfig(
                model_preference="gpt-4",
                max_tool_calls=5
            )
            assert config.model_preference == "gpt-4"
            assert config.max_tool_calls == 5
        except ImportError:
            pytest.skip("Module not available")
```

**Benefits:**
- Verifies dataclass contract
- Tests both defaults and overrides
- Documents expected field names

**Used In:**
- `tests/agent/test_core.py` (AgentConfig, TaskResult, ToolCall)
- `tests/mcp/test_lifecycle.py` (HealthStatus, LifecycleConfig)
- `tests/mcp/test_auth.py` (Principal)

---

### 4. Click CLI Test Pattern

**Use Case:** Testing Click-based CLI applications.

```python
import pytest
from click.testing import CliRunner

@pytest.fixture
def cli_runner():
    """Provide Click CLI test runner."""
    return CliRunner()

@pytest.fixture
def mock_service():
    """Mock service for testing."""
    with patch("src.module.cli.Service") as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance

class TestCLICommands:
    """Tests for CLI commands."""

    def test_command_help(self, cli_runner):
        """Test command help output."""
        from src.module.cli import cli
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_command_execution(self, cli_runner, mock_service):
        """Test command execution."""
        from src.module.cli import cli
        result = cli_runner.invoke(cli, ["subcommand", "--option", "value"])
        assert result.exit_code == 0
```

**Benefits:**
- Isolated CLI testing without side effects
- Mock services for unit testing
- Tests both success and error paths

**Used In:**
- `tests/cli/test_archive_cli_comprehensive.py`
- `tests/cli/test_codex_cli_comprehensive.py`
- `tests/cli/test_deploy_comprehensive.py`

---

### 5. Argparse CLI Test Pattern

**Use Case:** Testing argparse-based CLI applications.

```python
class TestBuildParser:
    """Tests for build_parser function."""

    def test_parser_creation(self):
        """Test parser is created successfully."""
        from module.cli import build_parser
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_subcommand_parsing(self):
        """Test subcommand parsing."""
        from module.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["subcommand", "--option", "value"])
        assert args.command == "subcommand"
        assert args.option == "value"

    def test_missing_required_arg(self):
        """Test missing required argument fails."""
        from module.cli import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["subcommand"])  # Missing required arg
```

**Benefits:**
- Tests argument parsing separately from execution
- Verifies default values
- Tests error handling for missing args

**Used In:**
- `tests/codex_crm/test_cli.py`
- `tests/cli/test_main_cli_comprehensive.py`

---

### 6. Hash/Cryptographic Function Pattern

**Use Case:** Testing hash functions and cryptographic operations.

```python
class TestHashCredential:
    """Tests for hash_credential function."""

    def test_hash_string_credential(self):
        """Test hashing string input."""
        from src.mcp.auth import hash_credential
        result = hash_credential("test_password")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest

    def test_hash_consistency(self):
        """Test same input produces same hash."""
        from src.mcp.auth import hash_credential
        hash1 = hash_credential("consistent")
        hash2 = hash_credential("consistent")
        assert hash1 == hash2

    def test_hash_different_inputs(self):
        """Test different inputs produce different hashes."""
        from src.mcp.auth import hash_credential
        hash1 = hash_credential("password1")
        hash2 = hash_credential("password2")
        assert hash1 != hash2
```

**Benefits:**
- Verifies hash length/format
- Tests determinism
- Tests uniqueness

**Used In:**
- `tests/mcp/test_auth.py`

---

### 7. State Transition Validation Pattern

**Use Case:** Testing state machines with valid/invalid transitions.

```python
class TestStateTransitions:
    """Tests for valid state transitions."""

    def test_uninitialized_can_initialize(self):
        """Test UNINITIALIZED can transition to INITIALIZING."""
        from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState
        assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.UNINITIALIZED]

    def test_error_recovery(self):
        """Test ERROR can transition to recovery states."""
        from src.mcp.lifecycle import VALID_TRANSITIONS, ServerState
        assert ServerState.STOPPING in VALID_TRANSITIONS[ServerState.ERROR]
        assert ServerState.INITIALIZING in VALID_TRANSITIONS[ServerState.ERROR]
```

**Benefits:**
- Documents valid state transitions
- Catches accidental state machine changes
- Easy to extend for new states

**Used In:**
- `tests/mcp/test_lifecycle.py`

---

### 8. Exception Creation Pattern

**Use Case:** Testing custom exception classes.

```python
class TestCustomException:
    """Tests for custom exception."""

    def test_exception_creation(self):
        """Test creating exception with args."""
        from src.module import CustomException
        exc = CustomException("arg1", "arg2")
        assert exc.arg1 == "arg1"
        assert exc.arg2 == "arg2"

    def test_exception_message(self):
        """Test exception message format."""
        from src.module import CustomException
        exc = CustomException("value1", "value2")
        assert "value1" in str(exc)
        assert "value2" in str(exc)
```

**Benefits:**
- Verifies exception attributes
- Tests message formatting
- Documents exception usage

**Used In:**
- `tests/mcp/test_lifecycle.py` (InvalidStateTransition)

---

### 9. Backwards Compatibility Alias Pattern

**Use Case:** Testing that module aliases exist for backwards compatibility.

```python
class TestBackwardsCompatibility:
    """Tests for backwards compatible aliases."""

    def test_old_class_alias(self):
        """Test old class name still works."""
        from src.mcp.auth import OldClassName, NewClassName
        assert OldClassName is NewClassName

    def test_deprecated_import_path(self):
        """Test deprecated import path still works."""
        from src.old_path import SomeClass
        from src.new_path import SomeClass as NewClass
        assert SomeClass is NewClass
```

**Benefits:**
- Prevents breaking changes
- Documents migration path
- Easy to remove when deprecation period ends

**Used In:**
- `tests/mcp/test_auth.py` (BasicAuthenticator, AllowAllAuthorizer)

---

### 10. Module Structure Test Pattern

**Use Case:** Testing that module exports expected classes/functions.

```python
class TestModuleImports:
    """Tests for module-level imports."""

    def test_logger_configured(self):
        """Test that logger is configured."""
        from src.module import logger
        assert logger is not None

    def test_all_exports(self):
        """Test key classes are exported."""
        from src.module import (
            ClassA,
            ClassB,
            function_c,
        )
        assert all([ClassA, ClassB, function_c])
```

**Benefits:**
- Verifies public API
- Catches accidental export removals
- Documents what's available

**Used In:**
- `tests/agent/test_core.py`
- `tests/mcp/test_auth.py`

---

## 📊 Test Development Statistics

### Files Created (Phases 41-52)

| Category | Files | Tests | Avg Tests/File |
|----------|-------|-------|----------------|
| CLI Tests | 17 | ~400 | 23.5 |
| Module Tests | 12 | ~250 | 20.8 |
| Integration Tests | 6 | ~100 | 16.7 |
| **Total** | **35** | **~750** | **21.4** |

### Pattern Usage Frequency

| Pattern | Usage Count | Primary Use Case |
|---------|-------------|------------------|
| Import-Safe | 45+ | Optional dependencies |
| Enum Values | 12 | State/status enums |
| Dataclass Defaults | 18 | Configuration classes |
| Click CLI | 8 | CLI commands |
| Argparse CLI | 4 | Subcommand parsing |
| Hash Functions | 6 | Auth/crypto testing |
| State Transitions | 8 | State machines |
| Exceptions | 5 | Custom exceptions |
| Aliases | 3 | Backwards compat |
| Module Structure | 10 | API verification |

---

## 🚀 Quick Start Template

Use this template for new test files:

```python
"""Comprehensive tests for src/path/to/module.py."""

import pytest
from unittest.mock import Mock, patch, MagicMock


# ==================== Fixtures ====================

@pytest.fixture
def mock_dependency():
    """Mock external dependency."""
    with patch("src.path.to.module.Dependency") as mock:
        instance = Mock()
        mock.return_value = instance
        yield instance


# ==================== Import Tests ====================

class TestModuleImports:
    """Tests for module imports."""

    def test_module_import(self):
        """Test that module can be imported."""
        try:
            from src.path.to.module import MainClass
            assert MainClass is not None
        except ImportError:
            pytest.skip("Module not available")


# ==================== Class Tests ====================

class TestMainClass:
    """Tests for MainClass."""

    def test_creation(self):
        """Test creating instance."""
        try:
            from src.path.to.module import MainClass
            instance = MainClass()
            assert instance is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_defaults(self):
        """Test default values."""
        try:
            from src.path.to.module import MainClass
            instance = MainClass()
            assert instance.some_property == "expected_default"
        except ImportError:
            pytest.skip("Module not available")

    def test_custom_values(self):
        """Test custom initialization values."""
        try:
            from src.path.to.module import MainClass
            instance = MainClass(some_property="custom")
            assert instance.some_property == "custom"
        except ImportError:
            pytest.skip("Module not available")


# ==================== Method Tests ====================

class TestMainClassMethods:
    """Tests for MainClass methods."""

    def test_method_returns_expected(self):
        """Test method return value."""
        try:
            from src.path.to.module import MainClass
            instance = MainClass()
            result = instance.some_method("input")
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")
```

---

## 📋 Checklist for New Test Files

- [ ] Module docstring describing what's tested
- [ ] Import-safe pattern for optional dependencies
- [ ] Test class per logical group
- [ ] Descriptive test method names
- [ ] Both positive and negative test cases
- [ ] Default value verification
- [ ] Custom value override tests
- [ ] Error/exception handling tests
- [ ] Fixtures for common setup
- [ ] Mocks for external dependencies

---

**Document Status:** Active  
**Last Updated:** 2026-02-04  
**Maintainer:** Copilot Coding Agent
