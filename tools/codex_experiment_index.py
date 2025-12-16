#!/usr/bin/env python
"""Index experiment metadata under a runs directory."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class RunRecord:
    run_id: str
    meta_path: str
    meta: Dict[str, object]


def _load_meta(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_index(runs_root: Path) -> Dict[str, object]:
    runs: List[RunRecord] = []
    for meta_file in sorted(
        list(runs_root.rglob("meta.json")) + list(runs_root.rglob("experiment_meta.json"))
    ):
        run_id = meta_file.parent.name
        runs.append(
            RunRecord(
                run_id=run_id,
                meta_path=str(meta_file.relative_to(runs_root)),
                meta=_load_meta(meta_file),
            )
        )
    return {"runs_root": str(runs_root), "runs": runs}


def _write_json(index: Dict[str, object], path: Path) -> None:
    payload = {
        "runs_root": index["runs_root"],
        "runs": [record.__dict__ for record in index["runs"]],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(index: Dict[str, object], path: Path) -> None:
    lines = [
        "# Experiment Index",
        "",
        f"Runs root: `{index['runs_root']}`",
        "",
        "| Run ID | Meta Path |",
        "| --- | --- |",
    ]
    for record in index["runs"]:
        lines.append(f"| {record.run_id} | {record.meta_path} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Index experiment metadata under runs/.")
    parser.add_argument(
        "--runs-dir", type=Path, default=Path("runs"), help="Root directory containing run outputs."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("codex_experiment_index.json"),
        help="JSON output path.",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=Path("codex_experiment_index.md"),
        help="Markdown output path.",
    )
    args = parser.parse_args(argv)

    runs_root = args.runs_dir.expanduser().resolve()
    runs_root.mkdir(parents=True, exist_ok=True)

    index = build_index(runs_root)
    json_out = args.json_out.expanduser().resolve()
    md_out = args.md_out.expanduser().resolve()
    _write_json(index, json_out)
    _write_markdown(index, md_out)
    print(f"Wrote experiment index to {json_out} and {md_out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
