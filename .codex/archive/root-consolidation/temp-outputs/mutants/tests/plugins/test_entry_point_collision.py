"""
Test Entry Point Collision

Test module for entry point collision.
"""

import sys
import types
import warnings

from codex_ml.plugins.registry import Registry


def test_entry_point_collision_skips(monkeypatch) -> None:
    class Ep:
        def __init__(self, name: str, obj) -> None:
            self.name = name
            self._obj = obj

        def load(self):
            return self._obj

    def fake_iter_entry_points(group: str):
        """Return fake entry points for testing collision detection."""
        return [Ep("dup", types.SimpleNamespace())]

    reg = Registry("x")

    @reg.register("dup")
    class Local:
        pass

    # Get the actual module from sys.modules (not the shadowed function)
    registry_module = sys.modules["codex_ml.plugins.registry"]
    monkeypatch.setattr(registry_module, "_iter_entry_points", fake_iter_entry_points)

    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        count, errs = reg.load_from_entry_points("codex_ml.x")

    assert count == 0 and not errs, "Count must be greater than zero"
    assert reg.get("dup").obj is Local, "Object must be initialized"
    assert any("dup" in str(w.message) for w in rec), "Condition must be true"
