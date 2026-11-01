"""Exported signal -> real pipeline -> proposal-bound read-only assessment."""

import json
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from codex.cognitive_brain.authority import AuthorityEnvelope
from codex.cognitive_brain.improvement_loop_runner import assess_evidence_record, main
from codex.cognitive_brain.improvement_pipeline import ImprovementPipeline

SHA = "a" * 40
NOW = datetime(2026, 11, 1, 0, 0, 10, tzinfo=timezone.utc)
COMMANDS = [["pytest", f"test_{kind}"] for kind in ("negative", "boundary", "regression")]


@pytest.fixture
def pipeline(monkeypatch):
    monkeypatch.setattr("os.environ", {})
    match = SimpleNamespace(
        pattern_id="measured-timeout",
        times_applied=3,
        success_rate=0.8,
        solutions=["TIMEOUT = 30\n"],
    )
    return ImprovementPipeline(
        repo="Aries-Serpent/_codex_",
        ref="refs/heads/fixture",
        sha=SHA,
        brain_interface=SimpleNamespace(query_patterns=lambda terms: [match]),
        authority=AuthorityEnvelope(),
    )


@pytest.fixture
def record():
    return {
        "repo": "Aries-Serpent/_codex_",
        "sha": SHA,
        "author": "fixture-author",
        "signal": {
            "source": "ci_workflow",
            "kind": "ci_job_failure",
            "measured_at": "2026-11-01T00:00:00Z",
            "availability": "measured",
            "summary": "Measured timeout failures",
            "details": {"files": ["src/measured.py"], "baseline_metric": 3},
        },
        "brief": {
            "module": "src/measured.py",
            "hypothesis": "Bound measured timeout failures",
            "baseline_metric": 3,
            "expected_metric": 0,
            "confidence": 0.8,
            "risk": "low",
            "acceptance_criteria": ["No measured timeout failures"],
            "verification_commands": COMMANDS,
            "lane_id": "fixture",
            "write_paths": ["src/measured.py"],
            "dependencies": [],
            "budget_seconds": 60,
            "stop_condition": "Stop after three corrections",
            "falsification": "Timeout failures persist",
        },
    }


def assess(record, pipeline, **kwargs):
    return assess_evidence_record(record, pipeline=pipeline, observed_at=NOW, **kwargs)


def attach_validation(record, result):
    record["validation"] = {
        "author": record["author"],
        "observer": "fixture-validator",
        "base_sha": SHA,
        "proposal_id": result["proposal"]["proposal_id"],
        "patch_hash": result["event"]["proposal"]["patch_hash"],
        "evidence_digest": result["evidence_digest"],
        "required_checks": ["negative", "boundary", "regression"],
        "checks": [
            {
                "name": kind,
                "kind": kind,
                "completed": True,
                "command": command,
                "returncode": 0,
                "evidence_ref": f"fixture:{kind}",
                "base_sha": SHA,
                "proposal_id": result["proposal"]["proposal_id"],
                "patch_hash": result["event"]["proposal"]["patch_hash"],
                "evidence_digest": result["evidence_digest"],
            }
            for kind, command in zip(("negative", "boundary", "regression"), COMMANDS, strict=True)
        ],
    }


def test_real_pipeline_and_bound_observations_never_authorize_execution(record, pipeline):
    before = deepcopy(record)
    first = assess(record, pipeline, human_approved=True)
    assert first["status"] == "unknown"
    assert first["pipeline_actionable"]
    assert first["review"]["questions"]
    assert record == before
    attach_validation(record, first)
    result = assess(record, pipeline, human_approved=True)
    assert result["status"] == "ready-for-human-review"
    assert result["validation"]["status"] == "pass"
    assert not result["execution_authorized"]
    assert not result["integration_authorized"]


def test_authority_default_remains_denied(record, pipeline):
    record["human_approved"] = True
    result = assess(record, pipeline)
    assert result["status"] == "blocked"
    assert not result["pipeline_actionable"]
    assert "human approval" in result["reason"]


@pytest.mark.parametrize("key", ["proposal_id", "patch_hash", "base_sha", "author"])
def test_foreign_validation_is_unknown(record, pipeline, key):
    attach_validation(record, assess(record, pipeline, human_approved=True))
    record["validation"][key] = "unrelated"
    assert assess(record, pipeline, human_approved=True)["status"] == "unknown"


@pytest.mark.parametrize(
    "scenario,status",
    [
        ("self-review", "unknown"),
        ("partial", "unknown"),
        ("failure", "fail"),
        ("commands", "unknown"),
    ],
)
def test_independent_checks_fail_closed(record, pipeline, scenario, status):
    attach_validation(record, assess(record, pipeline, human_approved=True))
    validation = record["validation"]
    if scenario == "self-review":
        validation["observer"] = record["author"]
    elif scenario == "partial":
        validation["checks"][0]["completed"] = False
    elif scenario == "failure":
        validation["checks"][0]["returncode"] = 1
    else:
        validation["checks"][0]["command"] = ["echo", "not the required test"]
    assert assess(record, pipeline, human_approved=True)["status"] == status


