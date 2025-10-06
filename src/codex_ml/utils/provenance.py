"""Utilities for recording configuration provenance."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Sequence

try:  # Optional dependency
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception:  # pragma: no cover - optional
    DictConfig = object  # type: ignore
    OmegaConf = None  # type: ignore

DEFAULT_ENV_JSON = "environment.json"
DEFAULT_ENV_NDJSON = "environment.ndjson"
DEFAULT_PIP_FREEZE = "pip-freeze.txt"


def _capture_command(args: Sequence[str]) -> str | None:
    try:
        return subprocess.check_output(
            list(args), text=True, stderr=subprocess.STDOUT, timeout=5
        ).strip()
    except Exception:
        return None


def _parse_key_value_output(raw: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key:
            parsed[key] = value
    return parsed


def _pip_freeze() -> list[str]:
    try:  # pragma: no cover - dependent on environment
        output = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _yaml_dumps(data: Any) -> str:
    """Serialize ``data`` to YAML, falling back to JSON when PyYAML is unavailable."""

    try:  # pragma: no cover - optional dependency
        import yaml
    except Exception:
        return json.dumps(data, indent=2, sort_keys=True)
    return yaml.safe_dump(data, sort_keys=False)


def _git_commit() -> str | None:
    try:  # pragma: no cover - git may be unavailable
        root = Path(__file__).resolve()
        for parent in root.parents:
            if (parent / ".git").exists():
                root = parent
                break
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return None


def _cpu_metadata() -> MutableMapping[str, Any]:
    details: MutableMapping[str, Any] = {}

    try:
        logical = os.cpu_count()
        if logical is not None:
            details["logical_cores"] = int(logical)
    except Exception:
        pass

    try:
        import psutil  # type: ignore

        physical = psutil.cpu_count(logical=False)
        if physical is not None:
            details["physical_cores"] = int(physical)
        freq = psutil.cpu_freq()
        if freq is not None:
            if getattr(freq, "max", None):
                details["max_frequency_mhz"] = round(float(freq.max), 3)
            if getattr(freq, "min", None):
                details["min_frequency_mhz"] = round(float(freq.min), 3)
    except Exception:
        pass

    brand = platform.processor()
    if brand:
        details.setdefault("brand", brand)

    machine = platform.machine()
    if machine:
        details.setdefault("machine", machine)

    lscpu_output = _capture_command(["lscpu"])
    if lscpu_output:
        parsed = _parse_key_value_output(lscpu_output)
        if parsed:
            details["lscpu"] = parsed

    return details


def _gpu_metadata() -> MutableMapping[str, Any]:
    details: MutableMapping[str, Any] = {}
    try:  # pragma: no cover - torch optional
        import torch

        cuda_version = getattr(torch.version, "cuda", None)
        if cuda_version:
            details["cuda_version"] = cuda_version
        if torch.cuda.is_available():
            details["gpus"] = [
                torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
            ]
    except Exception:
        pass

    query = _capture_command(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader",
        ]
    )
    if query:
        gpu_entries: list[dict[str, Any]] = []
        driver_version: str | None = None
        for line in query.splitlines():
            parts = [segment.strip() for segment in line.split(",")]
            if not parts:
                continue
            record: dict[str, Any] = {}
            if parts:
                record["name"] = parts[0]
            if len(parts) >= 2:
                record["memory_total"] = parts[1]
            if len(parts) >= 3:
                driver_version = driver_version or parts[2]
            if record:
                gpu_entries.append(record)
        if gpu_entries:
            details.setdefault("devices", gpu_entries)
        if driver_version:
            details.setdefault("driver_version", driver_version)
    return details


def environment_summary() -> dict[str, Any]:
    """Collect Git, hardware, package, and Python runtime metadata."""

    info: dict[str, Any] = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "pip_freeze": _pip_freeze(),
    }

    hardware: dict[str, Any] = {}

    cpu_info = _cpu_metadata()
    if cpu_info:
        hardware["cpu"] = cpu_info

    gpu_info = _gpu_metadata()
    if gpu_info:
        hardware["gpu"] = gpu_info
        if "cuda_version" in gpu_info:
            info.setdefault("cuda_version", gpu_info["cuda_version"])
        names: list[str] = []
        devices = gpu_info.get("devices")
        if isinstance(devices, list):
            for device in devices:
                if isinstance(device, Mapping):
                    name = device.get("name")
                    if name:
                        names.append(str(name))
        if not names:
            gpus = gpu_info.get("gpus")
            if isinstance(gpus, list):
                names = [str(item) for item in gpus if isinstance(item, str)]
        if names:
            info.setdefault("gpus", names)
    else:
        info.setdefault("gpus", [])

    if hardware:
        info["hardware"] = hardware
    commit = _git_commit()
    if commit:
        info["git_commit"] = commit
    try:  # pragma: no cover - optional deps
        from codex_ml.monitoring.codex_logging import _codex_sample_system

        info["system_metrics"] = _codex_sample_system()
    except Exception:
        pass
    return info


def _concise_summary(
    info: Mapping[str, Any],
    *,
    seed: int | None,
    command: str | None,
    extras: Mapping[str, Any] | None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "python": info.get("python"),
        "platform": info.get("platform"),
        "git_commit": info.get("git_commit"),
        "cuda_version": info.get("cuda_version"),
        "gpus": info.get("gpus"),
        "pip_freeze_count": len(info.get("pip_freeze", [])) if info.get("pip_freeze") else 0,
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat(),
    }
    if seed is not None:
        summary["seed"] = int(seed)
    if command:
        summary["command"] = command
    if extras:
        summary.update({k: v for k, v in extras.items() if v is not None})
    return {k: v for k, v in summary.items() if v not in (None, [], {})}


def export_environment(
    out_dir: Path | str,
    *,
    seed: int | None = None,
    command: str | None = None,
    extras: Mapping[str, Any] | None = None,
    summary_filename: str = DEFAULT_ENV_JSON,
    ndjson_filename: str = DEFAULT_ENV_NDJSON,
    freeze_filename: str = DEFAULT_PIP_FREEZE,
    stream: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    """Write reproducibility artefacts and return a concise summary."""

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    info = environment_summary()
    summary_path = out / summary_filename
    summary_path.write_text(json.dumps(info, indent=2, sort_keys=True), encoding="utf-8")

    freeze_lines = info.get("pip_freeze", []) or []
    freeze_path = out / freeze_filename
    if freeze_lines:
        freeze_path.write_text("\n".join(freeze_lines) + "\n", encoding="utf-8")
    else:  # ensure artefact exists even when empty
        freeze_path.write_text("", encoding="utf-8")

    concise = _concise_summary(info, seed=seed, command=command, extras=extras)
    ndjson_line = json.dumps(concise, sort_keys=True)
    ndjson_path = out / ndjson_filename
    ndjson_path.write_text(ndjson_line + "\n", encoding="utf-8")
    if stream is not None:
        stream(ndjson_line)
    return concise


def load_environment_summary(
    out_dir: Path | str, ndjson_filename: str = DEFAULT_ENV_NDJSON
) -> dict[str, Any]:
    """Load the concise environment summary previously written by :func:`export_environment`."""

    path = Path(out_dir) / ndjson_filename
    if not path.exists():
        return {}
    last_line: str | None = None
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line:
                last_line = line
    if not last_line:
        return {}
    try:
        return json.loads(last_line)
    except json.JSONDecodeError:
        return {}


def snapshot_hydra_config(
    cfg: DictConfig | Mapping[str, object],
    out_dir: Path,
    overrides: Sequence[str] | None = None,
) -> None:
    """Persist the effective Hydra configuration and environment details."""

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered_config: str
    if OmegaConf is not None:
        if isinstance(cfg, DictConfig):
            target = cfg
        else:
            target = OmegaConf.create(cfg)  # type: ignore[assignment]

        if hasattr(OmegaConf, "to_yaml"):
            rendered_config = OmegaConf.to_yaml(target)  # type: ignore[attr-defined]
        else:
            container = OmegaConf.to_container(target, resolve=True)
            rendered_config = _yaml_dumps(container)
    else:
        rendered_config = json.dumps(cfg, indent=2, sort_keys=True)

    (out_dir / "config.yaml").write_text(rendered_config)
    if overrides:
        (out_dir / "overrides.txt").write_text("\n".join(overrides))
    info = environment_summary()
    (out_dir / "provenance.json").write_text(json.dumps(info, indent=2))


__all__ = [
    "environment_summary",
    "export_environment",
    "load_environment_summary",
    "snapshot_hydra_config",
]
