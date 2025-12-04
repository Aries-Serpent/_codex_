#!/usr/bin/env python
"""Local gate runner for lightweight validation.

Gates are shell commands (e.g., pytest targets) defined in a YAML file. The
runner executes each gate sequentially, capturing stdout/stderr and emitting a
JSON summary. A Markdown table is also produced for quick inspection.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

import yaml


@dataclass
class GateCommand:
    name: str
    cmd: Sequence[str]


@dataclass
class GateResult:
    name: str
    cmd: Sequence[str]
    returncode: int
    stdout: str
    stderr: str


def _load_gate_config(path: Path) -> List[GateCommand]:
    if not path.exists():
        return [GateCommand(name="echo-smoke", cmd=["python", "-c", "print('local gate ok')"])]

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    gate_entries = raw.get("gates", []) if isinstance(raw, dict) else []
    commands: List[GateCommand] = []
    for entry in gate_entries:
        name = entry.get("name") or entry.get("id") or "gate"
        cmd = entry.get("cmd") or entry.get("command") or entry.get("run")
        if not cmd:
            continue
        if isinstance(cmd, str):
            stripped = cmd.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                inner = stripped[1:-1]
                cmd_list = [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
            else:
                cmd_list = shlex.split(cmd)
        else:
            cmd_list = list(cmd)
        commands.append(GateCommand(name=name, cmd=cmd_list))
    if not commands:
        commands.append(GateCommand(name="echo-smoke", cmd=["python", "-c", "print('local gate ok')"]))
    return commands


def _run_command(command: Sequence[str], repo_root: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    try:
        return subprocess.run(command, cwd=str(repo_root), check=False, capture_output=True, text=True, env=env)
    except TypeError:
        return subprocess.run(command, check=False)  # type: ignore[arg-type]


def run_gates(repo_root: Path, commands: List[GateCommand]) -> Dict[str, object]:
    results: List[GateResult] = []
    overall_rc = 0
    for command in commands:
        proc = _run_command(command.cmd, repo_root)
        rc = proc.returncode
        if rc != 0:
            overall_rc = rc
        stdout = getattr(proc, "stdout", "") or ""
        stderr = getattr(proc, "stderr", "") or ""
        results.append(
            GateResult(
                name=command.name,
                cmd=list(command.cmd),
                returncode=rc,
                stdout=stdout,
                stderr=stderr,
            )
        )
    return {"overall_returncode": overall_rc, "results": [r.__dict__ for r in results]}


def _write_markdown(summary: Dict[str, object], path: Path) -> None:
    lines = ["# Local Gate Report", "", "| Gate | Return Code |", "| --- | --- |"]
    for result in summary.get("results", []):
        name = result.get("name", "")
        rc = result.get("returncode", "")
        lines.append(f"| {name} | {rc} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local gate commands and capture a report.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root for running commands.")
    parser.add_argument("--config", type=Path, default=Path("codex_local_gate.yaml"), help="YAML file defining gates.")
    parser.add_argument("--json-out", type=Path, default=Path("codex_local_gate_report.json"), help="JSON summary output path.")
    parser.add_argument("--md-out", type=Path, default=Path("codex_local_gate_report.md"), help="Markdown summary output path.")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.expanduser().resolve()
    commands = _load_gate_config(args.config.expanduser())
    summary = run_gates(repo_root, commands)

    json_out = args.json_out.expanduser().resolve()
    json_out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    _write_markdown(summary, args.md_out.expanduser().resolve())
    print(f"Wrote local gate report to {json_out}")
    return int(summary.get("overall_returncode", 0) or 0)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
