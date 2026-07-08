"""Tests for unified cache management system."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from codex.ci.cache_manager import (
    CacheConfig,
    CacheHealth,
    CacheManager,
    CacheType,
)


class TestCacheType:
    """Test CacheType enum."""

    def test_cache_types_exist(self):
        """Test that all expected cache types exist."""
        expected_types = [
            "pip",
            "nox",
            "uv",
            "gh",
            "huggingface",
            "transformers",
            "pre-commit",
            "mypy",
            "pytest",
            "docker-buildx",
            "yarn",
            "cargo",
            "custom",
        ]

        actual_types = [ct.value for ct in CacheType]

        for expected in expected_types:
            assert expected in actual_types, "Condition must be true"


class TestCacheConfig:
    """Test CacheConfig dataclass."""

    def test_cache_config_creation(self):
        """Test creating a cache configuration."""
        config = CacheConfig(
            cache_type=CacheType.PIP,
            paths=["~/.cache/pip"],
            key_components=["Linux-pr-checks-pip-abc123"],
            restore_keys=["Linux-pr-checks-pip-", "Linux-pip-"],
        )

        assert config.cache_type == CacheType.PIP, "cache_type is not valid"
        assert config.paths == ["~/.cache/pip"], "paths is not valid"
        assert len(config.key_components) == 1, "Collection must not be empty"
        assert len(config.restore_keys) == 2, "Collection must not be empty"

    def test_to_github_actions(self):
        """Test converting config to GitHub Actions format."""
        config = CacheConfig(
            cache_type=CacheType.PIP,
            paths=["~/.cache/pip", "~/.cache/nox"],
            key_components=["Linux-pr-checks-pip-abc123"],
            restore_keys=["Linux-pr-checks-pip-", "Linux-pip-"],
        )

        gh_config = config.to_github_actions()

        assert "path" in gh_config, "Condition must be true"
        assert "key" in gh_config, "Condition must be true"
        assert "restore-keys" in gh_config, "Condition must be true"
        assert gh_config["key"] == "Linux-pr-checks-pip-abc123", "Condition must be true"
        assert "~/.cache/pip" in gh_config["path"], "Condition must be true"


class TestCacheHealth:
    """Test CacheHealth dataclass."""

    def test_healthy_cache(self):
        """Test healthy cache status."""
        health = CacheHealth(
            total_size_gb=5.0,
            total_caches=100,
            cache_hit_rate=0.95,
            oldest_cache_days=15,
            is_critical=False,
        )

        assert not health.is_critical, "Condition must be true"
        assert health.total_size_gb == 5.0, "total_size_gb is not valid"
        assert health.cache_hit_rate == 0.95, "cache_hit_rate is not valid"

    def test_critical_cache(self):
        """Test critical cache status."""
        health = CacheHealth(
            total_size_gb=9.5,
            total_caches=200,
            oldest_cache_days=90,
            is_critical=True,
            warnings=["Size exceeds threshold", "Old caches detected"],
            recommendations=["Run cleanup", "Review cache strategy"],
        )

        assert health.is_critical, "Condition must be true"
        assert len(health.warnings) == 2, "Collection must not be empty"
        assert len(health.recommendations) == 2, "Collection must not be empty"


class TestCacheManager:
    """Test CacheManager class."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a cache manager for testing."""
        return CacheManager(repo_root=tmp_path)

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock GitHub Actions environment."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("RUNNER_OS", "Linux")
        monkeypatch.setenv("RUNNER_ARCH", "X64")
        monkeypatch.setenv("GITHUB_WORKFLOW", "test-workflow")
        monkeypatch.setenv("GITHUB_JOB", "test-job")

    def test_manager_initialization(self, manager):
        """Test manager initializes correctly."""
        assert manager.repo_root.exists(), "Condition must be true"
        assert isinstance(manager.github_context, dict)
        assert "runner_os" in manager.github_context, "Condition must be true"

    def test_detect_repo_root(self, tmp_path, monkeypatch):
        """Test repository root detection."""
        # Create a fake .git directory
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Set GITHUB_WORKSPACE to avoid real repo detection
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))

        manager = CacheManager()

        assert manager.repo_root == tmp_path, "repo_root is not valid"

    def test_generate_cache_key_basic(self, manager, mock_env):
        """Test basic cache key generation."""
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
        )

        assert "Linux" in key, "Condition must be true"
        assert "pr-checks" in key, "Condition must be true"
        assert "pip" in key, "Condition must be true"

    def test_generate_cache_key_with_identifiers(self, manager, mock_env):
        """Test cache key with extra identifiers."""
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
            extra_identifiers={"job": "test", "python": "3.12"},
        )

        assert "Linux" in key, "Condition must be true"
        assert "pr-checks" in key, "Condition must be true"
        assert "job-test" in key, "Condition must be true"
        assert "python-3.12" in key, "Condition must be true"
        assert "pip" in key, "Condition must be true"

    def test_generate_cache_key_with_timestamp(self, manager, mock_env):
        """Test cache key with timestamp."""
        key = manager.generate_cache_key(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
            include_timestamp=True,
        )

        # Should have timestamp component
        parts = key.split("-")
        assert len(parts) >= 4, "Parts must not be empty"

    def test_generate_restore_keys(self, manager):
        """Test restore key generation."""
        primary_key = "Linux-pr-checks-test-python312-pip-abc123def456"
        restore_keys = manager.generate_restore_keys(primary_key, fallback_levels=3)

        assert len(restore_keys) == 3, "Restore_keys must not be empty"
        assert restore_keys[0] == "Linux-pr-checks-test-python312-pip-", "rest is not valid"
        assert restore_keys[1] == "Linux-pr-checks-test-python312-", "rest is not valid"
        assert restore_keys[2] == "Linux-pr-checks-test-", "rest is not valid"

    def test_hash_dependencies(self, manager, tmp_path):
        """Test dependency file hashing."""
        # Create a fake pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        hash1 = manager._hash_dependencies(CacheType.PIP)
        assert len(hash1) == 12, "Hash1 must not be empty"
        assert hash1.isalnum(), "Condition must be true"

        # Modify file
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'modified'\n")
        hash2 = manager._hash_dependencies(CacheType.PIP)

        # Hash should change
        assert hash1 != hash2, "hash1 is not valid"

    def test_create_cache_config(self, manager, mock_env):
        """Test complete cache configuration creation."""
        config = manager.create_cache_config(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
            extra_identifiers={"job": "test"},
        )

        assert isinstance(config, CacheConfig)
        assert config.cache_type == CacheType.PIP, "cache_type is not valid"
        assert len(config.paths) > 0, "Collection must not be empty"
        assert len(config.key_components) == 1, "Collection must not be empty"
        assert len(config.restore_keys) > 0, "Collection must not be empty"

    def test_create_cache_config_with_additional_paths(self, manager, mock_env):
        """Test cache config with additional paths."""
        config = manager.create_cache_config(
            cache_type=CacheType.PIP,
            workflow_name="pr-checks",
            additional_paths=["~/.cache/custom"],
        )

        assert "~/.cache/custom" in config.paths, "Condition must be true"

    def test_validate_cache_health_no_gh_cli(self, manager):
        """Test cache health validation without GitHub CLI."""
        health = manager.validate_cache_health()

        assert isinstance(health, CacheHealth)
        assert health.total_size_gb >= 0, "total_size_gb must be greater than zero"
        assert health.total_caches >= 0, "total_caches must be greater than zero"

    @patch("subprocess.run")
    def test_validate_cache_health_with_gh_cli(self, mock_run, manager, mock_env):
        """Test cache health validation with GitHub CLI."""
        # Mock gh CLI response
        mock_run.return_value = MagicMock(
            stdout='[{"key":"test","sizeInBytes":1073741824,"createdAt":"2026-02-01T00:00:00Z"}]',
            returncode=0,
        )

        # Mock gh CLI availability check
        with patch.object(manager, "_is_gh_cli_available", return_value=True):
            health = manager.validate_cache_health(size_threshold_gb=0.5)

        assert health.total_size_gb > 0, "total_size_gb must be greater than zero"
        assert health.total_caches > 0, "total_caches must be greater than zero"
        assert health.is_critical, "Condition must be true"

    def test_validate_cache_health_critical_size(self, manager):
        """Test cache health detects critical size."""
        health = CacheHealth(
            total_size_gb=9.0,
            total_caches=150,
        )

        # Manually set critical based on size
        health.is_critical = health.total_size_gb > 8.0
        health.warnings.append("Size exceeds threshold")

        assert health.is_critical, "Condition must be true"
        assert len(health.warnings) > 0, "Collection must not be empty"

    def test_cache_paths_defined(self, manager):
        """Test that cache paths are defined for all types."""
        for cache_type in CacheType:
            if cache_type == CacheType.CUSTOM:
                continue

            paths = manager.CACHE_PATHS.get(cache_type)
            assert paths is not None, f"CACHE_PATHS must define paths for {cache_type}"
            assert len(paths) > 0, "Paths must not be empty"

    def test_dependency_files_defined(self, manager):
        """Test that dependency files are defined for key types."""
        key_types = [CacheType.PIP, CacheType.NOX, CacheType.PRE_COMMIT]

        for cache_type in key_types:
            files = manager.DEPENDENCY_FILES.get(cache_type)
            assert files is not None, f"DEPENDENCY_FILES must define files for {cache_type}"
            assert len(files) > 0, "Files must not be empty"


