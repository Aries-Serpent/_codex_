"""Installed-wheel supplied-data workflow; never execute imported fixture code."""

from __future__ import annotations

import copy
import gzip
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path("/home/runner/work/_codex_/_codex_")
OUT = Path(__file__).resolve().parent
BEFORE = ROOT / ".codex/evidence/institutional-foundation/iteration-005"
SOURCE = "fa2e6e406f5767fd8ab5a15ffc99b49f9123f71c"
WHEEL_SHA = "08fe4659b7338d8f8cf161da8c1cca31700d35e1dfa6832983fefa20f2e4cb00"
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


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)


def save(name, value):
    (OUT / name).write_bytes(core.canonical(value) + b"\n")


def load(path):
    return json.loads(path.read_bytes())


def rejected(call, reason, name):
    try:
        call()
    except core.Rejected as exc:
        check(reason in exc.reason, name)
    else:
        raise AssertionError(name)


def environment():
    origins = {
        name: str(Path(module.__file__).resolve())
        for name, module in (
            ("core", core),
            ("assurance", assurance),
            ("review", review),
            ("storage", storage),
        )
    }
    check(sys.flags.isolated == 1 and "PYTHONPATH" not in os.environ, "isolated runtime")
    check(sys.prefix != sys.base_prefix, "fresh virtual environment")
    check(
        all(Path(p).is_relative_to(Path(sys.prefix)) for p in origins.values()),
        "SDK imports originate in fresh installed environment",
    )
    url = json.loads(metadata.distribution("codex-ml").read_text("direct_url.json"))
    check(not url.get("dir_info", {}).get("editable", False), "noneditable wheel")
    check(url["archive_info"]["hashes"]["sha256"] == WHEEL_SHA, "exact retained wheel")
    versions = {
        name: metadata.version(name)
        for name in (
            "codex-ml",
            "codex-contracts",
            "jsonschema",
            "jsonschema-specifications",
            "referencing",
            "rpds-py",
            "attrs",
            "typing-extensions",
        )
    }
    save(
        "environment.json",
        {
            "scope": "SDK-only; historical full-base closure not rerun",
            "origins": origins,
            "versions": versions,
            "direct_url": url,
            "python": sys.version,
            "executable": sys.executable,
            "sys_path": sys.path,
            "cwd": str(Path.cwd()),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
            "guard": "Process-local audit hook denies sockets and subprocesses; not kernel isolation",
            "G5": "NOT_RUN",
            "authority": "none",
        },
    )


