"""Composed admission and recovery, also exercised from an isolated installed wheel."""

from __future__ import annotations

import copy
import gzip
import json
import os
from pathlib import Path

import pytest

from codex.institutional import admission, assurance, core, review, storage

from .test_assurance import (
    alter_status,
    clock,
    complete,
    event_id,
    fixture_plan,
    manifest,
    reseal,
    supplied_result,
)


def attached(root):
    (root / "candidate.py").write_bytes(b"candidate")
    (root / "candidate.py").chmod(0o644)
    original = core.candidate(root, "composed-admission", clock)
    history = complete()
    final = assurance.reconcile(history, manifest(), [], clock=clock)
    value = assurance.attach_continuation(original, [history, final], clock=clock)
    return original, value, history, final


def test_semantically_invalid_resealed_attachment_rejected_everywhere(tmp_path):
    original, value, _, _ = attached(tmp_path)
    bad = fixture_plan()
    bad["payload"]["data"]["limits"]["approval"] = True
    bad = reseal(bad)
    core.validate(bad)
    value["payload"]["records"].append(bad)
    value = reseal(value)
    assert any("ASSURANCE_AUTHORITY" in reason for reason in core.inspect_candidate(value))
    assert any("ASSURANCE_AUTHORITY" in reason for reason in core.verify(value, tmp_path))
    with pytest.raises(core.Rejected, match="ASSURANCE_AUTHORITY"):
        storage.plan(tmp_path, value)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    path = tmp_path / "import.json"
    path.write_bytes(core.canonical(value))
    original_bytes = path.read_bytes()
    with pytest.raises(core.Rejected, match="ASSURANCE_AUTHORITY"):
        core.load(path)
    assert core.load(path, inspection_only=True) == value
    assert path.read_bytes() == original_bytes
    path.write_bytes(core.canonical(bad))
    with pytest.raises(core.Rejected, match="ASSURANCE_AUTHORITY"):
        core.load(path)
    (tmp_path / core.NAMESPACE / "checkpoint.json").write_bytes(core.canonical(value))
    with pytest.raises(core.Rejected, match="ASSURANCE_AUTHORITY"):
        storage.recover(tmp_path)


def test_current_binding_is_explicit_scoped_and_non_authorizing(tmp_path):
    original, value, history, final = attached(tmp_path)
    before = copy.deepcopy(value)
    assert all(
        item["association"] == "unbound-diagnostic"
        for item in admission.inspect_associations(value)
    )
    bound = admission.bind(value, [history, final], root=tmp_path)
    assert value == before
    assert core.inspect_candidate(bound) == []
    assert core.verify(bound, tmp_path) == []
    assert all(
        item["association"] == "current-bound" and item["authority"] == "none"
        for item in admission.inspect_associations(bound)
    )
    assert bound["payload"]["gates"]["G5"] == "NOT_RUN"
    assert bound["payload"]["actors"]["activation"] == "unsupported"
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, bound, storage.plan(tmp_path, bound, core.digest(original)))
    assert storage.recover(tmp_path, core.digest(bound)) == bound


@pytest.mark.parametrize(
    "field",
    [
        "candidate_ref",
        "source_sha",
        "dirty_tree",
        "configuration_digest",
        "review_binding",
        "review_plan_digest",
        "artifact_digest",
    ],
)
def test_wrong_candidate_context_artifact_or_reference_rejected(tmp_path, field):
    _, value, history, _ = attached(tmp_path)
    bound = admission.bind(value, [history], root=tmp_path)
    bound["payload"]["assurance_bindings"][0][field] = "a" * 64
    bound = reseal(bound)
    assert any("ASSOCIATION_" in item for item in core.inspect_candidate(bound))
    with pytest.raises(core.Rejected, match="ASSOCIATION_"):
        storage.plan(tmp_path, bound)


def test_bound_source_drift_cannot_reach_plan_or_apply(tmp_path):
    original, value, history, _ = attached(tmp_path)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    bound = admission.bind(value, [history], root=tmp_path)
    preview = storage.plan(tmp_path, bound, core.digest(original))
    (tmp_path / "candidate.py").write_bytes(b"changed")
    with pytest.raises(core.Rejected, match="ASSOCIATION_SOURCE_DRIFT"):
        storage.plan(tmp_path, bound, core.digest(original))
    with pytest.raises(core.Rejected, match="ASSOCIATION_SOURCE_DRIFT"):
        storage.apply(tmp_path, bound, preview)
    assert storage.recover(tmp_path) == original


