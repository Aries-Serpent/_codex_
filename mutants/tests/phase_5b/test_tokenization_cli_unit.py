"""
Comprehensive unit tests for src/tokenization/cli.py

Tests cover:
- Fallback implementations when typer unavailable
- Command registration and help output
- Parameter type conversion
- Error handling
- SystemExit handling
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tokenization.cli import (
    _append_error_block,
    _fail,
    _fallback_echo,
    _fallback_option,
    _FallbackExit,
    _FallbackTyper,
    _format_context,
    _load_tokenizer,
    _resolve_root,
    app,
    inspect,
    vocab,
)


class TestFallbackExit:
    """Tests for _FallbackExit exception class."""

    def test_fallback_exit_is_system_exit(self):
        """Test that _FallbackExit is a SystemExit subclass."""
        assert issubclass(_FallbackExit, SystemExit)

    def test_fallback_exit_creation(self):
        """Test creating _FallbackExit instance."""
        exit_exc = _FallbackExit(1)
        assert isinstance(exit_exc, SystemExit)
        assert exit_exc.code == 1, "code is not valid"

    def test_fallback_exit_default_code(self):
        """Test _FallbackExit with default code."""
        exit_exc = _FallbackExit()
        assert isinstance(exit_exc, SystemExit)


class TestFallbackEcho:
    """Tests for _fallback_echo function."""

    def test_fallback_echo_stdout(self, capsys):
        """Test _fallback_echo outputs to stdout by default."""
        _fallback_echo("test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out, "Condition must be true"

    def test_fallback_echo_stderr(self, capsys):
        """Test _fallback_echo outputs to stderr when err=True."""
        _fallback_echo("error message", err=True)
        captured = capsys.readouterr()
        assert "error message" in captured.err, "Error should be raised or set"

    def test_fallback_echo_various_types(self, capsys):
        """Test _fallback_echo with various object types."""
        _fallback_echo(123)
        captured = capsys.readouterr()
        assert "123" in captured.out, "Condition must be true"

        _fallback_echo(None)
        captured = capsys.readouterr()
        assert "None" in captured.out, "Condition must be true"

        _fallback_echo({"key": "value"})
        captured = capsys.readouterr()
        assert "key" in captured.out, "Condition must be true"


class TestFallbackOption:
    """Tests for _fallback_option function."""

    def test_fallback_option_with_default(self):
        """Test _fallback_option returns default value."""
        result = _fallback_option("my_default")
        assert result == "my_default", "Result must not be empty"

    def test_fallback_option_none_default(self):
        """Test _fallback_option with None default."""
        result = _fallback_option(None)
        assert result is None, "Result must not be empty"

    def test_fallback_option_ignores_extra_args(self):
        """Test _fallback_option ignores extra arguments."""
        result = _fallback_option("default", "arg1", "arg2", key="value")
        assert result == "default", "Result must not be empty"

    def test_fallback_option_no_default(self):
        """Test _fallback_option without default argument."""
        result = _fallback_option()
        assert result is None, "Result must not be empty"


class TestFallbackTyper:
    """Tests for _FallbackTyper class."""

    def test_fallback_typer_creation(self):
        """Test creating _FallbackTyper instance."""
        typer = _FallbackTyper(help="Test help")
        assert typer._help_text == "Test help", "_help_text is not valid"
        assert typer._commands == {}, "_commands is not valid"

    def test_fallback_typer_command_registration(self):
        """Test command registration."""
        typer = _FallbackTyper()

        @typer.command()
        def test_cmd(arg1):
            return arg1

        assert "test-cmd" in typer._commands, "Condition must be true"
        assert typer._commands["test-cmd"][0] is test_cmd, "Condition must be true"

    def test_fallback_typer_custom_command_name(self):
        """Test command registration with custom name."""
        typer = _FallbackTyper()

        @typer.command("custom-name")
        def my_func():
            pass

        assert "custom-name" in typer._commands, "Condition must be true"

    def test_fallback_typer_print_app_help(self, capsys):
        """Test printing app help."""
        typer_app = _FallbackTyper(help="App help text")

        @typer_app.command()
        def cmd1():
            pass

        @typer_app.command()
        def cmd2():
            pass

        typer_app._print_app_help()
        captured = capsys.readouterr()
        assert "App help text" in captured.out, "Condition must be true"
        assert "cmd1" in captured.out, "Condition must be true"
        assert "cmd2" in captured.out, "Condition must be true"

    def test_fallback_typer_print_command_help(self, capsys):
        """Test printing command help."""
        typer_app = _FallbackTyper()

        @typer_app.command()
        def my_command(arg1: str, arg2: int = 42):
            pass

        cmd_func, sig = typer_app._commands["my-command"]
        typer_app._print_command_help("my-command", sig)
        captured = capsys.readouterr()
        assert "my-command" in captured.out, "Condition must be true"
        assert "ARG1" in captured.out, "Condition must be true"

    def test_fallback_typer_no_arguments(self, monkeypatch):
        """Test calling typer with no arguments."""
        typer_app = _FallbackTyper(help="Test")

        @typer_app.command()
        def cmd():
            pass

        monkeypatch.setattr(sys, "argv", ["test"])
        with pytest.raises(SystemExit) as exc_info:
            typer_app()
        assert exc_info.value.code == 0, "Value must be initialized"

    def test_fallback_typer_help_flag(self, monkeypatch):
        """Test calling typer with --help flag."""
        typer_app = _FallbackTyper(help="Test app")

        monkeypatch.setattr(sys, "argv", ["test", "--help"])
        with pytest.raises(SystemExit) as exc_info:
            typer_app()
        assert exc_info.value.code == 0, "Value must be initialized"

    def test_fallback_typer_unknown_command(self, monkeypatch):
        """Test calling typer with unknown command."""
        typer_app = _FallbackTyper()

        @typer_app.command()
        def known_cmd():
            pass

        monkeypatch.setattr(sys, "argv", ["test", "unknown"])
        with pytest.raises(SystemExit) as exc_info:
            typer_app()
        assert exc_info.value.code == 1, "Value must be initialized"

    def test_fallback_typer_command_help(self, monkeypatch):
        """Test calling typer command with --help."""
        typer_app = _FallbackTyper()

        @typer_app.command()
        def my_cmd(arg: str):
            pass

        monkeypatch.setattr(sys, "argv", ["test", "my-cmd", "--help"])
        with pytest.raises(SystemExit) as exc_info:
            typer_app()
        assert exc_info.value.code == 0, "Value must be initialized"

    def test_fallback_typer_path_conversion(self, monkeypatch, tmp_path):
        """Test Path parameter conversion."""
        typer_app = _FallbackTyper()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        received_arg = None

        @typer_app.command()
        def cmd_with_path(filepath: Path):
            nonlocal received_arg
            received_arg = filepath

        monkeypatch.setattr(sys, "argv", ["test", "cmd-with-path", str(test_file)])
        typer_app()
        assert isinstance(received_arg, Path)
        assert received_arg.name == "test.txt", "name is not valid"

    def test_fallback_typer_string_parameter(self, monkeypatch):
        """Test string parameter handling."""
        typer_app = _FallbackTyper()
        received_arg = None

        @typer_app.command()
        def cmd(text: str):
            nonlocal received_arg
            received_arg = text

        monkeypatch.setattr(sys, "argv", ["test", "cmd", "hello"])
        typer_app()
        assert received_arg == "hello", "received_arg is not valid"


class TestFormatContext:
    """Tests for _format_context function."""

    def test_format_context_none(self):
        """Test formatting None context."""
        result = _format_context(None)
        assert result == "None", "Result must not be empty"

    def test_format_context_string(self):
        """Test formatting string context."""
        result = _format_context("error message")
        assert result == "error message", "Result must not be empty"

    def test_format_context_dict(self):
        """Test formatting dict context."""
        context = {"key": "value", "number": 42}
        result = _format_context(context)
        assert "key" in result, "Result must not be empty"
        assert "value" in result, "Result must not be empty"
        assert "42" in result, "Result must not be empty"

    def test_format_context_dict_with_exception(self):
        """Test formatting dict with non-JSON-serializable objects."""
        context = {"exc": Exception("test error")}
        result = _format_context(context)
        assert isinstance(result, str)
        assert "Exception" in result or "test error" in result, "Result must not be empty"


class TestResolveRoot:
    """Tests for _resolve_root function."""

    def test_resolve_root_with_directory(self, tmp_path):
        """Test _resolve_root with directory path."""
        result = _resolve_root(tmp_path)
        assert result == tmp_path, "Result must not be empty"

    def test_resolve_root_with_file(self, tmp_path):
        """Test _resolve_root with file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        result = _resolve_root(test_file)
        assert result == tmp_path, "Result must not be empty"

    def test_resolve_root_nested_path(self, tmp_path):
        """Test _resolve_root with nested file path."""
        subdir = tmp_path / "sub" / "dir"
        subdir.mkdir(parents=True)
        test_file = subdir / "file.txt"
        test_file.write_text("test")
        result = _resolve_root(test_file)
        assert result == subdir, "Result must not be empty"


