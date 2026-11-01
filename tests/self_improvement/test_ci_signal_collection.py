"""Bounded metadata collection never invents health or GitHub authority."""

import json
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from codex.cognitive_brain.ci_signal_collection import (
    _read_public_metadata,
    collect_ci_run,
    public_actions_reader,
)
from codex.cognitive_brain.improvement_loop_runner import assess_evidence_record

REPO = "Aries-Serpent/_codex_"
SHA = "a" * 40
NOW = datetime(2026, 11, 1, 2, 0, 10, tzinfo=timezone.utc)


def run():
    return {
        "id": 42,
        "repository": {"full_name": REPO},
        "head_sha": SHA,
        "run_attempt": 2,
        "status": "completed",
        "conclusion": "failure",
        "updated_at": "2026-11-01T02:00:00Z",
    }


def job(identifier=1, conclusion="failure"):
    return {
        "id": identifier,
        "run_id": 42,
        "run_attempt": 2,
        "head_sha": SHA,
        "status": "completed",
        "conclusion": conclusion,
        "started_at": "2026-11-01T01:59:00Z",
        "completed_at": "2026-11-01T02:00:00Z",
        "name": "private job name",
        "steps": [{"name": "private step"}],
    }


class Reader:
    def __init__(self, jobs=None, first=None, final=None):
        self.first = first if first is not None else run()
        self.final = final if final is not None else deepcopy(self.first)
        self.jobs = jobs if jobs is not None else [job()]
        self.paths = []

    def __call__(self, path):
        self.paths.append(path)
        if "/jobs?" not in path:
            return 200, deepcopy(self.first if len(self.paths) == 1 else self.final)
        page = int(path.rsplit("=", 1)[1])
        return 200, {
            "total_count": len(self.jobs),
            "jobs": deepcopy(self.jobs[(page - 1) * 100 : page * 100]),
        }


def collect(reader, **kwargs):
    return collect_ci_run(repo=REPO, sha=SHA, run_id=42, reader=reader, observed_at=NOW, **kwargs)


def test_complete_failure_retains_only_structured_measurements():
    reader = Reader([job(), job(2, "success"), job(3, "skipped")])
    signal = collect(reader)
    assert signal.availability == "measured"
    assert signal.kind == "ci_job_failure"
    assert signal.details["baseline_metric"] == 1
    assert signal.details["run_attempt"] == 2
    assert signal.details["job_count"] == 3
    assert signal.details["measured_job_count"] == 2
    assert signal.measured_at == "2026-11-01T02:00:00Z"
    assert reader.paths == [
        f"/repos/{REPO}/actions/runs/42",
        f"/repos/{REPO}/actions/runs/42/attempts/2/jobs?per_page=100&page=1",
        f"/repos/{REPO}/actions/runs/42",
    ]
    assert "private" not in json.dumps(asdict(signal))


def test_success_is_metric_only_not_a_failure_proposal():
    snapshot = {**run(), "conclusion": "success"}
    signal = collect(Reader([job(conclusion="success")], first=snapshot))
    assert signal.availability == "measured"
    assert signal.kind == "metric_sample"
    assert signal.details["baseline_metric"] == 0


@pytest.mark.parametrize("status", [401, 403, 404, 429])
def test_denied_source_is_unavailable_without_zero_baseline(status):
    signal = collect(lambda path: (status, {"message": "private credential details"}))
    assert signal.availability == "unavailable"
    assert "baseline_metric" not in signal.details
    assert "private" not in json.dumps(asdict(signal))


@pytest.mark.parametrize(
    "status,conclusion",
    [
        ("in_progress", None),
        ("completed", "action_required"),
        ("completed", "cancelled"),
        ("queued", None),
    ],
)
def test_gated_or_nonterminal_run_never_reports_measured_health(status, conclusion):
    reader = Reader(first={**run(), "status": status, "conclusion": conclusion})
    assert collect(reader).availability == "unavailable"
    assert len(reader.paths) == 1