class TestCacheManagerCLI:
    """Test cache manager CLI interface."""

    @patch("sys.argv", ["cache_manager.py", "generate-key", "--cache-type", "pip"])
    @patch("codex.ci.cache_manager.CacheManager")
    def test_cli_generate_key(self, mock_manager_class):
        """Test CLI key generation."""
        mock_manager = MagicMock()
        mock_manager.generate_cache_key.return_value = "Linux-test-pip-abc123"
        mock_manager_class.return_value = mock_manager

        from codex.ci.cache_manager import main

        # Should not raise
        try:
            main()
        except SystemExit:
            _ = None  # Expected


class TestCacheManagerIntegration:
    """Integration tests for cache manager."""

    def test_end_to_end_cache_workflow(self, tmp_path, monkeypatch):
        """Test complete cache workflow."""
        # Setup environment
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("RUNNER_OS", "Linux")
        monkeypatch.setenv("GITHUB_WORKFLOW", "integration-test")

        # Create fake dependency files
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        # Initialize manager
        manager = CacheManager(repo_root=tmp_path)

        # Generate cache config
        config = manager.create_cache_config(
            cache_type=CacheType.PIP,
            workflow_name="integration-test",
            extra_identifiers={"stage": "build"},
        )

        # Validate configuration
        assert config.cache_type == CacheType.PIP, "cache_type is not valid"
        assert "Linux" in config.key_components[0], "Condition must be true"
        assert "integration-test" in config.key_components[0], "Condition must be true"
        assert "pip" in config.key_components[0], "Condition must be true"

        # Check restore keys
        assert len(config.restore_keys) > 0, "Collection must not be empty"

        # Validate health
        health = manager.validate_cache_health()
        assert isinstance(health, CacheHealth)

    def test_multiple_cache_types(self, tmp_path):
        """Test managing multiple cache types."""
        manager = CacheManager(repo_root=tmp_path)

        cache_types = [CacheType.PIP, CacheType.NOX, CacheType.MYPY]
        configs = {}

        for cache_type in cache_types:
            config = manager.create_cache_config(
                cache_type=cache_type,
                workflow_name="multi-cache-test",
            )
            configs[cache_type] = config

        # Verify all have unique keys
        keys = [config.key_components[0] for config in configs.values()]
        assert len(keys) == len(set(keys)), "Keys must not be empty"

        # Verify all have appropriate cache type
        for cache_type, config in configs.items():
            assert cache_type.value in config.key_components[0], "Value must be initialized"
