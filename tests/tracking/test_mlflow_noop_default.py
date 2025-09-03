from __future__ import annotations

import importlib
import sys
from types import ModuleType


def _install_fake_mlflow() -> None:
    fake = ModuleType("mlflow")

    def log_params(*args, **kwargs):  # pragma: no cover - raises if called
        raise RuntimeError("log_params should not be invoked")

    def log_metrics(*args, **kwargs):  # pragma: no cover - raises if called
        raise RuntimeError("log_metrics should not be invoked")

    fake.log_params = log_params  # type: ignore[attr-defined]
    fake.log_metrics = log_metrics  # type: ignore[attr-defined]
    sys.modules["mlflow"] = fake


def test_log_helpers_noop_with_mlflow_installed():
    sys.modules.pop("mlflow", None)
    sys.modules.pop("codex_ml.tracking.mlflow_utils", None)
    _install_fake_mlflow()
    mfu = importlib.import_module("codex_ml.tracking.mlflow_utils")

    # Should be no-ops when enabled is left as default (None)
    mfu.log_params({"a": 1})
    mfu.log_metrics({"b": 2}, step=0)

    # Cleanup to avoid leaking fake module to other tests
    sys.modules.pop("mlflow", None)
