"""Supplied-data assurance fixtures; names never establish trusted independence."""

from __future__ import annotations

import builtins
import copy
import io
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from codex.institutional import assurance, core, review, storage

NOW = datetime(2026, 10, 25, tzinfo=timezone.utc)
BEARINGS = (
    ("000", "Policy"),
    ("045", "Security"),
    ("090", "Architecture"),
    ("135", "Adversarial"),
    ("180", "Verification"),
    ("225", "Operations"),
    ("270", "Portability"),
    ("315", "History"),
)


def clock():
    return NOW


def event_id(number):
    return str(UUID(f"00000000-0000-4000-8000-{number:012x}"))


def reseal(value):
    value = copy.deepcopy(value)
    value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    return value


def manifest(content=b"candidate", context=None):
    return review.candidate_manifest(
        [{"path": "candidate.py", "content": content, "kind": "file", "mode": 0o644}],
        context or {"purpose": "fixture"},
        clock=clock,
    )


def original_finding():
    return {
        "id": "concern",
        "source_quote": "original concern",
        "normalized": "Preserve the original concern",
        "kind": "inference",
        "confidence": 0.4,
        "coverage": ["correctness"],
        "clearance_conditions": ["reproduce-original"],
    }


def review_fixture(findings=False, contradiction=False):
    lanes = [
        {
            "id": coordinate,
            "bearing": bearing,
            "actor": "same-platform:" + coordinate,
            "run": "fixture:" + coordinate,
            "dissent": False,
            "required": True,
            "coverage": ["correctness"],
            "tools": ["read", "search"],
        }
        for coordinate, bearing in BEARINGS
    ]
    lanes.extend(
        {
            "id": name,
            "bearing": bearing,
            "actor": "same-platform:" + name,
            "run": "fixture:" + name,
            "dissent": name == "dissent",
            "required": name == "dissent",
            "coverage": ["correctness"],
            "tools": ["read", "search"],
        }
        for name, bearing in (("dissent", "cross-cutting"), ("rotated", "Reasoning integrity"))
    )
    planned = review.review_plan(manifest(), lanes, ["correctness"], ["correctness"], clock=clock)
    outputs = [
        review.lane_output(
            planned,
            lane["id"],
            lane["id"] + ": original concern; observed original reproduction",
            [original_finding()] if findings and lane["id"] in ("000", "dissent") else [],
            clock=clock,
        )
        for lane in lanes
        if lane["required"]
    ]
    relations = (
        [{"type": "contradicts", "from": "000/concern", "to": "dissent/concern"}]
        if contradiction
        else []
    )
    return planned, outputs, relations


def fixture_plan(*, findings=False, contradiction=False, dependencies=True):
    planned, outputs, relations = review_fixture(findings, contradiction)
    baseline = review.reconcile(planned, outputs, relations, clock=clock)["payload"]["data"]
    requirements = [
        {"finding": key, "requirement_digest": core.digest(value)}
        for key, value in baseline["findings"].items()
    ]
    procedures = [
        {"id": kind + "-fixture", "version": "1", "kind": kind, "expected_outputs": ["report"]}
        for kind in assurance.KINDS
    ]
    nodes = [
        {
            "id": kind,
            "kind": kind,
            "depends_on": (
                ["technical_verification"]
                if dependencies and kind != "technical_verification"
                else []
            ),
            "requirement": "required",
            "rationale": "Explicit fixture coverage, not an operational assurance decision.",
            "role": kind,
            "actor": "same-platform:" + kind,
            "identity_assurance": "unverified",
            "independence": "fixture-only",
            "procedure": {"id": kind + "-fixture", "version": "1"},
            "environment_digest": core.digest({"runtime": "fixture"}),
            "expected_outputs": ["report"],
            "resource_caps": {"max_bytes": 65536, "max_attempts": 8},
            "finding_requirements": requirements,
            "evidence_requirements": ["procedure-observation"],
            "pending": "Supply bound external fixture report",
            "recovery": "Reevaluate prerequisites and append explicit retry",
        }
        for kind in assurance.KINDS
    ]
    return assurance.assurance_plan(planned, outputs, relations, procedures, nodes, clock=clock)


def changed_plan(planned, change):
    value = copy.deepcopy(planned)
    change(value["payload"]["data"])
    return reseal(value)


def supplied_result(history, node_id, *, outcome="PASS", suffix=""):
    planned = history["payload"]["data"]["plan"]
    data = planned["payload"]["data"]
    node = next(n for n in data["nodes"] if n["id"] == node_id)
    state = assurance.readiness(history, manifest())
    return {
        "node_id": node_id,
        "plan_digest": core.digest(planned),
        "binding": data["binding"],
        "procedure": copy.deepcopy(node["procedure"]),
        "environment_digest": node["environment_digest"],
        "actor": node["actor"],
        "identity_assurance": "unverified",
        "outcome": outcome,
        "outputs": ["report"],
        "bytes_used": 300,
        "prerequisites": state["nodes"][node_id]["prerequisites"],
        "evidence": [
            {
                "id": "observation" + suffix,
                "source": (
                    "supplied fixture observation; original concern; "
                    "observed original reproduction; "
                    "fixture reproduction does not substantiate original concern " + suffix
                ),
                "provenance": "unverified",
                "authority": "none",
                "status": "ACTIVE",
                "applicability": "applicable",
                "eligibility": "eligible",
                "critical": True,
                "requirements": ["procedure-observation"],
                "finding_requirements": copy.deepcopy(node["finding_requirements"]),
            }
        ],
    }


