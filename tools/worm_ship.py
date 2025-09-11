"""Optional WORM archive shipping to object storage.

Disabled unless CODEX_ENABLE_WORM=1 and CODEX_WORM_BUCKET is set.
"""
from __future__ import annotations

import os
from pathlib import Path

try:  # optional dependency
    import boto3
except Exception:  # pragma: no cover
    boto3 = None


def ship(path: Path) -> None:
    bucket = os.environ.get("CODEX_WORM_BUCKET")
    if not bucket or os.environ.get("CODEX_ENABLE_WORM") != "1":
        print("[worm] disabled")
        return
    if boto3 is None:
        raise RuntimeError("boto3 required for WORM shipping")
    s3 = boto3.client("s3")
    key = path.name
    s3.upload_file(str(path), bucket, key, ExtraArgs={"ObjectLockMode": "COMPLIANCE"})


def _main() -> int:
    p = Path(".codex").glob("bundles/*.tar.zst")
    for path in p:
        ship(path)
    for path in Path(".codex/warehouse").glob("*.parquet"):
        ship(path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
