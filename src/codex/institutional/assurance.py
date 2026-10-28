"""Inert, fixture-only assurance DAGs over explicitly supplied review records.

Procedures are declarations, never executable commands. Actor, provenance and
eligibility claims remain unverified. No result grants approval or activation.
Persistence uses the existing continuation coordinator, not a second store.
"""

from __future__ import annotations

import copy
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from . import core, review
from .core import Clock, Rejected, canonical, digest, record, utc, validate

SCHEMA = "codex.assurance.v1"
MAX_BYTES = 1024 * 1024
MAX_NODES = 32
MAX_EVENTS = 128
MAX_ITEMS = 128
STATUSES = ("ACTIVE", "SUPERSEDED", "REVOKED", "DISPUTED", "STALE", "UNAVAILABLE")
KINDS = ("technical_verification", "independent_reproduction", "institutional_audit")
_LIMITS = {
    "fixture_only": True,
    "identity_assurance": "unverified",
    "authority": "none",
    "approval": False,
    "activation": False,
    "full_convergence_model": "unsupported",
}
_EXEMPLAR = record(
    SCHEMA, {"kind": "plan", "data": {}}, lambda: datetime(2026, 10, 25, tzinfo=timezone.utc)
)


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected("ASSURANCE_" + reason)


def _keys(value: Any, keys: str) -> None:
    _require(isinstance(value, dict) and set(value) == set(keys.split()), "FIELDS")


def _text(value: Any) -> None:
    _require(isinstance(value, str) and 0 < len(value.strip()) <= 8192, "TEXT")


def _choice(value: Any, choices: tuple | list) -> None:
    _require(isinstance(value, str) and value in choices, "CHOICE")


def _hash(value: Any) -> None:
    _require(isinstance(value, str) and re.fullmatch("[a-f0-9]{64}", value) is not None, "HASH")


def _integer(value: Any, maximum: int) -> None:
    _require(type(value) is int and 0 <= value <= maximum, "RESOURCE_LIMIT")


def _list(value: Any, maximum: int = MAX_ITEMS) -> None:
    _require(isinstance(value, list) and len(value) <= maximum, "RESOURCE_LIMIT")


def _strings(value: Any, *, nonempty: bool = False) -> None:
    _list(value)
    _require(not nonempty or bool(value), "EMPTY")
    for item in value:
        _text(item)
    _require(len(value) == len(set(value)), "DUPLICATE")


def _bounded(value: Any, *, maximum: int = MAX_BYTES) -> None:
    # Bound integers and nesting before JSON encoding (including huge-int conversion).
    remaining = maximum

    def visit(item: Any, depth: int) -> None:
        nonlocal remaining
        remaining -= 1
        _require(remaining >= 0 and depth <= 48, "RESOURCE_LIMIT")
        if item is None or type(item) is bool:
            return
        if type(item) is int:
            _require(item.bit_length() <= 63, "RESOURCE_LIMIT")
        elif type(item) is float:
            _require(item == item and abs(item) <= 1e100, "JSON")
        elif isinstance(item, str):
            remaining -= len(item)
            _require(remaining >= 0, "RESOURCE_LIMIT")
        elif isinstance(item, (dict, list)):
            _require(len(item) <= maximum, "RESOURCE_LIMIT")
            if isinstance(item, dict):
                for key, child in item.items():
                    _require(isinstance(key, str), "JSON")
                    visit(key, depth + 1)
                    visit(child, depth + 1)
            else:
                for child in item:
                    visit(child, depth + 1)
        else:
            raise Rejected("ASSURANCE_JSON")

    visit(value, 0)
    try:
        size = len(canonical(value))
    except (ValueError, TypeError, RecursionError) as exc:
        raise Rejected("ASSURANCE_JSON") from exc
    _require(size <= maximum, "RESOURCE_LIMIT")


