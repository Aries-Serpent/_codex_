from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import time
from collections.abc import Iterable


def sha256_file(path: pathlib.Path) -> str:
    """Compute the SHA-256 checksum for ``path``."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _gather_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    if not root.exists():
        return []
    return (path for path in root.rglob("*") if path.is_file())


def write_evidence(out_dir: str, seeds: dict[str, int] | None = None) -> None:
    """Write a deterministic evidence bundle into ``out_dir``."""

    output = pathlib.Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    (output / "seeds.json").write_text(
        json.dumps(seeds or {"rng": 1337}, indent=2), encoding="utf-8"
    )

    env = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "time": time.time(),
    }
    (output / "env.json").write_text(json.dumps(env, indent=2), encoding="utf-8")

    checksum_targets = [
        pathlib.Path("config/zd"),
        pathlib.Path("config/d365"),
        pathlib.Path("config/powerautomate/templates"),
    ]
    checksums = {}
    for root in checksum_targets:
        for file_path in _gather_files(root):
            checksums[str(file_path)] = sha256_file(file_path)
    (output / "checksums.json").write_text(json.dumps(checksums, indent=2), encoding="utf-8")

    manifest = {
        "ts": time.time(),
        "artifacts": sorted(checksums.keys()),
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
