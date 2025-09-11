"""Compact the JSON ledger into monthly Parquet files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from . import ledger


def compact(path: Path = Path(".codex/ledger.jsonl")) -> List[Path]:
    """Validate the ledger and write monthly Parquet files.

    Returns a list of written Parquet paths.
    """
    ledger.verify_chain(path)
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("ledger is empty")
    out_dir = Path(".codex/warehouse")
    out_dir.mkdir(parents=True, exist_ok=True)
    buckets: dict[str, list[dict]] = {}
    for r in rows:
        ts = datetime.fromisoformat(r["ts"].replace("Z", ""))
        r["ts"] = ts
        month = ts.strftime("%Y%m")
        buckets.setdefault(month, []).append(r)
    out_paths: List[Path] = []
    for month, entries in buckets.items():
        out_path = out_dir / f"ledger-{month}.parquet"
        pd.DataFrame(entries).to_parquet(out_path, index=False)
        out_paths.append(out_path)
    return out_paths


def _main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".codex/ledger.jsonl")
    ns = ap.parse_args()
    compact(Path(ns.path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
