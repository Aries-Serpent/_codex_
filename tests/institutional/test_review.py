"""Reusable offline SDK fixtures; source identities are claims, not independence."""

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

from codex.institutional import core, review, storage

NOW = datetime(2026, 10, 25, tzinfo=timezone.utc)


def clock():
    return NOW


def event_id(number):
    return str(UUID(f"00000000-0000-4000-8000-{number:012x}"))


def reseal(value):
    value = copy.deepcopy(value)
    value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    return value


def manifest(content=b"raw\r\n", context=None, mode=0o644):
    return review.candidate_manifest(
        [{"path": "src/a.py", "content": content, "kind": "file", "mode": mode}],
        context or {"policy": "fixture-only", "actor": "implementer"},
        clock=clock,
    )


def lanes():
    return [
        {
            "id": name,
            "bearing": bearing,
            "actor": "same-platform:" + name,
            "run": "fixture-run:" + name,
            "dissent": name == "dissent",
            "required": name != "rotated",
            "coverage": ["correctness", "security"],
            "tools": ["read", "search"],
        }
        for name, bearing in [
            ("logic", "correctness"),
            ("risk", "security"),
            ("dissent", "cross-cutting"),
            ("rotated", "followup"),
        ]
    ]


def plan():
    return review.review_plan(
        manifest(), lanes(), ["correctness", "security"], ["security"], clock=clock
    )


def finding():
    return {
        "id": "f1",
        "source_quote": "original wording",
        "normalized": "Retained risk",
        "kind": "inference",
        "confidence": 0.4,
        "coverage": ["security"],
        "clearance_conditions": ["reproduce"],
    }


def outputs(planned):
    return [
        review.lane_output(
            planned,
            name,
            f"{name}: original wording; reproduced fixture observation",
            [finding()],
            clock=clock,
        )
        for name in ("logic", "risk", "dissent", "rotated")
    ]


def fixture_review():
    """Deterministic end-to-end fixture reusable against an installed package."""
    planned = plan()
    supplied = outputs(planned)
    relation = {"type": "contradicts", "from": "logic/f1", "to": "dissent/f1"}
    recommendation = review.reconcile(planned, supplied[:3], [relation], clock=clock)
    history = review.new_history(planned, clock=clock)
    history = review.append_event(history, event_id(1), "advance", {"to": "meta"}, clock=clock)
    blocker = copy.deepcopy(recommendation["payload"]["data"]["blockers"][0])
    blocker["blocked_from_state"] = "meta"
    history = review.append_event(history, event_id(2), "block", blocker, clock=clock)
    resumed = review.resume(
        history, manifest(), event_id(3), blocker["clearance_conditions"], clock=clock
    )
    return planned, supplied, recommendation, history, resumed


def test_deterministic_end_to_end_preserves_dissent_and_pending_requirement():
    first = fixture_review()
    assert first == fixture_review()
    planned, supplied, recommendation, history, resumed = first
    data = recommendation["payload"]["data"]
    assert data["authorization"] == "none"
    assert data["classification"] == "Repository-Internal"
    assert data["independence"] == "unverified"
    assert data["blockers"][0]["cause"] == "unresolved-conflict"
    assert data["findings"]["logic/f1"]["source"] == supplied[0]["payload"]["data"]["source"]
    assert data["findings"]["logic/f1"]["normalized"] == "Retained risk"
    assert review.fold_events(history)["state"]["blocker"] is not None
    state = review.fold_events(resumed)["state"]
    assert state == {"stage": "meta", "blocker": None, "pending_requirement": "resolve-conflict"}
    assert planned["payload"]["data"]["coordinator_role"] == "implementer"
    assert history != resumed


@pytest.mark.parametrize("kind", ["symlink", "submodule", "archive-expanded", "directory"])
def test_manifest_rejects_unsupported_kinds(kind):
    with pytest.raises(core.Rejected, match="UNSUPPORTED_FILE_KIND"):
        review.candidate_manifest(
            [{"path": "x", "content": b"x", "kind": kind, "mode": 0o644}], {"a": 1}
        )


@pytest.mark.parametrize("path", ["/x", "../x", "a/../x", "a//x", "./x", "a\\x", "c:x", "a\nx"])
def test_manifest_rejects_non_normal_relative_paths(path):
    with pytest.raises(core.Rejected, match="REVIEW_PATH"):
        review.candidate_manifest(
            [{"path": path, "content": b"x", "kind": "file", "mode": 0o644}], {"a": 1}
        )


