"""Smoke tests for the Helm chart defaults."""

from __future__ import annotations

from pathlib import Path

import yaml

VALUES_PATH = Path(__file__).resolve().parents[2] / "deploy" / "helm" / "values.yaml"


def _load_spec() -> dict:
    data = yaml.safe_load(VALUES_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    spec = data.get("spec", {})
    assert isinstance(spec, dict)
    return spec


def test_image_pull_policy_prefers_cache() -> None:
    spec = _load_spec()
    image = spec.get("image", {})
    assert image.get("pullPolicy") == "IfNotPresent", "Condition must be true"


def test_offline_environment_defaults() -> None:
    spec = _load_spec()
    env = {item["name"]: item.get("value") for item in spec.get("env", [])}
    assert env.get("WANDB_MODE") == "offline", "Condition must be true"
    assert env.get("HF_HUB_OFFLINE") == "1", "Condition must be true"
    assert env.get("LOG_LEVEL") == "INFO", "Condition must be true"
