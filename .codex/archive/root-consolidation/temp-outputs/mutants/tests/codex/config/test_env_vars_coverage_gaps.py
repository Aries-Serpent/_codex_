"""Coverage gap-fill tests for codex.config.env_vars module.

Phase 12 WS3 Testing Lane - Tier 1 Gap-Fill Coverage Enhancement
Focus: Branch coverage, error paths, and edge cases

Identified gaps:
- Boolean validation with mixed case variations
- get() method edge cases with None returns
- Error message formatting with multiple validators
- Path fallback logic (CODEX_DB_PATH vs CODEX_LOG_DB_PATH)
- _ensure_validated() double validation prevention
- Validator edge cases with various return types
"""
from __future__ import annotations
import os
import uuid
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager
        from codex.config.env_vars import EnvironmentManager





class TestBooleanValidationEdgeCases:
    """Test boolean string validation with various case combinations."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_is_sqlite_pool_enabled_with_true_uppercase(self, clean_env):
        """Test SQLite pool with 'TRUE' (uppercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "TRUE"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is True

    def test_is_sqlite_pool_enabled_with_true_mixed_case(self, clean_env):
        """Test SQLite pool with 'True' (mixed case)."""

        os.environ["CODEX_SQLITE_POOL"] = "True"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is True

    def test_is_sqlite_pool_enabled_with_yes(self, clean_env):
        """Test SQLite pool with 'yes' (lowercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "yes"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is True

    def test_is_sqlite_pool_enabled_with_yes_uppercase(self, clean_env):
        """Test SQLite pool with 'YES' (uppercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "YES"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is True

    def test_is_sqlite_pool_enabled_with_false_uppercase(self, clean_env):
        """Test SQLite pool with 'FALSE' (uppercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "FALSE"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is False

    def test_is_sqlite_pool_enabled_with_false_mixed_case(self, clean_env):
        """Test SQLite pool with 'False' (mixed case)."""

        os.environ["CODEX_SQLITE_POOL"] = "False"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is False

    def test_is_sqlite_pool_enabled_with_no(self, clean_env):
        """Test SQLite pool with 'no' (lowercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "no"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is False

    def test_is_sqlite_pool_enabled_with_no_uppercase(self, clean_env):
        """Test SQLite pool with 'NO' (uppercase)."""

        os.environ["CODEX_SQLITE_POOL"] = "NO"
        manager = EnvironmentManager(lazy_validation=True)
        assert manager.is_sqlite_pool_enabled() is False

    def test_force_cpu_validation_true_variants(self, clean_env):
        """Test CODEX_FORCE_CPU accepts all true variants."""

        for value in ("1", "true", "True", "TRUE", "yes", "YES"):
            os.environ["CODEX_FORCE_CPU"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None

    def test_force_cpu_validation_false_variants(self, clean_env):
        """Test CODEX_FORCE_CPU accepts all false variants."""

        for value in ("0", "false", "False", "FALSE", "no", "NO"):
            os.environ["CODEX_FORCE_CPU"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None


class TestGetMethodEdgeCases:
    """Test edge cases of the get() method."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_get_unknown_var_no_default_returns_empty_string(self, clean_env):
        """Test getting unknown variable with no default returns empty string."""

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get("UNKNOWN_VARIABLE_XYZ")
        assert result == ""
        assert isinstance(result, str)

    def test_get_with_empty_string_value(self, clean_env):
        """Test getting variable with empty string value."""

        os.environ["CODEX_SESSION_LOG_DIR"] = ""
        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get("CODEX_SESSION_LOG_DIR")
        # Empty string is falsy but should be returned if explicitly set
        assert result == ""

    def test_get_parameter_default_overrides_configured_default(self, clean_env):
        """Test that parameter default overrides configured default."""

        manager = EnvironmentManager(lazy_validation=True)
        # CODEX_SESSION_LOG_DIR has configured default of ".codex/sessions"
        # but we pass our own default
        result = manager.get("CODEX_SESSION_LOG_DIR", default="custom_default")
        assert result == "custom_default"

    def test_get_with_none_parameter_default_uses_configured(self, clean_env):
        """Test that None parameter default uses configured default."""

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get("CODEX_SESSION_LOG_DIR", default=None)
        # Should use configured default ".codex/sessions"
        assert result == ".codex/sessions"

    def test_get_multiple_calls_consistent(self, clean_env):
        """Test that multiple get() calls return consistent values."""

        os.environ["CODEX_FORCE_CPU"] = "1"
        manager = EnvironmentManager(lazy_validation=True)
        result1 = manager.get("CODEX_FORCE_CPU")
        result2 = manager.get("CODEX_FORCE_CPU")
        assert result1 == result2 == "1"


class TestPathFallbackLogic:
    """Test path fallback logic between CODEX_LOG_DB_PATH and CODEX_DB_PATH."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_get_db_path_uses_log_db_path_first(self, clean_env, tmp_path):
        """Test that CODEX_LOG_DB_PATH is preferred over CODEX_DB_PATH."""

        log_db = str(tmp_path / "log.db")
        alt_db = str(tmp_path / "alt.db")
        os.environ["CODEX_LOG_DB_PATH"] = log_db
        os.environ["CODEX_DB_PATH"] = alt_db

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_db_path()
        assert str(result) == log_db

    def test_get_db_path_falls_back_to_db_path(self, clean_env, tmp_path):
        """Test fallback to CODEX_DB_PATH when CODEX_LOG_DB_PATH is not set."""

        alt_db = str(tmp_path / "alt.db")
        os.environ["CODEX_DB_PATH"] = alt_db
        # Don't set CODEX_LOG_DB_PATH

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_db_path()
        assert str(result) == alt_db

    def test_get_db_path_with_empty_log_db_uses_fallback(self, clean_env, tmp_path):
        """Test that empty CODEX_LOG_DB_PATH triggers fallback."""

        alt_db = str(tmp_path / "alt.db")
        os.environ["CODEX_LOG_DB_PATH"] = ""
        os.environ["CODEX_DB_PATH"] = alt_db

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_db_path()
        # Empty string is falsy in 'or' expression, so should use alt_db
        assert str(result) == alt_db


class TestDoubleValidationPrevention:
    """Test that validation only happens once."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_ensure_validated_skips_second_validation(self, clean_env):
        """Test that _ensure_validated() prevents double validation."""

        manager = EnvironmentManager(lazy_validation=True)
        assert manager._validated is False

        # First call to _ensure_validated
        manager._ensure_validated()
        assert manager._validated is True

        # Change environment (invalid value)
        os.environ["CODEX_SQLITE_POOL"] = "invalid"

        # Second call to _ensure_validated should not revalidate
        manager._ensure_validated()  # Should not raise
        assert manager._validated is True

    def test_multiple_operations_use_cached_validation(self, clean_env):
        """Test that multiple operations don't retrigger validation."""

        manager = EnvironmentManager(lazy_validation=True)

        # Multiple operations
        val1 = manager.get("CODEX_FORCE_CPU")
        val2 = manager.get("CODEX_SESSION_LOG_DIR")
        val3 = manager.get_session_id()

        # All should succeed without validation errors
        assert manager._validated is True


class TestValidatorBehavior:
    """Test validator callable behavior and edge cases."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_vendor_purge_validation_variants(self, clean_env):
        """Test CODEX_VENDOR_PURGE validation with all variants."""

        for value in ("1", "0", "true", "false", "yes", "no"):
            os.environ["CODEX_VENDOR_PURGE"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None

    def test_abort_on_gpu_pull_validation(self, clean_env):
        """Test CODEX_ABORT_ON_GPU_PULL validation."""

        for value in ("1", "true", "yes"):
            os.environ["CODEX_ABORT_ON_GPU_PULL"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None

    def test_dependency_evidence_enable_validation(self, clean_env):
        """Test CODEX_DEPENDENCY_EVIDENCE_ENABLE validation."""

        for value in ("1", "0", "true", "false"):
            os.environ["CODEX_DEPENDENCY_EVIDENCE_ENABLE"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None

    def test_collect_coverage_validation(self, clean_env):
        """Test CODEX_COLLECT_COVERAGE validation."""

        for value in ("1", "0", "true", "false", "yes", "no"):
            os.environ["CODEX_COLLECT_COVERAGE"] = value
            manager = EnvironmentManager(lazy_validation=False)
            assert manager is not None


class TestValidationErrorMessages:
    """Test error message formatting with multiple errors."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_single_validation_error_message(self, clean_env):
        """Test error message for single validation failure."""

        os.environ["CODEX_FORCE_CPU"] = "invalid"

        with pytest.raises(EnvironmentError) as exc_info:
            EnvironmentManager(lazy_validation=False)

        error_msg = str(exc_info.value)
        assert "CODEX_FORCE_CPU" in error_msg
        assert "invalid" in error_msg

    def test_multiple_validation_errors_newline_separated(self, clean_env):
        """Test error message for multiple validation failures."""

        os.environ["CODEX_FORCE_CPU"] = "invalid1"
        os.environ["CODEX_SQLITE_POOL"] = "invalid2"

        with pytest.raises(EnvironmentError) as exc_info:
            EnvironmentManager(lazy_validation=False)

        error_msg = str(exc_info.value)
        assert "CODEX_FORCE_CPU" in error_msg
        assert "CODEX_SQLITE_POOL" in error_msg
        assert "\n" in error_msg  # Multiple errors should be newline-separated


class TestSessionIdEdgeCases:
    """Test session ID edge cases and caching behavior."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_get_session_id_sets_environment(self, clean_env):
        """Test that get_session_id() sets the environment variable."""

        manager = EnvironmentManager(lazy_validation=True)
        session_id = manager.get_session_id()

        # Should be set in environment
        assert os.getenv("CODEX_SESSION_ID") == session_id

    def test_get_session_id_with_existing_env_value(self, clean_env):
        """Test get_session_id uses existing environment value."""

        test_id = str(uuid.uuid4())
        os.environ["CODEX_SESSION_ID"] = test_id

        manager = EnvironmentManager(lazy_validation=True)
        session_id = manager.get_session_id()

        assert session_id == test_id

    def test_get_session_id_generates_valid_uuid(self, clean_env):
        """Test that generated session ID is a valid UUID."""

        manager = EnvironmentManager(lazy_validation=True)
        session_id = manager.get_session_id()

        # Should be parseable as UUID
        parsed = uuid.UUID(session_id)
        assert str(parsed) == session_id


class TestDumpConfigCompleteness:
    """Test dump_config() returns all configured variables."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_dump_config_includes_all_env_vars(self, clean_env):
        """Test that dump_config includes all configured variables."""

        manager = EnvironmentManager(lazy_validation=True)
        config = manager.dump_config()

        # Should have all variables from ENV_VARS
        assert len(config) == len(manager.ENV_VARS)

        # Should have keys from ENV_VARS
        for key in manager.ENV_VARS:
            assert key in config

    def test_dump_config_uses_get_method(self, clean_env):
        """Test that dump_config respects get() fallback logic."""

        manager = EnvironmentManager(lazy_validation=True)
        config = manager.dump_config()

        # CODEX_SESSION_LOG_DIR should have configured default
        assert config["CODEX_SESSION_LOG_DIR"] == ".codex/sessions"

        # CODEX_SQLITE_POOL should have configured default
        assert config["CODEX_SQLITE_POOL"] == "0"

    def test_dump_config_reflects_environment_values(self, clean_env):
        """Test that dump_config reflects actual environment values."""

        os.environ["CODEX_FORCE_CPU"] = "0"
        manager = EnvironmentManager(lazy_validation=True)
        config = manager.dump_config()

        assert config["CODEX_FORCE_CPU"] == "0"


class TestLogDirCreation:
    """Test log directory creation behavior."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_get_log_dir_nested_path_creation(self, clean_env, tmp_path):
        """Test that get_log_dir creates nested parent directories."""

        nested_path = str(tmp_path / "a" / "b" / "c" / "logs")
        os.environ["CODEX_SESSION_LOG_DIR"] = nested_path

        manager = EnvironmentManager(lazy_validation=True)
        result = manager.get_log_dir()

        assert result.exists()
        assert result.is_dir()
        assert str(result) == nested_path

    def test_get_log_dir_idempotent(self, clean_env, tmp_path):
        """Test that get_log_dir can be called multiple times safely."""

        log_path = str(tmp_path / "logs")
        os.environ["CODEX_SESSION_LOG_DIR"] = log_path

        manager = EnvironmentManager(lazy_validation=True)
        result1 = manager.get_log_dir()
        result2 = manager.get_log_dir()

        assert result1 == result2
        assert result1.exists()


class TestEnvironmentVariableDefaults:
    """Test that all environment variables have correct defaults."""

    @pytest.fixture
    def clean_env(self):
        """Clear CODEX environment variables for testing."""
        env_vars = [k for k in os.environ if k.startswith("CODEX_")]
        saved = {k: os.environ.pop(k) for k in env_vars}
        yield
        test_added_keys = [k for k in os.environ if k.startswith("CODEX_")]
        for k in test_added_keys:
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v

    def test_python_version_has_default(self, clean_env):
        """Test CODEX_ENV_PYTHON_VERSION has default."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_ENV_PYTHON_VERSION")
        assert value == "3.12"

    def test_optional_language_versions_no_default(self, clean_env):
        """Test optional language versions have None as default."""

        manager = EnvironmentManager(lazy_validation=True)
        for var in ["CODEX_ENV_NODE_VERSION", "CODEX_ENV_RUST_VERSION",
                    "CODEX_ENV_GO_VERSION", "CODEX_ENV_SWIFT_VERSION"]:
            value = manager.get(var)
            # Should return empty string (None mapped to "")
            assert value == ""

    def test_force_cpu_defaults_to_one(self, clean_env):
        """Test CODEX_FORCE_CPU defaults to '1'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_FORCE_CPU")
        assert value == "1"

    def test_cpu_minimal_defaults_to_zero(self, clean_env):
        """Test CODEX_CPU_MINIMAL defaults to '0'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_CPU_MINIMAL")
        assert value == "0"

    def test_vendor_purge_defaults_to_one(self, clean_env):
        """Test CODEX_VENDOR_PURGE defaults to '1'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_VENDOR_PURGE")
        assert value == "1"

    def test_abort_on_gpu_pull_defaults_to_zero(self, clean_env):
        """Test CODEX_ABORT_ON_GPU_PULL defaults to '0'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_ABORT_ON_GPU_PULL")
        assert value == "0"

    def test_dependency_evidence_enable_defaults_to_one(self, clean_env):
        """Test CODEX_DEPENDENCY_EVIDENCE_ENABLE defaults to '1'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_DEPENDENCY_EVIDENCE_ENABLE")
        assert value == "1"

    def test_collect_coverage_defaults_to_zero(self, clean_env):
        """Test CODEX_COLLECT_COVERAGE defaults to '0'."""

        manager = EnvironmentManager(lazy_validation=True)
        value = manager.get("CODEX_COLLECT_COVERAGE")
        assert value == "0"
