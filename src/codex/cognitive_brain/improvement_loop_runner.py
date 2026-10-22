"""Runnable wiring: PDA failure log -> improvement pipeline -> JSONL events.

This module turns the vertical slice in
:mod:`codex.cognitive_brain.improvement_pipeline` into a runnable loop:

1. Load measured failure signals from a ``pda_failure_logger`` JSONL file.
2. Run each signal through :class:`ImprovementPipeline`.
3. Emit one :meth:`ImprovementEvent.to_dict` JSON object per line on stdout.

The CLI fails closed: malformed records are reported on stderr and force a
non-zero exit code, while decisions for valid records are still emitted so
evidence is never silently dropped.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_pipeline import (
    ImprovementPipeline,
    ProposalDecision,
    load_pda_signals,
    signal_from_pda_record,
)

logger = logging.getLogger(__name__)

#: Exit code returned when every record parsed cleanly.
EXIT_OK = 0
#: Exit code returned when at least one record was malformed (fail closed).
EXIT_MALFORMED = 1


def run_from_pda(
    jsonl_path: Path,
    *,
    repo: str,
    ref: str,
    sha: str,
    brain_interface: Any,
    authority: Optional[AuthorityEnvelope] = None,
    human_approved: bool = False,
) -> List[ProposalDecision]:
    """Load PDA failure signals and run each through the pipeline.

    Returns decisions in input order. Malformed records raise ``ValueError``
    from :func:`signal_from_pda_record` so bad evidence fails closed.
    """

    pipeline = ImprovementPipeline(
        repo=repo,
        ref=ref,
        sha=sha,
        brain_interface=brain_interface,
        authority=authority,
    )
    signals = load_pda_signals(Path(jsonl_path))
    return [
        pipeline.process_signal(signal, human_approved=human_approved) for signal in signals
    ]


def _load_signals_tolerant(jsonl_path: Path) -> Tuple[List[Any], List[str]]:
    """Parse a PDA JSONL log line-by-line, collecting signals and errors.

    Non-failure records are skipped (matching :func:`load_pda_signals`);
    malformed failure records are collected as error strings instead of
    aborting, so valid records still produce decisions.
    """

    signals: List[Any] = []
    errors: List[str] = []
    with open(jsonl_path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError as exc:
                errors.append(f"{jsonl_path}:{lineno}: invalid JSON: {exc}")
                continue
            if isinstance(record, dict) and record.get("type") != "failure":
                continue
            try:
                signals.append(signal_from_pda_record(record))
            except ValueError as exc:
                errors.append(f"{jsonl_path}:{lineno}: malformed record: {exc}")
    return signals, errors


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m codex.cognitive_brain.improvement_loop_runner",
        description=(
            "Run the self-improvement loop over a PDA failure-log JSONL file "
            "and emit one ImprovementEvent JSON object per line."
        ),
    )
    parser.add_argument("jsonl_path", type=Path, help="Path to the PDA failure-log JSONL file.")
    parser.add_argument("--repo", required=True, help="Repository slug, e.g. 'Aries-Serpent/_codex_'.")
    parser.add_argument("--ref", required=True, help="Git ref the signals were observed on.")
    parser.add_argument("--sha", required=True, help="Commit SHA the signals were observed on.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root holding .codex/cognitive_brain/pattern_learning_store.json "
        "(default: current working directory).",
    )
    parser.add_argument(
        "--human-approved",
        action="store_true",
        help="Treat the run as human-approved for authority evaluation.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns 0 on success, 1 if any record was malformed."""

    args = _build_parser().parse_args(argv)

    brain = AgentBrainInterface(
        agent_id="improvement-loop",
        repo_root=args.repo_root,
        auto_register=False,
    )
    pipeline = ImprovementPipeline(
        repo=args.repo,
        ref=args.ref,
        sha=args.sha,
        brain_interface=brain,
    )

    signals, errors = _load_signals_tolerant(args.jsonl_path)
    for signal in signals:
        decision = pipeline.process_signal(signal, human_approved=args.human_approved)
        print(json.dumps(decision.event.to_dict()))

    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        logger.warning("failing closed: %d malformed record(s) in %s", len(errors), args.jsonl_path)
        return EXIT_MALFORMED
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