def synthetic():
    checkpoint = json.loads(gzip.decompress((BEFORE / "continuation.json.gz").read_bytes()))
    check(
        core.digest(checkpoint)
        == "e2ed9e24c5c7ea3f9e17745830059c39cb492fd2c8c478caeba5e1b2b145f12b",
        "exact sequence-five checkpoint",
    )
    fixture = load(BEFORE / "assurance-fixtures.json")["reopened_revoked"]["payload"]["data"]
    history = fixture["history"]
    manifest = fixture["current_manifest"]
    cache = load(BEFORE / "assurance-resume-cache.json")
    check(history in checkpoint["payload"]["records"], "retained exact history attachment")
    state = assurance.fold_events(history, cache)
    check(state["pending_node"] == "technical_verification", "exact pending technical node")
    dispatch = assurance.resume(history, manifest, "technical_verification")
    check(dispatch["ready"] and dispatch["prerequisites"] == {}, "technical dispatch prerequisites")
    save("input-history.json", history)
    save("input-manifest.json", manifest)
    save("input-cache.json", cache)
    save("input-dispositions.json", fixture["dispositions"])
    save("dispatch.json", dispatch)
    result = copy.deepcopy(history["payload"]["data"]["events"][0]["detail"]["result"])
    result["prerequisites"] = dispatch["prerequisites"]
    result["evidence"][0]["id"] = "fabricated-iteration006-retry"
    result["evidence"][0]["source"] = (
        "NEW FABRICATED synthetic fixture observation for iteration006 retry; "
        "not repository, wheel-test, scanner or production evidence; original concern; "
        "observed original reproduction; "
        "fixture reproduction does not substantiate original concern"
    )
    previous = state["latest_results"]["technical_verification"]
    check(
        previous == "cb5b179291c00e59dfe82129dfbca592cca02da6c9ac955180db4c1b51aa3452",
        "exact revoked result predecessor",
    )
    bad_cache = copy.deepcopy(cache)
    bad_cache["pending_node"] = "forged"
    rejected(
        lambda: assurance.fold_events(history, bad_cache),
        "CACHE_MISMATCH",
        "wrong replay cache rejected",
    )
    rejected(
        lambda: assurance.ingest_result(
            history, manifest, str(uuid4()), result, previous_result="0" * 64
        ),
        "RETRY_PREDECESSOR",
        "wrong retry predecessor rejected",
    )
    for label, current in (
        (
            "source",
            review.candidate_manifest(
                [{"path": "candidate.py", "content": b"changed", "kind": "file", "mode": 0o644}],
                {"purpose": "fixture"},
            ),
        ),
        (
            "context",
            review.candidate_manifest(
                [{"path": "candidate.py", "content": b"candidate", "kind": "file", "mode": 0o644}],
                {"purpose": "changed"},
            ),
        ),
    ):
        rejected(
            lambda: assurance.resume(history, current, "technical_verification"),
            "STALE_BINDING",
            label + " drift rejects exact resume",
        )
    event = str(uuid4())
    after = assurance.ingest_result(history, manifest, event, result, previous_result=previous)
    folded = assurance.fold_events(after)
    check(
        after["payload"]["data"]["events"][:-1] == history["payload"]["data"]["events"],
        "all original events and revocation preserved",
    )
    check(
        after["payload"]["data"]["plan"] == history["payload"]["data"]["plan"],
        "original findings dissent plan and candidate preserved",
    )
    check(
        folded["nodes"]["technical_verification"]["state"] == "PASSED",
        "new synthetic technical retry passes",
    )
    check(
        folded["evidence_states"][previous] == state["evidence_states"][previous],
        "revoked original evidence retained unchanged",
    )
    check(folded["result_statuses"][previous] == "SUPERSEDED", "old result superseded")
    for node in ("independent_reproduction", "institutional_audit"):
        check(
            "stale-prerequisite-binding" in folded["nodes"][node]["blockers"],
            node + " requires explicit downstream retry",
        )
    recommendation = assurance.reconcile(after, manifest, fixture["dispositions"])
    data = recommendation["payload"]["data"]
    check(data["recommendation"] == "BLOCKED", "downstream and old disposition bindings block")
    check(
        data["original_review"] == fixture["original_review"],
        "original review findings dissent and contradictions retained",
    )
    check(
        data["limits"]["approval"] is False
        and data["limits"]["activation"] is False
        and data["limits"]["authority"] == "none",
        "no approval activation or authority",
    )
    check(assurance.fold_events(after, folded) == folded, "exact after-cache replay")
    assurance.validate_artifact(recommendation)
    save("retry-result.json", result)
    save("after-history.json", after)
    save("after-cache.json", folded)
    save("after-readiness.json", assurance.readiness(after, manifest))
    save("final-recommendation.json", recommendation)
    save(
        "resumption.json",
        {
            "status": "PASS_NEW_SYNTHETIC_RETRY_DOWNSTREAM_REMAINS_BLOCKED",
            "scope": "New fabricated fixture observation only; no real tests bound to synthetic candidate",
            "previous_result": previous,
            "event_id": event,
            "history_before": core.digest(history),
            "history_after": core.digest(after),
            "plan_digest": core.digest(history["payload"]["data"]["plan"]),
            "binding": result["binding"],
            "pending_node": folded["pending_node"],
            "new_checks": CHECKS,
            "new_check_count": len(CHECKS),
            "historical_tests_rerun": 0,
            "G5": "NOT_RUN",
            "checkpoint_written": False,
            "extensions_preserved_by_no_checkpoint_mutation": True,
            "artifact_sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in OUT.glob("*.json")
                if p.name != "resumption.json"
            },
        },
    )


