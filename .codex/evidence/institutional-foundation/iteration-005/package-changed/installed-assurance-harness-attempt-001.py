"""Installed-wheel observation harness; no authenticated independence or approval."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata, resources
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

EVIDENCE = Path(sys.argv[1]).resolve()
RELEASE = json.loads((EVIDENCE / "release.json").read_text())
SOURCE = json.loads((EVIDENCE / "source-manifest.json").read_text())
OUTPUT = EVIDENCE / "installed-assurance-artifacts"
OUTPUT.mkdir()
CHECKS = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)


def save(name, value):
    (OUTPUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def offline(event, args):
    if event.startswith("socket.") or event == "subprocess.Popen":
        raise OSError("INSTALLED_RUNTIME_NETWORK_AND_SUBPROCESS_DISABLED")


sys.addaudithook(offline)
check("PYTHONPATH" not in os.environ, "PYTHONPATH absent")
check(sys.flags.isolated == 1, "Python isolated mode")
check(sys.prefix != sys.base_prefix, "fresh virtual environment")
check(
    "include-system-site-packages = false" in (Path(sys.prefix) / "pyvenv.cfg").read_text(),
    "system site packages disabled",
)
check(Path.cwd().resolve() == Path(RELEASE["runtime_cwd"]), "external runtime cwd")
check(
    all(
        not Path(p).resolve().is_relative_to(Path(RELEASE["repository_root"]))
        and not Path(p).resolve().is_relative_to(Path(RELEASE["export_root"]))
        for p in sys.path
        if p
    ),
    "checkout and exported source absent from import paths",
)

from codex.institutional import assurance, core, review, storage  # noqa: E402
import codex_contracts  # noqa: E402

ORIGINS = {
    name: str(Path(module.__file__).resolve())
    for name, module in [
        ("assurance", assurance),
        ("core", core),
        ("review", review),
        ("storage", storage),
        ("codex_contracts", codex_contracts),
    ]
}
check(
    all(Path(p).is_relative_to(Path(sys.prefix)) for p in ORIGINS.values()),
    "all SDK and contracts imports originate in installed runtime environment",
)
try:
    metadata.version("pytest")
except metadata.PackageNotFoundError:
    CHECKS.append("pytest absent from SDK runtime environment")
else:
    raise AssertionError("test-only pytest leaked into SDK environment")

WHEEL = Path(RELEASE["wheel"])
check(
    hashlib.sha256(WHEEL.read_bytes()).hexdigest() == RELEASE["wheel_sha256"],
    "wheel digest matches immutable release manifest",
)
installed = {}
package = resources.files("codex.institutional")
with ZipFile(WHEEL) as archive:
    for name, record in SOURCE["files"].items():
        if not name.startswith("src/codex/institutional/"):
            continue
        relative = name.removeprefix("src/codex/institutional/")
        data = package.joinpath(relative).read_bytes()
        check(
            data == archive.read("codex/institutional/" + relative)
            and hashlib.sha256(data).hexdigest() == record["sha256"],
            "exact source/wheel/installed bytes: " + relative,
        )
        installed[relative] = {
            "path": str(package.joinpath(relative)),
            "sha256": record["sha256"],
            "bytes": len(data),
        }
check("codex.assurance.v1" in core.contracts()["implemented"], "assurance schema installed")
formulas = json.loads(package.joinpath("review-formulas.json").read_bytes())
check(
    [f["id"] for f in formulas["formulas"]] == [f"RD4-F{i:03}" for i in range(1, 59)],
    "all 58 formula identities preserved",
)
save(
    "formula-identities.json",
    {
        "source_preservation": formulas["source_preservation"],
        "formulas": formulas["formulas"],
        "metadata": formulas["metadata"],
        "limits": "Exact planned notation, not numerical evaluation.",
    },
)

documentation = EVIDENCE / "inputs/assurance-review.rst"
lines = documentation.read_text().splitlines()
namespace = {}
blocks = []
index = 0
while index < len(lines):
    if lines[index] != ".. code-block:: python":
        index += 1
        continue
    index += 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    code = []
    while index < len(lines) and (lines[index].startswith("    ") or not lines[index].strip()):
        code.append(lines[index][4:] if lines[index].startswith("    ") else "")
        index += 1
    text = "\n".join(code)
    blocks.append(text)
    exec(compile(text, str(documentation), "exec"), namespace)
    if len(blocks) == 1:
        original_history = copy.deepcopy(namespace["history"])
check(len(blocks) == 2, "two exact documentation Python blocks executed installed and offline")
save("documentation-blocks.json", blocks)
manifest = namespace["manifest"]
plan = namespace["plan"]
revoked = namespace["history"]
clock = lambda: datetime(2026, 10, 25, tzinfo=timezone.utc)
check(
    namespace["recommendation"]["payload"]["data"]["recommendation"]
    == "CONVERGED_FOR_AUTHORIZED_DECISION",
    "documentation fixture recommendation converges without approval",
)
check(
    namespace["reopened"]["payload"]["data"]["recommendation"] == "BLOCKED",
    "documentation revocation reopens recommendation",
)


def rejected(call, label):
    try:
        call()
    except core.Rejected as exc:
        CHECKS.append(label + ":" + exc.reason)
    else:
        raise AssertionError(label)


def reseal(value):
    value = copy.deepcopy(value)
    value["id"] = f"{value['schema']}:{core.digest(value['payload'])}"
    value["integrity"] = core.digest({k: v for k, v in value.items() if k != "integrity"})
    return value


def status(history, fields):
    state = assurance.fold_events(history)
    result = state["latest_results"]["technical_verification"]
    previous = state["evidence_states"][result]["observation"]
    return assurance.evidence_status(
        history, str(uuid4()), result, "observation", core.digest(previous), fields, clock=clock
    )


initial_state = assurance.fold_events(original_history)
result_digest = initial_state["latest_results"]["technical_verification"]
original_status = initial_state["evidence_states"][result_digest]["observation"]
restored = status(
    revoked,
    {key: original_status[key] for key in ("status", "applicability", "eligibility", "reason")},
)
restored_state = assurance.fold_events(restored)
check(
    restored_state["nodes"]["technical_verification"]["state"] == "PASSED",
    "identical upstream fields can restore upstream technical fixture",
)
check(
    all(
        restored_state["nodes"][kind]["state"] == "BLOCKED"
        for kind in ("independent_reproduction", "institutional_audit")
    ),
    "identical upstream status restoration cannot restore stale downstream proofs",
)
check(
    original_status["revision"]
    != restored_state["evidence_states"][result_digest]["observation"]["revision"],
    "evidence revisions preserve intervening revocation",
)
check(
    assurance.resume(restored, manifest, "independent_reproduction")["ready"],
    "exact pending resume rechecks current prerequisites",
)
rejected(
    lambda: assurance.resume(restored, manifest, "institutional_audit"),
    "wrong pending node rejected",
)
drift = review.candidate_manifest(
    [{"path": "candidate.py", "kind": "file", "mode": 0o644, "content": b"drift"}],
    {"purpose": "fixture-only"},
    clock=clock,
)
rejected(
    lambda: assurance.resume(restored, drift, "independent_reproduction"),
    "candidate drift rejected on resume",
)
check(
    assurance.reconcile(restored, drift, [], clock=clock)["payload"]["data"]["recommendation"]
    == "BLOCKED",
    "candidate drift reopens recommendation",
)
cache = assurance.fold_events(restored)
check(assurance.fold_events(restored, cache) == cache, "exact replay cache accepted")
forged_cache = copy.deepcopy(cache)
forged_cache["pending_node"] = "forged"
rejected(lambda: assurance.fold_events(restored, forged_cache), "forged cache rejected")

bridge = copy.deepcopy(plan)
nodes = bridge["payload"]["data"]["nodes"]
nodes[1]["requirement"] = "not_required_with_rationale"
nodes[2]["depends_on"] = [nodes[1]["id"]]
bridge = reseal(bridge)
bridge_history = assurance.new_history(bridge, clock=clock)
bridge_state = assurance.fold_events(bridge_history)
check(
    bridge_state["nodes"]["independent_reproduction"]["state"] == "BLOCKED"
    and not bridge_state["nodes"]["institutional_audit"]["ready"],
    "exempt dependency bridge cannot bypass missing upstream requirement",
)

finding = {
    "id": "concern",
    "source_quote": "Original source concern.",
    "normalized": "Retain exact concern",
    "kind": "inference",
    "confidence": 0.4,
    "coverage": ["correctness"],
    "clearance_conditions": ["observed-response"],
}
review_plan = review.review_plan(
    manifest,
    [
        *namespace["lanes"],
        {
            "id": "rotated",
            "bearing": "Reasoning integrity",
            "actor": "fixture:rotated",
            "run": "run:rotated",
            "dissent": False,
            "required": False,
            "coverage": ["correctness"],
            "tools": ["read", "search"],
        },
    ],
    ["correctness"],
    ["correctness"],
    clock=clock,
)
finding_outputs = [
    review.lane_output(
        review_plan,
        lane["id"],
        "Original source concern. Fixture rejection: supplied counterexample. Observation recorded.",
        [finding] if lane["id"] in ("000", "dissent") else [],
        clock=clock,
    )
    for lane in namespace["lanes"]
]
relations = [{"type": "contradicts", "from": "000/concern", "to": "dissent/concern"}]
baseline = review.reconcile(review_plan, finding_outputs, relations, clock=clock)["payload"]["data"]
finding_requirements = [
    {"finding": key, "requirement_digest": core.digest(value)}
    for key, value in baseline["findings"].items()
]
finding_nodes = copy.deepcopy(namespace["nodes"])
for node in finding_nodes:
    node["finding_requirements"] = finding_requirements
finding_plan = assurance.assurance_plan(
    review_plan, finding_outputs, relations, namespace["procedures"], finding_nodes, clock=clock
)
finding_history = assurance.new_history(finding_plan, clock=clock)
for node in finding_nodes:
    result = {
        "node_id": node["id"],
        "plan_digest": core.digest(finding_plan),
        "binding": finding_plan["payload"]["data"]["binding"],
        "procedure": node["procedure"],
        "environment_digest": node["environment_digest"],
        "actor": node["actor"],
        "identity_assurance": "unverified",
        "outcome": "PASS",
        "outputs": ["report"],
        "bytes_used": 100,
        "prerequisites": assurance.readiness(finding_history, manifest)["nodes"][node["id"]][
            "prerequisites"
        ],
        "evidence": [
            {
                "id": "observation",
                "source": (
                    "Original source concern. Fixture rejection: supplied counterexample. "
                    "Observation recorded."
                ),
                "provenance": "unverified",
                "authority": "none",
                "status": "ACTIVE",
                "applicability": "applicable",
                "eligibility": "eligible",
                "critical": True,
                "requirements": ["procedure-observation"],
                "finding_requirements": finding_requirements,
            }
        ],
    }
    finding_history = assurance.ingest_result(
        finding_history, manifest, str(uuid4()), result, clock=clock
    )
check(
    assurance.reconcile(finding_history, manifest, [], clock=clock)["payload"]["data"][
        "recommendation"
    ] == "BLOCKED",
    "passed assurance results alone cannot clear original contradictory findings",
)
proposals = [
    {
        "finding": key,
        "disposition": "FIXED",
        "route": "proposed-mutation",
        "rationale": "Only proposed, never executed.",
    }
    for key in baseline["findings"]
]
fixed = assurance.reconcile(finding_history, manifest, proposals, clock=clock)
check(
    fixed["payload"]["data"]["recommendation"] == "BLOCKED"
    and fixed["payload"]["data"]["original_review"]["relations"] == relations,
    "FIXED mutation proposals remain unresolved and preserve contradictions",
)
followup = review.lane_output(
    review_plan,
    "rotated",
    "Original source concern. Fixture rejection: supplied counterexample. Observation recorded.",
    [finding],
    clock=clock,
)
bound_result = assurance.fold_events(finding_history)["latest_results"]["technical_verification"]
dispositions = []
for original_output in finding_outputs:
    for item in original_output["payload"]["data"]["findings"]:
        dispositions.append(
            {
                "finding": original_output["payload"]["data"]["lane"] + "/" + item["id"],
                "disposition": "REJECTED_WITH_EVIDENCE",
                "route": "nonmutating",
                "disposition_reason": "Fixture rejection: supplied counterexample.",
                "followup": followup,
                "evidence": {
                    "original_output": core.digest(original_output),
                    "finding_id": item["id"],
                    "followup_output": core.digest(followup),
                    "checks": [
                        {
                            "condition": "observed-response",
                            "observation": "Observation recorded.",
                            "source_quote": "Observation recorded.",
                        }
                    ],
                },
                "result_digest": bound_result,
                "evidence_id": "observation",
                "dissent": {
                    "source_quote": "Original source concern.",
                    "response": "Original wording retained alongside supplied fixture response.",
                },
            }
        )
nonmutating = assurance.reconcile(finding_history, manifest, dispositions, clock=clock)
assurance.validate_artifact(nonmutating)
check(
    nonmutating["payload"]["data"]["recommendation"] == "CONVERGED_FOR_AUTHORIZED_DECISION"
    and nonmutating["payload"]["data"]["original_review"]["relations"] == relations
    and nonmutating["payload"]["data"]["original_review"]["findings"]["dissent/concern"][
        "source_quote"
    ] == "Original source concern.",
    "bound nonmutating rejection retains original dissent and contradictions without adjudication",
)

root = Path.cwd() / "storage-fixture"
root.mkdir()
original = core.candidate(root, "installed-assurance-stable-session", clock)
original["payload"]["configuration"]["retained_profile"] = "x" * (assurance.MAX_BYTES + 1)
original["extensions"] = {"user": {"preserve": True}}
original = reseal(original)
check(
    assurance.MAX_BYTES < len(core.canonical(original)) < core.MAX_BYTES,
    "existing continuation exceeds assurance artifact cap but fits inherited aggregate cap",
)
successor = assurance.attach_continuation(
    original, [plan, original_history, namespace["recommendation"]], clock=clock
)
check(
    successor["extensions"] == original["extensions"]
    and successor["payload"]["session_id"] == original["payload"]["session_id"]
    and successor["payload"]["sequence"] == 2
    and successor["payload"]["predecessor"] == core.digest(original),
    "attachment preserves session, extensions and exact predecessor",
)
preview = storage.plan(root, original)
check(not (root / core.NAMESPACE).exists(), "storage preview does not write")
storage.apply(root, original, preview)
storage.apply(root, successor, storage.plan(root, successor, core.digest(original)))
checkpoint = root / core.NAMESPACE / "checkpoint.json"
recovered = core.load(checkpoint)
check(recovered == successor, "actual installed storage roundtrip retains assurance artifacts")
check(checkpoint.stat().st_mode & 0o777 == 0o600, "checkpoint uses private 0600 mode")
recovered_history = recovered["payload"]["records"][-2]
reopened_history = status(
    recovered_history,
    {
        "status": "REVOKED",
        "applicability": "applicable",
        "eligibility": "eligible",
        "reason": "Installed fixture revocation after recovery.",
    },
)
reopened_recommendation = assurance.reconcile(reopened_history, manifest, [], clock=clock)
next_checkpoint = assurance.attach_continuation(
    recovered, [reopened_history, reopened_recommendation], clock=clock
)
storage.apply(root, next_checkpoint, storage.plan(root, next_checkpoint, core.digest(recovered)))
reloaded = core.load(checkpoint)
reloaded_history = reloaded["payload"]["records"][-2]
check(
    reloaded["payload"]["sequence"] == 3
    and reloaded["payload"]["session_id"] == "installed-assurance-stable-session"
    and assurance.fold_events(reloaded_history)["pending_node"] == "technical_verification",
    "durable recovery preserves identity and reopens exact technical pending node",
)
restored_reloaded = status(
    reloaded_history,
    {key: original_status[key] for key in ("status", "applicability", "eligibility", "reason")},
)
check(
    assurance.resume(restored_reloaded, manifest, "independent_reproduction")["ready"]
    and assurance.reconcile(restored_reloaded, manifest, [], clock=clock)["payload"]["data"][
        "recommendation"
    ] == "BLOCKED",
    "persisted recovery resumes pending downstream work without silent convergence",
)
check(
    (root / core.NAMESPACE / f"previous-{core.digest(original)}.json").read_bytes()
    == core.canonical(original),
    "original predecessor bytes preserved",
)
bad_binding = copy.deepcopy(original)
bad_binding["payload"]["candidate_ref"] = "0" * 64
rejected(lambda: storage.plan(root, reseal(bad_binding)), "storage rejects candidate binding drift")
rejected(lambda: storage.apply(root, original, preview), "repeat/stale write rejected")

for call, label in [
    (lambda: socket.create_connection(("example.invalid", 443)), "socket denied offline"),
    (lambda: subprocess.run(["never-executed-command"]), "subprocess denied offline"),
]:
    try:
        call()
    except OSError as exc:
        check(
            str(exc) == "INSTALLED_RUNTIME_NETWORK_AND_SUBPROCESS_DISABLED",
            label,
        )
    else:
        raise AssertionError(label)

limits = namespace["recommendation"]["payload"]["data"]["limits"]
check(
    limits["authority"] == "none"
    and limits["approval"] is False
    and limits["activation"] is False
    and limits["fixture_only"] is True,
    "all fixture convergence remains non-authorizing and unapproved",
)
for name, artifact in [
    ("plan", plan),
    ("original-history", original_history),
    ("revoked-history", revoked),
    ("identically-restored-history", restored),
    ("exempt-bridge-history", bridge_history),
    ("findings-history", finding_history),
    ("fixed-unresolved", fixed),
    ("nonmutating-fixture-rejection", nonmutating),
    ("recovered-continuation", reloaded),
    ("reopened-history", reopened_history),
    ("reopened-recommendation", reopened_recommendation),
]:
    save(name + ".json", artifact)
direct_urls = {
    name: json.loads(metadata.distribution(name).read_text("direct_url.json"))
    for name in ("codex-ml", "codex-contracts")
}
check(
    all(
        "archive_info" in data and not data.get("dir_info", {}).get("editable", False)
        for data in direct_urls.values()
    ),
    "main SDK and local contracts both installed noneditably from wheel archives",
)
result = {
    "status": "PASS",
    "source_commit": SOURCE["source_commit"],
    "wheel_sha256": RELEASE["wheel_sha256"],
    "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "checks_passed": len(CHECKS),
    "checks": CHECKS,
    "python": sys.version,
    "cwd": str(Path.cwd()),
    "sys_path": sys.path,
    "runtime_prefix": sys.prefix,
    "import_origins": ORIGINS,
    "installed_resources": installed,
    "direct_urls": direct_urls,
    "documentation_blocks_executed": len(blocks),
    "continuation_sizes": {
        "original": len(core.canonical(original)),
        "successor": len(core.canonical(successor)),
        "sequence3": len(core.canonical(reloaded)),
    },
    "network": "Process-local audit hook denies sockets and subprocess creation with OSError.",
    "authority": "none",
    "independence": "unverified same-platform fixtures, separately authored harness",
    "G5": "NOT_RUN",
    "limits": [
        "No authenticated identity, approval, activation or independent production assurance.",
        "SDK dependency closure only; whole-distribution pip check retained separately.",
        "Documentation source fixtures are fabricated observations, not external factual proof.",
        "Process-local offline guard is not kernel network isolation.",
        "Formula notation preserved; numerical evaluation not implemented.",
        "Source-only parent fixture harness retained unchanged, not relabeled or executed here.",
    ],
}
save("results.json", result)
print(json.dumps({"status": "PASS", "checks_passed": len(CHECKS)}))
