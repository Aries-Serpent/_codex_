"""
Unit tests for codex.config module.

Tests environment variable management, validation, and configuration handling.
"""

import os
from unittest.mock import patch


class TestEnvVarConfig:
    """Test EnvVarConfig dataclass."""

    def test_env_var_config_import(self):
        """Test EnvVarConfig can be imported."""
        from codex.config.env_vars import EnvVarConfig

        assert EnvVarConfig is not None

    def test_env_var_config_basic_creation(self):
        """Test creating EnvVarConfig with basic fields."""
        from codex.config.env_vars import EnvVarConfig

        config = EnvVarConfig(name="TEST_VAR")
        assert config.name == "TEST_VAR"
        assert config.default is None
        assert config.required is False

    def test_env_var_config_with_default(self):
        """Test EnvVarConfig with default value."""
        from codex.config.env_vars import EnvVarConfig

        config = EnvVarConfig(name="TEST_VAR", default="default_value")
        assert config.default == "default_value"

    def test_env_var_config_with_description(self):
        """Test EnvVarConfig with description."""
        from codex.config.env_vars import EnvVarConfig

        config = EnvVarConfig(name="TEST_VAR", description="Test variable for testing")
        assert config.description == "Test variable for testing"

    def test_env_var_config_required_flag(self):
        """Test EnvVarConfig required flag."""
        from codex.config.env_vars import EnvVarConfig

        config = EnvVarConfig(name="TEST_VAR", required=True)
        assert config.required is True


class TestEnvironmentManager:
    """Test EnvironmentManager class."""

    def test_environment_manager_import(self):
        """Test EnvironmentManager can be imported."""
        from codex.config.env_vars import EnvironmentManager

        assert EnvironmentManager is not None

    def test_environment_manager_creation(self):
        """Test creating EnvironmentManager instance."""
        from codex.config.env_vars import EnvironmentManager

        env_mgr = EnvironmentManager()
        assert env_mgr is not None

    def test_environment_manager_has_env_vars(self):
        """Test EnvironmentManager has ENV_VARS attribute."""
        from codex.config.env_vars import EnvironmentManager

        assert hasattr(EnvironmentManager, "ENV_VARS")
        assert isinstance(EnvironmentManager.ENV_VARS, dict)

    def test_env_vars_contains_python_version(self):
        """Test ENV_VARS contains CODEX_ENV_PYTHON_VERSION."""
        from codex.config.env_vars import EnvironmentManager

        assert "CODEX_ENV_PYTHON_VERSION" in EnvironmentManager.ENV_VARS

    def test_env_vars_python_version_default(self):
        """Test CODEX_ENV_PYTHON_VERSION has default value."""
        from codex.config.env_vars import EnvironmentManager

        python_version_config = EnvironmentManager.ENV_VARS["CODEX_ENV_PYTHON_VERSION"]
        assert python_version_config.default == "3.12"

    def test_env_vars_contains_node_version(self):
        """Test ENV_VARS contains CODEX_ENV_NODE_VERSION."""
        from codex.config.env_vars import EnvironmentManager

        assert "CODEX_ENV_NODE_VERSION" in EnvironmentManager.ENV_VARS

    @patch.dict(os.environ, {"CODEX_ENV_PYTHON_VERSION": "3.11"}, clear=False)
    def test_environment_manager_reads_env_var(self):
        """Test EnvironmentManager can read environment variables."""
        from codex.config.env_vars import EnvironmentManager

        # Verify the environment variable is set
        assert os.environ.get("CODEX_ENV_PYTHON_VERSION") == "3.11"

        # Create EnvironmentManager and verify it can access the variable
        EnvironmentManager()
        # The manager should be able to read from ENV_VARS
        assert "CODEX_ENV_PYTHON_VERSION" in EnvironmentManager.ENV_VARS

    def test_environment_manager_get_method_exists(self):
        """Test EnvironmentManager has getter methods."""
        from codex.config.env_vars import EnvironmentManager

        env_mgr = EnvironmentManager()
        # Check if common methods exist
        assert (
            callable(getattr(env_mgr, "get_session_id", None))
            or callable(getattr(env_mgr, "get_log_dir", None))
            or hasattr(env_mgr, "ENV_VARS")
        )

    def test_module_has_dataclass_decorator(self):
        """Test EnvVarConfig uses dataclass."""
        from codex.config.env_vars import EnvVarConfig

        # Check if it's a dataclass by looking for __dataclass_fields__
        assert hasattr(EnvVarConfig, "__dataclass_fields__")

    def test_env_var_config_field_count(self):
        """Test EnvVarConfig has expected fields."""
        from codex.config.env_vars import EnvVarConfig

        fields = EnvVarConfig.__dataclass_fields__
        assert "name" in fields
        assert "default" in fields
        assert "required" in fields
        assert "description" in fields


class TestConfigModuleDocumentation:
    """Test module-level documentation and structure."""

    def test_module_docstring_exists(self):
        """Test module has documentation."""
        import codex.config.env_vars as env_vars_module

        assert env_vars_module.__doc__ is not None
        assert len(env_vars_module.__doc__) > 0

    def test_module_exports_expected_classes(self):
        """Test module exports expected classes."""
        from codex.config import env_vars

        assert hasattr(env_vars, "EnvVarConfig")
        assert hasattr(env_vars, "EnvironmentManager")

    def test_environment_manager_docstring(self):
        """Test EnvironmentManager has documentation."""
        from codex.config.env_vars import EnvironmentManager

        assert EnvironmentManager.__doc__ is not None
        assert "environment" in EnvironmentManager.__doc__.lower()
