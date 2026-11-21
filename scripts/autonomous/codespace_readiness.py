"""Read-only Codespace shutdown and autonomous-restart readiness audit."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP_PROCESS_MARKERS = (
    "cognitive_app.src.server.cli_api_server:app",
    "vite",
    "playwright",
    "scripts/autonomous/mcp_server.py",
    "scripts/autonomous/codespace_keepalive.py",
)
SENSITIVE_TEMP_NAMES = {".env", ".env-secrets", "mcp.sock"}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--no-pager", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def worktree_state(repo: Path) -> dict[str, Any]:
    status = run_git(repo, "status", "--porcelain=v2", "--untracked-files=all")
    head = run_git(repo, "rev-parse", "HEAD")
    branch = run_git(repo, "branch", "--show-current")
    upstream = run_git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    divergence = None
    if upstream.returncode == 0:
        counts = run_git(
            repo, "rev-list", "--left-right", "--count", f"HEAD...{upstream.stdout.strip()}"
        )
        if counts.returncode == 0:
            ahead, behind = (int(value) for value in counts.stdout.split())
            divergence = {"ahead": ahead, "behind": behind}

    operation_state = "none"
    for ref, label in (("MERGE_HEAD", "merge"), ("REBASE_HEAD", "rebase")):
        if run_git(repo, "rev-parse", "-q", "--verify", ref).returncode == 0:
            operation_state = label
            break
    git_dir = run_git(repo, "rev-parse", "--git-dir")
    if git_dir.returncode == 0 and operation_state == "none":
        git_path = Path(git_dir.stdout.strip())
        if not git_path.is_absolute():
            git_path = repo / git_path
        if (git_path / "CHERRY_PICK_HEAD").exists():
            operation_state = "cherry-pick"
        elif (git_path / "REVERT_HEAD").exists():
            operation_state = "revert"

    return {
        "path": str(repo),
        "branch": branch.stdout.strip() or None,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "upstream": upstream.stdout.strip() if upstream.returncode == 0 else None,
        "divergence": divergence,
        "dirty": bool(status.stdout.strip()),
        "status_entries": len(status.stdout.splitlines()),
        "operation_state": operation_state,
        "valid_git_repository": head.returncode == 0,
    }


def stash_count(repo: Path) -> int:
    result = run_git(repo, "stash", "list", "--format=%gd")
    return len(result.stdout.splitlines()) if result.returncode == 0 else 0


def listening_socket_inodes() -> dict[str, int]:
    inodes: dict[str, int] = {}
    for table in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        try:
            lines = table.read_text(encoding="utf-8").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) < 10 or fields[3] != "0A":
                continue
            try:
                port = int(fields[1].rsplit(":", 1)[1], 16)
                inodes[fields[9]] = port
            except (ValueError, IndexError):
                continue
    return inodes


def owned_processes(worktrees: list[Path]) -> list[dict[str, Any]]:
    roots = [path.resolve() for path in worktrees]
    socket_ports = listening_socket_inodes()
    findings: list[dict[str, Any]] = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            raw = (
                (proc / "cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", errors="replace")
            )
            cwd = Path((proc / "cwd").resolve())
        except (OSError, RuntimeError):
            continue
        marker = next((item for item in APP_PROCESS_MARKERS if item in raw), None)
        if marker is None or not any(cwd == root or root in cwd.parents for root in roots):
            continue
        ports: set[int] = set()
        try:
            for descriptor in (proc / "fd").iterdir():
                try:
                    target = descriptor.readlink().as_posix()
                except OSError:
                    continue
                if target.startswith("socket:[") and target.endswith("]"):
                    inode = target[8:-1]
                    if inode in socket_ports:
                        ports.add(socket_ports[inode])
        except OSError:
            pass
        findings.append(
            {
                "pid": int(proc.name),
                "kind": marker,
                "cwd": str(cwd),
                "ports": sorted(ports),
            }
        )
    return sorted(findings, key=lambda item: item["pid"])


def temporary_candidates(roots: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            if path.name in SENSITIVE_TEMP_NAMES or path.is_socket():
                continue
            try:
                candidates.append(
                    {
                        "path": str(path),
                        "kind": "directory" if path.is_dir() else "file",
                        "bytes": path.stat().st_size if path.is_file() else None,
                    }
                )
            except OSError:
                continue
    return candidates


def keepalive_status() -> dict[str, Any]:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts.autonomous.codespace_keepalive import read_status, runtime_dir_default

    return read_status(runtime_dir_default())


def build_report(worktrees: list[Path], temp_roots: list[Path]) -> dict[str, Any]:
    worktree_reports = [worktree_state(path) for path in worktrees]
    processes = owned_processes(worktrees)
    repository = worktrees[0] if worktrees else ROOT
    blockers: list[dict[str, str]] = []
    for state in worktree_reports:
        if not state["valid_git_repository"]:
            blockers.append({"code": "invalid_worktree", "path": state["path"]})
        if state["dirty"]:
            blockers.append({"code": "dirty_worktree", "path": state["path"]})
        if state["operation_state"] != "none":
            blockers.append({"code": "git_operation_active", "path": state["path"]})
        divergence = state["divergence"]
        if divergence and (divergence["ahead"] or divergence["behind"]):
            blockers.append({"code": "upstream_divergence", "path": state["path"]})
    if stash_count(repository):
        blockers.append({"code": "stashes_present", "path": str(repository)})
    for process in processes:
        blockers.append({"code": "repository_process_running", "path": process["cwd"]})

    return {
        "schema_version": 1,
        "generated_at": utc_timestamp(),
        "worktrees": worktree_reports,
        "stashes": stash_count(repository),
        "repository_processes": processes,
        "keepalive": keepalive_status(),
        "temporary_candidates": temporary_candidates(temp_roots),
        "blockers": blockers,
        "ready": not blockers,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", action="append", type=Path, dest="worktrees")
    parser.add_argument("--temp-root", action="append", type=Path, dest="temp_roots")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit the JSON report (default)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    worktrees = [path.resolve() for path in (args.worktrees or [ROOT])]
    temp_roots = [path.resolve() for path in (args.temp_roots or [Path("/tmp")])]
    report = build_report(worktrees, temp_roots)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 1 if args.strict and not report["ready"] else 0


if __name__ == "__main__":
    sys.exit(main())