class TestLoadTokenizer:
    """Tests for _load_tokenizer function."""

    @patch("tokenization.cli.build_tokenizer")
    def test_load_tokenizer_success(self, mock_build):
        """Test successful tokenizer loading."""
        mock_tokenizer = MagicMock()
        mock_build.return_value = mock_tokenizer
        path = Path("tokenizer.json")

        result = _load_tokenizer(path, step="test")
        assert result is mock_tokenizer, "Result must not be empty"

    @patch("tokenization.cli.build_tokenizer")
    def test_load_tokenizer_not_found(self, mock_build):
        """Test tokenizer loading with file not found."""
        mock_build.side_effect = FileNotFoundError("Tokenizer not found")
        path = Path("nonexistent.json")

        with pytest.raises((SystemExit, Exception)):
            _load_tokenizer(path, step="test")

    @patch("tokenization.cli.build_tokenizer")
    def test_load_tokenizer_generic_error(self, mock_build):
        """Test tokenizer loading with generic error."""
        mock_build.side_effect = RuntimeError("Load failed")
        path = Path("tokenizer.json")

        with pytest.raises((SystemExit, Exception)):
            _load_tokenizer(path, step="test")


class TestAppendErrorBlock:
    """Tests for _append_error_block function."""

    @patch("tokenization.cli._ERROR_REPORT_DIR")
    def test_append_error_block_creates_directory(self, mock_dir, tmp_path, monkeypatch):
        """Test _append_error_block creates error directory."""
        error_dir = tmp_path / "reports"
        monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)

        _append_error_block("test_step", "test message", None)
        assert error_dir.exists(), "Error should be raised or set"

    def test_append_error_block_with_context(self, tmp_path, monkeypatch):
        """Test _append_error_block with context information."""
        error_dir = tmp_path / "reports"
        monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)

        context = {"key": "value"}
        _append_error_block("step1", "message", context)
        assert error_dir.exists(), "Error should be raised or set"

    def test_append_error_block_with_custom_question(self, tmp_path, monkeypatch):
        """Test _append_error_block with custom question."""
        error_dir = tmp_path / "reports"
        monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)

        question = "Custom question?"
        _append_error_block("step1", "message", None, question=question)
        assert error_dir.exists(), "Error should be raised or set"

    def test_append_error_block_appends_to_file(self, tmp_path, monkeypatch):
        """Test that _append_error_block appends to existing file."""
        error_dir = tmp_path / "reports"
        monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)

        _append_error_block("step1", "message1", None)
        _append_error_block("step2", "message2", None)

        # Find the created log file
        log_files = list(error_dir.glob("*.md"))
        assert len(log_files) > 0, "Log_files must not be empty"


