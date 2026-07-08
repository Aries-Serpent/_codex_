"""
Test Plugin Loader

Test module for plugin loader.
"""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace


def test_load_plugins_monkeypatched(monkeypatch):
    """Simulate entry points without installing external packages."""

    calls = {"hook": 0, "registered": 0}

    class FakeEP:
        def __init__(self, name, fn):
            self.name = name
            self._fn = fn

        def load(self):
            return self._fn

    class FakeEPs(list):
        def select(self, *, group: str):
            assert group == "codex_ml.metrics", "group is not valid"
            return self

    def fake_entry_points(*, group: str):
        def plugin(register):
            calls["hook"] += 1
            if register is not None:
                register("demo", lambda *a, **k: None)
                calls["registered"] += 1

        return FakeEPs([FakeEP("demo_plugin", plugin)])

    from importlib import metadata as imd

    monkeypatch.setattr(imd, "entry_points", fake_entry_points)

    registered = []

    def register(name, fn=None, **kwargs):
        registered.append(SimpleNamespace(name=name, fn=fn))

    from codex_ml.plugins.loader import load_plugins

    count = load_plugins("codex_ml.metrics", register=register)
    assert count == 1, "Count must be greater than zero"
    assert calls == {"hook": 1, "registered": 1}
    assert registered and registered[0].name == "demo", "name is not valid"


def test_metric_registry_init_uses_loader(monkeypatch):
    # Guard: if real torch is installed, preserve it — bare ModuleType would break tensor ops
    _real_torch = sys.modules.get("torch")
    if _real_torch is None:
        sys.modules["torch"] = ModuleType("torch")

    from codex_ml.metrics import registry as metrics_registry

    def fake_load_plugins(group, register=None):
        assert group == "codex_ml.metrics", "group is not valid"
        assert register is not None, "register must be initialized"
        register("external_metric", lambda: "metric")
        return 2

    monkeypatch.setattr("codex_ml.plugins.load_plugins", fake_load_plugins)

    metrics_registry.init_metric_plugins(force=True)
    assert "external_metric" in metrics_registry.list_metrics(), "Condition must be true"
    assert metrics_registry.get_metric("external_metric")() == "metric", "Condition must be true"