def repository():
    """Coordinator supplies immutable bytes and genuine analytical output JSON."""
    if not (OUT / "repository-input.json").exists():
        build_repository_input()
    supplied = load(OUT / "repository-input.json")
    check(supplied["source_commit"] == SOURCE, "exact immutable repository source")
    check(supplied["wheel_sha256"] == WHEEL_SHA, "same installed retained wheel")
    files = []
    expected = [
        "src/codex/institutional/" + name
        for name in ("assurance.py", "contracts.json", "core.py", "storage.py")
    ]
    check(
        sorted(item["path"] for item in supplied["files"]) == expected,
        "exact bounded repository candidate file list",
    )
    for item in sorted(supplied["files"], key=lambda x: x["path"]):
        source = OUT / "immutable-source" / item["path"]
        content = source.read_bytes()
        check(
            hashlib.sha256(content).hexdigest() == item["sha256"],
            "immutable supplied bytes " + item["path"],
        )
        files.append(
            {"path": item["path"], "content": content, "kind": "file", "mode": item["mode"]}
        )
    context = supplied["context"]
    check(
        context["source_commit"] == SOURCE and context["wheel_sha256"] == WHEEL_SHA,
        "repository context independently bound",
    )
    check(bool(context.get("retention_limits")), "explicit unresolved retention limits in context")
    manifest = review.candidate_manifest(files, context)
    plan = review.review_plan(
        manifest, supplied["lanes"], supplied["mandatory"], supplied["critical"]
    )
    outputs = []
    for item in supplied["analytical_outputs"]:
        outputs.append(review.lane_output(plan, item["lane"], item["source"], item["findings"]))
    recommendation = review.reconcile(plan, outputs, supplied["relations"], stage="final")
    initial = review.reconcile(plan, outputs, supplied["relations"], stage="initial")
    meta = review.reconcile(plan, outputs, supplied["relations"], stage="meta")
    save("repository-manifest.json", manifest)
    save("repository-plan.json", plan)
    save("repository-lane-outputs.json", outputs)
    save("repository-recommendation.json", recommendation)
    save("repository-initial.json", initial)
    save("repository-meta.json", meta)
    repository_assurance(manifest, plan, outputs, supplied["relations"], context)
    save(
        "repository-checks.json",
        {
            "checks": CHECKS,
            "G5": "NOT_RUN",
            "authority": "none",
            "retention_blocker": context["retention_limits"],
            "limits": {
                "fixture_only": True,
                "identity_assurance": "unverified",
                "observations": "Genuine supplied analytical wording, not fabricated observations",
                "generic_storage_admission": "Not semantic assurance validation or inventory association",
                "hostile_whole_history_reseal": "Unsupported",
            },
        },
    )


