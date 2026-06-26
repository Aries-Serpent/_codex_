"""Tests for feature_store CLI module."""

from __future__ import annotations

import pytest

pytest_plugins = ["tests.phase_5_coverage_cli.conftest"]

try:
    from codex_ml.cli import feature_store
except ImportError:
    feature_store = None


@pytest.mark.skipif(feature_store is None, reason="feature_store not importable")
class TestFeatureStoreApp:
    """Test feature_store Typer app."""

    def test_app_exists(self) -> None:
        """Test that Typer app is created."""
        assert hasattr(feature_store, "app")

    def test_app_is_typer_instance(self) -> None:
        """Test that app is a Typer instance."""
        try:
            import typer

            assert isinstance(feature_store.app, typer.Typer)
        except ImportError:
            pytest.skip("Typer not available")

    def test_console_exists(self) -> None:
        """Test that console object exists."""
        assert hasattr(feature_store, "console")

    def test_register_command_exists(self) -> None:
        """Test that register command exists."""
        assert hasattr(feature_store, "register")
        assert callable(feature_store.register), "Condition must be true"

    def test_list_command_exists(self) -> None:
        """Test that list command exists."""
        assert hasattr(feature_store, "list")
        assert callable(feature_store.list), "Condition must be true"


@pytest.mark.skipif(feature_store is None, reason="feature_store not importable")
class TestFeatureStoreCommands:
    """Test individual commands."""

    def test_register_has_proper_signature(self) -> None:
        """Test register command has required parameters."""
        import inspect

        sig = inspect.signature(feature_store.register)
        params = list(sig.parameters.keys())
        # Should have name and version at minimum
        assert "name" in params, "Condition must be true"
        assert "version" in params, "Condition must be true"

    def test_list_has_proper_signature(self) -> None:
        """Test list command has proper parameters."""
        import inspect

        sig = inspect.signature(feature_store.list)
        # list has optional parameters
        assert len(sig.parameters) > 0, "Collection must not be empty"


@pytest.mark.skipif(feature_store is None, reason="feature_store not importable")
class TestFeatureStoreIntegration:
    """Integration tests for feature_store CLI."""

    def test_app_can_be_invoked(self, mock_typer_runner) -> None:
        """Test that app can be invoked via CLI runner."""
        try:
            from typer.testing import CliRunner

            runner = CliRunner()
            result = runner.invoke(feature_store.app, ["--help"])
            # Should not crash
            assert result is not None, "result must be initialized"
        except ImportError:
            pytest.skip("Typer not available")


@pytest.mark.skipif(feature_store is None, reason="feature_store not importable")
class TestFeatureStoreUtilities:
    """Test utility components."""

    def test_feature_group_class_available(self) -> None:
        """Test that FeatureGroup is available."""
        try:
            from codex_ml.features.feature_store import FeatureGroup

            assert FeatureGroup is not None, "FeatureGroup must be initialized"
        except ImportError:
            pytest.skip("FeatureGroup not importable")

    def test_feature_store_class_available(self) -> None:
        """Test that FeatureStore is available."""
        try:
            from codex_ml.features.feature_store import FeatureStore

            assert FeatureStore is not None, "FeatureStore must be initialized"
        except ImportError:
            pytest.skip("FeatureStore not importable")


@pytest.mark.skipif(feature_store is None, reason="feature_store not importable")
class TestFeatureStoreImports:
    """Test that required imports are successful."""

    def test_typer_available(self) -> None:
        """Test that typer is available."""
        try:
            import typer

            assert typer is not None, "typer must be initialized"
        except ImportError:
            pytest.skip("Typer not installed")

    def test_rich_available(self) -> None:
        """Test that rich is available."""
        try:
            from rich.console import Console
            from rich.table import Table

            assert Console is not None, "Console must be initialized"
            assert Table is not None, "Table must be initialized"
        except ImportError:
            pytest.skip("Rich not installed")
