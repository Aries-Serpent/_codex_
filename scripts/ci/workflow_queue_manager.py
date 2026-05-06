#!/usr/bin/env python3
"""
workflow_queue_manager.py — Branch-agnostic, rate-limit-aware workflow queue
manager with cancellation.

Addresses two recurring failure modes:
  1. GitHub API rate-limit exhaustion caused by too many workflow requests in a
     short window (secondary rate-limit / "scraping / ToS" 403s).
  2. Stale queued or in_progress workflow runs that block CI resources and pile
     up when multiple pushes land in quick succession.

Branch / environment agnosticism
---------------------------------
This module makes **no assumptions** about which branch, repository, or CI
environment it is running in.  Every context value — repo slug, branch filter,
event filter, and state-file path — is resolved at runtime from the environment
or from explicit CLI arguments.  The same script runs identically on:

  • Any feature branch, release branch, or the default branch.
  • Self-hosted runners, GitHub-hosted runners, or local developer machines.
  • Any GitHub organisation / repository (not just this one).

Resolution order for the repository slug:
  1. ``--repo`` CLI argument
  2. ``GITHUB_REPOSITORY`` environment variable  (set by GitHub Actions)
  3. ``git remote get-url origin``  (auto-detect from working tree)
  4. Fail loudly with an actionable error message — no silent hardcoded default.

Resolution order for the branch filter:
  1. ``--branch`` CLI argument
  2. ``GITHUB_REF_NAME`` environment variable  (set by GitHub Actions)
  3. ``git rev-parse --abbrev-ref HEAD``  (current branch in working tree)
  4. Empty string  → no branch filter (all branches scanned).

The persistent state file is also environment-scoped via ``WQM_STATE_FILE``
so that parallel pipelines on different branches write to different files and
never corrupt each other's sliding-window counters.

Design principles
-----------------
* **Sliding-window request tracker** — all outbound GitHub API mutation calls
  (cancel, dispatch, approve) are recorded with a UTC timestamp in a persistent
  JSON state file.  Before each call the manager checks how many mutations were
  issued in the last 60 s and 3 600 s and sleeps/backs off if either window
  is full.

* **Pre-call rate-limit check** — reads /rate_limit before every batch of
  cancellations.  If core.remaining < MIN_REMAINING it rotates to the next
  token or waits for the reset epoch (capped at MAX_WAIT seconds).

* **Token rotation** — uses the same discovery order as github_api_trickle.py:
  CODEX_MASTER_KEY → CODEX_BACKUP_KEY → CODEX_ADMIN_KEY →
  AGENT_GITHUB_TOKEN → GH_TOKEN → GITHUB_TOKEN.

* **Cancellation policy** — for each workflow file, if there are more than
  MAX_QUEUED_PER_WORKFLOW queued (or waiting) runs, the oldest ones are
  cancelled, keeping only the N most-recent.  Runs that are already
  in_progress are left alone unless ``--cancel-in-progress`` is passed.

* **Dry-run mode** — ``--dry-run`` prints every action that would be taken
  without making any API mutations.

* **No shell=True** — all subprocess calls use a list of arguments.

State file schema
-----------------
Default path: .codex/workflow_queue_state.json
Override:     WQM_STATE_FILE env var or computed from branch name (see below).

{
  "lock": false,
  "last_updated": "<ISO-8601>",
  "env": {                  // resolved context written on first use
    "repo": "owner/repo",
    "branch": "my-branch"
  },
  "mutations": [            // last N mutation timestamps (ISO-8601 strings)
    "2026-05-06T15:00:00Z",
    ...
  ],
  "cancelled": {            // run_id -> {name, cancelled_at, reason}
    "12345678": {...},
    ...
  }
}

CLI usage
---------
  # Scan all branches (no filter):
  python scripts/ci/workflow_queue_manager.py --scan

  # Scan only runs on the current branch:
  python scripts/ci/workflow_queue_manager.py --scan --branch auto

  # Scan a specific branch in any repo:
  python scripts/ci/workflow_queue_manager.py --scan --repo owner/repo --branch main

  # Cancel excess queued runs (keep newest per workflow), dry-run first:
  python scripts/ci/workflow_queue_manager.py --cancel-excess --dry-run
  python scripts/ci/workflow_queue_manager.py --cancel-excess

  # Cancel excess on a specific branch only:
  python scripts/ci/workflow_queue_manager.py --cancel-excess --branch feature/my-branch

  # Cancel a specific run by ID:
  python scripts/ci/workflow_queue_manager.py --cancel-run 12345678

  # Cancel all queued runs for a specific workflow file:
  python scripts/ci/workflow_queue_manager.py --cancel-workflow validate.yml

  # Filter by event type (push, pull_request, schedule, workflow_dispatch, …):
  python scripts/ci/workflow_queue_manager.py --scan --event push

  # Adjust thresholds:
  python scripts/ci/workflow_queue_manager.py --cancel-excess \\
      --max-queued 1 --max-per-minute 10 --max-per-hour 200

Environment variables
---------------------
  CODEX_MASTER_KEY      Primary write token
  CODEX_BACKUP_KEY      Fallback PAT
  CODEX_ADMIN_KEY       Second fallback PAT
  AGENT_GITHUB_TOKEN    Third fallback
  GH_TOKEN / GITHUB_TOKEN  Last-resort token
  GITHUB_REPOSITORY     owner/repo slug  (set by GitHub Actions)
  GITHUB_REF_NAME       Branch name       (set by GitHub Actions)
  WQM_MAX_QUEUED        Override --max-queued default (2)
  WQM_MAX_PER_MINUTE    Override --max-per-minute default (20)
  WQM_MAX_PER_HOUR      Override --max-per-hour default (300)
  WQM_MIN_REMAINING     Override minimum REST remaining before token rotation (10)
  WQM_MAX_WAIT          Override maximum seconds to wait for rate-limit reset (120)
  WQM_STATE_FILE        Override path to state JSON file (default: auto per branch)
  WQM_DRY_RUN           "true" to enable dry-run without the CLI flag

Security note (subprocess)
--------------------------
All subprocess calls use ``shell=False`` (list-of-strings form).  No
user-supplied data is ever inserted into a shell command string.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] wqm: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("wqm")

# ── Constants / defaults ──────────────────────────────────────────────────────
_BASE = "https://api.github.com"

# How many queued runs per workflow are acceptable before we start cancelling.
MAX_QUEUED_PER_WORKFLOW: int = int(os.environ.get("WQM_MAX_QUEUED", "2"))

# Sliding-window limits for outbound *mutation* API calls (cancel / dispatch).
MAX_MUTATIONS_PER_MINUTE: int = int(os.environ.get("WQM_MAX_PER_MINUTE", "20"))
MAX_MUTATIONS_PER_HOUR: int = int(os.environ.get("WQM_MAX_PER_HOUR", "300"))

# Rate-limit guard: if core.remaining drops below this, rotate token or wait.
MIN_REMAINING: int = int(os.environ.get("WQM_MIN_REMAINING", "10"))

# Maximum seconds to wait when all tokens are exhausted.
MAX_WAIT: float = float(os.environ.get("WQM_MAX_WAIT", "120"))

# Statuses considered "waiting" (eligible for cancellation under excess policy).
_QUEUED_STATUSES = {"queued", "waiting"}

# Keep at most this many mutation timestamps in the state file.
_MAX_MUTATION_HISTORY = 1000

# Sentinel used when --branch auto is requested but detection fails.
_BRANCH_UNDETECTED = ""

# Maximum length of a sanitised branch name used as a filename component.
# Keeps state-file paths within FS limits on all platforms.
_MAX_BRANCH_NAME_LENGTH = 64

# Polite sleep between paginated list requests to avoid secondary rate-limit.
_PAGINATION_DELAY_SECONDS = 0.3

# Clock-skew buffer added to rate-limit reset epoch before sleeping.
_RATE_LIMIT_RESET_BUFFER_SECONDS = 2

# Optimistic fallback when /rate_limit returns no data for a token; allows
# operations to proceed when quota information is temporarily unavailable.
_ASSUMED_REMAINING_ON_ERROR = 999


# ── Environment / context resolution ─────────────────────────────────────────
def _resolve_repo(explicit: str = "") -> str:
    """
    Resolve the owner/repo slug with no hardcoded fallback.

    Resolution order:
      1. ``explicit`` argument (from --repo CLI flag)
      2. ``GITHUB_REPOSITORY`` environment variable  (set by GitHub Actions)
      3. ``git remote get-url origin``  (current working tree)
      4. Raises RuntimeError with an actionable message.
    """
    if explicit.strip():
        return explicit.strip()

    env_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env_repo:
        return env_repo

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5, shell=False,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            for prefix in ("https://github.com/", "git@github.com:"):
                if url.startswith(prefix):
                    slug = url[len(prefix):].removesuffix(".git")
                    if "/" in slug:
                        return slug
    except Exception as exc:
        log.debug("git remote URL resolution failed; continuing to fallback: %s", exc, exc_info=True)

    raise RuntimeError(
        "Cannot determine repository slug.\n"
        "Provide one of:\n"
        "  --repo owner/repo\n"
        "  export GITHUB_REPOSITORY=owner/repo\n"
        "  Run from inside a git working tree with a GitHub remote."
    )


def _resolve_branch(explicit: str = "") -> str:
    """
    Resolve the branch name for API filtering.

    Resolution order:
      1. ``explicit`` argument (from --branch CLI flag), unless it equals
         the special token ``"auto"`` which triggers auto-detection.
      2. ``GITHUB_REF_NAME`` environment variable  (set by GitHub Actions)
      3. ``git rev-parse --abbrev-ref HEAD``  (current branch in working tree)
      4. Empty string  → no branch filter (all branches).

    Returns empty string when no branch can be determined (meaning the caller
    should not add a branch filter to API requests).
    """
    # Explicit non-auto value wins immediately
    if explicit.strip() and explicit.strip().lower() != "auto":
        return explicit.strip()

    # GitHub Actions injects GITHUB_REF_NAME (branch or tag name)
    env_branch = os.environ.get("GITHUB_REF_NAME", "").strip()
    if env_branch:
        return env_branch

    # Fallback: ask git
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5, shell=False,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            if branch and branch != "HEAD":
                return branch
    except Exception as exc:
        log.debug("git branch auto-detection failed; falling back to no-filter: %s", exc, exc_info=True)

    if explicit.strip().lower() == "auto":
        log.warning(
            "--branch auto requested but branch could not be detected; "
            "scanning all branches"
        )
    return _BRANCH_UNDETECTED


def _state_file_for_branch(branch: str) -> Path:
    """
    Return the path to the state file for a given branch.

    If WQM_STATE_FILE is set explicitly, that path is always used regardless
    of branch (useful when the caller wants a single shared state).

    Otherwise each branch gets its own file so parallel branch pipelines
    never corrupt each other's sliding-window counters:
      .codex/wqm_state_<safe_branch>.json

    The branch name is sanitised — only alphanumerics, hyphens, and dots are
    kept, matching what is safe as a filename on all platforms.
    """
    env_override = os.environ.get("WQM_STATE_FILE", "").strip()
    if env_override:
        return Path(env_override)

    if not branch:
        return Path(".codex/workflow_queue_state.json")

    # Sanitise: keep only alphanumerics, hyphens, and underscores.
    # Dots are intentionally excluded — a dot-containing filename like
    # "wqm_state_feature.test.json" can be misread as having a different
    # extension, which confuses some tooling and glob patterns.
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in branch)
    safe = safe[:_MAX_BRANCH_NAME_LENGTH]
    return Path(f".codex/wqm_state_{safe}.json")


# ── Token discovery ───────────────────────────────────────────────────────────
def _discover_tokens() -> list[str]:
    """Return deduplicated list of available GitHub tokens, highest privilege first."""
    candidates = [
        os.environ.get("CODEX_MASTER_KEY"),
        os.environ.get("CODEX_BACKUP_KEY"),
        os.environ.get("CODEX_ADMIN_KEY"),
        os.environ.get("AGENT_GITHUB_TOKEN"),
        os.environ.get("GH_TOKEN"),
        os.environ.get("GITHUB_TOKEN"),
    ]
    seen: set[str] = set()
    tokens: list[str] = []
    for t in candidates:
        if t and t.strip() and t not in seen:
            seen.add(t)
            tokens.append(t)
    if not tokens:
        log.warning(
            "No GitHub tokens discovered — unauthenticated requests will be "
            "heavily rate-limited.  Set CODEX_MASTER_KEY, GH_TOKEN, or "
            "GITHUB_TOKEN in your environment."
        )
    else:
        log.debug("Token discovery: %d unique token(s) found", len(tokens))
    return tokens


_TOKENS: list[str] = _discover_tokens()


# ── State file helpers ────────────────────────────────────────────────────────
def _load_state(state_file: Path) -> dict[str, Any]:
    """Load and return the persistent state for *state_file*, creating it if absent."""
    if state_file.exists():
        try:
            with state_file.open() as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("State file corrupt (%s) — resetting: %s", state_file, exc)
    return {"lock": False, "last_updated": "", "env": {}, "mutations": [], "cancelled": {}}


def _save_state(state: dict[str, Any], state_file: Path) -> None:
    """Persist state to disk atomically, creating parent directories as needed."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = _now_iso()
    try:
        tmp = state_file.with_suffix(".tmp")
        with tmp.open("w") as fh:
            json.dump(state, fh, indent=2)
        tmp.replace(state_file)
    except OSError as exc:
        log.error("Failed to save state file %s: %s", state_file, exc)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_ts() -> float:
    return time.time()


