#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate presence and basic integrity of configuration (Hydra/YAML) assets.
# Offline, deterministic, skips gracefully if configs/ absent.

from __future__ import annotations

import os
from pathlib import Path

import pytest

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"


def _yaml_files():
    if not CONFIGS_DIR.exists():
        return []
    return sorted([p for p in CONFIGS_DIR.rglob("*.y*ml")])


@pytest.mark.smoke
def test_configuration_configs_dir_present():
    if not CONFIGS_DIR.exists():
        pytest.skip("configs/ directory not present; skipping configuration validation")
    assert CONFIGS_DIR.is_dir()


@pytest.mark.smoke
def test_configuration_yaml_parses():
    files = _yaml_files()
    if not files:
        pytest.skip("No YAML files under configs/; skipping")
    for yml in files:
        with yml.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert isinstance(data, (dict, list))


@pytest.mark.smoke
def test_configuration_has_base_and_experiment_if_present():
    """
    Soft policy: Encourage presence of base and experiment YAMLs.
    """
    if not CONFIGS_DIR.exists():
        pytest.skip("configs/ directory not present")
    names = {p.name for p in _yaml_files()}
    # Non-failing hints; passes if either is present or directory empty
    assert any(n.lower().startswith("base") for n in names) or not names
    assert any("experiment" in n.lower() for n in names) or not names


@pytest.mark.smoke
def test_configuration_env_overrides_example():
    """
    Demonstrate deterministic override pattern using environment variables with YAML.
    This is a local demonstration, not repository-config dependent.
    """
    # minimal demo config
    base_cfg = {"trainer": {"batch_size": 32, "seed": 123}}
    override_env = {"TRAINER_BATCH_SIZE": "64"}

    def apply_env_overrides(cfg: dict, env: dict) -> dict:
        new_cfg = dict(cfg)
        # basic override rule: TRAINER_BATCH_SIZE -> cfg["trainer"]["batch_size"]
        if "TRAINER_BATCH_SIZE" in env:
            bs = int(env["TRAINER_BATCH_SIZE"])
            inner = dict(new_cfg.get("trainer", {}))
            inner["batch_size"] = bs
            new_cfg["trainer"] = inner
        return new_cfg

    applied = apply_env_overrides(base_cfg, override_env)
    assert applied["trainer"]["batch_size"] == 64
    assert applied["trainer"]["seed"] == 123
