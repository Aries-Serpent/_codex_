# BEGIN: CODEX_DATA_CLI
"""Command-line helpers for streaming data and collecting stats."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from codex.logging.structured_logger import logger

from .loaders import collect_stats, stream_paths


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Data loader CLI (JSONL/TXT streaming)")
    sub = ap.add_subparsers(dest="subcmd")

    # validate subcommand — quick ok/fail check on a data file
    val_p = sub.add_parser("validate", help="Validate a data file")
    val_p.add_argument("path", help="Input file path")

    # metadata subcommand — return basic metadata about a data file
    meta_p = sub.add_parser("metadata", help="Get metadata for a data file")
    meta_p.add_argument("path", help="Input file path")

    # legacy stream subcommand (original behaviour)
    stream_p = sub.add_parser("stream", help="Stream and collect stats (legacy)")
    stream_p.add_argument("--paths", nargs="+", required=True, help="Input file paths")
    stream_p.add_argument("--format", choices=["jsonl", "txt"], default="jsonl")
    stream_p.add_argument("--num-workers", type=int, default=0)
    stream_p.add_argument("--prefetch", type=int, default=0)
    stream_p.add_argument("--max-samples", type=int, default=None)
    stream_p.add_argument("--delimiter", default="\t")
    stream_p.add_argument("--out", default="output/data_stats.json")
    stream_p.add_argument("--stats-limit", type=int, default=None)

    # also support legacy flat --paths invocation (no subcommand)
    ap.add_argument("--paths", nargs="+", help="Input file paths (legacy)")
    ap.add_argument("--format", choices=["jsonl", "txt"], default="jsonl")
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--prefetch", type=int, default=0)
    ap.add_argument("--max-samples", type=int, default=None)
    ap.add_argument("--delimiter", default="\t")
    ap.add_argument("--out", default="output/data_stats.json")
    ap.add_argument("--stats-limit", type=int, default=None)

    args = ap.parse_args(argv)

    if args.subcmd == "validate":
        p = Path(args.path)
        ok = p.exists() and p.stat().st_size > 0
        logger.info(json.dumps({"ok": ok, "path": str(p)}))
        return

    if args.subcmd == "metadata":
        p = Path(args.path)
        suffix = p.suffix.lower()
        kind_map = {
            ".parquet": "parquet",
            ".arrow": "arrow",
            ".h5": "hdf5",
            ".hdf5": "hdf5",
        }
        kind = kind_map.get(suffix, "generic")
        print(
            json.dumps(
                {
                    "path": str(p),
                    "kind": kind,
                    "size": p.stat().st_size if p.exists() else 0,
                }
            )
        )
        return

    # legacy stream / flat --paths mode
    paths = getattr(args, "paths", None)
    if not paths:
        ap.print_help()
        raise SystemExit(2)

    rows = stream_paths(
        paths,
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
    logger.info(json.dumps({"ok": True, "out": str(out), "stats": stats}, indent=2))


if __name__ == "__main__":
    main()
# END: CODEX_DATA_CLI
