#!/usr/bin/env python
"""Unified Gap Pipeline CLI for _codex_.

This script runs the main gap-related tools in a single command:

1) Validate hardship map (if present).
2) Validate capability map (if present).
3) Build codex_gap_registry.yaml from the latest audit and logs.
4) Run coverage check (codex_yaml_gap_report.md).
5) Generate snapshot trends (codex_gap_trends.md).

It is intentionally linear and conservative: failures in validation cause a
non-zero exit code so they can be noticed in local runs.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import Optional


def _run(cmd: str, cwd: Path) -> None:
    proc = subprocess.run(shlex.split(cmd), cwd=str(cwd), check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the _codex_ gap pipeline.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--audit",
        type=str,
        default="_codex_status_update-2025-11-27.md",
        help="Audit markdown to use (default: _codex_status_update-2025-11-27.md).",
    )
    parser.add_argument(
        "--hardship",
        type=str,
        default="codex_hardship.yaml",
        help="Hardship metadata YAML (default: codex_hardship.yaml).",
    )
    parser.add_argument(
        "--cap-map",
        type=str,
        default="codex_capability_map.yaml",
        help="Capability map YAML (default: codex_capability_map.yaml).",
    )
    parser.add_argument(
        "--registry",
        type=str,
        default="codex_gap_registry.yaml",
        help="Output registry path (default: codex_gap_registry.yaml).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()

    hardship_path = root / args.hardship
    if hardship_path.exists():
        _run(f"python tools/codex_hardship_validate.py --path {args.hardship}", root)

    cap_map_path = root / args.cap_map
    if cap_map_path.exists():
        _run(f"python tools/codex_capability_map_validate.py --path {args.cap_map}", root)

    _run(
        "python tools/codex_gap_registry.py "
        f"--audit {args.audit} "
        "--change-log codex_change_log.md "
        "--errors codex_error_questions.md "
        f"--hardship {args.hardship} "
        f"--cap-map {args.cap_map} "
        f"--out {args.registry}",
        root,
    )

    _run(
        "python tools/codex_yaml_gap_check.py "
        f"--gaps {args.registry} "
        "--yaml codex_task_sequence.yaml "
        "--out codex_yaml_gap_report.md",
        root,
    )

    _run(
        "python tools/codex_gap_trends.py "
        f"--registry {args.registry} "
        "--out codex_gap_trends.md",
        root,
    )

    print("Gap pipeline completed successfully.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
