"""
Test Schema Validate

Test module for schema validate.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

import tools.schema_validate as sv


def _install_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.SimpleNamespace()

    def validate(instance: object, schema: dict[str, object]) -> None:
        required = schema.get("required", []) if isinstance(schema, dict) else []
        if isinstance(required, list):
            for field in required:
                if isinstance(field, str) and not isinstance(instance, dict):
                    raise ValueError("instance must be object")
                if isinstance(field, str) and field not in instance:
                    raise ValueError(f"missing required field: {field}")

    module.validate = validate  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "jsonschema", module)


def test_validate_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_stub(monkeypatch)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
    data = {"name": "ok"}
    s = tmp_path / "s.json"
    d = tmp_path / "d.json"
    s.write_text(json.dumps(schema), encoding="utf-8")
    d.write_text(json.dumps(data), encoding="utf-8")
    assert sv._validate_pair(str(d), str(s)) is True


def test_validate_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _install_stub(monkeypatch)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
    data = {"nope": "x"}
    s = tmp_path / "s.json"
    d = tmp_path / "d.json"
    s.write_text(json.dumps(schema), encoding="utf-8")
    d.write_text(json.dumps(data), encoding="utf-8")
    assert sv._validate_pair(str(d), str(s)) is False
