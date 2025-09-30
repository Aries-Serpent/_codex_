# [Module]: Reproducibility utilities
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
from __future__ import annotations

import importlib.metadata as importlib_metadata
import json
import os
import random
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import numpy as np
except Exception:
    np = None  # type: ignore
try:
    import torch
except Exception:
    torch = None  # type: ignore


@dataclass
class RNGState:
    py_random_state: Any
    np_random_state: Optional[Any]
    torch_state: Optional[Any]
    torch_cuda_state: Optional[Any]


def set_seed(seed: int, deterministic: bool = True) -> RNGState:
    random.seed(seed)
    np_state = None
    if np is not None:
        np.random.seed(seed)
        np_state = np.random.get_state()
    torch_state = None
    torch_cuda_state = None
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            # Favor strict determinism when available. This can impact
            # performance and may restrict certain operators.
            try:  # pragma: no cover - environment dependent
                if hasattr(torch, "use_deterministic_algorithms"):
                    torch.use_deterministic_algorithms(True)  # type: ignore[attr-defined]
            except Exception:
                # Fallback to legacy CuDNN knobs
                try:
                    torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                    torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]
                except Exception:
                    pass
        torch_state = torch.get_rng_state().tolist() if hasattr(torch, "get_rng_state") else None
        if hasattr(torch.cuda, "get_rng_state_all"):
            try:
                torch_cuda_state = [t.tolist() for t in torch.cuda.get_rng_state_all()]  # type: ignore
            except Exception:
                torch_cuda_state = None
    return RNGState(random.getstate(), np_state, torch_state, torch_cuda_state)


def _to_jsonable(obj: Any) -> Any:
    """Best-effort conversion of RNG state to JSON-serializable structures.

    - numpy arrays -> lists
    - tuples/sets  -> lists
    - dict/list    -> recurse
    """
    try:
        import numpy as _np  # type: ignore
    except Exception:  # pragma: no cover - numpy optional
        _np = None  # type: ignore

    if _np is not None and isinstance(obj, _np.ndarray):
        return obj.tolist()
    if isinstance(obj, (tuple, set)):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj


def save_rng(path: str, state: RNGState) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = _to_jsonable(asdict(state))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def load_rng(path: str) -> RNGState:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RNGState(**data)


def restore_rng(state: RNGState) -> None:
    """Restore Python, NumPy and Torch RNG state from ``state``."""

    py_state = state.py_random_state
    if isinstance(py_state, list):
        version = py_state[0]
        inner = tuple(py_state[1]) if len(py_state) > 1 else ()
        gauss = py_state[2] if len(py_state) > 2 else None
        py_state = (version, inner, gauss)
    random.setstate(py_state)
    if np is not None and state.np_random_state is not None:
        try:
            np_state = state.np_random_state
            # Convert JSON-safe lists back to tuple + ndarray where applicable
            if isinstance(np_state, list):
                # MT19937 format: (str, ndarray, int, int, float)
                seq = list(np_state)
                if len(seq) >= 2 and isinstance(seq[1], list):
                    try:
                        arr = np.array(seq[1], dtype="uint32")
                        seq[1] = arr
                    except Exception:
                        pass
                np_state = tuple(seq)
            np.random.set_state(np_state)
        except Exception:
            pass
    if torch is not None:
        if state.torch_state is not None and hasattr(torch, "set_rng_state"):
            try:
                torch.set_rng_state(torch.ByteTensor(state.torch_state))  # type: ignore[attr-defined]
            except Exception:
                pass
        if (
            state.torch_cuda_state is not None
            and hasattr(torch, "cuda")
            and hasattr(torch.cuda, "set_rng_state_all")
        ):
            try:
                tensors = [torch.ByteTensor(t) for t in state.torch_cuda_state]
                torch.cuda.set_rng_state_all(tensors)  # type: ignore[attr-defined]
            except Exception:
                pass


def log_env_info(path: str | Path) -> None:
    """Record git commit, packages, system metrics, and CUDA version."""

    commit = "unknown"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        pass

    packages = {
        dist.metadata.get("Name", dist.metadata.get("name", "unknown")): dist.version
        for dist in importlib_metadata.distributions()
    }

    system: dict[str, Any] = {}
    try:  # pragma: no cover - optional deps
        from codex_ml.monitoring.codex_logging import _codex_sample_system

        system = _codex_sample_system()
    except Exception:
        system = {}

    cuda_version = None
    if torch is not None:
        try:  # pragma: no cover - torch optional
            cuda_version = getattr(torch.version, "cuda", None)
        except Exception:
            cuda_version = None

    info = {
        "git_commit": commit,
        "python": sys.version,
        "packages": packages,
        "system": system,
    }
    if cuda_version:
        info["cuda_version"] = cuda_version

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(info, f, sort_keys=True)