def test_foreign_manifest_is_diagnostic_only_and_cannot_bind(tmp_path):
    original = core.candidate(tmp_path, "legacy", clock)
    history = complete()
    value = assurance.attach_continuation(original, [history], clock=clock)
    assert core.inspect_candidate(value) == []
    assert admission.inspect_associations(value)[0]["association"] == "unbound-diagnostic"
    with pytest.raises(core.Rejected, match="SOURCE_UNAVAILABLE"):
        admission.bind(value, [history], root=tmp_path)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, value, storage.plan(tmp_path, value, core.digest(original)))
    assert storage.recover(tmp_path) == value


def test_dropped_history_rejected_and_original_bytes_preserved(tmp_path):
    original, value, _, _ = attached(tmp_path)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, value, storage.plan(tmp_path, value, core.digest(original)))
    new = copy.deepcopy(value)
    new["payload"].update(sequence=3, predecessor=core.digest(value))
    new["payload"]["records"] = [
        item for item in new["payload"]["records"] if item["schema"] != assurance.SCHEMA
    ]
    new = reseal(new)
    with pytest.raises(core.Rejected, match="REQUIRED_HISTORY_LOSS"):
        storage.plan(tmp_path, new, core.digest(value))
    assert storage.recover(tmp_path) == value


@pytest.mark.parametrize("mutation", ["missing", "substitution", "sequence", "extension"])
def test_recovery_rechecks_entire_retained_chain(tmp_path, mutation):
    original, value, _, _ = attached(tmp_path)
    original["extensions"] = {"protected": {"cache": "inert-data"}}
    original = reseal(original)
    value["payload"]["predecessor"] = core.digest(original)
    value["extensions"] = copy.deepcopy(original["extensions"])
    value = reseal(value)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, value, storage.plan(tmp_path, value, core.digest(original)))
    predecessor = tmp_path / core.NAMESPACE / f"previous-{core.digest(original)}.json"
    if mutation == "missing":
        predecessor.unlink()
    elif mutation == "substitution":
        changed = copy.deepcopy(original)
        changed["payload"]["session_id"] = "substituted"
        predecessor.write_bytes(core.canonical(reseal(changed)))
    else:
        changed = copy.deepcopy(value)
        if mutation == "sequence":
            changed["payload"]["sequence"] = 8
        else:
            changed["extensions"] = {}
        (predecessor.parent / "checkpoint.json").write_bytes(core.canonical(reseal(changed)))
    with pytest.raises(core.Rejected):
        storage.recover(tmp_path)


def test_fork_and_replayed_acceptance_rejected_against_retained_history(tmp_path):
    _, value, history, final = attached(tmp_path)
    revoked = alter_status(history)
    next_value = assurance.attach_continuation(value, [revoked], clock=clock)
    with pytest.raises(core.Rejected, match="STALE_HISTORY"):
        admission.bind(next_value, [final], root=tmp_path)
    current = admission.bind(next_value, [revoked], root=tmp_path)
    assert assurance.fold_events(revoked)["pending_node"] == "technical_verification"
    assert admission.inspect_associations(current)[-1]["association"] == "current-bound"
    fork = alter_status(history, status="DISPUTED", event=21)
    forked = assurance.attach_continuation(next_value, [fork], clock=clock)
    assert "ASSURANCE_HISTORY_FORK" in core.inspect_candidate(forked)


def test_explicit_rebinding_after_append_does_not_rewrite_old_observations(tmp_path):
    _, value, history, _ = attached(tmp_path)
    bound = admission.bind(value, [history], root=tmp_path)
    next_value = assurance.attach_continuation(bound, [alter_status(history)], clock=clock)
    assert "ASSOCIATION_STALE_HISTORY" in core.inspect_candidate(next_value)
    rebound = admission.bind(
        next_value, [next_value["payload"]["records"][-1]], root=tmp_path, replace=True
    )
    assert core.inspect_candidate(rebound) == []
    admission.transition(bound, rebound)
    assert history in rebound["payload"]["records"]


