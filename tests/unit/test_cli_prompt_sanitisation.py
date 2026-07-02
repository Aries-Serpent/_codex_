"""
pytest.importorskip("mlflow")
Test Cli Prompt Sanitisation

Test module for cli prompt sanitisation.
"""

from __future__ import annotations

import importlib.util
import os

import pytest

pytest.importorskip("hydra")
pytest.importorskip("omegaconf")

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1") # pragma: allowlist secret # pragma: allowlist secret
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
try:  # pragma: no cover - hydra stub may omit utils
    if importlib.util.find_spec("hydra") is None:
        raise ModuleNotFoundError("hydra not found")
except ModuleNotFoundError:
    pytest.skip("Hydra utilities unavailable", allow_module_level=True)

from codex_ml.cli.evaluate import _sanitize_eval_config
from codex_ml.cli.train import _run_from_cfg
from omegaconf import OmegaConf


def _make_base_cfg() -> dict:
    return {
        "epochs": 1,
        "grad_accum": 1,
        "steps_per_epoch": 1,
        "sanitize_prompts": True,
        "dataset": {"train_texts": ["AKIA1234567890123456"]},
        "checkpoint": {},
        "telemetry": {},
        "optimizer": {},
        "reproducibility": {},
        "lora": {},
        "amp": {},
    }


def test_train_cli_sanitises_dataset(monkeypatch):
    calls: dict[str, object] = {}

    def _stub_run_training(**kwargs):
        calls["called"] = True
        return {"status": "ok"}

    monkeypatch.setattr("codex_ml.cli.train.run_training", _stub_run_training)
    cfg = OmegaConf.create(_make_base_cfg())
    _run_from_cfg(cfg)
    assert calls.get("called"), "Condition must be true"
    assert "«REDACTED:SECRET»" in cfg.dataset.train_texts[0], "Data must not be empty"


def test_train_cli_respects_disable_flag(monkeypatch):
    def _stub_run_training(**kwargs):  # pragma: no cover - shared stub
        return {"status": "ok"}

    monkeypatch.setattr("codex_ml.cli.train.run_training", _stub_run_training)
    cfg = OmegaConf.create(_make_base_cfg())
    cfg.sanitize_prompts = False
    original = cfg.dataset.train_texts[0]
    _run_from_cfg(cfg)
    assert cfg.dataset.train_texts[0] == original, "Data must not be empty"


def test_evaluate_cli_sanitises_config():
    cfg_map = {
        "sanitize_prompts": True,
        "dataset": {"texts": ["sk-test-secret-123"]},
        "prompts": ["AKIA0000000000000000"],
    }
    count = _sanitize_eval_config(cfg_map)
    assert count >= 1, "count must be positive"
    assert "«REDACTED:SECRET»" in cfg_map["dataset"]["texts"][0], "Data must not be empty"
    assert "«REDACTED:SECRET»" in cfg_map["prompts"][0], "Condition must be true"


def test_evaluate_cli_disable_flag():
    cfg_map = {
        "sanitize_prompts": False,
        "dataset": {"texts": ["sk-test-secret-123"]},
        "prompts": ["AKIA0000000000000000"],
    }
    count = _sanitize_eval_config(cfg_map)
    assert count == 0, "Count must be greater than zero"
    assert cfg_map["dataset"]["texts"][0] == "sk-test-secret-123", "Data must not be empty"
    assert cfg_map["prompts"][0] == "AKIA0000000000000000", "Condition must be true"
