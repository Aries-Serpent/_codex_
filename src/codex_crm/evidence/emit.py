"""Evidence bundle helpers for offline reproducibility."""

from __future__ import annotations

import hashlib
import json
import platform
import time
from pathlib import Path

CONFIG_DIRS = (
    Path("config/zd"),
    Path("config/d365"),
    Path("config/powerautomate/templates"),
)


def sha256_file(path: Path) -> str:
    """Compute the SHA-256 hash of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_evidence(out_dir: str | Path, seeds: dict[str, int] | None = None) -> None:
    """Write the evidence bundle (seeds, environment, checksums, manifest)."""

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    (output / "seeds.json").write_text(
        json.dumps(seeds or {"rng": 1337}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    env = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "timestamp": time.time(),
    }
    (output / "env.json").write_text(json.dumps(env, indent=2, sort_keys=True), encoding="utf-8")

    checksums: dict[str, str] = {}
    for folder in CONFIG_DIRS:
        if folder.exists():
            for candidate in folder.rglob("*"):
                if candidate.is_file():
                    checksums[str(candidate)] = sha256_file(candidate)

    (output / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    manifest = {"timestamp": time.time(), "artifacts": sorted(checksums)}
    (output / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
