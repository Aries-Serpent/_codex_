"""
Test Registry Documentation

Test module for registry documentation.
"""

from __future__ import annotations

import codex_ml.registry as registry_facade
from codex_ml.registry import Registry


def test_registry_docstring_contains_table():
    doc = registry_facade.__doc__ or ""
    assert "| ``model_registry``" in doc, "Condition must be true"


def test_registry_temporary_registration():
    reg = Registry("toy")

    class Toy:
        pass

    with reg.temporarily_registered({"toy": Toy}):
        assert reg.get("toy") is Toy, "Condition must be true"
    with reg.temporarily_registered({"alt": Toy}):
        assert reg.list() == ["alt"], "Condition must be true"
