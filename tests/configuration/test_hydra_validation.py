"""
Test Hydra Validation

Test module for hydra validation.
"""

#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate presence and basic integrity of configuration (Hydra/YAML) assets.
# Offline, deterministic, skips gracefully if configs/ absent.

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

from codex_ml.cli import config as config_cli

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
    assert CONFIGS_DIR.is_dir(), "Condition must be true"


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
    assert any(n.lower().startswith("base") for n in names) or not names, "Condition must be true"
    assert any("experiment" in n.lower() for n in names) or not names, "Condition must be true"


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
    assert applied["trainer"]["batch_size"] == 64, "Condition must be true"
    assert applied["trainer"]["seed"] == 123, "Condition must be true"


@pytest.mark.smoke
def test_configuration_cli_audit_enforces_self_last(capsys):
    cfg_path = CONFIGS_DIR / "default.yaml"
    if not cfg_path.exists():
        pytest.skip("configs/base/default.yaml missing; audit CLI not exercised")

    args = Namespace(path=str(cfg_path), audit="last")
    code = config_cli.cmd_audit(args)
    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert payload["_self_"] is True, "Condition must be true"
    assert payload["ok"] is (not payload["unresolved_refs"]), "Condition must be true"
    assert code in {0, 4}
    expected_code = 0 if not payload["unresolved_refs"] else 4
    assert code == expected_code, "code is not valid"

    defaults_raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")).get("defaults", [])
    normalized: list[str] = []
    for entry in defaults_raw:
        if isinstance(entry, dict):
            normalized.extend(entry.keys())
        else:
            normalized.append(str(entry))

    assert normalized, "defaults list should not be empty"
    assert normalized[-1] == "_self_", "n is not valid"
    assert payload["position"] == len(normalized) - 1, "Normalized must not be empty"


@pytest.mark.smoke
def test_configuration_cli_audit_handles_missing_file(tmp_path, capsys):
    args = Namespace(path=str(tmp_path / "absent.yaml"), audit="last")
    code = config_cli.cmd_audit(args)
    captured = capsys.readouterr()

    assert code == 2, "code is not valid"
    # Error message is logged, not in stderr. Check the JSON output has error indicator.
    output = json.loads(captured.out)
    assert output["ok"] is False, "Condition must be true"
    assert output["unresolved_refs"] is True, "Condition must be true"


@pytest.mark.smoke
def test_configuration_structured_defaults_are_reproducible():
    cfg = config_cli.AppConfig()

    assert cfg.training.seed == 42, "seed is not valid"
    assert cfg.training.deterministic is True, "deterministic is not valid"
    assert cfg.training.log_formats == ("ndjson",)
    assert cfg.logging.wandb_enable is False, "wandb_enable is not valid"
    assert cfg.training.metrics_out.startswith(".codex/"), "Condition must be true"
