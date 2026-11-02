"""Recorded PR5746 metadata is a fixture, not a live GitHub verifier."""

import json
from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from codex.cognitive_brain import merged_observation
from codex.cognitive_brain.merged_observation import observe_merged_pr

REPO = "Aries-Serpent/_codex_"
SHA = "f48fb7a36eb31fd1ff518c186e54ec212c0d8366"
RUN = 41367213426
NAME = "Enterprise Compliance & CodeQL"
NOW = datetime(2026, 11, 2, 1, tzinfo=timezone.utc)


def stamp(clock: str) -> str:
    return f"2026-11-02T{clock}Z"


class RecordedReader:
    """Minimal allowlisted projection of supplied recorded live metadata."""

    def __init__(self) -> None:
        self.pr: dict[str, Any] = {
            "number": 5746,
            "merged": True,
            "state": "closed",
            "merge_commit_sha": SHA,
            "merged_at": stamp("00:27:05"),
            "base": {"ref": "0D_base_", "repo": {"full_name": REPO}},
        }
        self.run: dict[str, Any] = {
            "id": RUN,
            "repository": {"full_name": REPO},
            "head_sha": SHA,
            "head_branch": "0D_base_",
            "name": NAME,
            "event": "push",
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
            "created_at": stamp("00:27:08"),
            "updated_at": stamp("00:36:36"),
        }
        self.jobs = [
            {
                "id": identifier,
                "run_id": RUN,
                "run_attempt": 1,
                "head_sha": SHA,
                "status": "completed",
                "conclusion": "success",
                "started_at": stamp(start),
                "completed_at": stamp(end),
            }
            for identifier, start, end in (
                (125029811662, "00:27:10", "00:27:57"),
                (125029811904, "00:27:10", "00:29:08"),
                (125029811957, "00:27:11", "00:28:41"),
                (125029811971, "00:27:11", "00:36:14"),
                (125032278961, "00:36:16", "00:36:36"),
            )
        ]
        self.paths: list[str] = []

    def __call__(self, path: str) -> tuple[int, Any]:
        self.paths.append(path)
        if path == f"/repos/{REPO}/pulls/5746":
            return 200, deepcopy(self.pr)
        if path == f"/repos/{REPO}/actions/runs/{RUN}":
            return 200, deepcopy(self.run)
        prefix = f"/repos/{REPO}/actions/runs/{RUN}/attempts/1/jobs?per_page=100&page="
        assert path.startswith(prefix)
        page = int(path.removeprefix(prefix))
        return 200, {
            "total_count": len(self.jobs),
            "jobs": deepcopy(self.jobs[(page - 1) * 100 : page * 100]),
        }


def observe(reader: Any, **overrides: Any) -> Any:
    context: dict[str, Any] = {
        "repo": REPO,
        "pr_number": 5746,
        "expected_sha": SHA,
        "base_ref": "0D_base_",
        "run_id": RUN,
        "run_attempt": 1,
        "workflow_name": NAME,
        "event": "push",
        "window_start": NOW - timedelta(hours=1),
        "window_end": NOW,
        "observed_at": NOW,
        "max_age": timedelta(hours=1),
        "evidence_origin": "recorded",
    }
    return observe_merged_pr(reader=reader, **{**context, **overrides})


def test_recorded_measurement_is_immutable_json_handoff_not_learning() -> None:
    reader = RecordedReader()
    result = observe(reader)
    assert result.availability == "measured"
    assert result.evidence_origin == "recorded"
    assert result.scope == "compliance-scanners"
    assert result.human_handoff_required is True
    assert result.learning_eligible is False
    assert result.merge_commit_sha == SHA
    assert result.failed_jobs == 0
    assert len(result.jobs) == 5
    assert result.completed_at == stamp("00:36:36")
    assert result.window_start == stamp("00:00:00")
    assert result.window_end == stamp("01:00:00")
    assert result.max_age_seconds == 3600
    assert len(reader.paths) == 5
    assert reader.paths[0] == reader.paths[-1] == f"/repos/{REPO}/pulls/5746"
    detached = result.to_dict()
    json.dumps(detached)
    detached["jobs"][0]["conclusion"] = "failure"
    assert result.jobs[0].conclusion == "success"
    with pytest.raises(FrozenInstanceError):
        result.failed_jobs = 99
    with pytest.raises(FrozenInstanceError):
        result.jobs[0].conclusion = "failure"


@pytest.mark.parametrize(
    "patch",
    [
        {"number": 5747},
        {"merged": False},
        {"merged": 1},
        {"state": "open"},
        {"merge_commit_sha": "b" * 40},
        {"base": {"ref": "main", "repo": {"full_name": REPO}}},
        {"base": {"ref": "0D_base_", "repo": {"full_name": "other/repo"}}},
        {"merged_at": stamp("01:00:01")},
        {"merged_at": stamp("00:27:05")[:-1]},
    ],
)
def test_separate_pr_validation_precedes_run_reads(patch: dict[str, Any]) -> None:
    reader = RecordedReader()
    reader.pr.update(patch)
    result = observe(reader)
    assert result.availability == "unavailable"
    assert result.failed_jobs is None
    assert len(reader.paths) == 1


