"""Contract tests for the evidence schema: replay, validation, fail-closed."""

from __future__ import annotations

import pytest

from codex_cognitive_sdk.evidence import (
    EVIDENCE_SCHEMA_VERSION,
    DataAvailability,
    EvidenceValidationError,
    ExecutionEnvironment,
    GateResult,
    GateStatus,
    ImprovementEvent,
    ImprovementResult,
    MergeState,
    PatchProposal,
    PatternRef,
    PostMergeOutcome,
    SchemaVersionError,
    SignalEvidence,
    SignalSource,
    event_from_dict,
    event_to_dict,
    make_event_id,
    result_from_dict,
    result_to_dict,
)


def _signal() -> SignalEvidence:
    return SignalEvidence(
        source=SignalSource.PDA_FAILURE_LOG,
        kind="ci_job_failure",
        measured_at="2026-10-19T00:00:00+00:00",
        availability=DataAvailability.MEASURED,
        summary="pytest collection error",
    )


def _event() -> ImprovementEvent:
    signal = _signal()
    pattern = PatternRef(pattern_id="RP-019", pattern_version="3", success_rate=0.9)
    proposal = PatchProposal(
        patch_hash="a" * 64, files=("src/codex/x.py",), diff_lines=12
    )
    return ImprovementEvent(
        schema_version=EVIDENCE_SCHEMA_VERSION,
        event_id=make_event_id("o/r", "deadbeef", signal, pattern, proposal),
        repo="o/r",
        ref="refs/heads/main",
        sha="deadbeef",
        signal=signal,
        recorded_at="2026-10-19T00:01:00+00:00",
        pattern=pattern,
        proposal=proposal,
    )


def test_event_round_trip_is_deterministic() -> None:
    event = _event()
    replayed = event_from_dict(event_to_dict(event))
    assert replayed == event
    assert event_to_dict(replayed) == event_to_dict(event)


def test_event_id_is_stable_idempotency_key() -> None:
    assert make_event_id("o/r", "sha", _signal(), None, None) == make_event_id(
        "o/r", "sha", _signal(), None, None
    )


def test_missing_evidence_fails_closed() -> None:
    with pytest.raises(EvidenceValidationError):
        SignalEvidence(
            source=SignalSource.MANUAL, kind="", measured_at="2026-10-19T00:00:00Z"
        ).validate()


def test_proposal_requires_pattern() -> None:
    with pytest.raises(EvidenceValidationError):
        ImprovementEvent(
            schema_version=EVIDENCE_SCHEMA_VERSION,
            event_id="e1",
            repo="o/r",
            ref="main",
            sha="abc",
            signal=_signal(),
            recorded_at="2026-10-19T00:01:00Z",
            proposal=PatchProposal(patch_hash="b" * 64, files=("src/a.py",), diff_lines=1),
        ).validate()


def test_incompatible_schema_version_rejected() -> None:
    payload = event_to_dict(_event())
    payload["schema_version"] = "99.0.0"
    with pytest.raises(SchemaVersionError):
        event_from_dict(payload)


def test_malformed_payload_rejected() -> None:
    with pytest.raises((EvidenceValidationError, SchemaVersionError, TypeError, ValueError)):
        event_from_dict({"schema_version": EVIDENCE_SCHEMA_VERSION})


def test_result_confidence_update_requires_measured_post_merge() -> None:
    env = ExecutionEnvironment(runner="local-worktree", python_version="3.12")
    base = dict(
        schema_version=EVIDENCE_SCHEMA_VERSION,
        event_id="e1",
        environment=env,
        gates=(GateResult(name="tests", status=GateStatus.PASSED),),
        pr_number=7,
    )
    # Pending outcome with a confidence update must be rejected.
    with pytest.raises(EvidenceValidationError):
        ImprovementResult(
            **base,
            merge_state=MergeState.MERGED,
            post_merge_outcome=PostMergeOutcome.PENDING,
            confidence_update={"pattern_id": "RP-019", "new_rate": 0.95},
        ).validate()

    # Measured success outcome permits the update.
    ImprovementResult(
        **base,
        merge_state=MergeState.MERGED,
        post_merge_outcome=PostMergeOutcome.SUCCESS,
        confidence_update={"pattern_id": "RP-019", "new_rate": 0.95},
    ).validate()


def test_result_round_trip() -> None:
    result = ImprovementResult(
        schema_version=EVIDENCE_SCHEMA_VERSION,
        event_id="e1",
        environment=ExecutionEnvironment(runner="local-worktree"),
        gates=(GateResult(name="tests", status=GateStatus.FAILED, output_hash="c" * 64),),
        merge_state=MergeState.NOT_CREATED,
        post_merge_outcome=PostMergeOutcome.PENDING,
    )
    assert result_from_dict(result_to_dict(result)) == result


def test_pr_number_required_once_opened() -> None:
    with pytest.raises(EvidenceValidationError):
        ImprovementResult(
            schema_version=EVIDENCE_SCHEMA_VERSION,
            event_id="e1",
            environment=ExecutionEnvironment(runner="local-worktree"),
            merge_state=MergeState.PR_OPEN,
        ).validate()