def complete(planned=None):
    planned = planned or fixture_plan()
    history = assurance.new_history(planned, clock=clock)
    for index, kind in enumerate(assurance.KINDS, 1):
        result = supplied_result(history, kind)
        history = assurance.ingest_result(history, manifest(), event_id(index), result, clock=clock)
    return history


def alter_status(history, status="REVOKED", *, eligibility="eligible", event=20):
    folded = assurance.fold_events(history)
    result_hash = folded["latest_results"]["technical_verification"]
    previous = folded["evidence_states"][result_hash]["observation"]
    return assurance.evidence_status(
        history,
        event_id(event),
        result_hash,
        "observation",
        core.digest(previous),
        {
            "status": status,
            "applicability": "applicable",
            "eligibility": eligibility,
            "reason": "external fixture status assertion",
        },
        clock=clock,
    )


def test_fixture_canonical_bearings_and_dag_are_distinct_from_independence():
    planned = fixture_plan()
    lanes = planned["payload"]["data"]["review_plan"]["payload"]["data"]["lanes"]
    assert [(lane["id"], lane["bearing"]) for lane in lanes[:8]] == list(BEARINGS)
    assert lanes[8]["bearing"] == "cross-cutting" and lanes[8]["dissent"]
    assert lanes[9]["bearing"] == "Reasoning integrity"
    history = assurance.new_history(planned, clock=clock)
    ready = assurance.readiness(history, manifest())
    assert ready["pending_node"] == "technical_verification"
    assert ready["nodes"]["technical_verification"]["ready"]
    assert not ready["nodes"]["institutional_audit"]["ready"]
    assert assurance.resume(history, manifest(), "technical_verification")["state"] == "READY"
    assert assurance.fold_events(history)["pending_node"] == "technical_verification"


def test_happy_path_no_vacuous_authority_and_no_universal_reproduction_gate():
    history = complete()
    result = assurance.reconcile(history, manifest(), [], clock=clock)
    assert result == assurance.reconcile(history, manifest(), [], clock=clock)
    data = result["payload"]["data"]
    assert data["recommendation"] == "CONVERGED_FOR_AUTHORIZED_DECISION"
    assert data["limits"]["authority"] == "none"
    assert data["limits"]["approval"] is False
    assert data["limits"]["activation"] is False
    assert data["limits"]["fixture_only"] is True
    assurance.validate_artifact(result)
    independent_plan = fixture_plan(dependencies=False)
    state = assurance.readiness(assurance.new_history(independent_plan), manifest())
    assert all(node["ready"] for node in state["nodes"].values())
    # Declared technical prerequisite suffices; reproduction is not an audit prerequisite.
    partial = assurance.new_history(fixture_plan(), clock=clock)
    partial = assurance.ingest_result(
        partial, manifest(), event_id(1), supplied_result(partial, "technical_verification")
    )
    assert assurance.readiness(partial, manifest())["nodes"]["institutional_audit"]["ready"]


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d["nodes"][0].update(depends_on=["technical_verification"]),
        lambda d: d["nodes"][0].update(depends_on=["institutional_audit"]),
        lambda d: d["nodes"][0].update(depends_on=["missing"]),
        lambda d: d["nodes"].append(copy.deepcopy(d["nodes"][0])),
        lambda d: d["nodes"][0].update(rationale=""),
        lambda d: d["nodes"][0].update(requirement="not-required"),
        lambda d: d["nodes"][0]["procedure"].update(version="unknown"),
        lambda d: d["nodes"][0]["procedure"].update(command="echo no"),
        lambda d: d["procedures"].append(copy.deepcopy(d["procedures"][0])),
        lambda d: d["nodes"][0].update(role="authorized_decision_authority"),
        lambda d: d["nodes"][0].update(identity_assurance="trusted"),
        lambda d: d["nodes"][0]["resource_caps"].update(max_attempts=True),
        lambda d: d["nodes"][0]["resource_caps"].update(max_bytes=10**10000),
        lambda d: d["nodes"][0]["resource_caps"].update(max_bytes=0),
        lambda d: d["nodes"][0].update(environment_digest="bad"),
        lambda d: d.update(binding="a" * 64),
    ],
)
def test_imported_plan_strictly_rejected(change):
    bad = copy.deepcopy(fixture_plan())
    change(bad["payload"]["data"])
    if "resource_caps" in bad["payload"]["data"]["nodes"][0]:
        cap = bad["payload"]["data"]["nodes"][0]["resource_caps"]["max_bytes"]
        if type(cap) is int and cap.bit_length() > 63:
            with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
                assurance.validate_artifact(bad)
            return
    with pytest.raises(core.Rejected):
        assurance.new_history(reseal(bad))


