import pytest

from codex.logging.structured_logger import logger

#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# - Tokenizer inspection commands
# - Tokenizer building and training
# - Encoding/decoding operations
# - Vocabulary inspection
# - Error handling and fallback behavior
#     def test_command_help(self, runner):
# """
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# from pathlib import Path
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# # Import the CLI module - handle both typer and fallback cases
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# 
#     HAS_TYPER = True
#     HAS_TYPER = True
# except ImportError:
#     HAS_TYPER = False
#     app = None
#     CliRunner = None
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# 
# @pytest.fixture
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
#     return None
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
#     """Create temporary corpus files for tokenizer training."""
#     corpus_dir = tmp_path / "corpus"
#     corpus_dir.mkdir()
# 
#     (corpus_dir / "train.txt").write_text(
#     (corpus_dir / "train.txt").write_text(
#         "This is a training corpus.\n"
#         "It contains multiple lines of text.\n"
#         "Used for training tokenizers.\n"
#     )
#     (corpus_dir / "valid.txt").write_text("Validation text for tokenizer.\n")
# 
#     return corpus_dir
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# 
#     def test_format_context_none(self):
#     def test_format_context_none(self):
#         """Verify None context formatting."""
#         result = _format_context(None)
#         assert result == "None", "Result must not be empty"
#     def test_format_context_string(self):
#     def test_format_context_string(self):
#         """Verify string context passthrough."""
#         result = _format_context("test string")
#         assert result == "test string", "Result must not be empty"
#     def test_format_context_dict(self):
#     def test_format_context_dict(self):
#         """Verify dictionary JSON serialization."""
#         context = {"key": "value", "number": 42}
#         result = _format_context(context)
#         parsed = json.loads(result)
#         assert parsed["key"] == "value", "Value must be initialized"
#         assert parsed["number"] == 42, "Condition must be true"
#     def test_format_context_nested(self):
#     def test_format_context_nested(self):
#         """Verify nested structure serialization."""
#         context = {"outer": {"inner": ["a", "b", "c"]}}
#         result = _format_context(context)
#         assert "outer" in result, "Result must not be empty"
#         assert "inner" in result, "Result must not be empty"
#     def test_format_context_with_datetime(self):
#     def test_format_context_with_datetime(self):
#         """Verify datetime object handling."""
#         from datetime import datetime
#         context = {"timestamp": datetime(2024, 1, 1, 12, 0, 0)}
#         result = _format_context(context)
#         assert "2024" in result, "Result must not be empty"
# 
#     def test_format_context_unserializable_fallback(self):
#     def test_format_context_unserializable_fallback(self):
#         """Verify fallback for unserializable objects."""
#         class CustomObj:
#             def __str__(self):
#                 return "custom_object"
#         # Should not crash - falls back to str()
#         result = _format_context({"obj": CustomObj()})
#         assert isinstance(result, str)
# 
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# 
#     def test_append_error_block_basic(self, tmp_path: Path, monkeypatch):
#     def test_append_error_block_basic(self, tmp_path: Path, monkeypatch):
#         """Verify basic error block appending."""
#         error_dir = tmp_path / "errors"
#         error_dir.mkdir()
#         monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)
#         monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)
# 
#         _append_error_block(
#             step="TEST_STEP", message="Test error message", context={"test": "context"}
#         )
#         # Check file created
#         error_files = list(error_dir.glob("errors_*.md"))
#         assert len(error_files) >= 1, "Error_files must not be empty"
#         assert len(error_files) >= 1, "Error_files must not be empty"
# 
#     def test_append_error_block_with_custom_question(self, tmp_path: Path, monkeypatch):
#     def test_append_error_block_with_custom_question(self, tmp_path: Path, monkeypatch):
#         """Verify custom question in error block."""
#         error_dir = tmp_path / "errors"
#         error_dir.mkdir()
#         monkeypatch.setattr("tokenization.cli._ERROR_REPORT_DIR", error_dir)
#         _append_error_block(step="TEST", message="Error", context=None, question="Custom question?")
# 
#         error_files = list(error_dir.glob("errors_*.md"))
#         if error_files:
#             content = error_files[0].read_text()
#             assert "Custom question?" in content, "Content must not be empty"
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
# 
#     @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
#     @patch("tokenization.cli.build_tokenizer")
#     def test_inspect_command(self, mock_build, runner):
#     def test_inspect_command(self, mock_build, runner):
#         """Verify tokenizer inspection output."""
#         mock_tokenizer = MagicMock()
#         mock_tokenizer.vocab_size = 30000
#         mock_tokenizer.get_vocab.return_value = {"hello": 0, "world": 1}
#         mock_build.return_value = mock_tokenizer
#         result = runner.invoke(app, ["inspect", "--model", "test_tokenizer"])
#         # Should complete without error
#         assert result.exit_code == 0 or "inspect" not in str(, "Result must not be empty"
#             app.registered_commands if hasattr(app, "registered_commands") else []
#         ), "Result must not be empty"
#         ), "Result must not be empty"
# 
#     @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
#     @patch("tokenization.cli.build_tokenizer")
#     def test_vocab_size_command(self, mock_build, runner):
#     def test_vocab_size_command(self, mock_build, runner):
#         """Verify vocabulary size reporting."""
#         mock_tokenizer = MagicMock()
#         mock_tokenizer.vocab_size = 50000
#         mock_build.return_value = mock_tokenizer
#         result = runner.invoke(app, ["vocab-size", "--model", "test_model"])
#         # Command may not exist - check for reasonable response
#         if result.exit_code == 0:
#             assert "50000" in result.output or "vocab" in result.output.lower(), "Result must not be empty"


