from __future__ import annotations

import sys
import types
from typing import Dict

import pytest

from codex_ml.training import run_functional_training


def test_training_eval_fallback_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure optional dependencies appear missing so the fallback synthetic path is exercised.
    for mod in ("datasets", "transformers"):
        monkeypatch.delitem(sys.modules, mod, raising=False)
        monkeypatch.setitem(sys.modules, mod, types.ModuleType(mod))
        module = sys.modules[mod]
        # Remove attributes to trigger ImportError from "from module import attr".
        for attr in list(getattr(module, "__dict__", {})):
            if not attr.startswith("__"):
                delattr(module, attr)

    cfg: Dict[str, object] = {
        "seed": 123,
        "max_epochs": 3,
        "dataset": {"train_texts": ["a b c", "d e f"], "format": "inline"},
        "model": {"name": "MiniLM"},
        "learning_rate": 1e-3,
        "batch_size": 2,
        "gradient_accumulation": 1,
        "tensorboard": False,
        "mlflow_enable": False,
        "wandb_enable": False,
        "system_metrics": "off",
    }

    result = run_functional_training(cfg)
    assert isinstance(result, dict)
    metrics = result.get("metrics")
    assert isinstance(metrics, list)
    assert len(metrics) == cfg["max_epochs"]
    first = metrics[0]
    assert isinstance(first, dict)
    assert {"epoch", "tokens", "loss"}.issubset(first.keys())