def test_cache_event_digest_and_invalid_fold_are_recomputed(tmp_path):
    _, value, history, _ = attached(tmp_path)
    cache = assurance.fold_events(history)
    cache["history_digest"] = "a" * 64
    with pytest.raises(core.Rejected, match="CACHE_MISMATCH"):
        assurance.fold_events(history, cache)
    cache = assurance.fold_events(history)
    cache["nodes"]["technical_verification"]["state"] = "APPROVED"
    with pytest.raises(core.Rejected, match="CACHE_MISMATCH"):
        assurance.fold_events(history, cache)
    bad = copy.deepcopy(history)
    bad["payload"]["data"]["events"][0]["digest"] = "a" * 64
    value["payload"]["records"].append(reseal(bad))
    assert any("EVENT_DIGEST" in finding for finding in core.inspect_candidate(reseal(value)))


def test_wholesale_reseal_needs_external_anchor_and_is_not_authentication(tmp_path):
    original, value, _, _ = attached(tmp_path)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    storage.apply(tmp_path, value, storage.plan(tmp_path, value, core.digest(original)))
    anchor = core.digest(value)
    replacement = core.candidate(tmp_path, "hostile-replacement", clock)
    (tmp_path / core.NAMESPACE / "checkpoint.json").write_bytes(core.canonical(replacement))
    assert storage.recover(tmp_path) == replacement
    with pytest.raises(core.Rejected, match="RECOVERY_ANCHOR_MISMATCH"):
        storage.recover(tmp_path, anchor)


def test_recovery_import_preserves_gzip_bytes_and_ordinary_candidate(tmp_path):
    value = core.candidate(tmp_path, "ordinary", clock)
    path = tmp_path / "legacy.json.gz"
    content = gzip.compress(core.canonical(value), mtime=0)
    path.write_bytes(content)
    assert core.load(path) == value
    assert path.read_bytes() == content
    assert admission.inspect_associations(value) == []
    assert json.loads(gzip.decompress(content)) == value


def test_replayed_result_cannot_be_new_acceptance():
    history = complete()
    result = supplied_result(assurance.new_history(fixture_plan()), "technical_verification")
    with pytest.raises(core.Rejected, match="DUPLICATE_RESULT"):
        assurance.ingest_result(
            history,
            manifest(),
            event_id(31),
            result,
            previous_result=core.digest(result),
            clock=clock,
        )