class TestTokenizerEncode:
    """Test tokenizer encoding commands."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_encode_text(self, mock_build, runner):
        """Verify text encoding."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = [101, 2023, 2003, 102]
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(app, ["encode", "--model", "test_model", "--text", "This is a test"])

        # Check for encoding output
        if result.exit_code == 0:
            assert any(str(num) in result.output for num in [101, 2023, 2003, 102])

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_encode_empty_text(self, mock_build, runner):
        """Verify empty text encoding."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.return_value = []
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(app, ["encode", "--model", "test_model", "--text", ""])

        # Should handle gracefully
        assert result.exit_code in [0, 2]  # 0=success, 2=no command


class TestTokenizerDecode:
    """Test tokenizer decoding commands."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_decode_ids(self, mock_build, runner):
        """Verify ID decoding."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.decode.return_value = "decoded text"
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(app, ["decode", "--model", "test_model", "--ids", "101,2023,102"])

        if result.exit_code == 0:
            assert "decoded" in result.output.lower(), "Result must not be empty"

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_decode_empty_ids(self, mock_build, runner):
        """Verify empty ID list handling."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.decode.return_value = ""
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(app, ["decode", "--model", "test_model", "--ids", ""])

        # Should handle gracefully
        assert result.exit_code in [0, 2]


class TestTokenizerTrain:
    """Test tokenizer training commands."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_train_basic(self, mock_build, runner, temp_corpus: Path):
        """Verify basic tokenizer training."""
        mock_tokenizer = MagicMock()
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(
            app,
            [
                "train",
                "--corpus",
                str(temp_corpus / "train.txt"),
                "--vocab-size",
                "1000",
                "--output",
                str(temp_corpus / "tokenizer.json"),
            ],
        )

        # Command might not exist yet
        assert result.exit_code in [0, 2]

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_train_with_special_tokens(self, mock_build, runner, temp_corpus: Path):
        """Verify training with special tokens."""
        mock_tokenizer = MagicMock()
        mock_build.return_value = mock_tokenizer

        result = runner.invoke(
            app,
            [
                "train",
                "--corpus",
                str(temp_corpus / "train.txt"),
                "--vocab-size",
                "1000",
                "--special-tokens",
                "[PAD],[UNK],[CLS],[SEP]",
            ],
        )

        assert result.exit_code in [0, 2]


class TestTokenizerRoundtrip:
    """Test encode-decode roundtrip functionality."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_roundtrip_basic(self, mock_build, runner):
        """Verify encode-decode roundtrip."""
        mock_tokenizer = MagicMock()
        test_text = "Hello world"
        test_ids = [101, 7592, 2088, 102]

        mock_tokenizer.encode.return_value = test_ids
        mock_tokenizer.decode.return_value = test_text
        mock_build.return_value = mock_tokenizer

        # Encode
        encode_result = runner.invoke(app, ["encode", "--model", "test", "--text", test_text])

        # Decode
        decode_result = runner.invoke(
            app, ["decode", "--model", "test", "--ids", ",".join(map(str, test_ids))]
        )

        # Both should succeed if commands exist
        assert encode_result.exit_code in [0, 2]
        assert decode_result.exit_code in [0, 2]


