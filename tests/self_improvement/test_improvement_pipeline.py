"""Stage 2 acceptance: deterministic signal -> pattern -> proposal slice."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_pipeline import (
    ImprovementPipeline,
    load_pda_signals,
    signal_from_pda_record,
)

PATTERN_STORE = {
    "patterns": {
        "ci_timeout": {
            "id": "RP-019",
            "category": "ci_cd",
            "symptoms": [
                "ci job failure timeout",
                "workflow timeout minutes",
                "job timed out",
                "pytest",
            ],
            "solutions": ["jobs:\n  test:\n    timeout-minutes: 30"],
            "success_rate": 0.9,
            "times_applied": 3,
        }
    }
}


def _brain(tmp_path: Path) -> AgentBrainInterface:
    store_dir = tmp_path / ".codex" / "cognitive_brain"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "pattern_learning_store.json").write_text(json.dumps(PATTERN_STORE))
    return AgentBrainInterface(agent_id="test-agent", repo_root=tmp_path, auto_register=False)


def _pipeline(tmp_path: Path) -> ImprovementPipeline:
    return ImprovementPipeline(
        repo="Aries-Serpent/_codex_",
        ref="refs/heads/main",
        sha="cd47831318fe",
        brain_interface=_brain(tmp_path),
        authority=AuthorityEnvelope(require_human_approval=False),
    )


def _failure_record() -> dict:
    return {
        "type": "failure",
        "timestamp": "2026-10-19T00:00:00+00:00",
        "pattern_id": "RP-019",
        "workflow": "ci",
        "error_text": "job timed out after 360 minutes",
        "root_cause": "ci job failure timeout on workflow timeout minutes",
        "fix_template": "jobs:\n  test:\n    timeout-minutes: 30",
        "files": ["src/codex/ci_config.py"],
        "verification_cmd": "nox -s tests",
    }


def test_signal_to_pattern_to_proposal(tmp_path: Path, monkeypatch) -> None:
    # Strip ambient CI secret metadata so the authority check measures the
    # action, not the surrounding automation environment.
    monkeypatch.setattr("os.environ", {})
    signal = signal_from_pda_record(_failure_record())
    decision = _pipeline(tmp_path).process_signal(signal)
    assert decision.actionable, decision.reason
    event = decision.event
    event.validate()
    assert event.pattern is not None and event.pattern.pattern_id == "RP-019"
    assert event.proposal is not None
    assert event.proposal.files == ("src/codex/ci_config.py",)


class _FixedDatetime:
    """Deterministic stand-in for datetime used in replay testing."""

    @staticmethod
    def now(tz=None):
        from datetime import datetime, timezone

        return datetime(2026, 10, 19, tzinfo=timezone.utc)


def test_replay_is_deterministic(tmp_path: Path, monkeypatch) -> None:
    signal = signal_from_pda_record(_failure_record())
    monkeypatch.setattr(
        "codex.cognitive_brain.improvement_pipeline.datetime",
        _FixedDatetime,
    )
    first = _pipeline(tmp_path).process_signal(signal)
    second = _pipeline(tmp_path).process_signal(signal)
    assert first.event == second.event
    assert first == second


def test_no_match_case(tmp_path: Path) -> None:
    record = _failure_record()
    record["root_cause"] = "zzzqxx unmatched failure domain"
    record["error_text"] = "zzzqxx"
    record["fix_template"] = ""
    decision = _pipeline(tmp_path).process_signal(signal_from_pda_record(record))
    assert not decision.actionable
    assert "no pattern matched" in decision.reason
    assert decision.event.proposal is None


def test_non_actionable_signal(tmp_path: Path) -> None:
    signal = signal_from_pda_record(_failure_record())
    heartbeat = type(signal)(
        source=signal.source,
        kind="heartbeat",
        measured_at=signal.measured_at,
        availability=signal.availability,
        summary="routine heartbeat",
    )
    decision = _pipeline(tmp_path).process_signal(heartbeat)
    assert not decision.actionable
    assert "non-actionable" in decision.reason


def test_malformed_pda_record_fails_closed() -> None:
    with pytest.raises(ValueError):
        signal_from_pda_record({"type": "session", "timestamp": "2026-10-19T00:00:00Z"})
    with pytest.raises(ValueError):
        signal_from_pda_record({"type": "failure"})


def test_load_pda_signals_filters_non_failures(tmp_path: Path) -> None:
    log = tmp_path / "pda.jsonl"
    log.write_text(
        json.dumps(_failure_record())
        + "\n"
        + json.dumps({"type": "session", "timestamp": "t"})
        + "\n"
    )
    signals = load_pda_signals(log)
    assert len(signals) == 1
    assert signals[0].kind == "ci_job_failure"