def test_not_required_rationale_and_empty_required_set_fail_closed():
    planned = changed_plan(
        fixture_plan(),
        lambda d: [n.update(requirement="not_required_with_rationale") for n in d["nodes"]],
    )
    history = assurance.new_history(planned)
    assert assurance.reconcile(history, manifest(), [])["payload"]["data"]["blockers"] == [
        "empty-required-set"
    ]
    for change in (
        lambda d: d.update(nodes=[]),
        lambda d: d["nodes"][0].update(requirement="blocked"),
    ):
        planned = changed_plan(fixture_plan(), change)
        history = assurance.new_history(planned)
        assert assurance.reconcile(history, manifest(), [])["payload"]["data"][
            "recommendation"
        ] == ("BLOCKED")
    invalid = changed_plan(
        fixture_plan(),
        lambda d: d["nodes"][0].update(requirement="not_required_with_rationale", rationale=" "),
    )
    with pytest.raises(core.Rejected, match="TEXT"):
        assurance.new_history(invalid)


@pytest.mark.parametrize("outcome", ["FAIL", "INCONCLUSIVE", "BLOCKED"])
def test_outcomes_and_declared_prerequisites_block(outcome):
    history = assurance.new_history(fixture_plan(), clock=clock)
    result = supplied_result(history, "technical_verification", outcome=outcome)
    history = assurance.ingest_result(history, manifest(), event_id(1), result)
    state = assurance.readiness(history, manifest())
    assert state["nodes"]["technical_verification"]["state"] == "BLOCKED"
    assert not state["nodes"]["institutional_audit"]["ready"]
    with pytest.raises(core.Rejected, match="PREREQUISITES"):
        assurance.ingest_result(
            history, manifest(), event_id(2), supplied_result(history, "institutional_audit")
        )


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r.update(node_id="missing"),
        lambda r: r.update(plan_digest="a" * 64),
        lambda r: r.update(binding="a" * 64),
        lambda r: r["procedure"].update(version="2"),
        lambda r: r.update(environment_digest="b" * 64),
        lambda r: r.update(actor="independent"),
        lambda r: r.update(identity_assurance="trusted"),
        lambda r: r.update(bytes_used=10**10000),
        lambda r: r.update(bytes_used=True),
        lambda r: r.update(outputs=["unknown"]),
        lambda r: r.update(prerequisites={"fake": "c" * 64}),
        lambda r: r["evidence"][0].update(provenance="verified"),
        lambda r: r["evidence"][0].update(authority="owner"),
        lambda r: r["evidence"][0].update(status="UNKNOWN"),
        lambda r: r["evidence"][0].update(critical="yes"),
        lambda r: r["evidence"][0].update(requirements=["missing"]),
        lambda r: r["evidence"][0].update(finding_requirements=[{}]),
        lambda r: r["evidence"].append(copy.deepcopy(r["evidence"][0])),
    ],
)
def test_result_bindings_and_bounds_cannot_be_self_asserted(change):
    history = assurance.new_history(fixture_plan())
    result = supplied_result(history, "technical_verification")
    change(result)
    with pytest.raises(core.Rejected):
        assurance.ingest_result(history, manifest(), event_id(1), result)


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r["evidence"][0].update(eligibility="unknown"),
        lambda r: r["evidence"][0].update(eligibility="ineligible"),
        lambda r: r["evidence"][0].update(applicability="unknown"),
        lambda r: r["evidence"][0].update(applicability="not_applicable"),
        lambda r: r.update(evidence=[]),
        lambda r: r.update(outputs=[]),
    ],
)
def test_valid_but_ineligible_assertions_never_satisfy_required_node(change):
    history = assurance.new_history(fixture_plan())
    result = supplied_result(history, "technical_verification")
    change(result)
    history = assurance.ingest_result(history, manifest(), event_id(1), result)
    assert assurance.fold_events(history)["nodes"]["technical_verification"]["state"] == "BLOCKED"
    assert assurance.reconcile(history, manifest(), [])["payload"]["data"]["recommendation"] == (
        "BLOCKED"
    )


def test_independent_role_name_never_satisfies_trusted_independence():
    planned = changed_plan(
        fixture_plan(),
        lambda d: d["nodes"][0].update(independence="trusted-required"),
    )
    history = assurance.new_history(planned)
    result = supplied_result(history, "technical_verification")
    assert (
        "trusted-independence-unavailable"
        in assurance.fold_events(history)["nodes"]["technical_verification"]["blockers"]
    )
    with pytest.raises(core.Rejected, match="PREREQUISITES"):
        assurance.ingest_result(history, manifest(), event_id(1), result)


@pytest.mark.parametrize("status", assurance.STATUSES[1:])
def test_status_invalidation_reopens_passed_downstream_and_recommendation(status):
    history = complete()
    invalidated = alter_status(history, status)
    state = assurance.fold_events(invalidated)
    assert state["nodes"]["technical_verification"]["state"] == "BLOCKED"
    assert state["nodes"]["institutional_audit"]["state"] == "BLOCKED"
    assert history["payload"]["data"]["events"] == invalidated["payload"]["data"]["events"][:-1]
    assert assurance.reconcile(invalidated, manifest(), [])["payload"]["data"][
        "recommendation"
    ] == ("BLOCKED")
    restored = alter_status(invalidated, "ACTIVE", event=21)
    state = assurance.fold_events(restored)
    assert state["nodes"]["technical_verification"]["state"] == "PASSED"
    assert state["nodes"]["institutional_audit"]["state"] == "BLOCKED"
    assert "stale-prerequisite-binding" in state["nodes"]["institutional_audit"]["blockers"]
    assert state["nodes"]["institutional_audit"]["ready"]


