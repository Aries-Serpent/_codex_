from __future__ import annotations

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


@dataclass
class DVCStageProvenance:
    stage: str
    outs: dict[str, dict[str, Any]]
    deps: dict[str, dict[str, Any]]
    params: dict[str, Any]


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _config_fingerprint(cfg: DictConfig) -> str:
    container = _to_container(cfg)
    yml = yaml.safe_dump(container, sort_keys=True)
    return _sha256_bytes(yml.encode("utf-8"))


def _read_dvc_lock(lock_path: Path) -> dict[str, Any]:
    if not lock_path.exists():
        return {}
    with lock_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_dvc_stage(lock: dict[str, Any], stage: str = "prepare") -> DVCStageProvenance | None:
    stages = lock.get("stages") or {}
    s = stages.get(stage)
    if not s:
        return None
    outs_list = s.get("outs") or []
    deps_list = s.get("deps") or []
    params = (s.get("params") or {}).get("params.yaml", {})
    outs = {
        o["path"]: {k: v for k, v in o.items() if k != "path"} for o in outs_list if "path" in o
    }
    deps = {
        d["path"]: {k: v for k, v in d.items() if k != "path"} for d in deps_list if "path" in d
    }
    return DVCStageProvenance(stage=stage, outs=outs, deps=deps, params=params)


def write_provenance(cfg: DictConfig, stage: str = "prepare", out_dir: Path | None = None) -> Path:
    out_dir = out_dir or Path(".codex")
    out_dir.mkdir(parents=True, exist_ok=True)
    lock = _read_dvc_lock(Path("dvc.lock"))
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
    out_path = out_dir / "provenance.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return out_path
