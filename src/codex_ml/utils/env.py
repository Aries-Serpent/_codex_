from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional torch dependency
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


def _git_commit(root: Optional[Path] = None) -> Optional[str]:
    """Return current Git commit hash if available."""
    root = root or Path(__file__).resolve().parent.parent.parent.parent
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True)
            .strip()
        )
    except Exception:
        return None


def environment_summary() -> Dict[str, Any]:
    """Collect basic environment information for reproducibility."""
    info: Dict[str, Any] = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "processor": platform.processor() or None,
        "cpu_count": os.cpu_count(),
    }
    git_sha = _git_commit()
    if git_sha is not None:
        info["git_commit"] = git_sha
    if torch is not None:
        info["cuda_version"] = getattr(torch.version, "cuda", None)
        try:
            info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        except Exception:  # pragma: no cover - torch but CUDA unavailable
            info["gpu"] = None
    return info


__all__ = ["environment_summary"]
