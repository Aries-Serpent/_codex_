"""Read-only evidence skills: supplied observations are not execution authority.

These deterministic handlers assess fixture or caller-supplied evidence. They
do not execute commands, author patches, invoke agents, approve, or publish.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

_SCHEMA_ROOT = Path(__file__).parent / "assurance_schema"


def rubber_duck_review(payload: dict[str, Any]) -> dict[str, Any]:
    """Return questions and risks, never a success verdict."""
    criteria = payload.get("acceptance_criteria", [])
    questions = [
        "What independent evidence would falsify the objective?",
        "Which dependencies must finish before implementation or integration?",
        "Which data/control-flow boundaries could invalidate the assumptions?",
        "Is there a simpler alternative with fewer authority or dependency risks?",
    ]
    for key in ("objective", "acceptance_criteria", "evidence", "dependencies", "falsification"):
        if not payload.get(key):
            questions.append(f"What is the missing {key} evidence?")
    return {
        "objective": payload.get("objective", ""),
        "acceptance_criteria": criteria,
        "questions": questions,
        "assumptions": payload.get("assumptions", []),
        "risks": ["Author reasoning is not independent validation", "Scheduling is not execution"],
        "approval_authority": False,
        "patch_authored": False,
    }


def adversarial_validation(payload: dict[str, Any]) -> dict[str, Any]:
    """Assess complete independent command observations; partial evidence is unknown."""
    required = payload.get("required_checks", [])
    checks = payload.get("checks", [])
    status = "unknown"
    reason = "Missing complete independent negative, boundary and regression evidence"
    observer = payload.get("observer")
    author = payload.get("author")
    if observer and author and observer != author and required and isinstance(checks, list):
        names = [check.get("name") for check in checks if isinstance(check, dict)]
        complete = (
            len(names) == len(checks)
            and len(set(names)) == len(names)
            and set(names) == set(required)
            and all(
                check.get("completed") is True
                and type(check.get("returncode")) is int
                and check.get("command")
                and check.get("evidence_ref")
                and check.get("base_sha") == payload.get("base_sha")
                and re.fullmatch(r"[0-9a-f]{40}", str(check.get("base_sha", "")))
                for check in checks
            )
            and {"negative", "boundary", "regression"} <= {check.get("kind") for check in checks}
        )
        if complete:
            status = "fail" if any(check["returncode"] != 0 for check in checks) else "pass"
            reason = "All required supplied observations accounted for; no commands executed by this skill"
    return {"status": status, "reason": reason, "checks": checks, "approval_authority": False}


def evidence_to_improvement_brief(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize a measured signal into an approval-aware bounded proposal."""
    required = (
        "source",
        "timestamp",
        "observed_at",
        "freshness_seconds",
        "base_sha",
        "problem",
        "module",
        "hypothesis",
        "baseline_metric",
        "expected_metric",
        "confidence",
        "risk",
        "acceptance_criteria",
        "verification_commands",
        "lane_id",
        "write_paths",
        "dependencies",
        "budget_seconds",
        "stop_condition",
        "falsification",
    )
    missing = [key for key in required if key not in payload or payload[key] is None]
    if missing:
        return {"status": "unknown", "missing": missing, "execution_authorized": False}
    try:
        measured = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        observed = datetime.fromisoformat(payload["observed_at"].replace("Z", "+00:00"))
        valid_time = (
            measured.tzinfo is not None
            and observed.tzinfo is not None
            and 0 <= (observed - measured).total_seconds() <= payload["freshness_seconds"]
        )
    except (ValueError, TypeError, AttributeError):
        valid_time = False
    if not valid_time:
        return {
            "status": "unknown",
            "reason": "stale or invalid timestamp evidence",
            "execution_authorized": False,
        }
    if not re.fullmatch(r"[0-9a-f]{40}", payload["base_sha"]):
        raise ValueError("base_sha must be an immutable commit SHA")
    if payload["budget_seconds"] <= 0 or payload["baseline_metric"] == payload["expected_metric"]:
        raise ValueError("proposal needs a positive budget and a measurable change")
    brief = {key: payload[key] for key in required}
    brief["observed_at"] = payload["observed_at"]
    canonical = json.dumps(
        {key: value for key, value in brief.items() if key != "observed_at"},
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "status": (
            "signal-only" if payload.get("category") == "session-productivity" else "proposal"
        ),
        "proposal_id": hashlib.sha256(canonical.encode()).hexdigest(),
        "brief": brief,
        "execution_authorized": False,
        "max_correction_cycles": 3,
        "approvals_required": [
            "Authorized implementation",
            "Independent validation",
            "Human integration approval",
        ],
    }


