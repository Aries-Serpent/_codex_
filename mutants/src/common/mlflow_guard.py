"""
Mlflow Guard Module

This module provides functionality for mlflow guard.

Usage:
    from common.mlflow_guard import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import contextlib
import hashlib
import json
import os
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import mlflow
except Exception:  # pragma: no cover - mlflow not installed or misconfigured
    mlflow = None  # type: ignore

from omegaconf import DictConfig, OmegaConf

from .provenance import _read_dvc_lock, collect_dvc_stage
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__config_fingerprint__mutmut_orig(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_1(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = None
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_2(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(None, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_3(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=None)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_4(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_5(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, )
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_6(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_7(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = None
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_8(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(None, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_9(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=None, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_10(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=None)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_11(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_12(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_13(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, )
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_14(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=True, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_15(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=False)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_16(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = None
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_17(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(None, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_18(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=None)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_19(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_20(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, )
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_21(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_22(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = None
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_23(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(None, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_24(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=None, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_25(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=None)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_26(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_27(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_28(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, )
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_29(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=True, sort_keys=True)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_30(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=False)
    return hashlib.sha256(yml.encode("utf-8")).hexdigest()


def x__config_fingerprint__mutmut_31(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(None).hexdigest()


def x__config_fingerprint__mutmut_32(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode(None)).hexdigest()


def x__config_fingerprint__mutmut_33(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("XXutf-8XX")).hexdigest()


def x__config_fingerprint__mutmut_34(cfg: DictConfig) -> str:
    """Stable SHA256 of resolved config YAML (aligned with provenance)."""
    import yaml
    try:
        # OmegaConf.to_yaml doesn't exist in older versions, use to_container
        container = OmegaConf.to_container(cfg, resolve=True)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    except Exception:
        # Fallback to unresolved config
        container = OmegaConf.to_container(cfg, resolve=False)
        yml = yaml.dump(container, default_flow_style=False, sort_keys=True)
    return hashlib.sha256(yml.encode("UTF-8")).hexdigest()

x__config_fingerprint__mutmut_mutants : ClassVar[MutantDict] = {
'x__config_fingerprint__mutmut_1': x__config_fingerprint__mutmut_1, 
    'x__config_fingerprint__mutmut_2': x__config_fingerprint__mutmut_2, 
    'x__config_fingerprint__mutmut_3': x__config_fingerprint__mutmut_3, 
    'x__config_fingerprint__mutmut_4': x__config_fingerprint__mutmut_4, 
    'x__config_fingerprint__mutmut_5': x__config_fingerprint__mutmut_5, 
    'x__config_fingerprint__mutmut_6': x__config_fingerprint__mutmut_6, 
    'x__config_fingerprint__mutmut_7': x__config_fingerprint__mutmut_7, 
    'x__config_fingerprint__mutmut_8': x__config_fingerprint__mutmut_8, 
    'x__config_fingerprint__mutmut_9': x__config_fingerprint__mutmut_9, 
    'x__config_fingerprint__mutmut_10': x__config_fingerprint__mutmut_10, 
    'x__config_fingerprint__mutmut_11': x__config_fingerprint__mutmut_11, 
    'x__config_fingerprint__mutmut_12': x__config_fingerprint__mutmut_12, 
    'x__config_fingerprint__mutmut_13': x__config_fingerprint__mutmut_13, 
    'x__config_fingerprint__mutmut_14': x__config_fingerprint__mutmut_14, 
    'x__config_fingerprint__mutmut_15': x__config_fingerprint__mutmut_15, 
    'x__config_fingerprint__mutmut_16': x__config_fingerprint__mutmut_16, 
    'x__config_fingerprint__mutmut_17': x__config_fingerprint__mutmut_17, 
    'x__config_fingerprint__mutmut_18': x__config_fingerprint__mutmut_18, 
    'x__config_fingerprint__mutmut_19': x__config_fingerprint__mutmut_19, 
    'x__config_fingerprint__mutmut_20': x__config_fingerprint__mutmut_20, 
    'x__config_fingerprint__mutmut_21': x__config_fingerprint__mutmut_21, 
    'x__config_fingerprint__mutmut_22': x__config_fingerprint__mutmut_22, 
    'x__config_fingerprint__mutmut_23': x__config_fingerprint__mutmut_23, 
    'x__config_fingerprint__mutmut_24': x__config_fingerprint__mutmut_24, 
    'x__config_fingerprint__mutmut_25': x__config_fingerprint__mutmut_25, 
    'x__config_fingerprint__mutmut_26': x__config_fingerprint__mutmut_26, 
    'x__config_fingerprint__mutmut_27': x__config_fingerprint__mutmut_27, 
    'x__config_fingerprint__mutmut_28': x__config_fingerprint__mutmut_28, 
    'x__config_fingerprint__mutmut_29': x__config_fingerprint__mutmut_29, 
    'x__config_fingerprint__mutmut_30': x__config_fingerprint__mutmut_30, 
    'x__config_fingerprint__mutmut_31': x__config_fingerprint__mutmut_31, 
    'x__config_fingerprint__mutmut_32': x__config_fingerprint__mutmut_32, 
    'x__config_fingerprint__mutmut_33': x__config_fingerprint__mutmut_33, 
    'x__config_fingerprint__mutmut_34': x__config_fingerprint__mutmut_34
}

def _config_fingerprint(*args, **kwargs):
    result = _mutmut_trampoline(x__config_fingerprint__mutmut_orig, x__config_fingerprint__mutmut_mutants, args, kwargs)
    return result 

_config_fingerprint.__signature__ = _mutmut_signature(x__config_fingerprint__mutmut_orig)
x__config_fingerprint__mutmut_orig.__name__ = 'x__config_fingerprint'


def x__dataset_hash_from_dvc__mutmut_orig(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_1(
    lock_path: Path = Path("dvc.lock"), stage: str = "XXprepareXX"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_2(
    lock_path: Path = Path("dvc.lock"), stage: str = "PREPARE"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_3(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = None
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_4(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(None)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_5(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_6(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(None, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_7(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=None) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_8(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_9(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, ) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_10(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_11(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs and {}).items():  # type: ignore[attr-defined]
        h = meta.get("md5")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_12(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = None
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_13(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get(None)
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_14(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("XXmd5XX")
        if h:
            return h
    return None


def x__dataset_hash_from_dvc__mutmut_15(
    lock_path: Path = Path("dvc.lock"), stage: str = "prepare"
) -> str | None:
    lock = _read_dvc_lock(lock_path)
    st = collect_dvc_stage(lock, stage=stage) if lock else None
    if not st:
        return None
    for _, meta in (st.outs or {}).items():  # type: ignore[attr-defined]
        h = meta.get("MD5")
        if h:
            return h
    return None

x__dataset_hash_from_dvc__mutmut_mutants : ClassVar[MutantDict] = {
'x__dataset_hash_from_dvc__mutmut_1': x__dataset_hash_from_dvc__mutmut_1, 
    'x__dataset_hash_from_dvc__mutmut_2': x__dataset_hash_from_dvc__mutmut_2, 
    'x__dataset_hash_from_dvc__mutmut_3': x__dataset_hash_from_dvc__mutmut_3, 
    'x__dataset_hash_from_dvc__mutmut_4': x__dataset_hash_from_dvc__mutmut_4, 
    'x__dataset_hash_from_dvc__mutmut_5': x__dataset_hash_from_dvc__mutmut_5, 
    'x__dataset_hash_from_dvc__mutmut_6': x__dataset_hash_from_dvc__mutmut_6, 
    'x__dataset_hash_from_dvc__mutmut_7': x__dataset_hash_from_dvc__mutmut_7, 
    'x__dataset_hash_from_dvc__mutmut_8': x__dataset_hash_from_dvc__mutmut_8, 
    'x__dataset_hash_from_dvc__mutmut_9': x__dataset_hash_from_dvc__mutmut_9, 
    'x__dataset_hash_from_dvc__mutmut_10': x__dataset_hash_from_dvc__mutmut_10, 
    'x__dataset_hash_from_dvc__mutmut_11': x__dataset_hash_from_dvc__mutmut_11, 
    'x__dataset_hash_from_dvc__mutmut_12': x__dataset_hash_from_dvc__mutmut_12, 
    'x__dataset_hash_from_dvc__mutmut_13': x__dataset_hash_from_dvc__mutmut_13, 
    'x__dataset_hash_from_dvc__mutmut_14': x__dataset_hash_from_dvc__mutmut_14, 
    'x__dataset_hash_from_dvc__mutmut_15': x__dataset_hash_from_dvc__mutmut_15
}

def _dataset_hash_from_dvc(*args, **kwargs):
    result = _mutmut_trampoline(x__dataset_hash_from_dvc__mutmut_orig, x__dataset_hash_from_dvc__mutmut_mutants, args, kwargs)
    return result 

_dataset_hash_from_dvc.__signature__ = _mutmut_signature(x__dataset_hash_from_dvc__mutmut_orig)
x__dataset_hash_from_dvc__mutmut_orig.__name__ = 'x__dataset_hash_from_dvc'


def x_ensure_local_tracking__mutmut_orig(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_1(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is not None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_2(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = None
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_3(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = True
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_4(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_5(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = None
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_6(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(None, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_7(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, None, None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_8(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr("monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_9(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_10(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", )
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_11(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "XXmonitorXX", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_12(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "MONITOR", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_13(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_14(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(None, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_15(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, None, None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_16(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr("tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_17(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_18(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", ) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_19(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "XXtrackingXX", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_20(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "TRACKING", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_21(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_22(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_23(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = None

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_24(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(None)

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_25(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(None, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_26(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, None, False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_27(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", None))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_28(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr("allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_29(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_30(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", ))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_31(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "XXallow_remoteXX", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_32(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "ALLOW_REMOTE", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_33(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", True))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_34(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = None
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_35(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_36(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith(None):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_37(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri and "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_38(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "XXXX").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_39(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("XXfile:XX"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_40(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("FILE:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_41(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri(None)

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_42(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("XXfile:./mlrunsXX")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_43(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("FILE:./MLRUNS")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_44(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(None):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_45(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=None, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_46(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=None)

    return mlflow


def x_ensure_local_tracking__mutmut_47(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_48(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, )

    return mlflow


def x_ensure_local_tracking__mutmut_49(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path(None).mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_50(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("XX./mlrunsXX").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_51(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./MLRUNS").mkdir(parents=True, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_52(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=False, exist_ok=True)

    return mlflow


def x_ensure_local_tracking__mutmut_53(cfg: DictConfig | None = None) -> Any | None:
    """
    Force MLflow file store (./mlruns) unless monitor.tracking.allow_remote is True.
    Returns mlflow module or None if mlflow unavailable.
    """
    if mlflow is None:
        return None

    allow_remote = False
    if cfg is not None:
        monitor = getattr(cfg, "monitor", None)
        tracking = getattr(monitor, "tracking", None) if monitor is not None else None
        if tracking is not None:
            allow_remote = bool(getattr(tracking, "allow_remote", False))

    uri = mlflow.get_tracking_uri()
    if allow_remote:
        return mlflow

    if not (uri or "").startswith("file:"):
        mlflow.set_tracking_uri("file:./mlruns")

    with contextlib.suppress(Exception):  # pragma: no cover - best effort
        Path("./mlruns").mkdir(parents=True, exist_ok=False)

    return mlflow

x_ensure_local_tracking__mutmut_mutants : ClassVar[MutantDict] = {
'x_ensure_local_tracking__mutmut_1': x_ensure_local_tracking__mutmut_1, 
    'x_ensure_local_tracking__mutmut_2': x_ensure_local_tracking__mutmut_2, 
    'x_ensure_local_tracking__mutmut_3': x_ensure_local_tracking__mutmut_3, 
    'x_ensure_local_tracking__mutmut_4': x_ensure_local_tracking__mutmut_4, 
    'x_ensure_local_tracking__mutmut_5': x_ensure_local_tracking__mutmut_5, 
    'x_ensure_local_tracking__mutmut_6': x_ensure_local_tracking__mutmut_6, 
    'x_ensure_local_tracking__mutmut_7': x_ensure_local_tracking__mutmut_7, 
    'x_ensure_local_tracking__mutmut_8': x_ensure_local_tracking__mutmut_8, 
    'x_ensure_local_tracking__mutmut_9': x_ensure_local_tracking__mutmut_9, 
    'x_ensure_local_tracking__mutmut_10': x_ensure_local_tracking__mutmut_10, 
    'x_ensure_local_tracking__mutmut_11': x_ensure_local_tracking__mutmut_11, 
    'x_ensure_local_tracking__mutmut_12': x_ensure_local_tracking__mutmut_12, 
    'x_ensure_local_tracking__mutmut_13': x_ensure_local_tracking__mutmut_13, 
    'x_ensure_local_tracking__mutmut_14': x_ensure_local_tracking__mutmut_14, 
    'x_ensure_local_tracking__mutmut_15': x_ensure_local_tracking__mutmut_15, 
    'x_ensure_local_tracking__mutmut_16': x_ensure_local_tracking__mutmut_16, 
    'x_ensure_local_tracking__mutmut_17': x_ensure_local_tracking__mutmut_17, 
    'x_ensure_local_tracking__mutmut_18': x_ensure_local_tracking__mutmut_18, 
    'x_ensure_local_tracking__mutmut_19': x_ensure_local_tracking__mutmut_19, 
    'x_ensure_local_tracking__mutmut_20': x_ensure_local_tracking__mutmut_20, 
    'x_ensure_local_tracking__mutmut_21': x_ensure_local_tracking__mutmut_21, 
    'x_ensure_local_tracking__mutmut_22': x_ensure_local_tracking__mutmut_22, 
    'x_ensure_local_tracking__mutmut_23': x_ensure_local_tracking__mutmut_23, 
    'x_ensure_local_tracking__mutmut_24': x_ensure_local_tracking__mutmut_24, 
    'x_ensure_local_tracking__mutmut_25': x_ensure_local_tracking__mutmut_25, 
    'x_ensure_local_tracking__mutmut_26': x_ensure_local_tracking__mutmut_26, 
    'x_ensure_local_tracking__mutmut_27': x_ensure_local_tracking__mutmut_27, 
    'x_ensure_local_tracking__mutmut_28': x_ensure_local_tracking__mutmut_28, 
    'x_ensure_local_tracking__mutmut_29': x_ensure_local_tracking__mutmut_29, 
    'x_ensure_local_tracking__mutmut_30': x_ensure_local_tracking__mutmut_30, 
    'x_ensure_local_tracking__mutmut_31': x_ensure_local_tracking__mutmut_31, 
    'x_ensure_local_tracking__mutmut_32': x_ensure_local_tracking__mutmut_32, 
    'x_ensure_local_tracking__mutmut_33': x_ensure_local_tracking__mutmut_33, 
    'x_ensure_local_tracking__mutmut_34': x_ensure_local_tracking__mutmut_34, 
    'x_ensure_local_tracking__mutmut_35': x_ensure_local_tracking__mutmut_35, 
    'x_ensure_local_tracking__mutmut_36': x_ensure_local_tracking__mutmut_36, 
    'x_ensure_local_tracking__mutmut_37': x_ensure_local_tracking__mutmut_37, 
    'x_ensure_local_tracking__mutmut_38': x_ensure_local_tracking__mutmut_38, 
    'x_ensure_local_tracking__mutmut_39': x_ensure_local_tracking__mutmut_39, 
    'x_ensure_local_tracking__mutmut_40': x_ensure_local_tracking__mutmut_40, 
    'x_ensure_local_tracking__mutmut_41': x_ensure_local_tracking__mutmut_41, 
    'x_ensure_local_tracking__mutmut_42': x_ensure_local_tracking__mutmut_42, 
    'x_ensure_local_tracking__mutmut_43': x_ensure_local_tracking__mutmut_43, 
    'x_ensure_local_tracking__mutmut_44': x_ensure_local_tracking__mutmut_44, 
    'x_ensure_local_tracking__mutmut_45': x_ensure_local_tracking__mutmut_45, 
    'x_ensure_local_tracking__mutmut_46': x_ensure_local_tracking__mutmut_46, 
    'x_ensure_local_tracking__mutmut_47': x_ensure_local_tracking__mutmut_47, 
    'x_ensure_local_tracking__mutmut_48': x_ensure_local_tracking__mutmut_48, 
    'x_ensure_local_tracking__mutmut_49': x_ensure_local_tracking__mutmut_49, 
    'x_ensure_local_tracking__mutmut_50': x_ensure_local_tracking__mutmut_50, 
    'x_ensure_local_tracking__mutmut_51': x_ensure_local_tracking__mutmut_51, 
    'x_ensure_local_tracking__mutmut_52': x_ensure_local_tracking__mutmut_52, 
    'x_ensure_local_tracking__mutmut_53': x_ensure_local_tracking__mutmut_53
}

def ensure_local_tracking(*args, **kwargs):
    result = _mutmut_trampoline(x_ensure_local_tracking__mutmut_orig, x_ensure_local_tracking__mutmut_mutants, args, kwargs)
    return result 

ensure_local_tracking.__signature__ = _mutmut_signature(x_ensure_local_tracking__mutmut_orig)
x_ensure_local_tracking__mutmut_orig.__name__ = 'x_ensure_local_tracking'


def x_start_run_with_tags__mutmut_orig(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_1(
    cfg: DictConfig, run_name: str = "XXpipelineXX"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_2(
    cfg: DictConfig, run_name: str = "PIPELINE"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_3(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is not None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_4(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = None
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_5(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(None)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_6(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is not None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_7(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = None

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_8(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "XXcodex.seriesXX": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_9(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "CODEX.SERIES": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_10(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "XXI4_Config_TrackingXX",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_11(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "i4_config_tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_12(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_CONFIG_TRACKING",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_13(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "XXcodex.iterationXX": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_14(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "CODEX.ITERATION": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_15(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "XXP4XX",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_16(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "p4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_17(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "XXgit_commitXX": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_18(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "GIT_COMMIT": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_19(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get(None, ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_20(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", None),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_21(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get(""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_22(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_23(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("XXGIT_COMMITXX", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_24(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("git_commit", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_25(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", "XXXX"),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_26(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "XXconfig_sha256XX": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_27(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "CONFIG_SHA256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_28(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(None),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_29(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "XXenvXX": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_30(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "ENV": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_31(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(None, "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_32(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), None, "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_33(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", None),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_34(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr("name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_35(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_36(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", ),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_37(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(None, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_38(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, None, {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_39(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", None), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_40(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr("env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_41(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_42(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", ), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_43(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "XXenvXX", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_44(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "ENV", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_45(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "XXnameXX", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_46(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "NAME", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_47(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "XXunknownXX"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_48(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "UNKNOWN"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_49(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "XXprojectXX": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_50(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "PROJECT": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_51(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get(None, "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_52(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", None),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_53(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_54(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", ),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_55(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(None, "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_56(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), None, {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_57(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", None).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_58(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr("tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_59(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_60(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", ).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_61(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(None, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_62(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, None, {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_63(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", None), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_64(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr("monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_65(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_66(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", ), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_67(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "XXmonitorXX", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_68(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "MONITOR", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_69(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "XXtagsXX", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_70(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "TAGS", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_71(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("XXprojectXX", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_72(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("PROJECT", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_73(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "XXhhg_logisticsXX"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_74(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "HHG_LOGISTICS"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_75(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = None
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_76(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = None

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_77(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["XXdataset_hashXX"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_78(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["DATASET_HASH"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_79(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment(None)
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_80(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("XXhhg_logisticsXX")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_81(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("HHG_LOGISTICS")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_82(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = None

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_83(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=None)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_84(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(None):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_85(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(None)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_86(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = None
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_87(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("XXmodelXX", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_88(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("MODEL", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_89(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "XXtrainXX", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_90(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "TRAIN", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_91(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "XXpipelineXX", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_92(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "PIPELINE", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_93(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "XXserveXX", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_94(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "SERVE", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_95(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "XXmonitorXX"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_96(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "MONITOR"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_97(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = None
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_98(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(None, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_99(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, None, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_100(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_101(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_102(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, )
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_103(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is not None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_104(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            break
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_105(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = None
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_106(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(None, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_107(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=None)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_108(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_109(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, )
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_110(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=True)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_111(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = None

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_112(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = None
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_113(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) and v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_114(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is not None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_115(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(None):
            ml.log_param(key, value)

    return ctx


def x_start_run_with_tags__mutmut_116(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(None, value)

    return ctx


def x_start_run_with_tags__mutmut_117(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, None)

    return ctx


def x_start_run_with_tags__mutmut_118(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(value)

    return ctx


def x_start_run_with_tags__mutmut_119(
    cfg: DictConfig, run_name: str = "pipeline"
) -> contextlib.AbstractContextManager[Any]:
    """Context manager that starts an MLflow run with Codex tags & params."""
    if mlflow is None:
        return contextlib.nullcontext()

    ml = ensure_local_tracking(cfg)
    if ml is None:
        return contextlib.nullcontext()

    tags: dict[str, Any] = {
        "codex.series": "I4_Config_Tracking",
        "codex.iteration": "P4",
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_sha256": _config_fingerprint(cfg),
        "env": getattr(getattr(cfg, "env", {}), "name", "unknown"),
        "project": getattr(getattr(cfg, "monitor", {}), "tags", {}).get("project", "hhg_logistics"),
    }

    ds_hash = _dataset_hash_from_dvc()
    if ds_hash:
        tags["dataset_hash"] = ds_hash

    ml.set_experiment("hhg_logistics")
    ctx = ml.start_run(run_name=run_name)

    with contextlib.suppress(Exception):
        ml.set_tags(tags)

    params: dict[str, Any] = {}
    for sect in ("model", "train", "pipeline", "serve", "monitor"):
        section = getattr(cfg, sect, None)
        if section is None:
            continue
        container = OmegaConf.to_container(section, resolve=False)
        if isinstance(container, dict):
            for key, value in container.items():
                params[f"{sect}.{key}"] = value

    simple_params = {
        k: v for k, v in params.items() if isinstance(v, str | int | float | bool) or v is None
    }
    for key, value in simple_params.items():
        with contextlib.suppress(Exception):
            ml.log_param(key, )

    return ctx

x_start_run_with_tags__mutmut_mutants : ClassVar[MutantDict] = {
'x_start_run_with_tags__mutmut_1': x_start_run_with_tags__mutmut_1, 
    'x_start_run_with_tags__mutmut_2': x_start_run_with_tags__mutmut_2, 
    'x_start_run_with_tags__mutmut_3': x_start_run_with_tags__mutmut_3, 
    'x_start_run_with_tags__mutmut_4': x_start_run_with_tags__mutmut_4, 
    'x_start_run_with_tags__mutmut_5': x_start_run_with_tags__mutmut_5, 
    'x_start_run_with_tags__mutmut_6': x_start_run_with_tags__mutmut_6, 
    'x_start_run_with_tags__mutmut_7': x_start_run_with_tags__mutmut_7, 
    'x_start_run_with_tags__mutmut_8': x_start_run_with_tags__mutmut_8, 
    'x_start_run_with_tags__mutmut_9': x_start_run_with_tags__mutmut_9, 
    'x_start_run_with_tags__mutmut_10': x_start_run_with_tags__mutmut_10, 
    'x_start_run_with_tags__mutmut_11': x_start_run_with_tags__mutmut_11, 
    'x_start_run_with_tags__mutmut_12': x_start_run_with_tags__mutmut_12, 
    'x_start_run_with_tags__mutmut_13': x_start_run_with_tags__mutmut_13, 
    'x_start_run_with_tags__mutmut_14': x_start_run_with_tags__mutmut_14, 
    'x_start_run_with_tags__mutmut_15': x_start_run_with_tags__mutmut_15, 
    'x_start_run_with_tags__mutmut_16': x_start_run_with_tags__mutmut_16, 
    'x_start_run_with_tags__mutmut_17': x_start_run_with_tags__mutmut_17, 
    'x_start_run_with_tags__mutmut_18': x_start_run_with_tags__mutmut_18, 
    'x_start_run_with_tags__mutmut_19': x_start_run_with_tags__mutmut_19, 
    'x_start_run_with_tags__mutmut_20': x_start_run_with_tags__mutmut_20, 
    'x_start_run_with_tags__mutmut_21': x_start_run_with_tags__mutmut_21, 
    'x_start_run_with_tags__mutmut_22': x_start_run_with_tags__mutmut_22, 
    'x_start_run_with_tags__mutmut_23': x_start_run_with_tags__mutmut_23, 
    'x_start_run_with_tags__mutmut_24': x_start_run_with_tags__mutmut_24, 
    'x_start_run_with_tags__mutmut_25': x_start_run_with_tags__mutmut_25, 
    'x_start_run_with_tags__mutmut_26': x_start_run_with_tags__mutmut_26, 
    'x_start_run_with_tags__mutmut_27': x_start_run_with_tags__mutmut_27, 
    'x_start_run_with_tags__mutmut_28': x_start_run_with_tags__mutmut_28, 
    'x_start_run_with_tags__mutmut_29': x_start_run_with_tags__mutmut_29, 
    'x_start_run_with_tags__mutmut_30': x_start_run_with_tags__mutmut_30, 
    'x_start_run_with_tags__mutmut_31': x_start_run_with_tags__mutmut_31, 
    'x_start_run_with_tags__mutmut_32': x_start_run_with_tags__mutmut_32, 
    'x_start_run_with_tags__mutmut_33': x_start_run_with_tags__mutmut_33, 
    'x_start_run_with_tags__mutmut_34': x_start_run_with_tags__mutmut_34, 
    'x_start_run_with_tags__mutmut_35': x_start_run_with_tags__mutmut_35, 
    'x_start_run_with_tags__mutmut_36': x_start_run_with_tags__mutmut_36, 
    'x_start_run_with_tags__mutmut_37': x_start_run_with_tags__mutmut_37, 
    'x_start_run_with_tags__mutmut_38': x_start_run_with_tags__mutmut_38, 
    'x_start_run_with_tags__mutmut_39': x_start_run_with_tags__mutmut_39, 
    'x_start_run_with_tags__mutmut_40': x_start_run_with_tags__mutmut_40, 
    'x_start_run_with_tags__mutmut_41': x_start_run_with_tags__mutmut_41, 
    'x_start_run_with_tags__mutmut_42': x_start_run_with_tags__mutmut_42, 
    'x_start_run_with_tags__mutmut_43': x_start_run_with_tags__mutmut_43, 
    'x_start_run_with_tags__mutmut_44': x_start_run_with_tags__mutmut_44, 
    'x_start_run_with_tags__mutmut_45': x_start_run_with_tags__mutmut_45, 
    'x_start_run_with_tags__mutmut_46': x_start_run_with_tags__mutmut_46, 
    'x_start_run_with_tags__mutmut_47': x_start_run_with_tags__mutmut_47, 
    'x_start_run_with_tags__mutmut_48': x_start_run_with_tags__mutmut_48, 
    'x_start_run_with_tags__mutmut_49': x_start_run_with_tags__mutmut_49, 
    'x_start_run_with_tags__mutmut_50': x_start_run_with_tags__mutmut_50, 
    'x_start_run_with_tags__mutmut_51': x_start_run_with_tags__mutmut_51, 
    'x_start_run_with_tags__mutmut_52': x_start_run_with_tags__mutmut_52, 
    'x_start_run_with_tags__mutmut_53': x_start_run_with_tags__mutmut_53, 
    'x_start_run_with_tags__mutmut_54': x_start_run_with_tags__mutmut_54, 
    'x_start_run_with_tags__mutmut_55': x_start_run_with_tags__mutmut_55, 
    'x_start_run_with_tags__mutmut_56': x_start_run_with_tags__mutmut_56, 
    'x_start_run_with_tags__mutmut_57': x_start_run_with_tags__mutmut_57, 
    'x_start_run_with_tags__mutmut_58': x_start_run_with_tags__mutmut_58, 
    'x_start_run_with_tags__mutmut_59': x_start_run_with_tags__mutmut_59, 
    'x_start_run_with_tags__mutmut_60': x_start_run_with_tags__mutmut_60, 
    'x_start_run_with_tags__mutmut_61': x_start_run_with_tags__mutmut_61, 
    'x_start_run_with_tags__mutmut_62': x_start_run_with_tags__mutmut_62, 
    'x_start_run_with_tags__mutmut_63': x_start_run_with_tags__mutmut_63, 
    'x_start_run_with_tags__mutmut_64': x_start_run_with_tags__mutmut_64, 
    'x_start_run_with_tags__mutmut_65': x_start_run_with_tags__mutmut_65, 
    'x_start_run_with_tags__mutmut_66': x_start_run_with_tags__mutmut_66, 
    'x_start_run_with_tags__mutmut_67': x_start_run_with_tags__mutmut_67, 
    'x_start_run_with_tags__mutmut_68': x_start_run_with_tags__mutmut_68, 
    'x_start_run_with_tags__mutmut_69': x_start_run_with_tags__mutmut_69, 
    'x_start_run_with_tags__mutmut_70': x_start_run_with_tags__mutmut_70, 
    'x_start_run_with_tags__mutmut_71': x_start_run_with_tags__mutmut_71, 
    'x_start_run_with_tags__mutmut_72': x_start_run_with_tags__mutmut_72, 
    'x_start_run_with_tags__mutmut_73': x_start_run_with_tags__mutmut_73, 
    'x_start_run_with_tags__mutmut_74': x_start_run_with_tags__mutmut_74, 
    'x_start_run_with_tags__mutmut_75': x_start_run_with_tags__mutmut_75, 
    'x_start_run_with_tags__mutmut_76': x_start_run_with_tags__mutmut_76, 
    'x_start_run_with_tags__mutmut_77': x_start_run_with_tags__mutmut_77, 
    'x_start_run_with_tags__mutmut_78': x_start_run_with_tags__mutmut_78, 
    'x_start_run_with_tags__mutmut_79': x_start_run_with_tags__mutmut_79, 
    'x_start_run_with_tags__mutmut_80': x_start_run_with_tags__mutmut_80, 
    'x_start_run_with_tags__mutmut_81': x_start_run_with_tags__mutmut_81, 
    'x_start_run_with_tags__mutmut_82': x_start_run_with_tags__mutmut_82, 
    'x_start_run_with_tags__mutmut_83': x_start_run_with_tags__mutmut_83, 
    'x_start_run_with_tags__mutmut_84': x_start_run_with_tags__mutmut_84, 
    'x_start_run_with_tags__mutmut_85': x_start_run_with_tags__mutmut_85, 
    'x_start_run_with_tags__mutmut_86': x_start_run_with_tags__mutmut_86, 
    'x_start_run_with_tags__mutmut_87': x_start_run_with_tags__mutmut_87, 
    'x_start_run_with_tags__mutmut_88': x_start_run_with_tags__mutmut_88, 
    'x_start_run_with_tags__mutmut_89': x_start_run_with_tags__mutmut_89, 
    'x_start_run_with_tags__mutmut_90': x_start_run_with_tags__mutmut_90, 
    'x_start_run_with_tags__mutmut_91': x_start_run_with_tags__mutmut_91, 
    'x_start_run_with_tags__mutmut_92': x_start_run_with_tags__mutmut_92, 
    'x_start_run_with_tags__mutmut_93': x_start_run_with_tags__mutmut_93, 
    'x_start_run_with_tags__mutmut_94': x_start_run_with_tags__mutmut_94, 
    'x_start_run_with_tags__mutmut_95': x_start_run_with_tags__mutmut_95, 
    'x_start_run_with_tags__mutmut_96': x_start_run_with_tags__mutmut_96, 
    'x_start_run_with_tags__mutmut_97': x_start_run_with_tags__mutmut_97, 
    'x_start_run_with_tags__mutmut_98': x_start_run_with_tags__mutmut_98, 
    'x_start_run_with_tags__mutmut_99': x_start_run_with_tags__mutmut_99, 
    'x_start_run_with_tags__mutmut_100': x_start_run_with_tags__mutmut_100, 
    'x_start_run_with_tags__mutmut_101': x_start_run_with_tags__mutmut_101, 
    'x_start_run_with_tags__mutmut_102': x_start_run_with_tags__mutmut_102, 
    'x_start_run_with_tags__mutmut_103': x_start_run_with_tags__mutmut_103, 
    'x_start_run_with_tags__mutmut_104': x_start_run_with_tags__mutmut_104, 
    'x_start_run_with_tags__mutmut_105': x_start_run_with_tags__mutmut_105, 
    'x_start_run_with_tags__mutmut_106': x_start_run_with_tags__mutmut_106, 
    'x_start_run_with_tags__mutmut_107': x_start_run_with_tags__mutmut_107, 
    'x_start_run_with_tags__mutmut_108': x_start_run_with_tags__mutmut_108, 
    'x_start_run_with_tags__mutmut_109': x_start_run_with_tags__mutmut_109, 
    'x_start_run_with_tags__mutmut_110': x_start_run_with_tags__mutmut_110, 
    'x_start_run_with_tags__mutmut_111': x_start_run_with_tags__mutmut_111, 
    'x_start_run_with_tags__mutmut_112': x_start_run_with_tags__mutmut_112, 
    'x_start_run_with_tags__mutmut_113': x_start_run_with_tags__mutmut_113, 
    'x_start_run_with_tags__mutmut_114': x_start_run_with_tags__mutmut_114, 
    'x_start_run_with_tags__mutmut_115': x_start_run_with_tags__mutmut_115, 
    'x_start_run_with_tags__mutmut_116': x_start_run_with_tags__mutmut_116, 
    'x_start_run_with_tags__mutmut_117': x_start_run_with_tags__mutmut_117, 
    'x_start_run_with_tags__mutmut_118': x_start_run_with_tags__mutmut_118, 
    'x_start_run_with_tags__mutmut_119': x_start_run_with_tags__mutmut_119
}

def start_run_with_tags(*args, **kwargs):
    result = _mutmut_trampoline(x_start_run_with_tags__mutmut_orig, x_start_run_with_tags__mutmut_mutants, args, kwargs)
    return result 

start_run_with_tags.__signature__ = _mutmut_signature(x_start_run_with_tags__mutmut_orig)
x_start_run_with_tags__mutmut_orig.__name__ = 'x_start_run_with_tags'


def x_log_artifacts_safe__mutmut_orig(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(path), artifact_path=name)


def x_log_artifacts_safe__mutmut_1(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is not None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(path), artifact_path=name)


def x_log_artifacts_safe__mutmut_2(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(None):
            if path.is_file():
                mlflow.log_artifact(str(path), artifact_path=name)


def x_log_artifacts_safe__mutmut_3(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(None, artifact_path=name)


def x_log_artifacts_safe__mutmut_4(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(path), artifact_path=None)


def x_log_artifacts_safe__mutmut_5(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(artifact_path=name)


def x_log_artifacts_safe__mutmut_6(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(path), )


def x_log_artifacts_safe__mutmut_7(paths: dict[str, Path]) -> None:
    """Log small artifacts if MLflow available; ignore failures silently."""
    if mlflow is None:
        return

    for name, path in paths.items():
        with contextlib.suppress(Exception):
            if path.is_file():
                mlflow.log_artifact(str(None), artifact_path=name)

x_log_artifacts_safe__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_artifacts_safe__mutmut_1': x_log_artifacts_safe__mutmut_1, 
    'x_log_artifacts_safe__mutmut_2': x_log_artifacts_safe__mutmut_2, 
    'x_log_artifacts_safe__mutmut_3': x_log_artifacts_safe__mutmut_3, 
    'x_log_artifacts_safe__mutmut_4': x_log_artifacts_safe__mutmut_4, 
    'x_log_artifacts_safe__mutmut_5': x_log_artifacts_safe__mutmut_5, 
    'x_log_artifacts_safe__mutmut_6': x_log_artifacts_safe__mutmut_6, 
    'x_log_artifacts_safe__mutmut_7': x_log_artifacts_safe__mutmut_7
}

def log_artifacts_safe(*args, **kwargs):
    result = _mutmut_trampoline(x_log_artifacts_safe__mutmut_orig, x_log_artifacts_safe__mutmut_mutants, args, kwargs)
    return result 

log_artifacts_safe.__signature__ = _mutmut_signature(x_log_artifacts_safe__mutmut_orig)
x_log_artifacts_safe__mutmut_orig.__name__ = 'x_log_artifacts_safe'


def x_log_dict_safe__mutmut_orig(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_1(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = None
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_2(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(None)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_3(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = None

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_4(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_5(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(None):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_6(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(None, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_7(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, None)
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_8(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_9(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, )
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_10(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(None))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_11(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=None, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_12(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=None)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_13(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_14(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, )
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_15(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=False, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_16(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=False)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_17(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open(None, encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_18(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding=None) as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_19(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open(encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_20(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", ) as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_21(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("XXwXX", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_22(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("W", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_23(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="XXutf-8XX") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_24(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="UTF-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_25(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(None, handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_26(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, None, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_27(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=None, sort_keys=True)


def x_log_dict_safe__mutmut_28(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=None)


def x_log_dict_safe__mutmut_29(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(handle, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_30(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, indent=2, sort_keys=True)


def x_log_dict_safe__mutmut_31(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, sort_keys=True)


def x_log_dict_safe__mutmut_32(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, )


def x_log_dict_safe__mutmut_33(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=3, sort_keys=True)


def x_log_dict_safe__mutmut_34(payload: Any, artifact_path: str | Path) -> None:
    """Log dictionaries via MLflow if available; fallback to local JSON."""

    target = Path(artifact_path)
    data = payload

    if mlflow is not None:
        with contextlib.suppress(Exception):
            mlflow.log_dict(data, str(target))
            return

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=False)

x_log_dict_safe__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_dict_safe__mutmut_1': x_log_dict_safe__mutmut_1, 
    'x_log_dict_safe__mutmut_2': x_log_dict_safe__mutmut_2, 
    'x_log_dict_safe__mutmut_3': x_log_dict_safe__mutmut_3, 
    'x_log_dict_safe__mutmut_4': x_log_dict_safe__mutmut_4, 
    'x_log_dict_safe__mutmut_5': x_log_dict_safe__mutmut_5, 
    'x_log_dict_safe__mutmut_6': x_log_dict_safe__mutmut_6, 
    'x_log_dict_safe__mutmut_7': x_log_dict_safe__mutmut_7, 
    'x_log_dict_safe__mutmut_8': x_log_dict_safe__mutmut_8, 
    'x_log_dict_safe__mutmut_9': x_log_dict_safe__mutmut_9, 
    'x_log_dict_safe__mutmut_10': x_log_dict_safe__mutmut_10, 
    'x_log_dict_safe__mutmut_11': x_log_dict_safe__mutmut_11, 
    'x_log_dict_safe__mutmut_12': x_log_dict_safe__mutmut_12, 
    'x_log_dict_safe__mutmut_13': x_log_dict_safe__mutmut_13, 
    'x_log_dict_safe__mutmut_14': x_log_dict_safe__mutmut_14, 
    'x_log_dict_safe__mutmut_15': x_log_dict_safe__mutmut_15, 
    'x_log_dict_safe__mutmut_16': x_log_dict_safe__mutmut_16, 
    'x_log_dict_safe__mutmut_17': x_log_dict_safe__mutmut_17, 
    'x_log_dict_safe__mutmut_18': x_log_dict_safe__mutmut_18, 
    'x_log_dict_safe__mutmut_19': x_log_dict_safe__mutmut_19, 
    'x_log_dict_safe__mutmut_20': x_log_dict_safe__mutmut_20, 
    'x_log_dict_safe__mutmut_21': x_log_dict_safe__mutmut_21, 
    'x_log_dict_safe__mutmut_22': x_log_dict_safe__mutmut_22, 
    'x_log_dict_safe__mutmut_23': x_log_dict_safe__mutmut_23, 
    'x_log_dict_safe__mutmut_24': x_log_dict_safe__mutmut_24, 
    'x_log_dict_safe__mutmut_25': x_log_dict_safe__mutmut_25, 
    'x_log_dict_safe__mutmut_26': x_log_dict_safe__mutmut_26, 
    'x_log_dict_safe__mutmut_27': x_log_dict_safe__mutmut_27, 
    'x_log_dict_safe__mutmut_28': x_log_dict_safe__mutmut_28, 
    'x_log_dict_safe__mutmut_29': x_log_dict_safe__mutmut_29, 
    'x_log_dict_safe__mutmut_30': x_log_dict_safe__mutmut_30, 
    'x_log_dict_safe__mutmut_31': x_log_dict_safe__mutmut_31, 
    'x_log_dict_safe__mutmut_32': x_log_dict_safe__mutmut_32, 
    'x_log_dict_safe__mutmut_33': x_log_dict_safe__mutmut_33, 
    'x_log_dict_safe__mutmut_34': x_log_dict_safe__mutmut_34
}

def log_dict_safe(*args, **kwargs):
    result = _mutmut_trampoline(x_log_dict_safe__mutmut_orig, x_log_dict_safe__mutmut_mutants, args, kwargs)
    return result 

log_dict_safe.__signature__ = _mutmut_signature(x_log_dict_safe__mutmut_orig)
x_log_dict_safe__mutmut_orig.__name__ = 'x_log_dict_safe'