@pytest.mark.parametrize(
    "key,value",
    [
        ("head_sha", "b" * 40),
        ("id", 43),
        ("repository", {"full_name": "other/repo"}),
        ("run_attempt", True),
        ("updated_at", "2026-11-01T02:00:00"),
        ("updated_at", "2027-01-01T00:00:00Z"),
    ],
)
def test_foreign_or_invalid_run_identity_is_error(key, value):
    assert collect(Reader(first={**run(), key: value})).availability == "error"


@pytest.mark.parametrize(
    "key,value",
    [
        ("head_sha", "b" * 40),
        ("run_id", 43),
        ("id", True),
        ("run_attempt", 1),
        ("run_attempt", None),
        ("completed_at", "2027-01-01T00:00:00Z"),
        ("started_at", "2027-01-01T00:00:00Z"),
    ],
)
def test_foreign_or_invalid_job_identity_is_error(key, value):
    assert collect(Reader([{**job(), key: value}])).availability == "error"


def test_duplicate_jobs_and_over_budget_inventory_fail():
    assert collect(Reader([job(), job()])).availability == "error"
    reader = Reader([job(i + 1) for i in range(501)])
    assert collect(reader).availability == "error"
    assert len(reader.paths) == 2


def test_paginated_job_inventory_is_complete_and_bounded():
    reader = Reader([job(i + 1) for i in range(101)])
    signal = collect(reader)
    assert signal.details["baseline_metric"] == 101
    assert len(reader.paths) == 4


def test_changed_page_count_fails_closed():
    reader = Reader([job(i + 1) for i in range(101)])

    def changing(path):
        code, payload = reader(path)
        if path.endswith("page=2"):
            payload["total_count"] = 100
        return code, payload

    assert collect(changing).availability == "error"


@pytest.mark.parametrize(
    "key,value",
    [
        ("head_sha", "b" * 40),
        ("run_attempt", 3),
        ("conclusion", "success"),
        ("updated_at", "2026-11-01T02:00:01Z"),
    ],
)
def test_changed_run_cannot_be_recorded_as_same_attempt(key, value):
    assert collect(Reader(final={**run(), key: value})).availability == "error"


def test_empty_and_unexecuted_jobs_are_unavailable():
    assert collect(Reader([])).availability == "unavailable"
    assert collect(Reader([job(conclusion="skipped")])).availability == "unavailable"
    assert collect(Reader([job(conclusion="cancelled")])).availability == "unavailable"


def test_reader_exception_does_not_leak_error_text():
    def broken(path):
        raise RuntimeError("private credential details")

    signal = collect(broken)
    assert signal.availability == "error"
    assert "private" not in json.dumps(asdict(signal))


@pytest.mark.parametrize(
    "repo,sha,run_id",
    [
        ("../other", SHA, 42),
        ("owner/..", SHA, 42),
        (REPO, "main", 42),
        (REPO, SHA, True),
        (REPO, SHA, 0),
    ],
)
def test_invalid_request_context_never_calls_reader(repo, sha, run_id):
    with pytest.raises(ValueError):
        collect_ci_run(
            repo=repo,
            sha=sha,
            run_id=run_id,
            reader=lambda path: pytest.fail("invalid context called reader"),
        )


@pytest.mark.parametrize(
    "path",
    [
        "https://evil.example/api",
        "/repos/owner/repo/issues",
        "/repos/o/r/actions/runs/1/approve",
        "/repos/o/r/actions/runs/1/attempts/1/jobs?per_page=100&page=6",
    ],
)
def test_public_transport_rejects_non_metadata_paths(path):
    with pytest.raises(ValueError):
        public_actions_reader(path)


