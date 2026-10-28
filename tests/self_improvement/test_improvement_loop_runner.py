"""Stage 3 acceptance: runnable PDA failure-log -> improvement loop wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aries_serpent_core.cognitive.brain_interface import AgentBrainInterface
from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_loop_runner import (
    EXIT_MALFORMED,
    EXIT_OK,
    main,
    run_from_pda,
)
from codex.cognitive_brain.improvement_pipeline import (
    ImprovementPipeline,
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

REPO = "Aries-Serpent/_codex_"
REF = "refs/heads/main"
SHA = "cd47831318fe"  # pragma: allowlist secret


def _brain(tmp_path: Path) -> AgentBrainInterface:
    store_dir = tmp_path / ".codex" / "cognitive_brain"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "pattern_learning_store.json").write_text(json.dumps(PATTERN_STORE))
    return AgentBrainInterface(agent_id="test-agent", repo_root=tmp_path, auto_register=False)


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


def _write_log(tmp_path: Path, *records: dict) -> Path:
    log = tmp_path / "pda.jsonl"
    log.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return log


def _run(tmp_path: Path, log: Path, **kwargs):
    return run_from_pda(
        log,
        repo=REPO,
        ref=REF,
        sha=SHA,
        brain_interface=_brain(tmp_path),
        authority=AuthorityEnvelope(require_human_approval=False),
        **kwargs,
    )


def test_failure_record_produces_actionable_event(tmp_path: Path, monkeypatch) -> None:
    # Strip ambient CI secret metadata so the authority check measures the
    # action, not the surrounding automation environment.
    monkeypatch.setattr("os.environ", {})
    log = _write_log(tmp_path, _failure_record())
    decisions = _run(tmp_path, log)
    assert len(decisions) == 1
    decision = decisions[0]
    assert decision.actionable, decision.reason
    decision.event.validate()
    event_dict = decision.event.to_dict()
    assert event_dict["repo"] == REPO
    assert event_dict["pattern"]["pattern_id"] == "RP-019"
    assert list(event_dict["proposal"]["files"]) == ["src/codex/ci_config.py"]


def test_decisions_preserve_input_order(tmp_path: Path) -> None:
    record = _failure_record()
    unmatched = _failure_record()
    unmatched["root_cause"] = "zzzqxx unmatched failure domain"
    unmatched["error_text"] = "zzzqxx"
    unmatched["fix_template"] = ""
    log = _write_log(tmp_path, record, unmatched)
    decisions = _run(tmp_path, log)
    assert len(decisions) == 2
    assert decisions[0].event.signal.summary == record["root_cause"]
    assert decisions[1].event.signal.summary == unmatched["root_cause"]


def test_no_match_signal_is_inactionable(tmp_path: Path) -> None:
    record = _failure_record()
    record["root_cause"] = "zzzqxx unmatched failure domain"
    record["error_text"] = "zzzqxx"
    record["fix_template"] = ""
    log = _write_log(tmp_path, record)
    (decision,) = _run(tmp_path, log)
    assert not decision.actionable
    assert "no pattern matched" in decision.reason


def test_non_actionable_signal_kind(tmp_path: Path) -> None:
    signal = signal_from_pda_record(_failure_record())
    heartbeat = type(signal)(
        source=signal.source,
        kind="heartbeat",
        measured_at=signal.measured_at,
        availability=signal.availability,
        summary="routine heartbeat",
    )
    pipeline = ImprovementPipeline(
        repo=REPO,
        ref=REF,
        sha=SHA,
        brain_interface=_brain(tmp_path),
        authority=AuthorityEnvelope(require_human_approval=False),
    )
    decision = pipeline.process_signal(heartbeat)
    assert not decision.actionable
    assert "non-actionable" in decision.reason


def test_malformed_record_fails_closed(tmp_path: Path) -> None:
    # Non-failure type reaching signal_from_pda_record raises.
    with pytest.raises(ValueError):
        signal_from_pda_record({"type": "failure"})
    # Missing-timestamp failure record embedded in a log aborts run_from_pda.
    bad = _failure_record()
    del bad["timestamp"]
    log = _write_log(tmp_path, bad)
    with pytest.raises(ValueError):
        _run(tmp_path, log)


def test_cli_emits_jsonl_and_exit_zero(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("os.environ", {})
    _brain(tmp_path)  # materialize the pattern store for --repo-root
    log = _write_log(tmp_path, _failure_record())
    rc = main(
        [
            str(log),
            "--repo",
            REPO,
            "--ref",
            REF,
            "--sha",
            SHA,
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == EXIT_OK
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1
    event = json.loads(out[0])
    assert event["repo"] == REPO
    assert event["pattern"]["pattern_id"] == "RP-019"


def test_cli_malformed_record_fails_closed_but_emits(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("os.environ", {})
    _brain(tmp_path)  # materialize the pattern store for --repo-root
    bad = _failure_record()
    del bad["timestamp"]
    log = _write_log(tmp_path, _failure_record(), bad)
    rc = main(
        [
            str(log),
            "--repo",
            REPO,
            "--ref",
            REF,
            "--sha",
            SHA,
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == EXIT_MALFORMED
    captured = capsys.readouterr()
    # The valid record still emits its decision event.
    assert len(captured.out.strip().splitlines()) == 1
    # The malformed record is reported on stderr.
    assert "malformed record" in captured.err