@pytest.mark.parametrize("scenario", ["stale", "future", "naive", "unavailable", "productivity"])
def test_unusable_or_productivity_signals_never_reach_pipeline(record, pipeline, scenario):
    pipeline.brain.query_patterns = lambda terms: pytest.fail("unusable signal reached pipeline")
    if scenario == "stale":
        record["signal"]["measured_at"] = "2026-10-01T00:00:00Z"
        record["brief"]["observed_at"] = "2026-10-01T00:00:01Z"
        record["brief"]["freshness_seconds"] = 10**10
    elif scenario == "future":
        record["signal"]["measured_at"] = "2027-01-01T00:00:00Z"
    elif scenario == "naive":
        record["signal"]["measured_at"] = "2026-11-01T00:00:00"
    elif scenario == "unavailable":
        record["signal"]["availability"] = "unavailable"
    else:
        record["brief"]["category"] = "session-productivity"
        record["signal"]["source"] = "manual"
    result = assess(record, pipeline)
    assert result["status"] in ("unknown", "signal-only")
    assert "event" not in result


@pytest.mark.parametrize("scenario", ["sha", "repo", "metric", "nan", "cycle", "path"])
def test_malformed_context_and_budgets_raise(record, pipeline, scenario):
    if scenario in ("sha", "repo"):
        record[scenario] = "other"
    elif scenario == "metric":
        record["brief"]["baseline_metric"] = 99
    elif scenario == "nan":
        record["brief"]["expected_metric"] = float("nan")
    elif scenario == "cycle":
        record["correction_cycle"] = 4
    else:
        record["brief"]["write_paths"] = ["src/../../outside"]
    with pytest.raises(ValueError):
        assess(record, pipeline)


def test_proposal_cannot_exceed_brief_boundary(record, pipeline):
    record["brief"]["write_paths"] = ["tests"]
    result = assess(record, pipeline, human_approved=True)
    assert result["status"] == "blocked"
    assert "write boundary" in result["reason"]


def test_validation_cannot_be_replayed_against_different_target(record, pipeline):
    record["brief"]["write_paths"] = ["src"]
    attach_validation(record, assess(record, pipeline, human_approved=True))
    record["signal"]["details"]["files"] = ["src/other.py"]
    result = assess(record, pipeline, human_approved=True)
    assert result["status"] == "unknown"
    assert result["evidence_digest"] != record["validation"]["evidence_digest"]


def test_each_observation_must_bind_current_proposal(record, pipeline):
    attach_validation(record, assess(record, pipeline, human_approved=True))
    record["validation"]["checks"][0]["evidence_digest"] = "foreign"
    assert assess(record, pipeline, human_approved=True)["status"] == "unknown"


@pytest.mark.parametrize("command", [[None], [""], "pytest", [], ["pytest", "\0"]])
def test_malformed_commands_cannot_produce_readiness(record, pipeline, command):
    record["brief"]["verification_commands"] = [command]
    attach_validation(record, assess(record, pipeline, human_approved=True))
    for check in record["validation"]["checks"]:
        check["command"] = command
    assert assess(record, pipeline, human_approved=True)["status"] == "unknown"


@pytest.mark.parametrize("content,sha", [("", SHA), ("\n \n", SHA), ("", "not-a-sha")])
def test_cli_empty_evidence_is_not_success(tmp_path, capsys, content, sha):
    log = tmp_path / "bundle.jsonl"
    log.write_text(content, encoding="utf-8")
    assert (
        main(
            [
                str(log),
                "--evidence-bundle",
                "--repo",
                "Aries-Serpent/_codex_",
                "--ref",
                "refs/heads/fixture",
                "--sha",
                sha,
                "--repo-root",
                str(tmp_path),
            ]
        )
        == 1
    )


def test_cli_reports_malformed_input_without_echoing_content(tmp_path, monkeypatch, capsys):
    log = tmp_path / "bundle.jsonl"
    log.write_text('{"unexpected": "private input"}\n', encoding="utf-8")
    result = main(
        [
            str(log),
            "--evidence-bundle",
            "--repo",
            "Aries-Serpent/_codex_",
            "--ref",
            "refs/heads/fixture",
            "--sha",
            SHA,
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert result == 1
    captured = capsys.readouterr()
    assert "invalid evidence record at line 1" in captured.err
    assert "private input" not in captured.out + captured.err


@pytest.mark.parametrize("malformed", [False, True])
def test_cli_emits_complete_assessment_and_retains_valid_records(
    tmp_path, monkeypatch, capsys, record, pipeline, malformed
):
    from codex.cognitive_brain import improvement_loop_runner as runner

    attach_validation(record, assess(record, pipeline, human_approved=True))
    monkeypatch.setattr(runner, "AgentBrainInterface", lambda **kwargs: pipeline.brain)
    original = runner.assess_evidence_record
    monkeypatch.setattr(
        runner,
        "assess_evidence_record",
        lambda item, **kwargs: original(item, observed_at=NOW, **kwargs),
    )
    log = tmp_path / "bundle.jsonl"
    log.write_text(
        json.dumps(record) + "\n" + ("bad-json\n" if malformed else ""), encoding="utf-8"
    )
    result = main(
        [
            str(log),
            "--evidence-bundle",
            "--human-approved",
            "--repo",
            pipeline.repo,
            "--ref",
            pipeline.ref,
            "--sha",
            SHA,
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert result == (1 if malformed else 0)
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "ready-for-human-review"
    assert output["evidence_digest"] == record["validation"]["evidence_digest"]
    assert not output["execution_authorized"]