def test_transport_no_auth_redirects_or_ambient_config(monkeypatch, tmp_path):
    import requests

    seen = {}

    class Response:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_content(self, chunk_size):
            return iter([b'{"id":42}'])

    class Session:
        trust_env = True

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url, **kwargs):
            seen.update(url=url, trust_env=self.trust_env, **kwargs)
            return Response()

    monkeypatch.setattr(requests, "Session", Session)
    output = tmp_path / "response"
    _read_public_metadata(f"/repos/{REPO}/actions/runs/42", str(output))
    assert output.read_bytes() == b'200\n{"id":42}'
    assert seen["url"] == f"https://api.github.com/repos/{REPO}/actions/runs/42"
    assert seen["trust_env"] is False and seen["allow_redirects"] is False
    assert "Authorization" not in seen["headers"]
    assert seen["timeout"] == (10, 10) and seen["stream"]


def test_response_size_limit(monkeypatch, tmp_path):
    import requests

    class Response:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def iter_content(self, chunk_size):
            return iter([b"x" * 1048577])

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr(requests, "Session", Session)
    output = tmp_path / "response"
    _read_public_metadata(f"/repos/{REPO}/actions/runs/42", str(output))
    assert output.read_bytes() == b"0\n"


def test_worker_timeout_terminates_blocking_transport(monkeypatch):
    from codex.cognitive_brain import ci_signal_collection as collection

    events = []
    outputs = []

    class Worker:
        pid = 123

        def start(self):
            outputs[0].write_bytes(b"200\n{")
            events.append("start")

        def is_alive(self):
            return "kill" not in events

        def terminate(self):
            events.append("terminate")

        def kill(self):
            events.append("kill")

        def join(self, timeout):
            events.append(("join", timeout))

        def close(self):
            events.append("close")

    def process(**kwargs):
        from pathlib import Path

        outputs.append(Path(kwargs["args"][1]))
        return Worker()

    context = SimpleNamespace(Process=process)
    monkeypatch.setattr(collection.multiprocessing, "get_context", lambda method: context)
    with pytest.raises(TimeoutError):
        public_actions_reader(f"/repos/{REPO}/actions/runs/42", timeout=0.1)
    assert "terminate" in events and "kill" in events and "close" in events
    assert len([event for event in events if isinstance(event, tuple) and event[0] == "join"]) == 3
    assert not outputs[0].parent.exists()


def test_completed_worker_response_is_read_only_after_exit(monkeypatch):
    from pathlib import Path

    from codex.cognitive_brain import ci_signal_collection as collection

    outputs = []

    class Worker:
        pid = 123

        def start(self):
            outputs[0].write_bytes(b'200\n{"id":42}')

        def is_alive(self):
            return False

        def join(self, timeout):
            pass

        def close(self):
            pass

    def process(**kwargs):
        outputs.append(Path(kwargs["args"][1]))
        return Worker()

    monkeypatch.setattr(
        collection.multiprocessing,
        "get_context",
        lambda method: SimpleNamespace(Process=process),
    )
    assert public_actions_reader(f"/repos/{REPO}/actions/runs/42") == (200, {"id": 42})
    assert not outputs[0].parent.exists()


def test_collection_flows_into_existing_pipeline_without_authority(monkeypatch):
    from codex.cognitive_brain.authority import AuthorityEnvelope
    from codex.cognitive_brain.improvement_pipeline import ImprovementPipeline

    monkeypatch.setattr("os.environ", {})
    brain = SimpleNamespace(
        query_patterns=lambda terms: [
            SimpleNamespace(
                pattern_id="measured", times_applied=2, success_rate=0.8, solutions=["x = 1\n"]
            )
        ]
    )
    pipeline = ImprovementPipeline(
        repo=REPO,
        ref="refs/heads/fixture",
        sha=SHA,
        brain_interface=brain,
        authority=AuthorityEnvelope(),
    )
    signal = asdict(collect(Reader()))
    signal["details"]["files"] = ["src/fixture.py"]
    record = {
        "repo": REPO,
        "sha": SHA,
        "signal": signal,
        "brief": {
            "module": "src/fixture.py",
            "hypothesis": "Reduce failed jobs",
            "baseline_metric": 1,
            "expected_metric": 0,
            "confidence": 0.8,
            "risk": "low",
            "acceptance_criteria": ["Zero failures"],
            "verification_commands": [["pytest"]],
            "lane_id": "fixture",
            "write_paths": ["src/fixture.py"],
            "dependencies": [],
            "budget_seconds": 60,
            "stop_condition": "Three corrections",
            "falsification": "Failures persist",
        },
    }
    result = assess_evidence_record(record, pipeline=pipeline, observed_at=NOW)
    assert result["status"] == "blocked"
    assert result["event"]["signal"]["details"]["workflow_run_id"] == 42
    assert result["event"]["signal"]["details"]["run_attempt"] == 2
    assert not result["execution_authorized"] and not result["integration_authorized"]


