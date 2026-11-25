#!/usr/bin/env python3
"""Canonical Codespace and Copilot Agent session continuity guard."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
HANDOFF_PATH = ROOT / ".codex" / "session_handoff.json"
CONTINUATION_PATH = ROOT / ".codex" / "NEXT_CONTINUATION_PROMPT.md"
CHECKPOINT_ROOT = ROOT / ".codex" / "checkpoints"
BUNDLE_ROOT = ROOT / ".codex" / "sandbox-bundles" / "codespace-session"
LOCAL_SESSION_STORE_NAMES = ("session-store.db",)

SENSITIVE_PATH_PARTS = (
    "credential",
    "private_key",
    "private-key",
    "token",
    "secret",
)
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--no-pager", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def git_value(repo: Path, *args: str) -> str | None:
    result = git(repo, *args)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def worktree_entries(repo: Path) -> dict[str, list[str]]:
    result = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    modified: list[str] = []
    created: list[str] = []
    deleted: list[str] = []
    if result.returncode != 0:
        return {"modified": modified, "created": created, "deleted": deleted}

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        code = line[:2]
        path = line[3:].strip()
        if not path:
            continue
        if "D" in code:
            deleted.append(path)
        elif code.startswith("??") or "A" in code:
            created.append(path)
        else:
            modified.append(path)
    return {
        "modified": sorted(set(modified)),
        "created": sorted(set(created)),
        "deleted": sorted(set(deleted)),
    }


def load_handoff() -> tuple[dict[str, Any] | None, str | None]:
    if not HANDOFF_PATH.is_file():
        return None, "missing"
    try:
        payload = json.loads(HANDOFF_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"
    if not isinstance(payload, dict):
        return None, "invalid_object"
    return payload, None


def sanitize_remote_url(remote: str | None) -> str | None:
    if not remote:
        return None
    if "://" not in remote:
        return remote
    scheme, remainder = remote.split("://", 1)
    if "@" not in remainder:
        return remote
    host_and_path = remainder.split("@", 1)[1]
    return f"{scheme}://{host_and_path}"


def origin_state(repo: Path) -> dict[str, str | None]:
    refs: dict[str, str | None] = {}
    for name in ("main", "0D_base_"):
        refs[name] = git_value(repo, "rev-parse", "--verify", f"origin/{name}")
    return refs


def readiness_report(repo: Path) -> dict[str, Any]:
    try:
        from scripts.autonomous.codespace_readiness import build_report

        return build_report([repo], [repo, Path("/tmp")])
    except Exception as exc:
        return {
            "schema_version": 1,
            "generated_at": utc_timestamp(),
            "ready": False,
            "blockers": [{"code": "readiness_unavailable", "path": str(repo)}],
            "error": type(exc).__name__,
        }


def find_latest_checkpoint(repo: Path, runtime_dir: Path) -> dict[str, Any] | None:
    candidates: list[Path] = []
    for root in (
        repo / ".codex" / "checkpoints",
        runtime_dir / "checkpoints",
    ):
        if root.is_dir():
            candidates.extend(root.rglob("checkpoint_cp_*.json"))
            candidates.extend(root.rglob("checkpoint_cp_*.json.gz"))
    for path in sorted(set(candidates), key=lambda item: item.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue
        checkpoint_id = path.name.replace("checkpoint_", "").rsplit(".", 1)[0]
        if path.suffix == ".gz":
            checkpoint_id = path.name.replace("checkpoint_", "").removesuffix(".json.gz")
        elif path.suffix == ".zst":
            checkpoint_id = path.name.replace("checkpoint_", "").removesuffix(".json.zst")
        else:
            checkpoint_id = path.name.replace("checkpoint_", "").removesuffix(".json")
        if checkpoint_id:
            return {
                "checkpoint_id": checkpoint_id,
                "path": str(path),
                "portable_path": (
                    str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path)
                ),
            }
    return None


def find_local_session_store(repo: Path) -> Path | None:
    candidates: list[Path] = []
    home = Path.home()
    candidates.extend(
        root / "User" / "globalStorage" / "github.copilot-chat" / name
        for root in (
            home / ".vscode-remote" / "data",
            home / ".config" / "Code",
            home / ".config" / "Code - OSS",
        )
        for name in LOCAL_SESSION_STORE_NAMES
    )
    candidates.append(repo / ".codex" / "session_logs.db")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def is_sensitive_path(relative_path: str) -> bool:
    lower = relative_path.lower()
    name = Path(lower).name
    if name == ".env":
        return True
    if name.startswith(".env."):
        return "example" not in name
    if any(part in lower for part in SENSITIVE_PATH_PARTS):
        return True
    if name.endswith(SENSITIVE_SUFFIXES):
        return True
    return False


def validate_bundle_paths(entries: dict[str, list[str]], repo: Path | None = None) -> list[str]:
    blocked: list[str] = []
    for path in entries["created"] + entries["modified"] + entries["deleted"]:
        if is_sensitive_path(path):
            blocked.append(path)

    if repo is not None:
        repo_resolved = repo.resolve()
        for path in entries["created"] + entries["modified"]:
            source = repo / path
            if source.is_symlink():
                blocked.append(f"symlink:{path}")
                continue
            if not source.exists():
                continue
            try:
                resolved = source.resolve(strict=True)
                resolved.relative_to(repo_resolved)
            except (FileNotFoundError, OSError, RuntimeError, ValueError):
                blocked.append(f"outside_repo:{path}")
    return sorted(set(blocked))


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_readiness_report(report: dict[str, Any]) -> dict[str, Any]:
    worktrees: list[dict[str, Any]] = []
    for state in report.get("worktrees", []):
        worktrees.append(
            {
                "path": state.get("path"),
                "branch": state.get("branch"),
                "head": state.get("head"),
                "upstream": state.get("upstream"),
                "divergence": state.get("divergence"),
                "dirty": state.get("dirty"),
                "status_entries": state.get("status_entries"),
                "operation_state": state.get("operation_state"),
            }
        )
    return {
        "schema_version": report.get("schema_version", 1),
        "generated_at": report.get("generated_at", utc_timestamp()),
        "ready": report.get("ready", False),
        "blockers": report.get("blockers", []),
        "worktrees": worktrees,
        "stashes": report.get("stashes", 0),
        "repository_processes": report.get("repository_processes", []),
        "keepalive": report.get("keepalive", {}),
    }


def build_handoff(
    repo: Path,
    *,
    checkpoint_id: str | None,
    checkpoint_path: str | None,
    active_issue: int | None,
    active_pr: int | None,
    completed: list[str],
    pending: list[str],
    objective: str,
    bundle_path: str | None,
    bundle_sha256: str | None,
) -> dict[str, Any]:
    entries = worktree_entries(repo)
    existing, _ = load_handoff()
    existing = existing if isinstance(existing, dict) else {}

    if active_issue is None:
        value = existing.get("active_issue")
        active_issue = value if isinstance(value, int) else None
    if active_pr is None:
        value = existing.get("active_pr")
        active_pr = value if isinstance(value, int) else None

    existing_completed = existing.get("completed_tasks")
    combined_completed = list(existing_completed) if isinstance(existing_completed, list) else []
    combined_completed.extend(completed)
    existing_pending = existing.get("pending_tasks")
    combined_pending = list(existing_pending) if isinstance(existing_pending, list) else []
    combined_pending.extend(pending)

    branch = git_value(repo, "branch", "--show-current")
    head = git_value(repo, "rev-parse", "HEAD")
    remote = git_value(repo, "config", "--get", "remote.origin.url")

    return {
        "schema_version": 2,
        "generated_at": utc_timestamp(),
        "repository": "Aries-Serpent/_codex_",
        "owner": "mbaetiong",
        "remote": sanitize_remote_url(remote),
        "branch": branch,
        "head": head,
        "origin_refs": origin_state(repo),
        "active_issue": active_issue,
        "active_pr": active_pr,
        "objective": objective,
        "completed_tasks": list(dict.fromkeys(str(item) for item in combined_completed)),
        "pending_tasks": list(dict.fromkeys(str(item) for item in combined_pending)),
        "files": {
            "modified": entries["modified"],
            "created": entries["created"],
            "deleted": entries["deleted"],
        },
        "checkpoint": {
            "checkpoint_id": checkpoint_id,
            "path": checkpoint_path,
        },
        "preservation_bundle": {
            "path": bundle_path,
            "sha256": bundle_sha256,
        },
        "validation": compact_readiness_report(readiness_report(repo)),
        "stop_conditions": [
            "kill switch enabled",
            "budget or rate limit exhausted",
            "live write scope unverified",
            "required checks failed or pending",
            "exact-SHA AI approval absent",
            "finding lacks reproducible evidence",
        ],
        "next_continuation_prompt": str(CONTINUATION_PATH.relative_to(repo)),
    }


def continuation_prompt(handoff: dict[str, Any]) -> str:
    origin = handoff.get("origin_refs") or {}
    checkpoint = handoff.get("checkpoint") or {}
    bundle = handoff.get("preservation_bundle") or {}
    pending = handoff.get("pending_tasks") or []
    completed = handoff.get("completed_tasks") or []

    pending_lines = "\n".join(f"- [ ] {item}" for item in pending) or "- [ ] None"
    completed_lines = "\n".join(f"- [x] {item}" for item in completed) or "- [x] None"

    pr_line = f"PR #{handoff['active_pr']}" if handoff.get("active_pr") else "No active PR"
    issue_line = (
        f"Issue #{handoff['active_issue']}" if handoff.get("active_issue") else "No active issue"
    )

    return f"""## Next Continuation Prompt