def source_workflow(root):
    """Exercise actual runtime bytes; all analysis is same-platform, not independent."""
    source = Path(core.__file__).read_bytes()
    (root / "core.py").write_bytes(source)
    (root / "core.py").chmod(0o644)
    context = {"scope": "core.inspect_candidate semantic dispatch", "authority": "none"}
    current = review.candidate_manifest(
        [{"path": "core.py", "content": source, "kind": "file", "mode": 0o644}],
        context,
        clock=clock,
    )
    lanes = [
        {
            "id": key,
            "bearing": bearing,
            "actor": "same-platform:coordinator",
            "run": "source-composition:" + key,
            "dissent": key == "dissent",
            "required": key != "rotated",
            "coverage": ["admission"],
            "tools": ["read", "search"],
        }
        for key, bearing in [
            ("architecture", "090"),
            ("verification", "180"),
            ("dissent", "cross-cutting"),
            ("rotated", "315-history"),
        ]
    ]
    planned = review.review_plan(current, lanes, ["admission"], ["admission"], clock=clock)
    quote = "validate_artifact(child)"
    assert quote.encode() in source
    finding = {
        "id": "semantic-dispatch",
        "source_quote": quote,
        "normalized": "Semantic dispatch is present; this alone is not authentication.",
        "kind": "inference",
        "confidence": 0.8,
        "coverage": ["admission"],
        "clearance_conditions": ["inspect-dispatch"],
    }
    exact_source = (
        "FACT: exact quotation from core.inspect_candidate: "
        + quote
        + "\nINFERENCE: scoped semantic dispatch is not whole-history authentication."
    )
    outputs = [
        review.lane_output(planned, key, exact_source, [finding], clock=clock)
        for key in ("architecture", "verification", "dissent")
    ]
    relations = [
        {
            "type": "contradicts",
            "from": "architecture/semantic-dispatch",
            "to": "dissent/semantic-dispatch",
        }
    ]
    initial = review.reconcile(planned, outputs, relations, clock=clock)
    rotated = review.lane_output(planned, "rotated", exact_source, [finding], clock=clock)
    adequacy = review.remediation_adequacy(
        planned,
        outputs[0],
        finding["id"],
        rotated,
        {
            "original_output": core.digest(outputs[0]),
            "finding_id": finding["id"],
            "followup_output": core.digest(rotated),
            "checks": [
                {"condition": "inspect-dispatch", "observation": quote, "source_quote": quote}
            ],
        },
    )
    meta = review.reconcile(planned, [*outputs, rotated], relations, stage="meta", clock=clock)
    template = fixture_plan()["payload"]["data"]
    nodes = copy.deepcopy(template["nodes"])
    for node in nodes:
        node["finding_requirements"] = [
            {"finding": key, "requirement_digest": core.digest(value)}
            for key, value in initial["payload"]["data"]["findings"].items()
        ]
    nodes[-1].update(requirement="blocked", rationale="Owner retention/security decisions absent")
    ap = assurance.assurance_plan(
        planned, outputs, relations, template["procedures"], nodes, clock=clock
    )
    history = assurance.new_history(ap, clock=clock)
    node = nodes[0]
    result = {
        "node_id": node["id"],
        "plan_digest": core.digest(ap),
        "binding": ap["payload"]["data"]["binding"],
        "procedure": node["procedure"],
        "environment_digest": node["environment_digest"],
        "actor": node["actor"],
        "identity_assurance": "unverified",
        "outcome": "PASS",
        "outputs": ["report"],
        "bytes_used": len(quote),
        "prerequisites": {},
        "evidence": [
            {
                "id": "source-dispatch",
                "source": exact_source,
                "provenance": "unverified",
                "authority": "none",
                "status": "ACTIVE",
                "applicability": "applicable",
                "eligibility": "eligible",
                "critical": True,
                "requirements": node["evidence_requirements"],
                "finding_requirements": node["finding_requirements"],
            }
        ],
    }
    history = assurance.ingest_result(history, current, event_id(80), result, clock=clock)
    final = assurance.reconcile(history, current, [], clock=clock)
    original = core.candidate(root, "source-backed-composition", clock)
    successor = assurance.attach_continuation(original, [ap, history, final], clock=clock)
    bound = admission.bind(successor, [history, final], root=root)
    storage.apply(root, original, storage.plan(root, original))
    storage.apply(root, bound, storage.plan(root, bound, core.digest(original)))
    assert storage.recover(root) == bound
    assert initial["payload"]["data"]["relations"] == meta["payload"]["data"]["relations"]
    assert final["payload"]["data"]["recommendation"] == "BLOCKED"
    assert adequacy["authorization"] == "none"
    assert assurance.resume(history, current, "independent_reproduction")["ready"]
    with pytest.raises(core.Rejected, match="PENDING"):
        assurance.resume(history, current, "institutional_audit")
    return {
        "manifest": current,
        "review_plan": planned,
        "outputs": outputs,
        "initial": initial,
        "response": rotated,
        "adequacy": adequacy,
        "meta": meta,
        "assurance_plan": ap,
        "history": history,
        "final": final,
        "bound_candidate": bound,
        "limits": "Same-platform source analysis and technical fixture; G5 NOT_RUN; no approval.",
    }


def test_source_backed_non_authorizing_workflow_and_exact_resume(tmp_path):
    source_workflow(tmp_path)


def test_chain_budget_denies_successor_before_store_becomes_unrecoverable(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "MAX_CHECKPOINTS", 2)
    original = core.candidate(tmp_path, "bounded-chain", clock)
    storage.apply(tmp_path, original, storage.plan(tmp_path, original))
    second = assurance.attach_continuation(original, [], clock=clock)
    storage.apply(tmp_path, second, storage.plan(tmp_path, second, core.digest(original)))
    third = assurance.attach_continuation(second, [], clock=clock)
    with pytest.raises(core.Rejected, match="BLOCKED_RESOURCE_LIMIT"):
        storage.plan(tmp_path, third, core.digest(second))
    assert storage.recover(tmp_path) == second


@pytest.mark.parametrize("replacement", ["symlink", "fifo", "race"])
def test_manifest_reads_are_descriptor_anchored_and_special_files_do_not_block(
    tmp_path, monkeypatch, replacement
):
    _, value, history, _ = attached(tmp_path)
    bound = admission.bind(value, [history], root=tmp_path)
    path = tmp_path / "candidate.py"
    if replacement == "race":
        original_open = os.open

        def raced_open(name, flags, *args, **kwargs):
            if name == "candidate.py":
                path.unlink()
                path.symlink_to(tmp_path / "outside")
            return original_open(name, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", raced_open)
    else:
        path.unlink()
        if replacement == "fifo":
            os.mkfifo(path)
        else:
            path.symlink_to(tmp_path / "outside")
    with pytest.raises(core.Rejected, match="ASSOCIATION_"):
        admission.inspect_associations(bound, tmp_path)
