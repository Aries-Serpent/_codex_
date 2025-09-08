"""Simple registry for pluggable components.

This registry allows registering tokenizers, reward models and RL agents under
string keys. Interfaces are loaded on demand via entry-points or config.
"""
from __future__ import annotations

import json
import os
import warnings
from importlib import import_module
from typing import Any, Callable, Dict

import yaml

_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        if name in _REGISTRY:
            warnings.warn(f"duplicate registration: {name}", stacklevel=2)
        _REGISTRY[name] = fn
        return fn

    return deco


def get(name: str, *, fallback: str | None = None) -> Any:
    if name in _REGISTRY:
        return _REGISTRY[name]
    if fallback:
        module, attr = fallback.split(":")
        return getattr(import_module(module), attr)
    raise KeyError(f"No registered component named {name}")


def load_component(path: str) -> Any:
    """Load a component from ``module:Class`` notation."""

    if ":" not in path:
        raise ValueError(f"invalid component path: {path}")
    module_name, class_name = path.split(":", 1)
    module = import_module(module_name)
    return getattr(module, class_name)


def get_component(cfg_key: str, default_path: str) -> Any:
    """Instantiate component using env var ``cfg_key`` or ``default_path``."""

    path = os.environ.get(cfg_key, default_path)
    cls = load_component(path)
    return cls()


def apply_config(config_path: str) -> None:
    """Load interface definitions from ``config_path`` and export env vars.

    The configuration file should map interface names (``tokenizer``,
    ``reward_model``, ``rl_agent``) to either a ``module:Class`` string or a
    mapping containing ``path`` and optional ``kwargs``. Loaded values are
    exported via ``CODEX_*`` environment variables to mirror manual
    configuration.
    """

    if not os.path.exists(config_path):
        return
    with open(config_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    mapping = {
        "tokenizer": ("CODEX_TOKENIZER_PATH", "CODEX_TOKENIZER_KWARGS"),
        "reward_model": ("CODEX_REWARD_PATH", "CODEX_REWARD_KWARGS"),
        "rl_agent": ("CODEX_RL_PATH", "CODEX_RL_KWARGS"),
    }

    for key, (path_env, kw_env) in mapping.items():
        if key not in cfg:
            continue
        entry = cfg[key]
        if isinstance(entry, str):
            os.environ.setdefault(path_env, entry)
        else:
            path = entry.get("path")
            kwargs = entry.get("kwargs")
            if path:
                os.environ.setdefault(path_env, path)
            if kwargs:
                os.environ.setdefault(kw_env, json.dumps(kwargs))
