"""Bounded, supplied-input review SDK; recommendations never confer authority.

All inputs are inert data. No target files are read, tools invoked or writes made.
At import, core.record supplies a validated Draft envelope exemplar. Pure review
calls copy that strict envelope without reopening the installed contract resource.
Persistence belongs to the existing coordinator/storage, not this module.
"""

from __future__ import annotations

import copy
import hashlib
import math
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from .core import Clock, Rejected, canonical, digest, record, utc, validate

SCHEMA = "codex.review.v1"
MAX_FILES = 256
MAX_BYTES = 1024 * 1024
MAX_LANES = 16
MAX_FINDINGS = 128
MAX_EVENTS = 256
RELATIONS = {
    "equivalent",
    "contradicts",
    "depends_on",
    "supersedes",
    "narrows",
    "supports_minority",
}
STATES = ("initial", "meta", "final")
RULES = {
    "symlinks": "reject",
    "submodules": "reject",
    "archives": "opaque-no-expansion",
    "hardlinks": "independent-bytes",
    "permissions": "explicit-posix-mode",
    "line_endings": "raw",
}
_EXEMPLAR = record(
    SCHEMA,
    {"kind": "manifest", "data": {}},
    lambda: datetime(2026, 10, 25, tzinfo=timezone.utc),
)
_KINDS = {"manifest", "plan", "lane-output", "history", "recommendation"}


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def _keys(value: Any, keys: str) -> None:
    _require(isinstance(value, dict) and set(value) == set(keys.split()), "REVIEW_FIELDS")


def _text(value: Any) -> None:
    _require(isinstance(value, str) and bool(value.strip()) and len(value) <= 8192, "REVIEW_TEXT")


def _strings(value: Any, *, nonempty: bool = False) -> None:
    _require(
        isinstance(value, list) and len(value) <= MAX_FINDINGS and (bool(value) or not nonempty),
        "REVIEW_LIST",
    )
    for item in value:
        _text(item)
    _require(len(value) == len(set(value)), "REVIEW_DUPLICATE")


def _hash(value: Any) -> None:
    _require(
        isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None, "REVIEW_HASH"
    )


def _bounded(value: Any) -> None:
    try:
        size = len(canonical(value))
    except (ValueError, TypeError, RecursionError) as exc:
        raise Rejected("REVIEW_JSON") from exc
    _require(size <= MAX_BYTES, "REVIEW_RESOURCE_LIMIT")


def _wrap(kind: str, data: dict[str, Any], clock: Clock) -> dict[str, Any]:
    _bounded(data)
    now = clock()
    _require(
        isinstance(now, datetime) and now.tzinfo is not None and now.utcoffset() is not None,
        "NAIVE_CLOCK",
    )
    result = copy.deepcopy(_EXEMPLAR)
    result["created_at"] = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result["payload"] = {"kind": kind, "data": copy.deepcopy(data)}
    result["id"] = f"{SCHEMA}:{digest(result['payload'])}"
    result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    return result


