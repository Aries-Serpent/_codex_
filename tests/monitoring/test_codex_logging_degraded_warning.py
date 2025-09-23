"""Ensure degraded telemetry surfaces CLI-visible warnings."""

from __future__ import annotations

import argparse
import importlib

from codex_ml.monitoring import codex_logging as cl


def test_degraded_mode_prints_warning(monkeypatch, capsys):
    module = importlib.reload(cl)
    monkeypatch.setattr(module, "SummaryWriter", None)
    monkeypatch.setattr(module, "wandb", None)
    monkeypatch.setattr(module, "mlflow", None)

    loggers = module._codex_logging_bootstrap(argparse.Namespace(hydra_cfg={}))

    captured = capsys.readouterr().out
    assert "degraded mode" in captured
    assert not loggers.mlflow_active