@pytest.mark.parametrize("mode", [-1, 0o1000, True, "644"])
def test_manifest_explicit_permissions(mode):
    with pytest.raises(core.Rejected, match="REVIEW_MODE"):
        manifest(mode=mode)


def test_manifest_exact_raw_bytes_metadata_and_context():
    a = manifest()
    assert a != manifest(b"raw\n")
    assert a != manifest(context={"policy": "changed"})
    assert a != manifest(mode=0o600)
    files = [
        {"path": path, "content": b"same hardlink bytes", "kind": "file", "mode": 0o644}
        for path in ["a", "b"]
    ]
    data = review.candidate_manifest(files, {"fixture": 1})["payload"]["data"]
    assert data["entries"][0]["sha256"] == data["entries"][1]["sha256"]
    for bad in (files[::-1], files + [files[0]], [], files * 200):
        with pytest.raises(core.Rejected):
            review.candidate_manifest(bad, {"fixture": 1})
    with pytest.raises(core.Rejected, match="RESOURCE_LIMIT"):
        manifest(b"x" * (review.MAX_BYTES + 1))
    with pytest.raises(core.Rejected, match="REVIEW_BYTES"):
        manifest("not bytes")
    with pytest.raises(core.Rejected, match="REVIEW_CONTEXT"):
        review.candidate_manifest(files, {})


@pytest.mark.parametrize(
    "change",
    [
        lambda x: x[0].update(tools=["write"]),
        lambda x: x[0].update(tools=["read", "execute"]),
        lambda x: x[1].update(id="logic"),
        lambda x: x[1].update(bearing="correctness"),
        lambda x: x[2].update(dissent=False),
        lambda x: x[2].update(required=False),
        lambda x: x[2].update(coverage=["security"]),
        lambda x: x[0].update(actor=""),
        lambda x: x[0].update(required="yes"),
        lambda x: x[0].update(coverage=["unknown"]),
        lambda x: x[0].update(extra="ignored"),
    ],
)
def test_adversarial_plan(change):
    declared = lanes()
    change(declared)
    with pytest.raises(core.Rejected):
        review.review_plan(manifest(), declared, ["correctness", "security"], ["security"])


def test_plan_bounds_modes_and_coverage():
    for declared in [lanes()[:2], lanes() * 5]:
        with pytest.raises(core.Rejected, match="LANE_LIMIT"):
            review.review_plan(manifest(), declared, ["security"], [])
    for mode in ["implicit", "approve", "FIXED"]:
        with pytest.raises(core.Rejected):
            review.review_plan(manifest(), lanes(), ["correctness", "security"], [], mode=mode)
    with pytest.raises(core.Rejected, match="CRITICAL_COVERAGE"):
        review.review_plan(manifest(), lanes(), ["correctness", "security"], ["unknown"])
    declared = lanes()
    declared[0]["coverage"] = declared[1]["coverage"] = ["security"]
    with pytest.raises(core.Rejected, match="MANDATORY_COVERAGE"):
        review.review_plan(manifest(), declared, ["correctness", "security"], [])
    assert (
        review.review_plan(manifest(), lanes(), ["correctness", "security"], [], mode="replace")[
            "payload"
        ]["data"]["mode"]
        == "replace"
    )


@pytest.mark.parametrize(
    "change",
    [
        lambda f: f.update(kind="fact"),
        lambda f: f.update(confidence=True),
        lambda f: f.update(confidence=-0.1),
        lambda f: f.update(confidence=1.1),
        lambda f: f.update(source_quote="invented quote"),
        lambda f: f.update(coverage=["unknown"]),
        lambda f: f.update(clearance_conditions=[]),
        lambda f: f.update(adequate=True),
    ],
)
def test_output_rejects_invalid_normalization(change):
    f = finding()
    change(f)
    with pytest.raises(core.Rejected):
        review.lane_output(plan(), "logic", "original wording", [f])


@pytest.mark.parametrize(
    "confidence", [10**400, -(10**400)], ids=["oversized-positive", "oversized-negative"]
)
def test_huge_integer_confidence_rejected_in_lane_and_import(confidence):
    planned = plan()
    bad_finding = finding()
    bad_finding["confidence"] = confidence
    with pytest.raises(core.Rejected, match="REVIEW_CONFIDENCE"):
        review.lane_output(planned, "logic", "original wording", [bad_finding])
    imported = outputs(planned)[0]
    imported["payload"]["data"]["findings"][0]["confidence"] = confidence
    with pytest.raises(core.Rejected, match="REVIEW_CONFIDENCE"):
        review.reconcile(planned, [reseal(imported)], [])


