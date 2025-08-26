# BEGIN: CODEX_DATA_CLI
"""Command-line helpers for streaming data and collecting stats."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .loaders import collect_stats, stream_paths


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Data loader CLI (JSONL/TXT streaming)")
    ap.add_argument("--paths", nargs="+", required=True, help="Input file paths")
    ap.add_argument("--format", choices=["jsonl", "txt"], default="jsonl")
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--prefetch", type=int, default=0)
    ap.add_argument("--max-samples", type=int, default=None)
    ap.add_argument("--delimiter", default="\t")
    ap.add_argument("--out", default="output/data_stats.json")
    ap.add_argument(
        "--stats-limit", type=int, default=None, help="Limit when computing stats"
    )
    args = ap.parse_args(argv)

    rows = stream_paths(
        args.paths,
        fmt=args.format,
        num_workers=args.num_workers,
        prefetch=args.prefetch,
        max_samples=args.max_samples,
        delimiter=args.delimiter,
    )
    stats = collect_stats(rows, sample_limit=args.stats_limit)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "stats": stats}, indent=2))


if __name__ == "__main__":
    main()
# END: CODEX_DATA_CLI
