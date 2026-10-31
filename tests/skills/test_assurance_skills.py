"""Deterministic skill discovery and offline evidence-to-validation fixtures."""

from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
import yaml

from aries_serpent_core.skills import assurance
from aries_serpent_core.skills.envelope import ExecutionEnvelope
from aries_serpent_core.skills.models import SkillManifest
from aries_serpent_core.skills.registry import SkillRegistry

SHA = "a" * 40
ROOT = Path(assurance.__file__).parent
SKILLS = (
    "rubber_duck_review",
    "adversarial_validation",
    "evidence_to_improvement_brief",
    "lane_contract_and_handoff",
    "agent_regression_evaluation",
    "pypi_release_assurance",
)


def validation():
    return {
        "author": "fixture-author",
        "observer": "fixture-validator",
        "base_sha": SHA,
        "required_checks": ["negative", "boundary", "regression"],
        "checks": [
            {
                "name": kind,
                "kind": kind,
                "completed": True,
                "command": ["pytest", f"test_{kind}"],
                "returncode": 0,
                "evidence_ref": f"fixture:{kind}",
                "base_sha": SHA,
            }
            for kind in ("negative", "boundary", "regression")
        ],
    }


def brief():
    return {
        "source": "fixture:historical-ci",
        "timestamp": "2026-10-31T00:00:00Z",
        "observed_at": "2026-10-31T00:00:10Z",
        "freshness_seconds": 60,
        "base_sha": SHA,
        "problem": "Repeated package install failure",
        "module": "packages/contracts",
        "hypothesis": "Validate built artifact contents before release",
        "baseline_metric": 1,
        "expected_metric": 0,
        "confidence": 0.8,
        "risk": "low",
        "acceptance_criteria": ["Installed artifact imports offline"],
        "verification_commands": [["pytest", "tests/release/test_publishing_assurance.py"]],
        "lane_id": "packaging",
        "write_paths": ["packages/contracts"],
        "dependencies": [],
        "budget_seconds": 60,
        "stop_condition": "Stop after three non-progressing corrections",
        "falsification": "Artifact imports fail despite content verification",
    }


def contract():
    return {
        "run_id": "fixture-run",
        "base_sha": SHA,
        "lane_id": "packaging",
        "dependencies": [],
        "read_paths": ["packages"],
        "write_paths": ["packages/contracts"],
        "timeout_seconds": 60,
        "cost_budget": 0,
        "evidence_inputs": ["fixture:ci"],
        "acceptance_criteria": ["Independent import test"],
        "output_schema": {"type": "object"},
        "state": "pending",
    }


@pytest.mark.parametrize("skill", SKILLS)
def test_manifests_use_real_registry(skill):
    manifest = SkillManifest.model_validate(
        yaml.safe_load((ROOT / skill / "manifest.yaml").read_text())
    )
    registry = SkillRegistry()
    registered = registry.register(manifest, source_path=str(ROOT / skill / "manifest.yaml"))
    resolved = registry.resolve(manifest.id)
    assert resolved == registered
    module, function = manifest.entrypoint.split(":")
    assert module == "aries_serpent_core.skills.assurance"
    assert callable(getattr(assurance, function))
    for schema in (manifest.io.input_schema, manifest.io.output_schema):
        import json

        jsonschema.Draft7Validator.check_schema(json.loads((ROOT / skill / schema).read_text()))
    assert not manifest.telemetry.emit_jsonl


def test_discovery_and_execution_do_not_turn_unknown_into_pass():
    registry = SkillRegistry()
    assert registry.discover(ROOT / "adversarial_validation") >= 1
    envelope = ExecutionEnvelope(registry=registry)
    result = envelope.run("adversarial.validation", {}, caller_id="fixture-validator")
    assert result.data["status"] == "unknown"


def test_review_has_no_verdict_or_patch():
    result = assurance.rubber_duck_review({"objective": "Prove import safety"})
    assert "status" not in result
    assert result["questions"]
    assert not result["approval_authority"] and not result["patch_authored"]


def test_validation_pass_fail_unknown():
    payload = validation()
    assert assurance.adversarial_validation(payload)["status"] == "pass"
    payload["checks"][0]["returncode"] = 1
    assert assurance.adversarial_validation(payload)["status"] == "fail"
    payload["checks"][0]["completed"] = False
    assert assurance.adversarial_validation(payload)["status"] == "unknown"


