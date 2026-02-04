"""
Provenance Module

This module provides functionality for provenance.

Usage:
    from common.provenance import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from omegaconf import DictConfig, OmegaConf

    def _to_container(cfg: DictConfig) -> dict[str, Any]:
        return OmegaConf.to_container(cfg, resolve=True)  # type: ignore[arg-type]

except ImportError:  # pragma: no cover - fallback for optional dependency
    DictConfig = dict  # type: ignore[misc, assignment]

    def _to_container(cfg: DictConfig) -> dict[str, Any]:  # type: ignore[override]
        return cfg  # type: ignore[return-value]
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


@dataclass
class DVCStageProvenance:
    stage: str
    outs: dict[str, dict[str, Any]]
    deps: dict[str, dict[str, Any]]
    params: dict[str, Any]


def x__sha256_bytes__mutmut_orig(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def x__sha256_bytes__mutmut_1(b: bytes) -> str:
    return hashlib.sha256(None).hexdigest()

x__sha256_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x__sha256_bytes__mutmut_1': x__sha256_bytes__mutmut_1
}

def _sha256_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x__sha256_bytes__mutmut_orig, x__sha256_bytes__mutmut_mutants, args, kwargs)
    return result 

_sha256_bytes.__signature__ = _mutmut_signature(x__sha256_bytes__mutmut_orig)
x__sha256_bytes__mutmut_orig.__name__ = 'x__sha256_bytes'


def x__config_fingerprint__mutmut_orig(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_1(cfg: DictConfig) -> str:
    container = None
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_2(cfg: DictConfig) -> str:
    container = _to_container(None)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_3(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = None
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_4(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(None, sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_5(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=None)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_6(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_7(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, )
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_8(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=False)
    return _sha256_bytes(yml.encode("utf-8"))


def x__config_fingerprint__mutmut_9(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(None)


def x__config_fingerprint__mutmut_10(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode(None))


def x__config_fingerprint__mutmut_11(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("XXutf-8XX"))


def x__config_fingerprint__mutmut_12(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("UTF-8"))

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
    'x__config_fingerprint__mutmut_12': x__config_fingerprint__mutmut_12
}

def _config_fingerprint(*args, **kwargs):
    result = _mutmut_trampoline(x__config_fingerprint__mutmut_orig, x__config_fingerprint__mutmut_mutants, args, kwargs)
    return result 

_config_fingerprint.__signature__ = _mutmut_signature(x__config_fingerprint__mutmut_orig)
x__config_fingerprint__mutmut_orig.__name__ = 'x__config_fingerprint'


def x__read_dvc_lock__mutmut_orig(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_1(lock_path: Path) -> dict[str, Any]:
    if lock_path.exists():
        return {}
    with lock_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_2(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open(None, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_3(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding=None) as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_4(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_5(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", ) as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_6(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("XXrXX", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_7(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("R", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_8(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="XXutf-8XX") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_9(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="UTF-8") as f:
        return yaml.safe_load(f) or {}


def x__read_dvc_lock__mutmut_10(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) and {}


def x__read_dvc_lock__mutmut_11(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(None) or {}

x__read_dvc_lock__mutmut_mutants : ClassVar[MutantDict] = {
'x__read_dvc_lock__mutmut_1': x__read_dvc_lock__mutmut_1, 
    'x__read_dvc_lock__mutmut_2': x__read_dvc_lock__mutmut_2, 
    'x__read_dvc_lock__mutmut_3': x__read_dvc_lock__mutmut_3, 
    'x__read_dvc_lock__mutmut_4': x__read_dvc_lock__mutmut_4, 
    'x__read_dvc_lock__mutmut_5': x__read_dvc_lock__mutmut_5, 
    'x__read_dvc_lock__mutmut_6': x__read_dvc_lock__mutmut_6, 
    'x__read_dvc_lock__mutmut_7': x__read_dvc_lock__mutmut_7, 
    'x__read_dvc_lock__mutmut_8': x__read_dvc_lock__mutmut_8, 
    'x__read_dvc_lock__mutmut_9': x__read_dvc_lock__mutmut_9, 
    'x__read_dvc_lock__mutmut_10': x__read_dvc_lock__mutmut_10, 
    'x__read_dvc_lock__mutmut_11': x__read_dvc_lock__mutmut_11
}

def _read_dvc_lock(*args, **kwargs):
    result = _mutmut_trampoline(x__read_dvc_lock__mutmut_orig, x__read_dvc_lock__mutmut_mutants, args, kwargs)
    return result 

_read_dvc_lock.__signature__ = _mutmut_signature(x__read_dvc_lock__mutmut_orig)
x__read_dvc_lock__mutmut_orig.__name__ = 'x__read_dvc_lock'


def x__deep_update_dict__mutmut_orig(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(target[key], value)
        else:
            target[key] = value


def x__deep_update_dict__mutmut_1(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) or isinstance(target.get(key), dict):
            _deep_update_dict(target[key], value)
        else:
            target[key] = value


def x__deep_update_dict__mutmut_2(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(None, value)
        else:
            target[key] = value


def x__deep_update_dict__mutmut_3(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(target[key], None)
        else:
            target[key] = value


def x__deep_update_dict__mutmut_4(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(value)
        else:
            target[key] = value


def x__deep_update_dict__mutmut_5(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(target[key], )
        else:
            target[key] = value


def x__deep_update_dict__mutmut_6(target: dict[str, Any], new: dict[str, Any]) -> None:
    for key, value in new.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update_dict(target[key], value)
        else:
            target[key] = None

x__deep_update_dict__mutmut_mutants : ClassVar[MutantDict] = {
'x__deep_update_dict__mutmut_1': x__deep_update_dict__mutmut_1, 
    'x__deep_update_dict__mutmut_2': x__deep_update_dict__mutmut_2, 
    'x__deep_update_dict__mutmut_3': x__deep_update_dict__mutmut_3, 
    'x__deep_update_dict__mutmut_4': x__deep_update_dict__mutmut_4, 
    'x__deep_update_dict__mutmut_5': x__deep_update_dict__mutmut_5, 
    'x__deep_update_dict__mutmut_6': x__deep_update_dict__mutmut_6
}

def _deep_update_dict(*args, **kwargs):
    result = _mutmut_trampoline(x__deep_update_dict__mutmut_orig, x__deep_update_dict__mutmut_mutants, args, kwargs)
    return result 

_deep_update_dict.__signature__ = _mutmut_signature(x__deep_update_dict__mutmut_orig)
x__deep_update_dict__mutmut_orig.__name__ = 'x__deep_update_dict'


def x_collect_dvc_stage__mutmut_orig(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_1(lock: dict[str, Any], stage: str = "XXprepareXX") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_2(lock: dict[str, Any], stage: str = "PREPARE") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_3(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = None
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_4(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") and {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_5(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get(None) or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_6(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("XXstagesXX") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_7(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("STAGES") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_8(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = None
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_9(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(None)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_10(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_11(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = None
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_12(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") and []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_13(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get(None) or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_14(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("XXoutsXX") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_15(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("OUTS") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_16(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = None
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_17(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") and []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_18(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get(None) or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_19(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("XXdepsXX") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_20(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("DEPS") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_21(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = None

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_22(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") and {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_23(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get(None) or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_24(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("XXparamsXX") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_25(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("PARAMS") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_26(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = None
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_27(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = None
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_28(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(None) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_29(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_30(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                break
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_31(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_32(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    break
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_33(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_34(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = None
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_35(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(None)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_36(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(None, value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_37(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], None)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_38(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_39(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], )

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_40(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = None
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_41(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get(None, {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_42(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", None)
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_43(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get({})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_44(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", )
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_45(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("XXparams.yamlXX", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_46(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("PARAMS.YAML", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_47(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = None
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_48(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["XXpathXX"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_49(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["PATH"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_50(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k == "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_51(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "XXpathXX"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_52(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "PATH"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_53(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "XXpathXX" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_54(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "PATH" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_55(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" not in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_56(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = None
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_57(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["XXpathXX"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_58(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["PATH"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_59(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k == "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_60(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "XXpathXX"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_61(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "PATH"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_62(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "XXpathXX" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_63(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "PATH" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_64(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" not in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_65(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=None, outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_66(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=None, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_67(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=None, params=params)


def x_collect_dvc_stage__mutmut_68(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=None)


def x_collect_dvc_stage__mutmut_69(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(outs=outs, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_70(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, deps=deps, params=params)


def x_collect_dvc_stage__mutmut_71(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, params=params)


def x_collect_dvc_stage__mutmut_72(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    raw_params = s.get("params") or {}

    params_by_file: dict[str, dict[str, Any]] = {}
    if isinstance(raw_params, dict):
        params_by_file = {
            key: dict(value) for key, value in raw_params.items() if isinstance(value, dict)
        }
    elif isinstance(raw_params, list):
        for entry in raw_params:
            if not isinstance(entry, dict):
                continue
            for filename, value in entry.items():
                if not isinstance(value, dict):
                    continue
                if filename not in params_by_file:
                    params_by_file[filename] = dict(value)
                else:
                    _deep_update_dict(params_by_file[filename], value)

    params = params_by_file.get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, )

x_collect_dvc_stage__mutmut_mutants : ClassVar[MutantDict] = {
'x_collect_dvc_stage__mutmut_1': x_collect_dvc_stage__mutmut_1, 
    'x_collect_dvc_stage__mutmut_2': x_collect_dvc_stage__mutmut_2, 
    'x_collect_dvc_stage__mutmut_3': x_collect_dvc_stage__mutmut_3, 
    'x_collect_dvc_stage__mutmut_4': x_collect_dvc_stage__mutmut_4, 
    'x_collect_dvc_stage__mutmut_5': x_collect_dvc_stage__mutmut_5, 
    'x_collect_dvc_stage__mutmut_6': x_collect_dvc_stage__mutmut_6, 
    'x_collect_dvc_stage__mutmut_7': x_collect_dvc_stage__mutmut_7, 
    'x_collect_dvc_stage__mutmut_8': x_collect_dvc_stage__mutmut_8, 
    'x_collect_dvc_stage__mutmut_9': x_collect_dvc_stage__mutmut_9, 
    'x_collect_dvc_stage__mutmut_10': x_collect_dvc_stage__mutmut_10, 
    'x_collect_dvc_stage__mutmut_11': x_collect_dvc_stage__mutmut_11, 
    'x_collect_dvc_stage__mutmut_12': x_collect_dvc_stage__mutmut_12, 
    'x_collect_dvc_stage__mutmut_13': x_collect_dvc_stage__mutmut_13, 
    'x_collect_dvc_stage__mutmut_14': x_collect_dvc_stage__mutmut_14, 
    'x_collect_dvc_stage__mutmut_15': x_collect_dvc_stage__mutmut_15, 
    'x_collect_dvc_stage__mutmut_16': x_collect_dvc_stage__mutmut_16, 
    'x_collect_dvc_stage__mutmut_17': x_collect_dvc_stage__mutmut_17, 
    'x_collect_dvc_stage__mutmut_18': x_collect_dvc_stage__mutmut_18, 
    'x_collect_dvc_stage__mutmut_19': x_collect_dvc_stage__mutmut_19, 
    'x_collect_dvc_stage__mutmut_20': x_collect_dvc_stage__mutmut_20, 
    'x_collect_dvc_stage__mutmut_21': x_collect_dvc_stage__mutmut_21, 
    'x_collect_dvc_stage__mutmut_22': x_collect_dvc_stage__mutmut_22, 
    'x_collect_dvc_stage__mutmut_23': x_collect_dvc_stage__mutmut_23, 
    'x_collect_dvc_stage__mutmut_24': x_collect_dvc_stage__mutmut_24, 
    'x_collect_dvc_stage__mutmut_25': x_collect_dvc_stage__mutmut_25, 
    'x_collect_dvc_stage__mutmut_26': x_collect_dvc_stage__mutmut_26, 
    'x_collect_dvc_stage__mutmut_27': x_collect_dvc_stage__mutmut_27, 
    'x_collect_dvc_stage__mutmut_28': x_collect_dvc_stage__mutmut_28, 
    'x_collect_dvc_stage__mutmut_29': x_collect_dvc_stage__mutmut_29, 
    'x_collect_dvc_stage__mutmut_30': x_collect_dvc_stage__mutmut_30, 
    'x_collect_dvc_stage__mutmut_31': x_collect_dvc_stage__mutmut_31, 
    'x_collect_dvc_stage__mutmut_32': x_collect_dvc_stage__mutmut_32, 
    'x_collect_dvc_stage__mutmut_33': x_collect_dvc_stage__mutmut_33, 
    'x_collect_dvc_stage__mutmut_34': x_collect_dvc_stage__mutmut_34, 
    'x_collect_dvc_stage__mutmut_35': x_collect_dvc_stage__mutmut_35, 
    'x_collect_dvc_stage__mutmut_36': x_collect_dvc_stage__mutmut_36, 
    'x_collect_dvc_stage__mutmut_37': x_collect_dvc_stage__mutmut_37, 
    'x_collect_dvc_stage__mutmut_38': x_collect_dvc_stage__mutmut_38, 
    'x_collect_dvc_stage__mutmut_39': x_collect_dvc_stage__mutmut_39, 
    'x_collect_dvc_stage__mutmut_40': x_collect_dvc_stage__mutmut_40, 
    'x_collect_dvc_stage__mutmut_41': x_collect_dvc_stage__mutmut_41, 
    'x_collect_dvc_stage__mutmut_42': x_collect_dvc_stage__mutmut_42, 
    'x_collect_dvc_stage__mutmut_43': x_collect_dvc_stage__mutmut_43, 
    'x_collect_dvc_stage__mutmut_44': x_collect_dvc_stage__mutmut_44, 
    'x_collect_dvc_stage__mutmut_45': x_collect_dvc_stage__mutmut_45, 
    'x_collect_dvc_stage__mutmut_46': x_collect_dvc_stage__mutmut_46, 
    'x_collect_dvc_stage__mutmut_47': x_collect_dvc_stage__mutmut_47, 
    'x_collect_dvc_stage__mutmut_48': x_collect_dvc_stage__mutmut_48, 
    'x_collect_dvc_stage__mutmut_49': x_collect_dvc_stage__mutmut_49, 
    'x_collect_dvc_stage__mutmut_50': x_collect_dvc_stage__mutmut_50, 
    'x_collect_dvc_stage__mutmut_51': x_collect_dvc_stage__mutmut_51, 
    'x_collect_dvc_stage__mutmut_52': x_collect_dvc_stage__mutmut_52, 
    'x_collect_dvc_stage__mutmut_53': x_collect_dvc_stage__mutmut_53, 
    'x_collect_dvc_stage__mutmut_54': x_collect_dvc_stage__mutmut_54, 
    'x_collect_dvc_stage__mutmut_55': x_collect_dvc_stage__mutmut_55, 
    'x_collect_dvc_stage__mutmut_56': x_collect_dvc_stage__mutmut_56, 
    'x_collect_dvc_stage__mutmut_57': x_collect_dvc_stage__mutmut_57, 
    'x_collect_dvc_stage__mutmut_58': x_collect_dvc_stage__mutmut_58, 
    'x_collect_dvc_stage__mutmut_59': x_collect_dvc_stage__mutmut_59, 
    'x_collect_dvc_stage__mutmut_60': x_collect_dvc_stage__mutmut_60, 
    'x_collect_dvc_stage__mutmut_61': x_collect_dvc_stage__mutmut_61, 
    'x_collect_dvc_stage__mutmut_62': x_collect_dvc_stage__mutmut_62, 
    'x_collect_dvc_stage__mutmut_63': x_collect_dvc_stage__mutmut_63, 
    'x_collect_dvc_stage__mutmut_64': x_collect_dvc_stage__mutmut_64, 
    'x_collect_dvc_stage__mutmut_65': x_collect_dvc_stage__mutmut_65, 
    'x_collect_dvc_stage__mutmut_66': x_collect_dvc_stage__mutmut_66, 
    'x_collect_dvc_stage__mutmut_67': x_collect_dvc_stage__mutmut_67, 
    'x_collect_dvc_stage__mutmut_68': x_collect_dvc_stage__mutmut_68, 
    'x_collect_dvc_stage__mutmut_69': x_collect_dvc_stage__mutmut_69, 
    'x_collect_dvc_stage__mutmut_70': x_collect_dvc_stage__mutmut_70, 
    'x_collect_dvc_stage__mutmut_71': x_collect_dvc_stage__mutmut_71, 
    'x_collect_dvc_stage__mutmut_72': x_collect_dvc_stage__mutmut_72
}

def collect_dvc_stage(*args, **kwargs):
    result = _mutmut_trampoline(x_collect_dvc_stage__mutmut_orig, x_collect_dvc_stage__mutmut_mutants, args, kwargs)
    return result 

collect_dvc_stage.__signature__ = _mutmut_signature(x_collect_dvc_stage__mutmut_orig)
x_collect_dvc_stage__mutmut_orig.__name__ = 'x_collect_dvc_stage'


def _default_project_root() -> Path:
    """Return a writable default root, falling back to the current working directory."""

    return Path.cwd()


def x__resolve_out_dir__mutmut_orig(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is None:
        return project_root / ".codex"
    if out_dir.is_absolute():
        return out_dir
    return project_root / out_dir


def x__resolve_out_dir__mutmut_1(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is not None:
        return project_root / ".codex"
    if out_dir.is_absolute():
        return out_dir
    return project_root / out_dir


def x__resolve_out_dir__mutmut_2(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is None:
        return project_root * ".codex"
    if out_dir.is_absolute():
        return out_dir
    return project_root / out_dir


def x__resolve_out_dir__mutmut_3(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is None:
        return project_root / "XX.codexXX"
    if out_dir.is_absolute():
        return out_dir
    return project_root / out_dir


def x__resolve_out_dir__mutmut_4(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is None:
        return project_root / ".CODEX"
    if out_dir.is_absolute():
        return out_dir
    return project_root / out_dir


def x__resolve_out_dir__mutmut_5(project_root: Path, out_dir: Path | None) -> Path:
    if out_dir is None:
        return project_root / ".codex"
    if out_dir.is_absolute():
        return out_dir
    return project_root * out_dir

x__resolve_out_dir__mutmut_mutants : ClassVar[MutantDict] = {
'x__resolve_out_dir__mutmut_1': x__resolve_out_dir__mutmut_1, 
    'x__resolve_out_dir__mutmut_2': x__resolve_out_dir__mutmut_2, 
    'x__resolve_out_dir__mutmut_3': x__resolve_out_dir__mutmut_3, 
    'x__resolve_out_dir__mutmut_4': x__resolve_out_dir__mutmut_4, 
    'x__resolve_out_dir__mutmut_5': x__resolve_out_dir__mutmut_5
}

def _resolve_out_dir(*args, **kwargs):
    result = _mutmut_trampoline(x__resolve_out_dir__mutmut_orig, x__resolve_out_dir__mutmut_mutants, args, kwargs)
    return result 

_resolve_out_dir.__signature__ = _mutmut_signature(x__resolve_out_dir__mutmut_orig)
x__resolve_out_dir__mutmut_orig.__name__ = 'x__resolve_out_dir'


def x_write_provenance__mutmut_orig(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_1(
    cfg: DictConfig,
    stage: str = "XXprepareXX",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_2(
    cfg: DictConfig,
    stage: str = "PREPARE",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_3(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = None
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_4(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root and _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_5(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = None
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_6(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(None, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_7(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, None)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_8(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_9(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, )
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_10(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=None, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_11(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=None)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_12(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_13(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, )
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_14(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=False, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_15(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=False)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_16(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = None
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_17(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(None)
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_18(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root * "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_19(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "XXdvc.lockXX")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_20(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "DVC.LOCK")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_21(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = ""
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_22(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = None
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_23(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(None, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_24(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=None)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_25(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_26(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, )
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_27(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = None

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_28(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(None)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_29(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = None
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_30(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "XXtimestamp_utcXX": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_31(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "TIMESTAMP_UTC": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_32(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(None).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_33(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "XXgit_commitXX": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_34(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "GIT_COMMIT": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_35(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get(None, ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_36(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", None),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_37(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get(""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_38(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_39(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("XXGIT_COMMITXX", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_40(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("git_commit", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_41(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", "XXXX"),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_42(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "XXconfig_fingerprint_sha256XX": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_43(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "CONFIG_FINGERPRINT_SHA256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_44(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(None),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_45(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "XXdvcXX": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_46(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "DVC": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_47(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = None
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_48(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir * "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_49(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "XXprovenance.jsonXX"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_50(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "PROVENANCE.JSON"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_51(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open(None, encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_52(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding=None) as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_53(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open(encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_54(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", ) as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_55(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("XXwXX", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_56(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("W", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_57(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="XXutf-8XX") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_58(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="UTF-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_59(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(None, f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_60(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, None, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_61(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=None, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_62(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=None)
    return out_path


def x_write_provenance__mutmut_63(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(f, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_64(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, indent=2, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_65(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_66(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, )
    return out_path


def x_write_provenance__mutmut_67(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=3, sort_keys=True)
    return out_path


def x_write_provenance__mutmut_68(
    cfg: DictConfig,
    stage: str = "prepare",
    out_dir: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    project_root = project_root or _default_project_root()
    resolved_out_dir = _resolve_out_dir(project_root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(project_root / "dvc.lock")
    dvc_info: dict[str, Any] | None = None
    if lock:
        st = collect_dvc_stage(lock, stage=stage)
        if st:
            dvc_info = asdict(st)

    data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": os.environ.get("GIT_COMMIT", ""),
        "config_fingerprint_sha256": _config_fingerprint(cfg),
        "dvc": dvc_info,
    }
    out_path = resolved_out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
    return out_path

x_write_provenance__mutmut_mutants : ClassVar[MutantDict] = {
'x_write_provenance__mutmut_1': x_write_provenance__mutmut_1, 
    'x_write_provenance__mutmut_2': x_write_provenance__mutmut_2, 
    'x_write_provenance__mutmut_3': x_write_provenance__mutmut_3, 
    'x_write_provenance__mutmut_4': x_write_provenance__mutmut_4, 
    'x_write_provenance__mutmut_5': x_write_provenance__mutmut_5, 
    'x_write_provenance__mutmut_6': x_write_provenance__mutmut_6, 
    'x_write_provenance__mutmut_7': x_write_provenance__mutmut_7, 
    'x_write_provenance__mutmut_8': x_write_provenance__mutmut_8, 
    'x_write_provenance__mutmut_9': x_write_provenance__mutmut_9, 
    'x_write_provenance__mutmut_10': x_write_provenance__mutmut_10, 
    'x_write_provenance__mutmut_11': x_write_provenance__mutmut_11, 
    'x_write_provenance__mutmut_12': x_write_provenance__mutmut_12, 
    'x_write_provenance__mutmut_13': x_write_provenance__mutmut_13, 
    'x_write_provenance__mutmut_14': x_write_provenance__mutmut_14, 
    'x_write_provenance__mutmut_15': x_write_provenance__mutmut_15, 
    'x_write_provenance__mutmut_16': x_write_provenance__mutmut_16, 
    'x_write_provenance__mutmut_17': x_write_provenance__mutmut_17, 
    'x_write_provenance__mutmut_18': x_write_provenance__mutmut_18, 
    'x_write_provenance__mutmut_19': x_write_provenance__mutmut_19, 
    'x_write_provenance__mutmut_20': x_write_provenance__mutmut_20, 
    'x_write_provenance__mutmut_21': x_write_provenance__mutmut_21, 
    'x_write_provenance__mutmut_22': x_write_provenance__mutmut_22, 
    'x_write_provenance__mutmut_23': x_write_provenance__mutmut_23, 
    'x_write_provenance__mutmut_24': x_write_provenance__mutmut_24, 
    'x_write_provenance__mutmut_25': x_write_provenance__mutmut_25, 
    'x_write_provenance__mutmut_26': x_write_provenance__mutmut_26, 
    'x_write_provenance__mutmut_27': x_write_provenance__mutmut_27, 
    'x_write_provenance__mutmut_28': x_write_provenance__mutmut_28, 
    'x_write_provenance__mutmut_29': x_write_provenance__mutmut_29, 
    'x_write_provenance__mutmut_30': x_write_provenance__mutmut_30, 
    'x_write_provenance__mutmut_31': x_write_provenance__mutmut_31, 
    'x_write_provenance__mutmut_32': x_write_provenance__mutmut_32, 
    'x_write_provenance__mutmut_33': x_write_provenance__mutmut_33, 
    'x_write_provenance__mutmut_34': x_write_provenance__mutmut_34, 
    'x_write_provenance__mutmut_35': x_write_provenance__mutmut_35, 
    'x_write_provenance__mutmut_36': x_write_provenance__mutmut_36, 
    'x_write_provenance__mutmut_37': x_write_provenance__mutmut_37, 
    'x_write_provenance__mutmut_38': x_write_provenance__mutmut_38, 
    'x_write_provenance__mutmut_39': x_write_provenance__mutmut_39, 
    'x_write_provenance__mutmut_40': x_write_provenance__mutmut_40, 
    'x_write_provenance__mutmut_41': x_write_provenance__mutmut_41, 
    'x_write_provenance__mutmut_42': x_write_provenance__mutmut_42, 
    'x_write_provenance__mutmut_43': x_write_provenance__mutmut_43, 
    'x_write_provenance__mutmut_44': x_write_provenance__mutmut_44, 
    'x_write_provenance__mutmut_45': x_write_provenance__mutmut_45, 
    'x_write_provenance__mutmut_46': x_write_provenance__mutmut_46, 
    'x_write_provenance__mutmut_47': x_write_provenance__mutmut_47, 
    'x_write_provenance__mutmut_48': x_write_provenance__mutmut_48, 
    'x_write_provenance__mutmut_49': x_write_provenance__mutmut_49, 
    'x_write_provenance__mutmut_50': x_write_provenance__mutmut_50, 
    'x_write_provenance__mutmut_51': x_write_provenance__mutmut_51, 
    'x_write_provenance__mutmut_52': x_write_provenance__mutmut_52, 
    'x_write_provenance__mutmut_53': x_write_provenance__mutmut_53, 
    'x_write_provenance__mutmut_54': x_write_provenance__mutmut_54, 
    'x_write_provenance__mutmut_55': x_write_provenance__mutmut_55, 
    'x_write_provenance__mutmut_56': x_write_provenance__mutmut_56, 
    'x_write_provenance__mutmut_57': x_write_provenance__mutmut_57, 
    'x_write_provenance__mutmut_58': x_write_provenance__mutmut_58, 
    'x_write_provenance__mutmut_59': x_write_provenance__mutmut_59, 
    'x_write_provenance__mutmut_60': x_write_provenance__mutmut_60, 
    'x_write_provenance__mutmut_61': x_write_provenance__mutmut_61, 
    'x_write_provenance__mutmut_62': x_write_provenance__mutmut_62, 
    'x_write_provenance__mutmut_63': x_write_provenance__mutmut_63, 
    'x_write_provenance__mutmut_64': x_write_provenance__mutmut_64, 
    'x_write_provenance__mutmut_65': x_write_provenance__mutmut_65, 
    'x_write_provenance__mutmut_66': x_write_provenance__mutmut_66, 
    'x_write_provenance__mutmut_67': x_write_provenance__mutmut_67, 
    'x_write_provenance__mutmut_68': x_write_provenance__mutmut_68
}

def write_provenance(*args, **kwargs):
    result = _mutmut_trampoline(x_write_provenance__mutmut_orig, x_write_provenance__mutmut_mutants, args, kwargs)
    return result 

write_provenance.__signature__ = _mutmut_signature(x_write_provenance__mutmut_orig)
x_write_provenance__mutmut_orig.__name__ = 'x_write_provenance'
