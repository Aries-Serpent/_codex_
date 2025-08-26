# [Module]: Reproducibility utilities
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import json
import os
import random
from dataclasses import asdict, dataclass
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
            try:
                torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
                torch.backends.cudnn.benchmark = False  # type: ignore[attr-defined]
            except Exception:
                pass
        torch_state = (
            torch.get_rng_state().tolist() if hasattr(torch, "get_rng_state") else None
        )
        if hasattr(torch.cuda, "get_rng_state_all"):
            try:
                torch_cuda_state = [t.tolist() for t in torch.cuda.get_rng_state_all()]  # type: ignore
            except Exception:
                torch_cuda_state = None
    return RNGState(random.getstate(), np_state, torch_state, torch_cuda_state)


def save_rng(path: str, state: RNGState) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f)


def load_rng(path: str) -> RNGState:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RNGState(**data)
