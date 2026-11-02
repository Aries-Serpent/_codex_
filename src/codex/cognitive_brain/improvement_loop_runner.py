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
import hashlib
import json
import logging
import math
import re
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Callable, List, Mapping, Optional, Sequence, Tuple, cast

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from aries_serpent_core.skills.assurance import (
    adversarial_validation,
    evidence_to_improvement_brief,
    rubber_duck_review,
)
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.improvement_evaluator import evaluate_event
from codex.cognitive_brain.improvement_pipeline import (
    DataAvailability,
    ImprovementPipeline,
    ProposalDecision,
    SignalEvidence,
    load_pda_signals,
    signal_from_pda_record,
)
from codex.cognitive_brain.isolated_execution import IsolatedExecutor
from codex.cognitive_brain.post_attempt_handoff import (
    RecordedFixtureReader,
)
from codex.cognitive_brain.post_attempt_handoff import (
    compose_post_attempt_handoff as _compose_post_attempt_handoff,
)

logger = logging.getLogger(__name__)

#: Exit code returned when every record parsed cleanly.
EXIT_OK = 0
#: Exit code returned when at least one record was malformed (fail closed).
EXIT_MALFORMED = 1


def assess_evidence_record(
    record: dict[str, Any],
    *,
    pipeline: ImprovementPipeline,
    observed_at: Optional[datetime] = None,
    freshness_seconds: int = 3600,
    human_approved: bool = False,
    patch_bytes: Optional[bytes] = None,
    patch_hash: Optional[str] = None,
    base_sha: Optional[str] = None,
) -> dict[str, Any]:
    """Join exported observations to bounded proposals, never execute them.

    Repository/SHA and assessment time are supplied by the caller, not by an
    untrusted brief. Validation observations must bind the generated proposal
    identity and content hash. Claimed observer identities are not authenticated
    here; even complete evidence remains subject to independent human review.
    """
    if not re.fullmatch(r"[0-9a-f]{40}", pipeline.sha):
        raise ValueError("evidence assessment requires an immutable commit SHA")
    if record.get("repo") != pipeline.repo or record.get("sha") != pipeline.sha:
        raise ValueError("signal repository/SHA does not match the assessment context")
    if type(freshness_seconds) is not int or not 0 < freshness_seconds <= 86400:
        raise ValueError("freshness budget must be between one second and one day")
    cycle = record.get("correction_cycle", 0)
    if type(cycle) is not int or not 0 <= cycle <= 3:
        raise ValueError("at most three correction cycles are permitted")
    now = observed_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("observation time must be timezone-aware")
    signal = SignalEvidence(**record["signal"])
    signal.validate()
    result: dict[str, Any] = {
        "status": "unknown",
        "execution_authorized": False,
        "integration_authorized": False,
        "correction_cycle": cycle,
        "max_correction_cycles": 3,
    }
    if signal.availability != DataAvailability.MEASURED:
        return {**result, "reason": f"signal not measured: {signal.availability}"}
    if record["brief"].get("category") != "session-productivity":
        baseline = signal.details.get("baseline_metric")
        expected = record["brief"].get("expected_metric")
        if any(
            type(value) not in (int, float) or not math.isfinite(cast(float, value))
            for value in (baseline, expected)
        ):
            raise ValueError("code proposals require finite measured baseline and expected metrics")
        if baseline != record["brief"].get("baseline_metric"):
            raise ValueError("brief baseline must match the measured signal")
    payload = {
        **record["brief"],
        "source": signal.source,
        "timestamp": signal.measured_at,
        "observed_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "freshness_seconds": freshness_seconds,
        "base_sha": pipeline.sha,
        "problem": signal.summary,
    }
    brief = evidence_to_improvement_brief(payload)
    result["proposal"] = brief
    if brief["status"] != "proposal":
        return {**result, "status": brief["status"], "reason": "signal is not a code proposal"}
    paths = payload["write_paths"]
    if not isinstance(paths, list) or not paths:
        raise ValueError("a proposal requires an explicit write boundary")
    for path in paths:
        if (
            not isinstance(path, str)
            or not path.strip()
            or PurePosixPath(path).is_absolute()
            or ".." in PurePosixPath(path).parts
            or "\\" in path
            or str(PurePosixPath(path)) == "."
        ):
            raise ValueError("write paths must be bounded repository-relative paths")
    decision = pipeline.process_signal(
        signal,
        human_approved=human_approved,
        patch_bytes=patch_bytes,
        patch_hash=patch_hash,
        base_sha=base_sha,
    )
    result["event"] = decision.event.to_dict()
    result["pipeline_actionable"] = decision.actionable
    result["review"] = rubber_duck_review(
        {**payload, "objective": signal.summary, "evidence": signal.details}
    )
    proposal = decision.event.proposal
    if proposal is None or not decision.actionable:
        return {**result, "status": "blocked", "reason": decision.reason}
    if not proposal.files or any(
        not any(
            path == boundary or path.startswith(boundary.rstrip("/") + "/") for boundary in paths
        )
        or ".." in PurePosixPath(path).parts
        or "\\" in path
        for path in proposal.files
    ):
        return {
            **result,
            "status": "blocked",
            "reason": "proposal exceeds the brief write boundary",
        }
    binding = {
        "repo": pipeline.repo,
        "sha": pipeline.sha,
        "proposal_id": brief["proposal_id"],
        "proposal": result["event"]["proposal"],
        "signal": result["event"]["signal"],
    }
    evidence_digest = hashlib.sha256(
        json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result["evidence_digest"] = evidence_digest
    validation = record.get("validation", {})
    if (
        not record.get("author")
        or validation.get("author") != record["author"]
        or validation.get("base_sha") != pipeline.sha
        or validation.get("proposal_id") != brief["proposal_id"]
        or validation.get("patch_hash") != proposal.patch_hash
        or validation.get("evidence_digest") != evidence_digest
    ):
        return {**result, "reason": "missing or mismatched proposal-bound independent evidence"}
    declared_commands = payload["verification_commands"]
    checks = validation.get("checks", [])
    if (
        validation.get("required_checks") != ["negative", "boundary", "regression"]
        or not isinstance(declared_commands, list)
        or not declared_commands
        or not isinstance(checks, list)
        or not checks
        or any(not _valid_command(command) for command in declared_commands)
        or any(
            not isinstance(check, dict)
            or not _valid_command(check.get("command"))
            or check.get("evidence_digest") != evidence_digest
            or check.get("proposal_id") != brief["proposal_id"]
            or check.get("patch_hash") != proposal.patch_hash
            for check in checks
        )
        or any(
            command not in [check.get("command") for check in checks]
            for command in declared_commands
        )
    ):
        return {
            **result,
            "reason": "independent evidence omits bound checks or valid required commands",
        }
    assessment = adversarial_validation(validation)
    result["validation"] = assessment
    result["status"] = (
        "ready-for-human-review" if assessment["status"] == "pass" else assessment["status"]
    )
    result["reason"] = "Supplied observations assessed; no patch execution or integration performed"
    return result


def compose_local_improvement(
    record: dict[str, Any],
    *,
    pipeline: ImprovementPipeline,
    patch_bytes: bytes,
    patch_hash: str,
    base_sha: str,
    executor: Optional[IsolatedExecutor] = None,
    execute_authorized: bool = False,
    human_approved: bool = False,
    observed_at: Optional[datetime] = None,
    freshness_seconds: int = 3600,
    review_verifier: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Compose existing skills/pipeline/executor/store/evaluator locally.

    Defaults to read-only preparation, even when supplied reviews pass. For
    execution the trusted local caller must separately opt in, provide human
    approval and an executor with the same authority and an explicit in-repo
    work root. Distinct review names and boolean fields are not authentication:
    an injected trusted ``review_verifier`` must return exactly True over an
    immutable binding containing canonical record bytes/digest, author/observer,
    evidence digest, event, base and patch identities. The verifier must actually
    authenticate task-specific review evidence; this module cannot do so itself.
    Negative/boundary taxonomy is supplied human-review evidence, not independent
    rerun proof unless the trusted verifier authenticates that mapping.
    Production uses the current UTC clock; only explicit ``synthetic=True``
    fixture mode accepts ``observed_at`` and never qualifies production evidence.

    Exactly one attempt is made per call, never automatic corrections,
    integration, outcome collection or learning. Authentic private readers and
    post-merge measurement remain separate authorized human handoff work. A crash
    after recording the event but before execution/result storage leaves pending
    evidence requiring manual reconciliation; replay never retries that event.
    """
    if any(type(value) is not bool for value in (execute_authorized, human_approved, synthetic)):
        raise ValueError("local execution and human approval must be explicit booleans")
    if observed_at is not None and not synthetic:
        raise ValueError("clock injection is restricted to explicit synthetic fixture mode")
    canonical_record = json.dumps(
        record, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    # Snapshot caller evidence before verification; the verifier receives only
    # immutable canonical bytes and scalar identity fields, not mutable records.
    record = json.loads(canonical_record)
    store = pipeline.evidence_store
    if not isinstance(store, EvidenceStore):
        raise ValueError("local composition requires the existing durable eligibility store")
    actual = pipeline.proposal_from_patch(
        patch_bytes=patch_bytes, patch_hash=patch_hash, base_sha=base_sha
    )
    now = observed_at or datetime.now(timezone.utc)
    result = assess_evidence_record(
        record,
        pipeline=pipeline,
        observed_at=now,
        freshness_seconds=freshness_seconds,
        human_approved=human_approved,
        patch_bytes=patch_bytes,
        patch_hash=patch_hash,
        base_sha=base_sha,
    )
    handoff = {
        "patch_hash": actual.patch_hash,
        "base_sha": base_sha,
        "files": list(actual.files),
        "attempt_id": None,
        "artifact_hash": None,
        "artifact_path": None,
        "candidate_tree_hash": None,
        "required_gates": [],
        "gate_logs": [],
        "baseline_gate_logs": [],
        "integration_authorized": False,
        "learning_performed": False,
        "synthetic": synthetic,
        "limits": [
            "Local caller review identities are not hosted approval authentication",
            "Negative/boundary taxonomy is human-review evidence, not authenticated rerun proof",
            "No PR creation, merge, private reader or authentic post-merge outcome",
            "TCP/filesystem confinement is not a full sandbox; UDP/Unix sockets unsupported",
            "No automatic integration, correction retry or confidence learning",
            "Crash after event recording requires manual reconciliation; replay never retries",
            "Synthetic fixture evidence never qualifies production review or outcome evidence",
        ],
    }
    result["handoff"] = handoff
    result["synthetic"] = synthetic
    if "event" not in result:
        return result
    event = result["event"] = json.loads(json.dumps(result["event"]))
    handoff["event_id"] = event["event_id"]
    review = record.get("local_review", {})
    validation = record.get("validation", {})
    questions = result["review"]["questions"]
    answers = review.get("answers", {}) if isinstance(review, dict) else {}

    def fresh(timestamp: Any) -> bool:
        try:
            measured = datetime.fromisoformat(
                record["signal"]["measured_at"].replace("Z", "+00:00")
            )
            reviewed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return (
                reviewed.tzinfo is not None
                and measured <= reviewed <= now
                and (now - reviewed).total_seconds() <= freshness_seconds
            )
        except (ValueError, TypeError, AttributeError):
            return False

    reviewed = (
        isinstance(review, dict)
        and review.get("decision") == "pass"
        and review.get("author") == record.get("author")
        and isinstance(review.get("observer"), str)
        and bool(review["observer"].strip())
        and review["observer"].strip() != str(record.get("author", "")).strip()
        and review["observer"] == validation.get("observer")
        and review.get("objective") == result["review"]["objective"]
        and review.get("base_sha") == base_sha
        and review.get("patch_hash") == patch_hash
        and review.get("event_id") == event["event_id"]
        and review.get("evidence_digest") == result.get("evidence_digest")
        and review.get("files") == list(actual.files)
        and isinstance(answers, dict)
        and all(isinstance(answers.get(q), str) and answers[q].strip() for q in questions)
        and fresh(review.get("timestamp"))
        and all(fresh(check.get("timestamp")) for check in validation.get("checks", []))
    )
    result["task_review_supplied"] = reviewed
    result["task_review_passed"] = False
    if result["status"] != "ready-for-human-review" or not reviewed:
        return {**result, "reason": "Fresh proposal-bound validation and task review required"}
    review_binding = MappingProxyType(
        {
            "canonical_record": canonical_record,
            "record_digest": hashlib.sha256(canonical_record).hexdigest(),
            "evidence_digest": result["evidence_digest"],
            "author": record["author"],
            "observer": review["observer"],
            "event_id": event["event_id"],
            "base_sha": base_sha,
            "patch_hash": patch_hash,
            "synthetic": synthetic,
        }
    )
    try:
        verified_review = callable(review_verifier) and review_verifier(review_binding) is True
    except Exception:
        verified_review = False
    result["task_review_passed"] = verified_review
    result["review_scope"] = (
        ("synthetic-fixture" if synthetic else "trusted-local-review")
        if verified_review
        else "unverified-human-review"
    )
    if not execute_authorized:
        return {
            **result,
            "reason": "Read-only local preparation; explicit execution opt-in required",
        }
    if not verified_review:
        return {
            **result,
            "status": "blocked",
            "reason": "Trusted proposal-bound independent review verifier required",
        }
    if not human_approved:
        return {
            **result,
            "status": "blocked",
            "reason": "Explicit human execution approval required",
        }
    if not isinstance(executor, IsolatedExecutor) or executor.authority != pipeline.authority:
        raise ValueError("local execution requires the existing executor with matching authority")
    if executor.work_root is None or not Path(executor.work_root).resolve().is_relative_to(
        executor.repo_path.resolve()
    ):
        raise ValueError(
            "local execution requires an explicit repository-local disposable work root"
        )
    commands = record["brief"]["verification_commands"]
    if [list(command) for _, command in executor.gates] != commands:
        return {
            **result,
            "status": "blocked",
            "reason": "Executor gates differ from reviewed commands",
        }
    if store.seen(event["event_id"]):
        pending = not any(
            record["kind"] == "execution" for record in store.audit_trail(event["event_id"])
        )
        return {
            **result,
            "status": "duplicate",
            "manual_reconciliation_required": pending,
            "reason": (
                "Pending recorded event requires manual reconciliation; no automatic retry"
                if pending
                else "Event already recorded; no replay execution"
            ),
            "evaluation": asdict(evaluate_event(store, event["event_id"])),
        }
    event["synthetic"] = synthetic
    if not store.record_event(event):
        return {
            **result,
            "status": "duplicate",
            "manual_reconciliation_required": True,
            "reason": "Concurrent event recording requires manual reconciliation; no retry",
        }
    outcome = executor.execute(
        event_id=event["event_id"],
        patch_content=patch_bytes.decode("utf-8"),
        patch_hash=patch_hash,
        base_sha=base_sha,
        files=actual.files,
        diff_lines=actual.diff_lines,
        human_approved=human_approved,
    )
    # Normalize dataclass tuples to the durable JSON contract without inventing
    # gate/attempt evidence on rejected or interrupted executions.
    execution = json.loads(json.dumps(asdict(outcome)))
    execution["pattern_id"] = event["pattern"]["pattern_id"]
    execution["synthetic"] = synthetic
    store.record("execution", event["event_id"], execution)
    for key in (
        "attempt_id",
        "artifact_hash",
        "artifact_path",
        "candidate_tree_hash",
        "required_gates",
        "gate_logs",
        "baseline_gate_logs",
    ):
        handoff[key] = execution[key]
    return {
        **result,
        "status": outcome.status,
        "execution_authorized": True,
        "execution": execution,
        "evaluation": asdict(evaluate_event(store, event["event_id"])),
        "reason": "Local attempt recorded; human PR/outcome handoff only",
    }


def compose_post_attempt_handoff(
    store: EvidenceStore,
    *,
    event_id: str,
    pattern_id: str | None = None,
    patch_hash: str | None = None,
    attempt_id: str | None = None,
    observation_context: Mapping[str, Any] | None = None,
    reader: RecordedFixtureReader | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Explicit post-attempt diagnostics; never part of local preparation.

    Offline retained metadata is not fresh live observation, independent review,
    qualified learning, or permission to reconcile an external write.
    """
    return _compose_post_attempt_handoff(
        store,
        event_id=event_id,
        pattern_id=pattern_id,
        patch_hash=patch_hash,
        attempt_id=attempt_id,
        observation_context=observation_context,
        reader=reader,
        now=now,
    )


def _valid_command(command: Any) -> bool:
    return (
        isinstance(command, (list, tuple))
        and bool(command)
        and all(isinstance(arg, str) and bool(arg.strip()) and "\0" not in arg for arg in command)
    )


def run_from_pda(
    jsonl_path: Path,
    *,
    repo: str,
    ref: str,
    sha: str,
    brain_interface: Any,
    authority: Optional[AuthorityEnvelope] = None,
    human_approved: bool = False,
    evidence_store: Optional[EvidenceStore] = None,
) -> List[ProposalDecision]:
    """Load PDA failure signals and run each through the pipeline.

    Returns decisions in input order. Malformed records raise ``ValueError``
    from :func:`signal_from_pda_record` so bad evidence fails closed.
    """

    if evidence_store is None:
        root = getattr(brain_interface, "repo_root", None)
        if root is None:
            raise ValueError("a repository root or durable eligibility store is required")
        evidence_store = EvidenceStore(Path(root) / ".codex" / "improvement" / "evidence.jsonl")
    pipeline = ImprovementPipeline(
        repo=repo,
        ref=ref,
        sha=sha,
        brain_interface=brain_interface,
        authority=authority,
        evidence_store=evidence_store,
    )
    signals = load_pda_signals(Path(jsonl_path))
    return [pipeline.process_signal(signal, human_approved=human_approved) for signal in signals]


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
    parser.add_argument(
        "--evidence-bundle",
        action="store_true",
        help="Assess exported measured signal/brief/validation JSONL instead of legacy PDA records; "
        "never execute patches or authenticate approval/observer identities.",
    )
    parser.add_argument(
        "--collect-ci-run",
        type=int,
        help="Read one GitHub Actions run's public metadata and replace exported signals in "
        "evidence-bundle records; requires --evidence-bundle and never reads credentials or logs.",
    )
    parser.add_argument(
        "--repo", required=True, help="Repository slug, e.g. 'Aries-Serpent/_codex_'."
    )
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
    if args.collect_ci_run is not None and not args.evidence_bundle:
        print("--collect-ci-run requires --evidence-bundle", file=sys.stderr)
        return EXIT_MALFORMED

    try:
        evidence_store = EvidenceStore(args.repo_root / ".codex" / "improvement" / "evidence.jsonl")
    except (EvidenceIntegrityError, OSError):
        print("durable eligibility evidence unavailable or corrupt", file=sys.stderr)
        return EXIT_MALFORMED
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
        evidence_store=evidence_store,
    )

    if args.evidence_bundle:
        if not re.fullmatch(r"[0-9a-f]{40}", args.sha):
            print("invalid assessment SHA", file=sys.stderr)
            return EXIT_MALFORMED
        bundle_errors = 0
        assessed_records = 0
        collected = None
        if args.collect_ci_run is not None:
            from codex.cognitive_brain.ci_signal_collection import collect_ci_run

            try:
                collected = collect_ci_run(repo=args.repo, sha=args.sha, run_id=args.collect_ci_run)
            except ValueError:
                print("invalid CI collection context", file=sys.stderr)
                return EXIT_MALFORMED
        with args.jsonl_path.open(encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if collected is not None:
                        signal = asdict(collected)
                        signal["details"] = {
                            **signal["details"],
                            "files": record["brief"].get("write_paths", []),
                        }
                        record = {**record, "signal": signal}
                    result = assess_evidence_record(
                        record,
                        pipeline=pipeline,
                        human_approved=args.human_approved,
                    )
                    if collected is not None:
                        result["collection"] = asdict(collected)
                    assessed_records += 1
                    print(json.dumps(result))
                    if result["status"] != "ready-for-human-review":
                        bundle_errors += 1
                except (ValueError, TypeError, KeyError, AttributeError):
                    bundle_errors += 1
                    print(f"invalid evidence record at line {lineno}", file=sys.stderr)
        return EXIT_MALFORMED if bundle_errors or not assessed_records else EXIT_OK

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