@pytest.mark.parametrize(
    "patch",
    [
        {"id": RUN + 1},
        {"head_sha": "b" * 40},
        {"repository": {"full_name": "other/repo"}},
        {"run_attempt": 2},
        {"run_attempt": True},
        {"name": "Other workflow"},
        {"event": "pull_request"},
        {"head_branch": "main"},
        {"status": "in_progress"},
        {"conclusion": "cancelled"},
        {"created_at": stamp("00:27:04")},
        {"created_at": stamp("00:40:00")},
        {"updated_at": stamp("01:00:01")},
    ],
)
def test_run_binding_and_time_window_fail_closed(patch: dict[str, Any]) -> None:
    reader = RecordedReader()
    reader.run.update(patch)
    assert observe(reader).availability == "unavailable"


@pytest.mark.parametrize(
    "overrides",
    [
        {"expected_sha": "main"},
        {"pr_number": True},
        {"repo": "owner/.."},
        {"run_attempt": 0},
        {"max_age": timedelta(0)},
        {"max_age": timedelta(days=2)},
        {"window_start": NOW},
        {"window_start": NOW - timedelta(days=2)},
        {"window_end": NOW + timedelta(seconds=1)},
        {"observed_at": NOW.replace(tzinfo=None)},
        {"evidence_origin": "not-a-source"},
    ],
)
def test_invalid_context_never_reads(overrides: dict[str, Any]) -> None:
    reader = RecordedReader()
    assert observe(reader, **overrides).availability == "unavailable"
    assert not reader.paths


def test_stale_merge_and_outside_window_are_unavailable() -> None:
    assert observe(RecordedReader(), max_age=timedelta(minutes=30)).availability == "unavailable"
    assert (
        observe(RecordedReader(), window_start=NOW - timedelta(minutes=30)).availability
        == "unavailable"
    )
    assert (
        observe(RecordedReader(), window_end=NOW - timedelta(minutes=25)).availability
        == "unavailable"
    )


@pytest.mark.parametrize("kind", ["pr", "run", "attempt", "created", "name", "event"])
def test_metadata_reread_detects_context_changes(kind: str) -> None:
    reader = RecordedReader()

    def changing(path: str) -> tuple[int, Any]:
        status, payload = reader(path)
        if path.endswith("/pulls/5746") and len(reader.paths) > 1 and kind == "pr":
            payload["merged_at"] = stamp("00:27:06")
        if path.endswith(f"/runs/{RUN}") and len(reader.paths) > 2:
            changes = {
                "run": ("head_sha", "b" * 40),
                "attempt": ("run_attempt", 2),
                "created": ("created_at", stamp("00:27:09")),
                "name": ("name", "Other workflow"),
                "event": ("event", "workflow_dispatch"),
            }
            if kind in changes:
                key, value = changes[kind]
                payload[key] = value
        return status, payload

    assert observe(changing).availability == "unavailable"


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
@pytest.mark.parametrize("stage", ["pr", "run", "jobs", "reread"])
def test_denied_metadata_is_sanitized(status: int, stage: str) -> None:
    reader = RecordedReader()

    def denied(path: str) -> tuple[int, Any]:
        code, payload = reader(path)
        if (
            (stage == "pr" and "/pulls/" in path)
            or (stage == "run" and path.endswith(f"/runs/{RUN}"))
            or (stage == "jobs" and "/jobs?" in path)
            or (stage == "reread" and len(reader.paths) == 5)
        ):
            return status, {"message": "secret credential actor"}
        return code, payload

    result = observe(denied)
    assert result.availability == "unavailable"
    assert result.failed_jobs is None
    assert result.learning_eligible is False
    assert "secret" not in json.dumps(result.to_dict())


def test_reader_exception_is_sanitized_and_no_ambient_reader(monkeypatch: Any) -> None:
    def broken(path: str) -> Any:
        raise RuntimeError("secret credential actor")

    monkeypatch.setenv("GH_TOKEN", "secret credential actor")
    monkeypatch.setattr("codex.cognitive_brain.ci_signal_collection.public_actions_reader", broken)
    result = observe(broken)
    assert result.availability == "unavailable"
    assert "secret" not in json.dumps(result.to_dict())
    with pytest.raises(TypeError):
        observe_merged_pr()  # type: ignore[call-arg]
    assert observe(RecordedReader()).availability == "measured"


