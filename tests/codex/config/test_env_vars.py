"""Tests for codex.config.env_vars module.

Phase 6 tests covering:
- EnvVarConfig dataclass
- EnvironmentManager class
- Environment variable validation
- Session ID generation
- Log directory and DB path resolution
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest


class TestEnvVarConfig:
    """Tests for EnvVarConfig dataclass."""

    def test_create_basic_config(self):
        """Test creating basic environment variable config."""
        from codex.config.env_vars import EnvVarConfig
        
        config = EnvVarConfig(name="TEST_VAR")
        assert config.name == "TEST_VAR"
        assert config.default is None
        assert config.validator is None
        assert config.required is False
        assert config.description == ""

    def test_create_config_with_defaults(self):
        """Test creating config with default value."""
        from codex.config.env_vars import EnvVarConfig
        
        config = EnvVarConfig(
            name="TEST_VAR",
            default="default_value",
            description="A test variable",
        )
        assert config.default == "default_value"
        assert config.description == "A test variable"

    def test_create_config_with_validator(self):
        """Test creating config with validator."""
        from codex.config.env_vars import EnvVarConfig
        
        validator = lambda v: v in ("0", "1")
        config = EnvVarConfig(
            name="TEST_VAR",
            validator=validator,
        )
        assert config.validator is not None
        assert config.validator("1") is True
        assert config.validator("2") is False

    def test_create_required_config(self):
        """Test creating required environment variable config."""
        from codex.config.env_vars import EnvVarConfig
        
        config = EnvVarConfig(name="REQUIRED_VAR", required=True)
        assert config.required is True


class TestEnvironmentManager:
    """Tests for EnvironmentManager class."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        # Restore
        for k, v in saved.items():
            os.environ[k] = v

    @pytest.fixture
    def manager(self, clean_env):
        """Create EnvironmentManager with lazy validation."""
        from codex.config.env_vars import EnvironmentManager
        return EnvironmentManager(lazy_validation=True)

    def test_instantiation_with_lazy_validation(self, clean_env):
        """Test that manager can be created with lazy validation."""
        from codex.config.env_vars import EnvironmentManager
        
        manager = EnvironmentManager(lazy_validation=True)
        assert manager._lazy_validation is True
        assert manager._validated is False

    def test_instantiation_with_eager_validation(self, clean_env):
        """Test that manager validates on init by default."""
        from codex.config.env_vars import EnvironmentManager
        
        # Should not raise with no required vars
        manager = EnvironmentManager(lazy_validation=False)
        assert manager is not None

    def test_get_existing_env_var(self, manager):
        """Test getting an existing environment variable."""
        os.environ["CODEX_FORCE_CPU"] = "1"
        result = manager.get("CODEX_FORCE_CPU")
        assert result == "1"

    def test_get_with_default_fallback(self, manager):
        """Test getting env var with default fallback."""
        result = manager.get("CODEX_NONEXISTENT", default="fallback")
        assert result == "fallback"

    def test_get_with_configured_default(self, manager):
        """Test getting env var with configured default."""
        result = manager.get("CODEX_SESSION_LOG_DIR")
        assert result == ".codex/sessions"

    def test_get_session_id_generates_uuid(self, manager, clean_env):
        """Test that session ID is generated if not set."""
        session_id = manager.get_session_id()
        # Verify it's a valid UUID
        uuid.UUID(session_id)
        assert session_id is not None

    def test_get_session_id_uses_env_value(self, manager, clean_env):
        """Test that session ID uses env value if set."""
        os.environ["CODEX_SESSION_ID"] = "test-session-123"
        session_id = manager.get_session_id()
        assert session_id == "test-session-123"

    def test_get_session_id_caches_value(self, manager, clean_env):
        """Test that session ID is cached after first call."""
        session_id1 = manager.get_session_id()
        session_id2 = manager.get_session_id()
        assert session_id1 == session_id2

    def test_get_log_dir_creates_directory(self, clean_env, tmp_path):
        """Test that get_log_dir creates directory if not exists."""
        from codex.config.env_vars import EnvironmentManager
        
        log_dir = str(tmp_path / "test_logs")
        os.environ["CODEX_SESSION_LOG_DIR"] = log_dir
        
        # Create fresh manager to pick up new env var
        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_log_dir()
        
        assert result.exists()
        assert result.is_dir()

    def test_get_db_path(self, clean_env, tmp_path):
        """Test getting database path."""
        from codex.config.env_vars import EnvironmentManager
        
        db_path = str(tmp_path / "test.db")
        os.environ["CODEX_LOG_DB_PATH"] = db_path
        
        # Create fresh manager to pick up new env var
        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_db_path()
        
        assert str(result).endswith("test.db")

    def test_is_sqlite_pool_enabled_false(self, manager, clean_env):
        """Test SQLite pool disabled by default."""
        os.environ["CODEX_SQLITE_POOL"] = "0"
        assert manager.is_sqlite_pool_enabled() is False

    def test_is_sqlite_pool_enabled_true(self, manager, clean_env):
        """Test SQLite pool enabled."""
        os.environ["CODEX_SQLITE_POOL"] = "1"
        assert manager.is_sqlite_pool_enabled() is True

    def test_dump_config_returns_dict(self, manager):
        """Test that dump_config returns dictionary."""
        result = manager.dump_config()
        assert isinstance(result, dict)
        assert "CODEX_SESSION_LOG_DIR" in result

    def test_validate_method(self, manager):
        """Test explicit validate method."""
        manager.validate()
        assert manager._validated is True

    def test_validate_idempotent(self, manager):
        """Test that validate can be called multiple times."""
        manager.validate()
        manager.validate()  # Should not raise
        assert manager._validated is True


class TestEnvironmentManagerValidation:
    """Tests for environment validation logic."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        # Restore
        for k, v in saved.items():
            os.environ[k] = v

    def test_validation_fails_on_invalid_value(self, clean_env):
        """Test validation fails for invalid values."""
        from codex.config.env_vars import EnvironmentManager
        
        # Set invalid value for CODEX_SQLITE_POOL (expects "0" or "1")
        os.environ["CODEX_SQLITE_POOL"] = "invalid"
        
        with pytest.raises(EnvironmentError):
            EnvironmentManager(lazy_validation=False)

    def test_validation_passes_with_valid_values(self, clean_env):
        """Test validation passes with valid values."""
        from codex.config.env_vars import EnvironmentManager
        
        os.environ["CODEX_SQLITE_POOL"] = "1"
        os.environ["CODEX_FORCE_CPU"] = "1"
        
        manager = EnvironmentManager(lazy_validation=False)
        assert manager is not None


class TestGlobalEnvManager:
    """Tests for global env_manager instance."""

    def test_global_instance_exists(self):
        """Test that global env_manager exists."""
        from codex.config.env_vars import env_manager
        assert env_manager is not None

    def test_global_instance_is_environment_manager(self):
        """Test that global instance is EnvironmentManager."""
        from codex.config.env_vars import EnvironmentManager, env_manager
        assert isinstance(env_manager, EnvironmentManager)
