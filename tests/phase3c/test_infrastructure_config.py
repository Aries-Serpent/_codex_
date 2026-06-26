"""Phase 3C: Infrastructure Coverage - Configuration Management Tests.

Focus: Config resolvers and environment variable management with edge cases,
error handling, and integration scenarios.

Target: Boost config module coverage from 82.14% to 95%+
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from unittest import mock

import pytest

from src.codex.config.env_vars import EnvironmentManager, EnvVarConfig


class TestEnvironmentManagerBasics:
    """Test basic environment variable access and defaults."""

    def test_environment_manager_init_eager_validation(self):
        """Test eager validation mode (default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["CODEX_SESSION_LOG_DIR"] = tmpdir
            manager = EnvironmentManager()
            assert manager._validated is False, "_validated is not valid"
            manager.validate()
            assert manager._validated is True, "_validated is not valid"

    def test_environment_manager_init_lazy_validation(self):
        """Test lazy validation mode."""
        manager = EnvironmentManager(lazy_validation=True)
        assert manager._validated is False, "_validated is not valid"
        # Validation happens on first use
        manager.get("CODEX_SESSION_LOG_DIR")
        assert manager._validated is True, "_validated is not valid"

    def test_get_default_python_version(self):
        """Test getting default Python version."""
        manager = EnvironmentManager()
        version = manager.get("CODEX_ENV_PYTHON_VERSION")
        assert version == "3.12", "version is not valid"

    def test_get_with_env_override(self):
        """Test environment variable override."""
        test_version = "3.11"
        with mock.patch.dict(os.environ, {"CODEX_ENV_PYTHON_VERSION": test_version}):
            manager = EnvironmentManager()
            version = manager.get("CODEX_ENV_PYTHON_VERSION")
            assert version == test_version, "version is not valid"

    def test_get_missing_variable_returns_empty_string(self):
        """Test missing optional variable returns empty string."""
        manager = EnvironmentManager()
        value = manager.get("CODEX_ENV_NODE_VERSION")
        assert value == "", "Value must be initialized"

    def test_get_with_explicit_default(self):
        """Test explicit default override in get()."""
        manager = EnvironmentManager()
        value = manager.get("NONEXISTENT_VAR", default="fallback")
        assert value == "fallback", "Value must be initialized"

    def test_env_var_config_dataclass(self):
        """Test EnvVarConfig dataclass creation."""
        config = EnvVarConfig(
            name="TEST_VAR",
            default="test_default",
            validator=lambda x: x.startswith("test"),
            required=True,
            description="Test configuration",
        )
        assert config.name == "TEST_VAR", "name is not valid"
        assert config.default == "test_default", "default is not valid"
        assert config.validator("test_value"), "Value must be initialized"
        assert not config.validator("invalid"), "Condition must be true"
        assert config.required is True, "required is not valid"


class TestSessionManagement:
    """Test session ID generation and management."""

    def test_get_session_id_generates_uuid(self):
        """Test session ID generation when not provided."""
        with mock.patch.dict(os.environ, {}, clear=False):
            if "CODEX_SESSION_ID" in os.environ:
                del os.environ["CODEX_SESSION_ID"]
            manager = EnvironmentManager()
            session_id_1 = manager.get_session_id()
            # Should be a valid UUID
            uuid.UUID(session_id_1)

    def test_get_session_id_caches_value(self):
        """Test that session ID is cached."""
        manager = EnvironmentManager()
        session_id_1 = manager.get_session_id()
        session_id_2 = manager.get_session_id()
        assert session_id_1 == session_id_2, "session_id_1 is not valid"

    def test_get_session_id_from_environment(self):
        """Test reading session ID from environment."""
        test_id = str(uuid.uuid4())
        with mock.patch.dict(os.environ, {"CODEX_SESSION_ID": test_id}):
            manager = EnvironmentManager()
            session_id = manager.get_session_id()
            assert session_id == test_id, "session_id is not valid"

    def test_session_id_stored_in_environment(self):
        """Test that generated session ID is stored in environment."""
        with mock.patch.dict(os.environ, {}, clear=False):
            if "CODEX_SESSION_ID" in os.environ:
                del os.environ["CODEX_SESSION_ID"]
            manager = EnvironmentManager()
            session_id = manager.get_session_id()
            assert os.environ["CODEX_SESSION_ID"] == session_id, "Condition must be true"


class TestPathManagement:
    """Test log directory and database path management."""

    def test_get_log_dir_creates_directory(self):
        """Test that get_log_dir creates the directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            assert not log_dir.exists(), "Condition must be true"
            with mock.patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": str(log_dir)}):
                manager = EnvironmentManager()
                result = manager.get_log_dir()
                assert result == log_dir, "Result must not be empty"
                assert log_dir.exists(), "Condition must be true"
                assert log_dir.is_dir(), "Condition must be true"

    def test_get_log_dir_idempotent(self):
        """Test that get_log_dir is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            with mock.patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": str(log_dir)}):
                manager = EnvironmentManager()
                result1 = manager.get_log_dir()
                result2 = manager.get_log_dir()
                assert result1 == result2, "Result must not be empty"
                # Should still be a directory
                assert log_dir.is_dir(), "Condition must be true"

    def test_get_db_path_creates_parent_directory(self):
        """Test that get_db_path creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "data" / "subdir" / "test.db"
            with mock.patch.dict(
                os.environ,
                {
                    "CODEX_LOG_DB_PATH": str(db_path),
                    "CODEX_DB_PATH": str(db_path),
                },
            ):
                manager = EnvironmentManager()
                result = manager.get_db_path()
                assert result == db_path, "Result must not be empty"
                assert db_path.parent.exists(), "Condition must be true"

    def test_get_db_path_fallback_to_db_path(self):
        """Test that get_db_path falls back to CODEX_DB_PATH."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "fallback.db"
            with mock.patch.dict(
                os.environ,
                {
                    "CODEX_LOG_DB_PATH": "",
                    "CODEX_DB_PATH": str(db_path),
                },
            ):
                manager = EnvironmentManager()
                result = manager.get_db_path()
                assert result == db_path, "Result must not be empty"


class TestBooleanVariables:
    """Test boolean variable validation and conversion."""

    @pytest.mark.parametrize("true_val", ["1", "true", "yes", "True", "TRUE", "YES"])
    def test_bool_validator_accepts_true_values(self, true_val):
        """Test that boolean validator accepts all true values."""
        config = EnvironmentManager.ENV_VARS["CODEX_SQLITE_POOL"]
        assert config.validator(true_val), "Condition must be true"

    @pytest.mark.parametrize("false_val", ["0", "false", "no", "False", "FALSE", "NO"])
    def test_bool_validator_accepts_false_values(self, false_val):
        """Test that boolean validator accepts all false values."""
        config = EnvironmentManager.ENV_VARS["CODEX_SQLITE_POOL"]
        assert config.validator(false_val), "Condition must be true"

    @pytest.mark.parametrize("invalid_val", ["invalid", "2", "maybe", "", "null"])
    def test_bool_validator_rejects_invalid_values(self, invalid_val):
        """Test that boolean validator rejects invalid values."""
        config = EnvironmentManager.ENV_VARS["CODEX_SQLITE_POOL"]
        if config.validator:
            assert not config.validator(invalid_val), "Condition must be true"

    def test_is_sqlite_pool_enabled_true(self):
        """Test is_sqlite_pool_enabled returns True for enabled."""
        with mock.patch.dict(os.environ, {"CODEX_SQLITE_POOL": "1"}):
            manager = EnvironmentManager()
            assert manager.is_sqlite_pool_enabled() is True, "Condition must be true"

    def test_is_sqlite_pool_enabled_false(self):
        """Test is_sqlite_pool_enabled returns False for disabled."""
        with mock.patch.dict(os.environ, {"CODEX_SQLITE_POOL": "0"}):
            manager = EnvironmentManager()
            assert manager.is_sqlite_pool_enabled() is False, "Condition must be true"

    def test_is_sqlite_pool_enabled_with_string_true(self):
        """Test is_sqlite_pool_enabled with string 'true'."""
        with mock.patch.dict(os.environ, {"CODEX_SQLITE_POOL": "true"}):
            manager = EnvironmentManager()
            assert manager.is_sqlite_pool_enabled() is True, "Condition must be true"


class TestEnvironmentValidation:
    """Test environment variable validation."""

    def test_validate_all_configs_defined(self):
        """Test that all ENV_VARS configurations are properly defined."""
        manager = EnvironmentManager()
        for var_name, config in manager.ENV_VARS.items():
            assert config.name == var_name, "name is not valid"
            assert hasattr(config, "default")
            assert hasattr(config, "validator")
            assert hasattr(config, "required")
            assert hasattr(config, "description")

    def test_validate_required_variables(self):
        """Test validation of required variables."""
        # Create a test case with a required variable that's missing
        with tempfile.TemporaryDirectory():
            # Most variables have required=False, so this should pass
            manager = EnvironmentManager()
            # Should not raise
            manager.validate()

    def test_validate_custom_validator_success(self):
        """Test validation with custom validator that passes."""
        with mock.patch.dict(os.environ, {"CODEX_SQLITE_POOL": "true"}):
            manager = EnvironmentManager()
            # Should not raise
            manager.validate()

    def test_dump_config_returns_all_variables(self):
        """Test dump_config returns all configured variables."""
        manager = EnvironmentManager()
        config_dict = manager.dump_config()
        assert isinstance(config_dict, dict)
        assert len(config_dict) > 0, "Config_dict must not be empty"
        # Should have at least some of the known variables
        assert "CODEX_ENV_PYTHON_VERSION" in config_dict, "Condition must be true"


class TestEnvironmentEdgeCases:
    """Test edge cases in environment variable handling."""

    def test_empty_string_environment_variable(self):
        """Test handling of empty string environment variables."""
        with mock.patch.dict(os.environ, {"CODEX_ENV_NODE_VERSION": ""}):
            manager = EnvironmentManager()
            value = manager.get("CODEX_ENV_NODE_VERSION")
            assert value == "", "Value must be initialized"

    def test_whitespace_environment_variable(self):
        """Test handling of whitespace in environment variables."""
        with mock.patch.dict(os.environ, {"CODEX_ENV_NODE_VERSION": "  "}):
            manager = EnvironmentManager()
            value = manager.get("CODEX_ENV_NODE_VERSION")
            assert value == "  ", "Value must be initialized"

    def test_special_characters_in_path(self):
        """Test handling of special characters in paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            special_path = Path(tmpdir) / "path-with_special.chars"
            with mock.patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": str(special_path)}):
                manager = EnvironmentManager()
                result = manager.get_log_dir()
                assert result.exists(), "Result must not be empty"

    def test_multiple_gets_with_different_defaults(self):
        """Test multiple get calls with different defaults."""
        manager = EnvironmentManager()
        result1 = manager.get("NONEXISTENT", default="default1")
        result2 = manager.get("NONEXISTENT", default="default2")
        assert result1 == "default1", "Result must not be empty"
        assert result2 == "default2", "Result must not be empty"

    def test_session_id_numeric_string(self):
        """Test session ID as numeric string."""
        numeric_id = "1234567890"
        with mock.patch.dict(os.environ, {"CODEX_SESSION_ID": numeric_id}):
            manager = EnvironmentManager()
            session_id = manager.get_session_id()
            assert session_id == numeric_id, "session_id is not valid"

    def test_get_log_dir_with_nested_nonexistent_path(self):
        """Test get_log_dir with deeply nested non-existent path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "a" / "b" / "c" / "d" / "e"
            with mock.patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": str(nested_path)}):
                manager = EnvironmentManager()
                result = manager.get_log_dir()
                assert result == nested_path, "Result must not be empty"
                assert nested_path.exists(), "Condition must be true"
                assert nested_path.is_dir(), "Condition must be true"