# ── Sliding-window rate tracker ───────────────────────────────────────────────
def _prune_mutations(mutations: list[str]) -> list[str]:
    """Remove mutation timestamps older than 1 hour; trim to max history."""
    cutoff = _now_ts() - 3600
    pruned = [m for m in mutations if _iso_to_ts(m) > cutoff]
    return pruned[-_MAX_MUTATION_HISTORY:]


def _iso_to_ts(iso: str) -> float:
    """Convert ISO-8601 UTC string to POSIX timestamp."""
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return 0.0


def _count_mutations_in_window(mutations: list[str], window_seconds: float) -> int:
    """Return number of mutations within the last ``window_seconds``."""
    cutoff = _now_ts() - window_seconds
    return sum(1 for m in mutations if _iso_to_ts(m) > cutoff)


def _enforce_sliding_window_limit(
    state: dict[str, Any],
    state_file: Path,
    *,
    dry_run: bool = False,
) -> None:
    """
    Block until the sliding-window mutation rate is within limits.

    Checks both the per-minute and per-hour windows.  When either limit is
    reached, sleeps in small increments (5 s) and re-checks until the window
    clears.  This prevents secondary rate-limit 403s caused by rapid bursts.
    """
    mutations = state.get("mutations", [])
    while True:
        per_minute = _count_mutations_in_window(mutations, 60)
        per_hour = _count_mutations_in_window(mutations, 3600)

        if per_minute >= MAX_MUTATIONS_PER_MINUTE:
            wait = 5
            if dry_run:
                log.info("[DRY] Would wait %ds (per-minute limit %d/%d reached)",
                         wait, per_minute, MAX_MUTATIONS_PER_MINUTE)
                return
            log.warning(
                "Sliding-window: %d mutations in last 60 s (limit %d) — waiting %ds",
                per_minute, MAX_MUTATIONS_PER_MINUTE, wait,
            )
            time.sleep(wait)
            # Re-read mutations from disk in case another process updated state
            state = _load_state(state_file)
            mutations = state.get("mutations", [])
            continue

        if per_hour >= MAX_MUTATIONS_PER_HOUR:
            wait = 30
            if dry_run:
                log.info("[DRY] Would wait %ds (per-hour limit %d/%d reached)",
                         wait, per_hour, MAX_MUTATIONS_PER_HOUR)
                return
            log.warning(
                "Sliding-window: %d mutations in last 3600 s (limit %d) — waiting %ds",
                per_hour, MAX_MUTATIONS_PER_HOUR, wait,
            )
            time.sleep(wait)
            state = _load_state(state_file)
            mutations = state.get("mutations", [])
            continue

        # Within limits
        break


