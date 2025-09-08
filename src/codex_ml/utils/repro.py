"""Reproducibility helpers for deterministic seeding."""

from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path
from typing import Dict, Iterable

try:  # pragma: no cover - optional numpy dependency
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - numpy missing
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

try:  # pragma: no cover - optional torch dependency
    import torch

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - torch missing
    TORCH_AVAILABLE = False
    torch = None  # type: ignore


def set_reproducible(seed: int = 42) -> None:
    """Best-effort reproducibility settings.

    Seeds Python, NumPy and torch (when available) and enables deterministic
    algorithms where supported. cuDNN benchmarking is disabled and a default
    ``CUBLAS_WORKSPACE_CONFIG`` is set when absent.

    See PyTorch notes for guarantees and limitations.
    """
    random.seed(seed)

    if NUMPY_AVAILABLE and np is not None:
        np.random.seed(seed)

    if TORCH_AVAILABLE and torch is not None:
        torch.manual_seed(seed)
        # Enable deterministic algorithms when available
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:  # pragma: no cover - older torch
            pass
        # Configure cuDNN for determinism
        try:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        except Exception:  # pragma: no cover - no cudnn
            pass
        # Set CUDA seed if available
        if hasattr(torch.cuda, "is_available") and torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    # Set CUBLAS workspace configuration for deterministic operations
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")


def record_dataset_checksums(files: Iterable[Path], out_path: Path) -> Dict[str, str]:
    """Write SHA256 checksums for ``files`` to ``out_path``."""

    checksums: Dict[str, str] = {}
    for fp in files:
        p = Path(fp)
        if p.exists():
            checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    return checksums


__all__ = ["set_reproducible", "record_dataset_checksums"]