@pytest.mark.parametrize("kind", ["incomplete", "attempt", "duplicate", "pending", "empty"])
def test_collector_job_validation_is_reused(kind: str) -> None:
    reader = RecordedReader()
    if kind == "attempt":
        reader.jobs[0]["run_attempt"] = 2
    elif kind == "duplicate":
        reader.jobs[0]["id"] = reader.jobs[1]["id"]
    elif kind == "pending":
        reader.jobs[0]["status"] = "in_progress"
    elif kind == "empty":
        reader.jobs = []

    def inventory(path: str) -> tuple[int, Any]:
        status, payload = reader(path)
        if kind == "incomplete" and "/jobs?" in path:
            payload["total_count"] += 1
        return status, payload

    assert observe(inventory).availability == "unavailable"


def test_pagination_is_owned_by_collector_and_origin_is_explicit() -> None:
    reader = RecordedReader()
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 102)]
    result = observe(reader, evidence_origin="synthetic")
    assert result.availability == "measured"
    assert result.evidence_origin == "synthetic"
    assert len(result.jobs) == 101
    assert len(reader.paths) == 6
    assert "page=2" in reader.paths[3]
    assert not result.learning_eligible


def test_five_pages_fit_explicit_nine_read_budget() -> None:
    reader = RecordedReader()
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 501)]
    result = observe(reader, evidence_origin="synthetic")
    assert result.availability == "measured"
    assert len(result.jobs) == 500
    assert len(reader.paths) == 9


@pytest.mark.parametrize("run_conclusion", ["success", "failure"])
def test_last_paged_failure_is_counted_or_rejects_success(run_conclusion: str) -> None:
    reader = RecordedReader()
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 102)]
    reader.jobs[-1]["conclusion"] = "failure"
    reader.run["conclusion"] = run_conclusion
    result = observe(reader, evidence_origin="synthetic")
    if run_conclusion == "success":
        assert result.availability == "unavailable"
        assert result.failed_jobs is None
    else:
        assert result.availability == "measured"
        assert result.failed_jobs == 1
        assert len(result.jobs) == 101
        assert result.jobs[-1].conclusion == "failure"
    assert not result.learning_eligible


@pytest.mark.parametrize("stage", ["last_page", "run_reread", "pr_reread"])
def test_incomplete_or_interrupted_reads_never_return_partial_metrics(stage: str) -> None:
    reader = RecordedReader()
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 102)]

    def interrupted(path: str) -> tuple[int, Any]:
        status, payload = reader(path)
        if stage == "last_page" and path.endswith("page=2"):
            payload["jobs"] = []
        if (stage == "run_reread" and len(reader.paths) == 5) or (
            stage == "pr_reread" and len(reader.paths) == 6
        ):
            raise RuntimeError("secret transport detail")
        return status, payload

    result = observe(interrupted)
    assert result.availability == "unavailable"
    assert result.failed_jobs is None
    assert not result.jobs
    assert "secret" not in json.dumps(result.to_dict())


def test_recorded_provenance_never_claims_live_authenticated_verification() -> None:
    record = observe(RecordedReader()).to_dict()
    assert record["evidence_origin"] == "recorded"
    assert "live" not in json.dumps(record)
    assert "authenticated" not in json.dumps(record)
    assert record["human_handoff_required"] is True
    assert record["learning_eligible"] is False


def test_changing_page_count_and_over_budget_inventory_are_unavailable() -> None:
    reader = RecordedReader()
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 102)]

    def changing(path: str) -> tuple[int, Any]:
        status, payload = reader(path)
        if path.endswith("page=2"):
            payload["total_count"] = 100
        return status, payload

    assert observe(changing).availability == "unavailable"
    reader.jobs = [{**reader.jobs[0], "id": n} for n in range(1, 502)]
    assert observe(reader).availability == "unavailable"


def test_job_completion_cannot_predate_workflow_creation() -> None:
    reader = RecordedReader()
    reader.jobs[0].update(
        started_at=stamp("00:27:05"),
        completed_at=stamp("00:27:07"),
    )
    assert observe(reader).availability == "unavailable"


def test_no_learning_api_is_invoked(monkeypatch: Any) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("observation invoked a learning API")

    monkeypatch.setattr(
        "codex.cognitive_brain.improvement_pipeline.ImprovementPipeline.process_signal",
        forbidden,
    )
    monkeypatch.setattr(
        "codex.cognitive_brain.outcome_tracking.OutcomeTracker.process_outcome", forbidden
    )
    assert observe(RecordedReader()).availability == "measured"


def test_collection_budget_checked_after_injected_read(monkeypatch: Any) -> None:
    clock = [0.0]
    monkeypatch.setattr(merged_observation.time, "monotonic", lambda: clock[0])
    reader = RecordedReader()

    def slow(path: str) -> tuple[int, Any]:
        result = reader(path)
        clock[0] += 61
        return result

    assert observe(slow).availability == "unavailable"
    assert len(reader.paths) == 1
