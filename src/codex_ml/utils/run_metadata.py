from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any


def _sha256_file(path: Path) -> str | None:
    try:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 16), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return sha.strip()
    return None


def _lock_digest(root: Path) -> str | None:
    for candidate in ("uv.lock", "uv.lock.json"):
        lock_path = root / candidate
        if lock_path.exists():
            return _sha256_file(lock_path)
    return None


def collect_run_metadata(project_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root or ".").resolve()
    metadata: dict[str, Any] = {
        "python": ".".join(map(str, sys.version_info[:3])),
        "platform": platform.platform(),
        "git_sha": _git_sha(),
        "lock_sha256": _lock_digest(root),
        "env": {
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
            "CODEX_AUDIT": os.environ.get("CODEX_AUDIT"),
            "CODEX_DDP": os.environ.get("CODEX_DDP"),
        },
    }
    return metadata


def write_run_manifest(directory: str | Path, payload: dict[str, Any]) -> None:
    try:
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        manifest = target_dir / "run_manifest.json"
        manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        return
