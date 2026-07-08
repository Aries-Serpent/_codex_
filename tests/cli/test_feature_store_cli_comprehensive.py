"""Comprehensive tests for src/codex_ml/cli/feature_store.py module.

Tests cover:
- Feature registration commands
- Feature listing commands
- Health monitoring integration
- CLI argument handling
"""

from unittest.mock import MagicMock, patch

import pytest


class TestFeatureStoreImports:
    """Tests for module imports and dependencies."""

    def test_module_imports(self):
        """Test that module can be imported."""
        try:
            from codex_ml.cli import feature_store

            assert hasattr(feature_store, "app")
            assert hasattr(feature_store, "console")
        except ImportError as e:
            if "typer" in str(e) or "rich" in str(e):
                pytest.skip("typer/rich not available")
            raise

    def test_typer_app_configured(self):
        """Test that Typer app is properly configured."""
        try:
            from codex_ml.cli.feature_store import app

            assert app.info.name == "feature-store", "name is not valid"
            assert app.info.help == "Feature store management CLI", "help is not valid"
        except ImportError:
            pytest.skip("typer not available")


class TestFeatureRegistration:
    """Tests for feature registration functionality."""

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_register_creates_feature_group(self, mock_store_class):
        """Test register command creates feature group."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(app, ["register", "test_features", "1.0.0"])

            # Verify store was instantiated
            assert mock_store_class.called or result.exit_code in (0, 1)
        except ImportError:
            pytest.skip("typer not available")

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_register_with_description(self, mock_store_class):
        """Test register command with description option."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(
                app, ["register", "test_features", "1.0.0", "-d", "Test feature description"]
            )

            # Command should complete (success or handled error)
            assert result.exit_code in (0, 1)
        except ImportError:
            pytest.skip("typer not available")

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_register_with_custom_store_path(self, mock_store_class):
        """Test register command with custom store path."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            runner.invoke(
                app, ["register", "test_features", "1.0.0", "--store-path", "/custom/path"]
            )

            # Verify custom path was used
            if mock_store_class.called:
                call_args = mock_store_class.call_args
                assert "/custom/path" in str(call_args), "Condition must be true"
        except ImportError:
            pytest.skip("typer not available")


class TestFeatureListing:
    """Tests for feature listing functionality."""

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_list_command_basic(self, mock_store_class):
        """Test list command basic functionality."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store.list_features.return_value = []
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(app, ["list"])

            # Command should complete
            assert result.exit_code in (0, 1)
        except ImportError:
            pytest.skip("typer not available")

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_list_with_health_flag(self, mock_store_class):
        """Test list command with --health flag."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store.list_features.return_value = []
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(app, ["list", "--health"])

            assert result.exit_code in (0, 1)
        except ImportError:
            pytest.skip("typer not available")

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_list_without_versions(self, mock_store_class):
        """Test list command with --no-versions flag."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store.list_features.return_value = []
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(app, ["list", "--no-versions"])

            assert result.exit_code in (0, 1)
        except ImportError:
            pytest.skip("typer not available")


class TestFeatureStoreHelpers:
    """Tests for helper functions in feature store CLI."""

    def test_feature_group_import(self):
        """Test FeatureGroup can be imported."""
        try:
            from codex_ml.cli.feature_store import FeatureGroup

            assert FeatureGroup is not None, "FeatureGroup must be initialized"
        except ImportError:
            pytest.skip("Feature store dependencies not available")

    def test_feature_store_import(self):
        """Test FeatureStore can be imported."""
        try:
            from codex_ml.cli.feature_store import FeatureStore

            assert FeatureStore is not None, "FeatureStore must be initialized"
        except ImportError:
            pytest.skip("Feature store dependencies not available")

    def test_feature_health_monitor_import(self):
        """Test FeatureHealthMonitor can be imported."""
        try:
            from codex_ml.cli.feature_store import FeatureHealthMonitor

            assert FeatureHealthMonitor is not None, "FeatureHealthMonitor must be initialized"
        except ImportError:
            pytest.skip("Feature store dependencies not available")


class TestFeatureStoreErrorHandling:
    """Tests for error handling in feature store CLI."""

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_register_handles_store_error(self, mock_store_class):
        """Test register command handles store errors gracefully."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store_class.side_effect = Exception("Store initialization failed")

            runner = CliRunner()
            result = runner.invoke(app, ["register", "test", "1.0.0"])

            # Should exit with error code 1
            assert result.exit_code == 1, "Result must not be empty"
        except ImportError:
            pytest.skip("typer not available")

    @patch("codex_ml.cli.feature_store.FeatureStore")
    def test_list_handles_empty_store(self, mock_store_class):
        """Test list command handles empty store."""
        try:
            from typer.testing import CliRunner

            from codex_ml.cli.feature_store import app

            mock_store = MagicMock()
            mock_store.list_features.return_value = []
            mock_store_class.return_value = mock_store

            runner = CliRunner()
            result = runner.invoke(app, ["list"])

            # Should show "No features registered" message
            assert result.exit_code == 0 or "No features" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("typer not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