def _record_mutation(state: dict[str, Any], state_file: Path) -> None:
    """Append the current timestamp to the mutation log and persist."""
    mutations: list[str] = state.get("mutations", [])
    mutations.append(_now_iso())
    state["mutations"] = _prune_mutations(mutations)
    _save_state(state, state_file)


# ── GitHub API helpers ────────────────────────────────────────────────────────
def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-workflow-queue-manager/1.0",
    }


def _check_rate_limits(token: str) -> dict[str, Any]:
    """Return /rate_limit resources dict for *token*; {} on failure."""
    try:
        req = urllib.request.Request(
            f"{_BASE}/rate_limit",
            headers=_headers(token),
        )  # noqa: S310  # _BASE is the constant https://api.github.com
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            data = json.load(resp)
        return data.get("resources", {})
    except Exception as exc:
        log.debug("rate_limit check failed: %s", exc)
        return {}


def _pick_token(tokens: list[str]) -> str | None:
    """
    Return the first token that has sufficient core API remaining quota.
    Waits up to MAX_WAIT seconds if all tokens are exhausted.
    Returns None if no valid tokens are available at all.
    """
    if not tokens:
        return None

    for token in tokens:
        limits = _check_rate_limits(token)
        core = limits.get("core", {})
        remaining = core.get("remaining", _ASSUMED_REMAINING_ON_ERROR)
        reset_at = core.get("reset", 0)

        if remaining >= MIN_REMAINING:
            return token

        # This token is exhausted; check if we should wait for its reset
        wait_needed = max(0, reset_at - _now_ts()) + _RATE_LIMIT_RESET_BUFFER_SECONDS
        if wait_needed <= MAX_WAIT:
            log.info(
                "Token exhausted (remaining=%d) — waiting %.0fs for reset",
                remaining, wait_needed,
            )
            time.sleep(wait_needed)
            # Re-check after sleep
            limits2 = _check_rate_limits(token)
            remaining2 = limits2.get("core", {}).get("remaining", 0)
            if remaining2 >= MIN_REMAINING:
                return token

        log.info("Token slot exhausted (remaining=%d, reset too far) — trying next", remaining)

    log.warning("All tokens exhausted — proceeding anyway with first token (may 429)")
    return tokens[0]


