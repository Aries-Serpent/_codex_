from __future__ import annotations

import pytest

from codex.zendesk import apply as zapply


def test_extract_operations_sequence_ok() -> None:
    plan = {"triggers": [{"op": "add", "path": "/triggers/foo", "value": {"name": "foo"}}]}
    ops = zapply._extract_operations(plan, "triggers")
    assert isinstance(ops, list)
    assert ops[0]["op"] == "add"


def test_extract_operations_scalar_raises() -> None:
    with pytest.raises(ValueError):
        zapply._extract_operations("oops", "triggers")


def test_apply_functions_noop_ok(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    plan = {"fields": [{"op": "add", "path": "/fields/A", "value": {"name": "A"}}]}
    zapply.apply_fields(plan, env="dev")
    assert any("Prepared" in record.message for record in caplog.records)