def test_critical_unknown_eligibility_is_not_an_evidence_status():
    history = alter_status(complete(), "ACTIVE", eligibility="unknown")
    state = assurance.fold_events(history)
    assert (
        "critical-eligibility:observation" in state["nodes"]["technical_verification"]["blockers"]
    )
    assert assurance.STATUSES == (
        "ACTIVE",
        "SUPERSEDED",
        "REVOKED",
        "DISPUTED",
        "STALE",
        "UNAVAILABLE",
    )


def test_restoring_identical_evidence_assertion_cannot_erase_invalidation_revision():
    history = complete()
    original_state = assurance.fold_events(history)
    result_hash = original_state["latest_results"]["technical_verification"]
    initial = original_state["evidence_states"][result_hash]["observation"]
    revoked = alter_status(history)
    current = assurance.fold_events(revoked)["evidence_states"][result_hash]["observation"]
    restored = assurance.evidence_status(
        revoked,
        event_id(21),
        result_hash,
        "observation",
        core.digest(current),
        {key: initial[key] for key in ("status", "applicability", "eligibility", "reason")},
        clock=clock,
    )
    state = assurance.fold_events(restored)
    assert state["nodes"]["technical_verification"]["state"] == "PASSED"
    assert state["nodes"]["institutional_audit"]["state"] == "BLOCKED"
    assert state["nodes"]["independent_reproduction"]["state"] == "BLOCKED"
    assert assurance.reconcile(restored, manifest(), [])["payload"]["data"]["recommendation"] == (
        "BLOCKED"
    )


def exempt_bridge_plan():
    def change(data):
        data["nodes"][1].update(requirement="not_required_with_rationale")
        data["nodes"][2].update(depends_on=["independent_reproduction"])

    return changed_plan(fixture_plan(), change)


def test_exempt_execution_preserves_transitive_prerequisite_gating():
    history = assurance.new_history(exempt_bridge_plan(), clock=clock)
    state = assurance.fold_events(history)
    assert state["nodes"]["independent_reproduction"]["state"] == "BLOCKED"
    assert not state["nodes"]["institutional_audit"]["ready"]
    with pytest.raises(core.Rejected, match="PREREQUISITES"):
        assurance.ingest_result(
            history, manifest(), event_id(1), supplied_result(history, "institutional_audit")
        )


@pytest.mark.parametrize("invalidation", ["retry", "revoke", "restore-identical"])
def test_exempt_bridge_proof_tracks_upstream_revision_and_requires_downstream_retry(invalidation):
    history = assurance.new_history(exempt_bridge_plan(), clock=clock)
    original = supplied_result(history, "technical_verification")
    history = assurance.ingest_result(history, manifest(), event_id(1), original, clock=clock)
    history = assurance.ingest_result(
        history,
        manifest(),
        event_id(2),
        supplied_result(history, "institutional_audit"),
        clock=clock,
    )
    assert assurance.fold_events(history)["nodes"]["institutional_audit"]["state"] == "PASSED"
    initial_state = assurance.fold_events(history)
    result_hash = initial_state["latest_results"]["technical_verification"]
    initial = initial_state["evidence_states"][result_hash]["observation"]
    if invalidation == "retry":
        replacement = supplied_result(history, "technical_verification", suffix="-replacement")
        history = assurance.ingest_result(
            history,
            manifest(),
            event_id(10),
            replacement,
            previous_result=core.digest(original),
            clock=clock,
        )
    else:
        history = alter_status(history)
        if invalidation == "restore-identical":
            current = assurance.fold_events(history)["evidence_states"][result_hash]["observation"]
            history = assurance.evidence_status(
                history,
                event_id(21),
                result_hash,
                "observation",
                core.digest(current),
                {key: initial[key] for key in ("status", "applicability", "eligibility", "reason")},
                clock=clock,
            )
    state = assurance.fold_events(history)
    assert state["nodes"]["institutional_audit"]["state"] == "BLOCKED"
    assert assurance.reconcile(history, manifest(), [])["payload"]["data"]["recommendation"] == (
        "BLOCKED"
    )
    if invalidation != "revoke":
        replacement = supplied_result(history, "institutional_audit", suffix="-after-invalidation")
        history = assurance.ingest_result(
            history,
            manifest(),
            event_id(30),
            replacement,
            previous_result=state["latest_results"]["institutional_audit"],
            clock=clock,
        )
        assert assurance.fold_events(history)["nodes"]["institutional_audit"]["state"] == "PASSED"


def test_retry_preserves_original_and_invalidates_transitive_results():
    history = complete()
    prior = assurance.fold_events(history)["latest_results"]["technical_verification"]
    replacement = supplied_result(history, "technical_verification", suffix="-retry")
    for previous in (None, "a" * 64):
        with pytest.raises(core.Rejected, match="RETRY_PREDECESSOR"):
            assurance.ingest_result(
                history, manifest(), event_id(10), replacement, previous_result=previous
            )
    original = history["payload"]["data"]["events"][0]["detail"]["result"]
    with pytest.raises(core.Rejected, match="DUPLICATE_RESULT"):
        assurance.ingest_result(history, manifest(), event_id(10), original, previous_result=prior)
    successor = assurance.ingest_result(
        history, manifest(), event_id(10), replacement, previous_result=prior
    )
    state = assurance.fold_events(successor)
    assert state["result_statuses"][prior] == "SUPERSEDED"
    assert state["nodes"]["technical_verification"]["state"] == "PASSED"
    assert state["nodes"]["independent_reproduction"]["state"] == "BLOCKED"
    assert successor["payload"]["data"]["events"][:-1] == history["payload"]["data"]["events"]


