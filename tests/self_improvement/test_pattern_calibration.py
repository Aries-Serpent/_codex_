"""Receipt-backed calibration is a read-only model diagnostic."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface, LearningFeedback
from codex.cognitive_brain.evidence_store import EvidenceIntegrityError, EvidenceStore
from codex.cognitive_brain.pattern_calibration import (
    MAX_EVIDENCE_AGE,
    _beta_quantile,
    calibrate_pattern,
    event_partition,
)

NOW = datetime(2026, 11, 2, tzinfo=timezone.utc)
MEASURED = NOW - timedelta(days=1)


def _ids(partition: str, count: int) -> list[str]:
    return [f"event-{i}" for i in range(1000) if event_partition(f"event-{i}") == partition][:count]


def _record(
    store: EvidenceStore,
    event_id: str,
    *,
    qualified: bool = True,
    synthetic: bool = False,
    outcome: str = "success",
    observation_id: str | None = None,
    merge_identity: str | None = None,
    measured: datetime = MEASURED,
    pattern_id: str = "RP-1",
) -> None:
    identity = merge_identity or event_id
    store.record_outcome(
        event_id=event_id,
        merged=True,
        outcome=outcome,
        pattern_id=pattern_id,
        patch_hash=hashlib.sha256(identity.encode()).hexdigest(),
        merged_sha=hashlib.sha1(identity.encode()).hexdigest(),
        observation_id=observation_id or event_id,
        provenance={"source": "trusted-ci-fixture", "measured_at": measured.isoformat()},
        synthetic=synthetic,
    )
    if qualified:
        observation = store.outcome_for(event_id)
        assert observation is not None
        assert store.claim_observation(observation)
        store.complete_observation(observation)


def _populated(path: Path) -> EvidenceStore:
    # Offline verifier fixture exercises store-issued receipts, not live CI.
    store = EvidenceStore(path, measurement_verifier=lambda _: True)
    for event_id in _ids("training", 20) + _ids("holdout", 10):
        _record(store, event_id)
    return store


def test_qualified_reconstruction_is_read_only_and_separate_from_ema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    recovered = EvidenceStore(store.path)  # No ambient verifier required for reconstruction.
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    cached = copy.deepcopy(store._qualifications)

    def forbid_mutation(*args: object, **kwargs: object) -> None:
        raise AssertionError("calibration must not consume evidence or submit learning")

    for method in ("claim_observation", "complete_observation", "record_outcome", "record_event"):
        monkeypatch.setattr(EvidenceStore, method, forbid_mutation)
    monkeypatch.setattr(AgentBrainInterface, "submit_learning", forbid_mutation)
    result = calibrate_pattern(recovered, "RP-1", now=NOW, uncalibrated_ema=0.37)
    assert result.state == "calibrated"
    assert result.diagnostic_only is True
    assert (result.sample_count, result.training_count, result.holdout_count) == (30, 20, 10)
    assert (result.alpha, result.beta) == (21, 1)
    assert result.posterior_mean == pytest.approx(21 / 22)
    assert result.credible_interval == pytest.approx((0.025 ** (1 / 21), 0.975 ** (1 / 21)))
    assert result.holdout_brier == pytest.approx((1 / 22) ** 2)
    assert result.uncalibrated_ema == 0.37
    assert result.training_hash != result.holdout_hash
    assert result == calibrate_pattern(recovered, "RP-1", now=NOW, uncalibrated_ema=0.37)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    assert store._qualifications == cached
    with pytest.raises(FrozenInstanceError):
        result.state = "expired"  # type: ignore[misc]


@pytest.mark.parametrize("kind", ["synthetic", "unqualified", "legacy", "pending"])
def test_nonproduction_evidence_never_counts(tmp_path: Path, kind: str) -> None:
    store = EvidenceStore(
        tmp_path / "evidence.jsonl",
        measurement_verifier=lambda _: True,
        allow_synthetic=kind == "synthetic",
    )
    if kind == "legacy":
        store.record_event(
            {"event_id": "old", "pattern": {"pattern_id": "RP-1", "success_rate": 0.99}}
        )
        store.record("confidence", "old", {"qualified": True, "success": True})
    else:
        _record(store, "event", qualified=kind == "synthetic", synthetic=kind == "synthetic")
        if kind == "pending":
            observation = store.outcome_for("event")
            assert observation is not None
            store.claim_observation(observation)
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 0
    assert result.credible_interval == pytest.approx((0.025, 0.975))


def test_empty_store_and_caller_flags_cannot_manufacture_qualification(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "absent.jsonl")
    store._qualifications["forged"] = "production"
    assert calibrate_pattern(store, "RP-1", now=NOW).sample_count == 0
    assert not list(tmp_path.iterdir())
    with pytest.raises(TypeError, match="EvidenceStore"):
        calibrate_pattern([{"qualified": True}], "RP-1", now=NOW)  # type: ignore[arg-type]


def test_persisted_receipt_labels_are_not_qualification(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    _record(store, "unqualified", qualified=False)
    store.record(
        "confidence",
        "unqualified",
        {
            "qualified": True,
            "mode": "production",
            "proof_kind": "trusted_measurement_consumption",
        },
    )
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 0


@pytest.mark.parametrize(
    ("field", "replacement"),
    [("event_id", "other-event"), ("patch_hash", "f" * 64)],
)
def test_receipt_rebound_to_other_evidence_fails_closed(
    tmp_path: Path, field: str, replacement: str
) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    _record(store, "original")
    records = store.audit_trail()
    receipt = next(record for record in records if record["kind"] == "qualification")
    receipt["payload"][field] = replacement
    store.path.write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
    )
    before = store.path.read_bytes()
    with pytest.raises(EvidenceIntegrityError, match="qualification"):
        calibrate_pattern(store, "RP-1", now=NOW)
    assert store.path.read_bytes() == before


def test_repeated_event_and_retries_cannot_double_weight_or_cross_partitions(
    tmp_path: Path,
) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    before = calibrate_pattern(store, "RP-1", now=NOW)
    for partition in ("training", "holdout"):
        event_id = _ids(partition, 1)[0]
        observation = store.outcome_for(event_id)
        assert observation is not None
        store.record_outcome(**dict(observation))
        assert store.claim_observation(observation) is False
        for retry in range(2):
            _record(
                store,
                event_id,
                observation_id=f"retry-{retry}",
                measured=MEASURED + timedelta(minutes=retry + 1),
            )
    after = calibrate_pattern(store, "RP-1", now=NOW)
    assert after == before
    assert (after.training_count, after.holdout_count, after.sample_count) == (20, 10, 30)


def test_synthetic_receipts_in_production_journal_are_excluded(tmp_path: Path) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    fixture_store = EvidenceStore(store.path, allow_synthetic=True)
    _record(fixture_store, "synthetic", synthetic=True)
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "calibrated"
    assert result.sample_count == 30


@pytest.mark.parametrize(("training", "holdout"), [(0, 0), (19, 10), (20, 9)])
def test_minimum_samples(tmp_path: Path, training: int, holdout: int) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    for event_id in _ids("training", training) + _ids("holdout", holdout):
        _record(store, event_id)
    assert calibrate_pattern(store, "RP-1", now=NOW).state == "insufficient_samples"


def test_provenance_aliases_overlap_even_with_disjoint_event_ids(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    for event_id in _ids("training", 1) + _ids("holdout", 1):
        _record(store, event_id, observation_id="same-measurement", merge_identity="same-merge")
    assert calibrate_pattern(store, "RP-1", now=NOW).state == "holdout_overlap"


def test_same_partition_provenance_is_deduplicated(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    for event_id in _ids("training", 2):
        _record(store, event_id, observation_id="same-measurement", merge_identity="same-merge")
    assert calibrate_pattern(store, "RP-1", now=NOW).training_count == 1


def test_expiry_and_unqualified_history_downgrade(tmp_path: Path) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    assert calibrate_pattern(store, "RP-1", now=NOW).state == "calibrated"
    assert calibrate_pattern(store, "RP-1", now=MEASURED + MAX_EVIDENCE_AGE).state == "expired"
    _record(store, "unknown", qualified=False)
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 0
    assert "eligibility" in result.reason


def test_holdout_brier_failure_is_not_calibrated(tmp_path: Path) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    before = calibrate_pattern(store, "RP-1", now=NOW)
    for index, event_id in enumerate(_ids("holdout", 10)):
        _record(
            store,
            event_id,
            outcome="regression" if index % 2 == 0 else "success",
            observation_id=f"later-{event_id}",
            measured=MEASURED + timedelta(hours=1),
        )
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 30
    assert result.holdout_brier is not None and result.holdout_brier > 0.15
    assert "Brier" in result.reason
    assert (result.alpha, result.beta, result.posterior_mean, result.credible_interval) == (
        before.alpha,
        before.beta,
        before.posterior_mean,
        before.credible_interval,
    )
    assert result.training_hash == before.training_hash
    assert result.holdout_hash == before.holdout_hash
    assert result.holdout_brier != before.holdout_brier


def test_beta_quantiles_include_failure_and_mixed_cases() -> None:
    assert _beta_quantile(0.025, 1, 21) == pytest.approx(1 - 0.975 ** (1 / 21))
    assert _beta_quantile(0.5, 11, 11) == pytest.approx(0.5)


def test_disabled_breaker_downgrades_previously_calibrated_result(tmp_path: Path) -> None:
    store = _populated(tmp_path / "evidence.jsonl")
    for index in range(3):
        _record(store, f"regression-{index}", outcome="regression")
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 0


def test_simultaneous_conflicting_measurements_fail_closed(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    _record(store, "event")
    _record(store, "event", observation_id="second", outcome="regression")
    result = calibrate_pattern(store, "RP-1", now=NOW)
    assert result.state == "insufficient_samples"
    assert result.sample_count == 0
    assert "ambiguous" in result.reason


def test_bad_provenance_time_fails_closed(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl", measurement_verifier=lambda _: True)
    _record(store, "future", measured=NOW + timedelta(days=1))
    assert calibrate_pattern(store, "RP-1", now=NOW).sample_count == 0
    with pytest.raises(ValueError, match="timezone"):
        calibrate_pattern(store, "RP-1", now=NOW.replace(tzinfo=None))


def test_corrupt_store_errors_are_not_silently_loaded(tmp_path: Path) -> None:
    store = EvidenceStore(tmp_path / "evidence.jsonl")
    store.path.write_text("broken\n", encoding="utf-8")
    with pytest.raises(EvidenceIntegrityError):
        calibrate_pattern(store, "RP-1", now=NOW)


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        ("success", 0.93),
        ("failure", 0.63),
        ("partial", 0.78),
    ],
)
def test_legacy_ema_formula_remains_unchanged(outcome: str, expected: float) -> None:
    brain = object.__new__(AgentBrainInterface)
    brain._patterns = {"fixture": {"id": "RP-1", "success_rate": 0.9}}
    # Exercise the authoritative EMA method without persisting any brain data.
    brain._save_patterns = lambda: None
    feedback = LearningFeedback(
        agent_id="fixture",
        pattern_id="RP-1",
        outcome=outcome,
    )
    assert brain._update_pattern_stats(feedback)
    assert brain._patterns["fixture"]["success_rate"] == pytest.approx(expected)
