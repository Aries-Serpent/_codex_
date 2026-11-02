"""Direct-handler assurance invariants, independent of envelope schema validation."""

import json
from copy import deepcopy

import pytest

from aries_serpent_core.skills import assurance
from tests.skills.test_assurance_skills import SHA, brief, contract, validation


@pytest.mark.parametrize(
    "key",
    ["baseline_metric", "expected_metric", "budget_seconds", "freshness_seconds", "confidence"],
)
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True, "1"])
def test_brief_requires_finite_measurements(key, value):
    payload = brief()
    payload[key] = value
    with pytest.raises(ValueError, match="finite"):
        assurance.evidence_to_improvement_brief(payload)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("command", "pytest test_negative"),
        ("command", ["pytest", " "]),
        ("command", [1]),
        ("command", []),
        ("evidence_ref", " "),
        ("evidence_ref", {"path": "result"}),
        ("timestamp", "not-a-time"),
        ("timestamp", "2026-10-31T00:00:00"),
        ("timestamp", None),
        ("observed_at", "2026-10-30T00:00:00Z"),
        ("run_id", "other-run"),
        ("lane_id", "other-lane"),
        ("observer", " "),
        ("returncode", True),
        ("name", []),
        ("kind", []),
    ],
)
def test_invalid_command_observations_cannot_pass(key, value):
    payload = validation()
    payload["checks"][0][key] = value
    assert assurance.adversarial_validation(payload)["status"] == "unknown"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("author", " "),
        ("observer", ["validator"]),
        ("observer", " fixture-author "),
        ("required_checks", "negative"),
        ("required_checks", ["negative", [], "regression"]),
        ("required_checks", ["negative", "boundary", "regression", "negative"]),
        ("timestamp", "invalid"),
        ("freshness_seconds", float("nan")),
    ],
)
def test_invalid_validation_identity_and_time_unknown(key, value):
    payload = validation()
    payload[key] = value
    assert assurance.adversarial_validation(payload)["status"] == "unknown"


def passed_handoff():
    item = contract()
    return {
        "run_id": item["run_id"],
        "base_sha": SHA,
        "lane_id": item["lane_id"],
        "state": "passed",
        "changed_paths": [],
        "validation": validation(),
        "metrics": {},
        "risks": [],
        "unresolved_questions": [],
        "artifact_refs": ["fixture:result"],
    }


@pytest.mark.parametrize("key", ["base_sha", "run_id", "lane_id"])
def test_validation_must_match_handoff_identity(key):
    handoff = passed_handoff()
    handoff["validation"][key] = "b" * 40 if key == "base_sha" else "another-identity"
    for check in handoff["validation"]["checks"]:
        check[key] = handoff["validation"][key]
    assert assurance.adversarial_validation(handoff["validation"])["status"] == "pass"
    with pytest.raises(ValueError, match="validation identity"):
        assurance.lane_contract_and_handoff({"contract": contract(), "handoff": handoff})


def test_contract_required_checks_cannot_be_replaced():
    item = contract()
    item["required_checks"] = ["negative", "boundary", "regression", "imports"]
    handoff = passed_handoff()
    with pytest.raises(ValueError, match="required checks"):
        assurance.lane_contract_and_handoff({"contract": item, "handoff": handoff})
    handoff["validation"]["required_checks"].append("imports")
    extra = deepcopy(handoff["validation"]["checks"][0])
    extra["name"] = "imports"
    handoff["validation"]["checks"].append(extra)
    assert (
        assurance.lane_contract_and_handoff({"contract": item, "handoff": handoff})["status"]
        == "contract-valid"
    )


@pytest.mark.parametrize("checks", [None, ["negative", "boundary", "regression"]])
def test_published_contract_schema_matches_handler(checks):
    item = contract()
    if checks is None:
        item.pop("required_checks", None)
    else:
        item["required_checks"] = checks
    schema = json.loads((assurance._SCHEMA_ROOT / "lane-contract.json").read_text())
    assurance.jsonschema.Draft7Validator(schema).validate(item)
    assert assurance.lane_contract_and_handoff({"contract": item})["status"] == "contract-valid"


@pytest.mark.parametrize("checks", [[], ["negative", "negative"], [""], "negative"])
def test_published_contract_schema_rejects_invalid_checks(checks):
    item = {**contract(), "required_checks": checks}
    schema = json.loads((assurance._SCHEMA_ROOT / "lane-contract.json").read_text())
    with pytest.raises(assurance.jsonschema.ValidationError):
        assurance.jsonschema.Draft7Validator(schema).validate(item)
    with pytest.raises(assurance.jsonschema.ValidationError):
        assurance.lane_contract_and_handoff({"contract": item})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_contract_cost_requires_finite_measurement(value):
    item = contract()
    item["cost_budget"] = value
    with pytest.raises((ValueError, assurance.jsonschema.ValidationError)):
        assurance.lane_contract_and_handoff({"contract": item})


def replay():
    return [
        {
            "id": name,
            "holdout": holdout,
            "expected": "pass",
            "baseline": "pass",
            "actual": "pass",
            "human_interventions": 0,
            "runtime_seconds": 0,
            "cost": 0,
            "evidence_ref": f"fixture:{name}",
        }
        for name, holdout in (("baseline", False), ("holdout", True))
    ]


def test_holdout_only_and_empty_replay_evidence_cannot_pass():
    cases = replay()
    assert assurance.agent_regression_evaluation({"cases": cases[1:]})["status"] == "unknown"
    cases[0]["evidence_ref"] = ""
    assert assurance.agent_regression_evaluation({"cases": cases})["status"] == "unknown"


@pytest.mark.parametrize("key", ["runtime_seconds", "cost", "human_interventions"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True, "0"])
def test_replay_measurements_must_be_finite_nonnegative(key, value):
    cases = replay()
    cases[0][key] = value
    with pytest.raises(ValueError, match="finite"):
        assurance.agent_regression_evaluation({"cases": cases})


@pytest.mark.parametrize("key", ["runtime_seconds", "cost"])
def test_unavailable_replay_measurements_are_not_zero(key):
    cases = replay()
    assert assurance.agent_regression_evaluation({"cases": cases})["status"] == "pass"
    cases[0][key] = None
    result = assurance.agent_regression_evaluation({"cases": cases})
    assert result["status"] == "unknown"
    assert result["metrics"][key] is None


def test_measured_runtime_and_cost_do_not_impose_unspecified_policy_thresholds():
    cases = replay()
    cases[0]["runtime_seconds"] = 1_000_000
    cases[0]["cost"] = 1_000_000
    assert assurance.agent_regression_evaluation({"cases": cases})["status"] == "pass"