def test_event_chain_cache_and_status_predecessor_are_checked():
    history = complete()
    cache = assurance.fold_events(history)
    assert assurance.fold_events(history, cache) == cache
    bad_cache = copy.deepcopy(cache)
    bad_cache["pending_node"] = "forged"
    with pytest.raises(core.Rejected, match="CACHE_MISMATCH"):
        assurance.fold_events(history, bad_cache)
    for change in (
        lambda es: es.reverse(),
        lambda es: es.append(copy.deepcopy(es[0])),
        lambda es: es[0].update(sequence=9),
        lambda es: es[0].update(predecessor="a" * 64),
        lambda es: es[0].update(digest="a" * 64),
    ):
        bad = copy.deepcopy(history)
        change(bad["payload"]["data"]["events"])
        with pytest.raises(core.Rejected):
            assurance.fold_events(reseal(bad))
    state = assurance.fold_events(history)
    result_hash = state["latest_results"]["technical_verification"]
    with pytest.raises(core.Rejected, match="STATUS_PREDECESSOR"):
        assurance.evidence_status(
            history,
            event_id(5),
            result_hash,
            "observation",
            "a" * 64,
            {
                "status": "REVOKED",
                "applicability": "applicable",
                "eligibility": "eligible",
                "reason": "fixture",
            },
        )


@pytest.mark.parametrize(
    "changed",
    [
        lambda: manifest(b"changed"),
        lambda: manifest(context={"purpose": "new-context"}),
    ],
)
def test_candidate_context_drift_reopens_and_cannot_be_resumed(changed):
    history = complete()
    state = assurance.readiness(history, changed())
    assert state["current_binding"] is False
    assert all(n["state"] == "BLOCKED" for n in state["nodes"].values())
    with pytest.raises(core.Rejected, match="STALE_BINDING"):
        assurance.resume(history, changed(), state["pending_node"])
    with pytest.raises(core.Rejected, match="STALE_BINDING"):
        assurance.ingest_result(
            history, changed(), event_id(12), supplied_result(history, "technical_verification")
        )
    assert assurance.reconcile(history, changed(), [])["payload"]["data"]["recommendation"] == (
        "BLOCKED"
    )


def test_exact_pending_resume_rechecks_prerequisites_not_clearance_flags():
    history = complete()
    invalidated = alter_status(history)
    with pytest.raises(core.Rejected, match="PENDING_NODE"):
        assurance.resume(invalidated, manifest(), "institutional_audit")
    restored = alter_status(invalidated, "ACTIVE", event=21)
    state = assurance.fold_events(restored)
    assert state["pending_node"] == "independent_reproduction"
    resumed = assurance.resume(restored, manifest(), "independent_reproduction")
    assert resumed["ready"] and resumed["state"] == "BLOCKED"
    assert assurance.fold_events(restored)["pending_node"] == "independent_reproduction"


def response_dispositions(history):
    data = history["payload"]["data"]["plan"]["payload"]["data"]
    planned = data["review_plan"]
    followup = review.lane_output(
        planned,
        "rotated",
        "original concern; observed original reproduction; "
        "fixture reproduction does not substantiate original concern",
        [original_finding()],
        clock=clock,
    )
    dispositions = []
    for output in data["original_outputs"]:
        lane = output["payload"]["data"]["lane"]
        if not output["payload"]["data"]["findings"]:
            continue
        dispositions.append(
            {
                "finding": lane + "/concern",
                "disposition": "REJECTED_WITH_EVIDENCE",
                "route": "nonmutating",
                "disposition_reason": "fixture reproduction does not substantiate original concern",
                "followup": followup,
                "evidence": {
                    "original_output": core.digest(output),
                    "finding_id": "concern",
                    "followup_output": core.digest(followup),
                    "checks": [
                        {
                            "condition": "reproduce-original",
                            "observation": "observed original reproduction",
                            "source_quote": "observed original reproduction",
                        }
                    ],
                },
                "result_digest": assurance.fold_events(history)["latest_results"][
                    "technical_verification"
                ],
                "evidence_id": "observation",
                "dissent": {
                    "source_quote": "original concern",
                    "response": "Fixture addresses original concern; minority wording retained.",
                },
            }
        )
    return dispositions


