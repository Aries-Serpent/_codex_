#!/usr/bin/env python3
"""
orchestrate.py — Planset Orchestrator CLI

Production-ready script that surveys all unfinished plansets in ``.codex/plans/``,
scores them via QuantumPlansetEngine physics, and emits the best next actions for
agents to execute so the codebase reaches a production-ready, clean and safe state.

Usage
-----
::

    # Show the single highest-priority next action
    python scripts/cognitive/orchestrate.py next

    # Show ranked session plan (default 10 steps)
    python scripts/cognitive/orchestrate.py session

    # Survey all plansets and show their status + mapped area
    python scripts/cognitive/orchestrate.py survey

    # Mark a step complete and apply decoherence
    python scripts/cognitive/orchestrate.py advance SECURITY_REMEDIATION SEC-01

    # Print Markdown summary table
    python scripts/cognitive/orchestrate.py summary

    # Stamp every unfinished planset with an engine integration footer
    python scripts/cognitive/orchestrate.py stamp-plansets

    # With session context (JSON)
    python scripts/cognitive/orchestrate.py next \\
        --context '{"open_alerts":120,"coverage_pct":45,"failing_checks":3}'

    # Dry-run: compute without persisting state
    python scripts/cognitive/orchestrate.py session --dry-run --max 15

    # JSON output for CI integration
    python scripts/cognitive/orchestrate.py session --output json

Exit codes
----------
* 0  — success
* 1  — argument / runtime error
* 2  — no actions found (all plansets complete)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Allow running from repo root without installing the package
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from codex.cognitive.agent_brain_api import CognitiveBrain  # noqa: E402
from codex.cognitive.planset_orchestrator import (  # noqa: E402
    ImprovementArea,
    PlansetOrchestrator,
    PromptSet,
)
from codex.cognitive.quantum_planset_engine import QuantumPlansetEngine  # noqa: E402

# ---------------------------------------------------------------------------
# Integration footer added by stamp-plansets
# ---------------------------------------------------------------------------
_FOOTER_TEMPLATE = """
---

## 🔬 QuantumPlansetEngine Integration

This planset is tracked by `PlansetOrchestrator` as **`ImprovementArea.{area}`**.

```python
from codex.cognitive import PlansetOrchestrator, ImprovementArea

orch = PlansetOrchestrator()

# Generate the ranked next actions for this planset
prompts = orch.generate_session(max_prompts=5)
for p in prompts:
    if p.area == ImprovementArea.{area}.value:
        print(f"[{{p.step_id}}] {{p.agent}}: {{p.prompt[:120]}}")

# Get single highest-priority step
next_action = orch.next_promptset()

# Mark step complete after execution
orch.advance(ImprovementArea.{area}, "<step_id>")
```

Run via CLI:

```bash
python scripts/cognitive/orchestrate.py next
python scripts/cognitive/orchestrate.py session --output markdown
```