def _validate_api_path(path: str) -> None:
    """
    Raise ValueError if *path* looks suspicious.

    Allowed: starts with "/" and contains no "://" sequence.
    This prevents a constructed path from accidentally supplying an absolute
    URL and bypassing the intended _BASE host.
    """
    if not path.startswith("/"):
        raise ValueError(f"API path must start with '/': {path!r}")
    if "://" in path:
        raise ValueError(f"API path must not contain a URL scheme: {path!r}")


def _gh_get(path: str, token: str) -> tuple[int, Any]:
    """GET {_BASE}{path}. Returns (status_code, parsed_body)."""
    _validate_api_path(path)
    url = f"{_BASE}{path}"
    req = urllib.request.Request(url, headers=_headers(token))  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except Exception:
            body = {}
        return exc.code, body
    except Exception as exc:
        log.debug("GET %s failed: %s", path[:80], exc)
        return 0, {}


def _gh_post(path: str, token: str, body: dict | None = None) -> tuple[int, Any]:
    """POST {_BASE}{path}. Returns (status_code, parsed_body)."""
    _validate_api_path(path)
    url = f"{_BASE}{path}"
    data = json.dumps(body).encode() if body else b""
    req = urllib.request.Request(
        url,
        data=data,
        headers={**_headers(token), "Content-Type": "application/json"},
        method="POST",
    )  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            raw = resp.read()
            parsed = json.loads(raw) if raw.strip() else {}
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        try:
            resp_body = json.loads(exc.read())
        except Exception:
            resp_body = {}
        return exc.code, resp_body
    except Exception as exc:
        log.debug("POST %s failed: %s", path[:80], exc)
        return 0, {}


