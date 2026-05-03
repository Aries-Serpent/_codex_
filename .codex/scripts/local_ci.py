#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Step:
    name: str
    command: Sequence[str]
    description: str = ""
    env: Mapping[str, str] | None = None

    def render(self) -> str:
        shell = " ".join(shlex.quote(arg) for arg in self.command)
        return f"{self.name}: {shell}"


DEFAULT_STEPS: tuple[Step, ...] = (
    Step(
        name="pre-commit",
        command=("pre-commit", "run", "--all-files"),
        description="Formatters, linters, and secret scanning.",
    ),
    Step(
        name="tests",
        command=("nox", "-s", "tests"),
        description="Pytest with plugin autoload disabled for determinism.",
        env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    ),
    Step(
        name="reasoning",
        command=(
            "python",
            "-m",
            "codex_ml.eval.evaluator",
            "reasoning-suite",
            "--config",
            "configs/evaluation/reasoning/proof.yaml",
            "--config",
            "configs/evaluation/reasoning/math.yaml",
            "--config",
            "configs/evaluation/reasoning/tools.yaml",
            "--threshold",
            "reasoning/theorem_accuracy>=1.0",
            "--threshold",
            "reasoning/math_verification>=1.0",
            "--threshold",
            "reasoning/tool_audit>=1.0",
        ),
        description="Curated reasoning probes (proofs, math, and tool audits).",
    ),
    Step(
        name="gates",
        command=("nox", "-s", "gates"),
        description="Structure, schema validation, and evaluator smoke checks.",
        env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    ),
)

OPTIONAL_STEPS: tuple[Step, ...] = (
    Step(
        name="lint",
        command=("nox", "-s", "lint"),
        description="Ruff + Black + import sorting.",
    ),
    Step(
        name="typecheck",
        command=("nox", "-s", "typecheck"),
        description="Static typing with mypy.",
    ),
)


def build_steps(
    *,
    fast: bool = False,
    include_optional: bool = False,
    skip: Iterable[str] | None = None,
) -> list[Step]:
    skip_set = {name.strip().lower() for name in (skip or []) if name.strip()}
    steps: list[Step] = []
    base = DEFAULT_STEPS[:2] if fast else DEFAULT_STEPS
    for step in base:
        if step.name.lower() not in skip_set:
            steps.append(step)
    if include_optional:
        for step in OPTIONAL_STEPS:
            if step.name.lower() not in skip_set:
                steps.append(step)
    return steps


def _execute_step(step: Step) -> int:
    env = os.environ.copy()
    if step.env:
        env.update({key: str(value) for key, value in step.env.items()})
    print(f"[local-ci] >>> {step.render()}", flush=True)
    process = subprocess.run(step.command, env=env)
    return int(process.returncode)


def run_steps(
    steps: Sequence[Step],
    *,
    fail_fast: bool = False,
    runner: Callable[[Step], int] | None = None,
) -> tuple[int, list[tuple[Step, int]]]:
    results: list[tuple[Step, int]] = []
    status = 0
    execute = runner or _execute_step
    for step in steps:
        code = execute(step)
        results.append((step, code))
        if code != 0 and status == 0:
            status = code
        if code != 0 and fail_fast:
            break
    return status, results


def _render_summary(results: Sequence[tuple[Step, int]]) -> str:
    lines = []
    for step, code in results:
        state = "ok" if code == 0 else f"failed ({code})"
        lines.append(f"{step.name:<12} {state}")
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the standard Codex quality gates in sequence."
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip the structural gates (run pre-commit and tests only).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Include lint and typecheck nox sessions after the core gates.",
    )
    parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="STEP",
        help="Skip a named step (repeatable).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved commands without executing them.",
    )
    parser.add_argument(
        "--list", action="store_true", help="Show the resolved step list and exit."
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Execute all steps even if one fails (default is fail-fast).",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Working directory for the commands (defaults to current directory).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    steps = build_steps(fast=args.fast, include_optional=args.full, skip=args.skip)
    if args.list:
        for step in steps:
            description = f"  # {step.description}" if step.description else ""
            print(f"{step.render()}{description}")
        return 0
    if args.dry_run:
        for step in steps:
            print(step.render())
        return 0

    runner = None
    if args.workspace:
        workspace = args.workspace.expanduser().resolve()

        def _runner(step: Step) -> int:
            env = os.environ.copy()
            if step.env:
                env.update({key: str(value) for key, value in step.env.items()})
            print(f"[local-ci] >>> {step.render()} (cwd={workspace})", flush=True)
            process = subprocess.run(step.command, cwd=str(workspace), env=env)
            return int(process.returncode)

        runner = _runner

    status, results = run_steps(
        steps, fail_fast=not args.continue_on_failure, runner=runner
    )
    print(_render_summary(results))
    return status


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["Step", "build_steps", "run_steps", "main"]
