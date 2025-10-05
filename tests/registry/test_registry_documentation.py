from __future__ import annotations

from codex_ml.registry import Registry
import codex_ml.registry as registry_facade


def test_registry_docstring_contains_table():
    doc = registry_facade.__doc__ or ""
    assert "| ``model_registry``" in doc


def test_registry_temporary_registration():
    reg = Registry("toy")

    class Toy:
        pass

    with reg.temporarily_registered({"toy": Toy}):
        assert reg.get("toy") is Toy
    with reg.temporarily_registered({"alt": Toy}):
        assert reg.list() == ["alt"]
