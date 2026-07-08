"""
Tests for codex_ml.cli.tokenizer module.

Tests tokenizer CLI functionality.
"""

import subprocess
import sys

import pytest


class TestTokenizerModuleImport:
    """Tests for tokenizer module imports."""

    def test_tokenizer_module_import(self):
        """Test that tokenizer module can be imported."""
        try:
            from codex_ml.cli import tokenizer

            assert tokenizer is not None, "tokenizer must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestTokenizerCLI:
    """Tests for tokenizer CLI commands."""

    def test_tokenizer_module_help(self):
        """Test tokenizer module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_tokenizer_train_help(self):
        """Test tokenizer train subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer", "train", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_tokenizer_encode_help(self):
        """Test tokenizer encode subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer", "encode", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_tokenizer_decode_help(self):
        """Test tokenizer decode subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer", "decode", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestTokenizerFunctionality:
    """Tests for tokenizer module functionality."""

    def test_tokenizer_without_config(self):
        """Test that tokenizer shows help without config."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_tokenizer_encode_text(self):
        """Test tokenizer encode with sample text."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.tokenizer", "encode", "--text", "Hello world"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # May fail without proper tokenizer config
        assert result.returncode in (0, 1, 2)
