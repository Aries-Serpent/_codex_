#!/usr/bin/env python3
"""
Phase 7: Overall Integration — Persistent Agent Runner

Orchestration daemon that ties together all autonomy phases into a single
self-sustaining loop:

  Phase 1 → autonomy_scheduler  (health sense + action propose)
  Phase 2 → session_tracker     (session bookkeeping)
  Phase 3 → reflection          (code introspection)
  Phase 4 → budget_uncertainty  (probabilistic decisions)
  Phase 5 → budget_cap          (resource enforcement)
  Phase 6 → philosophy_parser   (synthesis docs)

Usage:
    python scripts/agent_runner.py [--iterations N] [--budget-seconds N] [--dry-run]
    python scripts/agent_runner.py --once  # single pass, then exit

The runner persists state between invocations via memory/ and can be resumed
from the last recorded session.

Environment Variables:
    AGENT_RUNNER_ITERATIONS     Loop iterations per invocation (default: 3)
    AGENT_RUNNER_BUDGET_SECONDS Total budget per invocation (default: 180)
    AGENT_RUNNER_DRY_RUN        Set to "1" to skip writes
    AGENT_KILL_SWITCH           Set to "1" to immediately halt all agent loops
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent
# Emergency stop: set AGENT_KILL_SWITCH=1 to immediately halt all agent loops
_KILL_SWITCH = os.environ.get("AGENT_KILL_SWITCH", "0") == "1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger("agent_runner")

# ── Dynamic import helpers ─────────────────────────────────────────────────────


def _import_script(name: str) -> Any:
    """Import a module from scripts/ by filename (without .py)."""
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules before exec so @dataclass and similar decorators work
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ── Phase executors ────────────────────────────────────────────────────────────


def _phase1_health_sense(deadline: float, dry_run: bool) -> dict[str, Any]:
    """Phase 1: sense codebase health and propose actions."""
    if time.monotonic() > deadline:
        return {"skipped": True, "reason": "budget_exceeded"}
    try:
        sched = _import_script("autonomy_scheduler")
        result = sched.run(dry_run=dry_run, max_iterations=1, budget_seconds=int(deadline - time.monotonic()))
        return {"exit_code": result, "status": "ok"}
    except Exception as exc:  # noqa: BLE001
        log.warning("Phase 1 error: %s", exc)
        return {"error": str(exc)}


def _phase3_reflect(deadline: float) -> dict[str, Any]:
    """Phase 3: reflect on core CLI module."""
    if time.monotonic() > deadline:
        return {"skipped": True, "reason": "budget_exceeded"}
    try:
        # Add src to sys.path for reflection import
        src_path = str(REPO_ROOT / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from codex.reflection import reflect, persist_reflection  # type: ignore[import]
        report = reflect("src/codex/cli.py", depth=1)
        persist_reflection(report, label="agent_runner_cycle")
        return {"summary": report.summary, "metrics": report.metrics}
    except Exception as exc:  # noqa: BLE001
        log.warning("Phase 3 error: %s", exc)
        return {"error": str(exc)}


def _phase4_uncertainty(deadline: float) -> dict[str, Any]:
    """Phase 4: update CI health beliefs under uncertainty."""
    if time.monotonic() > deadline:
        return {"skipped": True, "reason": "budget_exceeded"}
    try:
        bu = _import_script("budget_uncertainty")
        result = bu.scenario_ci_health()
        return result
    except Exception as exc:  # noqa: BLE001
        log.warning("Phase 4 error: %s", exc)
        return {"error": str(exc)}


def _phase6_philosophy(deadline: float, dry_run: bool) -> dict[str, Any]:
    """Phase 6: write a philosophy synthesis document."""
    if time.monotonic() > deadline:
        return {"skipped": True, "reason": "budget_exceeded"}
    if dry_run:
        return {"skipped": True, "reason": "dry_run"}
    try:
        pp = _import_script("philosophy_parser")
        rc = pp.cmd_write(topic="Agent Autonomy Cycle Reflection", template="structured")
        return {"exit_code": rc}
    except Exception as exc:  # noqa: BLE001
        log.warning("Phase 6 error: %s", exc)
        return {"error": str(exc)}


# ── Main orchestration loop ────────────────────────────────────────────────────


def run(iterations: int, budget_seconds: int, dry_run: bool, once: bool = False) -> int:
    run_id = str(uuid.uuid4())[:8]
    started = datetime.now(timezone.utc)
    deadline = time.monotonic() + budget_seconds

    log.info("Agent runner started (run=%s, iters=%d, budget=%ds, dry_run=%s)", run_id, iterations, budget_seconds, dry_run)

    if _KILL_SWITCH:
        log.warning("AGENT_KILL_SWITCH=1 — agent runner halted immediately")
        # Write a minimal audit record so the halt is traceable
        try:
            audit_dir = REPO_ROOT / "memory" / "sessions"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_path = audit_dir / f"kill_switch_{run_id}.json"
            audit_path.write_text(
                json.dumps({"run_id": run_id, "started_at": started.isoformat(),
                            "status": "kill_switch", "reason": "AGENT_KILL_SWITCH=1"}, indent=2) + "\n",
                encoding="utf-8",
            )
            log.info("Kill-switch audit record written: %s", audit_path.name)
        except Exception:  # noqa: BLE001
            pass
        return 1

    # Resume context from last session if available
    session_file = REPO_ROOT / "memory" / "sessions" / ".current_session.json"
    if session_file.exists():
        try:
            current = json.loads(session_file.read_text(encoding="utf-8"))
            log.info("Resuming from session: %s", current.get("session_id", "?")[:12])
        except Exception:  # noqa: BLE001
            pass

    summary: dict[str, Any] = {
        "run_id": run_id,
        "started_at": started.isoformat(),
        "iterations": [],
        "status": "running",
    }

    try:
        for i in range(iterations):
            if time.monotonic() > deadline:
                log.warning("Budget exceeded before iteration %d", i + 1)
                summary["status"] = "budget_exceeded"
                break

            iter_start = time.monotonic()
            log.info("─── Iteration %d/%d ───", i + 1, iterations)

            iter_result: dict[str, Any] = {"iteration": i + 1}

            # Phase 1: health
            iter_result["phase1"] = _phase1_health_sense(deadline, dry_run=dry_run)

            # Phase 3: reflection
            iter_result["phase3"] = _phase3_reflect(deadline)

            # Phase 4: uncertainty
            iter_result["phase4"] = _phase4_uncertainty(deadline)

            # Phase 6: philosophy (every 3rd iteration to avoid noise)
            if (i + 1) % 3 == 0:
                iter_result["phase6"] = _phase6_philosophy(deadline, dry_run=dry_run)

            iter_result["elapsed_s"] = round(time.monotonic() - iter_start, 2)
            summary["iterations"].append(iter_result)

            log.info("Iteration %d done in %.1fs", i + 1, iter_result["elapsed_s"])

            if once:
                break

            # Inter-iteration pause (respect budget)
            if i < iterations - 1 and time.monotonic() + 5 < deadline:
                time.sleep(2)

        summary["status"] = "completed"

    except Exception as exc:  # noqa: BLE001
        log.error("Agent runner error: %s", exc)
        log.debug(traceback.format_exc())
        summary["status"] = "error"
        summary["error"] = str(exc)

    finally:
        summary["ended_at"] = datetime.now(timezone.utc).isoformat()
        summary["elapsed_s"] = round(time.monotonic() - (deadline - budget_seconds), 2)

        if not dry_run:
            run_log = REPO_ROOT / "memory" / "sessions"
            run_log.mkdir(parents=True, exist_ok=True)
            log_path = run_log / f"agent_run_{run_id}.json"
            log_path.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
            log.info("Run log: %s", log_path)
        else:
            log.info("DRY RUN — not persisting run log")

    return 0 if summary["status"] == "completed" else 1


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    default_iters = int(os.environ.get("AGENT_RUNNER_ITERATIONS", "3"))
    default_budget = int(os.environ.get("AGENT_RUNNER_BUDGET_SECONDS", "180"))
    default_dry = os.environ.get("AGENT_RUNNER_DRY_RUN", "0") == "1"

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iterations", type=int, default=default_iters)
    parser.add_argument("--budget-seconds", type=int, default=default_budget)
    parser.add_argument("--dry-run", action="store_true", default=default_dry)
    parser.add_argument("--once", action="store_true", help="Run one iteration and exit")
    args = parser.parse_args()
    return run(
        iterations=args.iterations,
        budget_seconds=args.budget_seconds,
        dry_run=args.dry_run,
        once=args.once,
    )


if __name__ == "__main__":
    sys.exit(main())