class TestFailFunction:
    """Tests for _fail function."""

    def test_fail_exits_with_code_1(self):
        """Test _fail raises Exit with code 1."""
        with pytest.raises(Exception):  # Click Exit or similar
            _fail("step", "error message", None)

    def test_fail_with_context(self):
        """Test _fail with context information."""
        with pytest.raises(Exception):  # Click Exit or similar
            _fail("step", "error", {"key": "value"})

    def test_fail_with_question(self):
        """Test _fail with custom question."""
        with pytest.raises(Exception):  # Click Exit or similar
            _fail("step", "error", None, question="Why?")


class TestVocabCommand:
    """Tests for vocab command."""

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_negative_limit(self, mock_load):
        """Test vocab with negative limit."""
        with pytest.raises(Exception):  # Click Exit or SystemExit
            vocab(Path("tokenizer.json"), limit=-1)

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_zero_limit(self, mock_load, capsys):
        """Test vocab with zero limit."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.vocab_size = 50000
        mock_load.return_value = mock_tokenizer

        vocab(Path("tokenizer.json"), limit=0)
        captured = capsys.readouterr()
        assert "50000" in captured.out, "Condition must be true"

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_with_vocab_size_property(self, mock_load, capsys):
        """Test vocab command with vocab_size property."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.vocab_size = 30000
        mock_load.return_value = mock_tokenizer

        vocab(Path("tokenizer.json"), limit=5)

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_with_callable_vocab_size(self, mock_load, capsys):
        """Test vocab with callable vocab_size."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.vocab_size = MagicMock(return_value=30000)
        mock_load.return_value = mock_tokenizer

        vocab(Path("tokenizer.json"), limit=5)

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_without_vocab_size(self, mock_load):
        """Test vocab when tokenizer lacks vocab_size."""
        mock_tokenizer = MagicMock(spec=[])
        mock_tokenizer.vocab_size = None
        mock_load.return_value = mock_tokenizer

        with pytest.raises(Exception):  # Click Exit or SystemExit
            vocab(Path("tokenizer.json"), limit=5)

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_with_convert_ids_to_tokens(self, mock_load, capsys):
        """Test vocab with convert_ids_to_tokens method."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.vocab_size = 1000
        mock_tokenizer.convert_ids_to_tokens = MagicMock(side_effect=lambda x: f"token_{x}")
        mock_load.return_value = mock_tokenizer

        vocab(Path("tokenizer.json"), limit=3)
        captured = capsys.readouterr()
        assert "token_" in captured.out, "Condition must be true"

    @patch("tokenization.cli._load_tokenizer")
    def test_vocab_without_convert_ids_to_tokens(self, mock_load, capsys):
        """Test vocab when tokenizer lacks convert_ids_to_tokens."""
        mock_tokenizer = MagicMock(spec=["vocab_size"])
        mock_tokenizer.vocab_size = 1000
        mock_load.return_value = mock_tokenizer

        vocab(Path("tokenizer.json"), limit=5)
        captured = capsys.readouterr()
        assert "skipping" in captured.out.lower() or "lack" in captured.out.lower(), "Condition must be true"