# ── Workflow run listing ──────────────────────────────────────────────────────
def _list_runs_by_status(
    repo: str,
    status: str,
    token: str,
    *,
    branch: str = "",
    event: str = "",
    per_page: int = 100,
) -> list[dict[str, Any]]:
    """
    Return all workflow runs with the given status.

    Optional filters (branch and event) are passed verbatim as GitHub API query
    parameters — they are not validated here so that any future GitHub API
    extension automatically works without changes to this function.

    Paginates automatically.  Adds a polite 0.3 s sleep between pages to
    avoid secondary rate-limit triggers.
    """
    runs: list[dict[str, Any]] = []
    page = 1
    while True:
        path = (
            f"/repos/{repo}/actions/runs"
            f"?status={status}&per_page={per_page}&page={page}"
        )
        if branch:
            path += f"&branch={urllib.parse.quote(branch, safe='')}"
        if event:
            path += f"&event={urllib.parse.quote(event, safe='')}"
        status_code, data = _gh_get(path, token)
        if status_code == 403:
            msg = data.get("message", "") if isinstance(data, dict) else ""
            log.warning("GET runs HTTP 403 (possible rate-limit): %s", msg[:100])
            break
        if status_code != 200 or not isinstance(data, dict):
            log.debug("GET runs HTTP %d — stopping pagination", status_code)
            break
        batch: list[dict] = data.get("workflow_runs", [])
        runs.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(_PAGINATION_DELAY_SECONDS)  # polite pause between pages
    return runs


def list_queued_runs(
    repo: str,
    token: str,
    *,
    branch: str = "",
    event: str = "",
) -> list[dict[str, Any]]:
    """Return all runs in 'queued' or 'waiting' status, optionally filtered."""
    result: list[dict[str, Any]] = []
    for status in _QUEUED_STATUSES:
        result.extend(_list_runs_by_status(repo, status, token, branch=branch, event=event))
    return result


def list_in_progress_runs(
    repo: str,
    token: str,
    *,
    branch: str = "",
    event: str = "",
) -> list[dict[str, Any]]:
    """Return all currently in_progress runs, optionally filtered."""
    return _list_runs_by_status(repo, "in_progress", token, branch=branch, event=event)


# ── Cancellation ──────────────────────────────────────────────────────────────
def cancel_run(
    run_id: int,
    run_name: str,
    repo: str,
    token: str,
    state: dict[str, Any],
    state_file: Path,
    *,
    dry_run: bool = False,
    reason: str = "excess queue depth",
) -> bool:
    """
    Cancel a single workflow run with full rate-limit and sliding-window
    enforcement.

    Returns True if the run was cancelled (or would have been in dry-run).
    """
    label = f"{run_name} (run #{run_id})"

    if dry_run:
        log.info("[DRY] Would cancel: %s — reason: %s", label, reason)
        return True

    # Enforce sliding-window limit before every mutation
    _enforce_sliding_window_limit(state, state_file, dry_run=False)

    path = f"/repos/{repo}/actions/runs/{run_id}/cancel"
    status_code, body = _gh_post(path, token)

    _record_mutation(state, state_file)  # always record the attempt

    if status_code in (202, 204):
        log.info("✅ Cancelled: %s", label)
        state.setdefault("cancelled", {})[str(run_id)] = {
            "name": run_name,
            "cancelled_at": _now_iso(),
            "reason": reason,
        }
        _save_state(state, state_file)
        return True

    if status_code == 409:
        log.info("⏭️  Run %s already completed — nothing to cancel", label)
        return False

    if status_code == 403:
        msg = body.get("message", "") if isinstance(body, dict) else str(body)
        if "rate limit" in msg.lower() or "abuse" in msg.lower():
            log.warning("Rate-limited while cancelling %s — backing off 30 s", label)
            time.sleep(30)
        else:
            log.warning("403 cancelling %s: %s", label, msg[:120])
        return False

    msg = body.get("message", "") if isinstance(body, dict) else str(body)
    log.warning("HTTP %d cancelling %s: %s", status_code, label, msg[:120])
    return False


