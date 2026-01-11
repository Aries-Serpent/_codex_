from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Sequence

from codex_ml.workflow import DEFAULT_ROUTER, run_capability
from codex_ml.workflow.track_c_workflow import SIX_PHASES, WorkflowContext


def _gate_offline_mode(offline: bool) -> bool:
    return offline


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex Track C workflow orchestrator")
    parser.add_argument(
        "--capability",
        "-c",
        action="append",
        dest="capabilities",
        required=True,
        help="Capability to run (can be passed multiple times)",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Run in online mode (default is offline to avoid network usage)",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="Optional path to write JSON summary for the workflow run",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return non-zero exit code if any phase records an error",
    )
    parser.add_argument(
        "--require-phase-order",
        action="store_true",
        help="Validate that all six phases completed in the expected order",
    )
    return parser


def _validate_phase_order(ctx: WorkflowContext, expected: Sequence[str]) -> bool:
    return list(ctx.phase_history) == list(expected)


def _summarize_contexts(contexts: Iterable[WorkflowContext]) -> list[dict]:
    summaries: list[dict] = []
    for ctx in contexts:
        summaries.append(
            {
                "capability": ctx.capability,
                "phases": ctx.phase_history,
                "errors": [err.to_dict() for err in ctx.errors],
                "artifacts": list(ctx.artifacts),
                "pruned": list(ctx.pruned),
                "routes": ctx.routes,
                "offline": ctx.offline_mode,
            }
        )
    return summaries


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    offline_mode = not args.online
    if offline_mode and not _gate_offline_mode(offline_mode):
        parser.error("Offline gate failed; networked execution is not permitted.")

    contexts: list[WorkflowContext] = []
    for capability in args.capabilities:
        contexts.append(
            run_capability(capability, offline_mode=offline_mode, router=DEFAULT_ROUTER)
        )

    summaries = _summarize_contexts(contexts)
    for summary in summaries:
        print(json.dumps(summary, indent=2))

    if args.summary:
        args.summary.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    if args.require_phase_order:
        for ctx in contexts:
            if not _validate_phase_order(ctx, SIX_PHASES):
                print(f"Phase order validation failed for {ctx.capability}", file=sys.stderr)
                return 1

    if args.fail_on_error and any(ctx.errors for ctx in contexts):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
