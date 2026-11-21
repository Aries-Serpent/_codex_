#!/usr/bin/env python3
"""Own and report a bounded Codespace active-session heartbeat."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ACTIVE_MARKER_TTL_SECONDS = 8 * 60 * 60
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_MAX_DURATION_SECONDS = 8 * 60 * 60
DEFAULT_SERVICE_URL = "http://127.0.0.1:8765/api/health"
PID_NAME = "codespace_keepalive.pid"
LOCK_NAME = "codespace_keepalive.lock"
STATUS_NAME = "codespace_keepalive.json"
SSH_PID_NAME = "codespace_keepalive_ssh.pid"
MARKER_NAME = "agent-session.active"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_timestamp(value: datetime | None = None) -> str:
    return (value or utc_now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def runtime_dir_default() -> Path:
    raw = os.environ.get("CODEX_RUNTIME_DIR") or str(Path.home() / ".codex" / "runtime")
    return Path(raw).expanduser()


def repo_root_default() -> Path:
    candidate = os.environ.get("CODESPACE_VSCODE_FOLDER")
    if candidate:
        return Path(candidate).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def active_marker_fresh(marker: Path, ttl_seconds: int, now: datetime | None = None) -> bool:
    if ttl_seconds <= 0 or not marker.is_file():
        return False
    checked_at = now or utc_now()
    modified_at = datetime.fromtimestamp(marker.stat().st_mtime, tz=timezone.utc)
    return 0 <= (checked_at - modified_at).total_seconds() <= ttl_seconds


def touch_active_marker(runtime_dir: Path) -> Path:
    marker = runtime_dir / MARKER_NAME
    runtime_dir.mkdir(parents=True, exist_ok=True)
    marker.write_text(f"{utc_timestamp()}\n", encoding="utf-8")
    marker.touch()
    return marker


def local_service_probe(url: str = DEFAULT_SERVICE_URL) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
            return {"reachable": True, "http_status": response.status}
    except urllib.error.HTTPError as exc:
        return {"reachable": False, "http_status": exc.code, "error_type": "http_error"}
    except urllib.error.URLError:
        return {"reachable": False, "http_status": None, "error_type": "url_error"}
    except (TimeoutError, OSError):
        return {"reachable": False, "http_status": None, "error_type": "unreachable"}


def platform_probe() -> dict[str, Any]:
    codespace = os.environ.get("CODESPACE_NAME")
    token = os.environ.get("CODEX_BACKUP_KEY") or os.environ.get("CODEX_MASTER_KEY")
    if not codespace or not token:
        return {"observed": False, "idle_timeout_minutes": None}
    request = urllib.request.Request(
        f"https://api.github.com/user/codespaces/{codespace}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-codespace-keepalive",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            payload = json.load(response)
            return {
                "observed": True,
                "idle_timeout_minutes": payload.get("idle_timeout_minutes"),
                "last_used_at": payload.get("last_used_at"),
                "state": payload.get("state"),
            }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return {"observed": False, "idle_timeout_minutes": None, "error_type": "probe_failed"}
    except urllib.error.HTTPError:
        return {"observed": False, "idle_timeout_minutes": None, "error_type": "http_error"}


def _process_cwd(pid: int) -> Path | None:
    try:
        return Path(os.readlink(f"/proc/{pid}/cwd")).resolve()
    except OSError:
        return None


def _process_cmdline(pid: int) -> str:
    try:
        return (
            Path(f"/proc/{pid}/cmdline")
            .read_bytes()
            .replace(b"\0", b" ")
            .decode("utf-8", errors="replace")
        )
    except OSError:
        return ""


def pid_is_owned(pid_file: Path, repo_root: Path) -> bool:
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return False
    cwd = _process_cwd(pid)
    root = repo_root.resolve()
    return (
        cwd is not None
        and (cwd == root or root in cwd.parents)
        and "codespace_keepalive.py" in _process_cmdline(pid)
    )


def write_heartbeat(
    *,
    runtime_dir: Path,
    marker: Path,
    pid: int,
    started_at: datetime,
    max_duration_seconds: int,
    marker_ttl_seconds: int,
    service_probe: Callable[[], dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    checked_at = now or utc_now()
    elapsed = max(0, int((checked_at - started_at).total_seconds()))
    platform = platform_probe()
    active = active_marker_fresh(marker, marker_ttl_seconds, checked_at)
    payload = {
        "schema_version": 1,
        "pid": pid,
        "started_at": utc_timestamp(started_at),
        "heartbeat_at": utc_timestamp(checked_at),
        "active": active,
        "elapsed_seconds": elapsed,
        "remaining_seconds": max(0, max_duration_seconds - elapsed),
        "max_duration_seconds": max_duration_seconds,
        "marker": str(marker),
        "marker_ttl_seconds": marker_ttl_seconds,
        "service": service_probe(),
        "codespace": os.environ.get("CODESPACE_NAME"),
        "platform_idle_timeout_minutes": platform["idle_timeout_minutes"],
        "platform_state": platform.get("state"),
        "platform_last_used_at": platform.get("last_used_at"),
        "platform_policy_observed": platform["observed"],
        "overrides_platform_idle_policy": False,
        "platform_note": (
            "Forced-TTY terminal output refreshes inactivity; no platform policy is overridden."
        ),
    }
    atomic_json_write(runtime_dir / STATUS_NAME, payload)
    return payload


def start_daemon(
    *,
    runtime_dir: Path,
    repo_root: Path,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    marker_ttl_seconds: int = DEFAULT_ACTIVE_MARKER_TTL_SECONDS,
    max_duration_seconds: int = DEFAULT_MAX_DURATION_SECONDS,
    service_url: str = DEFAULT_SERVICE_URL,
) -> dict[str, Any]:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    pid_file = runtime_dir / PID_NAME
    if pid_file.exists() and pid_is_owned(pid_file, repo_root):
        return {
            "started": False,
            "already_running": True,
            "pid": int(pid_file.read_text(encoding="utf-8").strip()),
        }
    pid_file.unlink(missing_ok=True)
    touch_active_marker(runtime_dir)
    log_path = runtime_dir / "codespace_keepalive.log"
    with log_path.open("ab") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "run",
                "--runtime-dir",
                str(runtime_dir),
                "--repo-root",
                str(repo_root),
                "--interval-seconds",
                str(interval_seconds),
                "--marker-ttl-seconds",
                str(marker_ttl_seconds),
                "--max-duration-seconds",
                str(max_duration_seconds),
                "--service-url",
                service_url,
            ],
            cwd=repo_root,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return {"started": True, "already_running": False, "pid": process.pid}


def github_cli_path() -> Path | None:
    configured = os.environ.get("CODEX_GH_EXECUTABLE")
    candidates = [
        Path(configured).expanduser() if configured else None,
        Path.home() / ".local" / "bin" / "gh",
        Path("/usr/local/bin/gh"),
        Path("/usr/bin/gh"),
    ]
    for candidate in candidates:
        if candidate is not None and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def connection_process(
    *, runtime_dir: Path, max_duration_seconds: int
) -> subprocess.Popen[bytes] | None:
    codespace = os.environ.get("CODESPACE_NAME")
    gh = github_cli_path()
    token = os.environ.get("CODEX_BACKUP_KEY") or os.environ.get("CODEX_MASTER_KEY")
    if not codespace or gh is None or not token:
        return None
    log_path = runtime_dir / "codespace_keepalive_ssh.log"
    environment = os.environ.copy()
    environment["GH_TOKEN"] = token
    with log_path.open("ab") as log:
        process = subprocess.Popen(
            [
                str(gh),
                "codespace",
                "ssh",
                "-c",
                codespace,
                "--",
                "-tt",
                "-o",
                "ServerAliveInterval=30",
                "-o",
                "ServerAliveCountMax=3",
                (
                    "sh -c 'while :; do "
                    'printf "codex-codespace-keepalive %s\\\\n" '
                    '"$(date -u +%Y-%m-%dT%H:%M:%SZ)"; '
                    "sleep 30; done'"
                ),
            ],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=environment,
            start_new_session=True,
        )
    (runtime_dir / SSH_PID_NAME).write_text(f"{process.pid}\n", encoding="utf-8")
    return process


def stop_connection(process: subprocess.Popen[bytes] | None, runtime_dir: Path) -> None:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    (runtime_dir / SSH_PID_NAME).unlink(missing_ok=True)


def read_status(runtime_dir: Path) -> dict[str, Any]:
    status_path = runtime_dir / STATUS_NAME
    if not status_path.is_file():
        return {
            "running": False,
            "reason": "status_missing",
            "overrides_platform_idle_policy": False,
        }
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "running": False,
            "reason": "status_invalid",
            "overrides_platform_idle_policy": False,
        }
    pid_file = runtime_dir / PID_NAME
    payload["running"] = pid_file.is_file() and payload.get("pid") is not None
    if pid_file.is_file():
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            payload["running"] = pid == int(payload["pid"])
        except (OSError, TypeError, ValueError):
            payload["running"] = False
    if not payload["running"]:
        payload["active"] = False
        if isinstance(payload.get("connection"), dict):
            payload["connection"]["active"] = False
    payload.setdefault("overrides_platform_idle_policy", False)
    return payload


def stop_daemon(runtime_dir: Path, repo_root: Path) -> dict[str, Any]:
    pid_file = runtime_dir / PID_NAME
    if not pid_file.exists():
        return {"stopped": False, "reason": "not_running"}
    if not pid_is_owned(pid_file, repo_root):
        return {"stopped": False, "reason": "not_owned"}
    pid = int(pid_file.read_text(encoding="utf-8").strip())
    os.kill(pid, signal.SIGTERM)
    for _ in range(50):
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(0.1)
    pid_file.unlink(missing_ok=True)
    return {"stopped": True, "pid": pid}


def run_daemon(args: argparse.Namespace) -> int:
    runtime_dir = Path(args.runtime_dir).expanduser().resolve()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    lock_handle = (runtime_dir / LOCK_NAME).open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.close()
        return 1
    pid_file = runtime_dir / PID_NAME
    pid_file.write_text(f"{os.getpid()}\n", encoding="utf-8")
    marker = touch_active_marker(runtime_dir)
    started_at = utc_now()
    stopping = False
    stop_event = threading.Event()
    ssh_process: subprocess.Popen[bytes] | None = None

    def request_stop(_signum: int, _frame: Any) -> None:
        nonlocal stopping
        stopping = True
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    try:
        while not stopping:
            elapsed = (utc_now() - started_at).total_seconds()
            if elapsed >= args.max_duration_seconds:
                break
            active = active_marker_fresh(marker, args.marker_ttl_seconds)
            if active and ssh_process is None:
                ssh_process = connection_process(
                    runtime_dir=runtime_dir,
                    max_duration_seconds=args.max_duration_seconds,
                )
            elif active and ssh_process is not None and ssh_process.poll() is not None:
                stop_connection(ssh_process, runtime_dir)
                ssh_process = connection_process(
                    runtime_dir=runtime_dir,
                    max_duration_seconds=args.max_duration_seconds,
                )
            elif not active and ssh_process is not None:
                stop_connection(ssh_process, runtime_dir)
                ssh_process = None
            heartbeat = write_heartbeat(
                runtime_dir=runtime_dir,
                marker=marker,
                pid=os.getpid(),
                started_at=started_at,
                max_duration_seconds=args.max_duration_seconds,
                marker_ttl_seconds=args.marker_ttl_seconds,
                service_probe=lambda: local_service_probe(args.service_url),
            )
            heartbeat["connection"] = {
                "mode": "codespace_ssh",
                "pid": ssh_process.pid if ssh_process is not None else None,
                "active": ssh_process is not None and ssh_process.poll() is None,
            }
            atomic_json_write(runtime_dir / STATUS_NAME, heartbeat)
            stop_event.wait(args.interval_seconds)
    finally:
        stop_connection(ssh_process, runtime_dir)
        pid_file.unlink(missing_ok=True)
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--runtime-dir", default=str(runtime_dir_default()))
    common.add_argument("--repo-root", default=str(repo_root_default()))
    common.add_argument("--json", action="store_true", dest="json_output")

    start = subparsers.add_parser("start", parents=[common])
    start.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    start.add_argument("--marker-ttl-seconds", type=int, default=DEFAULT_ACTIVE_MARKER_TTL_SECONDS)
    start.add_argument("--max-duration-seconds", type=int, default=DEFAULT_MAX_DURATION_SECONDS)
    start.add_argument("--service-url", default=DEFAULT_SERVICE_URL)
    status = subparsers.add_parser("status", parents=[common])
    status.set_defaults(action="status")
    stop = subparsers.add_parser("stop", parents=[common])
    stop.set_defaults(action="stop")
    restart = subparsers.add_parser("restart", parents=[common])
    restart.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    restart.add_argument(
        "--marker-ttl-seconds", type=int, default=DEFAULT_ACTIVE_MARKER_TTL_SECONDS
    )
    restart.add_argument("--max-duration-seconds", type=int, default=DEFAULT_MAX_DURATION_SECONDS)
    restart.add_argument("--service-url", default=DEFAULT_SERVICE_URL)
    touch = subparsers.add_parser("touch", parents=[common])
    touch.set_defaults(action="touch")
    run = subparsers.add_parser("run", parents=[common])
    run.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    run.add_argument("--marker-ttl-seconds", type=int, default=DEFAULT_ACTIVE_MARKER_TTL_SECONDS)
    run.add_argument("--max-duration-seconds", type=int, default=DEFAULT_MAX_DURATION_SECONDS)
    run.add_argument("--service-url", default=DEFAULT_SERVICE_URL)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime_dir = Path(args.runtime_dir).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    if args.command == "run":
        return run_daemon(args)
    if args.command == "start":
        payload = start_daemon(
            runtime_dir=runtime_dir,
            repo_root=repo_root,
            interval_seconds=args.interval_seconds,
            marker_ttl_seconds=args.marker_ttl_seconds,
            max_duration_seconds=args.max_duration_seconds,
            service_url=args.service_url,
        )
    elif args.command == "stop":
        payload = stop_daemon(runtime_dir, repo_root)
    elif args.command == "restart":
        stopped = stop_daemon(runtime_dir, repo_root)
        payload = stopped | start_daemon(
            runtime_dir=runtime_dir,
            repo_root=repo_root,
            interval_seconds=args.interval_seconds,
            marker_ttl_seconds=args.marker_ttl_seconds,
            max_duration_seconds=args.max_duration_seconds,
            service_url=args.service_url,
        )
    elif args.command == "touch":
        marker = touch_active_marker(runtime_dir)
        payload = {"active": True, "marker": str(marker)}
    else:
        payload = read_status(runtime_dir)
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json_output else str(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
