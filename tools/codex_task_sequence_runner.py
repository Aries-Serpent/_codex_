#!/usr/bin/env python
"""codex_task_sequence_runner.py

Execute codex_task_sequence.yaml and record:
- codex_change_log.md : pipe table of steps and outcomes
- codex_error_questions.md : structured error questions for ChatGPT @codex

The runner is intentionally simple:
- YAML shape:

  codex_task_sequence:
    metadata: {...}
    phases:
      - id: 2
        name: Search & Mapping
        steps:
          - id: "2.4"
            description: ...
            actions: ["python ...", ...]
            on_error:
              strategy: record_and_continue

- Strategies: record_and_stop | record_and_continue
"""
from __future__ import annotations

import argparse
import datetime as dt
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


CHANGE_LOG_HEADER = "| timestamp | phase_id | step_id | status | details |\n"
CHANGE_LOG_RULE = "|-----------|---------|---------|--------|---------|\n"


@dataclass
class StepResult:
    phase_id: str
    step_id: str
    status: str
    details: str


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.")
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected YAML structure in {path}")
    return data


def _append_change_log(change_log: Path, result: StepResult) -> None:
    change_log.parent.mkdir(parents=True, exist_ok=True)
    if not change_log.exists():
        change_log.write_text(CHANGE_LOG_HEADER + CHANGE_LOG_RULE, encoding="utf-8")
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"| {ts} | {result.phase_id} | {result.step_id} | {result.status} | {result.details} |\n"
    with change_log.open("a", encoding="utf-8") as f:
        f.write(line)


def _append_error_question(
    error_file: Path,
    phase_id: str,
    step_id: str,
    description: str,
    command: str,
    rc: int,
    stderr: str,
) -> None:
    error_file.parent.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = (
        f"> Question for ChatGPT @codex {ts}:\n"
        f"> While performing [{phase_id}.{step_id}:{description}], "
        f"encountered the following error:\n"
        f"> Return code: {rc}\n"
        f"> Command: `{command}`\n"
        f"> Stderr (truncated):\n"
        f"> {stderr[:800]}\n\n"
        f"> Context: codex_task_sequence_runner executing codex_task_sequence.yaml.\n"
        f"> What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    with error_file.open("a", encoding="utf-8") as f:
        f.write(block)


def _run_action(
    cmd: str,
    cwd: Path,
    phase_id: str,
    step_id: str,
    description: str,
    change_log: Path,
    error_file: Path,
    on_error_strategy: str,
    dry_run: bool = False,
) -> bool:
    if dry_run:
        _append_change_log(
            change_log,
            StepResult(
                phase_id=phase_id,
                step_id=step_id,
                status="dry_run",
                details=f"Would run: {cmd}",
            ),
        )
        return True

    try:
        proc = subprocess.run(
            shlex.split(cmd),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - rare failures
        stderr = repr(exc)
        _append_change_log(
            change_log,
            StepResult(
                phase_id=phase_id,
                step_id=step_id,
                status="error",
                details=f"Exception: {exc}",
            ),
        )
        _append_error_question(
            error_file=error_file,
            phase_id=phase_id,
            step_id=step_id,
            description=description,
            command=cmd,
            rc=-1,
            stderr=stderr,
        )
        return on_error_strategy != "record_and_stop"

    if proc.returncode == 0:
        _append_change_log(
            change_log,
            StepResult(
                phase_id=phase_id,
                step_id=step_id,
                status="ok",
                details=f"Command: {cmd}",
            ),
        )
        return True

    stderr = (proc.stderr or "")[:800]
    _append_change_log(
        change_log,
        StepResult(
            phase_id=phase_id,
            step_id=step_id,
            status="error",
            details=f"Command failed rc={proc.returncode}",
        ),
    )
    _append_error_question(
        error_file=error_file,
        phase_id=phase_id,
        step_id=step_id,
        description=description,
        command=cmd,
        rc=proc.returncode,
        stderr=stderr,
    )
    return on_error_strategy != "record_and_stop"


def run_sequence(
    repo_root: Path,
    sequence_path: Path,
    change_log: Path,
    error_file: Path,
    dry_run: bool = False,
) -> None:
    data = _load_yaml(sequence_path)
    seq = data.get("codex_task_sequence")
    if not isinstance(seq, dict):
        raise ValueError("YAML missing 'codex_task_sequence' root object")
    phases = seq.get("phases") or []
    if not isinstance(phases, list):
        raise ValueError("Expected list under 'phases'")

    for phase in phases:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("id", "")).strip()
        steps = phase.get("steps") or []
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip()
            description = str(step.get("description", "")).strip()
            actions = step.get("actions") or []
            on_error = step.get("on_error", {}) or {}
            strategy = str(on_error.get("strategy", "record_and_continue")).strip()
            if not phase_id or not step_id:
                continue
            for cmd in actions:
                ok = _run_action(
                    cmd=cmd,
                    cwd=repo_root,
                    phase_id=phase_id,
                    step_id=step_id,
                    description=description,
                    change_log=change_log,
                    error_file=error_file,
                    on_error_strategy=strategy,
                    dry_run=dry_run,
                )
                if not ok:
                    return


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run codex_task_sequence.yaml.")
    p.add_argument(
        "--yaml",
        type=str,
        default="codex_task_sequence.yaml",
        help="Path to codex_task_sequence.yaml (default: codex_task_sequence.yaml).",
    )
    p.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    p.add_argument(
        "--change-log",
        type=str,
        default="codex_change_log.md",
        help="Path to change log markdown (default: codex_change_log.md).",
    )
    p.add_argument(
        "--errors",
        type=str,
        default="codex_error_questions.md",
        help="Path to error questions markdown (default: codex_error_questions.md).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually execute commands, only record dry_run events.",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    yaml_path = Path(args.yaml).expanduser().resolve()
    change_log = Path(args.change_log).expanduser().resolve()
    errors = Path(args.errors).expanduser().resolve()
    run_sequence(
        repo_root=repo_root,
        sequence_path=yaml_path,
        change_log=change_log,
        error_file=errors,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
