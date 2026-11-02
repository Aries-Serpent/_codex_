"""Bounded read-only GitHub Actions measurements, never execution authority.

The default transport reads public REST metadata only. Callers may inject an
authorized reader for private repositories; credential resolution and scope
verification belong to that caller. Logs, names, actor details and arbitrary
remote text are deliberately not copied into signal evidence.
"""

from __future__ import annotations

import json
import multiprocessing
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from codex.cognitive_brain.improvement_pipeline import (
    DataAvailability,
    SignalEvidence,
    SignalSource,
)

ReadJSON = Callable[[str], tuple[int, Any]]
_PATH = re.compile(
    r"/repos/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+/actions/runs/[1-9][0-9]*"
    r"(?:/attempts/[1-9][0-9]*/jobs\?per_page=100&page=[1-5])?"
)


def _read_public_metadata(path: str, output: str) -> None:
    """Read metadata in a disposable worker; never serialize exception text."""

    def write(status: int, body: bytes = b"") -> None:
        Path(output).write_bytes(str(status).encode("ascii") + b"\n" + body)

    try:
        import requests

        with requests.Session() as session:
            session.trust_env = False
            with session.get(
                "https://api.github.com" + path,
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "User-Agent": "codex-evidence-collector",
                },
                timeout=(10, 10),
                allow_redirects=False,
                stream=True,
            ) as response:
                if response.status_code != 200:
                    write(response.status_code)
                    return
                chunks = []
                size = 0
                for chunk in response.iter_content(chunk_size=65536):
                    size += len(chunk)
                    if size > 1048576:
                        write(0)
                        return
                    chunks.append(chunk)
                write(200, b"".join(chunks))
    except Exception:
        write(0)


def public_actions_reader(path: str, *, timeout: float = 20) -> tuple[int, Any]:
    """Read fixed-origin metadata with no redirects, auth, proxies or retries.

    A disposable process bounds DNS, TLS, headers and slow-stream body reads.
    Existing optional requests is imported in that worker only when needed.
    """
    if not isinstance(path, str) or not _PATH.fullmatch(path):
        raise ValueError("only bounded GitHub Actions metadata paths are permitted")
    if not 0 < timeout <= 20:
        raise ValueError("reader timeout must be positive and at most twenty seconds")
    deadline = time.monotonic() + timeout
    context = multiprocessing.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="codex-ci-metadata-") as directory:
        output = Path(directory) / "response"
        worker = context.Process(
            target=_read_public_metadata, args=(path, str(output)), daemon=True
        )
        try:
            worker.start()
            worker.join(timeout=max(0, deadline - time.monotonic()))
            if worker.is_alive():
                raise TimeoutError("GitHub metadata read exceeded deadline")
            # Read only after worker exit; no blocking IPC can escape supervision.
            with output.open("rb") as handle:
                response = handle.read(1048587)
            if len(response) > 1048586:
                raise ValueError("GitHub metadata response exceeds size limit")
            status_bytes, body = response.split(b"\n", 1)
            status = int(status_bytes)
            if status == 0:
                raise ValueError("GitHub metadata read failed or exceeded response limit")
            return status, json.loads(body) if status == 200 else None
        finally:
            if worker.pid is not None:
                if worker.is_alive():
                    worker.terminate()
                worker.join(timeout=1)
                if worker.is_alive():
                    worker.kill()
                    worker.join(timeout=1)
                worker.close()


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("missing timestamp")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return stamp.astimezone(timezone.utc)