def test_output_binding_source_schema_identity_and_missing_lanes():
    planned = plan()
    supplied = outputs(planned)
    before = copy.deepcopy(supplied)
    result = review.reconcile(planned, supplied[:1], [], clock=clock)
    assert supplied == before
    assert {b["pending_requirement"] for b in result["payload"]["data"]["blockers"]} == {
        "lane:risk",
        "lane:dissent",
    }
    with pytest.raises(core.Rejected, match="DUPLICATE_LANE"):
        review.reconcile(planned, [supplied[0], supplied[0]], [])
    with pytest.raises(core.Rejected, match="UNDECLARED_LANE"):
        review.lane_output(planned, "undeclared", "original wording", [])
    with pytest.raises(core.Rejected, match="DUPLICATE_FINDING"):
        review.lane_output(planned, "logic", "original wording", [finding(), finding()])
    for field, value, reason in [
        ("binding", "a" * 64, "MIXED_BINDING"),
        ("plan_digest", "b" * 64, "MIXED_BINDING"),
        ("lane", "other", "UNDECLARED_LANE"),
        ("actor", "verified", "ATTRIBUTION"),
        ("identity", "authenticated", "ATTRIBUTION"),
        ("run", "other", "ATTRIBUTION"),
    ]:
        poisoned = copy.deepcopy(supplied[0])
        poisoned["payload"]["data"][field] = value
        with pytest.raises(core.Rejected, match=reason):
            review.reconcile(planned, [reseal(poisoned)], [])
    unknown = copy.deepcopy(supplied[0])
    unknown["schema"] = "codex.review.v2"
    with pytest.raises(core.Rejected, match="UNSUPPORTED_SCHEMA"):
        review.reconcile(planned, [reseal(unknown)], [])
    for stage in ("approve", "accepted"):
        with pytest.raises(core.Rejected, match="REVIEW_STAGE"):
            review.reconcile(planned, supplied, [], stage=stage)


@pytest.mark.parametrize("relation_type", sorted(review.RELATIONS))
def test_typed_relations_keep_all_findings(relation_type):
    planned = plan()
    result = review.reconcile(
        planned,
        outputs(planned),
        [{"type": relation_type, "from": "logic/f1", "to": "dissent/f1"}],
    )["payload"]["data"]
    assert len(result["findings"]) == 4
    assert bool(result["blockers"]) == (relation_type == "contradicts")


@pytest.mark.parametrize(
    "relation",
    [
        {"type": "approves", "from": "logic/f1", "to": "dissent/f1"},
        {"type": "equivalent", "from": "logic/f1", "to": "missing"},
        {"type": "equivalent", "from": "logic/f1", "to": "logic/f1"},
        {"type": "equivalent", "from": "logic/f1", "to": "dissent/f1", "execute": True},
    ],
)
def test_relations_reject_invalid_refs_or_types(relation):
    planned = plan()
    with pytest.raises(core.Rejected):
        review.reconcile(planned, outputs(planned), [relation])


def test_event_copy_order_cache_transitions_and_global_style_ids():
    planned, _, _, history, resumed = fixture_review()
    before = copy.deepcopy(resumed)
    final = review.append_event(resumed, event_id(4), "advance", {"to": "final"}, clock=clock)
    assert resumed == before
    cache = review.fold_events(final)
    assert review.fold_events(final, cache) == cache
    assert cache["state"]["stage"] == "final"
    for bad_cache in [{}, review.fold_events(history)]:
        with pytest.raises(core.Rejected, match="CACHE_MISMATCH"):
            review.fold_events(final, bad_cache)
    for identifier, action, detail in [
        (event_id(4), "advance", {"to": "meta"}),
        ("content-hash-not-event-id", "advance", {"to": "meta"}),
        (event_id(5), "approve", {}),
        (event_id(5), "advance", {"to": "initial"}),
    ]:
        with pytest.raises(core.Rejected):
            review.append_event(final, identifier, action, detail)
    with pytest.raises(core.Rejected, match="TRANSITION"):
        review.append_event(review.new_history(planned), event_id(9), "advance", {"to": "final"})
    for change in [
        lambda es: es.reverse(),
        lambda es: es.append(copy.deepcopy(es[0])),
        lambda es: es[0].update(sequence=2),
        lambda es: es[0].update(content_id="a" * 64),
        lambda es: es[0].update(binding="a" * 64),
    ]:
        bad = copy.deepcopy(history)
        change(bad["payload"]["data"]["events"])
        with pytest.raises(core.Rejected):
            review.fold_events(reseal(bad))
    assert (
        history["payload"]["data"]["events"][0]["event_id"]
        != history["payload"]["data"]["events"][0]["content_id"]
    )


