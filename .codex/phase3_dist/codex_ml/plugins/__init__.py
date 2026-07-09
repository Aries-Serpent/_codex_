"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from plugins.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence

from .base import BasePlugin, MetricsPlugin, ModelPlugin, TokenizerPlugin
from .loader import load_plugins
from .programmatic import PluginRegistry, registry
from .registries import (
    datasets,
    load_dataset_entry_points,
    load_metric_entry_points,
    load_model_entry_points,
    load_reward_model_entry_points,
    load_rl_agent_entry_points,
    load_tokenizer_entry_points,
    load_trainer_entry_points,
    metrics,
    models,
    reward_models,
    rl_agents,
    tokenizers,
    trainers,
)

_ENTRY_POINT_LOADERS: dict[str, tuple[Callable[[bool, str], tuple[int, dict[str, str]]], str]]
_ENTRY_POINT_LOADERS = {
    "tokenizers": (load_tokenizer_entry_points, "codex_ml.tokenizers"),
    "models": (load_model_entry_points, "codex_ml.models"),
    "datasets": (load_dataset_entry_points, "codex_ml.datasets"),
    "metrics": (load_metric_entry_points, "codex_ml.metrics"),
    "trainers": (load_trainer_entry_points, "codex_ml.trainers"),
    "reward_models": (load_reward_model_entry_points, "codex_ml.reward_models"),
    "rl_agents": (load_rl_agent_entry_points, "codex_ml.rl_agents"),
}


def load_entry_point_plugins(
    *,
    enable: bool = False,
    groups: Mapping[str, str] | Sequence[str] | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, int]:
    """Load plugins registered via Python entry points.

    Parameters
    ----------
    enable:
        When ``False`` the function returns a mapping with zero counts without
        performing discovery.
    groups:
        Optional mapping overriding the default entry-point groups for the
        built-in registries. Sequence values are interpreted as registry names
        (e.g. ``["tokenizers", "models"]``) or as raw entry-point groups when
        they do not match a known registry.
    logger:
        Optional logger used to emit warnings when entry points fail to load.
    """

    resolved: dict[str, str] = {}
    if groups is None:
        resolved = {name: default for name, (_, default) in _ENTRY_POINT_LOADERS.items()}
    elif isinstance(groups, Mapping):
        resolved = {str(name): str(group) for name, group in groups.items()}
    else:
        for item in groups:
            key = str(item)
            if key in _ENTRY_POINT_LOADERS:
                resolved[key] = _ENTRY_POINT_LOADERS[key][1]
            else:
                resolved[key] = key

    results: dict[str, int] = {}
    if not enable:
        for name in resolved or _ENTRY_POINT_LOADERS.keys():
            results[name] = 0
        return results

    for name, (loader_fn, default_group) in _ENTRY_POINT_LOADERS.items():
        group_name = resolved.get(name, default_group)
        try:
            loaded, errors = loader_fn(True, group=group_name)  # type: ignore[call-arg]
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - defensive
            if logger is not None:
                logger.debug("Failed to load %s entry-point plugins: %s", name, exc)
            results[name] = 0
            continue
        results[name] = int(loaded)
        if errors and logger is not None:
            for ep_name, message in errors.items():
                logger.warning(
                    "Plugin entry point '%s' (%s) failed to load: %s",
                    ep_name,
                    name,
                    message,
                )

    for name, group_name in resolved.items():
        if name in results:
            continue
        try:
            count = load_plugins(group_name)
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - defensive
            if logger is not None:
                logger.debug("Generic plugin loader failed for %s: %s", name, exc)
            results[name] = 0
            continue
        results[name] = int(count)

    return results


__all__ = [
    "BasePlugin",
    "MetricsPlugin",
    "ModelPlugin",
    "PluginRegistry",
    "TokenizerPlugin",
    "datasets",
    "load_dataset_entry_points",
    "load_entry_point_plugins",
    "load_metric_entry_points",
    "load_model_entry_points",
    "load_plugins",
    "load_reward_model_entry_points",
    "load_rl_agent_entry_points",
    "load_tokenizer_entry_points",
    "load_trainer_entry_points",
    "metrics",
    "models",
    "registry",
    "reward_models",
    "rl_agents",
    "tokenizers",
    "trainers",
]
