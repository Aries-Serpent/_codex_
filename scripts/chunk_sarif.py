#!/usr/bin/env python3
"""
Chunk SARIF files to comply with GitHub's 5000-result limit.

Usage:
    python scripts/chunk_sarif.py input.sarif output-dir/ --chunk-size 4999
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 4999  # GitHub limit: 5000, safety margin


def load_sarif(filepath: Path) -> dict[str, Any]:
    """Load and validate SARIF file."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    if "version" not in data or "runs" not in data:
        raise ValueError("Invalid SARIF file structure")

    return data


def count_results(sarif_data: dict[str, Any]) -> int:
    """Count total results across all runs."""
    return sum(len(run.get("results", [])) for run in sarif_data.get("runs", []))


def chunk_sarif(sarif_data: dict[str, Any], chunk_size: int) -> list[dict[str, Any]]:
    """
    Split SARIF into chunks of max chunk_size results.

    Strategy:
    1. Flatten all results from all runs with metadata
    2. Split into chunks of chunk_size
    3. Rebuild SARIF structure for each chunk
    """
    runs = sarif_data.get("runs", [])

    # Collect all results with run context
    all_results = []
    for run_idx, run in enumerate(runs):
        for result in run.get("results", []):
            all_results.append({"run_idx": run_idx, "run": run, "result": result})

    total = len(all_results)
    if total <= chunk_size:
        return [sarif_data]

    # Create chunks
    chunks = []
    num_chunks = (total + chunk_size - 1) // chunk_size

    for chunk_idx in range(num_chunks):
        start = chunk_idx * chunk_size
        end = min(start + chunk_size, total)
        chunk_results = all_results[start:end]

        # Rebuild SARIF structure
        chunk_runs = {}
        for item in chunk_results:
            run_idx = item["run_idx"]
            if run_idx not in chunk_runs:
                chunk_runs[run_idx] = {
                    "tool": item["run"]["tool"],
                    "results": [],
                    **{
                        k: v
                        for k, v in item["run"].items()
                        if k in ["invocations", "properties", "taxonomies", "artifacts"]
                    },
                }
            chunk_runs[run_idx]["results"].append(item["result"])

        chunks.append(
            {
                "version": sarif_data["version"],
                "$schema": sarif_data.get(
                    "$schema",
                    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
                ),
                "runs": list(chunk_runs.values()),
                **({k: v for k, v in sarif_data.items() if k == "properties"}),
            }
        )

        logger.info(f"Chunk {chunk_idx + 1}/{num_chunks}: {end - start} results")

    return chunks


def save_chunks(chunks: list[dict[str, Any]], output_dir: Path, base_name: str) -> list[Path]:
    """Save chunks to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    for idx, chunk in enumerate(chunks):
        name = (
            f"{base_name}.sarif"
            if len(chunks) == 1
            else f"{base_name}-chunk-{idx + 1:03d}.sarif"
        )
        path = output_dir / name

        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2)

        logger.info(f"Saved {path} ({count_results(chunk)} results)")
        saved.append(path)

    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Chunk SARIF files for GitHub upload")
    parser.add_argument("input", type=Path, help="Input SARIF file")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--base-name", default="chunked")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    sarif_data = load_sarif(args.input)
    total = count_results(sarif_data)
    logger.info(f"Input: {total} results")

    if total > args.chunk_size:
        logger.warning(f"Exceeds limit ({args.chunk_size}), chunking required")

    chunks = chunk_sarif(sarif_data, args.chunk_size)
    saved = save_chunks(chunks, args.output_dir, args.base_name)

    print(f"\n{'='*60}")
    print("SARIF Chunking Summary")
    print(f"{'='*60}")
    print(f"Input:  {args.input} ({total} results)")
    print(f"Chunks: {len(chunks)}")
    print(f"Output: {args.output_dir}")
    for idx, path in enumerate(saved, 1):
        print(f"  {idx}. {path.name} ({count_results(chunks[idx-1])} results)")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
