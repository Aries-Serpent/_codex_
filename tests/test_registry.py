from importlib.metadata import EntryPoint

import pytest

from codex_ml.registry.base import (
    Registry,
    RegistryConflictError,
    RegistryLoadError,
    RegistryNotFoundError,
)


def test_registry_register_get_roundtrip():
    reg = Registry("demo")

    @reg.register("toy")
    def _build():  # pragma: no cover - trivial
        return 41

    assert callable(reg.get("toy"))
    assert reg.get("toy")() == 41
    assert "toy" in reg.list()


def test_registry_duplicate_registration_conflict():
    reg = Registry("demo")
    reg.register("dup")(lambda: 1)
    with pytest.raises(RegistryConflictError):
        reg.register("dup")(lambda: 2)


def test_registry_override_replaces():
    reg = Registry("demo")
    reg.register("item")(lambda: 1)
    reg.register("item", override=True)(lambda: 2)
    assert reg.get("item")() == 2


def test_registry_missing_key_raises():
    reg = Registry("demo")
    with pytest.raises(RegistryNotFoundError):
        reg.get("unknown")


def test_registry_entry_point_loading(monkeypatch):
    def fake_entry_points(*, group=None):
        if group != "codex_ml.tests":
            return ()
        ep = EntryPoint(name="toy", value="examples.plugins.toy_metric:build", group=group)
        return (ep,)

    monkeypatch.setattr("codex_ml.registry.base.metadata.entry_points", fake_entry_points)
    reg = Registry("metric", entry_point_group="codex_ml.tests")
    fn = reg.get("toy")
    assert callable(fn)
    assert fn() == {"name": "toy_metric"}


def test_registry_bubbles_entry_point_failure(monkeypatch):
    def fake_entry_points(*, group=None):
        if group != "codex_ml.tests":
            return ()
        ep = EntryPoint(name="broken", value="examples.plugins.broken:missing", group=group)
        return (ep,)

    monkeypatch.setattr("codex_ml.registry.base.metadata.entry_points", fake_entry_points)
    reg = Registry("metric", entry_point_group="codex_ml.tests")
    with pytest.raises(RegistryLoadError):
        reg.get("broken")
