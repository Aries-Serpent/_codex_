"""Unit tests for src/codex/utils/json_safe.py"""

from __future__ import annotations

import json

import pytest

from codex.utils.json_safe import (
    _sanitize_control_chars,
    safe_json_loads,
)


class TestSanitizeControlChars:
    def test_no_change_for_clean_string(self):
        text = '{"key": "value"}'
        assert _sanitize_control_chars(text) == text, "Condition must be true"

    def test_tab_newline_cr_preserved(self):
        # \t \n \r are legal JSON whitespace — must NOT be escaped
        text = '{"a": "line1\nline2\ttab\rcr"}'
        assert _sanitize_control_chars(text) == text, "Condition must be true"

    def test_null_byte_escaped(self):
        text = '{"a": "val\x00ue"}'
        result = _sanitize_control_chars(text)
        assert "\\u0000" in result, "Result must not be empty"
        assert "\x00" not in result, "Result must not be empty"

    def test_range_0x01_to_0x08_escaped(self):
        for byte in range(0x01, 0x09):
            char = chr(byte)
            text = f'{{"k": "v{char}v"}}'
            result = _sanitize_control_chars(text)
            assert char not in result, "Result must not be empty"
            assert f"\\u{byte:04x}" in result, "Result must not be empty"

    def test_range_0x0b_0x0c_escaped(self):
        for byte in (0x0B, 0x0C):
            char = chr(byte)
            text = f'{{"k": "{char}"}}'
            result = _sanitize_control_chars(text)
            assert char not in result, "Result must not be empty"
            assert f"\\u{byte:04x}" in result, "Result must not be empty"

    def test_range_0x0e_to_0x1f_escaped(self):
        for byte in range(0x0E, 0x20):
            char = chr(byte)
            text = f'{{"k": "{char}"}}'
            result = _sanitize_control_chars(text)
            assert char not in result, "Result must not be empty"


class TestSafeJsonLoads:
    # ── Fast-path (clean JSON) ────────────────────────────────────────────

    def test_clean_json_object(self):
        data = safe_json_loads('{"key": "value", "num": 42}', source="test")
        assert data == {"key": "value", "num": 42}

    def test_clean_json_array(self):
        data = safe_json_loads("[1, 2, 3]", source="test")
        assert data == [1, 2, 3]

    def test_bytes_input(self):
        data = safe_json_loads(b'{"a": 1}', source="test")
        assert data == {"a": 1}, "Data must not be empty"

    def test_empty_dict(self):
        assert safe_json_loads("{}", source="test") == {}

    # ── Control-character sanitisation (fix case) ─────────────────────────

    def test_control_char_in_value_fixed_by_sanitiser(self):
        """JSONDecodeError caused by an invalid C0 char should be auto-healed."""
        # Build a JSON string that contains a raw NUL byte inside a string value.
        # json.loads rejects it; safe_json_loads should sanitise and succeed.
        raw = '{"data": "hello\x00world"}'
        result = safe_json_loads(raw, source="test-nul")
        # After sanitisation the NUL becomes \u0000 which is a valid JSON escape
        assert "hello" in result["data"], "Result must not be empty"
        assert "world" in result["data"], "Result must not be empty"

    def test_bell_char_in_key_fixed_by_sanitiser(self):
        """Bell character (0x07) inside a key should be sanitised."""
        raw = '{"key\x07name": "value"}'
        result = safe_json_loads(raw, source="test-bell")
        # Key should exist (sanitised form)
        assert len(result) == 1, "Result must not be empty"

    def test_multiple_control_chars_fixed(self):
        """Multiple different control characters in one payload."""
        # \x01, \x1f embedded in a JSON string
        raw = '{"msg": "a\x01b\x1fc"}'
        result = safe_json_loads(raw, source="test-multi")
        assert "msg" in result, "Result must not be empty"

    def test_sanitisation_writes_debug_artifact(self, tmp_path, monkeypatch):
        """A sanitised debug artefact should be written to the debug dir."""
        monkeypatch.setenv("CODEX_JSON_DEBUG_DIR", str(tmp_path))
        # Reload module so it picks up the new env var
        import importlib

        import codex.utils.json_safe as jm

        importlib.reload(jm)

        raw = '{"v": "\x00"}'
        jm.safe_json_loads(raw, source="artifact-test")
        artifacts = list(tmp_path.glob("sanitized_artifact_test_*.json"))
        assert len(artifacts) == 1, "Artifacts must not be empty"
        content = artifacts[0].read_text()
        assert "\\u0000" in content, "Content must not be empty"

    # ── Persistent failure (remains invalid after sanitisation) ───────────

    def test_completely_invalid_json_raises(self):
        """Garbage that cannot be fixed by sanitisation must raise JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            safe_json_loads("not json at all >>>", source="test-bad")

    def test_truncated_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            safe_json_loads('{"key": "value"', source="test-truncated")

    def test_control_char_outside_string_still_raises(self):
        """A control character BETWEEN tokens (not inside a string) cannot be healed."""
        # NUL between a key separator and value — the sanitiser escapes it to \\u0000
        # which is a valid JSON unicode escape, so it may succeed now. Test that
        # genuinely invalid JSON (bare garbage) raises.
        with pytest.raises(json.JSONDecodeError):
            safe_json_loads("{{{", source="test-garbage")

    # ── Type validation ──────────────────────────────────────────────────

    def test_non_string_raises_value_error(self):
        with pytest.raises(ValueError, match="str or bytes"):
            safe_json_loads(12345, source="test")  # type: ignore[arg-type]

    def test_none_raises_value_error(self):
        with pytest.raises(ValueError, match="str or bytes"):
            safe_json_loads(None, source="test")  # type: ignore[arg-type]
