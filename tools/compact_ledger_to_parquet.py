"""Compact the JSON ledger into monthly Parquet files."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import ledger


def compact(path: Path = Path(".codex/ledger.jsonl")) -> Path:
    """Validate the ledger and write a monthly Parquet file."""
    ledger.verify_chain(path)
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("ledger is empty")
    for r in rows:
        r["ts"] = datetime.fromisoformat(r["ts"].replace("Z", ""))
    month = rows[0]["ts"].strftime("%Y%m")
    out_dir = Path(".codex/warehouse")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ledger-{month}.parquet"
    pd.DataFrame(rows).to_parquet(out_path, index=False)
    return out_path


def _main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".codex/ledger.jsonl")
    ns = ap.parse_args()
    compact(Path(ns.path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