def build_repository_input():
    """Map actual analyst paragraphs verbatim; hypotheses are not code quotes."""
    architecture = load(OUT.parent / "architecture-bearing.json")
    verification = load(OUT.parent / "verification-bearing.json")
    dissent = load(OUT.parent / "dissent-bearing.json")
    areas = ["assurance-semantics", "trust-boundary"]
    lanes = [
        {
            "id": lane,
            "bearing": bearing,
            "actor": actor,
            "run": "iteration006:" + lane,
            "dissent": lane == "dissent",
            "required": True,
            "coverage": areas,
            "tools": ["read", "search"],
        }
        for lane, bearing, actor in (
            ("090", "Architecture", "rd6-architecture"),
            ("180", "Verification", "rd6-snapshot"),
            ("dissent", "cross-cutting", "rd6-dissent"),
        )
    ]

    def finding(identifier, quote, normalized, conditions):
        return {
            "id": identifier,
            "source_quote": quote,
            "normalized": normalized,
            "kind": "inference",
            "confidence": 0.9,
            "coverage": areas,
            "clearance_conditions": conditions,
        }

    findings = [
        finding(item["id"], item["observed"], item["inferred_risk"], [item["next_step"]])
        for item in architecture["residual_concerns"]
    ]
    broad = architecture["initial_to_meta_proposal"]["initial"]["hypothesis_quote"]
    findings.append(
        finding(
            "H1-broad",
            broad,
            dissent["quoted_initial_hypothesis"]["reasoning"],
            [
                "Evaluate generic structural admission separately from semantic assurance attachment."
            ],
        )
    )
    arch_source = json.dumps(
        {
            "attribution": "Actual rd6-architecture analytical wording; hypothesis is analyst prose, not code",
            "hypothesis": broad,
            "residual_concerns": architecture["residual_concerns"],
            "source_citations": {
                "semantic": "assurance.py:790-809,823-824",
                "generic": "core.py:373-384;contracts.json:5-13;storage.py:50-54",
                "binding": "assurance.py:276-283,818-840",
                "history": "assurance.py:519-524;storage.py:72-86,198-211",
            },
        },
        ensure_ascii=True,
    )
    gaps = verification["residual_source_binding_gaps"][:2]
    verification_findings = [
        finding(
            "binding-" + str(i), item["observation"], item["inference"], [item["owner_next_step"]]
        )
        for i, item in enumerate(gaps, 1)
    ]
    verification_source = json.dumps(
        {
            "attribution": "Actual rd6-snapshot analytical observation; same platform, not G5",
            "assessment": verification["assessment"],
            "gaps": gaps,
            "source_citations": "assurance.py:276-283,812-839;core.py:109-121,524-533",
        },
        ensure_ascii=True,
    )
    minority = dissent["quoted_initial_hypothesis"]
    dissent_findings = [
        finding(
            "H1-broad",
            minority["text"],
            minority["reasoning"],
            ["Do not generalize attachment-path counterevidence to generic admission."],
        ),
        finding(
            "C1-generic",
            dissent["residual_runtime_gap"]["title"],
            dissent["residual_runtime_gap"]["inferred_risk"],
            ["Compose assurance semantic replay into existing generic admission and recovery."],
        ),
    ]
    dissent_source = json.dumps(
        {
            "attribution": "Actual rd6-dissent cross-cutting source; analyst hypothesis is not code",
            "hypothesis": minority,
            "residual": {
                key: dissent["residual_runtime_gap"][key]
                for key in ("title", "status", "inferred_risk", "counterevidence_acknowledged")
            },
            "narrow_counterevidence": dissent["narrow_attach_path_counterevidence"]["claim"],
            "source_citations": "assurance.py:808-809,823-824;core.py:373-384;contracts.json:5-13;storage.py:50-54",
        },
        ensure_ascii=True,
    )
    analytical = [
        {"lane": "090", "source": arch_source, "findings": findings},
        {"lane": "180", "source": verification_source, "findings": verification_findings},
        {"lane": "dissent", "source": dissent_source, "findings": dissent_findings},
    ]
    receipts = {
        name: hashlib.sha256((OUT.parent / name).read_bytes()).hexdigest()
        for name in (
            "architecture-bearing.json",
            "verification-bearing.json",
            "dissent-bearing.json",
        )
    }
    context = {
        "source_commit": SOURCE,
        "wheel_sha256": WHEEL_SHA,
        "classification": "Repository-Internal; real source observations; SDK fixture_only/unverified",
        "retention_limits": load(OUT / "retention-limit.json"),
        "analytical_receipts_sha256": receipts,
        "verification_source_note": "Verification cites tested 0030626 source; scoped hashes match fixed fa2 candidate",
        "co_storage": "Artifacts unbound to continuation inventory; no implicit inventory association",
        "G5": "NOT_RUN",
        "approval": False,
        "activation": False,
    }
    save(
        "repository-input.json",
        {
            "source_commit": SOURCE,
            "wheel_sha256": WHEEL_SHA,
            "files": load(OUT / "immutable-source.json")["files"],
            "context": context,
            "lanes": lanes,
            "mandatory": areas,
            "critical": areas,
            "analytical_outputs": analytical,
            "relations": [],
        },
    )


