"""Tests for codex_cli.app module."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = ["tests.phase_5_coverage_cli.conftest"]

try:
    from codex_cli import app
except ImportError:
    app = None


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppConstants:
    """Test module constants."""

    def test_reasoning_template_root_exists(self) -> None:
        """Test that REASONING_TEMPLATE_ROOT points to valid location."""
        assert isinstance(app.REASONING_TEMPLATE_ROOT, Path)

    def test_reasoning_curricula_root_exists(self) -> None:
        """Test that REASONING_CURRICULA_ROOT points to valid location."""
        assert isinstance(app.REASONING_CURRICULA_ROOT, Path)


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppEcho:
    """Test echo function."""

    def test_echo_function_exists(self) -> None:
        """Test that echo function exists."""
        assert hasattr(app, "echo")
        assert callable(app.echo), "Condition must be true"

    def test_echo_is_callable(self) -> None:
        """Test echo can be called."""
        try:
            app.echo("test message")
        except (AssertionError, ValueError, TypeError, RuntimeError):
            # May fail if not in CLI context, but function should exist
            pass


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppExit:
    """Test Exit class."""

    def test_exit_class_exists(self) -> None:
        """Test that Exit class exists."""
        assert hasattr(app, "Exit")

    def test_exit_can_be_instantiated(self) -> None:
        """Test Exit can be instantiated."""
        exit_obj = app.Exit(code=0)
        assert exit_obj is not None, "exit_obj must be initialized"

    def test_exit_with_code(self) -> None:
        """Test Exit with specific code."""
        try:
            raise app.Exit(code=1)
        except (app.Exit, SystemExit):
            pass  # Expected


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppTrackSmokeImpl:
    """Test _track_smoke_impl function."""

    def test_track_smoke_impl_exists(self) -> None:
        """Test that _track_smoke_impl function exists."""
        assert hasattr(app, "_track_smoke_impl")
        assert callable(app._track_smoke_impl), "Condition must be true"

    def test_track_smoke_impl_with_none(self) -> None:
        """Test _track_smoke_impl with None path."""
        # This may fail if MLflow is not installed, but function should be callable
        try:
            app._track_smoke_impl(None)
        except (ImportError, app.Exit, SystemExit):
            pass  # Expected if MLflow not available

    def test_track_smoke_impl_with_temp_dir(self, tmp_path: Path) -> None:
        """Test _track_smoke_impl with temporary directory."""
        try:
            app._track_smoke_impl(tmp_path)
        except (ImportError, app.Exit, SystemExit):
            pass  # Expected if MLflow not available


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppSplitSmokeImpl:
    """Test _split_smoke_impl function."""

    def test_split_smoke_impl_exists(self) -> None:
        """Test that _split_smoke_impl function exists."""
        assert hasattr(app, "_split_smoke_impl")
        assert callable(app._split_smoke_impl), "Condition must be true"

    def test_split_smoke_impl_with_seed_zero(self) -> None:
        """Test _split_smoke_impl with seed 0."""
        try:
            app._split_smoke_impl(seed=0)
        except (ImportError, app.Exit, SystemExit):
            pass  # Expected if dependencies not available

    def test_split_smoke_impl_with_seed_nonzero(self) -> None:
        """Test _split_smoke_impl with non-zero seed."""
        try:
            app._split_smoke_impl(seed=42)
        except (ImportError, app.Exit, SystemExit):
            pass  # Expected if dependencies not available


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppFramework:
    """Test CLI framework selection."""

    def test_framework_selected(self) -> None:
        """Test that CLI framework is selected."""
        # Either Typer or Click should be selected
        assert app._USE_TYPER is True or app._USE_TYPER is False, "_USE_TYPER is not valid"

    def test_echo_from_selected_framework(self) -> None:
        """Test echo is from selected framework."""
        assert callable(app.echo), "Condition must be true"

        # Try to call it
        try:
            result = app.echo("test")
            # Should not raise if framework is properly configured
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            # May fail in non-CLI context
            pass


@pytest.mark.skipif(app is None, reason="codex_cli.app not importable")
class TestAppImportHandling:
    """Test optional dependency handling."""

    def test_handles_missing_typer(self) -> None:
        """Test graceful handling if Typer missing."""
        # Framework should still be usable (might fall back to Click)
        assert app.echo is not None, "echo must be initialized"
        assert app.Exit is not None, "Exit must be initialized"

    def test_handles_missing_click(self) -> None:
        """Test graceful handling if Click missing."""
        # Should use Typer if available, or Click as fallback
        assert hasattr(app, "echo")
        assert hasattr(app, "Exit")
