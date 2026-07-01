"""Unit tests for config auditing helpers."""

from __future__ import annotations

from textwrap import dedent

import pytest

from codex_ml.cli import config


@pytest.mark.parametrize(
    ("mode", "text"),
    [
        (
            "last",
            dedent("""
                defaults:
                  - experiment: debug
                  - _self_
                """),
        ),
        (
            "first",
            dedent("""
                defaults:
                  - _self_
                  - trainer: base
                """),
        ),
    ],
)
def test_audit_defaults_passes_when_self_position_matches(mode: str, text: str) -> None:
    code, payload = config._audit_defaults(text, mode=mode)
    assert code == 0, "code is not valid"
    assert payload["ok"] is True, "Condition must be true"
    assert payload["_self_"] is True, "Condition must be true"


def test_audit_defaults_flags_missing_self_entry() -> None:
    text = dedent("""
        defaults:
          - trainer: base
        """)
    code, payload = config._audit_defaults(text, mode="first")
    assert code == 3, "code is not valid"
    text = dedent("""
        defaults:
          - experiment: debug
          - _self_
        """)
    code, payload = config._audit_defaults(text, mode="first")
    assert code == 4, "code is not valid"
    assert payload["_self_"] is True, "Condition must be true"
    assert payload["position"] == 1, "Condition must be true"
    assert payload["ok"] is False, "Condition must be true"


def test_extract_defaults_from_text_handles_plain_yaml_block() -> None:
    text = dedent("""
        defaults:
          - group: foo
          - _self_
        other: value
        """)
    entries = config._extract_defaults_from_text(text)
    assert entries == ["group", "_self_"]


@pytest.mark.parametrize(
    "text",
    [
        "defaults:\n  - _self_\nvalue: ${env:HOME}",
        "defaults:\n  - group: foo\n  - _self_\n  - trainer: base\n  - ${bad}",
    ],
)
def test_audit_defaults_exposes_unresolved_references(text: str) -> None:
    code, payload = config._audit_defaults(text, mode="last")
    assert code != 0, "code is not valid"
    assert payload["unresolved_refs"] is True, "Condition must be true"