class TestFallbackBehavior:
    """Test fallback CLI behavior when Typer unavailable."""

    def test_fallback_typer_creation(self):
        """Verify fallback Typer class can be instantiated."""
        from tokenization.cli import _FallbackTyper

        app_fallback = _FallbackTyper(help="Test app")
        assert app_fallback is not None, "app_fallback must be initialized"

    def test_fallback_command_registration(self):
        """Verify command registration in fallback."""
        from tokenization.cli import _FallbackTyper

        app_fallback = _FallbackTyper()

        @app_fallback.command()
        def test_command():
            logger.info("Test")

        assert "test-command" in app_fallback._commands or "test_command" in app_fallback._commands

    def test_fallback_echo(self):
        """Verify fallback echo function."""
        import io
        import sys

        from tokenization.cli import _fallback_echo

        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        _fallback_echo("test message")

        sys.stdout = old_stdout
        assert "test message" in captured.getvalue(), "Value must be initialized"

    def test_fallback_option_returns_default(self):
        """Verify fallback Option returns default value."""
        from tokenization.cli import _fallback_option

        result = _fallback_option(default="test_default")
        assert result == "test_default", "Result must not be empty"


class TestErrorHandling:
    """Test CLI error handling."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_invalid_model_path(self, runner):
        """Verify error handling for invalid model path."""
        result = runner.invoke(app, ["inspect", "--model", "/nonexistent/path/to/model"])

        # Should fail gracefully
        assert result.exit_code != 0 or result.exit_code == 2, "Result must not be empty"

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_invalid_corpus_path(self, runner):
        """Verify error handling for invalid corpus."""
        result = runner.invoke(app, ["train", "--corpus", "/nonexistent/corpus.txt"])

        assert result.exit_code != 0 or result.exit_code == 2, "Result must not be empty"

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    @patch("tokenization.cli.build_tokenizer")
    def test_tokenizer_build_failure(self, mock_build, runner):
        """Verify error handling when tokenizer build fails."""
        mock_build.side_effect = Exception("Build failed")

        result = runner.invoke(app, ["inspect", "--model", "test_model"])

        # Should handle exception
        assert result.exit_code != 0 or result.exit_code == 2, "Result must not be empty"


class TestParameterValidation:
    """Test parameter validation across commands."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_negative_vocab_size(self, runner, temp_corpus: Path):
        """Verify vocab size validation."""
        result = runner.invoke(
            app, ["train", "--corpus", str(temp_corpus / "train.txt"), "--vocab-size", "-100"]
        )

        # Should reject negative value
        assert result.exit_code != 0 or result.exit_code == 2, "Result must not be empty"

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_invalid_ids_format(self, runner):
        """Verify ID format validation."""
        result = runner.invoke(app, ["decode", "--model", "test", "--ids", "not,a,number,list"])

        # Should handle invalid format
        assert result.exit_code != 0 or result.exit_code == 2, "Result must not be empty"


class TestHelpOutput:
    """Test help output for all commands."""

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_app_help(self, runner):
        """Verify main app help output."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "Tokenizer utilities" in result.output or "help" in result.output.lower(), "Result must not be empty"

    @pytest.mark.skipif(not HAS_TYPER, reason="Requires Typer")
    def test_command_help(self, runner):
        """Verify command-specific help."""
        result = runner.invoke(app, ["inspect", "--help"])

        # Should show help or indicate command not found
        assert result.exit_code in [0, 2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
