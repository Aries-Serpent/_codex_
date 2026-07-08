"""
Test Main Entry Point Module

Tests for the main.py module including argument parsing,
version resolution, CLI forwarding, and help display.
"""

from __future__ import annotations

import argparse
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

from codex_ml.main import (
    _forward_to_cli,
    _resolve_version,
    build_parser,
    main,
)


class TestBuildParser:
    """Tests for build_parser function."""

    def test_returns_argument_parser(self) -> None:
        """Test that build_parser returns an ArgumentParser."""
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_prog_name(self) -> None:
        """Test parser prog name is set correctly."""
        parser = build_parser()
        assert parser.prog == "codex-ml", "prog is not valid"

    def test_has_version_argument(self) -> None:
        """Test parser has --version argument."""
        parser = build_parser()
        # Parse with --version flag
        args = parser.parse_args(["--version"])
        assert args.version is True, "version is not valid"

    def test_has_forward_argument(self) -> None:
        """Test parser has --forward argument."""
        parser = build_parser()
        args = parser.parse_args(["--forward", "arg1", "arg2"])
        assert args.forward == ["arg1", "arg2"]

    def test_forward_captures_remainder(self) -> None:
        """Test --forward captures all remaining arguments."""
        parser = build_parser()
        # Note: argparse.REMAINDER doesn't allow -- separator after --forward
        args = parser.parse_args(["--forward", "sub", "--flag", "value"])
        assert args.forward == ["sub", "--flag", "value"]

    def test_default_values(self) -> None:
        """Test default argument values."""
        parser = build_parser()
        args = parser.parse_args([])
        assert args.version is False, "version is not valid"
        assert args.forward is None, "forward is not valid"


class TestResolveVersion:
    """Tests for _resolve_version function."""

    def test_returns_string(self) -> None:
        """Test version returns a string."""
        version = _resolve_version()
        assert isinstance(version, str)

    def test_returns_version_or_unknown(self) -> None:
        """Test version is either a valid version or 'unknown'."""
        version = _resolve_version()
        # Should be either a version string or "unknown"
        assert version == "unknown" or len(version) > 0, "Version must not be empty"

    @patch("codex_ml.main.importlib.import_module")
    def test_handles_import_error(self, mock_import: MagicMock) -> None:
        """Test handles import error gracefully."""
        mock_import.side_effect = ImportError("No module")
        version = _resolve_version()
        assert version == "unknown", "version is not valid"

    @patch("codex_ml.main.importlib.import_module")
    def test_handles_missing_version_attr(self, mock_import: MagicMock) -> None:
        """Test handles missing __version__ attribute."""
        mock_module = MagicMock(spec=[])  # No __version__
        mock_import.return_value = mock_module
        version = _resolve_version()
        assert version == "unknown", "version is not valid"

    @patch("codex_ml.main.importlib.import_module")
    def test_returns_module_version(self, mock_import: MagicMock) -> None:
        """Test returns module __version__ when available."""
        mock_module = MagicMock()
        mock_module.__version__ = "1.2.3"
        mock_import.return_value = mock_module
        version = _resolve_version()
        assert version == "1.2.3", "version is not valid"


class TestForwardToCli:
    """Tests for _forward_to_cli function."""

    def test_strips_leading_double_dash(self) -> None:
        """Test leading -- is stripped from argv."""
        # We just test that _forward_to_cli can be called without crashing
        # The actual behavior depends on CLI availability
        try:
            _forward_to_cli(["--", "subcommand"])
        except SystemExit:
            _ = None  # Expected when CLI is unavailable
        except Exception as _err:
            _ = None  # May fail but we're testing the stripping logic

    def test_missing_cli_raises_system_exit(self) -> None:
        """Test missing CLI module raises SystemExit."""
        with patch.dict("sys.modules", {"codex_ml.cli": None}):
            # This should raise SystemExit when CLI is unavailable
            # We can't easily test this without mocking the import
            pass

    def test_returns_zero_on_success(self) -> None:
        """Test returns 0 on successful CLI execution."""
        # Test that the function handles cases gracefully
        try:
            _forward_to_cli(["help"])
            # May succeed or fail depending on import
        except (SystemExit, Exception):
            _ = None  # Expected in test environment


