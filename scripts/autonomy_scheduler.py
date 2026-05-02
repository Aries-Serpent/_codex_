#!/usr/bin/env python3
"""
Phase 1: Full Autonomy Enhancement — Autonomy Scheduler

Self-driving decision loop that evaluates codebase health, proposes actions,
enforces budget limits, and records decisions to memory/sessions/.

Usage:
    python scripts/autonomy_scheduler.py [--dry-run] [--max-iterations N] [--budget-seconds N]

Environment Variables:
    AUTONOMY_BUDGET_SECONDS  Max wall-clock seconds per run (default: 300)
    AUTONOMY_MAX_ITERATIONS  Max decision iterations (default: 10)
    AUTONOMY_DRY_RUN         Set to "1" to disable mutating actions
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Re-export budget_cap from budget_uncertainty so callers can access it via
# this module's namespace without knowing the exact source location.
# Import is deferred / optional to avoid circular deps if budget_uncertainty
# is not installed.  Listed in __all__ to satisfy static-analysis re-export checks.
try:
    from budget_uncertainty import budget_cap
except ImportError:
    budget_cap = None  # type: ignore[assignment]

__all__ = [
    "budget_cap",
    "BudgetExceededError",
    "BUDGET_SECONDS",
    "MAX_ITERATIONS",
    "DRY_RUN",
    "KILL_SWITCH",
    "sense_json_health",
    "sense_yaml_health",
    "sense_test_health",
    "decide_actions",
    "write_session",
    "run",
    "run_autonomy_loop",
    "main",
]

# ── Configuration ─────────────────────────────────────────────────────────────

BUDGET_SECONDS = int(os.environ.get("AUTONOMY_BUDGET_SECONDS", "300"))
MAX_ITERATIONS = int(os.environ.get("AUTONOMY_MAX_ITERATIONS", "10"))
DRY_RUN = os.environ.get("AUTONOMY_DRY_RUN", "0") == "1"
# Emergency stop: set AGENT_KILL_SWITCH=1 to immediately halt all agent loops
KILL_SWITCH = os.environ.get("AGENT_KILL_SWITCH", "0") == "1"

REPO_ROOT = Path(__file__).parent.parent
SESSION_DIR = REPO_ROOT / "memory" / "sessions"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger("autonomy_scheduler")


# ── Budget enforcement decorator ───────────────────────────────────────────────

class BudgetExceededError(RuntimeError):
    pass


def with_budget(func, deadline: float):
    """Wrap a callable; raise BudgetExceededError if deadline passed."""
    def wrapper(*args, **kwargs):
        if time.monotonic() > deadline:
            raise BudgetExceededError(f"Budget exceeded before calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


# ── Health sensors ─────────────────────────────────────────────────────────────

def _run(cmd: list[str], cwd: Path = REPO_ROOT, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)


def sense_json_health() -> dict[str, Any]:
    """Check that all JSON files under .codex/ and docs/ are valid."""
    invalid = []
    for pattern in [".codex/**/*.json", "docs/**/*.json"]:
        for f in REPO_ROOT.glob(pattern):
            if "__pycache__" in str(f):
                continue
            try:
                json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                invalid.append({"file": str(f.relative_to(REPO_ROOT)), "error": str(exc)})
    return {"status": "ok" if not invalid else "degraded", "invalid_json_files": invalid}


def sense_yaml_health() -> dict[str, Any]:
    """Check YAML syntax for all active workflow files."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return {"status": "unknown", "reason": "pyyaml not installed"}

    errors = []
    for wf in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
        try:
            yaml.safe_load(wf.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append({"file": wf.name, "error": str(exc)})
    return {"status": "ok" if not errors else "degraded", "yaml_errors": errors}


def sense_test_health() -> dict[str, Any]:
    """Run pytest --collect-only to detect collection errors (fast)."""
    result = _run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--no-header", "tests/"],
        timeout=60,
    )
    return {
        "status": "ok" if result.returncode == 0 else "degraded",
        "returncode": result.returncode,
        "stderr_snippet": result.stderr[-400:] if result.stderr else "",
    }


# ── Decision engine ────────────────────────────────────────────────────────────

def decide_actions(health: dict[str, Any]) -> list[dict[str, Any]]:
    """Map health observations to proposed actions."""
    actions = []
    if health.get("json", {}).get("status") == "degraded":
        for bad in health["json"].get("invalid_json_files", []):
            actions.append({
                "type": "alert",
                "priority": "high",
                "description": f"Invalid JSON: {bad['file']}",
                "detail": bad["error"],
            })
    if health.get("yaml", {}).get("status") == "degraded":
        for err in health["yaml"].get("yaml_errors", []):
            actions.append({
                "type": "alert",
                "priority": "high",
                "description": f"YAML error: {err['file']}",
                "detail": err["error"],
            })
    if health.get("tests", {}).get("status") == "degraded":
        actions.append({
            "type": "alert",
            "priority": "medium",
            "description": "Pytest collection failure detected",
            "detail": health["tests"].get("stderr_snippet", ""),
        })
    if not actions:
        actions.append({"type": "noop", "priority": "low", "description": "All sensors nominal"})
    return actions


# ── Session persistence ────────────────────────────────────────────────────────