def _data(value: dict[str, Any], kind: str) -> dict[str, Any]:
    _bounded(value)
    _require(isinstance(value, dict) and isinstance(value.get("schema"), str), "REVIEW_FIELDS")
    # This strict subset of core's Draft envelope permits no authority,
    # extensions or evidence reference injection. The exemplar is core-validated.
    _require(value["schema"] == SCHEMA, "UNSUPPORTED_SCHEMA")
    _require(set(value) == set(_EXEMPLAR), "REVIEW_FIELDS")
    for key in _EXEMPLAR:
        if key not in ("created_at", "payload", "id", "integrity"):
            _require(value[key] == _EXEMPLAR[key], "REVIEW_ENVELOPE")
    try:
        datetime.strptime(value["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError) as exc:
        raise Rejected("REVIEW_TIMESTAMP") from exc
    _keys(value["payload"], "kind data")
    _require(
        isinstance(value["payload"]["kind"], str) and value["payload"]["kind"] in _KINDS,
        "REVIEW_KIND",
    )
    _require(isinstance(value["payload"]["data"], dict), "REVIEW_FIELDS")
    _require(
        value["id"] == f"{SCHEMA}:{digest(value['payload'])}"
        and value["integrity"] == digest({k: v for k, v in value.items() if k != "integrity"}),
        "REVIEW_INTEGRITY",
    )
    _require(value["schema"] == SCHEMA and value["payload"]["kind"] == kind, "REVIEW_KIND")
    return value["payload"]["data"]


def _path(path: Any) -> None:
    _text(path)
    _require(
        not path.startswith("/")
        and "\\" not in path
        and ":" not in path
        and all(part not in ("", ".", "..") for part in path.split("/"))
        and not any(ord(char) < 32 for char in path),
        "REVIEW_PATH",
    )


def candidate_manifest(
    files: list[dict[str, Any]], context: dict[str, Any], *, clock: Clock = utc
) -> dict[str, Any]:
    """Hash explicitly supplied regular-file bytes; never scan or normalize bytes.

    Each input has path, content (bytes), kind='file' and explicit mode (0..0777).
    Hardlinks require separate supplied entries; archives remain opaque bytes.
    """
    _require(isinstance(files, list) and 0 < len(files) <= MAX_FILES, "REVIEW_FILE_LIMIT")
    _require(isinstance(context, dict) and bool(context), "REVIEW_CONTEXT")
    _bounded(context)
    entries = []
    total = 0
    for item in files:
        _keys(item, "path content kind mode")
        _path(item["path"])
        _require(item["kind"] == "file", "REVIEW_UNSUPPORTED_FILE_KIND")
        _require(type(item["mode"]) is int and 0 <= item["mode"] <= 0o777, "REVIEW_MODE")
        _require(isinstance(item["content"], bytes), "REVIEW_BYTES")
        total += len(item["content"])
        _require(total <= MAX_BYTES, "REVIEW_RESOURCE_LIMIT")
        entries.append(
            {
                "path": item["path"],
                "sha256": hashlib.sha256(item["content"]).hexdigest(),
                "size": len(item["content"]),
                "mode": item["mode"],
            }
        )
    paths = [entry["path"] for entry in entries]
    _require(paths == sorted(set(paths)), "REVIEW_PATH_ORDER")
    return _wrap(
        "manifest",
        {
            "entries": entries,
            "context_digest": digest(context),
            "rules": RULES,
            "classification": "Repository-Internal",
        },
        clock,
    )


def _manifest(value: dict[str, Any]) -> dict[str, Any]:
    data = _data(value, "manifest")
    _keys(data, "entries context_digest rules classification")
    _hash(data["context_digest"])
    _require(data["rules"] == RULES, "REVIEW_RULES")
    _require(data["classification"] == "Repository-Internal", "REVIEW_DISCLOSURE")
    entries = data["entries"]
    _require(isinstance(entries, list) and 0 < len(entries) <= MAX_FILES, "REVIEW_FILE_LIMIT")
    total = 0
    for entry in entries:
        _keys(entry, "path sha256 size mode")
        _path(entry["path"])
        _hash(entry["sha256"])
        _require(type(entry["size"]) is int and entry["size"] >= 0, "REVIEW_SIZE")
        _require(type(entry["mode"]) is int and 0 <= entry["mode"] <= 0o777, "REVIEW_MODE")
        total += entry["size"]
    paths = [entry["path"] for entry in entries]
    _require(paths == sorted(set(paths)), "REVIEW_PATH_ORDER")
    _require(total <= MAX_BYTES, "REVIEW_RESOURCE_LIMIT")
    return data


def review_plan(
    manifest: dict[str, Any],
    lanes: list[dict[str, Any]],
    mandatory: list[str],
    critical: list[str],
    *,
    mode: str = "supplement",
    clock: Clock = utc,
) -> dict[str, Any]:
    """Declare bearings, cross-cutting dissent and exact read/search-only lanes.

    Lane fields: id, bearing, actor, run, dissent, required, coverage, tools.
    Attributions are claims, never authenticated independent identities.
    """
    data = _manifest(manifest)
    result = _wrap(
        "plan",
        {
            "manifest": manifest,
            "binding": digest(data),
            "lanes": lanes,
            "mandatory": mandatory,
            "critical": critical,
            "mode": mode,
            "coordinator_role": "implementer",
            "independence": "unverified",
        },
        clock,
    )
    _plan(result)
    return result


def _plan(value: dict[str, Any]) -> dict[str, Any]:
    data = _data(value, "plan")
    _keys(data, "manifest binding lanes mandatory critical mode coordinator_role independence")
    manifest = _manifest(data["manifest"])
    _require(data["binding"] == digest(manifest), "REVIEW_BINDING")
    _require(data["mode"] in ("replace", "supplement"), "REVIEW_MODE")
    _require(
        data["coordinator_role"] == "implementer" and data["independence"] == "unverified",
        "REVIEW_IDENTITY_CLAIM",
    )
    _strings(data["mandatory"], nonempty=True)
    _strings(data["critical"])
    _require(set(data["critical"]) <= set(data["mandatory"]), "REVIEW_CRITICAL_COVERAGE")
    lanes = data["lanes"]
    _require(isinstance(lanes, list) and 3 <= len(lanes) <= MAX_LANES, "REVIEW_LANE_LIMIT")
    for lane in lanes:
        _keys(lane, "id bearing actor run dissent required coverage tools")
        for key in ("id", "bearing", "actor", "run"):
            _text(lane[key])
        _require(type(lane["dissent"]) is bool and type(lane["required"]) is bool, "REVIEW_BOOL")
        _strings(lane["coverage"], nonempty=True)
        _strings(lane["tools"], nonempty=True)
        _require(set(lane["tools"]) <= {"read", "search"}, "REVIEW_MUTATING_TOOL")
        _require(set(lane["coverage"]) <= set(data["mandatory"]), "REVIEW_UNKNOWN_COVERAGE")
    _require(len({lane["id"] for lane in lanes}) == len(lanes), "REVIEW_DUPLICATE_LANE")
    analytical = [lane for lane in lanes if not lane["dissent"] and lane["required"]]
    _require(len({lane["bearing"] for lane in analytical}) >= 2, "REVIEW_BEARINGS")
    _require(
        any(
            lane["dissent"] and lane["required"] and set(lane["coverage"]) == set(data["mandatory"])
            for lane in lanes
        ),
        "REVIEW_CROSS_CUTTING_DISSENT",
    )
    covered = {area for lane in analytical for area in lane["coverage"]}
    _require(set(data["mandatory"]) <= covered, "REVIEW_MANDATORY_COVERAGE")
    return data


def lane_output(
    plan: dict[str, Any],
    lane_id: str,
    source: str,
    findings: list[dict[str, Any]],
    *,
    clock: Clock = utc,
) -> dict[str, Any]:
    """Bind exact source wording and normalized findings to one declared run.

    Findings: id, source_quote, normalized, kind (observation/inference),
    confidence [0,1], coverage and clearance_conditions. A quote must occur
    verbatim in source; normalization cannot replace the original source.
    """
    data = _plan(plan)
    lanes = {lane["id"]: lane for lane in data["lanes"]}
    _require(lane_id in lanes, "REVIEW_UNDECLARED_LANE")
    lane = lanes[lane_id]
    result = _wrap(
        "lane-output",
        {
            "plan_digest": digest(plan),
            "binding": data["binding"],
            "lane": lane_id,
            "actor": lane["actor"],
            "run": lane["run"],
            "identity": "unverified",
            "source": source,
            "findings": findings,
        },
        clock,
    )
    _output(result, plan)
    return result


def _output(value: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    data = _data(value, "lane-output")
    _keys(data, "plan_digest binding lane actor run identity source findings")
    planned = _plan(plan)
    _require(
        data["plan_digest"] == digest(plan) and data["binding"] == planned["binding"],
        "REVIEW_MIXED_BINDING",
    )
    lanes = {lane["id"]: lane for lane in planned["lanes"]}
    _require(isinstance(data["lane"], str) and data["lane"] in lanes, "REVIEW_UNDECLARED_LANE")
    lane = lanes[data["lane"]]
    _require(
        data["actor"] == lane["actor"]
        and data["run"] == lane["run"]
        and data["identity"] == "unverified",
        "REVIEW_ATTRIBUTION",
    )
    _text(data["source"])
    findings = data["findings"]
    _require(isinstance(findings, list) and len(findings) <= MAX_FINDINGS, "REVIEW_FINDING_LIMIT")
    for finding in findings:
        _keys(finding, "id source_quote normalized kind confidence coverage clearance_conditions")
        for key in ("id", "source_quote", "normalized"):
            _text(finding[key])
        _require(finding["source_quote"] in data["source"], "REVIEW_SOURCE_QUOTE")
        _require(finding["kind"] in ("observation", "inference"), "REVIEW_FINDING_KIND")
        confidence = finding["confidence"]
        _require(
            type(confidence) in (int, float) and 0 <= confidence <= 1 and math.isfinite(confidence),
            "REVIEW_CONFIDENCE",
        )
        _strings(finding["coverage"], nonempty=True)
        _strings(finding["clearance_conditions"], nonempty=True)
        _require(set(finding["coverage"]) <= set(lane["coverage"]), "REVIEW_UNKNOWN_COVERAGE")
    _require(len({f["id"] for f in findings}) == len(findings), "REVIEW_DUPLICATE_FINDING")
    return data


def _blocker(state: str, requirement: str, cause: str, conditions: list[str], scope: str) -> dict:
    return {
        "blocked_from_state": state,
        "pending_requirement": requirement,
        "cause": cause,
        "clearance_conditions": conditions,
        "scope": scope,
    }


def reconcile(
    plan: dict[str, Any],
    outputs: list[dict[str, Any]],
    relations: list[dict[str, str]],
    *,
    stage: str = "initial",
    clock: Clock = utc,
) -> dict[str, Any]:
    """Return non-authorizing recommendations; conflicts and missing lanes persist.

    Relation endpoints use 'lane-id/finding-id'. No finding is silently removed
    by equivalent, supersedes, or minority-support relations.
    """
    planned = _plan(plan)
    _require(stage in STATES, "REVIEW_STAGE")
    _require(isinstance(outputs, list) and len(outputs) <= MAX_LANES, "REVIEW_LANE_LIMIT")
    ingested = [_output(output, plan) for output in outputs]
    _require(len({o["lane"] for o in ingested}) == len(ingested), "REVIEW_DUPLICATE_LANE")
    findings = {}
    for output in ingested:
        for finding in output["findings"]:
            ref = output["lane"] + "/" + finding["id"]
            _require(ref not in findings, "REVIEW_DUPLICATE_FINDING")
            findings[ref] = {
                **copy.deepcopy(finding),
                "actor": output["actor"],
                "run": output["run"],
                "source": output["source"],
                "identity": "unverified",
            }
    _require(isinstance(relations, list) and len(relations) <= MAX_FINDINGS, "REVIEW_RELATIONS")
    seen = set()
    for relation in relations:
        _keys(relation, "type from to")
        _require(
            isinstance(relation["type"], str) and relation["type"] in RELATIONS,
            "REVIEW_RELATION_TYPE",
        )
        _require(
            isinstance(relation["from"], str)
            and isinstance(relation["to"], str)
            and relation["from"] in findings
            and relation["to"] in findings
            and relation["from"] != relation["to"],
            "REVIEW_RELATION_REFERENCE",
        )
        key = (relation["type"], relation["from"], relation["to"])
        _require(key not in seen, "REVIEW_DUPLICATE_RELATION")
        seen.add(key)
    present = {output["lane"] for output in ingested}
    blockers = [
        _blocker(
            stage,
            "lane:" + lane["id"],
            "missing-required-lane",
            ["supply-bound-output"],
            lane["id"],
        )
        for lane in planned["lanes"]
        if lane["required"] and lane["id"] not in present
    ]
    for relation in relations:
        if relation["type"] == "contradicts":
            blockers.append(
                _blocker(
                    stage,
                    "resolve-conflict",
                    "unresolved-conflict",
                    ["finding-bound-evidence", "explicit-dissent-disposition"],
                    relation["from"] + "|" + relation["to"],
                )
            )
    return _wrap(
        "recommendation",
        {
            "plan_digest": digest(plan),
            "binding": planned["binding"],
            "stage": stage,
            "outputs": outputs,
            "findings": findings,
            "relations": relations,
            "blockers": blockers,
            "recommendation": "blocked" if blockers else "review-further",
            "authorization": "none",
            "classification": "Repository-Internal",
            "independence": "unverified",
            "routing": "diagnostic-only; FIXED mutation is never executed",
        },
        clock,
    )


def new_history(plan: dict[str, Any], *, clock: Clock = utc) -> dict[str, Any]:
    """Start an empty, ordered Draft history (not a tamperproof audit log)."""
    _plan(plan)
    return _wrap("history", {"plan": plan, "events": []}, clock)


def _block(value: Any) -> None:
    _keys(value, "blocked_from_state pending_requirement cause clearance_conditions scope")
    for key in ("pending_requirement", "cause", "scope"):
        _text(value[key])
    _require(value["blocked_from_state"] in STATES, "REVIEW_STAGE")
    _strings(value["clearance_conditions"], nonempty=True)


def _fold(data: dict[str, Any]) -> dict[str, Any]:
    _keys(data, "plan events")
    planned = _plan(data["plan"])
    events = data["events"]
    _require(isinstance(events, list) and len(events) <= MAX_EVENTS, "REVIEW_EVENT_LIMIT")
    state: dict[str, Any] = {"stage": "initial", "blocker": None, "pending_requirement": None}
    seen = set()
    for sequence, event in enumerate(events, 1):
        _keys(event, "event_id sequence plan_digest binding action data content_id")
        try:
            identifier = uuid.UUID(event["event_id"])
        except (ValueError, TypeError, AttributeError) as exc:
            raise Rejected("REVIEW_EVENT_UUID") from exc
        _require(
            identifier.version == 4 and str(identifier) == event["event_id"], "REVIEW_EVENT_UUID"
        )
        _require(event["event_id"] not in seen, "REVIEW_DUPLICATE_EVENT")
        seen.add(event["event_id"])
        _require(
            type(event["sequence"]) is int and event["sequence"] == sequence, "REVIEW_EVENT_ORDER"
        )
        _require(
            event["plan_digest"] == digest(data["plan"]) and event["binding"] == planned["binding"],
            "REVIEW_MIXED_BINDING",
        )
        _require(
            event["content_id"] == digest({"action": event["action"], "data": event["data"]}),
            "REVIEW_EVENT_CONTENT",
        )
        action, detail = event["action"], event["data"]
        if action == "advance":
            _keys(detail, "to")
            _require(state["blocker"] is None, "REVIEW_BLOCKED")
            index = STATES.index(state["stage"])
            _require(index < 2 and detail["to"] == STATES[index + 1], "REVIEW_TRANSITION")
            state["stage"] = detail["to"]
            state["pending_requirement"] = None
        elif action == "block":
            _block(detail)
            _require(
                state["blocker"] is None and detail["blocked_from_state"] == state["stage"],
                "REVIEW_TRANSITION",
            )
            state["blocker"] = copy.deepcopy(detail)
            state["pending_requirement"] = detail["pending_requirement"]
        elif action == "resume":
            _keys(detail, "blocker_digest clearances current_manifest")
            _require(
                digest(_manifest(detail["current_manifest"])) == planned["binding"],
                "REVIEW_STALE_BINDING",
            )
            blocker = state["blocker"]
            _require(blocker is not None, "REVIEW_TRANSITION")
            _strings(detail["clearances"], nonempty=True)
            _require(
                detail["blocker_digest"] == digest(blocker)
                and set(detail["clearances"]) == set(blocker["clearance_conditions"]),
                "REVIEW_CLEARANCE",
            )
            state["blocker"] = None
        else:
            raise Rejected("REVIEW_EVENT_ACTION")
    return state


def fold_events(history: dict[str, Any], cache: dict[str, Any] | None = None) -> dict[str, Any]:
    """Recompute state; reject a stale or forged cache, never use it as authority."""
    data = _data(history, "history")
    state = _fold(data)
    result = {"event_digest": digest(data), "state": state}
    if cache is not None:
        _require(cache == result, "REVIEW_CACHE_MISMATCH")
    return copy.deepcopy(result)


def append_event(
    history: dict[str, Any],
    event_id: str,
    action: str,
    detail: dict[str, Any],
    *,
    clock: Clock = utc,
) -> dict[str, Any]:
    """Append by copy using caller-issued globally unique UUIDv4 event identities.

    Duplicate IDs are rejected within this history. Cross-store UUID uniqueness
    is the coordinator's responsibility; content hashes are not event identities.
    """
    data = copy.deepcopy(_data(history, "history"))
    _fold(data)
    planned = _plan(data["plan"])
    data["events"].append(
        {
            "event_id": event_id,
            "sequence": len(data["events"]) + 1,
            "plan_digest": digest(data["plan"]),
            "binding": planned["binding"],
            "action": action,
            "data": copy.deepcopy(detail),
            "content_id": digest({"action": action, "data": detail}),
        }
    )
    _fold(data)
    return _wrap("history", data, clock)


def resume(
    history: dict[str, Any],
    manifest: dict[str, Any],
    event_id: str,
    clearances: list[str],
    *,
    clock: Clock = utc,
) -> dict[str, Any]:
    """Resume the exact pending requirement after explicit current-binding clearance.

    Clearance strings are unverified coordinator assertions, not approval.
    Candidate bytes, modes or context drift require a new review, never a reset.
    """
    data = _data(history, "history")
    planned = _plan(data["plan"])
    _require(digest(_manifest(manifest)) == planned["binding"], "REVIEW_STALE_BINDING")
    blocker = fold_events(history)["state"]["blocker"]
    _require(blocker is not None, "REVIEW_TRANSITION")
    return append_event(
        history,
        event_id,
        "resume",
        {
            "blocker_digest": digest(blocker),
            "clearances": clearances,
            "current_manifest": manifest,
        },
        clock=clock,
    )


def remediation_adequacy(
    plan: dict[str, Any],
    original: dict[str, Any],
    finding_id: str,
    followup: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Check finding-bound evidence coverage, not a caller's 'adequate' boolean.

    Evidence is a claimed observation, not independently verified truth. The
    rotated lane must reproduce the original quote/normalization with its own
    exact attributed source. Contradictions remain a reconciliation concern.
    """
    old = _output(original, plan)
    new = _output(followup, plan)
    _require(old["lane"] != new["lane"] and old["run"] != new["run"], "REVIEW_ROTATION")
    matches = [finding for finding in old["findings"] if finding["id"] == finding_id]
    _require(len(matches) == 1, "REVIEW_FINDING_REFERENCE")
    finding = matches[0]
    _keys(evidence, "original_output finding_id followup_output checks")
    _require(
        evidence["original_output"] == digest(original)
        and evidence["finding_id"] == finding_id
        and evidence["followup_output"] == digest(followup),
        "REVIEW_REMEDIATION_BINDING",
    )
    _require(
        any(
            f["source_quote"] == finding["source_quote"]
            and f["normalized"] == finding["normalized"]
            for f in new["findings"]
        ),
        "REVIEW_FINDING_LOSS",
    )
    checks = evidence["checks"]
    _require(isinstance(checks, list) and len(checks) <= MAX_FINDINGS, "REVIEW_LIST")
    conditions = []
    for check in checks:
        _keys(check, "condition observation source_quote")
        for key in check:
            _text(check[key])
        _require(check["source_quote"] in new["source"], "REVIEW_SOURCE_QUOTE")
        _require(check["observation"] == check["source_quote"], "REVIEW_UNGROUNDED_OBSERVATION")
        conditions.append(check["condition"])
    _require(
        len(conditions) == len(set(conditions))
        and set(conditions) == set(finding["clearance_conditions"]),
        "REVIEW_REMEDIATION_COVERAGE",
    )
    return {
        "status": "evidence-coverage-only",
        "original_actor": old["actor"],
        "followup_actor": new["actor"],
        "identity": "unverified",
        "authorization": "none",
    }


def attach_continuation(
    continuation: dict[str, Any], artifacts: list[dict[str, Any]], *, clock: Clock = utc
) -> dict[str, Any]:
    """Return a compatible Draft successor for the existing persistence coordinator.

    Caller must revalidate repository drift via existing storage before writing.
    No new checkpoint namespace or standalone memory store is introduced.
    """
    validate(continuation)
    _require(continuation["schema"] == "codex.continuation-state.v1", "EXPECTED_CONTINUATION")
    _require(isinstance(artifacts, list) and len(artifacts) <= MAX_EVENTS, "REVIEW_RESOURCE_LIMIT")
    available = continuation["payload"]["records"] + artifacts
    plans = {}
    for artifact in available:
        _require(isinstance(artifact, dict), "REVIEW_FIELDS")
        if artifact.get("schema") == SCHEMA and artifact.get("payload", {}).get("kind") == "plan":
            _plan(artifact)
            plans[digest(artifact)] = artifact
        elif (
            artifact.get("schema") == SCHEMA
            and artifact.get("payload", {}).get("kind") == "history"
        ):
            history_plan = _data(artifact, "history").get("plan")
            if not isinstance(history_plan, dict):
                raise Rejected("REVIEW_FIELDS")
            _plan(history_plan)
            plans[digest(history_plan)] = history_plan
    for artifact in artifacts:
        kind = artifact.get("payload", {}).get("kind")
        if kind == "manifest":
            _manifest(artifact)
        elif kind == "plan":
            _plan(artifact)
        elif kind == "history":
            fold_events(artifact)
        elif kind in ("lane-output", "recommendation"):
            data = _data(artifact, kind)
            plan_digest = data.get("plan_digest")
            _require(isinstance(plan_digest, str) and plan_digest in plans, "REVIEW_MISSING_PLAN")
            bound_plan = plans[plan_digest]
            if kind == "lane-output":
                _output(artifact, bound_plan)
            else:
                _keys(
                    data,
                    "plan_digest binding stage outputs findings relations blockers recommendation "
                    "authorization classification independence routing",
                )
                expected = reconcile(
                    bound_plan, data["outputs"], data["relations"], stage=data["stage"], clock=clock
                )
                _require(data == expected["payload"]["data"], "REVIEW_RECOMMENDATION_MISMATCH")
        else:
            raise Rejected("REVIEW_UNSUPPORTED_ATTACHMENT")
    payload = copy.deepcopy(continuation["payload"])
    payload["sequence"] += 1
    payload["predecessor"] = digest(continuation)
    known = {r["id"] for r in payload["records"]}
    for artifact in artifacts:
        _require(artifact["id"] not in known, "REVIEW_DUPLICATE")
        known.add(artifact["id"])
        payload["records"].append(copy.deepcopy(artifact))
    result = record("codex.continuation-state.v1", payload, clock)
    result["supersedes"] = continuation["id"]
    result["extensions"] = copy.deepcopy(continuation["extensions"])
    result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    validate(result)
    return result