def collect_ci_run(
    *,
    repo: str,
    sha: str,
    run_id: int,
    reader: ReadJSON = public_actions_reader,
    observed_at: datetime | None = None,
) -> SignalEvidence:
    """Collect one completed run attempt, accounting for every job or denying.

    At most five pages / 500 jobs and seven GETs are permitted. HTTP denied,
    gated, pending, cancelled or empty runs are unavailable, never zero-failure
    measurements. Malformed, truncated or context-changing reads are errors.
    """
    if (
        not isinstance(repo, str)
        or not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", repo)
        or repo.split("/")[1] in (".", "..")
    ):
        raise ValueError("repo must be an owner/repository slug")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("sha must be an immutable commit SHA")
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("run_id must be a positive integer")
    now = observed_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("observation time must be timezone-aware")
    path = f"/repos/{repo}/actions/runs/{run_id}"
    deadline = time.monotonic() + 60
    details: dict[str, Any] = {
        "repo": repo,
        "sha": sha,
        "workflow_run_id": run_id,
        "observed_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evidence_ref": f"https://github.com/{repo}/actions/runs/{run_id}",
    }

    def unavailable(reason: str, *, error: bool = False) -> SignalEvidence:
        return SignalEvidence(
            source=SignalSource.CI_WORKFLOW,
            kind="metric_sample",
            measured_at=details["observed_at"],
            availability=DataAvailability.ERROR if error else DataAvailability.UNAVAILABLE,
            summary=reason,
            details=dict(details),
        )

    def read(target: str) -> Any:
        if time.monotonic() > deadline:
            raise ValueError("collection deadline exceeded")
        status, payload = (
            public_actions_reader(target, timeout=min(20, deadline - time.monotonic()))
            if reader is public_actions_reader
            else reader(target)
        )
        if time.monotonic() > deadline:
            raise ValueError("collection deadline exceeded")
        if status in (401, 403, 404, 429):
            raise PermissionError
        if status != 200:
            raise ValueError("metadata read failed")
        return payload

    try:
        run = read(path)
        if (
            not isinstance(run, dict)
            or type(run.get("id")) is not int
            or run.get("id") != run_id
            or run.get("head_sha") != sha
            or run.get("repository", {}).get("full_name") != repo
            or type(run.get("run_attempt")) is not int
            or run["run_attempt"] <= 0
        ):
            return unavailable("run identity does not match caller context", error=True)
        if run.get("status") != "completed" or run.get("conclusion") not in (
            "success",
            "failure",
            "timed_out",
        ):
            return unavailable("run is pending, gated or lacks a measurable terminal outcome")
        updated = _timestamp(run.get("updated_at"))
        if updated > now:
            return unavailable("run timestamp is in the future", error=True)
        attempt = run["run_attempt"]
        details["run_attempt"] = attempt
        jobs = []
        total = None
        for page in range(1, 6):
            payload = read(f"{path}/attempts/{attempt}/jobs?per_page=100&page={page}")
            if (
                isinstance(payload, dict)
                and payload.get("total_count") == 0
                and payload.get("jobs") == []
            ):
                return unavailable("run has no job evidence")
            if (
                not isinstance(payload, dict)
                or type(payload.get("total_count")) is not int
                or not 0 < payload["total_count"] <= 500
                or not isinstance(payload.get("jobs"), list)
                or len(payload["jobs"]) > 100
            ):
                return unavailable("malformed or over-budget job inventory", error=True)
            if total is None:
                total = payload["total_count"]
            if payload["total_count"] != total or not payload["jobs"]:
                return unavailable("job pagination changed or is incomplete", error=True)
            jobs.extend(payload["jobs"])
            if len(jobs) >= total:
                break
        if len(jobs) != total:
            return unavailable("job pagination is incomplete", error=True)
        ids: set[int] = set()
        observations = []
        for job in jobs:
            if (
                not isinstance(job, dict)
                or type(job.get("id")) is not int
                or job["id"] <= 0
                or job["id"] in ids
                or job.get("run_id") != run_id
                or job.get("head_sha") != sha
                or type(job.get("run_attempt")) is not int
                or job["run_attempt"] != attempt
            ):
                return unavailable("job identity is ambiguous or foreign", error=True)
            ids.add(job["id"])
            if job.get("status") != "completed" or job.get("conclusion") not in (
                "success",
                "failure",
                "timed_out",
                "skipped",
                "neutral",
            ):
                return unavailable("job outcome is not a complete measurement")
            finished = None
            if job["conclusion"] not in ("skipped", "neutral"):
                finished = _timestamp(job.get("completed_at"))
                started = _timestamp(job.get("started_at"))
                if not started <= finished <= updated:
                    return unavailable("job timestamp context is invalid", error=True)
            observations.append(
                {
                    "job_id": job["id"],
                    "run_attempt": attempt,
                    "conclusion": job["conclusion"],
                    "completed_at": finished.strftime("%Y-%m-%dT%H:%M:%SZ") if finished else None,
                }
            )
        final = read(path)
        if any(
            final.get(key) != run.get(key)
            for key in (
                "id",
                "head_sha",
                "run_attempt",
                "status",
                "conclusion",
                "updated_at",
                "repository",
            )
        ):
            return unavailable("run changed during collection", error=True)
        measured_jobs = [
            job for job in observations if job["conclusion"] not in ("skipped", "neutral")
        ]
        if not measured_jobs:
            return unavailable("run has no executed measurable jobs")
        failures = sum(job["conclusion"] in ("failure", "timed_out") for job in measured_jobs)
        if (run["conclusion"] == "success" and failures) or (
            run["conclusion"] != "success" and not failures
        ):
            return unavailable("run and job conclusions disagree", error=True)
        details.update(
            {
                "baseline_metric": failures,
                "metric_name": "failed_jobs_in_run_attempt",
                "job_count": len(jobs),
                "measured_job_count": len(measured_jobs),
                "jobs": sorted(observations, key=lambda job: job["job_id"]),
            }
        )
        return SignalEvidence(
            source=SignalSource.CI_WORKFLOW,
            kind="ci_job_failure" if failures else "metric_sample",
            measured_at=max(job["completed_at"] for job in measured_jobs),
            availability=DataAvailability.MEASURED,
            summary=f"GitHub Actions run attempt measured {failures} failed jobs",
            details=details,
        )
    except PermissionError:
        return unavailable("GitHub metadata access unavailable")
    except Exception:
        # Reader exceptions and remote error text may contain credentials/PII.
        return unavailable("GitHub metadata collection failed", error=True)