def test_finding_response_retains_minority_and_original_contradiction_ledger():
    history = complete(fixture_plan(findings=True, contradiction=True))
    dispositions = response_dispositions(history)
    unresolved = assurance.reconcile(history, manifest(), [])
    assert unresolved["payload"]["data"]["recommendation"] == "BLOCKED"
    final = assurance.reconcile(history, manifest(), dispositions, clock=clock)
    data = final["payload"]["data"]
    assert data["recommendation"] == "CONVERGED_FOR_AUTHORIZED_DECISION"
    assert data["original_review"]["relations"][0]["type"] == "contradicts"
    assert data["original_review"]["findings"]["dissent/concern"]["source_quote"] == (
        "original concern"
    )
    assert all(
        entry["adequacy"]["identity"] == "unverified" for entry in data["disposition_ledger"]
    )
    assert all(
        entry["disposition"] == "REJECTED_WITH_EVIDENCE"
        and entry["route"] == "nonmutating"
        and entry["decision_meaning"]
        == ("fixture-only rejection recommendation; not authorized adjudication")
        for entry in data["disposition_ledger"]
    )
    assurance.validate_artifact(final)
    reopened = assurance.reconcile(alter_status(history), manifest(), dispositions)
    assert reopened["payload"]["data"]["recommendation"] == "BLOCKED"


@pytest.mark.parametrize(
    "change",
    [
        lambda ds: ds.pop(),
        lambda ds: ds[0]["evidence"].update(checks=[]),
        lambda ds: ds[0]["evidence"].update(adequate=True),
        lambda ds: ds[0]["evidence"].update(original_output="a" * 64),
        lambda ds: ds[0].update(result_digest="a" * 64),
        lambda ds: ds[0].update(evidence_id="missing"),
        lambda ds: ds[0]["dissent"].update(source_quote="replacement wording"),
        lambda ds: ds[0]["dissent"].update(response=""),
        lambda ds: ds[0].update(disposition_reason="invented rejection"),
        lambda ds: ds.append(copy.deepcopy(ds[0])),
    ],
)
def test_no_boolean_string_or_incomplete_response_can_clear_original_concern(change):
    history = complete(fixture_plan(findings=True, contradiction=True))
    dispositions = response_dispositions(history)
    change(dispositions)
    try:
        final = assurance.reconcile(history, manifest(), dispositions)
    except core.Rejected:
        return
    assert final["payload"]["data"]["recommendation"] == "BLOCKED"


def test_fixed_route_is_never_executed_or_closure_and_relations_cannot_be_dropped():
    history = complete(fixture_plan(findings=True, contradiction=True))
    for route in ("proposed-mutation", "retain"):
        dispositions = [
            {
                "finding": key,
                "route": route,
                "rationale": "fixture proposal only",
                **({"disposition": "FIXED"} if route == "proposed-mutation" else {}),
            }
            for key in ("000/concern", "dissent/concern")
        ]
        data = assurance.reconcile(history, manifest(), dispositions)["payload"]["data"]
        assert data["recommendation"] == "BLOCKED"
        assert data["original_review"]["relations"]


@pytest.mark.parametrize(
    "disposition",
    ["ACCEPTED_RISK", "NOT_APPLICABLE", "SUPERSEDED", "DEFERRED", "OUT_OF_SCOPE_TRANSFER", "FIXED"],
)
def test_unsupported_dispositions_cannot_use_nonmutating_rejection_route(disposition):
    history = complete(fixture_plan(findings=True, contradiction=True))
    supplied = response_dispositions(history)
    supplied[0]["disposition"] = disposition
    with pytest.raises(core.Rejected, match="DISPOSITION_ROUTE"):
        assurance.reconcile(history, manifest(), supplied)


@pytest.mark.parametrize(
    "change",
    [
        lambda v: v.update(authority_refs=["self-approved"]),
        lambda v: v.update(lifecycle="Active"),
        lambda v: v.update(extensions={"runner": "shell"}),
        lambda v: v["producer"].update(assurance="trusted"),
        lambda v: v["payload"]["data"]["limits"].update(authority="approved"),
        lambda v: v["payload"]["data"]["limits"].update(approval=True),
        lambda v: v["payload"]["data"]["limits"].update(activation=True),
        lambda v: v["payload"]["data"]["limits"].update(fixture_only=False),
    ],
)
def test_imported_artifacts_never_elevate_authority(change):
    artifact = assurance.reconcile(complete(), manifest(), [])
    change(artifact)
    with pytest.raises(core.Rejected):
        assurance.validate_artifact(reseal(artifact))


@pytest.mark.parametrize("value", [None, [], {}, {"payload": []}, {"payload": {"kind": []}}])
def test_malformed_public_imports_fail_with_rejected(value):
    with pytest.raises(core.Rejected):
        assurance.validate_artifact(value)


def test_resource_byte_count_event_attempt_limits_and_command_data_stay_inert(monkeypatch):
    planned = fixture_plan()
    history = assurance.new_history(planned)

    def deny(*args, **kwargs):
        raise AssertionError("unexpected side effect")

    monkeypatch.setattr(builtins, "open", deny)
    monkeypatch.setattr(io, "open", deny)
    monkeypatch.setattr(subprocess, "Popen", deny)
    monkeypatch.setattr(socket, "socket", deny)
    for name in ("glob", "rglob", "iterdir", "write_text", "write_bytes"):
        monkeypatch.setattr(Path, name, deny)
    result = supplied_result(history, "technical_verification")
    result["evidence"][0]["source"] = "$(touch never-executed); rm -rf inert-data"
    successor = assurance.ingest_result(history, manifest(), event_id(1), result)
    assurance.reconcile(successor, manifest(), [])
    assurance.validate_artifact(successor)
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.ingest_result(
            history, manifest(), event_id(2), {"huge": "x" * assurance.MAX_BYTES}
        )
    monkeypatch.setattr(assurance, "MAX_EVENTS", 0)
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.fold_events(successor)


