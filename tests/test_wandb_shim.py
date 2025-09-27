from __future__ import annotations

import builtins

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
