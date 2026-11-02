"""Disposable persisted joins are diagnostics, never learning or live evidence."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain import post_attempt_handoff as handoff
from codex.cognitive_brain.evidence_store import EvidenceStore
from codex.cognitive_brain.pattern_calibration import event_partition

NOW = datetime(2026, 11, 2, 1, tzinfo=timezone.utc)
REPO = "example/repository"
BASE = "a" * 40
MERGE = "b" * 40
PATCH = "c" * 64


def context() -> dict[str, Any]:
    return {
        "repo": REPO,
        "pr_number": 12,
        "expected_sha": MERGE,
        "base_ref": "main",
        "run_id": 45,
        "run_attempt": 1,
        "workflow_name": "Scanner",
        "event": "push",
        "window_start": NOW - timedelta(hours=1),
        "window_end": NOW,
        "observed_at": NOW,
        "max_age": timedelta(hours=1),
        "evidence_origin": "recorded",
    }


def reader(*, origin: str = "recorded") -> handoff.RecordedFixtureReader:
    pr = {
        "number": 12,
        "merged": True,
        "state": "closed",
        "merge_commit_sha": MERGE,
        "merged_at": "2026-11-02T00:10:00Z",
        "base": {"ref": "main", "repo": {"full_name": REPO}},
        "headers": {"authorization": "must-not-be-exported"},
    }
    run = {
        "id": 45,
        "repository": {"full_name": REPO},
        "head_sha": MERGE,
        "head_branch": "main",
        "name": "Scanner",
        "event": "push",
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-11-02T00:11:00Z",
        "updated_at": "2026-11-02T00:20:00Z",
    }
    job = {
        "id": 67,
        "run_id": 45,
        "run_attempt": 1,
        "head_sha": MERGE,
        "status": "completed",
        "conclusion": "success",
        "started_at": "2026-11-02T00:11:01Z",
        "completed_at": "2026-11-02T00:19:00Z",
    }
    return handoff.RecordedFixtureReader(
        {
            f"/repos/{REPO}/pulls/12": (200, json.dumps(pr).encode()),
            f"/repos/{REPO}/actions/runs/45": (200, json.dumps(run).encode()),
            f"/repos/{REPO}/actions/runs/45/attempts/1/jobs?per_page=100&page=1": (
                200,
                json.dumps({"total_count": 1, "jobs": [job]}).encode(),
            ),
        },
        repo=REPO,
        source_id="recorded-fixture-12-run-45",
        evidence_origin=origin,
    )


def persisted(path: Path, *, pr: bool = True, execution: bool = True) -> EvidenceStore:
    store = EvidenceStore(path)
    store.record_event(
        {
            "event_id": "event",
            "repo": REPO,
            "sha": BASE,
            "signal": {
                "source": "scanner-fixture",
                "measured_at": "2026-11-01T23:00:00Z",
                "availability": "measured",
            },
            "pattern": {"pattern_id": "RP-1"},
            "proposal": {"patch_hash": PATCH},
            "headers": {"authorization": "must-not-be-exported"},
        }
    )
    if execution:
        store.record(
            "execution",
            "event",
            {
                "status": "verified",
                "pattern_id": "RP-1",
                "patch_hash": PATCH,
                "base_sha": BASE,
                "attempt_id": "attempt",
            },
        )
    if pr:
        store.record(
            "pr",
            "event",
            {
                "merge_state": "merged",
                "merged_sha": MERGE,
                "pr_number": 12,
                "patch_hash": PATCH,
                "base_sha": BASE,
                "attempt_id": "attempt",
                "run_id": 45,
                "run_attempt": 1,
                "window_start": "2026-11-02T00:00:00Z",
                "window_end": "2026-11-02T01:00:00Z",
            },
        )
    return store


def test_real_persisted_join_is_read_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("post-attempt handoff must be read only")

    for method in (
        "record",
        "record_event",
        "record_outcome",
        "claim_observation",
        "complete_observation",
        "reconcile_learning",
    ):
        monkeypatch.setattr(EvidenceStore, method, forbidden, raising=False)
    monkeypatch.setattr(AgentBrainInterface, "submit_learning", forbidden)
    result = handoff.compose_post_attempt_handoff(
        store, event_id="event", observation_context=context(), reader=reader(), now=NOW
    )
    assert result["status"] == "partial"  # No invented calibration samples.
    assert result["identity"]["attempt_id"] == "attempt"
    assert result["observation"]["availability"] == "measured"
    assert result["observation"]["evidence_origin"] == "recorded"
    assert result["observation"]["fresh_live_evidence"] is False
    assert result["observation"]["learning_eligible"] is False
    assert result["calibration"]["pattern_id"] == "RP-1"
    assert result["calibration"]["diagnostic_only"] is True
    assert result["calibration"]["state"] == "insufficient_samples"
    assert result["learning_performed"] is result["recovery_performed"] is False
    assert result["causal_evidence"] is False
    assert result["snapshot"]["atomic"] is False
    assert result["snapshot"]["unchanged_on_recheck"] is True
    assert result["signal_source"]["source"] == "scanner-fixture"
    assert "must-not-be-exported" not in json.dumps(result)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


@pytest.mark.parametrize(
    "override",
    [
        {"pattern_id": "RP-other"},
        {"patch_hash": "d" * 64},
        {"attempt_id": "other"},
        {"event_id": "missing"},
    ],
)
def test_wrong_requested_identity_never_associates(tmp_path: Path, override: dict) -> None:
    result = handoff.compose_post_attempt_handoff(
        persisted(tmp_path / "evidence.jsonl"),
        **{"event_id": "event", **override},
        observation_context=context(),
        reader=reader(),
        now=NOW,
    )
    assert result["status"] in ("partial", "rejected")
    assert result["observation"]["availability"] == "unavailable"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("expected_sha", "d" * 40),
        ("pr_number", 13),
        ("run_id", 46),
        ("run_attempt", 2),
        ("window_start", NOW - timedelta(minutes=45)),
        ("window_end", NOW - timedelta(minutes=1)),
        ("repo", "other/repository"),
        ("observed_at", NOW + timedelta(seconds=1)),
    ],
)
def test_mismatched_observation_binding_rejected(tmp_path: Path, key: str, value: Any) -> None:
    requested = {**context(), key: value}
    result = handoff.compose_post_attempt_handoff(
        persisted(tmp_path / "evidence.jsonl"),
        event_id="event",
        observation_context=requested,
        reader=reader(),
        now=NOW,
    )
    assert result["status"] == "rejected"


def test_contradictory_execution_terminal_is_not_last_write_wins(tmp_path: Path) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    store.record(
        "execution",
        "event",
        {"status": "cancelled", "attempt_id": "attempt", "patch_hash": PATCH},
    )
    result = handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)
    assert result["status"] == "rejected"


def test_nested_execution_identity_mismatch_is_rejected(tmp_path: Path) -> None:
    store = persisted(tmp_path / "evidence.jsonl", execution=False, pr=False)
    store.record(
        "execution",
        "event",
        {
            "status": "verified",
            "patch_hash": PATCH,
            "base_sha": BASE,
            "attempt_id": "attempt",
            "gate_logs": [{"event_id": "unrelated-event"}],
        },
    )
    result = handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)
    assert result["status"] == "rejected"


def test_absent_store_is_not_created(tmp_path: Path) -> None:
    path = tmp_path / "absent" / "evidence.jsonl"
    result = handoff.compose_post_attempt_handoff(EvidenceStore(path), event_id="missing", now=NOW)
    assert result["status"] == "partial"
    assert not list(tmp_path.iterdir())


def test_changed_journal_fails_partial_instead_of_joining_snapshots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    calibrate = handoff.calibrate_pattern

    def concurrent_writer(*args: Any, **kwargs: Any) -> Any:
        diagnostic = calibrate(*args, **kwargs)
        store.record("external-note", "event", {"source": "concurrent-writer-fixture"})
        return diagnostic

    monkeypatch.setattr(handoff, "calibrate_pattern", concurrent_writer)
    result = handoff.compose_post_attempt_handoff(
        store, event_id="event", observation_context=context(), reader=reader(), now=NOW
    )
    assert result["status"] == "partial"
    assert result["snapshot"]["unchanged_on_recheck"] is False
    assert result["observation"]["availability"] == "unavailable"
    assert result["calibration"]["availability"] == "unavailable"
    assert any("journal changed" in reason for reason in result["reasons"])


@pytest.mark.parametrize(("pr", "execution"), [(False, True), (True, False)])
def test_missing_association_is_not_invented(tmp_path: Path, pr: bool, execution: bool) -> None:
    fixture = reader()
    result = handoff.compose_post_attempt_handoff(
        persisted(tmp_path / "evidence.jsonl", pr=pr, execution=execution),
        event_id="event",
        observation_context=context(),
        reader=fixture,
        now=NOW,
    )
    assert result["status"] == "partial"
    assert result["observation"]["availability"] == "unavailable"
    assert fixture._reads == 0


def test_default_and_live_callable_are_explicitly_unavailable(tmp_path: Path) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    assert (
        handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)["observation"][
            "availability"
        ]
        == "unavailable"
    )

    def unsupported(path: str) -> Any:
        raise AssertionError("unbounded injected callable must never execute")

    result = handoff.compose_post_attempt_handoff(
        store,
        event_id="event",
        observation_context={**context(), "evidence_origin": "live"},
        reader=unsupported,  # type: ignore[arg-type]
        now=NOW,
    )
    assert result["observation"]["evidence_origin"] == "live"
    assert result["observation"]["origin_authenticated"] is False
    assert result["observation"]["availability"] == "unavailable"


@pytest.mark.parametrize("origin", ["recorded", "synthetic"])
def test_origin_cannot_be_promoted(tmp_path: Path, origin: str) -> None:
    result = handoff.compose_post_attempt_handoff(
        persisted(tmp_path / "evidence.jsonl"),
        event_id="event",
        observation_context={**context(), "evidence_origin": origin},
        reader=reader(origin=origin),
        now=NOW,
    )
    assert result["observation"]["evidence_origin"] == origin
    assert result["observation"]["learning_eligible"] is False


def test_recorded_reader_rejects_origin_bytes_and_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError):
        handoff.RecordedFixtureReader({}, repo=REPO, source_id="fixture", evidence_origin="live")
    for path, body in (
        ("https://attacker.invalid/", b"{}"),
        (f"/repos/{REPO}/pulls/12", b"x" * (256 * 1024 + 1)),
    ):
        with pytest.raises(ValueError):
            handoff.RecordedFixtureReader({path: (200, body)}, repo=REPO, source_id="fixture")
    fixture = reader()
    with pytest.raises(AttributeError):
        fixture.evidence_origin = "live"  # type: ignore[misc]
    monkeypatch.setattr(handoff.time, "monotonic", lambda: fixture._deadline + 1)
    with pytest.raises(ValueError, match="budget"):
        fixture(f"/repos/{REPO}/pulls/12")


def test_recorded_reader_has_hard_read_and_total_byte_caps() -> None:
    fixture = reader()
    for _ in range(9):
        fixture(f"/repos/{REPO}/pulls/12")
    with pytest.raises(ValueError, match="budget"):
        fixture(f"/repos/{REPO}/pulls/12")
    with pytest.raises(ValueError, match="byte budget"):
        handoff.RecordedFixtureReader(
            {f"/repos/{REPO}/pulls/{i}": (200, b" " * (256 * 1024)) for i in range(1, 6)},
            repo=REPO,
            source_id="fixture",
        )


@pytest.mark.parametrize(("age", "state"), [(1, "calibrated"), (91, "expired")])
def test_exact_pattern_calibration_retains_expired_and_unknown(
    tmp_path: Path, age: int, state: str
) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    store.measurement_verifier = lambda _: True
    identifiers = [
        f"sample-{i}"
        for partition, count in (("training", 20), ("holdout", 10))
        for i in [i for i in range(300) if event_partition(f"sample-{i}") == partition][:count]
    ]
    for identifier in identifiers:
        store.record_outcome(
            event_id=identifier,
            merged=True,
            outcome="success",
            pattern_id="RP-1",
            patch_hash=PATCH,
            merged_sha=MERGE,
            observation_id=identifier,
            provenance={
                "source": "recorded-calibration",
                "measured_at": (NOW - timedelta(days=age)).isoformat(),
            },
        )
        observation = store.outcome_for(identifier)
        assert observation is not None
        assert store.claim_observation(observation)
        store.complete_observation(observation)
    result = handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)
    assert result["calibration"]["state"] == state
    assert result["calibration"]["sample_count"] == 30
    observed = handoff.compose_post_attempt_handoff(
        store, event_id="event", now=NOW, observation_context=context(), reader=reader()
    )
    assert observed["status"] == ("joined" if state == "calibrated" else "partial")
    assert observed["learning_eligible"] is False
    store.record_outcome(
        event_id="unknown",
        merged=True,
        outcome="success",
        pattern_id="RP-1",
        patch_hash=PATCH,
        merged_sha=MERGE,
    )
    result = handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)
    assert result["calibration"]["eligibility"] == "unknown"
    assert result["calibration"]["state"] == "insufficient_samples"


def test_disabled_pattern_is_reported_without_mutation(tmp_path: Path) -> None:
    store = persisted(tmp_path / "evidence.jsonl")
    store.measurement_verifier = lambda _: True
    for index in range(3):
        identifier = f"regression-{index}"
        store.record_outcome(
            event_id=identifier,
            merged=True,
            outcome="regression",
            pattern_id="RP-1",
            patch_hash=PATCH,
            merged_sha=MERGE,
            observation_id=identifier,
            provenance={"source": "fixture", "measured_at": NOW.isoformat()},
        )
        observation = store.outcome_for(identifier)
        assert observation is not None
        assert store.claim_observation(observation)
        store.complete_observation(observation)
    before = store.path.read_bytes()
    result = handoff.compose_post_attempt_handoff(store, event_id="event", now=NOW)
    assert result["calibration"]["eligibility"] == "disabled"
    assert result["calibration"]["state"] == "insufficient_samples"
    assert store.path.read_bytes() == before