*Decoherence sessions: 0 → planset is fully viable.*
*Amplitude recalculated each session via Born-rule normalisation.*
"""

_FOOTER_SENTINEL = "🔬 QuantumPlansetEngine Integration"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_context(ctx_str: str) -> dict[str, Any]:
    """Parse a JSON string into a context dict."""
    try:
        return json.loads(ctx_str)
    except json.JSONDecodeError as exc:
        print(f"❌  --context must be valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)


def _build_orchestrator(
    args: argparse.Namespace,
    dry_run: bool = False,
) -> PlansetOrchestrator:
    planset_dir = _REPO_ROOT / ".codex" / "plans"
    state_path = planset_dir / ".orchestrator_state.json"
    if dry_run:
        # Use a temp state path so nothing is persisted to the real planset dir.
        # Register cleanup so the file is removed when the process exits.
        import atexit
        import tempfile
        _fd, _tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(_fd)
        state_path = Path(_tmp_path)
        def _cleanup_temp_file(path: str = _tmp_path) -> None:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                return
        atexit.register(_cleanup_temp_file)
    return PlansetOrchestrator(
        planset_dir=planset_dir,
        engine=QuantumPlansetEngine(),
        state_path=state_path,
    )


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def cmd_survey(args: argparse.Namespace) -> int:
    """List all plansets with status and mapped ImprovementArea."""
    orch = _build_orchestrator(args)
    records = orch.survey()

    if args.output == "json":
        out = [
            {
                "stem": r.stem,
                "area": r.area.value if r.area else None,
                "is_complete": r.is_complete,
                "status": r.status_line,
            }
            for r in records
        ]
        print(json.dumps(out, indent=2))
        return 0

    # Table output
    complete = [r for r in records if r.is_complete]
    pending  = [r for r in records if not r.is_complete]
    unmapped = [r for r in pending if r.area is None]

    print(f"\n{'─'*72}")
    print(f" 🗂  Planset Survey — {len(records)} files")
    print(f"{'─'*72}")
    print(f"  ✅  Complete   : {len(complete)}")
    print(f"  🔄  Unfinished : {len(pending)}  ({len(unmapped)} unmapped)")
    print(f"{'─'*72}\n")

    print(f"{'PLANSET':<52} {'AREA':<28} {'STATUS'}")
    print(f"{'─'*52} {'─'*28} {'─'*12}")
    for r in pending:
        area_str = r.area.value if r.area else "— UNMAPPED —"
        done_str = "✅" if r.is_complete else "🔄"
        print(f"  {done_str} {r.stem[:49]:<49} {area_str:<28} {r.status_line[:40]}")

    if unmapped:
        print(f"\n⚠️  {len(unmapped)} plansets have no ImprovementArea mapping:")
        for r in unmapped:
            print(f"   • {r.stem}")

    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """Print the single highest-priority next action."""
    ctx = _parse_context(args.context) if args.context else {}
    orch = _build_orchestrator(args, dry_run=args.dry_run)
    prompt = orch.next_promptset(context=ctx)

    if prompt is None:
        print("✅  All plansets complete — nothing left to orchestrate.")
        return 2

    if args.output == "json":
        print(prompt.to_json())
        return 0

    _print_prompt_card(prompt, rank=1, total=1)
    return 0


def cmd_session(args: argparse.Namespace) -> int:
    """Print ranked session plan."""
    ctx = _parse_context(args.context) if args.context else {}
    orch = _build_orchestrator(args, dry_run=args.dry_run)
    prompts = orch.generate_session(context=ctx, max_prompts=args.max)

    if not prompts:
        print("✅  All plansets complete — nothing left to orchestrate.")
        return 2

    if args.output == "json":
        print(json.dumps([p.to_dict() for p in prompts], indent=2))
        return 0

    if args.output == "markdown":
        print(orch.summary(context=ctx))
        return 0

    # Rich table
    print(f"\n{'═'*72}")
    print(f"  🧭  Planset Orchestrator — Session Plan  ({len(prompts)} actions)")
    print(f"{'═'*72}\n")
    for p in prompts:
        _print_prompt_card(p, rank=p.order + 1, total=len(prompts))
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    """Mark a step as complete."""
    try:
        area = ImprovementArea(args.area)
    except ValueError:
        valid = [a.value for a in ImprovementArea]
        print(f"❌  Unknown area '{args.area}'. Valid: {valid}", file=sys.stderr)
        return 1

    orch = _build_orchestrator(args)
    orch.advance(area, args.step_id)
    print(f"✅  Marked {area.value}:{args.step_id} complete. State saved.")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """Print Markdown summary table."""
    ctx = _parse_context(args.context) if args.context else {}
    orch = _build_orchestrator(args, dry_run=args.dry_run)
    print(orch.summary(context=ctx))
    return 0


def cmd_stamp_plansets(args: argparse.Namespace) -> int:
    """Add QuantumPlansetEngine integration footer to every unfinished planset."""
    orch = _build_orchestrator(args, dry_run=True)
    records = orch.survey()
    stamped = 0
    skipped_complete = 0
    skipped_no_area = 0
    skipped_has_footer = 0

    for rec in records:
        if rec.is_complete:
            skipped_complete += 1
            continue
        if rec.area is None:
            skipped_no_area += 1
            continue

        content = rec.path.read_text(encoding="utf-8")
        if _FOOTER_SENTINEL in content:
            skipped_has_footer += 1
            continue

        footer = _FOOTER_TEMPLATE.format(area=rec.area.value)
        rec.path.write_text(content.rstrip() + "\n" + footer, encoding="utf-8")
        stamped += 1
        print(f"  ✍️  Stamped: {rec.stem}  →  {rec.area.value}")

    print(f"\n{'─'*60}")
    print(f"  Stamped       : {stamped}")
    print(f"  Already done  : {skipped_has_footer}")
    print(f"  Complete/skip : {skipped_complete}")
    print(f"  Unmapped/skip : {skipped_no_area}")
    return 0


def cmd_help(args: argparse.Namespace) -> int:
    """Print the complete cognitive brain usage guide."""
    cb = CognitiveBrain(planset_dir=_REPO_ROOT / ".codex" / "plans")
    print(cb.help())
    return 0


def cmd_agent_context(args: argparse.Namespace) -> int:
    """Get full session context for a specific agent."""
    ctx_data = _parse_context(args.context) if args.context else {}
    cb = CognitiveBrain(
        planset_dir=_REPO_ROOT / ".codex" / "plans",
        state_path=_REPO_ROOT / ".codex" / "plans" / ".orchestrator_state.json",
    )
    session_ctx = cb.session(
        agent_id=args.agent_id,
        context=ctx_data,
        max_actions=args.max,
    )

    if args.output == "json":
        print(session_ctx.to_json())
        return 0

    if args.output == "prompt":
        print(session_ctx.continuation_prompt)
        return 0

    # Default: rich table
    print(f"\n{'═'*72}")
    print("  🧠  Cognitive Brain — Agent Session Context")
    print(f"  Agent: {session_ctx.agent_id}  |  Session: {session_ctx.session_id}")
    print(f"{'═'*72}\n")
    print(f"  Previous: {session_ctx.continuation_from}\n")
    print(f"  Capabilities: {', '.join(session_ctx.capabilities[:4])}"
          + (f" +{len(session_ctx.capabilities)-4}" if len(session_ctx.capabilities) > 4 else ""))
    print(f"\n  {'─'*68}")
    print(f"  {'#':<4} {'STEP':<12} {'AGENT':<38} {'AMP'}")
    print(f"  {'─'*68}")
    for p in session_ctx.next_actions[:8]:
        print(f"  {p.order+1:<4} {p.step_id:<12} {p.agent[:36]:<38} {p.amplitude:.4f}")
    print("\n  💬  Continuation Prompt (post to PR):")
    print("  " + "\n  ".join(session_ctx.continuation_prompt.split("\n")[:6]))
    print(f"\n  Run with: python scripts/cognitive/orchestrate.py agent-context "
          f"--agent-id {session_ctx.agent_id} --output prompt\n")
    return 0


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_prompt_card(p: PromptSet, rank: int, total: int) -> None:
    """Pretty-print a single PromptSet as a card."""
    bar = "█" * int(p.amplitude * 8) + "░" * max(0, 8 - int(p.amplitude * 8))
    print(f"  ┌{'─'*66}┐")
    print(f"  │  #{rank:02d}/{total}   [{bar}]  amp={p.amplitude:.4f}{'':>10}│")
    print(f"  │  Step  : {p.step_id:<20}  Area: {p.area:<25}│")
    print(f"  │  Agent : {p.agent:<55}│")
    print(f"  │  Source: {p.source_planset:<55}│")
    print(f"  │  Task  : {p.description[:55]:<55}│")
    print(f"  └{'─'*66}┘")
    print()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orchestrate",
        description=(
            "Planset Orchestrator — surveys unfinished plansets, scores via "
            "QuantumPlansetEngine, emits ranked next actions for production readiness."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # survey
    p_survey = sub.add_parser("survey", help="List all plansets with status")
    p_survey.add_argument("--output", choices=["table", "json"], default="table")

    # next
    p_next = sub.add_parser("next", help="Show single highest-priority next action")
    p_next.add_argument("--context", default="", help="JSON session context")
    p_next.add_argument("--output", choices=["table", "json"], default="table")
    p_next.add_argument("--dry-run", action="store_true")

    # session
    p_session = sub.add_parser("session", help="Show ranked session plan")
    p_session.add_argument("--context", default="", help="JSON session context")
    p_session.add_argument("--max", type=int, default=10, help="Max prompts")
    p_session.add_argument(
        "--output", choices=["table", "json", "markdown"], default="table"
    )
    p_session.add_argument("--dry-run", action="store_true")

    # advance
    p_adv = sub.add_parser("advance", help="Mark a step complete")
    p_adv.add_argument("area", help="ImprovementArea value (e.g. SECURITY_REMEDIATION)")
    p_adv.add_argument("step_id", help="Step ID to mark complete (e.g. SEC-01)")

    # summary
    p_sum = sub.add_parser("summary", help="Print Markdown summary table")
    p_sum.add_argument("--context", default="", help="JSON session context")
    p_sum.add_argument("--dry-run", action="store_true")

    # stamp-plansets
    sub.add_parser("stamp-plansets", help="Add engine integration footer to plansets")

    # help
    sub.add_parser("help", help="Print complete cognitive brain usage guide")

    # agent-context
    p_ac = sub.add_parser("agent-context", help="Get full session context for an agent")
    p_ac.add_argument(
        "--agent-id", default="copilot-coding-agent",
        help="Agent ID (e.g. codeql-alert-resolution-agent)",
    )
    p_ac.add_argument("--context", default="", help="JSON session context")
    p_ac.add_argument("--max", type=int, default=8, help="Max actions")
    p_ac.add_argument(
        "--output", choices=["table", "json", "prompt"], default="table",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "survey":         cmd_survey,
        "next":           cmd_next,
        "session":        cmd_session,
        "advance":        cmd_advance,
        "summary":        cmd_summary,
        "stamp-plansets": cmd_stamp_plansets,
        "help":           cmd_help,
        "agent-context":  cmd_agent_context,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