def test_existing_continuation_storage_roundtrip_and_tampered_recommendation(tmp_path):
    original = core.candidate(tmp_path, "fixture", clock)
    original["extensions"] = {"user": {"preserve": True}}
    original = reseal(original)
    history = complete()
    planned = history["payload"]["data"]["plan"]
    final = assurance.reconcile(history, manifest(), [], clock=clock)
    before = copy.deepcopy(original)
    successor = assurance.attach_continuation(original, [planned, history, final], clock=clock)
    assert original == before
    assert successor["extensions"] == original["extensions"]
    assert successor["payload"]["predecessor"] == core.digest(original)
    assert successor["payload"]["sequence"] == 2
    assert successor["payload"]["session_id"] == original["payload"]["session_id"]
    assert core.inspect_candidate(successor) == []
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, successor, storage.plan(tmp_path, successor, core.digest(original)))
    assert core.load(tmp_path / core.NAMESPACE / "checkpoint.json") == successor
    bad = copy.deepcopy(final)
    bad["payload"]["data"]["recommendation"] = "APPROVED"
    with pytest.raises(core.Rejected, match="RECOMMENDATION_MISMATCH"):
        assurance.attach_continuation(original, [reseal(bad)])
    with pytest.raises(core.Rejected, match="DUPLICATE_ATTACHMENT"):
        assurance.attach_continuation(successor, [history])


def test_persisted_recovery_preserves_session_extensions_and_rechecks_pending_node(tmp_path):
    original = core.candidate(tmp_path, "stable-recovery-session", clock)
    original["extensions"] = {"user": "unchanged"}
    original = reseal(original)
    history = complete()
    successor = assurance.attach_continuation(original, [history], clock=clock)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, successor, storage.plan(tmp_path, successor, core.digest(original)))
    recovered = core.load(tmp_path / core.NAMESPACE / "checkpoint.json")
    recovered_history = recovered["payload"]["records"][-1]
    revoked = alter_status(recovered_history)
    revoked_recommendation = assurance.reconcile(revoked, manifest(), [], clock=clock)
    next_checkpoint = assurance.attach_continuation(
        recovered, [revoked, revoked_recommendation], clock=clock
    )
    storage.apply(
        tmp_path, next_checkpoint, storage.plan(tmp_path, next_checkpoint, core.digest(recovered))
    )
    recovered = core.load(tmp_path / core.NAMESPACE / "checkpoint.json")
    assert recovered["payload"]["session_id"] == "stable-recovery-session"
    assert recovered["extensions"] == original["extensions"]
    assert recovered["payload"]["sequence"] == 3
    assert recovered["payload"]["predecessor"] == core.digest(successor)
    recovered_history = recovered["payload"]["records"][-2]
    assert assurance.fold_events(recovered_history)["pending_node"] == "technical_verification"
    restored = alter_status(recovered_history, "ACTIVE", event=21)
    assert assurance.resume(restored, manifest(), "independent_reproduction")["ready"]
    assert assurance.reconcile(restored, manifest(), [])["payload"]["data"]["recommendation"] == (
        "BLOCKED"
    )


def test_aggregate_continuation_larger_than_artifact_budget_remains_compatible(tmp_path):
    original = core.candidate(tmp_path, "large-stable-session", clock)
    original["payload"]["configuration"]["retained_profile"] = "x" * (assurance.MAX_BYTES + 1)
    original["extensions"] = {"user": {"preserve": True}}
    original = reseal(original)
    assert assurance.MAX_BYTES < len(core.canonical(original)) < core.MAX_BYTES
    core.validate(original)
    assert core.inspect_candidate(original) == []
    planned = fixture_plan()
    successor = assurance.attach_continuation(original, [planned], clock=clock)
    core.validate(successor)
    assert core.inspect_candidate(successor) == []
    assert successor["extensions"] == original["extensions"]
    assert successor["payload"]["session_id"] == "large-stable-session"
    assert successor["payload"]["configuration"] == original["payload"]["configuration"]
    assert successor["payload"]["sequence"] == 2
    assert successor["payload"]["predecessor"] == core.digest(original)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, successor, storage.plan(tmp_path, successor, core.digest(original)))
    assert core.load(tmp_path / core.NAMESPACE / "checkpoint.json") == successor


@pytest.mark.parametrize("overflow", ["input", "successor"])
def test_aggregate_continuation_inherits_core_cap_and_fails_closed(tmp_path, monkeypatch, overflow):
    original = core.candidate(tmp_path, "bounded-aggregate", clock)
    planned = fixture_plan()
    original_size = len(core.canonical(original))
    attachment_size = len(core.canonical([planned]))
    # Exercise the real aggregate boundary without allocating a 64 MiB fixture.
    limit = (
        original_size - 1
        if overflow == "input"
        else max(original_size, attachment_size) + min(original_size, attachment_size) // 2
    )
    if overflow == "successor":
        assert original_size <= limit and attachment_size <= limit
    monkeypatch.setattr(core, "MAX_BYTES", limit)
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.attach_continuation(original, [planned], clock=clock)