def lane_contract_and_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a human-mediated lane contract and optional evidence handoff."""
    contract = payload["contract"]
    schema = json.loads((_SCHEMA_ROOT / "lane-contract.json").read_text())
    jsonschema.Draft7Validator(schema).validate(contract)
    if contract["lane_id"] in contract["dependencies"]:
        raise ValueError("lane cannot depend on itself")
    for path in contract["read_paths"] + contract["write_paths"]:
        parsed = PurePosixPath(path)
        if parsed.is_absolute() or ".." in parsed.parts or "\\" in path:
            raise ValueError("contract paths must be bounded repository-relative paths")
    handoff = payload.get("handoff")
    if handoff is not None:
        handoff_schema = json.loads((_SCHEMA_ROOT / "handoff.json").read_text())
        jsonschema.Draft7Validator(handoff_schema).validate(handoff)
        if any(handoff[key] != contract[key] for key in ("run_id", "base_sha", "lane_id")):
            raise ValueError("handoff identity must match the immutable contract")
        for path in handoff["changed_paths"]:
            if (
                PurePosixPath(path).is_absolute()
                or ".." in PurePosixPath(path).parts
                or "\\" in path
            ):
                raise ValueError("handoff paths must be bounded repository-relative paths")
            if not any(
                path == boundary or path.startswith(boundary.rstrip("/") + "/")
                for boundary in contract["write_paths"]
            ):
                raise ValueError("handoff changed a path outside the write boundary")
        if handoff["state"] == "passed" and (
            not handoff["artifact_refs"]
            or adversarial_validation(handoff["validation"])["status"] != "pass"
        ):
            raise ValueError("passed handoff requires complete independent evidence")
    return {
        "status": "contract-valid",
        "contract": contract,
        "handoff": handoff,
        "execution": "human-mediated",
    }


def agent_regression_evaluation(payload: dict[str, Any]) -> dict[str, Any]:
    """Compare deterministic replay observations, including a distinct holdout."""
    cases = payload.get("cases", [])
    if not cases or not any(case.get("holdout") is True for case in cases):
        return {"status": "unknown", "reason": "baseline and holdout replay evidence required"}
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("replay case IDs must be unique")
    metrics = {
        "correct": 0,
        "regressions": 0,
        "false_positives": 0,
        "human_interventions": 0,
        "runtime_seconds": 0.0,
        "cost": 0.0,
    }
    for case in cases:
        if any(
            key not in case
            for key in (
                "expected",
                "baseline",
                "actual",
                "human_interventions",
                "runtime_seconds",
                "cost",
                "evidence_ref",
            )
        ):
            return {"status": "unknown", "reason": "incomplete replay observations"}
        metrics["correct"] += case["actual"] == case["expected"]
        metrics["regressions"] += (
            case["baseline"] == case["expected"] and case["actual"] != case["expected"]
        )
        metrics["false_positives"] += case["expected"] == "fail" and case["actual"] == "pass"
        for key in ("human_interventions", "runtime_seconds", "cost"):
            if case[key] < 0:
                raise ValueError("replay metrics cannot be negative")
            metrics[key] += case[key]
    return {
        "status": "fail" if metrics["correct"] != len(cases) else "pass",
        "metrics": metrics,
        "case_count": len(cases),
        "cases": cases,
        "execution_authorized": False,
    }


def pypi_release_assurance(payload: dict[str, Any]) -> dict[str, Any]:
    """Assess supplied artifact evidence; external publisher state stays unverified."""
    required = [
        "wheel",
        "sdist",
        "metadata",
        "tag",
        "isolated-install",
        "installed-imports",
        "provenance",
        "artifact-checksums",
    ]
    result = adversarial_validation({**payload, "required_checks": required})
    return {
        **result,
        "trusted_publisher": "unverified",
        "publication_authorized": False,
        "production_approval_required": True,
        "recovery": "Published versions are immutable; approve a corrected new version and yank/incident handling",
    }
