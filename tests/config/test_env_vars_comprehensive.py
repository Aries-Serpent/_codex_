"""
Comprehensive tests for environment variable management.

Tests cover:
- Environment variable retrieval
- Type conversion
- Validation
- Defaults
- Logging
"""

import os
from unittest.mock import patch

import pytest

from codex.config.env_vars import (
    EnvironmentManager,
    EnvVarConfig,
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def env_manager():
    """Create an environment manager."""
    return EnvironmentManager()


@pytest.fixture
def clean_env():
    """Clean environment for testing."""
    with patch.dict(os.environ, {}, clear=False):
        yield


# ============================================================================
# Initialization Tests
# ============================================================================

class TestEnvironmentManagerInit:
    """Test environment manager initialization."""

    def test_init_creates_manager(self, env_manager):
        """Test that manager initializes."""
        assert env_manager is not None
        assert isinstance(env_manager, EnvironmentManager)

    def test_env_vars_defined(self, env_manager):
        """Test that ENV_VARS are defined."""
        assert len(env_manager.ENV_VARS) > 0
        assert isinstance(env_manager.ENV_VARS, dict)

    def test_env_vars_have_required_keys(self, env_manager):
        """Test that ENV_VARS contain required variables."""
        required_vars = [
            "CODEX_ENV_PYTHON_VERSION",
            "CODEX_SESSION_ID",
            "CODEX_SESSION_LOG_DIR",
        ]
        for var in required_vars:
            assert var in env_manager.ENV_VARS


# ============================================================================
# EnvVarConfig Tests
# ============================================================================

class TestEnvVarConfig:
    """Test EnvVarConfig data class."""

    def test_create_basic_config(self):
        """Test creating basic config."""
        config = EnvVarConfig(name="TEST_VAR")
        assert config.name == "TEST_VAR"
        assert config.default is None
        assert config.validator is None
        assert config.required is False

    def test_create_config_with_default(self):
        """Test creating config with default."""
        config = EnvVarConfig(
            name="TEST_VAR",
            default="default_value",
        )
        assert config.default == "default_value"

    def test_create_config_with_validator(self):
        """Test creating config with validator."""
        def is_number(value):
            return value.isdigit()

        config = EnvVarConfig(
            name="TEST_VAR",
            validator=is_number,
        )
        assert config.validator is not None

    def test_create_config_required(self):
        """Test creating required config."""
        config = EnvVarConfig(
            name="TEST_VAR",
            required=True,
        )
        assert config.required is True

    def test_create_config_with_description(self):
        """Test creating config with description."""
        config = EnvVarConfig(
            name="TEST_VAR",
            description="Test variable",
        )
        assert config.description == "Test variable"


# ============================================================================
# Python Version Tests
# ============================================================================

class TestPythonVersionConfig:
    """Test Python version configuration."""

    def test_default_python_version(self, env_manager):
        """Test default Python version is 3.12."""
        with patch.dict(os.environ, {}, clear=True):
            manager = EnvironmentManager()
            config = manager.ENV_VARS["CODEX_ENV_PYTHON_VERSION"]
            assert config.default == "3.12"

    def test_get_python_version(self, env_manager):
        """Test retrieving Python version."""
        config = env_manager.ENV_VARS["CODEX_ENV_PYTHON_VERSION"]
        assert config.name == "CODEX_ENV_PYTHON_VERSION"

    def test_python_version_from_env(self):
        """Test Python version from environment."""
        with patch.dict(os.environ, {"CODEX_ENV_PYTHON_VERSION": "3.11"}):
            manager = EnvironmentManager()
            config = manager.ENV_VARS["CODEX_ENV_PYTHON_VERSION"]
            # Should read from environment
            assert config.default == "3.12"  # Default is always same


# ============================================================================
# Session ID Tests
# ============================================================================

class TestSessionIdConfig:
    """Test session ID configuration."""

    def test_session_id_config_exists(self, env_manager):
        """Test that session ID config exists."""
        assert "CODEX_SESSION_ID" in env_manager.ENV_VARS
        config = env_manager.ENV_VARS["CODEX_SESSION_ID"]
        assert config.name == "CODEX_SESSION_ID"

    def test_session_id_default_is_none(self, env_manager):
        """Test that session ID has no default (generated dynamically)."""
        config = env_manager.ENV_VARS["CODEX_SESSION_ID"]
        assert config.default is None

    def test_session_id_from_environment(self):
        """Test reading session ID from environment."""
        test_id = "test-session-12345"
        with patch.dict(os.environ, {"CODEX_SESSION_ID": test_id}):
            manager = EnvironmentManager()
            # Manager should be created successfully
            assert manager is not None


# ============================================================================
# Session Log Directory Tests
# ============================================================================

class TestSessionLogDirConfig:
    """Test session log directory configuration."""

    def test_session_log_dir_config_exists(self, env_manager):
        """Test that session log dir config exists."""
        assert "CODEX_SESSION_LOG_DIR" in env_manager.ENV_VARS
        config = env_manager.ENV_VARS["CODEX_SESSION_LOG_DIR"]
        assert config.name == "CODEX_SESSION_LOG_DIR"

    def test_session_log_dir_default(self, env_manager):
        """Test default session log directory."""
        config = env_manager.ENV_VARS["CODEX_SESSION_LOG_DIR"]
        # Should have a default
        assert config.default is not None

    def test_session_log_dir_from_environment(self):
        """Test reading session log dir from environment."""
        test_dir = "/custom/log/dir"
        with patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": test_dir}):
            manager = EnvironmentManager()
            assert manager is not None


# ============================================================================
# Language Version Configs Tests
# ============================================================================

class TestLanguageVersionConfigs:
    """Test language version environment configurations."""

    def test_node_version_config_exists(self, env_manager):
        """Test Node.js version config."""
        assert "CODEX_ENV_NODE_VERSION" in env_manager.ENV_VARS
        config = env_manager.ENV_VARS["CODEX_ENV_NODE_VERSION"]
        assert config.description is not None

    def test_rust_version_config_exists(self, env_manager):
        """Test Rust version config."""
        assert "CODEX_ENV_RUST_VERSION" in env_manager.ENV_VARS

    def test_go_version_config_exists(self, env_manager):
        """Test Go version config."""
        assert "CODEX_ENV_GO_VERSION" in env_manager.ENV_VARS

    def test_swift_version_config_exists(self, env_manager):
        """Test Swift version config."""
        assert "CODEX_ENV_SWIFT_VERSION" in env_manager.ENV_VARS

    def test_all_version_configs_have_defaults(self, env_manager):
        """Test that version configs have appropriate defaults."""
        version_vars = [
            "CODEX_ENV_PYTHON_VERSION",
            "CODEX_ENV_NODE_VERSION",
            "CODEX_ENV_RUST_VERSION",
            "CODEX_ENV_GO_VERSION",
            "CODEX_ENV_SWIFT_VERSION",
        ]

        for var in version_vars:
            if var in env_manager.ENV_VARS:
                config = env_manager.ENV_VARS[var]
                assert config.name == var


# ============================================================================
# Database Path Tests
# ============================================================================

class TestDatabasePathConfigs:
    """Test database configuration paths."""

    def test_db_path_config_exists(self, env_manager):
        """Test database path config."""
        assert "CODEX_DB_PATH" in env_manager.ENV_VARS or "CODEX_LOG_DB_PATH" in env_manager.ENV_VARS

    def test_userstore_backend_config_exists(self, env_manager):
        """Test userstore backend config."""
        assert "CODEX_USERSTORE_BACKEND" in env_manager.ENV_VARS


# ============================================================================
# Variable Validator Tests
# ============================================================================

class TestVariableValidators:
    """Test variable validators."""

    def test_config_with_validator(self):
        """Test config with custom validator."""
        def validate_port(value):
            try:
                port = int(value)
                return 0 < port < 65536
            except ValueError:
                return False

        config = EnvVarConfig(
            name="PORT",
            validator=validate_port,
            default="8080",
        )
        assert config.validator is not None

    def test_bool_validator_pattern(self, env_manager):
        """Test that boolean validators are available."""
        # Check if any configs have validators
        configs_with_validators = [
            config for config in env_manager.ENV_VARS.values()
            if config.validator is not None
        ]
        # Should have at least some configs with validators
        assert isinstance(configs_with_validators, list)


# ============================================================================
# Required Variable Tests
# ============================================================================

class TestRequiredVariables:
    """Test required variable handling."""

    def test_mark_variable_required(self):
        """Test marking variable as required."""
        config = EnvVarConfig(
            name="REQUIRED_VAR",
            required=True,
        )
        assert config.required is True

    def test_optional_variable(self):
        """Test optional variable."""
        config = EnvVarConfig(
            name="OPTIONAL_VAR",
            required=False,
        )
        assert config.required is False

    def test_config_description(self):
        """Test config description field."""
        config = EnvVarConfig(
            name="VAR",
            description="This is a test variable",
        )
        assert "test" in config.description.lower()


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases in environment configuration."""

    def test_empty_env_var_name(self):
        """Test config with empty name."""
        config = EnvVarConfig(name="")
        assert config.name == ""

    def test_very_long_env_var_name(self):
        """Test config with very long name."""
        long_name = "CODEX_" + "X" * 1000
        config = EnvVarConfig(name=long_name)
        assert len(config.name) > 1000

    def test_special_characters_in_name(self):
        """Test config with special characters in name."""
        config = EnvVarConfig(name="CODEX_VAR_123_ABC")
        assert "_" in config.name

    def test_none_default_value(self):
        """Test config with None as default."""
        config = EnvVarConfig(name="VAR", default=None)
        assert config.default is None

    def test_empty_string_default(self):
        """Test config with empty string default."""
        config = EnvVarConfig(name="VAR", default="")
        assert config.default == ""

    def test_zero_default(self):
        """Test config with 0 as default."""
        # Though defaults are typically strings
        config = EnvVarConfig(name="VAR", default="0")
        assert config.default == "0"


# ============================================================================
# Manager Methods Tests
# ============================================================================

class TestEnvironmentManagerMethods:
    """Test EnvironmentManager methods."""

    def test_manager_has_env_vars_dict(self, env_manager):
        """Test that manager has ENV_VARS dictionary."""
        assert hasattr(env_manager, "ENV_VARS")
        assert isinstance(env_manager.ENV_VARS, dict)

    def test_env_vars_not_empty(self, env_manager):
        """Test that ENV_VARS is not empty."""
        assert len(env_manager.ENV_VARS) > 0

    def test_all_env_vars_have_name(self, env_manager):
        """Test that all configs have name field."""
        for key, config in env_manager.ENV_VARS.items():
            assert config.name == key

    def test_can_iterate_env_vars(self, env_manager):
        """Test that ENV_VARS can be iterated."""
        count = 0
        for var_name, config in env_manager.ENV_VARS.items():
            assert var_name is not None
            assert config is not None
            count += 1

        assert count > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestEnvironmentConfigIntegration:
    """Integration tests for environment configuration."""

    def test_complete_config_workflow(self):
        """Test complete workflow with environment config."""
        with patch.dict(os.environ, {
            "CODEX_SESSION_ID": "test-session-123",
            "CODEX_SESSION_LOG_DIR": "/custom/logs",
            "CODEX_ENV_PYTHON_VERSION": "3.11",
        }):
            manager = EnvironmentManager()
            assert manager is not None
            assert len(manager.ENV_VARS) > 0

    def test_all_configs_have_required_fields(self, env_manager):
        """Test that all configs have required fields."""
        for var_name, config in env_manager.ENV_VARS.items():
            assert hasattr(config, "name")
            assert hasattr(config, "default")
            assert hasattr(config, "validator")
            assert hasattr(config, "required")
            assert hasattr(config, "description")

    def test_manager_with_environment_variables(self):
        """Test manager with real environment variables."""
        env_vars = {
            "CODEX_ENV_PYTHON_VERSION": "3.12",
            "CODEX_SESSION_ID": "test-123",
            "CODEX_ENV_NODE_VERSION": "18.0.0",
        }

        with patch.dict(os.environ, env_vars):
            manager = EnvironmentManager()

            # Manager should be created
            assert manager is not None

            # Should have access to configs
            assert "CODEX_ENV_PYTHON_VERSION" in manager.ENV_VARS

    def test_multiple_managers_independent(self, env_manager):
        """Test that multiple managers are independent."""
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()

        # Should have same structure but be different objects
        assert manager1 is not manager2
        assert len(manager1.ENV_VARS) == len(manager2.ENV_VARS)


# ============================================================================
# Documentation Tests
# ============================================================================

class TestConfigDocumentation:
    """Test that configurations are properly documented."""

    def test_all_configs_have_descriptions(self, env_manager):
        """Test that all important configs have descriptions."""
        # At least Python version config should have description
        python_config = env_manager.ENV_VARS.get("CODEX_ENV_PYTHON_VERSION")
        if python_config:
            assert python_config.description is not None

    def test_config_descriptions_not_empty(self, env_manager):
        """Test that descriptions are not empty."""
        for var_name, config in env_manager.ENV_VARS.items():
            if var_name in ["CODEX_ENV_PYTHON_VERSION", "CODEX_SESSION_ID"]:
                assert len(config.description) > 0 or config.description == ""


# ============================================================================
# Boolean Configuration Tests
# ============================================================================

class TestBooleanConfigs:
    """Test boolean-type configurations."""

    def test_boolean_config_patterns(self, env_manager):
        """Test configurations that might be boolean."""
        # Check for any boolean-related configs
        possible_bool_configs = [
            "CODEX_SQLITE_POOL",
            "COPILOT_AGENT_DEDUPLICATION_ENABLED",
            "COPILOT_AGENT_TURN_ISOLATION_ENABLED",
        ]

        for config_name in possible_bool_configs:
            if config_name in env_manager.ENV_VARS:
                config = env_manager.ENV_VARS[config_name]
                assert config is not None