def repository_assurance(manifest, review_plan, outputs, relations, context):
    observation = load(OUT / "admission-observation.json")
    baseline = review.reconcile(review_plan, outputs, relations, stage="final")["payload"]["data"]
    refs = [
        {"finding": ref, "requirement_digest": core.digest(baseline["findings"][ref])}
        for ref in ("090/C1", "090/H1-broad", "dissent/H1-broad", "dissent/C1-generic")
    ]
    environment_digest = core.digest(load(OUT / "environment.json"))
    procedures = [
        {
            "id": "installed-admission-observation",
            "version": "1",
            "kind": "technical_verification",
            "expected_outputs": ["admission-observation"],
        },
        {
            "id": "historical-log-retention",
            "version": "1",
            "kind": "institutional_audit",
            "expected_outputs": ["actual-retention-receipt"],
        },
    ]
    nodes = []
    for identifier, kind, requirement, procedure, expected, requirements in (
        (
            "technical_verification",
            "technical_verification",
            "required",
            "installed-admission-observation",
            ["admission-observation"],
            refs,
        ),
        (
            "historical_retention",
            "institutional_audit",
            "blocked",
            "historical-log-retention",
            ["actual-retention-receipt"],
            [],
        ),
    ):
        nodes.append(
            {
                "id": identifier,
                "kind": kind,
                "depends_on": [],
                "requirement": requirement,
                "rationale": (
                    "Actual new installed-component observation using explicitly synthetic invalid input; no broad closure."
                    if kind == "technical_verification"
                    else "Coordinator reports 151 unavailable historical raw logs; do not recreate or rerun."
                ),
                "role": kind,
                "actor": "rd6-runtime" if kind == "technical_verification" else "coordinator",
                "identity_assurance": "unverified",
                "independence": "fixture-only",
                "procedure": {"id": procedure, "version": "1"},
                "environment_digest": environment_digest,
                "expected_outputs": expected,
                "resource_caps": {"max_bytes": 65536, "max_attempts": 3},
                "finding_requirements": requirements,
                "evidence_requirements": [procedure],
                "pending": "Retain actual bound observation; residual concerns remain open",
                "recovery": "Existing coordinator must validate semantics and explicit candidate association; no new agent",
            }
        )
    planned = assurance.assurance_plan(review_plan, outputs, relations, procedures, nodes)
    history = assurance.new_history(planned)
    node = nodes[0]
    result = {
        "node_id": node["id"],
        "plan_digest": core.digest(planned),
        "binding": planned["payload"]["data"]["binding"],
        "procedure": node["procedure"],
        "environment_digest": environment_digest,
        "actor": node["actor"],
        "identity_assurance": "unverified",
        "outcome": "PASS",
        "outputs": node["expected_outputs"],
        "bytes_used": len(core.canonical(observation)),
        "prerequisites": assurance.resume(history, manifest, node["id"])["prerequisites"],
        "evidence": [
            {
                "id": "actual-installed-admission-observation",
                "source": core.canonical(observation).decode(),
                "provenance": "unverified",
                "authority": "none",
                "status": "ACTIVE",
                "applicability": "applicable",
                "eligibility": "eligible",
                "critical": True,
                "requirements": node["evidence_requirements"],
                "finding_requirements": refs,
            }
        ],
    }
    history = assurance.ingest_result(history, manifest, str(uuid4()), result)
    dispositions = [
        {
            "finding": ref,
            "route": "retain",
            "rationale": "Unresolved source-backed concern; scoped counterevidence is not broad rejection",
        }
        for ref in baseline["findings"]
    ]
    final = assurance.reconcile(history, manifest, dispositions)
    check(
        final["payload"]["data"]["recommendation"] == "BLOCKED",
        "source-backed assurance remains explicitly BLOCKED",
    )
    check(
        final["payload"]["data"]["original_review"]["findings"] == baseline["findings"],
        "all genuine analyst findings and broad minority dissent retained",
    )
    check(
        all(d["route"] == "retain" for d in dispositions),
        "no global or fabricated rejection disposition",
    )
    for artifact in (planned, history, final):
        assurance.validate_artifact(artifact)
    checkpoint = json.loads(gzip.decompress((BEFORE / "continuation.json.gz").read_bytes()))
    review_artifacts = [
        manifest,
        review_plan,
        *outputs,
        load(OUT / "repository-initial.json"),
        load(OUT / "repository-meta.json"),
        load(OUT / "repository-recommendation.json"),
    ]
    review_successor = review.attach_continuation(checkpoint, review_artifacts)
    successor = assurance.attach_continuation(review_successor, [planned, history, final])
    check(successor["extensions"] == checkpoint["extensions"], "pure helpers preserve extensions")
    save("repository-assurance-plan.json", planned)
    save("repository-assurance-result.json", result)
    save("repository-assurance-history.json", history)
    save("repository-assurance-cache.json", assurance.fold_events(history))
    save("repository-assurance-readiness.json", assurance.readiness(history, manifest))
    save("repository-assurance-final.json", final)
    save(
        "repository-attachment-preview.json",
        {
            "all_new_attachments_validated_by_public_helpers": True,
            "review_artifacts": [core.digest(a) for a in review_artifacts],
            "assurance_artifacts": [core.digest(a) for a in (planned, history, final)],
            "preview_digest": core.digest(successor),
            "preview_only_not_a_saved_checkpoint": True,
            "storage_apply": "NOT_CALLED",
            "co_stored_artifacts": "UNBOUND_TO_CONTINUATION_INVENTORY",
            "candidate_binding": planned["payload"]["data"]["binding"],
            "retention_blocker": context["retention_limits"],
            "followup_acceptance_tests": [
                "Existing admission/recovery must reject semantically invalid but resealed assurance records.",
                "Explicitly map assurance candidate/context to inventory or retain unbound classification.",
                "Preserve broad dissent and history; no hostile-reseal resistance claim without external trust.",
                "Missing historical raw logs remain disclosed; do not manufacture replacements.",
            ],
            "G5": "NOT_RUN",
            "authority": "none",
            "approval": False,
            "activation": False,
        },
    )


