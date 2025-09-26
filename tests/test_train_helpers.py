import sys

from codex_ml.utils.train_helpers import clip_gradients, maybe_autocast


def test_maybe_autocast_disabled() -> None:
    with maybe_autocast(enabled=False):
        pass


def test_clip_gradients_without_torch(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)
    clip_gradients([], 1.0)
