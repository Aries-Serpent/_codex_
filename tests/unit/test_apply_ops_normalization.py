"""Unit tests for Zendesk plan normalization helpers."""

from unittest.mock import patch

import pytest

from codex.zendesk import apply as zapply


def test_extract_operations_sequence_ok() -> None:
    plan = {"triggers": [{"op": "add", "path": "/triggers/foo", "value": {"name": "foo"}}]}
    ops = zapply._extract_operations(plan, "triggers")
    assert isinstance(ops, list)
    assert ops[0]["op"] == "add", "Condition must be true"


def test_extract_operations_scalar_raises() -> None:
    with pytest.raises(ValueError):
        zapply._extract_operations("oops", "triggers")


def test_apply_functions_noop_ok() -> None:
    plan = {"fields": [{"op": "add", "path": "/fields/A", "value": {"name": "A"}}]}
    with patch.object(zapply.LOGGER, "info") as mock_info:
        zapply.apply_fields(plan, env="dev")
    assert any("Prepared" in str(call.args[0]) for call in mock_info.call_args_list), "Condition must be true"