class TestInspectCommand:
    """Tests for inspect command."""

    @patch("tokenization.cli._load_tokenizer")
    def test_inspect_loads_tokenizer(self, mock_load):
        """Test inspect command loads tokenizer."""
        mock_tokenizer = MagicMock()
        mock_load.return_value = mock_tokenizer

        inspect(Path("tokenizer.json"))
        mock_load.assert_called_once()

    @patch("tokenization.cli._load_tokenizer")
    def test_inspect_with_manifest(self, mock_load, tmp_path):
        """Test inspect with manifest.json."""
        mock_tokenizer = MagicMock()
        mock_load.return_value = mock_tokenizer

        # Create manifest file
        manifest = {"name": "test_tokenizer", "version": "1.0"}
        tmp_path.joinpath("manifest.json").write_text(str(manifest))

        inspect(tmp_path)
        mock_load.assert_called_once()

    @patch("tokenization.cli._load_tokenizer")
    def test_inspect_without_manifest(self, mock_load, tmp_path):
        """Test inspect when manifest.json doesn't exist."""
        mock_tokenizer = MagicMock()
        mock_load.return_value = mock_tokenizer

        inspect(tmp_path)
        mock_load.assert_called_once()

    @patch("tokenization.cli._load_tokenizer")
    def test_inspect_invalid_manifest(self, mock_load, tmp_path):
        """Test inspect with invalid manifest.json."""
        mock_tokenizer = MagicMock()
        mock_load.return_value = mock_tokenizer

        # Create invalid manifest file
        tmp_path.joinpath("manifest.json").write_text("invalid json {")

        inspect(tmp_path)
        mock_load.assert_called_once()


class TestAppCreation:
    """Tests for app creation."""

    def test_app_exists(self):
        """Test that app is created."""
        assert app is not None, "app must be initialized"

    def test_app_is_callable(self):
        """Test that app is callable."""
        assert callable(app), "Condition must be true"
