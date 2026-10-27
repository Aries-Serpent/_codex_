"""Retain source-only fixture and newcomer-example evidence; no installed claim."""

from __future__ import annotations

import hashlib
import json
import runpy
import sys
from pathlib import Path

from codex.institutional import assurance, core, storage

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent
fixture = runpy.run_path(str(ROOT / "tests/institutional/test_assurance.py"))
history = fixture["complete"](fixture["fixture_plan"](findings=True, contradiction=True))
manifest = fixture["manifest"]()
dispositions = fixture["response_dispositions"](history)
converged = assurance.reconcile(history, manifest, dispositions, clock=fixture["clock"])
blocked = assurance.reconcile(history, manifest, [], clock=fixture["clock"])
revoked = assurance.reconcile(
    fixture["alter_status"](history), manifest, dispositions, clock=fixture["clock"]
)
drift = assurance.reconcile(
    history,
    fixture["manifest"](context={"purpose": "changed-context"}),
    dispositions,
    clock=fixture["clock"],
)
initial_state = assurance.fold_events(history)
original_result = initial_state["latest_results"]["technical_verification"]
initial_status = initial_state["evidence_states"][original_result]["observation"]
revoked_history = revoked["payload"]["data"]["history"]
revoked_status = assurance.fold_events(revoked_history)["evidence_states"][original_result][
    "observation"
]
identically_restored = assurance.evidence_status(
    revoked_history,
    fixture["event_id"](21),
    original_result,
    "observation",
    core.digest(revoked_status),
    {key: initial_status[key] for key in ("status", "applicability", "eligibility", "reason")},
    clock=fixture["clock"],
)
restored_state = assurance.fold_events(identically_restored)
assert restored_state["nodes"]["technical_verification"]["state"] == "PASSED"
for node in ("independent_reproduction", "institutional_audit"):
    assert restored_state["nodes"][node]["state"] == "BLOCKED"
restored_recommendation = assurance.reconcile(
    identically_restored, manifest, dispositions, clock=fixture["clock"]
)
bridge_history = assurance.new_history(fixture["exempt_bridge_plan"](), clock=fixture["clock"])
bridge_state = assurance.fold_events(bridge_history)
assert bridge_state["nodes"]["independent_reproduction"]["state"] == "BLOCKED"
assert not bridge_state["nodes"]["institutional_audit"]["ready"]
bridge_recommendation = assurance.reconcile(bridge_history, manifest, [], clock=fixture["clock"])
assert converged["payload"]["data"]["recommendation"] == "CONVERGED_FOR_AUTHORIZED_DECISION"
for artifact in (blocked, revoked, drift, restored_recommendation, bridge_recommendation):
    assert artifact["payload"]["data"]["recommendation"] == "BLOCKED"
for artifact in (
    converged,
    blocked,
    revoked,
    drift,
    restored_recommendation,
    bridge_recommendation,
):
    assurance.validate_artifact(artifact)
artifacts = {
    "source_only": True,
    "scope": "Synthetic same-platform fixtures, not independent production evidence.",
    "converged": converged,
    "blocked_original_findings": blocked,
    "reopened_revoked": revoked,
    "reopened_context_drift": drift,
    "reopened_identical_status_restoration": restored_recommendation,
    "blocked_required_exempt_required_bridge": bridge_recommendation,
}
(OUTPUT / "assurance-fixtures.json").write_text(json.dumps(artifacts, indent=2) + "\n")

documentation = ROOT / "docs/assurance-review.rst"
lines = documentation.read_text().splitlines()
namespace: dict = {}
executed = 0
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
    exec(compile("\n".join(code), str(documentation), "exec"), namespace)
    executed += 1
assert executed == 2
storage_root = OUTPUT / "assurance-scratch" / "storage-recovery"
storage_root.mkdir(parents=True)
original = core.candidate(storage_root, "stable-assurance-fixture-session", fixture["clock"])
original["payload"]["configuration"]["retained_profile"] = "x" * (assurance.MAX_BYTES + 1)
original["extensions"] = {"user": {"preserve": True}}
original = fixture["reseal"](original)
assert assurance.MAX_BYTES < len(core.canonical(original)) < core.MAX_BYTES
assert core.inspect_candidate(original) == []
successor = assurance.attach_continuation(original, [history, converged], clock=fixture["clock"])
storage.apply(storage_root, original, storage.plan(storage_root, original))
storage.apply(storage_root, successor, storage.plan(storage_root, successor, core.digest(original)))
recovered = core.load(storage_root / core.NAMESPACE / "checkpoint.json")
assert recovered == successor
assert core.inspect_candidate(recovered) == []
assert recovered["payload"]["session_id"] == original["payload"]["session_id"]
assert recovered["extensions"] == original["extensions"]
recovered_history = recovered["payload"]["records"][-2]
revoked_history = fixture["alter_status"](recovered_history)
next_checkpoint = assurance.attach_continuation(
    recovered, [revoked_history], clock=fixture["clock"]
)
storage.apply(
    storage_root,
    next_checkpoint,
    storage.plan(storage_root, next_checkpoint, core.digest(recovered)),
)
reloaded = core.load(storage_root / core.NAMESPACE / "checkpoint.json")
reloaded_history = reloaded["payload"]["records"][-1]
assert assurance.fold_events(reloaded_history)["pending_node"] == "technical_verification"
assert reloaded["payload"]["session_id"] == original["payload"]["session_id"]
assert reloaded["extensions"] == original["extensions"]
restored = fixture["alter_status"](reloaded_history, "ACTIVE", event=21)
assert assurance.resume(restored, manifest, "independent_reproduction")["ready"]
assert (
    assurance.reconcile(restored, manifest, dispositions)["payload"]["data"]["recommendation"]
    == "BLOCKED"
)
sources = [
    "src/codex/institutional/assurance.py",
    "src/codex/institutional/contracts.json",
    "src/codex/institutional/review.py",
    "tests/institutional/test_assurance.py",
    "docs/assurance-review.rst",
    "docs/adr/assurance-review-005.json",
]
summary = {
    "source_only": True,
    "python": sys.version,
    "interpreter": sys.executable,
    "newcomer_example_blocks_executed": executed,
    "existing_storage_roundtrip_recovery": {
        "passed": True,
        "session_id": reloaded["payload"]["session_id"],
        "extensions_preserved": reloaded["extensions"] == original["extensions"],
        "sequence": reloaded["payload"]["sequence"],
        "pending_after_recovery": assurance.fold_events(reloaded_history)["pending_node"],
        "fixture_only": True,
        "original_continuation_bytes": len(core.canonical(original)),
        "successor_continuation_bytes": len(core.canonical(successor)),
        "assurance_artifact_cap": assurance.MAX_BYTES,
        "inherited_aggregate_cap": core.MAX_BYTES,
    },
    "fixture_recommendations": {
        name: artifact["payload"]["data"]["recommendation"]
        for name, artifact in artifacts.items()
        if isinstance(artifact, dict)
    },
    "sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
}
(OUTPUT / "assurance-fixture-check.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
