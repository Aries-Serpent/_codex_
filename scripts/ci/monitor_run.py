#!/usr/bin/env python3
"""
monitor_run.py — GitHub Copilot Coding Agent Run Monitor & Cherry-Pick CLI
===========================================================================

Monitors a GitHub Actions workflow run (by run ID, check-run ID, or commit
SHA) while the agent or user continues working on other tasks concurrently.

CONCURRENCY MODEL
-----------------
The tool has three operating modes to support concurrent work:

  --daemon     Detach poll loop to a background process; return immediately
               so the caller can keep working.  State is written every poll
               to .codex/monitor/<run_id>/state.json.

  --status     Non-blocking: read the latest daemon state file and print it.
               Exit 0 = in_progress / 5 = success.  Use in a loop or CI
               step to gate subsequent work on run completion.

  --wait       Block until the background daemon exits (run complete or
               timeout).  Prints a live tail of the daemon log.

  (default)    Foreground poll loop (blocks terminal; useful in CI).

USAGE
-----
  # Start background daemon -- agent keeps working immediately:
  python scripts/ci/monitor_run.py --run-id 23220880384 --daemon --cherry-pick

  # Non-blocking status check at any point while doing other work:
  python scripts/ci/monitor_run.py --status 23220880384

  # Re-attach to see final result:
  python scripts/ci/monitor_run.py --wait 23220880384

  # One-shot snapshot (no poll loop):
  python scripts/ci/monitor_run.py --run-id 23220880384 --check-only

  # Resolve via check-run ID:
  python scripts/ci/monitor_run.py --check-id 67492995091 --daemon

  # Resolve via commit SHA:
  python scripts/ci/monitor_run.py --commit abc1234ef --daemon

  # Custom poll interval and timeout:
  python scripts/ci/monitor_run.py --run-id 23220880384 --interval 120 --timeout 60

  # Write JSON report on completion:
  python scripts/ci/monitor_run.py --run-id 23220880384 --json-out /tmp/report.json

  # Stop a running daemon:
  python scripts/ci/monitor_run.py --stop 23220880384

  # List all known monitors:
  python scripts/ci/monitor_run.py --list

CONCURRENT AGENT PATTERN
------------------------
  # Step 1 -- launch daemon (returns immediately):
  python scripts/ci/monitor_run.py --run-id RUN_ID --daemon --cherry-pick --triage

  # Step 2 -- agent does other work (edit files, run tests, commit, etc.)

  # Step 3 -- non-blocking status check:
  python scripts/ci/monitor_run.py --status RUN_ID
  #  exit 0 = in_progress  |  5 = success  |  1 = failure  |  2 = timeout

  # Step 4 -- re-attach when ready:
  python scripts/ci/monitor_run.py --wait RUN_ID

PYTHON EMBEDDING API
--------------------
  from scripts.ci.monitor_run import start_background_monitor, poll_status

  handle = start_background_monitor(
      run_id=23220880384, cherry_pick=True, triage=True
  )
  # ...do other work...
  state = poll_status(23220880384)
  if state and state.completed:
      print(state.conclusion)

EXIT CODES
----------
  0  In-progress (--status) or success (all other modes)
  1  Run failed / cancelled
  2  Timeout
  3  API / authentication error
  4  Post-completion triage checks failed
  5  Run succeeded (--status only, to distinguish from in-progress=0)

ENVIRONMENT
-----------
  GITHUB_TOKEN        PAT with repo / workflow read scope
  CODEX_MASTER_KEY    Fallback admin token
  CODEX_BACKUP_KEY    Second fallback
  GITHUB_REPOSITORY   owner/repo (auto-inferred from git remote if unset)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import signal
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
REPO_ROOT       = Path(__file__).resolve().parent.parent.parent
TRIAGE_SCRIPT   = REPO_ROOT / "scripts" / "ci" / "ci_triage_repro.sh"
MONITOR_DIR     = REPO_ROOT / ".codex" / "monitor"

API_BASE                 = "https://api.github.com"
DEFAULT_INTERVAL_SECONDS = 300   # 5-minute poll cadence
DEFAULT_TIMEOUT_MINUTES  = 90

_TTY   = sys.stdout.isatty()
C_GRN  = "\033[32m" if _TTY else ""
C_RED  = "\033[31m" if _TTY else ""
C_YEL  = "\033[33m" if _TTY else ""
C_CYN  = "\033[36m" if _TTY else ""
C_RST  = "\033[0m"  if _TTY else ""
C_BOLD = "\033[1m"  if _TTY else ""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PollSnapshot:
    """Written to .codex/monitor/<run_id>/state.json after every API poll.

    Timing fields
    -------------
    session_started_at : ISO-8601 UTC — when the Copilot Coding Agent session
                         began.  Resolved (in priority order) from:
                           1. ``--session-start`` CLI arg
                           2. ``GITHUB_RUN_STARTED_AT`` environment variable
                           3. The workflow run's own ``run_started_at`` from API
                           4. Daemon spawn time (fallback)
    current_dt         : ISO-8601 UTC — wall-clock time at this specific poll.
    session_elapsed_s  : Whole seconds elapsed between ``session_started_at``
                         and ``current_dt``.  Monotonically increases each poll.
    """
    run_id:       int
    repo:         str
    polled_at:    str           # ISO-8601 UTC — time of this poll (== current_dt)
    status:       str
    conclusion:   Optional[str]
    head_sha:     str
    head_branch:  str
    html_url:     str
    # ── Session timing ────────────────────────────────────────────────────
    session_started_at:  str = ""  # ISO-8601 UTC — agent session start
    session_started_ns:  int = 0   # nanoseconds since epoch at session start
    current_dt:          str = ""  # ISO-8601 UTC — wall-clock at this poll
    session_elapsed_s:   int = 0   # whole seconds elapsed since session start
    session_elapsed_ns:  int = 0   # sub-second nanosecond remainder (0–999999999)
    session_elapsed_str: str = ""  # human: "Xh Ym Zs NNNNNNNNNns"
    # ── Post-completion ───────────────────────────────────────────────────
    cherry_picked:  List[str]       = field(default_factory=list)
    triage_passed:  Optional[bool]  = None
    triage_details: List[str]       = field(default_factory=list)
    error:          Optional[str]   = None
    completed:      bool            = False

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "PollSnapshot":
        known = {f for f in cls.__dataclass_fields__}   # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in known})


# ---------------------------------------------------------------------------
# State-file helpers  (.codex/monitor/<run_id>/state.json)
# ---------------------------------------------------------------------------

def _state_dir(run_id: int) -> Path:
    d = MONITOR_DIR / str(run_id)
    d.mkdir(parents=True, exist_ok=True)
    return d

def _state_file(run_id: int) -> Path:
    return _state_dir(run_id) / "state.json"

def _pid_file(run_id: int) -> Path:
    return _state_dir(run_id) / "daemon.pid"

def _log_file(run_id: int) -> Path:
    return _state_dir(run_id) / "daemon.log"

def _write_state(snap: PollSnapshot) -> None:
    _state_file(snap.run_id).write_text(
        json.dumps(snap.to_dict(), indent=2), encoding="utf-8"
    )

def _read_state(run_id: int) -> Optional[PollSnapshot]:
    sf = _state_file(run_id)
    if not sf.exists():
        return None
    try:
        return PollSnapshot.from_dict(json.loads(sf.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# GitHub API client
# ---------------------------------------------------------------------------

class _Client:
    def __init__(self, token: Optional[str], verbose: bool = False):
        self.token   = token
        self.verbose = verbose

    def _get(self, path: str) -> Any:
        url = f"{API_BASE}{path}"
        headers: Dict[str, str] = {
            "Accept":               "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.verbose:
            _log(f"[api] GET {url}")
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"Network: {exc.reason} -- {url}") from exc

    def get_run(self, repo: str, run_id: int) -> PollSnapshot:
        d = self._get(f"/repos/{repo}/actions/runs/{run_id}")
        snap = PollSnapshot(
            run_id      = d["id"],
            repo        = repo,
            polled_at   = _now(),
            status      = d["status"],
            conclusion  = d.get("conclusion"),
            head_sha    = d.get("head_sha", ""),
            head_branch = d.get("head_branch", ""),
            html_url    = d["html_url"],
        )
        # Stash API run_started_at so _poll_loop can refine session_started_at
        # on the first poll when GITHUB_RUN_STARTED_AT env var is absent.
        snap._api_run_started_at = (  # type: ignore[attr-defined]
            d.get("run_started_at") or d.get("created_at", "")
        )
        return snap

    def get_check_run(self, repo: str, check_id: int) -> Dict:
        return self._get(f"/repos/{repo}/check-runs/{check_id}")

    def get_commit_runs(self, repo: str, sha: str) -> List[Dict]:
        d = self._get(f"/repos/{repo}/actions/runs?head_sha={sha}&per_page=20")
        return d.get("workflow_runs", [])


# ---------------------------------------------------------------------------
# Token / repo resolution
# ---------------------------------------------------------------------------

def _resolve_token() -> Optional[str]:
    for var in ("GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        v = os.environ.get(var, "").strip()
        if v:
            return v
    return None

def _resolve_repo() -> str:
    env = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env:
        return env
    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, cwd=REPO_ROOT,
        ).decode().strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", remote)
        if m:
            return m.group(1)
    except Exception:  # noqa: BLE001
        logger.debug("Suppressed exception in handler", exc_info=True)
    return "Aries-Serpent/_codex_"


# ---------------------------------------------------------------------------
# Run-ID resolution
# ---------------------------------------------------------------------------

def _run_id_from_check(client: _Client, repo: str, check_id: int) -> int:
    check    = client.get_check_run(repo, check_id)
    head_sha = check.get("head_sha", "")
    if not head_sha:
        raise RuntimeError(f"No head_sha on check-run {check_id}")
    runs = client.get_commit_runs(repo, head_sha)
    if not runs:
        raise RuntimeError(f"No workflow runs for commit {head_sha} (check {check_id})")
    return int(sorted(runs, key=lambda r: r.get("run_number", 0), reverse=True)[0]["id"])

def _run_id_from_commit(client: _Client, repo: str, sha: str) -> int:
    runs = client.get_commit_runs(repo, sha)
    if not runs:
        raise RuntimeError(f"No workflow runs for commit {sha!r}")
    return int(sorted(runs, key=lambda r: r.get("run_number", 0), reverse=True)[0]["id"])


# ---------------------------------------------------------------------------
# Git / triage helpers
# ---------------------------------------------------------------------------

def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], stderr=subprocess.PIPE, cwd=REPO_ROOT,
    ).decode().strip()

_SKIP_PATTERNS = (".codex/agent_auth", "CODEX_MANIFEST")

def cherry_pick_delta(branch: str, verbose: bool = False) -> List[str]:
    """Checkout files differing between HEAD and origin/<branch>; return applied paths."""
    _git("fetch", "origin", branch)
    diff_raw = _git("diff", "--name-only", "HEAD", f"origin/{branch}")
    if not diff_raw.strip():
        return []
    applied: List[str] = []
    for path in diff_raw.splitlines():
        if any(path.startswith(p) for p in _SKIP_PATTERNS):
            continue
        _git("checkout", f"origin/{branch}", "--", path)
        applied.append(path)
        if verbose:
            _log(f"  applied: {path}")
    return applied

def run_triage(verbose: bool = False) -> tuple[bool, List[str]]:
    """Run ci_triage_repro.sh --json.  Returns (passed, detail_lines)."""
    if not TRIAGE_SCRIPT.exists():
        return True, ["triage script not found -- skipped"]
    try:
        result = subprocess.run(
            ["bash", str(TRIAGE_SCRIPT), "--json"],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=300,
        )
        try:
            data    = json.loads(result.stdout)
            details = [
                f"{'OK' if c.get('passed') else 'FAIL'} {c.get('id','?')}: {c.get('detail','')}"
                for c in data.get("checks", [])
            ]
            passed = data.get("all_passed", result.returncode == 0)
        except (json.JSONDecodeError, KeyError):
            details = result.stdout.splitlines()[-10:]
            passed  = result.returncode == 0
        return passed, details
    except subprocess.TimeoutExpired:
        return False, ["triage timed out after 300s"]


# ---------------------------------------------------------------------------
# Logging (file + stdout, non-blocking)
# ---------------------------------------------------------------------------

_log_path: Optional[Path] = None

def _log(msg: str, *, to_file: bool = True, to_stdout: bool = True) -> None:
    ts   = datetime.now(tz=timezone.utc).strftime("%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    if to_stdout:
        print(line, flush=True)
    if to_file and _log_path:
        try:
            with _log_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception:  # noqa: BLE001
            logger.debug("Suppressed exception in handler", exc_info=True)
def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _resolve_session_start(
    api_run_started_at: str = "",
    *,
    cli_override: str = "",
) -> tuple[str, int]:
    """
    Return (iso_str, ns_since_epoch) of when the Copilot Coding Agent session began.

    Resolution priority:
    1. ``cli_override``                  — explicit ``--session-start`` flag; highest
       priority so users can always force a specific start time regardless of env.
    2. ``GITHUB_RUN_STARTED_AT`` env var — set by GitHub Actions; represents
       the moment the runner picked up the current workflow job (agent session
       start in CI).
    3. ``api_run_started_at``            — ``run_started_at`` from the GitHub
       Actions API for the monitored run (populated after first poll).
    4. ``time.time_ns()`` / ``datetime.now()`` — daemon/thread spawn time
       (fallback when running outside CI or before the first API poll).
    """
    src = cli_override or os.environ.get("GITHUB_RUN_STARTED_AT", "").strip() or api_run_started_at
    if src:
        try:
            dt = datetime.fromisoformat(src.replace("Z", "+00:00"))
            ns = int(dt.timestamp() * 1_000_000_000)
            return src, ns
        except Exception:  # noqa: BLE001
            logger.debug("Suppressed exception in handler", exc_info=True)
    # Fallback: capture current nanosecond-precision time
    ns  = time.time_ns()
    iso = datetime.now(tz=timezone.utc).isoformat()
    return iso, ns


def _compute_elapsed(session_started_ns: int) -> tuple[int, int, str]:
    """
    Return (elapsed_seconds, elapsed_ns_remainder, human_string) from
    ``session_started_ns`` (nanoseconds since epoch) to now.

    Format: ``Xh Ym Zs NNNNNNNNNns``
      - hours / minutes / seconds are whole-unit components
      - ``NNNNNNNNNns`` is the sub-second nanosecond remainder (9 digits, zero-padded)

    Examples
    --------
      0h  0m  2s 000000000ns   →  "2s 000000000ns"
      0h  3m  7s 123456789ns   →  "3m 07s 123456789ns"
      1h 12m 43s 987654321ns   →  "1h 12m 43s 987654321ns"
    """
    now_ns   = time.time_ns()
    total_ns = max(0, now_ns - session_started_ns)

    full_s, ns_rem = divmod(total_ns, 1_000_000_000)
    hours, rem_s   = divmod(full_s, 3600)
    mins,  secs    = divmod(rem_s, 60)

    ns_str = f"{ns_rem:09d}ns"
    if hours:
        human = f"{hours}h {mins}m {secs:02d}s {ns_str}"
    elif mins:
        human = f"{mins}m {secs:02d}s {ns_str}"
    else:
        human = f"{secs}s {ns_str}"

    return int(full_s), ns_rem, human


# ---------------------------------------------------------------------------
# Core poll loop  (runs foreground, daemon-process, or background thread)
# ---------------------------------------------------------------------------

def _poll_loop(
    run_id:    int,
    repo:      str,
    client:    _Client,
    interval:  int,
    timeout:   int,
    check_only: bool,
    do_cherry: bool,
    do_triage: bool,
    session_started_at:  str = "",   # ISO from _resolve_session_start()
    session_started_ns:  int = 0,    # ns from _resolve_session_start()
    on_complete: Optional[Callable[["PollSnapshot"], None]] = None,
    verbose:   bool = False,
) -> PollSnapshot:
    # Resolve session start once — used for every poll's elapsed computation
    _ss_at  = session_started_at
    _ss_ns  = session_started_ns
    # First-poll flag: if ns=0 and env is also absent, capture spawn time now
    if not _ss_ns:
        _ss_at, _ss_ns = _resolve_session_start()

    deadline = time.monotonic() + timeout * 60
    poll_n   = 0

    while True:
        poll_n += 1
        try:
            snap = client.get_run(repo, run_id)
        except RuntimeError as exc:
            now_iso = _now()
            el_s, el_ns, el_str = _compute_elapsed(_ss_ns)
            snap = PollSnapshot(
                run_id=run_id, repo=repo, polled_at=now_iso,
                status="error", conclusion=None,
                head_sha="", head_branch="", html_url="",
                session_started_at=_ss_at, session_started_ns=_ss_ns,
                current_dt=now_iso,
                session_elapsed_s=el_s, session_elapsed_ns=el_ns,
                session_elapsed_str=el_str,
                error=str(exc), completed=True,
            )
            _write_state(snap)
            _log(f"API error: {exc}")
            return snap

        # ── Stamp timing on every poll ────────────────────────────────────
        now_iso = _now()
        # On first poll, refine session_started_at using the run's own API
        # start time when GITHUB_RUN_STARTED_AT env var is absent (local runs).
        if poll_n == 1 and not os.environ.get("GITHUB_RUN_STARTED_AT"):
            api_ts = getattr(snap, "_api_run_started_at", "")
            if api_ts:
                _ss_at, _ss_ns = _resolve_session_start(api_ts)

        el_s, el_ns, el_str = _compute_elapsed(_ss_ns)
        snap.session_started_at  = _ss_at
        snap.session_started_ns  = _ss_ns
        snap.current_dt          = now_iso
        snap.session_elapsed_s   = el_s
        snap.session_elapsed_ns  = el_ns
        snap.session_elapsed_str = el_str
        snap.completed = (snap.status == "completed")
        _write_state(snap)

        col = C_GRN if snap.conclusion == "success" else (
              C_RED if snap.conclusion in ("failure","cancelled") else C_YEL)
        _log(
            f"poll#{poll_n:02d} run={run_id} "
            f"status={col}{snap.status}{C_RST} "
            f"conclusion={col}{snap.conclusion or '--'}{C_RST} "
            f"session_elapsed={C_CYN}{el_str}{C_RST} "
            f"now={now_iso}"
        )

        if snap.completed or check_only:
            if do_cherry and snap.completed and snap.head_branch:
                _log(f"Cherry-picking delta from {snap.head_branch}...")
                try:
                    applied = cherry_pick_delta(snap.head_branch, verbose=verbose)
                    snap.cherry_picked = applied
                    _log(f"  Applied {len(applied)} file(s)")
                except Exception as exc:  # noqa: BLE001
                    _log(f"  cherry-pick error: {exc}")
                    snap.error = str(exc)

            if do_triage or (do_cherry and snap.cherry_picked):
                _log("Running CI triage checks...")
                passed, details = run_triage(verbose=verbose)
                snap.triage_passed  = passed
                snap.triage_details = details
                for ln in details:
                    _log(f"  {ln}")
                _log("triage: all passed" if passed else "triage: FAILURES detected")

            snap.completed = True
            _write_state(snap)
            if on_complete:
                on_complete(snap)
            return snap

        if time.monotonic() >= deadline:
            snap.error     = f"Timeout after {timeout} minutes"
            snap.completed = True
            _write_state(snap)
            _log(f"Timeout ({timeout}m) -- run still in_progress")
            return snap

        remaining = max(0, int(deadline - time.monotonic()))
        _log(
            f"  next poll in {interval}s  "
            f"({remaining // 60}m{remaining % 60:02d}s until timeout)"
        )
        time.sleep(interval)


# ---------------------------------------------------------------------------
# Daemon (background process)
# ---------------------------------------------------------------------------

def _daemon_entrypoint(
    run_id: int, repo: str, interval: int, timeout: int,
    do_cherry: bool, do_triage: bool, verbose: bool,
    session_started_at: str = "", session_started_ns: int = 0,
) -> None:
    global _log_path
    _log_path = _log_file(run_id)
    _log_path.parent.mkdir(parents=True, exist_ok=True)
    _pid_file(run_id).write_text(str(os.getpid()), encoding="utf-8")
    token  = _resolve_token()
    client = _Client(token=token, verbose=verbose)
    # Resolve session start — prefer passed-in value, then env, then now
    ss_at, ss_ns = _resolve_session_start()
    if session_started_ns:
        ss_at, ss_ns = session_started_at, session_started_ns
    _, _, elapsed_str = _compute_elapsed(ss_ns)
    _log(
        f"daemon started  run_id={run_id}  pid={os.getpid()}  "
        f"session_start={ss_at}  elapsed_at_spawn={elapsed_str}"
    )
    try:
        _poll_loop(
            run_id=run_id, repo=repo, client=client,
            interval=interval, timeout=timeout,
            check_only=False, do_cherry=do_cherry, do_triage=do_triage,
            session_started_at=ss_at, session_started_ns=ss_ns,
            verbose=verbose,
        )
    finally:
        _pid_file(run_id).unlink(missing_ok=True)
        _log("daemon exiting")


def launch_daemon(
    run_id: int, repo: str,
    interval: int = DEFAULT_INTERVAL_SECONDS,
    timeout:  int = DEFAULT_TIMEOUT_MINUTES,
    do_cherry: bool = False, do_triage: bool = False,
    verbose: bool = False,
    session_started_at: str = "", session_started_ns: int = 0,
) -> int:
    """Fork as a background process; return child PID immediately."""
    # Capture session start NOW (in caller) so daemon inherits accurate timing
    ss_at, ss_ns = _resolve_session_start()
    if session_started_ns:
        ss_at, ss_ns = session_started_at, session_started_ns

    script = Path(__file__).resolve()
    cmd = [
        sys.executable, str(script),
        "--run-id",       str(run_id),
        "--repo",         repo,
        "--interval",     str(interval),
        "--timeout",      str(timeout),
        "--session-start", ss_at,
        "--session-start-ns", str(ss_ns),
        "--_daemon-worker",
    ]
    if do_cherry:
        cmd.append("--cherry-pick")
    if do_triage:
        cmd.append("--triage")
    if verbose:
        cmd.append("--verbose")

    log = _log_file(run_id)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            cmd, stdout=lf, stderr=lf,
            start_new_session=True, cwd=REPO_ROOT,
        )
    _pid_file(run_id).write_text(str(proc.pid), encoding="utf-8")
    return proc.pid


# ---------------------------------------------------------------------------
# Background thread API  (Python embedding)
# ---------------------------------------------------------------------------

class MonitorThread(threading.Thread):
    """
    Poll loop in a daemon thread -- calling thread is free immediately.

    Example::

        t = MonitorThread(run_id=23220880384, repo="owner/repo",
                          do_cherry=True, do_triage=True)
        t.start()
        # ... do other work here ...
        t.join()
        print(t.result.conclusion)
    """

    def __init__(
        self,
        run_id:    int,
        repo:      str,
        token:     Optional[str]  = None,
        interval:  int  = DEFAULT_INTERVAL_SECONDS,
        timeout:   int  = DEFAULT_TIMEOUT_MINUTES,
        do_cherry: bool = False,
        do_triage: bool = False,
        on_complete: Optional[Callable[[PollSnapshot], None]] = None,
        verbose:    bool = False,
        session_started_at: str = "",
        session_started_ns: int = 0,
    ):
        super().__init__(daemon=True, name=f"monitor-run-{run_id}")
        self._client     = _Client(token or _resolve_token(), verbose=verbose)
        self.run_id      = run_id
        self.repo        = repo
        self.interval    = interval
        self.timeout     = timeout
        self.do_cherry   = do_cherry
        self.do_triage   = do_triage
        self.on_complete = on_complete
        self.verbose     = verbose
        self.result: Optional[PollSnapshot] = None
        # Capture session start at thread-creation time (caller process)
        if session_started_ns:
            self._ss_at = session_started_at
            self._ss_ns = session_started_ns
        else:
            self._ss_at, self._ss_ns = _resolve_session_start(
                cli_override=session_started_at,
            )

    def run(self) -> None:
        self.result = _poll_loop(
            run_id=self.run_id, repo=self.repo, client=self._client,
            interval=self.interval, timeout=self.timeout,
            check_only=False, do_cherry=self.do_cherry,
            do_triage=self.do_triage, on_complete=self.on_complete,
            session_started_at=self._ss_at, session_started_ns=self._ss_ns,
            verbose=self.verbose,
        )


def start_background_monitor(
    run_id:    int,
    repo:      Optional[str] = None,
    token:     Optional[str] = None,
    interval:  int  = DEFAULT_INTERVAL_SECONDS,
    timeout:   int  = DEFAULT_TIMEOUT_MINUTES,
    cherry_pick: bool = False,
    triage:    bool = False,
    on_complete: Optional[Callable[[PollSnapshot], None]] = None,
    verbose:   bool = False,
) -> MonitorThread:
    """
    Public Python API: start a background monitor thread, return immediately.

    Example::

        from scripts.ci.monitor_run import start_background_monitor, poll_status

        handle = start_background_monitor(run_id=23220880384, cherry_pick=True)

        # do other work...

        state = poll_status(23220880384)
        if state and state.completed:
            print("Done:", state.conclusion)
    """
    t = MonitorThread(
        run_id=run_id, repo=repo or _resolve_repo(), token=token,
        interval=interval, timeout=timeout,
        do_cherry=cherry_pick, do_triage=triage,
        on_complete=on_complete, verbose=verbose,
    )
    t.start()
    return t


def poll_status(run_id: int) -> Optional[PollSnapshot]:
    """Non-blocking: read latest state from file. Returns None if no monitor started."""
    return _read_state(run_id)


# ---------------------------------------------------------------------------
# --status / --wait / --stop / --list subcommand handlers
# ---------------------------------------------------------------------------

def cmd_status(run_id: int) -> int:
    snap = _read_state(run_id)
    if snap is None:
        print(f"No monitor state found for run {run_id}.")
        print(f"  Start one:  python {Path(__file__).name} --run-id {run_id} --daemon")
        return 3

    col = C_GRN if snap.conclusion == "success" else (
          C_RED if snap.conclusion in ("failure","cancelled") else C_YEL)
    print(f"\n{'--'*30}")
    print(f"  Run ID         : {C_CYN}{snap.run_id}{C_RST}")
    print(f"  Status         : {col}{snap.status}{C_RST}")
    print(f"  Conclusion     : {col}{snap.conclusion or '--'}{C_RST}")
    print(f"  Branch         : {snap.head_branch}")
    print(f"  Commit         : {snap.head_sha[:12] if snap.head_sha else '--'}")
    print("  ── Timing ─────────────────────────────")
    print(f"  Session start  : {C_CYN}{snap.session_started_at or '--'}{C_RST}")
    print(f"  Current time   : {C_CYN}{snap.current_dt or snap.polled_at}{C_RST}")
    # Recompute live elapsed if daemon is still running (state file may be stale)
    if snap.session_started_ns and not snap.completed:
        _, _, live_str = _compute_elapsed(snap.session_started_ns)
        print(f"  Elapsed (live) : {C_YEL}{live_str}{C_RST}  ← recomputed now")
    elif snap.session_elapsed_str:
        print(f"  Elapsed (final): {C_GRN}{snap.session_elapsed_str}{C_RST}")
    print("  ─────────────────────────────────────")
    print(f"  Last polled    : {snap.polled_at}")
    print(f"  URL            : {snap.html_url}")
    if snap.cherry_picked:
        print(f"  Cherry-picked ({len(snap.cherry_picked)}):")
        for f in snap.cherry_picked:
            print(f"    * {f}")
    if snap.triage_passed is not None:
        t_col = C_GRN if snap.triage_passed else C_RED
        print(f"  Triage    : {t_col}{'passed' if snap.triage_passed else 'FAILED'}{C_RST}")
    if snap.error:
        print(f"  Error     : {C_RED}{snap.error}{C_RST}")
    pf = _pid_file(run_id)
    if pf.exists():
        print(f"  Daemon PID: {pf.read_text().strip()} (running)")
    print(f"{'--'*30}\n")

    if not snap.completed:
        return 0   # in_progress
    if snap.error and "Timeout" in (snap.error or ""):
        return 2
    if snap.error and not snap.conclusion:
        return 3
    if snap.triage_passed is False:
        return 4
    if snap.conclusion in ("success", "skipped"):
        return 5
    return 1  # failure/cancelled


def cmd_wait(run_id: int, poll_interval: int = 10) -> int:
    pid_f = _pid_file(run_id)
    log_f = _log_file(run_id)

    if not pid_f.exists() and not _state_file(run_id).exists():
        print(f"No running daemon for run {run_id}.")
        return 3

    print(f"{C_CYN}Waiting for run {run_id} -- tailing {log_f}{C_RST}")
    print("(Ctrl+C to detach without stopping the daemon)\n")

    last_size = 0
    try:
        while True:
            if log_f.exists():
                current_size = log_f.stat().st_size
                if current_size > last_size:
                    with log_f.open(encoding="utf-8") as fh:
                        fh.seek(last_size)
                        for line in fh:
                            print(line, end="", flush=True)
                    last_size = current_size

            if not pid_f.exists():
                snap = _read_state(run_id)
                if snap and snap.completed:
                    print(f"\n{C_BOLD}Monitor complete.{C_RST}")
                    return cmd_status(run_id)
                print(f"\n{C_RED}Daemon exited unexpectedly.{C_RST}")
                return 3

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pid = pid_f.read_text().strip() if pid_f.exists() else "?"
        print(f"\n{C_YEL}Detached -- daemon PID {pid} still running.{C_RST}")
        print(f"  Re-attach: python {Path(__file__).name} --wait {run_id}")
        return 0


def cmd_stop(run_id: int) -> int:
    pid_f = _pid_file(run_id)
    if not pid_f.exists():
        print(f"No running daemon found for run {run_id}.")
        return 0
    try:
        pid = int(pid_f.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        pid_f.unlink(missing_ok=True)
        print(f"Sent SIGTERM to daemon PID {pid} for run {run_id}")
        return 0
    except ProcessLookupError:
        pid_f.unlink(missing_ok=True)
        print("PID not found -- daemon may have already exited")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to stop daemon: {exc}")
        return 1


def cmd_list() -> int:
    if not MONITOR_DIR.exists():
        print("No monitor state directory found (.codex/monitor/).")
        return 0
    dirs = sorted(MONITOR_DIR.iterdir())
    if not dirs:
        print("No monitors recorded yet.")
        return 0
    print(f"\n{'Run ID':>14}  {'Status':12}  {'Conclusion':12}  {'Elapsed':22}  {'Current DT':26}  Daemon")
    print("-" * 105)
    for d in dirs:
        sf = d / "state.json"
        pf = d / "daemon.pid"
        if not sf.exists():
            continue
        try:
            snap = PollSnapshot.from_dict(json.loads(sf.read_text(encoding="utf-8")))
            daemon_info = f"PID {pf.read_text().strip()}" if pf.exists() else "stopped"
            col = C_GRN if snap.conclusion == "success" else (
                  C_RED if snap.conclusion in ("failure","cancelled") else C_YEL)
            # Live-recompute elapsed if daemon still running
            if snap.session_started_ns and pf.exists():
                _, _, elapsed_str = _compute_elapsed(snap.session_started_ns)
            else:
                elapsed_str = snap.session_elapsed_str or "--"
            current = snap.current_dt or snap.polled_at
            print(
                f"{snap.run_id:>14}  "
                f"{col}{snap.status:12}{C_RST}  "
                f"{col}{(snap.conclusion or '--'):12}{C_RST}  "
                f"{C_CYN}{elapsed_str:22}{C_RST}  "
                f"{current:26}  {daemon_info}"
            )
        except Exception:  # noqa: BLE001
            print(f"{d.name:>14}  (unreadable state)")
    print()
    return 0


# ---------------------------------------------------------------------------
# Exit code mapping
# ---------------------------------------------------------------------------

def _exit_code(snap: PollSnapshot) -> int:
    if snap.error and "Timeout" in (snap.error or ""):
        return 2
    if snap.error and not snap.conclusion:
        return 3
    if snap.triage_passed is False:
        return 4
    if snap.conclusion in ("success", "skipped"):
        return 0
    if snap.conclusion in ("failure", "cancelled", "timed_out"):
        return 1
    return 0


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="monitor_run",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--status", type=int, metavar="RUN_ID",
                      help="Non-blocking: print state file for RUN_ID")
    mode.add_argument("--wait",   type=int, metavar="RUN_ID",
                      help="Block + tail log until daemon finishes")
    mode.add_argument("--stop",   type=int, metavar="RUN_ID",
                      help="Terminate background daemon for RUN_ID")
    mode.add_argument("--list",   action="store_true",
                      help="List all known monitor state files")

    tgt = p.add_mutually_exclusive_group()
    tgt.add_argument("--run-id",   type=int,   metavar="RUN_ID",  help="Workflow run ID")
    tgt.add_argument("--check-id", type=int,   metavar="CHECK_ID",help="Check-run ID (resolves to run)")
    tgt.add_argument("--commit",   metavar="SHA", help="Commit SHA (monitors newest run for that commit)")

    p.add_argument("--daemon",      action="store_true",
                   help="Detach to background process; return immediately (non-blocking)")
    p.add_argument("--cherry-pick", action="store_true",
                   help="After completion, checkout new files from run branch")
    p.add_argument("--triage",      action="store_true",
                   help="Run all 7 CI triage checks after completion")
    p.add_argument("--check-only",  action="store_true",
                   help="Single snapshot; no poll loop")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, metavar="SECS",
                   help=f"Seconds between polls (default: {DEFAULT_INTERVAL_SECONDS})")
    p.add_argument("--timeout",  type=int, default=DEFAULT_TIMEOUT_MINUTES,  metavar="MINS",
                   help=f"Hard timeout in minutes (default: {DEFAULT_TIMEOUT_MINUTES})")
    p.add_argument("--json-out", metavar="PATH", help="Write JSON report on completion")
    p.add_argument("--repo",     metavar="OWNER/REPO",
                   help="Repository (default: inferred from git remote)")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument(
        "--session-start", metavar="ISO",
        help="ISO-8601 UTC timestamp of agent session start "
             "(default: GITHUB_RUN_STARTED_AT env → API run_started_at → now). "
             "Example: 2026-03-17T23:15:08Z",
    )
    p.add_argument(
        "--session-start-ns", type=int, default=0, metavar="NS",
        help=argparse.SUPPRESS,   # internal: nanoseconds since epoch at session start
    )
    p.add_argument("--_daemon-worker", action="store_true", help=argparse.SUPPRESS)

    return p


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main() -> int:
    global _log_path

    parser = _build_parser()
    args   = parser.parse_args()

    if args.list:
        return cmd_list()
    if args.status is not None:
        return cmd_status(args.status)
    if args.wait is not None:
        return cmd_wait(args.wait)
    if args.stop is not None:
        return cmd_stop(args.stop)

    # Internal: daemon worker (re-spawned by launch_daemon)
    if args._daemon_worker:
        if not args.run_id:
            print("--_daemon-worker requires --run-id", file=sys.stderr)
            return 3
        _daemon_entrypoint(
            run_id=args.run_id, repo=args.repo or _resolve_repo(),
            interval=args.interval, timeout=args.timeout,
            do_cherry=args.cherry_pick, do_triage=args.triage,
            verbose=args.verbose,
            session_started_at=args.session_start or "",
            session_started_ns=args.session_start_ns or 0,
        )
        return 0

    if not (args.run_id or args.check_id or args.commit):
        parser.error(
            "Specify a target: --run-id, --check-id, or --commit  "
            "(or use --status/--wait/--stop/--list)"
        )

    token  = _resolve_token()
    repo   = args.repo or _resolve_repo()
    client = _Client(token=token, verbose=args.verbose)

    if not token:
        print(
            f"{C_YEL}No GitHub token found "
            f"(GITHUB_TOKEN / CODEX_MASTER_KEY / CODEX_BACKUP_KEY). "
            f"Unauthenticated: 60 req/h rate limit.{C_RST}",
            file=sys.stderr,
        )

    run_id: int
    try:
        if args.run_id:
            run_id = args.run_id
        elif args.check_id:
            print(f"Resolving check-run {args.check_id} -> workflow run...")
            run_id = _run_id_from_check(client, repo, args.check_id)
            print(f"  -> run_id={run_id}")
        else:
            print(f"Resolving commit {args.commit[:12]} -> workflow run...")
            run_id = _run_id_from_commit(client, repo, args.commit)
            print(f"  -> run_id={run_id}")
    except RuntimeError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 3

    # Resolve session start in the caller process so it is as early as possible
    ss_at_cli = getattr(args, "session_start", None) or ""
    ss_ns_cli = getattr(args, "session_start_ns", 0) or 0
    if ss_ns_cli:
        ss_at, ss_ns = ss_at_cli, ss_ns_cli
    else:
        ss_at, ss_ns = _resolve_session_start(cli_override=ss_at_cli)
    _, _, ss_elapsed = _compute_elapsed(ss_ns)

    # Daemon mode -- non-blocking
    if args.daemon:
        pid = launch_daemon(
            run_id=run_id, repo=repo,
            interval=args.interval, timeout=args.timeout,
            do_cherry=args.cherry_pick, do_triage=args.triage,
            verbose=args.verbose,
            session_started_at=ss_at, session_started_ns=ss_ns,
        )
        log    = _log_file(run_id)
        state  = _state_file(run_id)
        print(f"\n{C_GRN}Monitor daemon started{C_RST}")
        print(f"  Run ID       : {C_CYN}{run_id}{C_RST}")
        print(f"  Daemon PID   : {pid}")
        print(f"  Session start: {C_CYN}{ss_at}{C_RST}")
        print(f"  Elapsed now  : {C_YEL}{ss_elapsed}{C_RST}")
        print(f"  Log          : {log}")
        print(f"  State        : {state}")
        print(f"\n  {C_BOLD}You can keep working.{C_RST}  Check status at any time:")
        print(f"  python {Path(__file__).name} --status {run_id}")
        print(f"  python {Path(__file__).name} --wait   {run_id}   # re-attach")
        print()
        return 0

    # Foreground mode -- blocks
    _log_path = _log_file(run_id)
    _log_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*62}")
    print("  GitHub Run Monitor  (foreground)")
    print(f"  Run ID       : {C_CYN}{run_id}{C_RST}  |  Repo: {repo}")
    print(f"  Session start: {C_CYN}{ss_at}{C_RST}")
    print(f"  Elapsed now  : {C_YEL}{ss_elapsed}{C_RST}")
    print(f"  Interval: {args.interval}s  |  Timeout: {args.timeout}m")
    if not args.check_only:
        print(f"\n  {C_YEL}Tip: add --daemon to return immediately and keep working.{C_RST}")
    print(f"{'='*62}\n")

    snap = _poll_loop(
        run_id=run_id, repo=repo, client=client,
        interval=args.interval, timeout=args.timeout,
        check_only=args.check_only,
        do_cherry=args.cherry_pick, do_triage=args.triage,
        session_started_at=ss_at, session_started_ns=ss_ns,
        verbose=args.verbose,
    )

    if args.json_out:
        try:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(snap.to_dict(), indent=2), encoding="utf-8")
            print(f"JSON report -> {args.json_out}")
        except Exception as exc:  # noqa: BLE001
            print(f"Could not write JSON: {exc}")

    return _exit_code(snap)


if __name__ == "__main__":
    sys.exit(main())