def test_partial_or_self_validation_unknown():
    payload = validation()
    payload["observer"] = payload["author"]
    assert assurance.adversarial_validation(payload)["status"] == "unknown"
    payload = validation()
    payload["checks"].pop()
    assert assurance.adversarial_validation(payload)["status"] == "unknown"


def test_offline_signal_brief_review_validation_bundle(monkeypatch, tmp_path):
    import socket

    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: pytest.fail("offline fixture must not access network"),
    )
    first = assurance.evidence_to_improvement_brief(brief())
    assert first == assurance.evidence_to_improvement_brief(brief())
    review = assurance.rubber_duck_review(
        {**first["brief"], "objective": first["brief"]["problem"]}
    )
    result = assurance.adversarial_validation(validation())
    bundle = {"proposal": first, "review": review, "validation": result, "fixture_only": True}
    import json

    output = tmp_path / "evidence-bundle.json"
    output.write_text(json.dumps(bundle, sort_keys=True))
    assert json.loads(output.read_text())["validation"]["status"] == "pass"
    assert not first["execution_authorized"]


def test_stale_and_session_tips_not_actionable():
    payload = brief()
    payload["observed_at"] = "2026-11-01T00:00:00Z"
    assert assurance.evidence_to_improvement_brief(payload)["status"] == "unknown"
    payload = brief()
    payload["category"] = "session-productivity"
    assert assurance.evidence_to_improvement_brief(payload)["status"] == "signal-only"


def test_handoff_scope_and_identity():
    item = contract()
    handoff = {
        "run_id": item["run_id"],
        "base_sha": SHA,
        "lane_id": "packaging",
        "state": "passed",
        "changed_paths": ["packages/contracts/src/fix.py"],
        "validation": validation(),
        "metrics": {},
        "risks": [],
        "unresolved_questions": [],
        "artifact_refs": ["fixture:result"],
    }
    assert (
        assurance.lane_contract_and_handoff({"contract": item, "handoff": handoff})["execution"]
        == "human-mediated"
    )
    for path in ("other/fix.py", "packages/contracts/../../secret", "/etc/passwd"):
        invalid = deepcopy(handoff)
        invalid["changed_paths"] = [path]
        with pytest.raises(ValueError):
            assurance.lane_contract_and_handoff({"contract": item, "handoff": invalid})
    handoff["base_sha"] = "b" * 40
    with pytest.raises(ValueError, match="identity"):
        assurance.lane_contract_and_handoff({"contract": item, "handoff": handoff})


def test_unvalidated_passed_handoff_rejected():
    item = contract()
    handoff = {
        "run_id": item["run_id"],
        "base_sha": SHA,
        "lane_id": "packaging",
        "state": "passed",
        "changed_paths": [],
        "validation": {},
        "metrics": {},
        "risks": [],
        "unresolved_questions": [],
        "artifact_refs": [],
    }
    with pytest.raises(ValueError, match="independent evidence"):
        assurance.lane_contract_and_handoff({"contract": item, "handoff": handoff})


def test_replay_tracks_holdout_regressions_and_cost():
    cases = [
        {
            "id": "ci",
            "holdout": False,
            "expected": "pass",
            "baseline": "pass",
            "actual": "fail",
            "human_interventions": 1,
            "runtime_seconds": 2,
            "cost": 0.01,
            "evidence_ref": "fixture:ci",
        },
        {
            "id": "package",
            "holdout": True,
            "expected": "fail",
            "baseline": "fail",
            "actual": "pass",
            "human_interventions": 0,
            "runtime_seconds": 1,
            "cost": 0.02,
            "evidence_ref": "fixture:package",
        },
    ]
    result = assurance.agent_regression_evaluation({"cases": cases})
    assert result["status"] == "fail"
    assert result["metrics"]["regressions"] == 2
    assert result["metrics"]["false_positives"] == 1
    assert result["metrics"]["runtime_seconds"] == 3
    assert assurance.agent_regression_evaluation({"cases": []})["status"] == "unknown"


def test_release_partial_checks_stay_unknown():
    result = assurance.pypi_release_assurance(validation())
    assert result["status"] == "unknown"
    assert not result["publication_authorized"]
    assert result["trusted_publisher"] == "unverified"
