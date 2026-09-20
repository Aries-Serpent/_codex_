#!/usr/bin/env python
"""Build a simple dataset index for local files.

The index is intended for quick inspection and reproducibility tracking. It
scans a data root (default: ``data``) and records recognized dataset-like
files, emitting both JSON and Markdown summaries.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatasetFile:
    path: str
    kind: str
    size_bytes: int


def _classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "ndjson"
    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"
    if suffix == ".parquet":
        return "parquet"
    return "unknown"


def build_index(data_root: Path) -> dict[str, list[DatasetFile]]:
    files: list[DatasetFile] = []
    for path in sorted(data_root.rglob("*")):
        if not path.is_file():
            continue
        files.append(
            DatasetFile(
                path=str(path.relative_to(data_root)),
                kind=_classify(path),
                size_bytes=path.stat().st_size,
            )
        )
    return {"root": str(data_root), "files": files}


def _write_json(index: dict[str, list[DatasetFile]], path: Path) -> None:
    payload = {
        "root": index["root"],
        "files": [file.__dict__ for file in index["files"]],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(index: dict[str, list[DatasetFile]], path: Path) -> None:
    lines = [
        "# Dataset Index",
        "",
        f"Root: `{index['root']}`",
        "",
        "| Path | Type | Size (bytes) |",
        "| --- | --- | --- |",
    ]
    for file in index["files"]:
        lines.append(f"| {file.path} | {file.kind} | {file.size_bytes} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate dataset index for a data root.")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("data"),
        help="Data directory to index (default: data).",
    )
    parser.add_argument(
        "--json-out", type=Path, default=Path("codex_dataset_index.json"), help="JSON output path."
    )
    parser.add_argument(
        "--md-out", type=Path, default=Path("codex_dataset_index.md"), help="Markdown output path."
    )
    args = parser.parse_args(argv)

    data_root = args.data_root.expanduser().resolve()
    data_root.mkdir(parents=True, exist_ok=True)

    index = build_index(data_root)

    json_out = args.json_out.expanduser().resolve()
    md_out = args.md_out.expanduser().resolve()
    _write_json(index, json_out)
    _write_markdown(index, md_out)
    print(f"Wrote dataset index to {json_out} and {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
