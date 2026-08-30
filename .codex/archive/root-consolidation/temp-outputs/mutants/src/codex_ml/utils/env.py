"""Environment fingerprint utilities for reproducibility logging.

Captures Python, CUDA, hardware, and driver versions so that training runs
can be fully reproduced from the metadata stored in checkpoint sidecars or
experiment-tracking systems.

Usage::

    from codex_ml.utils.env import environment_summary, EnvironmentFingerprint

    fp = EnvironmentFingerprint.capture()
    logger.info(fp.to_dict())
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional torch dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - optional psutil dependency
    import psutil as _psutil
except (ImportError, AttributeError):  # pragma: no cover
    _psutil = None

try:  # pragma: no cover - optional pynvml dependency
    import pynvml as _pynvml

    _pynvml.nvmlInit()
except (ImportError, AttributeError):  # pragma: no cover
    _pynvml = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


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
    except (IOError, OSError) as exc:
        LOGGER.debug("Unable to read git commit from %s: %s", root, exc)
        return None


def _cuda_driver_version() -> Optional[str]:
    """Return the CUDA driver version string, or *None* when unavailable."""
    if _pynvml is not None:
        try:
            val = _pynvml.nvmlSystemGetDriverVersion()
            if isinstance(val, (bytes, bytearray)):
                val = val.decode("utf-8", errors="replace")
            return val or None
        except (IOError, OSError):  # pragma: no cover - NVML runtime failure
            LOGGER.debug("pynvml driver version query failed", exc_info=True)
    # Fallback: read nvidia-smi output
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            out = subprocess.check_output(
                [smi, "--query-gpu=driver_version", "--format=csv,noheader"],
                timeout=5,
                text=True,
            )
            version = out.strip().splitlines()[0].strip()
            return version or None
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ):  # pragma: no cover - nvidia-smi unavailable / timeout
            LOGGER.debug("nvidia-smi driver version query failed", exc_info=True)
    return None


def _gpu_devices() -> list[dict[str, Any]]:
    """Return a list of GPU device info dicts (name, memory_total_mb)."""
    devices: list[dict[str, Any]] = []
    if torch is not None and hasattr(torch, "cuda"):
        try:
            count = torch.cuda.device_count()
        except Exception:  # pragma: no cover - CUDA not initialised
            return devices
        for i in range(count):
            entry: dict[str, Any] = {"index": i}
            try:
                entry["name"] = torch.cuda.get_device_name(i)
            except Exception:  # pragma: no cover
                entry["name"] = None
            try:
                props = torch.cuda.get_device_properties(i)
                entry["memory_total_mb"] = round(props.total_memory / 1024 / 1024, 1)
                entry["compute_capability"] = f"{props.major}.{props.minor}"
            except Exception:  # pragma: no cover
                pass
            devices.append(entry)
    elif _pynvml is not None:
        try:
            count = _pynvml.nvmlDeviceGetCount()
        except Exception:  # pragma: no cover
            return devices
        for i in range(count):
            entry = {"index": i}
            try:
                handle = _pynvml.nvmlDeviceGetHandleByIndex(i)
                name = _pynvml.nvmlDeviceGetName(handle)
                entry["name"] = (
                    name.decode("utf-8", errors="replace")
                    if isinstance(name, (bytes, bytearray))
                    else str(name)
                )
                mem = _pynvml.nvmlDeviceGetMemoryInfo(handle)
                entry["memory_total_mb"] = round(mem.total / 1024 / 1024, 1)
            except Exception:  # pragma: no cover
                pass
            devices.append(entry)
    return devices


def _ram_total_mb() -> Optional[float]:
    """Return total system RAM in MB, or *None* when psutil is unavailable."""
    if _psutil is not None:
        try:
            return round(_psutil.virtual_memory().total / 1024 / 1024, 1)
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover
            LOGGER.debug("psutil RAM query failed", exc_info=True)
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class EnvironmentFingerprint:
    """Structured snapshot of the execution environment.

    All fields are optional so that the fingerprint remains constructable
    in minimal environments (e.g., CPU-only CI or test runners without
    optional dependencies installed).
    """

    # Software versions
    python_version: str
    os_platform: str
    git_commit: Optional[str] = None

    # Hardware — CPU
    processor: Optional[str] = None
    cpu_count: Optional[int] = None
    ram_total_mb: Optional[float] = None

    # Hardware — GPU / CUDA
    cuda_version: Optional[str] = None
    cuda_driver_version: Optional[str] = None
    gpu_devices: list = dataclasses.field(default_factory=list)

    @classmethod
    def capture(cls, repo_root: Optional[Path] = None) -> "EnvironmentFingerprint":
        """Capture the current environment and return a fingerprint instance.

        Args:
            repo_root: Optional path to the repository root for git commit
                resolution.  Defaults to the repository containing this file.

        Returns:
            Populated :class:`EnvironmentFingerprint`.
        """
        cuda_ver: Optional[str] = None
        gpu_devices: list[dict[str, Any]] = []
        if torch is not None:
            version_mod = getattr(torch, "version", None)
            cuda_ver = getattr(version_mod, "cuda", None) if version_mod else None
            gpu_devices = _gpu_devices()

        return cls(
            python_version=platform.python_version(),
            os_platform=platform.platform(),
            git_commit=_git_commit(repo_root),
            processor=platform.processor() or None,
            cpu_count=os.cpu_count(),
            ram_total_mb=_ram_total_mb(),
            cuda_version=cuda_ver,
            cuda_driver_version=_cuda_driver_version(),
            gpu_devices=gpu_devices,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert fingerprint to a plain dictionary suitable for JSON serialisation."""
        return dataclasses.asdict(self)

    def digest(self) -> str:
        """Return a short SHA-256 hex digest of the fingerprint for quick comparison.

        Keys that vary run-to-run (e.g. ``git_commit``) are excluded so the
        digest is stable across commits on the same hardware.
        """
        stable: dict[str, Any] = {
            k: v for k, v in self.to_dict().items() if k not in {"git_commit"}
        }
        serialised = json.dumps(stable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialised.encode()).hexdigest()[:16]

    def log(self, logger: Optional[logging.Logger] = None) -> None:
        """Emit the fingerprint at INFO level to *logger* (defaults to module logger)."""
        _log = logger or LOGGER
        _log.info(
            "Environment fingerprint: python=%s os=%s cuda=%s driver=%s gpu_count=%d digest=%s",
            self.python_version,
            self.os_platform,
            self.cuda_version or "N/A",
            self.cuda_driver_version or "N/A",
            len(self.gpu_devices),
            self.digest(),
        )


def environment_summary() -> dict[str, Any]:
    """Collect basic environment information for reproducibility.

    .. deprecated::
        Prefer :class:`EnvironmentFingerprint` for structured captures.
        This function is retained for backward compatibility.
    """
    fp = EnvironmentFingerprint.capture()
    info: dict[str, Any] = {
        "os": fp.os_platform,
        "python": fp.python_version,
        "processor": fp.processor,
        "cpu_count": fp.cpu_count,
    }
    if fp.git_commit is not None:
        info["git_commit"] = fp.git_commit
    if fp.cuda_version is not None:
        info["cuda_version"] = fp.cuda_version
    if fp.gpu_devices:
        info["gpu"] = fp.gpu_devices[0].get("name")
    return info


__all__ = ["EnvironmentFingerprint", "environment_summary"]
