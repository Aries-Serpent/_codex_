#!/usr/bin/env python3
"""Offline CI orchestration mirroring the PR & CI gates workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class Step:
    name: str
    command: list[str]
    description: str


DEFAULT_STEPS: tuple[Step, ...] = (
    Step("security", ["nox", "-s", "security"], "pip-audit, bandit, gitleaks"),
    Step("coverage", ["nox", "-s", "coverage"], "pytest with coverage artifacts"),
    Step("typecheck", ["nox", "-s", "typecheck"], "mypy summary"),
    Step("env-snapshot", ["nox", "-s", "env-snapshot"], "environment manifest"),
)


def _stream_process(cmd: list[str], log_file: Path) -> int:
    with log_file.open("w", encoding="utf-8") as handle:
        handle.write(f"# Command: {' '.join(cmd)}\n")
        handle.write(f"# Started: {datetime.utcnow().isoformat()}Z\n\n")
        handle.flush()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            handle.write(line)
        proc.wait()
        handle.write(f"\n# Completed with exit code {proc.returncode}\n")
        handle.flush()
        return proc.returncode


def run_steps(steps: Iterable[Step], *, output_dir: Path, dry_run: bool = False) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for step in steps:
        log_file = output_dir / f"{step.name}.log"
        print(f"\n=== [{step.name}] {step.description} ===")
        if dry_run:
            print(f"(dry-run) would execute: {' '.join(step.command)}")
            summary.append({"step": step.name, "status": "skipped", "log": str(log_file)})
            continue
        code = _stream_process(step.command, log_file)
        status = "ok" if code == 0 else "failed"
        summary.append({"step": step.name, "status": status, "log": str(log_file)})
        if code != 0:
            print(f"Step {step.name} failed (exit code {code}); aborting pipeline.")
            break
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline CI gates sequentially")
    parser.add_argument("--output", type=Path, default=Path("artifacts/offline_ci"), help="Directory for step logs")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--skip", action="append", default=[], help="Step name to skip (can be repeated)")
    parser.add_argument(
        "--steps",
        nargs="*",
        choices=[step.name for step in DEFAULT_STEPS],
        help="Subset of steps to execute (defaults to all)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = [step for step in DEFAULT_STEPS if (not args.steps or step.name in args.steps)]
    selected = [step for step in selected if step.name not in set(args.skip)]
    summary = run_steps(selected, output_dir=args.output, dry_run=args.dry_run)
    summary_path = args.output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary written to {summary_path}")
    failed = [item for item in summary if item["status"] == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