def test_aggregate_budget_never_weakens_individual_assurance_artifact_cap(tmp_path):
    original = core.candidate(tmp_path, "artifact-still-bounded", clock)
    artifact = fixture_plan()
    artifact["oversize"] = "x" * assurance.MAX_BYTES
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.attach_continuation(original, [artifact], clock=clock)


def test_attempt_cap_and_actual_payload_bytes_not_just_claimed_usage():
    planned = changed_plan(
        fixture_plan(),
        lambda d: d["nodes"][0]["resource_caps"].update(max_attempts=1),
    )
    history = assurance.new_history(planned)
    result = supplied_result(history, "technical_verification")
    history = assurance.ingest_result(history, manifest(), event_id(1), result)
    replacement = supplied_result(history, "technical_verification", suffix="-retry")
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.ingest_result(
            history, manifest(), event_id(2), replacement, previous_result=core.digest(result)
        )
    planned = changed_plan(
        fixture_plan(),
        lambda d: d["nodes"][0]["resource_caps"].update(max_bytes=128),
    )
    history = assurance.new_history(planned)
    result = supplied_result(history, "technical_verification")
    result["bytes_used"] = 1
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.ingest_result(history, manifest(), event_id(1), result)


def test_history_mixed_plan_and_noncanonical_event_identity_rejected():
    history = complete()
    bad = copy.deepcopy(history)
    bad["payload"]["data"]["plan"] = fixture_plan(dependencies=False)
    with pytest.raises(core.Rejected, match="RESULT_BINDING"):
        assurance.fold_events(reseal(bad))
    for identity in ("not-a-uuid", str(UUID(int=0)), event_id(1).upper()):
        if identity == event_id(1):
            continue
        empty = assurance.new_history(fixture_plan())
        with pytest.raises(core.Rejected, match="EVENT_ID"):
            assurance.ingest_result(
                empty, manifest(), identity, supplied_result(empty, "technical_verification")
            )


def test_node_count_procedure_count_and_nested_json_limits():
    for key in ("nodes", "procedures"):
        planned = copy.deepcopy(fixture_plan())
        planned["payload"]["data"][key] *= assurance.MAX_NODES + 1
        with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
            assurance.new_history(reseal(planned))
    nested = []
    for _ in range(50):
        nested = [nested]
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        assurance.validate_artifact({"nested": nested})


def test_response_observation_must_occur_in_bound_result_evidence():
    planned = fixture_plan(findings=True, contradiction=True)
    history = assurance.new_history(planned)
    for index, kind in enumerate(assurance.KINDS, 1):
        result = supplied_result(history, kind)
        result["evidence"][0]["source"] = "Unrelated procedure report"
        history = assurance.ingest_result(history, manifest(), event_id(index), result)
    with pytest.raises(core.Rejected, match="FINDING_SOURCE"):
        assurance.reconcile(history, manifest(), response_dispositions(history))


def test_disposition_cannot_use_superseded_result_even_when_replacement_passes():
    history = complete(fixture_plan(findings=True, contradiction=True))
    dispositions = response_dispositions(history)
    previous = assurance.fold_events(history)["latest_results"]["technical_verification"]
    result = supplied_result(history, "technical_verification", suffix="-retry")
    history = assurance.ingest_result(
        history, manifest(), event_id(10), result, previous_result=previous
    )
    data = assurance.reconcile(history, manifest(), dispositions)["payload"]["data"]
    assert not any(item["current"] for item in data["disposition_ledger"])
    assert data["recommendation"] == "BLOCKED"


def test_delimiter_in_original_lane_and_finding_ids_does_not_lose_original():
    review_plan, outputs, _ = review_fixture(findings=True)
    lanes = review_plan["payload"]["data"]["lanes"]
    lanes[0]["id"] = "000/Policy"
    review_plan = review.review_plan(
        manifest(), lanes, ["correctness"], ["correctness"], clock=clock
    )
    supplied = []
    for output in outputs:
        data = output["payload"]["data"]
        findings = copy.deepcopy(data["findings"])
        if data["lane"] == "000":
            findings[0]["id"] = "nested/concern"
        supplied.append(
            review.lane_output(
                review_plan,
                "000/Policy" if data["lane"] == "000" else data["lane"],
                data["source"],
                findings,
                clock=clock,
            )
        )
    base = fixture_plan()
    original = review.reconcile(review_plan, supplied, [], clock=clock)["payload"]["data"]
    requirements = [
        {"finding": key, "requirement_digest": core.digest(value)}
        for key, value in original["findings"].items()
    ]
    nodes = copy.deepcopy(base["payload"]["data"]["nodes"])
    for node in nodes:
        node["finding_requirements"] = requirements
    planned = assurance.assurance_plan(
        review_plan, supplied, [], base["payload"]["data"]["procedures"], nodes, clock=clock
    )
    history = complete(planned)
    disposition = response_dispositions(history)[0]
    disposition["finding"] = "000/Policy/nested/concern"
    disposition["evidence"]["finding_id"] = "nested/concern"
    result = assurance.reconcile(history, manifest(), [disposition])["payload"]["data"]
    assert result["disposition_ledger"][0]["current"] is True
    assert "dissent/concern" in result["original_review"]["findings"]