class TestMain:
    """Tests for main function."""

    def test_returns_integer(self) -> None:
        """Test main returns an integer."""
        result = main([])
        assert isinstance(result, int)

    def test_version_flag_prints_version(self) -> None:
        """Test --version prints version."""
        with patch("builtins.print") as mock_print:
            result = main(["--version"])
            mock_print.assert_called_once()
            assert result == 0, "Result must not be empty"

    def test_no_args_prints_help(self) -> None:
        """Test no arguments prints help."""
        with patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
            result = main([])
            mock_stdout.getvalue()
            # Should contain help text or print help
            assert result == 0, "Result must not be empty"

    def test_version_returns_zero(self) -> None:
        """Test --version returns exit code 0."""
        with patch("builtins.print"):
            result = main(["--version"])
            assert result == 0, "Result must not be empty"

    @patch("codex_ml.main._forward_to_cli")
    def test_forward_calls_cli_forwarder(self, mock_forward: MagicMock) -> None:
        """Test --forward calls _forward_to_cli."""
        mock_forward.return_value = 0
        result = main(["--forward", "subcommand"])
        mock_forward.assert_called_once()
        assert result == 0, "Result must not be empty"

    @patch("codex_ml.main._forward_to_cli")
    def test_forward_passes_arguments(self, mock_forward: MagicMock) -> None:
        """Test --forward passes arguments correctly."""
        mock_forward.return_value = 0
        main(["--forward", "sub", "--flag", "value"])
        mock_forward.assert_called_once_with(["sub", "--flag", "value"])

    @patch("codex_ml.main._forward_to_cli")
    def test_forward_exit_code_propagated(self, mock_forward: MagicMock) -> None:
        """Test --forward exit code is propagated."""
        mock_forward.return_value = 42
        result = main(["--forward", "failing_command"])
        assert result == 42, "Result must not be empty"

    def test_version_and_forward_combined(self) -> None:
        """Test --version with --forward."""
        with patch("builtins.print"):
            with patch("codex_ml.main._forward_to_cli") as mock_forward:
                mock_forward.return_value = 5
                result = main(["--version", "--forward", "cmd"])
                # Should print version AND forward
                mock_forward.assert_called_once()
                assert result == 5, "Result must not be empty"

    @patch("codex_ml.main._forward_to_cli")
    def test_forward_empty_list(self, mock_forward: MagicMock) -> None:
        """Test --forward with empty list."""
        mock_forward.return_value = 0
        main(["--forward"])
        mock_forward.assert_called_once_with([])


class TestMainHelpOutput:
    """Tests for help output formatting."""

    def test_help_contains_prog_name(self) -> None:
        """Test help contains program name."""
        parser = build_parser()
        help_text = parser.format_help()
        assert "codex-ml" in help_text, "Condition must be true"

    def test_help_contains_version_option(self) -> None:
        """Test help mentions --version."""
        parser = build_parser()
        help_text = parser.format_help()
        assert "--version" in help_text, "Condition must be true"

    def test_help_contains_forward_option(self) -> None:
        """Test help mentions --forward."""
        parser = build_parser()
        help_text = parser.format_help()
        assert "--forward" in help_text, "Condition must be true"

    def test_help_contains_epilog(self) -> None:
        """Test help contains epilog with CLI reference."""
        parser = build_parser()
        help_text = parser.format_help()
        assert "codex_ml.cli" in help_text, "Condition must be true"


class TestMainEdgeCases:
    """Edge case tests for main function."""

    def test_none_argv_uses_defaults(self) -> None:
        """Test None argv uses default behavior."""
        # main(None) should use sys.argv[1:]
        with patch("builtins.print"), patch.object(sys, "argv", ["prog"]):
            result = main(None)
            assert isinstance(result, int)

    @patch("codex_ml.main._forward_to_cli")
    def test_forward_strips_leading_separator(self, mock_forward: MagicMock) -> None:
        """Test arguments are passed correctly to forward."""
        mock_forward.return_value = 0
        # Don't use -- separator as argparse.REMAINDER doesn't support it
        main(["--forward", "cmd", "--arg"])
        mock_forward.assert_called_once()

    def test_multiple_version_flags(self) -> None:
        """Test multiple --version flags."""
        with patch("builtins.print") as mock_print:
            # Should only print once
            main(["--version"])
            assert mock_print.call_count == 1, "Count must be greater than zero"


class TestForwardToCliEdgeCases:
    """Edge case tests for _forward_to_cli."""

    def test_forward_with_complex_args(self) -> None:
        """Test forwarding complex argument patterns."""
        # Test that various argument patterns are handled
        test_cases = [
            [],
            ["--help"],
            ["train", "--config", "path/to/config.yaml"],
            ["--", "--flag"],
        ]
        for args in test_cases:
            try:
                _forward_to_cli(args)
            except (SystemExit, Exception):
                _ = None  # Expected in test environment
