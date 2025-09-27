from __future__ import annotations

import builtins
import importlib
import sys


def test_tb_writer_noop_when_tensorboard_missing(monkeypatch, tmp_path):
    module_name = "codex_ml.monitoring.tb_writer"
    sys.modules.pop(module_name, None)

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "torch.utils.tensorboard":
            raise ImportError("tensorboard unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    module = importlib.import_module(module_name)
    writer = module.TBWriter(enabled=True, logdir=str(tmp_path))
    writer.add_scalar("test/value", 1.0, 1)
    writer.close()

    assert getattr(writer, "enabled", False) is False
