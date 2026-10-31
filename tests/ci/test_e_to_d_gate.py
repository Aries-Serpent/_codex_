"""Promotion criteria and minimal-diff preservation use temporary registries only."""

from copy import deepcopy

import pytest
import yaml

from scripts.ci.e_to_d_gate import assess
from scripts.cognitive.d_capable_promotion import evaluate_agent, save_registry

AGENT = {
    "id": "fixture",
    "autonomy_model": "E",
    "maturity": "production",
    "violations_30d": 0,
    "handoff_protocol": "structured",
    "capability_tags": ["analysis", "testing", "evidence"],
    "description": "Fixture only",
}


@pytest.mark.parametrize(
    "field,value",
    [
        ("autonomy_model", "D_CAPABLE"),
        ("maturity", "draft"),
        ("violations_30d", 1),
        ("violations_30d", None),
        ("violations_30d", -1),
        ("violations_30d", "0"),
        ("violations_30d", False),
        ("handoff_protocol", "none"),
        ("capability_tags", ["a", "b"]),
        ("capability_tags", "abc"),
        ("capability_tags", ["a", "a", "a"]),
        ("description", ""),
        ("description", 1),
    ],
)
def test_each_criterion_blocks(field, value):
    agent = deepcopy(AGENT)
    agent[field] = value
    eligible, reasons = evaluate_agent(agent)
    assert not eligible
    assert reasons


def test_explicit_evidence_is_eligible():
    assert evaluate_agent(AGENT) == (True, [])


def test_gate_never_writes_registry(tmp_path):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": [AGENT]}))
    before = registry.read_bytes()
    report = assess(registry)
    assert registry.read_bytes() == before
    assert report["status"] == "unknown"
    assert report["promotion_authorized"] is False
    assert report["registry_written"] is False


def test_minimal_writer_preserves_comments_and_order(tmp_path):
    registry = tmp_path / "fixture.yaml"
    original = "# Keep header\nlast_updated: 'old' # keep timestamp comment\nagents:\n  - id: fixture\n    autonomy_model: E # keep model comment\n    description: retained\n"
    registry.write_text(original)
    data = yaml.safe_load(original)
    data["agents"][0]["autonomy_model"] = "D_CAPABLE"
    data["last_updated"] = "2026-10-31T00:00:00Z"
    save_registry(data, registry)
    assert registry.read_text() == original.replace("'old'", "'2026-10-31T00:00:00Z'").replace(
        "autonomy_model: E", "autonomy_model: D_CAPABLE"
    )


def test_minimal_writer_refuses_other_changes(tmp_path):
    registry = tmp_path / "fixture.yaml"
    original = "agents:\n  - id: fixture\n    autonomy_model: E\n"
    registry.write_text(original)
    data = yaml.safe_load(original)
    data["agents"][0]["id"] = "other"
    with pytest.raises(ValueError, match="unrelated"):
        save_registry(data, registry)
    assert registry.read_text() == original
