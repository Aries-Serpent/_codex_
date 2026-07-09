"""Configuration loading utilities for _codex_.

This module provides a tiny, explicit API for reading YAML configuration
files from the conf/ tree. It is intentionally simple and does not depend
on Hydra; it is meant as a stepping stone towards a richer config system.

Conventions:
- Base configuration: conf/config.yaml
- Experiment overrides: conf/experiment/<name>.yaml

The base config is loaded first; then if an experiment file exists, it is
deep-merged into the base configuration with experiment values taking
precedence.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

import yaml


def _deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge dict b into dict a, returning a new dict.

    Values in b take precedence over values in a.
    """
    result: dict[str, Any] = deepcopy(a)
    for key, b_val in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(b_val, dict):
            result[key] = _deep_merge(result[key], b_val)
        else:
            result[key] = deepcopy(b_val)
    return result


def load_base_config(repo_root: Optional[Path] = None) -> dict[str, Any]:
    """Load conf/config.yaml from the given repo_root (or the current directory)."""
    root = repo_root or Path(".")
    cfg_path = root / "conf" / "config.yaml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Base config not found at {cfg_path}")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Base config must be a mapping at the top level")
    return data


def load_experiment_config(
    experiment_name: str, repo_root: Optional[Path] = None
) -> dict[str, Any]:
    """Load conf/experiment/<experiment_name>.yaml."""
    root = repo_root or Path(".")
    exp_path = root / "conf" / "experiment" / f"{experiment_name}.yaml"
    if not exp_path.exists():
        raise FileNotFoundError(f"Experiment config not found at {exp_path}")
    data = yaml.safe_load(exp_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("Experiment config must be a mapping at the top level")
    return data


def load_config(
    experiment_name: Optional[str] = None, repo_root: Optional[Path] = None
) -> dict[str, Any]:
    """Load the base config, optionally overlaying an experiment override.

    If experiment_name is None, only conf/config.yaml is used.
    """
    base = load_base_config(repo_root=repo_root)
    if experiment_name is None:
        return base
    exp = load_experiment_config(experiment_name, repo_root=repo_root)
    return _deep_merge(base, exp)
