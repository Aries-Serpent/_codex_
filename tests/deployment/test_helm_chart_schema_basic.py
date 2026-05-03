"""
Test Helm Chart Schema Basic

Test module for helm chart schema basic.
"""

from __future__ import annotations

import pathlib
from typing import Any

import pytest
import yaml


def _safe_load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict), f"{path} should parse to a mapping"
    return data


def test_chart_yaml_has_minimal_fields():
    chart = pathlib.Path("deploy/helm/Chart.yaml")
    if not chart.exists():
        pytest.skip("deploy/helm/Chart.yaml not present")
    data = _safe_load_yaml(chart)
    for key in ("apiVersion", "name", "version"):
        assert data.get(key), f"Chart.yaml missing required key: {key}"


def test_values_yaml_is_mapping_and_stable_types():
    values = pathlib.Path("deploy/helm/values.yaml")
    if not values.exists():
        pytest.skip("deploy/helm/values.yaml not present")
    data = _safe_load_yaml(values)
    assert isinstance(data, dict), "values.yaml must be a mapping"

    for key in sorted(list(data.keys()))[:25]:
        value = data[key]
        assert not (
            isinstance(value, str) and "\t" in value
        ), f"Tab character found in value for {key}"
