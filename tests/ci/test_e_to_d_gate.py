"""Promotion criteria and minimal-diff preservation use temporary registries only."""

import json
from copy import deepcopy

import pytest
import yaml

from scripts.ci.e_to_d_gate import assess
from scripts.ci.generate_manifest import add_integrity_hash
from scripts.cognitive.d_capable_promotion import evaluate_agent, run, save_registry

AGENT = {
    "id": "fixture",
    "name": "Fixture Agent",
    "status": "active",
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
    assert report["conditions"]["C3"]["status"] == "unknown"


def test_local_schema_and_hash_do_not_establish_hosted_readiness(tmp_path):
    agents = [{**AGENT, "id": f"fixture-{i}", "enforcement_tier": "GROUNDED"} for i in range(8)]
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": agents}))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(add_integrity_hash({"fixture": True})))
    before = registry.read_bytes(), manifest.read_bytes()
    report = assess(registry, manifest=manifest)
    assert report["conditions"]["C1"]["status"] == "pass"
    assert report["conditions"]["C4"]["status"] == "pass"
    assert report["conditions"]["C2"]["status"] == "unknown"
    assert report["status"] == "unknown"
    assert not report["promotion_authorized"]
    assert (registry.read_bytes(), manifest.read_bytes()) == before


@pytest.mark.parametrize("payload", [{}, {"integrity_sha256": "incorrect"}, [], None])
def test_missing_or_invalid_hash_fails(tmp_path, payload):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": [AGENT]}))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload))
    assert assess(registry, manifest=manifest)["conditions"]["C4"]["status"] == "fail"


@pytest.mark.parametrize("agents", [[], [AGENT, AGENT], [{**AGENT, "name": ""}]])
def test_canonical_schema_and_population_fail_closed(tmp_path, agents):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": agents}))
    report = assess(registry)
    assert report["conditions"]["C1"]["status"] == "fail"
    assert report["status"] == "fail"


def test_cli_cannot_overwrite_manifest_alias(tmp_path, monkeypatch):
    from scripts.ci.e_to_d_gate import main

    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": [AGENT]}))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(add_integrity_hash({"fixture": True})))
    alias = tmp_path / "alias.json"
    alias.hardlink_to(manifest)
    before = manifest.read_bytes()
    monkeypatch.setattr(
        "sys.argv",
        ["gate", "--registry", str(registry), "--manifest", str(manifest), "--output", str(alias)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert manifest.read_bytes() == before


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


@pytest.mark.parametrize("document_start", ["", "---\n"])
@pytest.mark.parametrize("document_end", ["", "\n", "\n...\n"])
def test_promotion_inserts_missing_timestamp(tmp_path, monkeypatch, document_start, document_end):
    monkeypatch.chdir(tmp_path)
    original = (
        "# Keep header\n"
        + document_start
        + yaml.safe_dump({"agents": [AGENT]}, sort_keys=False).rstrip("\n")
        + document_end
    )
    registry = tmp_path / "fixture.yaml"
    registry.write_text(original)
    assert run(registry, apply=True) == 0
    updated = registry.read_text()
    data = yaml.safe_load(updated)
    assert data["agents"] == [{**AGENT, "autonomy_model": "D_CAPABLE"}]
    timestamp_line = f"last_updated: '{data['last_updated']}'\n"
    assert timestamp_line in updated
    assert updated.replace(timestamp_line, "") == original.replace(
        "autonomy_model: E", "autonomy_model: D_CAPABLE"
    )


def test_timestamp_insertion_still_refuses_unrelated_changes(tmp_path):
    registry = tmp_path / "fixture.yaml"
    original = yaml.safe_dump({"agents": [AGENT]}, sort_keys=False)
    registry.write_text(original)
    data = yaml.safe_load(original)
    data["last_updated"] = "2026-11-01T00:00:00Z"
    data["agents"][0]["description"] = "unrelated"
    with pytest.raises(ValueError, match="unrelated"):
        save_registry(data, registry)
    assert registry.read_text() == original


@pytest.mark.parametrize(
    "original",
    [
        "# header\n  agents:\n    - id: fixture\n      autonomy_model: E\n",
        "# header\n{agents: [{id: fixture, autonomy_model: E}]}",
        "---\n&registry {agents: [{id: fixture, autonomy_model: E}]}\n...\n",
    ],
)
def test_timestamp_insertion_preserves_root_layout(tmp_path, original):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(original)
    data = yaml.safe_load(original)
    data["agents"][0]["autonomy_model"] = "D_CAPABLE"
    data["last_updated"] = "2026-11-01T00:00:00Z"
    save_registry(data, registry)
    updated = registry.read_text()
    assert yaml.safe_load(updated) == data
    timestamp = "last_updated: '2026-11-01T00:00:00Z'"
    if yaml.compose(original).flow_style:
        timestamp += ", "
    else:
        timestamp += "\n  "
    assert updated.replace(timestamp, "") == original.replace(
        "autonomy_model: E", "autonomy_model: D_CAPABLE"
    )
