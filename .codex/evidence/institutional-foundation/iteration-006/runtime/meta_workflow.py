"""Fixed coordinator adapter: actual analytical JSON is data, never executed."""

from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.metadata as metadata
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

OUT = Path(__file__).resolve().parent
ROOT = Path("/home/runner/work/_codex_/_codex_")
PRIOR = ROOT / ".codex/evidence/institutional-foundation/iteration-005"
SOURCE = "fa2e6e406f5767fd8ab5a15ffc99b49f9123f71c"
WHEEL = "08fe4659b7338d8f8cf161da8c1cca31700d35e1dfa6832983fefa20f2e4cb00"
CHECKS: list[str] = []


def guard(event, args):
    if event.startswith("socket.") or event in {
        "subprocess.Popen",
        "os.system",
        "os.posix_spawn",
        "os.posix_spawnp",
    }:
        raise OSError("Runtime network and subprocess operations denied")


sys.addaudithook(guard)

from codex.institutional import assurance, core, review, storage  # noqa: E402


def load(path):
    return json.loads(path.read_bytes())


def save(name, value):
    (OUT / name).write_bytes(core.canonical(value) + b"\n")


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)


def main():
    environment = {
        "cwd": str(Path.cwd()),
        "prefix": sys.prefix,
        "python": sys.version,
        "execution_location": "Inside checkout; not outside-checkout execution",
        "PYTHONPATH": os.environ.get("PYTHONPATH"),
        "origins": {
            name: str(Path(module.__file__).resolve())
            for name, module in (
                ("assurance", assurance),
                ("core", core),
                ("review", review),
                ("storage", storage),
            )
        },
        "versions": {
            name: metadata.version(name)
            for name in (
                "codex-ml",
                "codex-contracts",
                "jsonschema",
                "jsonschema-specifications",
                "attrs",
                "referencing",
                "rpds-py",
                "typing-extensions",
            )
        },
        "scope": "SDK-only; same previously advisory-checked pinned versions",
        "G5": "NOT_RUN",
        "authority": "none",
    }
    check(sys.flags.isolated == 1 and "PYTHONPATH" not in os.environ, "isolated installed runtime")
    check(
        all(Path(p).is_relative_to(Path(sys.prefix)) for p in environment["origins"].values()),
        "all component imports from restored SDK environment",
    )
    direct = json.loads(metadata.distribution("codex-ml").read_text("direct_url.json"))
    check(direct["archive_info"]["hashes"]["sha256"] == WHEEL, "same exact noneditable wheel")
    save("meta-environment.json", environment)

    supplied = load(OUT / "repository-input.json")
    architecture = load(OUT.parent / "architecture-bearing.json")
    verification = load(OUT.parent / "verification-bearing.json")
    dissent = load(OUT.parent / "dissent-bearing.json")
    raw = {}
    for name in ("architecture-bearing.json", "verification-bearing.json", "dissent-bearing.json"):
        raw[name] = hashlib.sha256((OUT.parent / name).read_bytes()).hexdigest()
        check(
            raw[name] == supplied["context"]["analytical_receipts_sha256"][name],
            "actual analytical bytes preserved " + name,
        )
    check(
        [lane["actor"] for lane in supplied["lanes"]]
        == ["rd6-architecture", "rd6-snapshot", "rd6-dissent"],
        "actual dispatched analyst identities",
    )
    check(
        verification["G5"] == "NOT_RUN" and dissent["lane_constraints"]["G5"] == "NOT_RUN",
        "analytical roles remain unverified not independent reproduction",
    )
    context = copy.deepcopy(supplied["context"])
    context["security_limits"] = {
        "status": "OPEN_TRIAGE_NOT_CLEARED",
        "reported_archive_scan_findings": 13,
        "source": "Coordinator message 2026-10-25T03:18:35.547+00:00",
        "candidate_scope": "Four candidate SDK files are not the reported affected files; formulas outside candidate",
        "classification": "Reported triage observations, not independently verified vulnerabilities by runtime lane",
    }
    context["meta_scope"] = (
        "Only the attachment-validator subcase may be rejected; broad generic admission remains open"
    )
    files = []
    for item in supplied["files"]:
        content = (OUT / "immutable-source" / item["path"]).read_bytes()
        check(
            hashlib.sha256(content).hexdigest() == item["sha256"],
            "fixed four-file source " + item["path"],
        )
        files.append(
            {"path": item["path"], "content": content, "kind": "file", "mode": item["mode"]}
        )
    check(len(files) == 4 and supplied["source_commit"] == SOURCE, "fixed candidate fa2 four files")
    manifest = review.candidate_manifest(files, context)
    lanes = copy.deepcopy(supplied["lanes"])
    lanes.append(
        {
            "id": "rotated-meta",
            "bearing": "Reasoning integrity",
            "actor": "rd6-runtime",
            "run": "iteration006:rotated-meta-actual-admission",
            "dissent": False,
            "required": False,
            "coverage": supplied["mandatory"],
            "tools": ["read", "search"],
        }
    )
    planned = review.review_plan(manifest, lanes, supplied["mandatory"], supplied["critical"])
    outputs = []
    broad_quote = architecture["initial_to_meta_proposal"]["initial"]["hypothesis_quote"]
    narrow = {
        "id": "H1-attach-only",
        "source_quote": broad_quote,
        "normalized": "Scope-limited subcase only: cached-string substitution on assurance.attach_continuation / assurance.validate_artifact",
        "kind": "inference",
        "confidence": 0.4,
        "coverage": supplied["mandatory"],
        "clearance_conditions": [
            architecture["initial_to_meta_proposal"]["initial"]["clearance_conditions"][0]
        ],
    }
    for item in supplied["analytical_outputs"]:
        findings = copy.deepcopy(item["findings"])
        for finding in findings:
            if finding["id"] == "H1-broad":
                finding["confidence"] = 0.4 if item["lane"] == "090" else 0.5
        if item["lane"] == "090":
            findings.append(narrow)
        outputs.append(review.lane_output(planned, item["lane"], item["source"], findings))
    initial = review.reconcile(planned, outputs, supplied["relations"], stage="initial")
    reason = architecture["initial_to_meta_proposal"]["meta"]["disposition_reason"]
    observation = load(OUT / "admission-observation.json")
    actual_check = "semantic assurance validator rejects false cached recommendation"
    check(
        actual_check in observation["checks"],
        "actual new executed check supports only narrow response",
    )
    response_source = "\n".join(
        [
            "Actual rd6-runtime coordinator followup; same platform, not independent reproduction.",
            "Original analyst-authored hypothesis, not a repository code quote: " + broad_quote,
            narrow["normalized"],
            reason,
            actual_check,
            dissent["narrow_attach_path_counterevidence"]["claim"],
            "Citations: assurance.py:808-809,823-824; generic path remains core.py:373-384; contracts.json:5-13.",
            "Executed observation uses deliberately invalid synthetic input to test actual installed component behavior.",
            "Broad dissent, retention gap and security triage remain unresolved.",
        ]
    )
    followup = review.lane_output(planned, "rotated-meta", response_source, [copy.deepcopy(narrow)])
    original = next(o for o in outputs if o["payload"]["data"]["lane"] == "090")
    response_evidence = {
        "original_output": core.digest(original),
        "finding_id": narrow["id"],
        "followup_output": core.digest(followup),
        "checks": [
            {
                "condition": narrow["clearance_conditions"][0],
                "observation": actual_check,
                "source_quote": actual_check,
            }
        ],
    }
    adequacy = review.remediation_adequacy(
        planned, original, narrow["id"], followup, response_evidence
    )
    meta = review.reconcile(planned, [*outputs, followup], supplied["relations"], stage="meta")
    check(
        "dissent/H1-broad" in meta["payload"]["data"]["findings"],
        "rotated meta retains broad minority finding",
    )
    baseline = initial["payload"]["data"]["findings"]
    requirement = {
        "finding": "090/H1-attach-only",
        "requirement_digest": core.digest(baseline["090/H1-attach-only"]),
    }
    procedures = [
        {
            "id": "actual-installed-semantic-observation",
            "version": "1",
            "kind": "technical_verification",
            "expected_outputs": ["admission-observation"],
        },
        {
            "id": "open-retention-security",
            "version": "1",
            "kind": "institutional_audit",
            "expected_outputs": ["actual-resolution-receipt"],
        },
    ]
    nodes = []
    for identifier, kind, blocked, procedure, expected, refs in (
        (
            "technical_verification",
            "technical_verification",
            False,
            procedures[0]["id"],
            procedures[0]["expected_outputs"],
            [requirement],
        ),
        (
            "retention_security",
            "institutional_audit",
            True,
            procedures[1]["id"],
            procedures[1]["expected_outputs"],
            [],
        ),
    ):
        nodes.append(
            {
                "id": identifier,
                "kind": kind,
                "depends_on": [],
                "requirement": "blocked" if blocked else "required",
                "rationale": (
                    "Open 151-log retention and 13-finding security triage"
                    if blocked
                    else "Actual iteration006 installed API observation, not historical 107 tests"
                ),
                "role": kind,
                "actor": "coordinator" if blocked else "rd6-runtime",
                "identity_assurance": "unverified",
                "independence": "fixture-only",
                "procedure": {"id": procedure, "version": "1"},
                "environment_digest": core.digest(environment),
                "expected_outputs": expected,
                "resource_caps": {"max_bytes": 65536, "max_attempts": 3},
                "finding_requirements": refs,
                "evidence_requirements": [procedure],
                "pending": "Supply genuine bound observations, not a clearance flag",
                "recovery": "Existing coordinator validation and candidate association; no new agent",
            }
        )
    aplan = assurance.assurance_plan(planned, outputs, supplied["relations"], procedures, nodes)
    history = assurance.new_history(aplan)
    dispatch = assurance.resume(history, manifest, "technical_verification")
    node = nodes[0]
    result = {
        "node_id": node["id"],
        "plan_digest": core.digest(aplan),
        "binding": aplan["payload"]["data"]["binding"],
        "procedure": node["procedure"],
        "environment_digest": node["environment_digest"],
        "actor": "rd6-runtime",
        "identity_assurance": "unverified",
        "outcome": "PASS",
        "outputs": node["expected_outputs"],
        "bytes_used": len(response_source.encode()),
        "prerequisites": dispatch["prerequisites"],
        "evidence": [
            {
                "id": "actual-narrow-semantic-check",
                "source": response_source + "\nObserved result digest: " + core.digest(observation),
                "provenance": "unverified",
                "authority": "none",
                "status": "ACTIVE",
                "applicability": "applicable",
                "eligibility": "eligible",
                "critical": True,
                "requirements": node["evidence_requirements"],
                "finding_requirements": [requirement],
            }
        ],
    }
    history = assurance.ingest_result(history, manifest, str(uuid4()), result)
    state = assurance.fold_events(history)
    dispositions = [
        {
            "finding": ref,
            "route": "retain",
            "rationale": "Unresolved genuine concern; no broad rejection",
        }
        for ref in baseline
        if ref != "090/H1-attach-only"
    ]
    dispositions.append(
        {
            "finding": "090/H1-attach-only",
            "disposition": "REJECTED_WITH_EVIDENCE",
            "route": "nonmutating",
            "disposition_reason": reason,
            "followup": followup,
            "evidence": response_evidence,
            "result_digest": state["latest_results"]["technical_verification"],
            "evidence_id": "actual-narrow-semantic-check",
            "dissent": {
                "source_quote": broad_quote,
                "response": "Scope is the explicitly normalized attachment-validator subcase only; broad dissent retained unresolved.",
            },
        }
    )
    final = assurance.reconcile(history, manifest, dispositions)
    data = final["payload"]["data"]
    check(data["recommendation"] == "BLOCKED", "final source-backed assurance BLOCKED")
    check(
        "finding:090/H1-attach-only" not in data["blockers"],
        "narrow subcase receives bound nonmutating recommendation",
    )
    check(
        "finding:090/H1-broad" in data["blockers"]
        and "finding:dissent/H1-broad" in data["blockers"],
        "broad original claim and minority dissent remain unresolved",
    )
    check(
        data["limits"]["fixture_only"] is True
        and data["limits"]["approval"] is False
        and data["limits"]["activation"] is False,
        "no approval independence or activation",
    )
    proposal = {
        "type": "Scope-limited analytical remediation proposal, not an authorized adjudication",
        "reason": reason,
        "narrow_finding": "090/H1-attach-only",
        "broad_findings_retained": ["090/H1-broad", "dissent/H1-broad"],
        "runtime_changes": False,
        "new_agent": False,
    }
    artifacts = {
        "meta-manifest.json": manifest,
        "meta-review-plan.json": planned,
        "meta-initial.json": initial,
        "meta-remediation-proposal.json": proposal,
        "meta-rotated-followup.json": followup,
        "meta-adequacy.json": adequacy,
        "meta-review.json": meta,
        "meta-assurance-plan.json": aplan,
        "meta-assurance-dispatch.json": dispatch,
        "meta-assurance-result.json": result,
        "meta-assurance-history.json": history,
        "meta-assurance-cache.json": state,
        "meta-assurance-readiness.json": assurance.readiness(history, manifest),
        "meta-assurance-final.json": final,
    }
    for name, artifact in artifacts.items():
        save(name, artifact)
    checkpoint = json.loads(gzip.decompress((PRIOR / "continuation.json.gz").read_bytes()))
    review_attachments = [manifest, planned, *outputs, initial, followup, meta]
    preview = review.attach_continuation(checkpoint, review_attachments)
    preview = assurance.attach_continuation(preview, [aplan, history, final])
    check(
        preview["extensions"] == checkpoint["extensions"],
        "all new attachments validated by public helpers",
    )
    save(
        "meta-reasoning-map.json",
        {
            "raw_analytical_sha256": raw,
            "finding_quote_origin": {
                "090/H1-broad": "architecture-bearing.json#/initial_to_meta_proposal/initial/hypothesis_quote",
                "090/H1-attach-only": "Same exact analyst-authored hypothesis quote, separate coordinator-selected narrow normalization; not invented code quotation",
                "dissent/H1-broad": "dissent-bearing.json#/quoted_initial_hypothesis/text",
            },
            "normalization_scope": "Narrow H1-attach-only does not replace broad H1-broad",
            "numeric_confidence_policy": "Coordinator maps speculative architecture hypotheses to 0.4 and unresolved broad dissent hypothesis to 0.5; residual source-based concerns remain 0.9. These normalization numbers are not original analyst numerical claims. Original qualitative confidence and observed/inference limits remain in raw analytical records.",
            "meta_response": "architecture-bearing.json#/initial_to_meta_proposal/meta/disposition_reason",
            "actual_check_result": {
                "path": str(OUT / "admission-observation.json"),
                "digest": core.digest(observation),
                "scope": "New iteration006 checks; historical 107 cases not rerun or counted",
            },
            "co_stored_artifacts": "UNBOUND_TO_CONTINUATION_INVENTORY",
            "context": context,
            "preview_only_no_checkpoint_written": True,
            "institutional_followup": "Enhance existing coordinator semantic validation/candidate association with acceptance tests; no new agent",
        },
    )
    save(
        "meta-completion.json",
        {
            "status": "EXECUTED_INITIAL_PROPOSAL_ROTATED_META_ASSURANCE_RESULT_FINAL_BLOCKED",
            "checks": CHECKS,
            "check_count": len(CHECKS),
            "new_procedure_execution": "NOT_RUN_BY_RECONCILER; coordinator ingests actual retained iteration006 observation",
            "history_digest": core.digest(history),
            "final_digest": core.digest(final),
            "preview_digest": core.digest(preview),
            "pending_node": state["pending_node"],
            "blockers": data["blockers"],
            "historical_tests_rerun": 0,
            "storage_apply": "NOT_CALLED",
            "G5": "NOT_RUN",
            "approval": False,
            "activation": False,
            "fixture_only": True,
        },
    )
    print(
        json.dumps(
            {
                "status": "PASS_FINAL_BLOCKED",
                "checks": len(CHECKS),
                "pending": state["pending_node"],
            }
        )
    )


if __name__ == "__main__":
    main()
