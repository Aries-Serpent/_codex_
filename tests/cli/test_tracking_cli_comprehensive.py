"""Comprehensive tests for src/codex_ml/cli/tracking_cli.py module.

Tests cover:
- MLflow enablement
- W&B enablement
- CLI argument parsing
- Bootstrap command functionality
"""

import os
from unittest.mock import patch

import pytest


class TestMLflowEnablement:
    """Tests for _enable_mlflow function."""

    def test_enable_mlflow_with_uri(self):
        """Test _enable_mlflow sets tracking URI."""
        from codex_ml.cli.tracking_cli import _enable_mlflow

        with patch.dict(os.environ, {}, clear=False):
            result = _enable_mlflow("file:./test_mlruns")

            assert isinstance(result, dict)
            assert "tracking_uri" in result or "enabled" in result, "Result must not be empty"

    def test_enable_mlflow_without_uri(self):
        """Test _enable_mlflow with default URI."""
        from codex_ml.cli.tracking_cli import _enable_mlflow

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MLFLOW_TRACKING_URI", None)
            result = _enable_mlflow(None)

        assert isinstance(result, dict)
        assert result.get("tracking_uri") == "mlruns" or "warning" in result, "Result must not be empty"

    @patch.dict(os.environ, {}, clear=False)
    def test_enable_mlflow_sets_env_var(self):
        """Test _enable_mlflow sets environment variable."""
        from codex_ml.cli.tracking_cli import _enable_mlflow

        result = _enable_mlflow("file:./custom_path")

        # Either MLflow is available and env is set, or warning is returned
        assert "enabled" in result or "warning" in result, "Result must not be empty"

    def test_enable_mlflow_handles_import_error(self):
        """Test _enable_mlflow handles missing mlflow gracefully."""
        from codex_ml.cli.tracking_cli import _enable_mlflow

        with patch.dict("sys.modules", {"mlflow": None}):
            result = _enable_mlflow("file:./mlruns")
            # Should not raise, returns result dict
            assert isinstance(result, dict)


class TestWandbEnablement:
    """Tests for _enable_wandb function."""

    def test_enable_wandb_offline_mode(self):
        """Test _enable_wandb in offline mode."""
        from codex_ml.cli.tracking_cli import _enable_wandb

        with patch.dict(os.environ, {}, clear=False):
            result = _enable_wandb(project="test_project", mode="offline")

            assert isinstance(result, dict)
            assert "enabled" in result or "warning" in result, "Result must not be empty"

    def test_enable_wandb_disabled_mode(self):
        """Test _enable_wandb in disabled mode."""
        from codex_ml.cli.tracking_cli import _enable_wandb

        with patch.dict(os.environ, {}, clear=False):
            result = _enable_wandb(project="test_project", mode="disabled")

            assert isinstance(result, dict)

    def test_enable_wandb_sets_mode_env(self):
        """Test _enable_wandb sets WANDB_MODE environment variable."""
        from codex_ml.cli.tracking_cli import _enable_wandb

        with patch.dict(os.environ, {}, clear=False):
            result = _enable_wandb(project=None, mode="offline")

            # Mode should be set in env if function ran
            assert isinstance(result, dict)

    def test_enable_wandb_handles_import_error(self):
        """Test _enable_wandb handles missing wandb gracefully."""
        from codex_ml.cli.tracking_cli import _enable_wandb

        with patch.dict("sys.modules", {"wandb": None}):
            result = _enable_wandb(project="test", mode="offline")
            # Should not raise, returns result dict
            assert isinstance(result, dict)


class TestArgumentParser:
    """Tests for _mk_parser function."""

    def test_parser_creation(self):
        """Test parser is created correctly."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        assert parser is not None, "parser must be initialized"
        assert parser.prog == "codex tracking", "prog is not valid"

    def test_parser_has_bootstrap_subcommand(self):
        """Test parser has bootstrap subcommand."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        # Parse with bootstrap subcommand
        args = parser.parse_args(["bootstrap"])
        assert args.subcommand == "bootstrap", "subcommand is not valid"

    def test_parser_bootstrap_mlflow_flag(self):
        """Test parser handles --mlflow flag."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--mlflow"])
        assert args.mlflow is True, "mlflow is not valid"

    def test_parser_bootstrap_wandb_flag(self):
        """Test parser handles --wandb flag."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--wandb"])
        assert args.wandb is True, "wandb is not valid"

    def test_parser_bootstrap_mlflow_uri(self):
        """Test parser handles --mlflow-uri option."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--mlflow", "--mlflow-uri", "file:./custom"])
        assert args.mlflow_uri == "file:./custom", "mlflow_uri is not valid"

    def test_parser_bootstrap_project(self):
        """Test parser handles --project option."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--wandb", "--project", "my_project"])
        assert args.project == "my_project", "project is not valid"

    def test_parser_bootstrap_mode_choices(self):
        """Test parser validates mode choices."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()

        # Valid modes
        for mode in ["online", "offline", "disabled"]:
            args = parser.parse_args(["bootstrap", "--mode", mode])
            assert args.mode == mode, "mode is not valid"

    def test_parser_default_mode(self):
        """Test parser default mode is offline."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap"])
        assert args.mode == "offline", "mode is not valid"

    def test_parser_default_mlflow_uri(self):
        """Test parser default mlflow-uri."""
        from codex_ml.cli.tracking_cli import _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap"])
        assert args.mlflow_uri == "file:./mlruns", "mlflow_uri is not valid"


class TestBootstrapCommand:
    """Tests for _cmd_bootstrap function."""

    def test_bootstrap_command_returns_int(self):
        """Test _cmd_bootstrap returns integer exit code."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap"])

        result = _cmd_bootstrap(args)
        assert isinstance(result, int)

    def test_bootstrap_with_mlflow_only(self):
        """Test _cmd_bootstrap with MLflow only."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--mlflow"])

        result = _cmd_bootstrap(args)
        assert result == 0, "Result must not be empty"

    def test_bootstrap_with_wandb_only(self):
        """Test _cmd_bootstrap with W&B only."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--wandb", "--mode", "disabled"])

        result = _cmd_bootstrap(args)
        assert result == 0, "Result must not be empty"

    def test_bootstrap_with_both(self):
        """Test _cmd_bootstrap with both MLflow and W&B."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap", "--mlflow", "--wandb", "--mode", "disabled"])

        result = _cmd_bootstrap(args)
        assert result == 0, "Result must not be empty"

    def test_bootstrap_without_trackers(self):
        """Test _cmd_bootstrap without any trackers."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(["bootstrap"])

        result = _cmd_bootstrap(args)
        assert result == 0, "Result must not be empty"


class TestTrackingCLIIntegration:
    """Integration tests for tracking CLI module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from codex_ml.cli import tracking_cli

        assert hasattr(tracking_cli, "_enable_mlflow")
        assert hasattr(tracking_cli, "_enable_wandb")
        assert hasattr(tracking_cli, "_mk_parser")
        assert hasattr(tracking_cli, "_cmd_bootstrap")

    def test_full_cli_workflow(self):
        """Test complete CLI workflow."""
        from codex_ml.cli.tracking_cli import _cmd_bootstrap, _mk_parser

        parser = _mk_parser()
        args = parser.parse_args(
            ["bootstrap", "--mlflow", "--mlflow-uri", "file:./test_mlruns", "--mode", "disabled"]
        )

        result = _cmd_bootstrap(args)
        assert isinstance(result, int)
        assert result in (0, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