def _wrap(kind: str, data: dict, clock: Clock) -> dict:
    _bounded(data)
    now = clock()
    _require(
        isinstance(now, datetime) and now.tzinfo is not None and now.utcoffset() is not None,
        "CLOCK",
    )
    result = copy.deepcopy(_EXEMPLAR)
    result["created_at"] = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result["payload"] = {"kind": kind, "data": copy.deepcopy(data)}
    result["id"] = f"{SCHEMA}:{digest(result['payload'])}"
    result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    _bounded(result)
    return result


def _data(value: Any, kind: str) -> dict:
    _bounded(value)
    _keys(value, " ".join(_EXEMPLAR))
    for key in _EXEMPLAR:
        if key not in ("created_at", "payload", "id", "integrity"):
            _require(value[key] == _EXEMPLAR[key], "ENVELOPE")
    try:
        _require(isinstance(value["created_at"], str), "TIMESTAMP")
        datetime.strptime(value["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError) as exc:
        raise Rejected("ASSURANCE_TIMESTAMP") from exc
    _keys(value["payload"], "kind data")
    _require(value["payload"]["kind"] == kind, "KIND")
    _require(isinstance(value["payload"]["data"], dict), "FIELDS")
    _require(
        value["id"] == f"{SCHEMA}:{digest(value['payload'])}"
        and value["integrity"] == digest({k: v for k, v in value.items() if k != "integrity"}),
        "INTEGRITY",
    )
    return value["payload"]["data"]


def _limits(data: dict) -> None:
    _require(data["limits"] == _LIMITS, "AUTHORITY")
    for key in ("fixture_only", "approval", "activation"):
        _require(type(data["limits"][key]) is bool, "AUTHORITY")


def _baseline(data: dict) -> dict:
    return review.reconcile(
        data["review_plan"], data["original_outputs"], data["relations"], stage="final"
    )["payload"]["data"]


def _topological(nodes: list[dict]) -> list[str]:
    ordered: list[str] = []
    remaining = {node["id"]: node for node in nodes}
    while remaining:
        ready = [key for key, node in remaining.items() if set(node["depends_on"]) <= set(ordered)]
        _require(bool(ready), "DAG_CYCLE")
        for key in ready:
            ordered.append(key)
            del remaining[key]
    return ordered


def _plan(value: Any) -> dict:
    data = _data(value, "plan")
    _keys(data, "review_plan original_outputs relations binding procedures nodes limits")
    _limits(data)
    baseline = _baseline(data)
    _require(data["binding"] == baseline["binding"], "BINDING")
    procedures = data["procedures"]
    _list(procedures, MAX_NODES)
    registry = {}
    for procedure in procedures:
        _keys(procedure, "id version kind expected_outputs")
        _text(procedure["id"])
        _text(procedure["version"])
        _choice(procedure["kind"], KINDS)
        _strings(procedure["expected_outputs"], nonempty=True)
        procedure_key = (procedure["id"], procedure["version"])
        _require(procedure_key not in registry, "DUPLICATE_PROCEDURE")
        registry[procedure_key] = procedure
    nodes = data["nodes"]
    _list(nodes, MAX_NODES)
    ids = []
    for node in nodes:
        _keys(
            node,
            "id kind depends_on requirement rationale role actor identity_assurance independence "
            "procedure environment_digest expected_outputs resource_caps finding_requirements "
            "evidence_requirements pending recovery",
        )
        for key in ("id", "rationale", "role", "actor", "pending", "recovery"):
            _text(node[key])
        ids.append(node["id"])
        _choice(node["kind"], KINDS)
        _require(node["role"] == node["kind"], "ROLE")
        _strings(node["depends_on"])
        _choice(node["requirement"], ("required", "not_required_with_rationale", "blocked"))
        _require(node["identity_assurance"] == "unverified", "IDENTITY")
        _choice(node["independence"], ("fixture-only", "trusted-required"))
        _keys(node["procedure"], "id version")
        _text(node["procedure"]["id"])
        _text(node["procedure"]["version"])
        procedure = registry.get((node["procedure"]["id"], node["procedure"]["version"]))
        if procedure is None:
            raise Rejected("ASSURANCE_PROCEDURE")
        _require(procedure["kind"] == node["kind"], "PROCEDURE")
        _strings(node["expected_outputs"], nonempty=True)
        _require(node["expected_outputs"] == procedure["expected_outputs"], "OUTPUTS")
        _hash(node["environment_digest"])
        _keys(node["resource_caps"], "max_bytes max_attempts")
        _integer(node["resource_caps"]["max_bytes"], MAX_BYTES)
        _integer(node["resource_caps"]["max_attempts"], MAX_EVENTS)
        _require(all(v > 0 for v in node["resource_caps"].values()), "RESOURCE_LIMIT")
        _strings(node["evidence_requirements"], nonempty=True)
        requirements = node["finding_requirements"]
        _list(requirements)
        seen = set()
        for requirement in requirements:
            _keys(requirement, "finding requirement_digest")
            ref = requirement["finding"]
            _text(ref)
            _require(ref in baseline["findings"] and ref not in seen, "FINDING")
            _require(
                requirement["requirement_digest"] == digest(baseline["findings"][ref]), "FINDING"
            )
            seen.add(ref)
    _require(len(ids) == len(set(ids)), "DUPLICATE_NODE")
    for node in nodes:
        _require(set(node["depends_on"]) <= set(ids), "MISSING_DEPENDENCY")
    _topological(nodes)
    return data


def assurance_plan(
    review_plan: dict,
    original_outputs: list[dict],
    relations: list[dict],
    procedures: list[dict],
    nodes: list[dict],
    *,
    clock: Clock = utc,
) -> dict:
    """Validate a supplied DAG and inert versioned procedure registry.

    Review outputs and relations are immutable original inputs, not a caller's
    cached recommendation. Finding requirement digests cover the full original
    reconciled finding, including source attribution and clearance conditions.
    """
    supplied = {
        "review_plan": review_plan,
        "original_outputs": original_outputs,
        "relations": relations,
        "procedures": procedures,
        "nodes": nodes,
    }
    _bounded(supplied)
    baseline = _baseline(supplied)
    result = _wrap("plan", {**supplied, "binding": baseline["binding"], "limits": _LIMITS}, clock)
    _plan(result)
    return result


def _current(data: dict, manifest: Any) -> bool:
    # Reuse the public review-plan validator for supplied manifest semantics.
    planned = data["review_plan"]["payload"]["data"]
    _bounded(manifest)
    current = review.review_plan(
        manifest, planned["lanes"], planned["mandatory"], planned["critical"], mode=planned["mode"]
    )
    return current["payload"]["data"]["binding"] == data["binding"]


def new_history(plan: dict, *, clock: Clock = utc) -> dict:
    """Create an empty append-only-by-copy Draft history."""
    _plan(plan)
    return _wrap("history", {"plan": plan, "events": []}, clock)


def _evidence(value: Any, node: dict) -> None:
    _keys(
        value,
        "id source provenance authority status applicability eligibility critical "
        "requirements finding_requirements",
    )
    _text(value["id"])
    _text(value["source"])
    _require(value["provenance"] == "unverified" and value["authority"] == "none", "PROVENANCE")
    _choice(value["status"], STATUSES)
    _choice(value["applicability"], ("applicable", "not_applicable", "unknown"))
    _choice(value["eligibility"], ("eligible", "ineligible", "unknown"))
    _require(type(value["critical"]) is bool, "BOOL")
    _strings(value["requirements"], nonempty=True)
    _require(
        set(value["requirements"]) <= set(node["evidence_requirements"]), "EVIDENCE_REQUIREMENT"
    )
    _list(value["finding_requirements"])
    _require(value["finding_requirements"] == node["finding_requirements"], "FINDING_BINDING")


def _result(value: Any, plan: dict, node: dict) -> None:
    _keys(
        value,
        "node_id plan_digest binding procedure environment_digest actor identity_assurance "
        "outcome outputs evidence bytes_used prerequisites",
    )
    data = plan["payload"]["data"]
    _require(
        value["node_id"] == node["id"]
        and value["plan_digest"] == digest(plan)
        and value["binding"] == data["binding"],
        "RESULT_BINDING",
    )
    _require(value["procedure"] == node["procedure"], "PROCEDURE")
    _require(value["environment_digest"] == node["environment_digest"], "ENVIRONMENT")
    _require(
        value["actor"] == node["actor"] and value["identity_assurance"] == "unverified",
        "ACTOR_SUBSTITUTION",
    )
    _choice(value["outcome"], ("PASS", "FAIL", "INCONCLUSIVE", "BLOCKED"))
    _strings(value["outputs"])
    _require(set(value["outputs"]) <= set(node["expected_outputs"]), "OUTPUTS")
    _integer(value["bytes_used"], node["resource_caps"]["max_bytes"])
    _require(len(canonical(value)) <= node["resource_caps"]["max_bytes"], "RESOURCE_LIMIT")
    _list(value["evidence"])
    ids = []
    for evidence in value["evidence"]:
        _evidence(evidence, node)
        ids.append(evidence["id"])
    _require(len(ids) == len(set(ids)), "DUPLICATE_EVIDENCE")
    _require(isinstance(value["prerequisites"], dict), "FIELDS")
    for key, item in value["prerequisites"].items():
        _text(key)
        _hash(item)


def _evaluate(data: dict, results: dict, states: dict) -> dict:
    planned = data["plan"]["payload"]["data"]
    nodes = {node["id"]: node for node in planned["nodes"]}
    evaluated: dict[str, Any] = {}
    for key in _topological(planned["nodes"]):
        node = nodes[key]
        blockers = []
        prerequisites = {}
        for dependency in node["depends_on"]:
            dep = evaluated[dependency]
            if dep["state"] not in ("PASSED", "NOT_REQUIRED"):
                blockers.append("prerequisite:" + dependency)
            else:
                prerequisites[dependency] = dep["proof_digest"]
        if node["requirement"] == "not_required_with_rationale":
            evaluated[key] = {
                "state": "BLOCKED" if blockers else "NOT_REQUIRED",
                "ready": False,
                "blockers": blockers,
                "prerequisites": prerequisites,
                "proof_digest": (
                    None if blockers else digest({"node": node, "prerequisites": prerequisites})
                ),
            }
            continue
        if node["requirement"] == "blocked":
            blockers.append("declared-blocked")
        if node["independence"] == "trusted-required":
            blockers.append("trusted-independence-unavailable")
        ready = not blockers
        result = results.get(key)
        state = "READY" if ready else "BLOCKED"
        proof = None
        if result is not None:
            result_hash = digest(result)
            if result["prerequisites"] != prerequisites:
                blockers.append("stale-prerequisite-binding")
            if result["outcome"] != "PASS":
                blockers.append("outcome:" + result["outcome"])
            if set(result["outputs"]) != set(node["expected_outputs"]):
                blockers.append("missing-expected-output")
            requirements: set[str] = set()
            if not result["evidence"]:
                blockers.append("missing-evidence")
            for evidence in result["evidence"]:
                status = states[result_hash][evidence["id"]]
                if status["status"] != "ACTIVE":
                    blockers.append("evidence:" + evidence["id"] + ":" + status["status"])
                if status["applicability"] != "applicable":
                    blockers.append("applicability:" + evidence["id"])
                if status["eligibility"] != "eligible":
                    prefix = "critical-eligibility:" if evidence["critical"] else "eligibility:"
                    blockers.append(prefix + evidence["id"])
                requirements.update(evidence["requirements"])
            if requirements != set(node["evidence_requirements"]):
                blockers.append("missing-evidence-requirement")
            state = "PASSED" if not blockers else "BLOCKED"
            proof = digest({"result": result_hash, "evidence": states[result_hash]})
        evaluated[key] = {
            "state": state,
            "ready": ready,
            "blockers": blockers,
            "prerequisites": prerequisites,
            "proof_digest": proof,
        }
    pending = next(
        (
            key
            for key in _topological(planned["nodes"])
            if evaluated[key]["state"] not in ("PASSED", "NOT_REQUIRED")
        ),
        None,
    )
    return {"nodes": evaluated, "pending_node": pending}


def _fold(history: Any) -> tuple[dict, dict, dict, dict]:
    data = _data(history, "history")
    _keys(data, "plan events")
    planned = _plan(data["plan"])
    _list(data["events"], MAX_EVENTS)
    nodes = {node["id"]: node for node in planned["nodes"]}
    results: dict[str, Any] = {}
    states: dict[str, Any] = {}
    archived: dict[str, Any] = {}
    ids = set()
    predecessor = None
    attempts: dict[str, int] = {}
    for sequence, event in enumerate(data["events"], 1):
        _keys(event, "id sequence predecessor action detail digest")
        _text(event["id"])
        try:
            identifier = uuid.UUID(event["id"])
        except (ValueError, TypeError, AttributeError) as exc:
            raise Rejected("ASSURANCE_EVENT_ID") from exc
        _require(str(identifier) == event["id"] and identifier.version == 4, "EVENT_ID")
        _require(event["id"] not in ids, "DUPLICATE_EVENT")
        ids.add(event["id"])
        _require(type(event["sequence"]) is int and event["sequence"] == sequence, "EVENT_ORDER")
        _require(event["predecessor"] == predecessor, "EVENT_PREDECESSOR")
        _require(
            event["digest"] == digest({k: v for k, v in event.items() if k != "digest"}),
            "EVENT_DIGEST",
        )
        detail = event["detail"]
        if event["action"] == "result":
            _keys(detail, "result previous_result")
            result = detail["result"]
            _require(isinstance(result, dict), "FIELDS")
            key = result.get("node_id")
            _require(isinstance(key, str) and key in nodes, "NODE")
            node = nodes[key]
            _result(result, data["plan"], node)
            current = _evaluate(data, results, states)["nodes"][key]
            _require(current["ready"], "PREREQUISITES")
            _require(result["prerequisites"] == current["prerequisites"], "PREREQUISITE_BINDING")
            old = results.get(key)
            _require(
                detail["previous_result"] == (digest(old) if old is not None else None),
                "RETRY_PREDECESSOR",
            )
            result_hash = digest(result)
            _require(result_hash not in archived, "DUPLICATE_RESULT")
            attempts[key] = attempts.get(key, 0) + 1
            _require(attempts[key] <= node["resource_caps"]["max_attempts"], "RESOURCE_LIMIT")
            results[key] = copy.deepcopy(result)
            archived[result_hash] = copy.deepcopy(result)
            states[result_hash] = {
                evidence["id"]: {
                    "status": evidence["status"],
                    "applicability": evidence["applicability"],
                    "eligibility": evidence["eligibility"],
                    "reason": "initial supplied assertion",
                    "revision": event["digest"],
                }
                for evidence in result["evidence"]
            }
        elif event["action"] == "evidence-status":
            _keys(detail, "result_digest evidence_id previous_status status")
            _hash(detail["result_digest"])
            _text(detail["evidence_id"])
            result_hash, evidence_id = detail["result_digest"], detail["evidence_id"]
            _require(
                result_hash in states and evidence_id in states[result_hash], "EVIDENCE_REFERENCE"
            )
            _require(
                detail["previous_status"] == digest(states[result_hash][evidence_id]),
                "STATUS_PREDECESSOR",
            )
            status = detail["status"]
            _keys(status, "status applicability eligibility reason")
            _choice(status["status"], STATUSES)
            _choice(status["applicability"], ("applicable", "not_applicable", "unknown"))
            _choice(status["eligibility"], ("eligible", "ineligible", "unknown"))
            _text(status["reason"])
            previous = states[result_hash][evidence_id]
            _require(
                status != {key: value for key, value in previous.items() if key != "revision"},
                "DUPLICATE_STATUS",
            )
            states[result_hash][evidence_id] = {
                **copy.deepcopy(status),
                "revision": event["digest"],
            }
        else:
            raise Rejected("ASSURANCE_EVENT_ACTION")
        predecessor = event["digest"]
    return data, results, states, archived


def fold_events(history: dict, cache: dict | None = None) -> dict:
    """Replay every event; caches are comparisons, never trusted inputs.

    Hash chains detect accidental corruption, not hostile resealing. Prior
    result assertions remain in events; retries never erase their predecessors.
    """
    data, results, states, archived = _fold(history)
    result = {
        "history_digest": digest(history),
        **_evaluate(data, results, states),
        "latest_results": {key: digest(value) for key, value in results.items()},
        "evidence_states": states,
        "result_statuses": {
            key: "ACTIVE" if key in {digest(r) for r in results.values()} else "SUPERSEDED"
            for key in archived
        },
    }
    if cache is not None:
        _bounded(cache)
        _require(cache == result, "CACHE_MISMATCH")
    return copy.deepcopy(result)


def readiness(history: dict, current_manifest: dict) -> dict:
    """Recompute exact node readiness; drift reopens every required node."""
    data, _, _, _ = _fold(history)
    state = fold_events(history)
    if not _current(data["plan"]["payload"]["data"], current_manifest):
        for key, node in state["nodes"].items():
            if node["state"] != "NOT_REQUIRED":
                node.update(state="BLOCKED", ready=False, proof_digest=None)
                node["blockers"].append("candidate-context-drift")
                if state["pending_node"] is None:
                    state["pending_node"] = key
        state["current_binding"] = False
    else:
        state["current_binding"] = True
    return state


def _append(history: dict, event_id: str, action: str, detail: dict, clock: Clock) -> dict:
    _bounded(detail)
    data = copy.deepcopy(_data(history, "history"))
    _fold(history)
    event = {
        "id": event_id,
        "sequence": len(data["events"]) + 1,
        "predecessor": data["events"][-1]["digest"] if data["events"] else None,
        "action": action,
        "detail": copy.deepcopy(detail),
    }
    event["digest"] = digest(event)
    data["events"].append(event)
    result = _wrap("history", data, clock)
    _fold(result)
    return result


def ingest_result(
    history: dict,
    current_manifest: dict,
    event_id: str,
    result: dict,
    *,
    previous_result: str | None = None,
    clock: Clock = utc,
) -> dict:
    """Ingest an external assertion, with exact retry and prerequisite bindings.

    ``result`` fields are documented in assurance-review.rst. Nothing here
    executes the registered procedure or authenticates the attributed actor.
    """
    state = readiness(history, current_manifest)
    _require(state["current_binding"], "STALE_BINDING")
    return _append(
        history, event_id, "result", {"result": result, "previous_result": previous_result}, clock
    )


def evidence_status(
    history: dict,
    event_id: str,
    result_digest: str,
    evidence_id: str,
    previous_status: str,
    status: dict,
    *,
    clock: Clock = utc,
) -> dict:
    """Append status/applicability/eligibility assertions with an exact predecessor."""
    return _append(
        history,
        event_id,
        "evidence-status",
        {
            "result_digest": result_digest,
            "evidence_id": evidence_id,
            "previous_status": previous_status,
            "status": status,
        },
        clock,
    )


def resume(history: dict, current_manifest: dict, pending_node: str) -> dict:
    """Return the exact pending node's rechecked dispatch prerequisites.

    This is not a clearance event. A ready node remains pending until a bound,
    eligible result is ingested. Flags or clearance strings cannot resume it.
    """
    _text(pending_node)
    state = readiness(history, current_manifest)
    _require(state["current_binding"], "STALE_BINDING")
    _require(pending_node == state["pending_node"], "PENDING_NODE")
    _require(state["nodes"][pending_node]["ready"], "PREREQUISITES")
    return copy.deepcopy(state["nodes"][pending_node])


def _dispositions(data: dict, state: dict, supplied: Any, baseline: dict) -> tuple[list, list]:
    _list(supplied)
    planned = data["plan"]["payload"]["data"]
    originals = {
        output["payload"]["data"]["lane"] + "/" + finding["id"]: (output, finding["id"])
        for output in planned["original_outputs"]
        for finding in output["payload"]["data"]["findings"]
    }
    _, _, _, archived = _fold(data["history"])
    ledger = []
    resolved = set()
    seen = set()
    for disposition in supplied:
        _require(isinstance(disposition, dict), "FIELDS")
        ref = disposition.get("finding")
        _text(ref)
        _require(ref in baseline["findings"] and ref not in seen, "FINDING")
        seen.add(ref)
        route = disposition.get("route")
        _choice(route, ("retain", "proposed-mutation", "nonmutating"))
        if route != "nonmutating":
            _keys(
                disposition,
                (
                    "finding route rationale"
                    if route == "retain"
                    else "finding disposition route rationale"
                ),
            )
            if route == "proposed-mutation":
                _require(disposition["disposition"] == "FIXED", "DISPOSITION_ROUTE")
            _text(disposition["rationale"])
            ledger.append(copy.deepcopy(disposition))
            continue
        _keys(
            disposition,
            "finding disposition route disposition_reason followup evidence "
            "result_digest evidence_id dissent",
        )
        _require(disposition["disposition"] == "REJECTED_WITH_EVIDENCE", "DISPOSITION_ROUTE")
        _text(disposition["disposition_reason"])
        original, finding_id = originals[ref]
        adequacy = review.remediation_adequacy(
            planned["review_plan"],
            original,
            finding_id,
            disposition["followup"],
            disposition["evidence"],
        )
        _keys(disposition["dissent"], "source_quote response")
        _require(
            disposition["dissent"]["source_quote"] == baseline["findings"][ref]["source_quote"],
            "DISSENT_SOURCE",
        )
        _text(disposition["dissent"]["response"])
        result_hash = disposition["result_digest"]
        evidence_id = disposition["evidence_id"]
        _hash(result_hash)
        _text(evidence_id)
        _require(result_hash in archived, "RESULT_REFERENCE")
        result = archived[result_hash]
        node = result["node_id"]
        usable = (
            state["current_binding"]
            and state["latest_results"].get(node) == result_hash
            and state["nodes"][node]["state"] == "PASSED"
        )
        matches = [e for e in result["evidence"] if e["id"] == evidence_id]
        _require(len(matches) == 1, "EVIDENCE_REFERENCE")
        _require(
            {"finding": ref, "requirement_digest": digest(baseline["findings"][ref])}
            in matches[0]["finding_requirements"],
            "FINDING_BINDING",
        )
        source = matches[0]["source"]
        _require(baseline["findings"][ref]["source_quote"] in source, "FINDING_SOURCE")
        _require(
            all(check["source_quote"] in source for check in disposition["evidence"]["checks"]),
            "RESPONSE_SOURCE",
        )
        _require(
            disposition["disposition_reason"] in source
            and disposition["disposition_reason"]
            in disposition["followup"]["payload"]["data"]["source"],
            "DISPOSITION_SOURCE",
        )
        ledger.append(
            {
                **copy.deepcopy(disposition),
                "adequacy": adequacy,
                "current": usable,
                "decision_meaning": "fixture-only rejection recommendation; not authorized adjudication",
            }
        )
        if usable:
            resolved.add(ref)
    blockers = ["finding:" + ref for ref in baseline["findings"] if ref not in resolved]
    for relation in planned["relations"]:
        if relation["type"] == "contradicts" and not {relation["from"], relation["to"]} <= resolved:
            blockers.append("unresolved-contradiction:" + relation["from"] + "|" + relation["to"])
    return ledger, blockers


def reconcile(
    history: dict,
    current_manifest: dict,
    dispositions: list[dict],
    *,
    clock: Clock = utc,
) -> dict:
    """Recompute original review and assurance; emit only a fixture recommendation.

    Every original finding and relation is retained. FIXED routes are proposals,
    never executed or treated as closure. Responses require public review
    remediation coverage plus currently eligible finding-bound assurance evidence.
    """
    _bounded(dispositions)
    history_data, _, _, _ = _fold(history)
    planned = history_data["plan"]["payload"]["data"]
    baseline = _baseline(planned)
    state = readiness(history, current_manifest)
    ledger, blockers = _dispositions(
        {"plan": history_data["plan"], "history": history}, state, dispositions, baseline
    )
    for blocker in baseline["blockers"]:
        if blocker["cause"] != "unresolved-conflict":
            blockers.append("review:" + blocker["pending_requirement"])
    required = [n for n in planned["nodes"] if n["requirement"] == "required"]
    if not required:
        blockers.append("empty-required-set")
    if not state["current_binding"]:
        blockers.append("candidate-context-drift")
    for node in planned["nodes"]:
        if node["requirement"] != "not_required_with_rationale":
            if state["nodes"][node["id"]]["state"] != "PASSED":
                blockers.append("node:" + node["id"])
    return _wrap(
        "recommendation",
        {
            "history": history,
            "current_manifest": current_manifest,
            "dispositions": dispositions,
            "original_review": baseline,
            "disposition_ledger": ledger,
            "state": state,
            "blockers": blockers,
            "recommendation": ("BLOCKED" if blockers else "CONVERGED_FOR_AUTHORIZED_DECISION"),
            "limits": _LIMITS,
        },
        clock,
    )


def validate_artifact(artifact: dict) -> None:
    """Validate a supplied plan, history or fully recomputed recommendation."""
    _bounded(artifact)
    _require(isinstance(artifact, dict) and isinstance(artifact.get("payload"), dict), "FIELDS")
    kind = artifact["payload"].get("kind")
    _choice(kind, ("plan", "history", "recommendation"))
    if kind == "plan":
        _plan(artifact)
    elif kind == "history":
        fold_events(artifact)
    else:
        data = _data(artifact, "recommendation")
        _keys(
            data,
            "history current_manifest dispositions original_review disposition_ledger "
            "state blockers recommendation limits",
        )
        _limits(data)
        expected = reconcile(data["history"], data["current_manifest"], data["dispositions"])
        _require(data == expected["payload"]["data"], "RECOMMENDATION_MISMATCH")


def attach_continuation(continuation: dict, artifacts: list[dict], *, clock: Clock = utc) -> dict:
    """Return a Draft successor for the existing storage coordinator to persist.

    The coordinator must still preview/revalidate repository drift and use its
    existing write path. No files are written and no new store is created here.
    """
    _bounded(continuation, maximum=core.MAX_BYTES)
    validate(continuation)
    _require(continuation["schema"] == "codex.continuation-state.v1", "CONTINUATION")
    _list(artifacts, MAX_EVENTS)
    _bounded(artifacts, maximum=core.MAX_BYTES)
    for artifact in artifacts:
        validate_artifact(artifact)
    payload = copy.deepcopy(continuation["payload"])
    payload["sequence"] += 1
    payload["predecessor"] = digest(continuation)
    known = {artifact["id"] for artifact in payload["records"]}
    for artifact in artifacts:
        _require(artifact["id"] not in known, "DUPLICATE_ATTACHMENT")
        known.add(artifact["id"])
        payload["records"].append(copy.deepcopy(artifact))
    _bounded(payload, maximum=core.MAX_BYTES)
    result = record("codex.continuation-state.v1", payload, clock)
    result["supersedes"] = continuation["id"]
    result["extensions"] = copy.deepcopy(continuation["extensions"])
    result["integrity"] = digest({k: v for k, v in result.items() if k != "integrity"})
    _bounded(result, maximum=core.MAX_BYTES)
    validate(result)
    return result
