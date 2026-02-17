"""
Env Module

This module provides functionality for env.

Usage:
    from utils.env import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


def _git_binary() -> Optional[Path]:
    """Return an absolute path to the git executable if available."""

    located = shutil.which("git")
    if located is None:
        LOGGER.debug("git executable not found on PATH")
        return None

    candidate = Path(located).resolve()
    if not candidate.exists():
        LOGGER.warning("Resolved git path %s does not exist", candidate)
        return None

    return candidate


try:  # pragma: no cover - optional torch dependency
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


def _git_commit(root: Optional[Path] = None) -> Optional[str]:
    """Return current Git commit hash if available."""
    root = root or Path(__file__).resolve().parent.parent.parent.parent
    git_bin = _git_binary()
    if git_bin is None:
        return None
    try:
        return subprocess.check_output(
            [str(git_bin), "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        LOGGER.debug("Unable to read git commit from %s: %s", root, exc)
        return None


def environment_summary() -> dict[str, Any]:
    """Collect basic environment information for reproducibility."""
    info: dict[str, Any] = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "processor": platform.processor() or None,
        "cpu_count": os.cpu_count(),
    }
    git_sha = _git_commit()
    if git_sha is not None:
        info["git_commit"] = git_sha
    if torch is not None:
        version_mod = getattr(torch, "version", None)
        info["cuda_version"] = getattr(version_mod, "cuda", None) if version_mod else None
        try:
            info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        except Exception:  # pragma: no cover - torch but CUDA unavailable
            info["gpu"] = None
    return info


__all__ = ["environment_summary"]
