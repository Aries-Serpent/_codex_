"""Read-only post-merge measurements for human compliance-scanner handoff.

The explicitly supplied reader must already be authorized for the exact repo and
provide fixed-origin GETs, no redirects, bounded response sizes and hard request
deadlines. This adapter cannot interrupt an injected blocking callable. It checks
a 60-second collection budget before/after reads and permits at most nine GETs:
two PR snapshots plus the existing collector's seven run/job reads.

No evidence here is a learning outcome, execution authority or a live verifier
when its origin is recorded/synthetic. Freshness and observation windows are
caller-selected, positive and capped at 24 hours.
"""

from __future__ import annotations

import re
import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from codex.cognitive_brain.ci_signal_collection import ReadJSON, collect_ci_run

EvidenceOrigin = Literal["live", "recorded", "synthetic"]
_LIMIT = timedelta(hours=24)


def _stamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError
    return result.astimezone(timezone.utc)


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class ObservedJob:
    job_id: int
    run_attempt: int
    conclusion: str
    completed_at: str | None


@dataclass(frozen=True)
class MergedObservation:
    """Immutable measurement, deliberately not a pipeline signal or outcome."""

    availability: Literal["measured", "unavailable"]
    reason: str
    evidence_origin: EvidenceOrigin
    scope: Literal["compliance-scanners"] = "compliance-scanners"
    human_handoff_required: bool = True
    learning_eligible: bool = False
    repo: str | None = None
    pr_number: int | None = None
    merge_commit_sha: str | None = None
    base_ref: str | None = None
    merged_at: str | None = None
    run_id: int | None = None
    run_attempt: int | None = None
    workflow_name: str | None = None
    event: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
    observed_at: str | None = None
    window_start: str | None = None
    window_end: str | None = None
    max_age_seconds: float | None = None
    failed_jobs: int | None = None
    jobs: tuple[ObservedJob, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a detached JSON-compatible record, never mutable shared state."""
        result = asdict(self)
        result["jobs"] = [asdict(job) for job in self.jobs]
        return result


def observe_merged_pr(
    *,
    reader: ReadJSON,
    repo: str,
    pr_number: int,
    expected_sha: str,
    base_ref: str,
    run_id: int,
    run_attempt: int,
    workflow_name: str,
    event: str,
    window_start: datetime,
    window_end: datetime,
    observed_at: datetime,
    max_age: timedelta,
    evidence_origin: EvidenceOrigin,
) -> MergedObservation:
    """Bind a separately verified merged PR to one complete workflow attempt.

    All identities are caller expectations, not values inferred from a run.
    Merge, run creation and completion must be inside the inclusive observation
    window; merge and completion must also be no older than ``max_age``.
    PR and extended workflow identity are rechecked after collecting all jobs.
    Reader failures and malformed/denied metadata return sanitized unavailable
    records without unverified identities, remote text or fabricated metrics.
    """
    origin: EvidenceOrigin = (
        evidence_origin if evidence_origin in ("live", "recorded", "synthetic") else "synthetic"
    )

    def unavailable(reason: str) -> MergedObservation:
        return MergedObservation("unavailable", reason, origin)

    try:
        if (
            not callable(reader)
            or not isinstance(repo, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", repo)
            or repo.split("/")[1] in (".", "..")
            or not isinstance(expected_sha, str)
            or not re.fullmatch(r"[0-9a-f]{40}", expected_sha)
            or any(type(n) is not int or n <= 0 for n in (pr_number, run_id, run_attempt))
            or not isinstance(base_ref, str)
            or not base_ref
            or not isinstance(workflow_name, str)
            or not 0 < len(workflow_name) <= 256
            or not isinstance(event, str)
            or not re.fullmatch(r"[a-z_]{1,64}", event)
            or evidence_origin not in ("live", "recorded", "synthetic")
            or not isinstance(max_age, timedelta)
            or not timedelta(0) < max_age <= _LIMIT
        ):
            return unavailable("invalid observation context")
        start, end, now = map(_utc, (window_start, window_end, observed_at))
        if not timedelta(0) < end - start <= _LIMIT or end > now:
            return unavailable("invalid observation window")
        pr_path = f"/repos/{repo}/pulls/{pr_number}"
        run_path = f"/repos/{repo}/actions/runs/{run_id}"
        deadline = time.monotonic() + 60
        reads = 0

        def read(path: str) -> tuple[int, Any]:
            nonlocal reads
            reads += 1
            if reads > 9 or time.monotonic() > deadline:
                raise ValueError
            status, payload = reader(path)
            if time.monotonic() > deadline:
                raise ValueError
            if status in (401, 403, 404, 429):
                raise PermissionError
            if status != 200:
                raise ValueError
            return status, deepcopy(payload)

        def pr_snapshot() -> datetime:
            _, pr = read(pr_path)
            if (
                not isinstance(pr, dict)
                or type(pr.get("number")) is not int
                or pr["number"] != pr_number
                or pr.get("merged") is not True
                or pr.get("state") != "closed"
                or pr.get("merge_commit_sha") != expected_sha
                or pr["base"]["ref"] != base_ref
                or pr["base"]["repo"]["full_name"] != repo
            ):
                raise ValueError
            merged = _stamp(pr.get("merged_at"))
            if not start <= merged <= end or not timedelta(0) <= now - merged <= max_age:
                raise ValueError
            return merged

        merged = pr_snapshot()
        run_snapshot: tuple[Any, ...] | None = None
        created: datetime | None = None
        completed: datetime | None = None

        def run_reader(path: str) -> tuple[int, Any]:
            nonlocal run_snapshot, created, completed
            status, payload = read(path)
            if path == run_path:
                if (
                    not isinstance(payload, dict)
                    or type(payload.get("run_attempt")) is not int
                    or payload["run_attempt"] != run_attempt
                    or payload.get("name") != workflow_name
                    or payload.get("event") != event
                    or payload.get("head_branch") != base_ref
                ):
                    raise ValueError
                current = tuple(
                    payload.get(key)
                    for key in ("name", "event", "head_branch", "created_at", "updated_at")
                )
                if run_snapshot is not None and current != run_snapshot:
                    raise ValueError
                run_snapshot = current
                created = _stamp(payload.get("created_at"))
                completed = _stamp(payload.get("updated_at"))
                if (
                    not start <= merged <= created <= completed <= end <= now
                    or not timedelta(0) <= now - completed <= max_age
                ):
                    raise ValueError
            return status, payload

        signal = collect_ci_run(
            repo=repo,
            sha=expected_sha,
            run_id=run_id,
            reader=run_reader,
            observed_at=now,
        )
        if signal.availability != "measured":
            return unavailable("workflow measurement unavailable")
        if pr_snapshot() != merged:
            return unavailable("merge context changed during observation")
        if created is None or completed is None:
            return unavailable("workflow measurement unavailable")
        jobs = tuple(ObservedJob(**job) for job in signal.details["jobs"])
        if any(
            job.completed_at is not None and not created <= _stamp(job.completed_at) <= completed
            for job in jobs
        ):
            return unavailable("job completion outside workflow window")
        return MergedObservation(
            availability="measured",
            reason="complete workflow attempt measured; human review required",
            evidence_origin=origin,
            repo=repo,
            pr_number=pr_number,
            merge_commit_sha=expected_sha,
            base_ref=base_ref,
            merged_at=_iso(merged),
            run_id=run_id,
            run_attempt=run_attempt,
            workflow_name=workflow_name,
            event=event,
            created_at=_iso(created),
            completed_at=_iso(completed),
            observed_at=_iso(now),
            window_start=_iso(start),
            window_end=_iso(end),
            max_age_seconds=max_age.total_seconds(),
            failed_jobs=signal.details["baseline_metric"],
            jobs=jobs,
        )
    except PermissionError:
        return unavailable("metadata access unavailable")
    except Exception:
        return unavailable("merged observation unavailable")
