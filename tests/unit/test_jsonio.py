"""Tests for codex_ml.utils.jsonio — CLI JSON stdout helpers."""

from __future__ import annotations

import json

from codex_ml.utils.jsonio import _ensure_newline, print_error_json, print_json


class TestEnsureNewline:
    def test_adds_newline_when_missing(self):
        assert _ensure_newline("hello") == "hello\n", "Condition must be true"

    def test_preserves_existing_newline(self):
        assert _ensure_newline("hello\n") == "hello\n", "Condition must be true"

    def test_empty_string(self):
        assert _ensure_newline("") == "\n", "Condition must be true"


class TestPrintJson:
    def test_emits_valid_json_dict(self, capsys):
        print_json({"key": "value", "n": 42})
        out = capsys.readouterr().out
        assert json.loads(out) == {"key": "value", "n": 42}

    def test_output_ends_with_newline(self, capsys):
        print_json({"x": 1})
        out = capsys.readouterr().out
        assert out.endswith("\n"), "Condition must be true"

    def test_emits_list(self, capsys):
        print_json([1, 2, 3])
        out = capsys.readouterr().out
        assert json.loads(out) == [1, 2, 3]

    def test_emits_string(self, capsys):
        print_json("hello")
        out = capsys.readouterr().out
        assert json.loads(out) == "hello", "Condition must be true"

    def test_emits_none(self, capsys):
        print_json(None)
        out = capsys.readouterr().out
        assert json.loads(out) is None, "Condition must be true"


class TestPrintErrorJson:
    def test_basic_error_envelope(self, capsys):
        print_error_json("something went wrong")
        payload = json.loads(capsys.readouterr().out)
        assert payload["ok"] is False, "Condition must be true"
        assert payload["error"] == "something went wrong", "Error should be raised or set"

    def test_includes_code_when_given(self, capsys):
        print_error_json("oops", code=404)
        payload = json.loads(capsys.readouterr().out)
        assert payload["code"] == 404, "Condition must be true"

    def test_includes_details_when_given(self, capsys):
        print_error_json("oops", details={"field": "x"})
        payload = json.loads(capsys.readouterr().out)
        assert payload["details"] == {"field": "x"}, "Condition must be true"

    def test_no_code_key_when_not_given(self, capsys):
        print_error_json("oops")
        payload = json.loads(capsys.readouterr().out)
        assert "code" not in payload, "Condition must be true"

    def test_no_details_key_when_not_given(self, capsys):
        print_error_json("oops")
        payload = json.loads(capsys.readouterr().out)
        assert "details" not in payload, "Condition must be true"

    def test_code_is_cast_to_int(self, capsys):
        print_error_json("oops", code=3.7)  # type: ignore[arg-type]
        payload = json.loads(capsys.readouterr().out)
        assert payload["code"] == 3, "Condition must be true"

    def test_output_ends_with_newline(self, capsys):
        print_error_json("msg")
        out = capsys.readouterr().out
        assert out.endswith("\n"), "Condition must be true"
