"""Utilities for recording configuration provenance."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

try:  # Optional dependency
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception:  # pragma: no cover - optional
    DictConfig = object  # type: ignore
    OmegaConf = None  # type: ignore


def _pip_freeze() -> str:
    try:  # pragma: no cover - dependent on environment
        return subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    except Exception:
        return ""


def _git_commit() -> str | None:
    try:  # pragma: no cover - git may be unavailable
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def environment_summary() -> dict[str, Any]:
    """Collect Git, hardware, and package metadata."""

    info: dict[str, Any] = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "pip_freeze": _pip_freeze(),
    }
    commit = _git_commit()
    if commit:
        info["git_commit"] = commit
    try:  # pragma: no cover - torch optional
        import torch

        cuda = getattr(torch.version, "cuda", None)
        if cuda:
            info["cuda_version"] = cuda
        if torch.cuda.is_available():
            info["gpus"] = [
                torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
            ]
    except Exception:
        pass
    try:  # pragma: no cover - optional deps
        from codex_ml.monitoring.codex_logging import _codex_sample_system

        info["system_metrics"] = _codex_sample_system()
    except Exception:
        pass
    return info


def snapshot_hydra_config(
    cfg: DictConfig | Mapping[str, object],
    out_dir: Path,
    overrides: Sequence[str] | None = None,
) -> None:
    """Persist the effective Hydra configuration and environment details."""

    out_dir.mkdir(parents=True, exist_ok=True)
    if OmegaConf is not None and isinstance(cfg, DictConfig):
        (out_dir / "config.yaml").write_text(OmegaConf.to_yaml(cfg))
    elif OmegaConf is not None:
        (out_dir / "config.yaml").write_text(OmegaConf.to_yaml(OmegaConf.create(cfg)))
    else:
        (out_dir / "config.yaml").write_text(json.dumps(cfg, indent=2))
    if overrides:
        (out_dir / "overrides.txt").write_text("\n".join(overrides))
    info = environment_summary()
    (out_dir / "provenance.json").write_text(json.dumps(info, indent=2))
