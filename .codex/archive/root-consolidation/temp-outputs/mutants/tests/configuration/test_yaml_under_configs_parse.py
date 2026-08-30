"""
Test Yaml Under Configs Parse

Test module for yaml under configs parse.
"""

from __future__ import annotations

import pathlib
from collections.abc import Iterable

import pytest
import yaml


def _iter_yaml_files(root: pathlib.Path) -> list[pathlib.Path]:
    if not root.exists():
        return []
    files: Iterable[pathlib.Path] = root.rglob("*")
    yaml_files = [p for p in files if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}]
    yaml_files.sort(key=str)
    return yaml_files


def _load_yaml(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_all_yaml_under_configs_parse():
    root = pathlib.Path("configs")
    yaml_files = _iter_yaml_files(root)
    if not yaml_files:
        pytest.skip("No YAML files found under configs/")

    for yaml_path in yaml_files:
        data = _load_yaml(yaml_path)
        assert data is not None, f"{yaml_path} parsed to None; ensure valid YAML content"


def test_minimal_config_examples_parse_if_present():
    candidates = [
        pathlib.Path("configs/base/hydra.yaml"),
        pathlib.Path("configs/experimental/config_minimal.yaml"),
    ]
    present = [path for path in candidates if path.exists()]
    if not present:
        pytest.skip("No baseline Hydra examples present")

    for config_path in present:
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        assert isinstance(data, (dict, list)), f"{config_path} must parse to dict or list"
