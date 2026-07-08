"""
Test Entry Point Discovery

Test module for entry point discovery.
"""

import types

from codex_ml.plugins.registry import Registry


def test_entry_point_discovery(monkeypatch) -> None:
    class Ep:
        def __init__(self, name: str, obj, fail: bool = False, api: str = "v1") -> None:
            self.name = name
            self.value = "mod:obj"
            self._obj = obj
            self._fail = fail
            self._api = api

        def load(self):
            if self._fail:
                raise RuntimeError("boom")
            self._obj.__codex_ext_api__ = self._api
            return self._obj

    def fake_entry_points():
        class Eps:
            def select(self, group: str):
                ok = Ep("ok", types.SimpleNamespace())
                bad = Ep("bad", types.SimpleNamespace(), fail=True)
                inc = Ep("inc", types.SimpleNamespace(), api="v0")
                return [ok, bad, inc]

        return Eps()

    # Patch importlib.metadata.entry_points which is imported in registry.py
    import importlib.metadata

    monkeypatch.setattr(importlib.metadata, "entry_points", fake_entry_points)

    reg = Registry("x")
    count, errs = reg.load_from_entry_points("codex_ml.x", require_api="v1")
    assert count == 1, "Count must be greater than zero"
    assert "bad" in errs and "boom" in errs["bad"], "Condition must be true"
    assert "inc" not in errs, "Condition must be true"