def write_session(session: dict[str, Any]) -> Path:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = SESSION_DIR / f"session_{ts}_{session['session_id'][:8]}.json"
    path.write_text(json.dumps(session, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def write_session_markdown(session: dict[str, Any]) -> Path:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = SESSION_DIR / f"session_{ts}_{session['session_id'][:8]}.md"
    lines = [
        f"# Autonomy Session {session['session_id'][:8]}",
        f"**Started:** {session['started_at']}",
        f"**Ended:** {session.get('ended_at', 'in-progress')}",
        f"**Iterations:** {session.get('iterations', 0)}",
        "",
        "## Health Summary",
    ]
    for sensor, result in session.get("health", {}).items():
        lines.append(f"- **{sensor}**: {result.get('status', 'unknown')}")
    lines += ["", "## Proposed Actions"]
    for action in session.get("actions", []):
        lines.append(f"- [{action['priority'].upper()}] {action['description']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ── Main loop ──────────────────────────────────────────────────────────────────

def run(dry_run: bool = DRY_RUN, max_iterations: int = MAX_ITERATIONS, budget_seconds: int = BUDGET_SECONDS) -> int:
    session_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    deadline = time.monotonic() + budget_seconds

    session: dict[str, Any] = {
        "session_id": session_id,
        "started_at": started.isoformat(),
        "dry_run": dry_run,
        "iterations": 0,
        "health": {},
        "actions": [],
        "status": "running",
    }

    log.info("Autonomy scheduler started (session=%s, budget=%ds, dry_run=%s)", session_id[:8], budget_seconds, dry_run)

    if KILL_SWITCH:
        log.warning("AGENT_KILL_SWITCH=1 — autonomy scheduler halted immediately")
        session["status"] = "kill_switch"
        return 1

    try:
        for iteration in range(max_iterations):
            if time.monotonic() > deadline:
                raise BudgetExceededError("Budget exceeded during iteration loop")

            log.info("Iteration %d/%d", iteration + 1, max_iterations)
            session["iterations"] = iteration + 1

            # Sense
            health = {
                "json": with_budget(sense_json_health, deadline)(),
                "yaml": with_budget(sense_yaml_health, deadline)(),
                "tests": with_budget(sense_test_health, deadline)(),
            }
            session["health"] = health

            # Decide
            actions = decide_actions(health)
            session["actions"] = actions

            log.info("Actions: %s", [a["description"] for a in actions])

            # Act (emit + log; no mutating actions in scheduler — use CI for mutations)
            all_nominal = all(a["type"] == "noop" for a in actions)
            if all_nominal:
                log.info("All sensors nominal — self-evaluation passed")
                break
            for action in actions:
                if action["type"] == "alert":
                    log.warning("ALERT [%s]: %s", action["priority"], action["description"])

            # Sleep briefly to avoid tight loop
            if time.monotonic() + 5 > deadline:
                break
            time.sleep(2)

        session["status"] = "completed"

    except BudgetExceededError as exc:
        log.warning("Budget exceeded: %s", exc)
        session["status"] = "budget_exceeded"
        session["budget_error"] = str(exc)

    except Exception as exc:  # noqa: BLE001
        log.error("Unexpected error: %s", exc, exc_info=True)
        session["status"] = "error"
        session["error"] = str(exc)

    finally:
        session["ended_at"] = datetime.now(timezone.utc).isoformat()
        session["elapsed_seconds"] = round(time.monotonic() - (deadline - budget_seconds), 2)
        if not dry_run:
            json_path = write_session(session)
            md_path = write_session_markdown(session)
            log.info("Session saved: %s", json_path)
            log.info("Summary: %s", md_path)
        else:
            log.info("DRY RUN — session NOT persisted")

    return 0 if session["status"] == "completed" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", default=DRY_RUN)
    parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS)
    parser.add_argument("--budget-seconds", type=int, default=BUDGET_SECONDS)
    args = parser.parse_args()
    return run(dry_run=args.dry_run, max_iterations=args.max_iterations, budget_seconds=args.budget_seconds)


# ── Programmatic API aliases (for test harness and external callers) ───────────

def run_autonomy_loop() -> int:
    """Run the autonomy loop using the current module-level configuration.

    This function explicitly reads ``DRY_RUN``, ``MAX_ITERATIONS``, and
    ``BUDGET_SECONDS`` from the module namespace at *call* time and passes
    them as keyword arguments to ``run()``.  This allows tests to patch
    module attributes and have the patched values take effect.

    Note: ``run()`` also accepts keyword arguments directly
    (``run(dry_run=..., max_iterations=..., budget_seconds=...)``), so tests
    can equally call ``run()`` with explicit values.  The default argument
    values of ``run()`` are evaluated once at *definition* time; only the
    keyword-argument path (used here) re-reads the module globals.
    """
    return run(dry_run=DRY_RUN, max_iterations=MAX_ITERATIONS, budget_seconds=BUDGET_SECONDS)


def _write_session_record(
    path: Path,
    session_id: str,
    status: str,
    iterations: int,
    actions: list[dict[str, Any]],
) -> None:
    """Write a minimal JSON session record to *path*.

    This helper exposes the session-persistence logic as a callable API so it
    can be exercised directly by tests without running the full scheduler loop.
    """
    record: dict[str, Any] = {
        "session_id": session_id,
        "status": status,
        "iterations": iterations,
        "actions": actions,
        "written_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