def test_resume_requires_current_binding_exact_clearance_and_pending_state():
    _, _, _, history, _ = fixture_review()
    for changed in [manifest(b"new"), manifest(context={"policy": "new"}), manifest(mode=0o600)]:
        with pytest.raises(core.Rejected, match="STALE_BINDING"):
            review.resume(history, changed, event_id(10), ["finding-bound-evidence"])
    for conditions in [[], ["wrong"], ["finding-bound-evidence"]]:
        with pytest.raises(core.Rejected):
            review.resume(history, manifest(), event_id(10), conditions)
    with pytest.raises(core.Rejected, match="BLOCKED"):
        review.append_event(history, event_id(10), "advance", {"to": "final"})
    with pytest.raises(core.Rejected, match="TRANSITION"):
        review.resume(review.new_history(plan()), manifest(), event_id(10), ["x"])
    blocker = copy.deepcopy(history["payload"]["data"]["events"][-1]["data"])
    blocker["blocked_from_state"] = "final"
    with pytest.raises(core.Rejected, match="TRANSITION"):
        review.append_event(review.new_history(plan()), event_id(10), "block", blocker)


def remediation_evidence(original, followup):
    return {
        "original_output": core.digest(original),
        "finding_id": "f1",
        "followup_output": core.digest(followup),
        "checks": [
            {
                "condition": "reproduce",
                "observation": "reproduced fixture observation",
                "source_quote": "reproduced fixture observation",
            }
        ],
    }


def test_rotated_followup_adequacy_is_finding_bound_not_boolean():
    planned = plan()
    original, _, _, followup = outputs(planned)
    evidence = remediation_evidence(original, followup)
    result = review.remediation_adequacy(planned, original, "f1", followup, evidence)
    assert result["status"] == "evidence-coverage-only"
    assert result["original_actor"] != result["followup_actor"]
    assert result["identity"] == "unverified"
    for change in [
        lambda e: e.update(adequate=True),
        lambda e: e.update(original_output="a" * 64),
        lambda e: e.update(finding_id="other"),
        lambda e: e.update(followup_output="a" * 64),
        lambda e: e.update(checks=[]),
        lambda e: e["checks"][0].update(condition="other"),
        lambda e: e["checks"][0].update(observation="invented success"),
        lambda e: e["checks"][0].update(source_quote="not in source"),
        lambda e: e["checks"].append(copy.deepcopy(e["checks"][0])),
    ]:
        bad = copy.deepcopy(evidence)
        change(bad)
        with pytest.raises(core.Rejected):
            review.remediation_adequacy(planned, original, "f1", followup, bad)
    with pytest.raises(core.Rejected, match="ROTATION"):
        review.remediation_adequacy(planned, original, "f1", original, evidence)
    lost = copy.deepcopy(followup)
    lost["payload"]["data"]["findings"][0]["normalized"] = "different"
    lost = reseal(lost)
    with pytest.raises(core.Rejected, match="FINDING_LOSS"):
        review.remediation_adequacy(
            planned, original, "f1", lost, remediation_evidence(original, lost)
        )
    with pytest.raises(core.Rejected, match="FINDING_REFERENCE"):
        review.remediation_adequacy(planned, original, "unknown", followup, evidence)


def test_pure_reconciler_never_scans_executes_or_uses_network(monkeypatch):
    planned = plan()
    supplied = outputs(planned)

    def deny(*args, **kwargs):
        raise AssertionError("prohibited side effect")

    monkeypatch.setattr(builtins, "open", deny)
    monkeypatch.setattr(io, "open", deny)
    for name in ("rglob", "glob", "iterdir", "write_text", "write_bytes"):
        monkeypatch.setattr(Path, name, deny)
    monkeypatch.setattr(subprocess, "Popen", deny)
    monkeypatch.setattr(socket, "socket", deny)
    before = copy.deepcopy((planned, supplied))
    review.reconcile(planned, supplied, [], clock=clock)
    assert before == (planned, supplied)


@pytest.mark.parametrize(
    "change",
    [
        lambda v: v.update(authority_refs=["self-approved"]),
        lambda v: v.update(lifecycle="Active"),
        lambda v: v.update(created_at="yesterday"),
        lambda v: v.update(extensions={"execute": True}),
        lambda v: v.update(evidence_refs=["unbound"]),
        lambda v: v.update(validation_state="accepted"),
        lambda v: v.update(integrity="a" * 64),
        lambda v: v["producer"].update(assurance="authenticated"),
    ],
)
def test_pure_envelope_subset_cannot_inject_privileges(change):
    planned = plan()
    supplied = outputs(planned)
    bad = copy.deepcopy(supplied[0])
    change(bad)
    with pytest.raises(core.Rejected):
        review.reconcile(planned, [bad], [])


