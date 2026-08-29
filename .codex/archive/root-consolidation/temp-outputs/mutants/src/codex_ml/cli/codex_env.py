"""Unified Codex environment CLI for local orchestration."""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import Optional


def _run(cmd: str, cwd: Path) -> int:
    proc = subprocess.run(shlex.split(cmd), cwd=str(cwd), check=False)
    return proc.returncode


def _cmd_health(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    return _run("python -m codex_ml.cli.env_check", root)


def _cmd_task_sequence(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    yaml_path = args.yaml or "codex_task_sequence.yaml"
    change_log = args.change_log or "codex_change_log.md"
    errors = args.errors or "codex_error_questions.md"
    cmd = (
        "python tools/codex_task_sequence_runner.py "
        f"--yaml {yaml_path} --repo-root . "
        f"--change-log {change_log} --errors {errors}"
    )
    return _run(cmd, root)


def _cmd_mltests(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    parts: list[str] = ["python tools/codex_mltest_runner.py"]
    if args.category:
        for cat in args.category:
            parts.append(f"--category {cat}")
    if args.json_summary:
        parts.append(f"--json-summary {args.json_summary}")
    cmd = " ".join(parts)
    return _run(cmd, root)


def _cmd_bundle(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    audit = args.audit or "_codex_status_update-2025-11-27.md"
    manifest = args.manifest_out or "codex_reproducibility_manifest.json"
    cmd = (
        "python tools/codex_reproducibility_bundle.py "
        f"--repo-root . --audit {audit} --manifest-out {manifest}"
    )
    return _run(cmd, root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified Codex environment CLI for local orchestration."
    )
    parser.add_argument("--repo-root", type=str, default=".", help="Repository root (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    ph = sub.add_parser("health", help="Run env & security health check.")
    ph.set_defaults(func=_cmd_health)

    pts = sub.add_parser("task-sequence", help="Run codex_task_sequence.yaml")
    pts.add_argument("--yaml", type=str, default="codex_task_sequence.yaml")
    pts.add_argument("--change-log", type=str, default="codex_change_log.md")
    pts.add_argument("--errors", type=str, default="codex_error_questions.md")
    pts.set_defaults(func=_cmd_task_sequence)

    pmt = sub.add_parser("mltests", help="Run ML Test Score categories")
    pmt.add_argument(
        "--category",
        "-c",
        action="append",
        default=None,
        help="Category to run (repeatable). If omitted, all categories run.",
    )
    pmt.add_argument(
        "--json-summary",
        type=str,
        default="codex_mltest_summary.json",
        help="Summary JSON output (default: codex_mltest_summary.json)",
    )
    pmt.set_defaults(func=_cmd_mltests)

    pb = sub.add_parser("bundle", help="Generate reproducibility bundle manifest")
    pb.add_argument(
        "--audit",
        type=str,
        default="_codex_status_update-2025-11-27.md",
        help="Audit filename (default: _codex_status_update-2025-11-27.md)",
    )
    pb.add_argument(
        "--manifest-out",
        type=str,
        default="codex_reproducibility_manifest.json",
        help="Manifest output path (default: codex_reproducibility_manifest.json)",
    )
    pb.set_defaults(func=_cmd_bundle)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
