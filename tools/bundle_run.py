"""Create compressed run bundles and log them to the ledger."""
from __future__ import annotations

import argparse
import tarfile
from datetime import datetime
from pathlib import Path

import zstandard as zstd

from . import ledger


def bundle_run(paths: list[str], run_id: str | None = None, level: int = 6) -> Path:
    """Bundle ``paths`` into ``.codex/bundles/{run_id}.tar.zst``.

    Parameters
    ----------
    paths:
        Files or directories to include.
    run_id:
        Identifier for this run. If omitted, a timestamp is used.
    level:
        Zstandard compression level.
    """
    run_id = run_id or datetime.utcnow().strftime("%Y%m%d%H%M%S")
    out_dir = Path(".codex/bundles")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{run_id}.tar.zst"
    with out_path.open("wb") as fh:
        cctx = zstd.ZstdCompressor(level=level).stream_writer(fh)
        with tarfile.open(fileobj=cctx, mode="w|") as tar:
            for p in paths:
                tar.add(p, arcname=Path(p).name)
        cctx.flush(zstd.FLUSH_FRAME)
    ledger.append_event({
        "run_id": run_id,
        "event": "bundle",
        "status": "ok",
        "data": {"path": str(out_path)},
    })
    return out_path


def _main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--run-id")
    ap.add_argument("--level", type=int, default=6)
    ns = ap.parse_args()
    bundle_run(ns.paths, ns.run_id, ns.level)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
