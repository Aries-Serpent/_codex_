#!/usr/bin/env python3
"""
Phase 4 & 5: Epistemic Uncertainty Handling + Finite Budget Enforcement

Combines probabilistic decision-making (simple Bayesian posterior) with
hard computational budget caps enforced via decorators.

Usage:
    python scripts/budget_uncertainty.py --scenario ci_health
    python scripts/budget_uncertainty.py --scenario decision [--options "pass fail skip"]

Environment Variables:
    UNCERTAINTY_BUDGET_SECONDS   Per-query time cap (default: 10)
"""
from __future__ import annotations

import argparse
import functools
import json
import logging
import math
import os
import signal
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

REPO_ROOT = Path(__file__).parent.parent
BUDGET_DIR = REPO_ROOT / "memory" / "budget"

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

F = TypeVar("F", bound=Callable[..., Any])

# ── Budget enforcement ─────────────────────────────────────────────────────────


class BudgetExceeded(RuntimeError):
    pass


def budget_cap(max_seconds: float = 10.0, label: str = ""):
    """Decorator: enforce/verify per-call wall-time budget."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                env_max_seconds = float(
                    os.environ.get("UNCERTAINTY_BUDGET_SECONDS", max_seconds)
                )
            except ValueError:
                log.warning(
                    "Invalid UNCERTAINTY_BUDGET_SECONDS value %r; using max_seconds=%s",
                    os.environ.get("UNCERTAINTY_BUDGET_SECONDS"),
                    max_seconds,
                )
                env_max_seconds = max_seconds
            cap = min(max_seconds, env_max_seconds)

            start = time.monotonic()
            timeout_supported = (
                hasattr(signal, "SIGALRM")
                and hasattr(signal, "setitimer")
                and cap > 0
                and threading.current_thread() is threading.main_thread()
            )
            if timeout_supported:
                def _handle_timeout(signum, frame):
                    raise BudgetExceeded(
                        f"{label or func.__name__} exceeded {cap}s cap"
                    )

                previous_handler = signal.getsignal(signal.SIGALRM)
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.setitimer(signal.ITIMER_REAL, cap)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, previous_handler)
            else:
                result = func(*args, **kwargs)

            elapsed = time.monotonic() - start
            if elapsed > cap:
                raise BudgetExceeded(
                    f"{label or func.__name__} took {elapsed:.2f}s, exceeded {cap}s cap"
                )
            return result
        return wrapper  # type: ignore[return-value]
    return decorator


# ── Simple Bayesian posterior (no external deps) ───────────────────────────────


@dataclass
class DirichletBeliefs:
    """
    Categorical distribution belief state via Dirichlet conjugate prior.
    Each option has an alpha concentration parameter (starts at 1 = uniform).
    """
    options: list[str]
    alphas: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.alphas:
            self.alphas = [1.0] * len(self.options)
        if len(self.options) != len(self.alphas):
            raise ValueError(
                f"options and alphas must have the same length, "
                f"got {len(self.options)} and {len(self.alphas)}"
            )

    def observe(self, option: str, weight: float = 1.0) -> None:
        """Update beliefs on observing evidence for an option."""
        if option not in self.options:
            raise ValueError(
                f"Unknown option {option!r}; expected one of {self.options!r}"
            )
        idx = self.options.index(option)
        self.alphas[idx] += weight

    @property
    def posterior_means(self) -> dict[str, float]:
        total = sum(self.alphas)
        return {opt: a / total for opt, a in zip(self.options, self.alphas)}

    @property
    def entropy(self) -> float:
        means = self.posterior_means
        return -sum(p * math.log(p + 1e-12) for p in means.values())

    @property
    def best_option(self) -> str:
        return max(self.posterior_means, key=lambda k: self.posterior_means[k])

    def to_dict(self) -> dict[str, Any]:
        return {
            "options": self.options,
            "alphas": self.alphas,
            "posterior_means": self.posterior_means,
            "entropy": round(self.entropy, 4),
            "best_option": self.best_option,
        }


# ── Scenarios ──────────────────────────────────────────────────────────────────


@budget_cap(max_seconds=10.0, label="ci_health_scenario")
def scenario_ci_health() -> dict[str, Any]:
    """Estimate CI health state from summary JSON if available."""
    summary_path = REPO_ROOT / "validation_summary.json"
    beliefs = DirichletBeliefs(options=["healthy", "degraded", "failing"])

    if summary_path.exists():
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
            # tools/validate.py writes exit_code (not status).  Derive health
            # from exit_code and optional junit failure/error counts.
            exit_code = data.get("exit_code", -1)
            junit = data.get("junit")
            if not isinstance(junit, dict):
                junit = {}
            failures = junit.get("failures", 0)
            errors = junit.get("errors", 0)
            if exit_code == 0 and failures == 0 and errors == 0:
                beliefs.observe("healthy", 5.0)
            elif exit_code == 0 or (failures + errors < 3):
                beliefs.observe("degraded", 3.0)
                beliefs.observe("healthy", 1.0)
            else:
                beliefs.observe("failing", 4.0)
                beliefs.observe("degraded", 1.0)
        except Exception as exc:  # noqa: BLE001
            beliefs.observe("degraded", 1.0)
            log.warning("Could not parse validation_summary.json: %s", exc)
    else:
        # No data — uniform beliefs
        pass

    return {"scenario": "ci_health", "beliefs": beliefs.to_dict()}


@budget_cap(max_seconds=10.0, label="decision_scenario")
def scenario_decision(options: list[str]) -> dict[str, Any]:
    """
    Model an N-way decision under uniform uncertainty.
    If the agent has prior evidence in memory, update beliefs accordingly.
    """
    beliefs = DirichletBeliefs(options=options)

    # Look for prior evidence in session files
    session_dir = REPO_ROOT / "memory" / "sessions"
    try:
        for sf in sorted(session_dir.glob("session_*.json"), reverse=True)[:5]:
            try:
                sess = json.loads(sf.read_text(encoding="utf-8"))
                outcome = sess.get("outcome", "")
                if outcome == "success" and "success" in options:
                    beliefs.observe("success", 0.5)
                elif outcome == "failure" and "failure" in options:
                    beliefs.observe("failure", 0.5)
            except (json.JSONDecodeError, OSError, KeyError) as exc:
                log.debug("Skipping session file %s: %s", sf.name, exc)
    except OSError as exc:
        log.debug("Cannot read session dir: %s", exc)

    return {"scenario": "decision", "beliefs": beliefs.to_dict()}


# ── Persistence ────────────────────────────────────────────────────────────────

def persist_result(result: dict[str, Any]) -> Path:
    from datetime import datetime, timezone
    BUDGET_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = BUDGET_DIR / f"uncertainty_{ts}_{result['scenario']}.json"
    path.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    return path


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", choices=["ci_health", "decision"], default="ci_health")
    parser.add_argument("--options", default="pass fail skip", help="Space-separated options for 'decision' scenario")
    parser.add_argument("--persist", action="store_true", help="Save result to memory/budget/")
    args = parser.parse_args()

    if args.scenario == "ci_health":
        result = scenario_ci_health()
    else:
        options = args.options.split()
        result = scenario_decision(options)

    print(json.dumps(result, indent=2, default=str))

    if args.persist:
        path = persist_result(result)
        print(f"\nResult persisted to: {path}", file=sys.stderr)

    best = result["beliefs"]["best_option"]
    entropy = result["beliefs"]["entropy"]
    log.info("Best option: %s (entropy=%.3f)", best, entropy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
