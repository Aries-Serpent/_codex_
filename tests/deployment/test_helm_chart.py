"""Validate Helm defaults stay aligned with deployment expectations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VALUES_FILE = PROJECT_ROOT / "deploy" / "helm" / "values.yaml"


def load_values() -> dict[str, Any]:
    data = yaml.safe_load(VALUES_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_values_image_configuration() -> None:
    values = load_values()
    image = values["image"]
    assert image["repository"], "image repository must be configured"
    assert image["tag"], "image tag must be configured"
    assert image["pullPolicy"] in {"IfNotPresent", "Always"}


def test_values_resources_limits_present() -> None:
    values = load_values()
    resources = values["resources"]
    for section in ("limits", "requests"):
        assert section in resources
        cpu = resources[section]["cpu"]
        memory = resources[section]["memory"]
        assert isinstance(cpu, str) and isinstance(memory, str)
