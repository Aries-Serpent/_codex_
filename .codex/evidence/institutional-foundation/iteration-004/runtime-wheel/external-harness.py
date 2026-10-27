"""Standalone installed-wheel exercise; no checkout imports or operational authority."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import socket
import sys
import uuid
from datetime import datetime, timezone
from importlib import metadata, resources
from pathlib import Path
from zipfile import ZipFile

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--release", type=Path, required=True)
PARSER.add_argument("--output", type=Path, required=True)
ARGS = PARSER.parse_args()
RELEASE = json.loads(ARGS.release.read_text())
ARGS.output.mkdir(parents=True, exist_ok=True)
CHECKS = []


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)


def save(name, value):
    (ARGS.output / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def network_guard(event, args):
    if event.startswith("socket.") or event == "subprocess.Popen":
        raise RuntimeError("RUNTIME_NETWORK_OR_SUBPROCESS_DISABLED")


sys.addaudithook(network_guard)
check("PYTHONPATH" not in os.environ, "PYTHONPATH absent")
check(sys.flags.isolated == 1, "Python isolated mode")
check(sys.prefix != sys.base_prefix, "fresh virtual environment")
check(
    "include-system-site-packages = false" in (Path(sys.prefix) / "pyvenv.cfg").read_text(),
    "system site packages disabled",
)
check(
    Path.cwd().resolve() == Path(RELEASE["runtime_cwd"]).resolve(),
    "dedicated external runtime working directory",
)
check(
    all(
        Path(entry).resolve()
        not in (Path(RELEASE["repository_root"]), Path(RELEASE["export_root"]) / "src")
        for entry in sys.path
        if entry
    ),
    "checkout and export source paths absent from import path",
)

from codex.institutional import core, review  # noqa: E402

NOW = datetime(2026, 10, 25, tzinfo=timezone.utc)


def clock():
    return NOW


def rejected(call, name):
    try:
        call()
    except core.Rejected:
        CHECKS.append(name)
    else:
        raise AssertionError(name)


def reseal(value):
    value = copy.deepcopy(value)
    value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
    value["integrity"] = core.digest(
        {key: data for key, data in value.items() if key != "integrity"}
    )
    return value


origins = {
    name: str(Path(module.__file__).resolve())
    for name, module in [("core", core), ("review", review)]
}
check(
    all(Path(origin).is_relative_to(Path(sys.prefix).resolve()) for origin in origins.values()),
    "all SDK imports originate in runtime venv",
)
dist = metadata.distribution("codex-ml")
direct_url = json.loads(dist.read_text("direct_url.json"))
check(not direct_url.get("dir_info", {}).get("editable", False), "non-editable installation")
check("archive_info" in direct_url, "installed distribution came from wheel archive")
wheel = Path(RELEASE["wheel"])
check(
    hashlib.sha256(wheel.read_bytes()).hexdigest() == RELEASE["wheel_sha256"],
    "actual wheel digest matches release manifest",
)
package = resources.files("codex.institutional")
resource_results = {}
expected_resources = ["contracts.json", *RELEASE["formula_resources"]]
check(
    "review-formulas.json" in RELEASE["formula_resources"],
    "formula registry declared for validation",
)
with ZipFile(wheel) as archive:
    for name in ["review.py", *expected_resources]:
        installed = package.joinpath(name).read_bytes()
        wheel_bytes = archive.read("codex/institutional/" + name)
        source_sha = RELEASE["source_files"]["src/codex/institutional/" + name]
        check(
            installed == wheel_bytes and hashlib.sha256(installed).hexdigest() == source_sha,
            "exact source/wheel/installed bytes: " + name,
        )
        resource_results[name] = {"sha256": source_sha, "bytes": len(installed)}
formula_data = json.loads(package.joinpath("review-formulas.json").read_bytes())
check(len(formula_data["formulas"]) == 58, "all 58 planned formulas packaged")
check(formula_data["authority"] is False, "formula registry confers no authority")
check(
    all(
        formula_data["metadata"][entry["metadata_ref"]]["implementation"] == "planned"
        for entry in formula_data["formulas"]
    ),
    "formulas remain planned, not numerical SDK claims",
)
check("codex.review.v1" in core.contracts()["implemented"], "versioned review contract packaged")
check(
    metadata.version("codex-contracts") is not None,
    "declared local contracts distribution installed",
)

context = {
    "actor": "same-platform:implementer",
    "policy": "Repository-Internal fixture, no approval",
    "model": "unverified",
    "source_commit": RELEASE["source_commit"],
}
file_bytes = b"explicit supplied bytes\r\n"


def manifest(content=file_bytes, supplied_context=context):
    return review.candidate_manifest(
        [{"path": "src/example.py", "content": content, "kind": "file", "mode": 0o644}],
        supplied_context,
        clock=clock,
    )


candidate = manifest()
lanes = [
    {
        "id": name,
        "bearing": bearing,
        "actor": "same-platform:" + name,
        "run": "wheel-fixture:" + name,
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
plan = review.review_plan(candidate, lanes, ["correctness", "security"], ["security"], clock=clock)
finding = {
    "id": "f1",
    "source_quote": "Original wording: risk remains.",
    "normalized": "Retained risk",
    "kind": "inference",
    "confidence": 0.4,
    "coverage": ["security"],
    "clearance_conditions": ["finding-bound-observation"],
}
outputs = [
    review.lane_output(
        plan,
        lane["id"],
        lane["actor"] + ": Original wording: risk remains. Fixture reproduced.",
        [finding],
        clock=clock,
    )
    for lane in lanes
]
relations = [{"type": "contradicts", "from": "logic/f1", "to": "dissent/f1"}]
recommendations = {}
for stage in ("initial", "meta", "final"):
    recommendations[stage] = review.reconcile(
        plan, outputs[:3], relations, stage=stage, clock=clock
    )
    data = recommendations[stage]["payload"]["data"]
    check(data["authorization"] == "none", stage + " has no authorization")
    check(data["independence"] == "unverified", stage + " identities remain unverified")
    check(data["blockers"][0]["cause"] == "unresolved-conflict", stage + " retains conflict")
    check(
        data["findings"]["logic/f1"]["source"] == outputs[0]["payload"]["data"]["source"],
        stage + " retains exact attributed source",
    )

missing = review.reconcile(plan, outputs[:1], [], clock=clock)
check(len(missing["payload"]["data"]["blockers"]) == 2, "missing required lanes explicit")
history = review.new_history(plan, clock=clock)
blocker = missing["payload"]["data"]["blockers"][0]
history = review.append_event(history, str(uuid.uuid4()), "block", blocker, clock=clock)
blocked_history = copy.deepcopy(history)
rejected(
    lambda: review.resume(
        history, manifest(b"changed"), str(uuid.uuid4()), blocker["clearance_conditions"]
    ),
    "candidate drift blocks resume",
)
rejected(
    lambda: review.resume(
        history,
        manifest(supplied_context={"policy": "changed"}),
        str(uuid.uuid4()),
        blocker["clearance_conditions"],
    ),
    "context drift blocks resume",
)
rejected(
    lambda: review.resume(history, candidate, str(uuid.uuid4()), ["invented"]),
    "inexact clearance blocks resume",
)
history = review.resume(
    history, candidate, str(uuid.uuid4()), blocker["clearance_conditions"], clock=clock
)
check(
    review.fold_events(history)["state"]["pending_requirement"] == blocker["pending_requirement"],
    "exact resume retains original pending requirement",
)
for stage in ("meta", "final"):
    history = review.append_event(history, str(uuid.uuid4()), "advance", {"to": stage}, clock=clock)
cache = review.fold_events(history)
check(cache["state"]["stage"] == "final", "strict event progression reaches final review stage")
check(review.fold_events(history, cache) == cache, "cache exactly bound to event digest")
rejected(
    lambda: review.fold_events(history, {"event_digest": "stale", "state": cache["state"]}),
    "stale cache rejected",
)
rejected(
    lambda: review.append_event(
        history, history["payload"]["data"]["events"][0]["event_id"], "advance", {"to": "meta"}
    ),
    "duplicate event identity rejected",
)
reordered = copy.deepcopy(history)
reordered["payload"]["data"]["events"].reverse()
rejected(lambda: review.fold_events(reseal(reordered)), "reordered history rejected")
evidence = {
    "original_output": core.digest(outputs[0]),
    "finding_id": "f1",
    "followup_output": core.digest(outputs[3]),
    "checks": [
        {
            "condition": "finding-bound-observation",
            "observation": "Fixture reproduced.",
            "source_quote": "Fixture reproduced.",
        }
    ],
}
adequacy = review.remediation_adequacy(plan, outputs[0], "f1", outputs[3], evidence)
check(adequacy["status"] == "evidence-coverage-only", "rotated response is coverage only")
check(adequacy["identity"] == "unverified", "rotated actor is not verified independence")
rejected(
    lambda: review.remediation_adequacy(
        plan, outputs[0], "f1", outputs[3], {**evidence, "adequate": True}
    ),
    "adequate boolean cannot replace original finding-bound checks",
)
for confidence in [10**400, -(10**400)]:
    bad_finding = {**finding, "confidence": confidence}
    rejected(
        lambda: review.lane_output(plan, "logic", finding["source_quote"], [bad_finding]),
        "huge integer confidence rejected before float conversion",
    )
    imported = copy.deepcopy(outputs[0])
    imported["payload"]["data"]["findings"][0]["confidence"] = confidence
    rejected(
        lambda: review.reconcile(plan, [reseal(imported)], []),
        "huge imported integer confidence rejected",
    )
try:
    socket.create_connection(("example.invalid", 443))
except RuntimeError as exc:
    check(str(exc) == "RUNTIME_NETWORK_OR_SUBPROCESS_DISABLED", "runtime network attempt denied")
else:
    raise AssertionError("network audit guard did not block connection")

save("candidate-manifest.json", candidate)
save("review-context.json", context)
save("review-plan.json", plan)
save("lane-outputs.json", outputs)
save("recommendations.json", recommendations)
save("blocked-history.json", blocked_history)
save("history.json", history)
save("event-cache.json", cache)
save("rotated-evidence.json", evidence)
save("rotated-adequacy.json", adequacy)
result = {
    "source_commit": RELEASE["source_commit"],
    "wheel": wheel.name,
    "wheel_sha256": RELEASE["wheel_sha256"],
    "distribution_version": dist.version,
    "codex_contracts_version": metadata.version("codex-contracts"),
    "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "python": sys.version,
    "runtime_prefix": sys.prefix,
    "cwd": str(Path.cwd()),
    "sys_path": sys.path,
    "import_origins": origins,
    "resource_manifest": resource_results,
    "direct_url": direct_url,
    "checks_passed": len(CHECKS),
    "checks": CHECKS,
    "network": "Python audit hook denies all socket events; subprocess creation denied",
    "authority": "none",
    "independence": "unverified same-platform fixture",
    "G5": "NOT_RUN",
    "limits": [
        "SDK-only dependency environment, not full codex-ml dependency conformance",
        "No numerical formula evaluator or assurance DAG",
        "No authenticated identities, acceptance, activation or operational routing",
        "Event digests are not tamperproof; cross-store UUID uniqueness not enforced",
        "Remediation checks source-bound evidence coverage, not truth",
    ],
}
save("results.json", result)
print(
    json.dumps(
        {
            "status": "PASS",
            "checks_passed": len(CHECKS),
            "source_commit": RELEASE["source_commit"],
            "wheel_sha256": RELEASE["wheel_sha256"],
        }
    )
)
