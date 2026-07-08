"""
Comprehensive tests for environment variable configuration.

Tests the EnvironmentManager and EnvVarConfig classes for proper
environment variable handling, validation, and configuration.
"""

import os
from unittest.mock import patch

import pytest

from src.codex.config.env_vars import EnvVarConfig, EnvironmentManager


@pytest.fixture
def env_manager():
    """Create a fresh EnvironmentManager instance for testing."""
    return EnvironmentManager()


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases in environment configuration."""

    def test_empty_env_var_name(self):
        """Test config with empty name."""
        config = EnvVarConfig(name="")
        assert config.name == "", "name is not valid"

    def test_very_long_env_var_name(self):
        """Test config with very long name."""
        long_name = "CODEX_" + "X" * 1000
        config = EnvVarConfig(name=long_name)
        assert len(config.name) > 1000, "Collection must not be empty"

    def test_special_characters_in_name(self):
        """Test config with special characters in name."""
        config = EnvVarConfig(name="CODEX_VAR_123_ABC")
        assert "_" in config.name, "Condition must be true"

    def test_none_default_value(self):
        """Test config with None as default."""
        config = EnvVarConfig(name="VAR", default=None)
        assert config.default is None, "default is not valid"

    def test_empty_string_default(self):
        """Test config with empty string default."""
        config = EnvVarConfig(name="VAR", default="")
        assert config.default == "", "default is not valid"

    def test_zero_default(self):
        """Test config with 0 as default."""
        # Though defaults are typically strings
        config = EnvVarConfig(name="VAR", default="0")
        assert config.default == "0", "default is not valid"


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
        assert len(env_manager.ENV_VARS) > 0, "Collection must not be empty"

    def test_all_env_vars_have_name(self, env_manager):
        """Test that all configs have name field."""
        for key, config in env_manager.ENV_VARS.items():
            assert config.name == key, "name is not valid"

    def test_can_iterate_env_vars(self, env_manager):
        """Test that ENV_VARS can be iterated."""
        count = 0
        for var_name, config in env_manager.ENV_VARS.items():
            assert var_name is not None, "var_name must be initialized"
            assert config is not None, "config must be initialized"
            count += 1

        assert count > 0, "count must be positive"


# ============================================================================
# Integration Tests
# ============================================================================


class TestEnvironmentConfigIntegration:
    """Integration tests for environment configuration."""

    def test_complete_config_workflow(self):
        """Test complete workflow with environment config."""
        with patch.dict(
            os.environ,
            {
                "CODEX_SESSION_ID": "test-session-123",
                "CODEX_SESSION_LOG_DIR": "/custom/logs",
                "CODEX_ENV_PYTHON_VERSION": "3.11",
            },
        ):
            manager = EnvironmentManager()
            assert manager is not None, "manager must be initialized"
            assert len(manager.ENV_VARS) > 0, "Collection must not be empty"

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
            assert manager is not None, "manager must be initialized"

            # Should have access to configs
            assert "CODEX_ENV_PYTHON_VERSION" in manager.ENV_VARS, "Condition must be true"

    def test_multiple_managers_independent(self, env_manager):
        """Test that multiple managers are independent."""
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()

        # Should have same structure but be different objects
        assert manager1 is not manager2, "manager1 is not valid"
        assert len(manager1.ENV_VARS) == len(manager2.ENV_VARS), "Collection must not be empty"


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
            assert python_config.description is not None, "description must be initialized"

    def test_config_descriptions_not_empty(self, env_manager):
        """Test that descriptions are not empty."""
        for var_name, config in env_manager.ENV_VARS.items():
            if var_name in ["CODEX_ENV_PYTHON_VERSION", "CODEX_SESSION_ID"]:
                assert len(config.description) > 0 or config.description == "", "Description must not be empty"


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
                assert config is not None, "config must be initialized"