# ── Excess-queue cancellation policy ─────────────────────────────────────────
def _group_runs_by_workflow(runs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group runs by workflow_id (str) for per-workflow policy enforcement."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        wf_id = str(run.get("workflow_id", run.get("id", "unknown")))
        groups.setdefault(wf_id, []).append(run)
    return groups


def cancel_excess_queued_runs(
    repo: str,
    tokens: list[str],
    state: dict[str, Any],
    state_file: Path,
    *,
    max_queued: int = MAX_QUEUED_PER_WORKFLOW,
    cancel_in_progress: bool = False,
    branch: str = "",
    event: str = "",
    dry_run: bool = False,
) -> dict[str, int]:
    """
    For every workflow that has more than ``max_queued`` queued runs, cancel
    the oldest ones so that at most ``max_queued`` remain.

    ``branch`` and ``event`` are forwarded to the GitHub API list calls so
    that only runs on the target branch / triggered by the given event are
    considered.  Pass empty strings to operate across all branches/events.

    Returns a summary dict: {workflow_path: number_cancelled}.
    """
    token = _pick_token(tokens)
    if token is None:
        log.error("No token available — aborting cancel_excess_queued_runs")
        return {}

    filter_desc = ""
    if branch:
        filter_desc += f" branch={branch}"
    if event:
        filter_desc += f" event={event}"
    log.info("Scanning for queued workflow runs (repo=%s%s)…", repo, filter_desc)

    queued = list_queued_runs(repo, token, branch=branch, event=event)
    log.info("Found %d queued/waiting run(s)", len(queued))

    candidates = list(queued)
    if cancel_in_progress:
        in_prog = list_in_progress_runs(repo, token, branch=branch, event=event)
        log.info(
            "Found %d in_progress run(s) (included per --cancel-in-progress)",
            len(in_prog),
        )
        candidates.extend(in_prog)

    if not candidates:
        log.info("No runs eligible for cancellation.")
        return {}

    groups = _group_runs_by_workflow(candidates)
    summary: dict[str, int] = {}

    for wf_id, runs in groups.items():
        sorted_runs = sorted(runs, key=lambda r: r.get("run_number", 0))
        wf_path = sorted_runs[-1].get("path", wf_id)

        excess = len(sorted_runs) - max_queued
        if excess <= 0:
            log.debug(
                "Workflow %s: %d run(s) ≤ max %d — no action",
                wf_path, len(sorted_runs), max_queued,
            )
            continue

        log.info(
            "Workflow %s: %d run(s) queued (max %d) — will cancel %d oldest",
            wf_path, len(sorted_runs), max_queued, excess,
        )

        cancelled_count = 0
        for run in sorted_runs[:excess]:
            run_id = run["id"]
            run_name = run.get("name", wf_path)
            ok = cancel_run(
                run_id, run_name, repo, token, state, state_file,
                dry_run=dry_run,
                reason=f"excess queue depth ({len(sorted_runs)} > {max_queued})",
            )
            if ok:
                cancelled_count += 1

        if cancelled_count:
            summary[wf_path] = cancelled_count

    return summary


def cancel_workflow_all_queued(
    workflow_file: str,
    repo: str,
    tokens: list[str],
    state: dict[str, Any],
    state_file: Path,
    *,
    branch: str = "",
    event: str = "",
    dry_run: bool = False,
) -> int:
    """Cancel all queued runs for a specific workflow file name. Returns count cancelled."""
    token = _pick_token(tokens)
    if token is None:
        log.error("No token available")
        return 0

    queued = list_queued_runs(repo, token, branch=branch, event=event)
    matching = [
        r for r in queued
        if workflow_file in (r.get("path", ""), r.get("name", ""))
    ]

    if not matching:
        log.info("No queued runs found for workflow %s", workflow_file)
        return 0

    log.info("Found %d queued run(s) for %s", len(matching), workflow_file)
    count = 0
    for run in matching:
        ok = cancel_run(
            run["id"], run.get("name", workflow_file),
            repo, token, state, state_file,
            dry_run=dry_run,
            reason=f"manual cancel of all queued runs for {workflow_file}",
        )
        if ok:
            count += 1
    return count


def cancel_run_by_id(
    run_id: int,
    repo: str,
    tokens: list[str],
    state: dict[str, Any],
    state_file: Path,
    *,
    dry_run: bool = False,
) -> bool:
    """Cancel a single run by its numeric ID."""
    token = _pick_token(tokens)
    if token is None:
        log.error("No token available")
        return False

    status_code, run_data = _gh_get(f"/repos/{repo}/actions/runs/{run_id}", token)
    run_name = run_data.get("name", f"run-{run_id}") if isinstance(run_data, dict) else f"run-{run_id}"

    return cancel_run(
        run_id, run_name, repo, token, state, state_file,
        dry_run=dry_run,
        reason="explicit --cancel-run request",
    )


# ── Scan / report ─────────────────────────────────────────────────────────────
def scan_and_report(
    repo: str,
    tokens: list[str],
    *,
    branch: str = "",
    event: str = "",
) -> dict[str, Any]:
    """
    List all queued and in_progress runs, print a report, and return the data.
    Does not make any mutations.

    ``branch`` and ``event`` narrow the results to a specific branch/event;
    pass empty strings to scan all branches and all event types.
    """
    token = _pick_token(tokens)
    if token is None:
        log.error("No token available for scan")
        return {}

    queued = list_queued_runs(repo, token, branch=branch, event=event)
    in_prog = list_in_progress_runs(repo, token, branch=branch, event=event)

    filter_parts: list[str] = []
    if branch:
        filter_parts.append(f"branch={branch}")
    if event:
        filter_parts.append(f"event={event}")
    filter_desc = f"  [{', '.join(filter_parts)}]" if filter_parts else "  [all branches / all events]"

    report: dict[str, Any] = {
        "scanned_at": _now_iso(),
        "repo": repo,
        "branch_filter": branch or None,
        "event_filter": event or None,
        "queued_count": len(queued),
        "in_progress_count": len(in_prog),
        "queued_runs": [],
        "in_progress_runs": [],
        "rate_limits": _check_rate_limits(token),
    }

    print(f"\n{'─'*60}")
    print(f"📋 Workflow Queue Report — {repo}{filter_desc}")
    print(f"   Scanned at : {report['scanned_at']}")
    core = report["rate_limits"].get("core", {})
    reset_ts = core.get("reset", 0)
    reset_str = (
        datetime.fromtimestamp(reset_ts, tz=timezone.utc).strftime("%H:%M:%S UTC")
        if reset_ts else "?"
    )
    print(
        f"   Rate-limit : {core.get('remaining', '?')}/{core.get('limit', '?')} remaining "
        f"(resets {reset_str})"
    )
    print(f"{'─'*60}")

    for section, runs, emoji in [
        ("QUEUED / WAITING", queued, "⏳"),
        ("IN PROGRESS", in_prog, "🔄"),
    ]:
        print(f"\n{emoji} {section} ({len(runs)} run(s)):")
        if not runs:
            print("   (none)")
        for run in sorted(runs, key=lambda r: r.get("run_number", 0)):
            run_id = run["id"]
            run_name = run.get("name", "?")
            run_number = run.get("run_number", "?")
            created = run.get("created_at", "?")
            wf_path = run.get("path", "?")
            run_branch = run.get("head_branch", "?")
            print(
                f"   #{run_number:>8}  id={run_id}  {run_name:<35}  "
                f"branch={run_branch:<25}  created={created}  [{wf_path}]"
            )

    groups = _group_runs_by_workflow(queued)
    excess_wfs = {
        wf_id: runs
        for wf_id, runs in groups.items()
        if len(runs) > MAX_QUEUED_PER_WORKFLOW
    }
    if excess_wfs:
        print(f"\n⚠️  Workflows exceeding max_queued={MAX_QUEUED_PER_WORKFLOW}:")
        for wf_id, runs in excess_wfs.items():
            wf_path = runs[-1].get("path", wf_id)
            excess = len(runs) - MAX_QUEUED_PER_WORKFLOW
            print(
                f"   {wf_path} — {len(runs)} queued "
                f"(cancel-excess will remove {excess})"
            )
    else:
        print(f"\n✅ No workflows exceed max_queued={MAX_QUEUED_PER_WORKFLOW}")

    print(f"{'─'*60}\n")

    report["queued_runs"] = [
        {
            "id": r["id"],
            "name": r.get("name"),
            "run_number": r.get("run_number"),
            "created_at": r.get("created_at"),
            "head_branch": r.get("head_branch"),
            "path": r.get("path"),
        }
        for r in queued
    ]
    report["in_progress_runs"] = [
        {
            "id": r["id"],
            "name": r.get("name"),
            "run_number": r.get("run_number"),
            "created_at": r.get("created_at"),
            "head_branch": r.get("head_branch"),
            "path": r.get("path"),
        }
        for r in in_prog
    ]
    return report


# ── CLI ───────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workflow_queue_manager",
        description=(
            "Branch-agnostic, rate-limit-aware GitHub Actions workflow queue "
            "manager with cancellation."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/ci/workflow_queue_manager.py --scan\n"
            "  python scripts/ci/workflow_queue_manager.py --scan --branch auto\n"
            "  python scripts/ci/workflow_queue_manager.py --scan --repo owner/repo --branch main\n"
            "  python scripts/ci/workflow_queue_manager.py --cancel-excess --dry-run\n"
            "  python scripts/ci/workflow_queue_manager.py --cancel-excess --branch feature/x\n"
            "  python scripts/ci/workflow_queue_manager.py --cancel-run 12345678\n"
            "  python scripts/ci/workflow_queue_manager.py --cancel-workflow validate.yml\n"
            "  python scripts/ci/workflow_queue_manager.py --scan --event push\n"
        ),
    )
    parser.add_argument(
        "--repo",
        default="",
        metavar="OWNER/REPO",
        help=(
            "GitHub repository slug.  "
            "Resolved from $GITHUB_REPOSITORY or git remote when omitted."
        ),
    )
    parser.add_argument(
        "--branch",
        default="",
        metavar="BRANCH|auto",
        help=(
            "Filter runs by branch name.  "
            "Use 'auto' to detect from $GITHUB_REF_NAME or current git branch.  "
            "Omit to operate across all branches."
        ),
    )
    parser.add_argument(
        "--event",
        default="",
        metavar="EVENT",
        help=(
            "Filter runs by trigger event "
            "(push, pull_request, schedule, workflow_dispatch, …).  "
            "Omit to include all events."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.environ.get("WQM_DRY_RUN", "").lower() == "true",
        help="Print actions without making API mutations.",
    )
    parser.add_argument(
        "--max-queued",
        type=int,
        default=MAX_QUEUED_PER_WORKFLOW,
        metavar="N",
        help=f"Maximum queued runs per workflow before cancelling excess (default: {MAX_QUEUED_PER_WORKFLOW}).",
    )
    parser.add_argument(
        "--max-per-minute",
        type=int,
        default=MAX_MUTATIONS_PER_MINUTE,
        metavar="N",
        help=f"Sliding-window per-minute mutation cap (default: {MAX_MUTATIONS_PER_MINUTE}).",
    )
    parser.add_argument(
        "--max-per-hour",
        type=int,
        default=MAX_MUTATIONS_PER_HOUR,
        metavar="N",
        help=f"Sliding-window per-hour mutation cap (default: {MAX_MUTATIONS_PER_HOUR}).",
    )
    parser.add_argument(
        "--cancel-in-progress",
        action="store_true",
        help="Include in_progress runs when applying the excess-queue policy.",
    )
    parser.add_argument(
        "--json-out",
        metavar="FILE",
        help="Write the scan/summary report as JSON to FILE.",
    )

    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "--scan",
        action="store_true",
        help="List queued and in_progress runs without making changes.",
    )
    actions.add_argument(
        "--cancel-excess",
        action="store_true",
        help="Cancel oldest queued runs exceeding --max-queued per workflow.",
    )
    actions.add_argument(
        "--cancel-run",
        type=int,
        metavar="RUN_ID",
        help="Cancel a specific workflow run by its numeric ID.",
    )
    actions.add_argument(
        "--cancel-workflow",
        metavar="WORKFLOW_FILE",
        help="Cancel all queued runs for a specific workflow file (e.g. validate.yml).",
    )
    return parser


