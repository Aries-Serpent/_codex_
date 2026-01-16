"""
Test Ita Openapi Exists

Test module for ita openapi exists.
"""

from __future__ import annotations

import pathlib

import pytest

import yaml


def test_ita_openapi_yaml_parses_and_has_paths():
    openapi = pathlib.Path("services/ita/openapi.yaml")
    if not openapi.exists():
        pytest.skip("services/ita/openapi.yaml not present")

    with openapi.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    assert isinstance(data, dict), "OpenAPI file should parse to a mapping"
    assert "paths" in data and isinstance(
        data["paths"], dict
    ), "OpenAPI spec should include 'paths'"
