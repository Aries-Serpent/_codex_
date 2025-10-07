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

    def fake_entry_points():
        class Eps:
            def select(self, group: str):
                return [Ep("dup", types.SimpleNamespace())]

        return Eps()

    reg = Registry("x")

    @reg.register("dup")
    class Local:
        pass

    monkeypatch.setattr("codex_ml.plugins.registry.metadata.entry_points", fake_entry_points)

    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        count, errs = reg.load_from_entry_points("codex_ml.x")

    assert count == 0 and not errs
    assert reg.get("dup").obj is Local
    assert any("dup" in str(w.message) for w in rec)
