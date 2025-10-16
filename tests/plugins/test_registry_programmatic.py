from __future__ import annotations

from codex_ml.plugins import BasePlugin, registry


class _DummyPlugin(BasePlugin):
    def name(self) -> str:
        return "dummy"

    def version(self) -> str:
        return "0.0.1"


def test_programmatic_register_and_get():
    reg = registry()
    plugin = _DummyPlugin()
    reg.register(plugin, override=True)
    assert reg.get("dummy") is plugin
    names = {p.name() for p in reg.all()}
    assert "dummy" in names