def test_continuation_uses_existing_draft_records_and_preserves_extensions(tmp_path):
    # Existing baseline core/storage integration only; SDK itself does no I/O.
    original = core.candidate(tmp_path, "fixture", clock)
    original["extensions"] = {"user": {"preserve": True}}
    original = reseal(original)
    before = copy.deepcopy(original)
    planned = plan()
    supplied = outputs(planned)
    recommendation = review.reconcile(planned, supplied, [], clock=clock)
    artifacts = [manifest(), planned, *supplied, recommendation, review.new_history(planned)]
    successor = review.attach_continuation(original, artifacts, clock=clock)
    assert original == before
    assert core.inspect_candidate(successor) == []
    assert successor["extensions"] == original["extensions"]
    assert successor["payload"]["predecessor"] == core.digest(original)
    assert successor["payload"]["sequence"] == 2
    assert successor["lifecycle"] == "Draft"
    with pytest.raises(core.Rejected, match="DUPLICATE"):
        review.attach_continuation(successor, [manifest()])
    with pytest.raises(core.Rejected, match="MISSING_PLAN"):
        review.attach_continuation(original, [outputs(plan())[0]])
    preview = storage.plan(tmp_path, original)
    storage.apply(tmp_path, original, preview)
    successor_preview = storage.plan(tmp_path, successor, core.digest(original))
    storage.apply(tmp_path, successor, successor_preview)
    persisted = core.load(tmp_path / core.NAMESPACE / "checkpoint.json")
    assert persisted == successor
    poisoned = copy.deepcopy(recommendation)
    poisoned["payload"]["data"]["authorization"] = "approved"
    with pytest.raises(core.Rejected, match="RECOMMENDATION_MISMATCH"):
        review.attach_continuation(original, [planned, reseal(poisoned)])


@pytest.mark.parametrize(
    "field,value",
    [
        ("rules", {}),
        ("classification", "Public"),
        ("context_digest", "bad"),
        ("entries", []),
    ],
)
def test_imported_manifest_cannot_bypass_validation(field, value):
    bad = manifest()
    bad["payload"]["data"][field] = value
    with pytest.raises(core.Rejected):
        review.review_plan(reseal(bad), lanes(), ["correctness", "security"], ["security"])


def test_reject_bad_structures_duplicate_relations_and_resource_bounds(monkeypatch):
    planned = plan()
    supplied = outputs(planned)
    for bad in (None, [], {"schema": []}):
        with pytest.raises(core.Rejected):
            review.reconcile(bad, [], [])
    relation = {"type": "equivalent", "from": "logic/f1", "to": "risk/f1"}
    with pytest.raises(core.Rejected, match="DUPLICATE_RELATION"):
        review.reconcile(planned, supplied, [relation, relation])
    for field in ("type", "from", "to"):
        bad_relation = {**relation, field: []}
        with pytest.raises(core.Rejected):
            review.reconcile(planned, supplied, [bad_relation])
    with pytest.raises(core.Rejected, match="FINDING_LIMIT"):
        review.lane_output(
            planned, "logic", "original wording", [finding()] * (review.MAX_FINDINGS + 1)
        )
    with pytest.raises(core.Rejected, match="LANE_LIMIT"):
        review.reconcile(planned, supplied * 5, [])
    history = review.new_history(planned, clock=clock)
    monkeypatch.setattr(review, "MAX_EVENTS", 0)
    with pytest.raises(core.Rejected, match="EVENT_LIMIT"):
        review.append_event(history, event_id(1), "advance", {"to": "meta"})


def test_direct_resume_event_cannot_omit_current_manifest():
    _, _, _, history, _ = fixture_review()
    blocker = review.fold_events(history)["state"]["blocker"]
    detail = {
        "blocker_digest": core.digest(blocker),
        "clearances": blocker["clearance_conditions"],
    }
    with pytest.raises(core.Rejected, match="REVIEW_FIELDS"):
        review.append_event(history, event_id(7), "resume", detail)
    detail["current_manifest"] = manifest(b"changed")
    with pytest.raises(core.Rejected, match="STALE_BINDING"):
        review.append_event(history, event_id(7), "resume", detail)
