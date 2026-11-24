#!/usr/bin/env python3
"""Atomic agent handoff writer for repository continuity."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from scripts.ci.copilot_agent_task import HandoffState, utc_now


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_handoff(
    record: Mapping[str, Any],
    *,
    repo_root: Path | str | None = None,
    state_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Persist an atomic handoff record and return the written payload."""
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    state = Path(state_dir) if state_dir is not None else root / ".codex"
    handoff = HandoffState(state_dir=state)
    payload = dict(record)
    payload.setdefault("created_at", utc_timestamp())
    payload.setdefault("updated_at", utc_now())
    payload.setdefault("schema_version", 1)
    return handoff.update(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write an atomic agent handoff record")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--state-dir", default="")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--objective", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--pr", dest="pr_number", default="")
    parser.add_argument("--last-sha", default="")
    parser.add_argument("--next-objective", default="")
    parser.add_argument("--stop-conditions", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    state_dir = Path(args.state_dir) if args.state_dir else repo_root / ".codex"
    record = {
        "task_id": args.task_id,
        "objective": args.objective,
        "branch": args.branch,
        "pr_number": args.pr_number,
        "last_verified_sha": args.last_sha,
        "next_objective": args.next_objective,
        "stop_conditions": args.stop_conditions,
    }
    result = write_handoff(record, repo_root=repo_root, state_dir=state_dir)
    if args.json:
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    else:
        print(str(state_dir / "copilot_agent_task_handoff.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