# ── Configuration dataclass (avoids mutating module-level globals) ─────────────
class _RunConfig:
    """Holds resolved runtime configuration for a single main() invocation."""

    __slots__ = (
        "repo", "branch", "event", "tokens", "dry_run",
        "max_queued", "max_per_minute", "max_per_hour",
        "cancel_in_progress", "state_file",
    )

    def __init__(self, args: argparse.Namespace, tokens: list[str]) -> None:
        self.repo: str = ""             # resolved below
        self.branch: str = ""
        self.event: str = args.event.strip()
        self.tokens: list[str] = tokens
        self.dry_run: bool = args.dry_run
        self.max_queued: int = args.max_queued
        self.max_per_minute: int = args.max_per_minute
        self.max_per_hour: int = args.max_per_hour
        self.cancel_in_progress: bool = args.cancel_in_progress
        self.state_file: Path = Path()  # resolved below


# ── Action handlers ───────────────────────────────────────────────────────────
def _handle_scan(
    cfg: _RunConfig,
    state: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[Any, int]:
    result = scan_and_report(cfg.repo, cfg.tokens, branch=cfg.branch, event=cfg.event)
    return result, 0


def _handle_cancel_excess(
    cfg: _RunConfig,
    state: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[Any, int]:
    result = cancel_excess_queued_runs(
        cfg.repo, cfg.tokens, state, cfg.state_file,
        max_queued=cfg.max_queued,
        cancel_in_progress=cfg.cancel_in_progress,
        branch=cfg.branch,
        event=cfg.event,
        dry_run=cfg.dry_run,
    )
    if result:
        print("\n📋 Cancellation summary:")
        for wf_path, count in result.items():
            verb = "Would cancel" if cfg.dry_run else "Cancelled"
            print(f"   {wf_path}: {verb} {count} run(s)")
    else:
        print("✅ No excess queued runs — nothing to cancel")
    return result, 0


def _handle_cancel_run(
    cfg: _RunConfig,
    state: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[Any, int]:
    ok = cancel_run_by_id(
        args.cancel_run, cfg.repo, cfg.tokens, state, cfg.state_file,
        dry_run=cfg.dry_run,
    )
    result = {"run_id": args.cancel_run, "cancelled": ok}
    return result, 0 if (ok or cfg.dry_run) else 1


def _handle_cancel_workflow(
    cfg: _RunConfig,
    state: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[Any, int]:
    count = cancel_workflow_all_queued(
        args.cancel_workflow, cfg.repo, cfg.tokens, state, cfg.state_file,
        branch=cfg.branch,
        event=cfg.event,
        dry_run=cfg.dry_run,
    )
    result = {"workflow": args.cancel_workflow, "cancelled": count}
    verb = "Would cancel" if cfg.dry_run else "Cancelled"
    print(f"\n{verb} {count} queued run(s) for {args.cancel_workflow}")
    return result, 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Resolve context — repo resolution fails loudly with an actionable message
    try:
        repo = _resolve_repo(args.repo)
    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    branch = _resolve_branch(args.branch)

    cfg = _RunConfig(args, _TOKENS)
    cfg.repo = repo
    cfg.branch = branch
    cfg.state_file = _state_file_for_branch(branch)

    if cfg.dry_run:
        log.info("🔍 DRY-RUN mode — no API mutations will be made")

    log.info(
        "Context: repo=%s  branch=%s  event=%s  state_file=%s",
        cfg.repo, cfg.branch or "(all)", cfg.event or "(all)", cfg.state_file,
    )

    state = _load_state(cfg.state_file)
    state["env"] = {
        "repo": cfg.repo,
        "branch": cfg.branch or None,
        "event": cfg.event or None,
    }
    state["mutations"] = _prune_mutations(state.get("mutations", []))

    # Dispatch to the appropriate handler
    _handlers = {
        "scan": (args.scan, _handle_scan),
        "cancel_excess": (args.cancel_excess, _handle_cancel_excess),
        "cancel_run": (args.cancel_run is not None, _handle_cancel_run),
        "cancel_workflow": (bool(args.cancel_workflow), _handle_cancel_workflow),
    }

    result: Any = {}
    exit_code = 0
    for _name, (active, handler) in _handlers.items():
        if active:
            result, exit_code = handler(cfg, state, args)
            break

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w") as fh:
            json.dump(result, fh, indent=2)
        log.info("Report written to %s", args.json_out)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