def test_collection_deadline_exhaustion_fails_without_more_reads(monkeypatch):
    from codex.cognitive_brain import ci_signal_collection as collection

    clock = iter([0, 1, 61])
    monkeypatch.setattr(collection.time, "monotonic", lambda: next(clock))
    reader = Reader()
    signal = collect(reader)
    assert signal.availability == "error"
    assert len(reader.paths) == 1


def test_skipped_job_cannot_refresh_old_measurement():
    snapshot = {**run(), "updated_at": "2026-11-01T02:00:00Z"}
    old = {**job(), "started_at": "2026-10-01T01:59:00Z", "completed_at": "2026-10-01T02:00:00Z"}
    skipped = job(2, "skipped")
    signal = collect(Reader([old, skipped], first=snapshot))
    assert signal.measured_at == "2026-10-01T02:00:00Z"


@pytest.mark.parametrize(
    "payload",
    [
        {"total_count": 2, "jobs": []},
        {"total_count": True, "jobs": []},
        {"total_count": 1, "jobs": [None]},
        [],
        None,
    ],
)
def test_malformed_inventory_never_measures(payload):
    reader = Reader()

    def malformed(path):
        if "/jobs?" in path:
            return 200, payload
        return reader(path)

    assert collect(malformed).availability == "error"


def test_ci_mode_requires_explicit_opt_in(tmp_path, capsys):
    from codex.cognitive_brain.improvement_loop_runner import main

    log = tmp_path / "input.jsonl"
    log.write_text("", encoding="utf-8")
    assert (
        main(
            [
                str(log),
                "--collect-ci-run",
                "42",
                "--repo",
                REPO,
                "--ref",
                "refs/heads/fixture",
                "--sha",
                SHA,
                "--repo-root",
                str(tmp_path),
            ]
        )
        == 1
    )
    assert "requires --evidence-bundle" in capsys.readouterr().err


def test_ci_cli_replaces_exports_once_and_retains_unavailable_provenance(
    tmp_path, monkeypatch, capsys
):
    from codex.cognitive_brain import ci_signal_collection as collection
    from codex.cognitive_brain.improvement_loop_runner import main

    calls = []

    def unavailable(**kwargs):
        calls.append(kwargs)
        return collect(lambda path: (403, None))

    monkeypatch.setattr(collection, "collect_ci_run", unavailable)
    record = {
        "repo": REPO,
        "sha": SHA,
        "signal": {"availability": "measured"},
        "brief": {"write_paths": ["src/fixture.py"]},
    }
    log = tmp_path / "input.jsonl"
    log.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n", encoding="utf-8")
    assert (
        main(
            [
                str(log),
                "--evidence-bundle",
                "--collect-ci-run",
                "42",
                "--repo",
                REPO,
                "--ref",
                "refs/heads/fixture",
                "--sha",
                SHA,
                "--repo-root",
                str(tmp_path),
            ]
        )
        == 1
    )
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(calls) == 1 and len(output) == 2
    for assessment in output:
        assert assessment["status"] == "unknown"
        assert assessment["collection"]["availability"] == "unavailable"
        assert "baseline_metric" not in assessment["collection"]["details"]
        assert not assessment["execution_authorized"]