def runtime_checks():
    import socket
    import subprocess

    for label, operation in (
        ("socket", socket.socket),
        ("subprocess", lambda: subprocess.run([sys.executable, "-V"], check=True)),
    ):
        try:
            operation()
        except OSError as exc:
            check("denied" in str(exc), label + " audit guard denies operation")
        else:
            raise AssertionError(label + " guard did not deny operation")
    origins = {}
    for name in (
        "codex_contracts",
        "jsonschema",
        "jsonschema_specifications",
        "referencing",
        "rpds",
        "attrs",
        "typing_extensions",
    ):
        spec = importlib.util.find_spec(name)
        check(
            spec is not None and Path(spec.origin).is_relative_to(Path(sys.prefix)),
            "installed dependency origin " + name,
        )
        origins[name] = spec.origin
    save(
        "runtime-checks.json",
        {
            "checks": CHECKS,
            "check_count": len(CHECKS),
            "dependency_origins": origins,
            "scope": "SDK closure and audit guards only, not whole-distribution pip check",
            "G5": "NOT_RUN",
            "authority": "none",
        },
    )


def admission_checks():
    """Probe real installed validators with explicitly invalid synthetic input."""
    recommendation = load(OUT / "final-recommendation.json")
    assurance.validate_artifact(recommendation)
    check(
        recommendation["payload"]["data"]["recommendation"] == "BLOCKED",
        "probe starts from semantically valid blocked synthetic recommendation",
    )
    invalid = copy.deepcopy(recommendation)
    invalid["payload"]["data"]["recommendation"] = "CONVERGED_FOR_AUTHORIZED_DECISION"
    invalid["id"] = f"{invalid['schema']}:{core.digest(invalid['payload'])}"
    invalid["integrity"] = core.digest(
        {key: value for key, value in invalid.items() if key != "integrity"}
    )
    core.validate(invalid)
    check(True, "generic core.validate admits structurally resealed false recommendation")
    rejected(
        lambda: assurance.validate_artifact(invalid),
        "RECOMMENDATION_MISMATCH",
        "semantic assurance validator rejects false cached recommendation",
    )
    checkpoint = json.loads(gzip.decompress((BEFORE / "continuation.json.gz").read_bytes()))
    assembled = copy.deepcopy(checkpoint)
    assembled["payload"]["records"].append(invalid)
    assembled["id"] = f"{assembled['schema']}:{core.digest(assembled['payload'])}"
    assembled["integrity"] = core.digest(
        {key: value for key, value in assembled.items() if key != "integrity"}
    )
    check(
        core.inspect_candidate(assembled) == [],
        "generic inspect_candidate admits false assurance recommendation structurally",
    )
    rejected(
        lambda: assurance.attach_continuation(checkpoint, [invalid]),
        "RECOMMENDATION_MISMATCH",
        "public assurance attachment helper rejects invalid new recommendation",
    )
    genuine_successor = assurance.attach_continuation(checkpoint, [recommendation])
    check(
        genuine_successor["extensions"] == checkpoint["extensions"],
        "valid helper attachment preserves extensions without writing",
    )
    check(
        genuine_successor["payload"]["session_id"] == checkpoint["payload"]["session_id"],
        "valid helper attachment preserves session without writing",
    )
    save(
        "invalid-recommendation-probe.json",
        {
            "classification": "DELIBERATELY_INVALID_SYNTHETIC_TEST_VECTOR_NOT_A_RECOMMENDATION",
            "artifact": invalid,
        },
    )
    save(
        "admission-observation.json",
        {
            "status": "OBSERVED_SEMANTIC_STRUCTURAL_VALIDATOR_DIFFERENCE",
            "checks": CHECKS,
            "check_count": len(CHECKS),
            "source_commit": SOURCE,
            "wheel_sha256": WHEEL_SHA,
            "input_classification": "Synthetic deliberately invalid test vector",
            "observation_classification": "Actual execution of installed component APIs",
            "semantic_rejection_scope": "assurance.validate_artifact and assurance.attach_continuation",
            "residual": "Generic core.validate/inspect_candidate admit structurally resealed false recommendation",
            "co_stored_artifacts": "UNBOUND to continuation inventory; co-storage is not candidate association",
            "storage_apply": "NOT_CALLED; no incorrect data persisted",
            "whole_history_reseal": "Unsupported trust boundary; not repaired or claimed",
            "institutional_followup": "Compose semantic validation and explicit candidate association in existing coordinator",
            "G5": "NOT_RUN",
            "fixture_only": True,
            "authority": "none",
            "approval": False,
            "activation": False,
        },
    )


if __name__ == "__main__":
    environment()
    if sys.argv[1:] == ["synthetic"]:
        synthetic()
    elif sys.argv[1:] == ["repository"]:
        repository()
    elif sys.argv[1:] == ["runtime-checks"]:
        runtime_checks()
    elif sys.argv[1:] == ["admission-checks"]:
        admission_checks()
    else:
        raise SystemExit("Expected synthetic, repository, runtime-checks or admission-checks")
    print(json.dumps({"status": "PASS", "new_checks": len(CHECKS), "mode": sys.argv[1]}))