```text
Continue Aries-Serpent/_codex_ from {issue_line} and {pr_line}.

Objective:
{handoff.get('objective') or 'Resume the live repository objective.'}

Verified handoff state:
- Branch: {handoff.get('branch') or 'unknown'}
- HEAD: {handoff.get('head') or 'unknown'}
- origin/main: {origin.get('main') or 'unknown'}
- origin/0D_base_: {origin.get('0D_base_') or 'unknown'}
- Checkpoint: {checkpoint.get('checkpoint_id') or 'none'}
- Bundle: {bundle.get('path') or 'none'}

Completed:
{completed_lines}

Pending:
{pending_lines}

First checks:
1. Fetch origin and verify live branch, issue, PR, SHA, review, and check state.
2. Read .codex/session_handoff.json and .codex/NEXT_CONTINUATION_PROMPT.md.
3. Preserve dirty/untracked work; do not reset, stash, clean, rebase, or force-push.
4. Run strict readiness and verify the latest checkpoint or bundle before mutation.

Rules:
- No direct push to 0D_base_ or main.
- No merge, promotion, deployment, workflow dispatch, secret rotation, or issue/PR closure without live exact-SHA controls.
- Treat local or chat state as untrusted until verified against remote Git and GitHub state.
- Stop if signing, write scope, required checks, exact-SHA AI approval, or reproducible evidence is unavailable.

After each meaningful milestone:
1. Update .codex/session_handoff.json.
2. Create a checked continuation checkpoint.
3. Re-run strict readiness and secret checks.
4. Generate an updated Next Continuation Prompt.
```
"""


def write_handoff(
    repo: Path,
    *,
    checkpoint_id: str | None = None,
    checkpoint_path: str | None = None,
    active_issue: int | None = None,
    active_pr: int | None = None,
    completed: list[str] | None = None,
    pending: list[str] | None = None,
    objective: str = "Resume the live repository objective.",
    bundle_path: str | None = None,
    bundle_sha256: str | None = None,
) -> dict[str, Any]:
    handoff = build_handoff(
        repo,
        checkpoint_id=checkpoint_id,
        checkpoint_path=checkpoint_path,
        active_issue=active_issue,
        active_pr=active_pr,
        completed=completed or [],
        pending=pending or [],
        objective=objective,
        bundle_path=bundle_path,
        bundle_sha256=bundle_sha256,
    )
    atomic_json_write(HANDOFF_PATH, handoff)
    atomic_text_write(CONTINUATION_PATH, continuation_prompt(handoff))
    return handoff


def create_checkpoint(
    repo: Path,
    runtime_dir: Path,
    *,
    session_id: str,
    task: str,
    completed: list[str],
    pending: list[str],
    active_issue: int | None,
    active_pr: int | None,
    checkpoint_in_repo: bool,
) -> dict[str, Any]:
    try:
        from scripts.cognitive.session_checkpoint_manager import SessionCheckpointManager
    except ImportError as exc:
        return {"created": False, "error": f"checkpoint_manager_unavailable:{exc}"}

    checkpoint_root = CHECKPOINT_ROOT if checkpoint_in_repo else runtime_dir / "checkpoints"
    manager = SessionCheckpointManager(
        storage_path=str(checkpoint_root),
        compression_algorithm="gzip",
        compression_level=9,
    )
    entries = worktree_entries(repo)
    repo_state = {
        "branch": git_value(repo, "branch", "--show-current"),
        "head": git_value(repo, "rev-parse", "HEAD"),
        "origin_refs": origin_state(repo),
        "modified": entries["modified"],
        "created": entries["created"],
        "deleted": entries["deleted"],
    }
    try:
        meta = manager.create_checkpoint(
            session_id=session_id,
            agent_state={
                "agent_id": "copilot-codespace",
                "status": "in_progress",
                "cwd": str(repo),
            },
            memory_snapshot={"short_term_memory": [], "long_term_memory": [], "total_patterns": 0},
            execution_progress={
                "current_task": task,
                "completed_tasks": completed,
                "pending_tasks": pending,
                "task_completion_percent": 0.0,
            },
            repository_state=repo_state,
            context_state={
                "active_issue": active_issue,
                "active_pr": active_pr,
                "objective": task,
            },
            metadata={"active_issue": active_issue, "active_pr": active_pr},
            compress=True,
            lane_bucket="codespace-continuity",
            task_id=session_id,
            checkpoint_state="in_progress",
        )
    except Exception as exc:
        return {"created": False, "error": f"{type(exc).__name__}:{exc}"}

    return {
        "created": True,
        "checkpoint_id": meta.checkpoint_id,
        "path": meta.storage_path,
        "sha256": meta.checksum_sha256,
    }


def create_bundle(repo: Path) -> dict[str, Any]:
    entries = worktree_entries(repo)
    blocked = validate_bundle_paths(entries, repo)
    if blocked:
        return {
            "created": False,
            "reason": "sensitive_paths_detected",
            "blocked_paths": blocked,
        }

    try:
        from scripts.archive.git_patch_bundle import bundle_changes, verify_bundle

        bundle = bundle_changes(repo, BUNDLE_ROOT, "codespace-session-continuity")
        manifest = verify_bundle(bundle)
        return {
            "created": True,
            "path": str(bundle),
            "sha256": sha256_file(bundle),
            "manifest": manifest,
        }
    except ValueError as exc:
        return {"created": False, "reason": "no_git_changes", "error": str(exc)}
    except Exception as exc:
        return {"created": False, "reason": "bundle_failed", "error": type(exc).__name__}


def reindex_session_store(repo: Path, runtime_dir: Path) -> dict[str, Any]:
    store = find_local_session_store(repo)
    output = runtime_dir / "chronicle_search_index.json"
    if store is None:
        return {"reindexed": False, "reason": "session_store_missing", "output": str(output)}

    command = [
        sys.executable,
        "-m",
        "aries_serpent_core.cli",
        "chronicle",
        "reindex",
        "--database",
        str(store),
        "--output",
        str(output),
    ]
    result = subprocess.run(command, cwd=repo, check=False, capture_output=True, text=True)
    if result.returncode == 0:
        return {
            "reindexed": True,
            "database": str(store),
            "output": str(output),
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[-500:],
            "stderr": result.stderr.strip()[-500:],
        }
    return {
        "reindexed": False,
        "reason": "reindex_failed",
        "database": str(store),
        "output": str(output),
        "returncode": result.returncode,
        "stdout": result.stdout.strip()[-500:],
        "stderr": result.stderr.strip()[-500:],
    }


def status_report(repo: Path, runtime_dir: Path, refresh: bool = False) -> dict[str, Any]:
    if refresh:
        git(repo, "fetch", "--no-tags", "origin", "--prune")

    handoff, handoff_error = load_handoff()
    return {
        "schema_version": 2,
        "generated_at": utc_timestamp(),
        "repository": str(repo),
        "branch": git_value(repo, "branch", "--show-current"),
        "head": git_value(repo, "rev-parse", "HEAD"),
        "origin_refs": origin_state(repo),
        "worktree": worktree_entries(repo),
        "handoff": {
            "loaded": handoff is not None,
            "error": handoff_error,
            "schema_version": handoff.get("schema_version") if handoff else None,
            "branch": handoff.get("branch") if handoff else None,
            "head": handoff.get("head") if handoff else None,
        },
        "latest_checkpoint": find_latest_checkpoint(repo, runtime_dir),
        "readiness": readiness_report(repo),
        "continuation_prompt": str(CONTINUATION_PATH),
    }


def resume_report(repo: Path, runtime_dir: Path, checkpoint_id: str | None) -> dict[str, Any]:
    handoff, handoff_error = load_handoff()
    target_id = checkpoint_id
    if target_id is None and handoff:
        checkpoint = handoff.get("checkpoint")
        if isinstance(checkpoint, dict):
            target_id = checkpoint.get("checkpoint_id")

    if not target_id:
        latest = find_latest_checkpoint(repo, runtime_dir)
        if latest:
            target_id = latest["checkpoint_id"]

    if not target_id:
        return {
            "resumed": False,
            "mode": "cold_bootstrap",
            "handoff_error": handoff_error,
            "reason": "no_verified_checkpoint",
            "continuation_prompt": str(CONTINUATION_PATH),
        }

    for checkpoint_root in (
        runtime_dir / "checkpoints",
        repo / ".codex" / "checkpoints",
    ):
        try:
            from scripts.cognitive.session_checkpoint_manager import SessionCheckpointManager
            from scripts.cognitive.session_resume_engine import SessionResumeEngine

            manager = SessionCheckpointManager(
                storage_path=str(checkpoint_root), compression_algorithm="gzip"
            )
            try:
                validation = manager.validate_checkpoint(target_id, quick_check=False)
            except Exception:
                continue
            if not validation.is_valid:
                errors = [getattr(error, "message", str(error)) for error in validation.errors]
                return {
                    "resumed": False,
                    "mode": "cold_bootstrap",
                    "checkpoint_id": target_id,
                    "reason": "checkpoint_failed_validation",
                    "validation": {
                        "is_valid": validation.is_valid,
                        "recoverable": validation.recoverable,
                        "integrity_score": validation.integrity_score,
                        "errors": errors,
                    },
                    "continuation_prompt": str(CONTINUATION_PATH),
                }
            try:
                context = SessionResumeEngine(
                    checkpoint_manager=manager, enable_warmup=False
                ).warm_start(target_id)
            except Exception:
                continue
            return {
                "resumed": True,
                "mode": "checkpoint",
                "checkpoint_id": target_id,
                "session_id": context.session_id,
                "execution_progress": context.execution_progress,
                "repository_state": context.agent_state.get("repository_state", {}),
                "continuation_prompt": str(CONTINUATION_PATH),
            }
        except ImportError:
            break

    return {
        "resumed": False,
        "mode": "cold_bootstrap",
        "checkpoint_id": target_id,
        "reason": "checkpoint_not_restored",
        "continuation_prompt": str(CONTINUATION_PATH),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Report local and remote continuity state")
    status.add_argument("--refresh", action="store_true", help="Fetch origin refs before reporting")
    status.add_argument("--strict", action="store_true", help="Exit nonzero when blockers exist")
    status.add_argument("--json", action="store_true", help="Emit the JSON status report")
    status.add_argument("--runtime-dir", type=Path)

    checkpoint = subparsers.add_parser("checkpoint", help="Create a continuity checkpoint")
    checkpoint.add_argument("--session-id", default="codespace-session")
    checkpoint.add_argument("--task", default="Continue repository work")
    checkpoint.add_argument("--completed", action="append", default=[])
    checkpoint.add_argument("--pending", action="append", default=[])
    checkpoint.add_argument("--active-pr", type=int)
    checkpoint.add_argument("--active-issue", type=int)
    checkpoint.add_argument("--runtime-only", action="store_true")
    checkpoint.add_argument("--runtime-dir", type=Path)

    resume = subparsers.add_parser("resume", help="Restore the latest verified checkpoint")
    resume.add_argument("--checkpoint-id")
    resume.add_argument("--runtime-dir", type=Path)

    reindex = subparsers.add_parser("reindex", help="Rebuild the local Chronicle session index")
    reindex.add_argument("--runtime-dir", type=Path)

    closeout = subparsers.add_parser("closeout", help="Create the canonical closeout handoff")
    closeout.add_argument("--active-pr", type=int)
    closeout.add_argument("--active-issue", type=int)
    closeout.add_argument("--completed", action="append", default=[])
    closeout.add_argument("--pending", action="append", default=[])
    closeout.add_argument("--objective", default="Resume the live repository objective.")
    closeout.add_argument("--no-bundle", action="store_true")
    closeout.add_argument("--no-reindex", action="store_true")
    closeout.add_argument("--runtime-dir", type=Path)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime_dir_arg = getattr(args, "runtime_dir", None)
    runtime_dir = (
        runtime_dir_arg.expanduser().resolve()
        if isinstance(runtime_dir_arg, Path)
        else Path(os.environ.get("CODEX_RUNTIME_DIR") or (Path.home() / ".codex" / "runtime"))
        .expanduser()
        .resolve()
    )

    if args.command == "status":
        report = status_report(ROOT, runtime_dir, refresh=args.refresh)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if args.strict and not report["readiness"]["ready"] else 0

    if args.command == "checkpoint":
        checkpoint = create_checkpoint(
            ROOT,
            runtime_dir,
            session_id=args.session_id,
            task=args.task,
            completed=args.completed,
            pending=args.pending,
            active_issue=args.active_issue,
            active_pr=args.active_pr,
            checkpoint_in_repo=not args.runtime_only,
        )
        handoff = None
        if not args.runtime_only:
            handoff = write_handoff(
                ROOT,
                checkpoint_id=checkpoint.get("checkpoint_id") if checkpoint["created"] else None,
                checkpoint_path=checkpoint.get("path") if checkpoint["created"] else None,
                active_issue=args.active_issue,
                active_pr=args.active_pr,
                completed=args.completed,
                pending=args.pending,
                objective=args.task,
            )
        result = {"checkpoint": checkpoint, "handoff": handoff}
        atomic_json_write(runtime_dir / "session_continuity.json", result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if checkpoint["created"] else 1

    if args.command == "resume":
        result = resume_report(ROOT, runtime_dir, args.checkpoint_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["resumed"] or result["mode"] == "cold_bootstrap" else 1

    if args.command == "reindex":
        result = reindex_session_store(ROOT, runtime_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        handoff, handoff_error = load_handoff()
        if handoff:
            handoff["reindex"] = result
            handoff["generated_at"] = utc_timestamp()
            atomic_json_write(HANDOFF_PATH, handoff)
        return 0 if result["reindexed"] or result.get("reason") in {"session_store_missing"} else 1

    if args.command == "closeout":
        checkpoint = create_checkpoint(
            ROOT,
            runtime_dir,
            session_id="codespace-closeout",
            task=args.objective,
            completed=args.completed,
            pending=args.pending,
            active_issue=args.active_issue,
            active_pr=args.active_pr,
            checkpoint_in_repo=True,
        )
        bundle = {"created": False, "reason": "disabled"}
        if not args.no_bundle:
            bundle = create_bundle(ROOT)
        reindex = {"reindexed": False, "reason": "disabled"}
        if not args.no_reindex:
            reindex = reindex_session_store(ROOT, runtime_dir)

        bundle_path_value = bundle.get("path")
        bundle_sha256_value = bundle.get("sha256")
        handoff = write_handoff(
            ROOT,
            checkpoint_id=checkpoint.get("checkpoint_id") if checkpoint["created"] else None,
            checkpoint_path=checkpoint.get("path") if checkpoint["created"] else None,
            active_issue=args.active_issue,
            active_pr=args.active_pr,
            completed=args.completed,
            pending=args.pending,
            objective=args.objective,
            bundle_path=bundle_path_value if isinstance(bundle_path_value, str) else None,
            bundle_sha256=bundle_sha256_value if isinstance(bundle_sha256_value, str) else None,
        )
        handoff["reindex"] = reindex
        atomic_json_write(HANDOFF_PATH, handoff)
        atomic_text_write(CONTINUATION_PATH, continuation_prompt(handoff))

        failures: list[str] = []
        if not checkpoint["created"]:
            failures.append("checkpoint_failed")
        if not args.no_bundle and not bundle["created"]:
            failures.append(str(bundle.get("reason", "bundle_failed")))
        if not args.no_reindex:
            if not reindex["reindexed"] and reindex.get("reason") not in {
                "session_store_missing",
                "disabled",
            }:
                failures.append(str(reindex.get("reason", "reindex_failed")))

        closeout_result: dict[str, Any] = {
            "success": not failures,
            "failures": failures,
            "checkpoint": checkpoint,
            "bundle": bundle,
            "reindex": reindex,
            "handoff": handoff,
            "continuation_prompt": str(CONTINUATION_PATH),
        }
        atomic_json_write(runtime_dir / "session_closeout.json", closeout_result)
        print(json.dumps(closeout_result, indent=2, sort_keys=True))
        return 0 if closeout_result["success"] else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
