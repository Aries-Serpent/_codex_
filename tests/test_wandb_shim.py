from __future__ import annotations

import builtins
import os
import sys
import types

from codex_ml.utils.logging_wandb import maybe_wandb


def test_maybe_wandb_returns_dummy_when_missing(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "wandb":
            raise ImportError("wandb missing")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with maybe_wandb(run_name="test", enable=True) as wb:
        wb.log({"metric": 1.0}, step=1)


def test_maybe_wandb_disabled():
    with maybe_wandb(run_name="disabled", enable=False) as wb:
        wb.log({"metric": 0.0}, step=0)


def test_maybe_wandb_enforces_offline_mode(monkeypatch):
    calls: dict[str, object] = {}

    class DummyRun:
        def __init__(self) -> None:
            calls["finished"] = False

        def finish(self) -> None:
            calls["finished"] = True

    def fake_init(**kwargs):
        calls["init"] = kwargs
        return DummyRun()

    def fake_log(data, step=None):  # type: ignore[no-untyped-def]
        calls.setdefault("log", []).append((data, step))

    module = types.SimpleNamespace(init=fake_init, log=fake_log)
    monkeypatch.setitem(sys.modules, "wandb", module)
    monkeypatch.delenv("WANDB_MODE", raising=False)
    monkeypatch.delenv("WANDB_PROJECT", raising=False)
    monkeypatch.delenv("WANDB_DIR", raising=False)

    with maybe_wandb(run_name="offline-test", enable=True) as wb:
        wb.log({"value": 1.0}, step=5)

    init_kwargs = calls.get("init")
    assert isinstance(init_kwargs, dict)
    assert init_kwargs["mode"] == "offline"
    assert init_kwargs["project"] == "codex-offline"
    assert calls.get("finished") is True
    assert os.environ.get("WANDB_MODE") == "offline"
