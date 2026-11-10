"""Tests of offline CDX startup discovery, separate from scanner preflight tests."""

from __future__ import annotations

import copy
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from detect_secrets.plugins.keyword import KeywordDetector

from scripts.archive import cdx_common as common
from scripts.ci import cdx_context, startup_health


@pytest.mark.parametrize("package_mode", [False, True])
def test_startup_health_import_modes(tmp_path, package_mode):
    root = Path(startup_health.__file__).resolve().parents[2]
    packet = tmp_path / "packet.json"
    packet.write_text("{}")
    entrypoint = (
        ["-m", "scripts.ci.startup_health"]
        if package_mode
        else [str(Path(startup_health.__file__))]
    )
    refreshed = subprocess.run(
        [sys.executable, *entrypoint, "--refresh-context", "--output", str(packet)],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert refreshed.returncode == 0
    validated = subprocess.run(
        [sys.executable, *entrypoint, "--validate", "--output", str(packet)],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "validated (offline)" in validated.stdout


def test_catalog_is_complete_deterministic_and_offline(monkeypatch):
    def forbidden(*_, **__):
        raise AssertionError("discovery must not execute tools or access network")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(Path, "iterdir", forbidden)
    monkeypatch.setattr(Path, "glob", forbidden)
    monkeypatch.setattr(Path, "rglob", forbidden)
    catalog = cdx_context.build_cdx_context()
    assert catalog == cdx_context.build_cdx_context()
    assert set(catalog["cdx_module_index"]) == {
        "common",
        "preflight",
        "review",
        "adapter",
        "packer",
        "query",
        "rehydrate",
        "gitleaks_adapter",
    }
    for entry in catalog["cdx_module_index"].values():
        assert entry["exported_signatures"]
        lines = (cdx_context.ROOT / entry["path"]).read_text().splitlines()
        for symbol, location in entry["functions"].items():
            assert symbol.split(".")[-1] in lines[location["line"] - 1]
            assert location["location"] == f"{entry['path']}:{location['line']}"
            assert location["signature"]
    candidate = catalog["skills_registry"]["agent_candidates"][0]
    assert candidate["discoverable"]
    assert candidate["status"] == "local_profile"
    assert candidate["path"] == ".github/agents/cdx-archive-lifecycle.agent.md"
    assert candidate["hosted_activation"] == "not_established"
    assert candidate["authorization"] == "none_granted"
    assert candidate["id"] == "cdx-archive-lifecycle"
    candidate_skill = next(
        skill
        for skill in catalog["skills_registry"]["skills"]
        if skill["id"] == "cdx-archive-lifecycle"
    )
    assert candidate_skill["kind"] == "agent_profile"
    assert candidate_skill["availability"] == "local_profile"
    assert candidate_skill["hosted_activation"] == "not_established"


def test_registered_profile_and_catalog_contracts():
    root = cdx_context.ROOT
    text = (root / cdx_context.CANDIDATE).read_text()
    _, header, body = text.split("---", 2)
    profile = yaml.safe_load(header)
    assert profile["name"] == "CDX Archive Lifecycle"
    assert isinstance(profile["description"], str) and profile["description"].strip()
    assert profile["tools"] == ["read", "search", "execute", "edit"]
    assert "model" not in profile
    assert "target" not in profile
    assert len(body) <= 30_000
    assert not (root / cdx_context.LEGACY_CANDIDATE).exists()
    registry = yaml.safe_load((root / ".github/agents/AGENT_REGISTRY.yaml").read_text())
    entries = [row for row in registry["agents"] if row["id"] == cdx_context.CANDIDATE_ID]
    assert len(entries) == 1
    assert entries[0]["name"] == profile["name"]
    assert entries[0]["file"] == cdx_context.CANDIDATE
    assert entries[0]["directory"] == ".github/agents"
    assert entries[0]["status"] == "active"
    assert registry["total_agents"] == len(registry["agents"])
    assert registry["active_agents"] == sum(row["status"] == "active" for row in registry["agents"])
    assert registry["archived_agents"] == sum(
        row["status"] == "archived" for row in registry["agents"]
    )


def test_missing_explicit_profile_rejects_decoy(tmp_path, monkeypatch):
    original_is_file = Path.is_file

    def missing_profile(path):
        if path == cdx_context.ROOT / cdx_context.CANDIDATE:
            return False
        return original_is_file(path)

    decoy = tmp_path / Path(cdx_context.CANDIDATE).name
    decoy.write_text("---\nname: CDX Archive Lifecycle\ndescription: decoy\n---\n")
    monkeypatch.setattr(Path, "is_file", missing_profile)
    with pytest.raises(ValueError, match="CDX local profile missing"):
        cdx_context.build_cdx_context()


def test_refresh_removes_stale_cdx_candidate_identity():
    packet = startup_health.build_packet({}, {})
    stale = [
        {"id": cdx_context.CANDIDATE_ID, "path": "other/location.agent.md"},
        {"path": cdx_context.LEGACY_CANDIDATE, "status": "staged_candidate"},
    ]
    packet["skills_registry"]["agent_candidates"].extend(stale)
    cdx_context.refresh_cdx_context(packet)
    startup_health.validate_packet(packet)
    candidates = packet["skills_registry"]["agent_candidates"]
    assert len(candidates) == 1
    assert candidates[0]["path"] == cdx_context.CANDIDATE
    assert candidates[0]["hosted_activation"] == "not_established"
    assert candidates[0]["authorization"] == "none_granted"


def test_generated_alias_baseline_is_exact_and_not_an_archive_approval():
    alias = cdx_context.build_cdx_context()["cdx_common_preflight"]["name_clarifications"][
        "run_secret_scanner"
    ]
    baseline = json.loads((cdx_context.ROOT / ".secrets.baseline").read_text())
    rows = baseline["results"][".codex/session_startup_packet.json"]
    assert len(rows) == 1
    assert rows[0]["type"] == "Secret Keyword"
    assert alias == "compatibility_alias_of_run_secret_scanners"
    expected = "c5162f254563733e6a9d2c28a44921ee91c682ea"  # pragma: allowlist secret
    assert rows[0]["hashed_secret"] == expected
    assert rows[0]["is_secret"] is False
    assert rows[0]["is_verified"] is False
    changed = KeywordDetector().analyze_line(
        ".codex/session_startup_packet.json", f'"run_secret_scanner": "{alias}_changed"'
    )
    assert changed
    assert all(finding.secret_hash != rows[0]["hashed_secret"] for finding in changed)


def test_common_preflight_maps_requested_functions_and_nonexistent_names():
    preflight = cdx_context.build_cdx_context()["cdx_common_preflight"]
    assert set(preflight["functions"]) >= {
        "inspect_text",
        "compute_merkle_root",
        "_canonical_scanner_finding",
        "_validate_external_path",
        "pack_archive",
        "CodexArchiveQuery",
        "rehydrate_archive",
        "verify_archive",
        "run_secret_scanners",
    }
    assert preflight["name_clarifications"]["pack_directory"] == "does_not_exist_use_pack_archive"
    assert preflight["name_clarifications"]["run_secret_scanner"] == (
        "compatibility_alias_of_run_secret_scanners"
    )


def test_cli_contracts_are_actual_parser_subcommands_and_options():
    index = cdx_context.build_cdx_context()["cdx_module_index"]
    assert set(index["query"]["cli_contract"]["subcommands"]) == {
        "info",
        "list",
        "read",
        "search",
        "symbols",
        "callgraph",
        "context",
    }
    assert set(index["rehydrate"]["cli_contract"]["subcommands"]) == {
        "verify",
        "extract",
        "compare",
    }
    assert index["rehydrate"]["cli"] == (
        "python -m scripts.archive.codex_rehydrate extract ARCHIVE.cdx.sqlite DESTINATION"
    )
    preflight_options = {
        name
        for argument in index["preflight"]["cli_contract"]["root"]["arguments"]
        for name in argument["names"]
    }
    assert {"--preflight-summary", "--json", "--assess-acquired-batch"} <= preflight_options
    assert index["gitleaks_adapter"]["cli_contract"]["root"]["stdin"] == "owner_only_request_json"


def test_packet_generator_and_validator_persist_catalog():
    packet = startup_health.build_packet({"branch_drift_severity": "LOW"}, {})
    startup_health.validate_packet(packet)
    assert packet["skills_registry"] == cdx_context.build_cdx_context()["skills_registry"]
    for field in ("skills_registry", "cdx_module_index", "cdx_common_preflight"):
        altered = copy.deepcopy(packet)
        del altered[field]
        with pytest.raises(ValueError, match="missing or stale"):
            startup_health.validate_packet(altered)
    altered = copy.deepcopy(packet)
    altered["cdx_module_index"]["adapter"]["functions"]["list_batches"]["line"] = 1
    with pytest.raises(ValueError, match="missing or stale"):
        startup_health.validate_packet(altered)
    altered = copy.deepcopy(packet)
    altered["skills_registry"]["schema_version"] = True
    with pytest.raises(ValueError, match="missing or stale"):
        startup_health.validate_packet(altered)


def test_checked_in_packet_catalog_is_current():
    startup_health.validate_packet(json.loads(startup_health.PACKET.read_text()))


def test_registry_preserves_unrelated_skills_and_candidates():
    packet = startup_health.build_packet({"branch_drift_severity": "LOW"}, {})
    skill = {"id": "unrelated_skill", "availability": "local_source", "cli": "other"}
    candidate = {"path": "other/candidate.md", "status": "unverified"}
    registry = packet["skills_registry"]
    registry["skills"].insert(0, skill)
    registry["agent_candidates"].append(candidate)
    registry["other_metadata"] = {"unchanged": True}
    startup_health.validate_packet(packet)
    cdx_context.refresh_cdx_context(packet)
    startup_health.validate_packet(packet)
    assert skill in packet["skills_registry"]["skills"]
    assert candidate in packet["skills_registry"]["agent_candidates"]
    assert packet["skills_registry"]["other_metadata"] == {"unchanged": True}


def test_refresh_preserves_health_fields_and_timestamp(tmp_path, capsys):
    packet = {"generated_at": "unchanged", "status": "historical", "ci_failure_rate": 7.3}
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet))
    assert startup_health.main(["--refresh-context", "--output", str(path)]) == 0
    refreshed = json.loads(path.read_text())
    assert all(refreshed[key] == value for key, value in packet.items())
    assert startup_health.main(["--validate", "--output", str(path)]) == 0
    del refreshed["skills_registry"]
    path.write_text(json.dumps(refreshed))
    assert startup_health.main(["--validate", "--output", str(path)]) == 2
    assert "BLOCKED" in capsys.readouterr().out


@pytest.mark.parametrize("raw", ["[]", "null", "{broken"])
def test_validator_rejects_malformed_packet(tmp_path, raw, capsys):
    path = tmp_path / "packet.json"
    path.write_text(raw)
    assert startup_health.main(["--validate", "--output", str(path)]) == 2
    assert "BLOCKED" in capsys.readouterr().out


def test_common_preflight_context_is_read_only_and_not_scanner_clearance(tmp_path, monkeypatch):
    archive = tmp_path / ".codex" / "archive"
    archive.mkdir(parents=True)
    documents = {
        "MANIFEST.json": json.dumps({"total_files": 1, "files": ["fixture.txt"]}),
        "ARCHIVE_LEDGER.jsonl": '{"path":"fixture.txt"}\n',
        "ARCHIVE_INDEX.md": "# Archive\n## Fixture\n",
    }
    for name, text in documents.items():
        (archive / name).write_text(text)

    def forbidden(*_, **__):
        raise AssertionError("context must not scan, pack or use the network")

    monkeypatch.setattr(common.shutil, "which", lambda _: None)
    monkeypatch.setattr(common.subprocess, "run", forbidden)
    monkeypatch.setattr(common, "run_secret_scanners", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    result = common.run_cdx_common_preflight(tmp_path)
    assert result["purpose"] == "read_only_context_not_secret_clearance"
    assert result["tools"]["gitleaks"]["status"] == "missing"
    assert result["archive"]["manifest"]["listed_files"] == 1
    assert result["archive"]["ledger"]["records"] == 1
    assert result["archive"]["index"]["headings"] == 2
    assert result["functions"]
    assert (
        next(row for row in result["functions"] if row["name"] == "run_cdx_common_preflight")[
            "path"
        ]
        == "scripts/archive/cdx_common.py"
    )
    assert {path.name: path.read_text() for path in archive.iterdir()} == documents


def test_common_context_reports_missing_and_malformed_archive(tmp_path, monkeypatch):
    archive = tmp_path / ".codex" / "archive"
    archive.mkdir(parents=True)
    (archive / "MANIFEST.json").write_text('{"files": null}')
    monkeypatch.setattr(common.shutil, "which", lambda _: None)
    result = common.run_cdx_common_preflight(tmp_path)
    assert result["archive"]["manifest"]["status"] == "unavailable_or_malformed"
    assert result["archive"]["ledger"]["status"] == "missing"
    assert result["archive"]["index"]["status"] == "missing"


def test_common_context_json_cli(monkeypatch, capsys):
    monkeypatch.setattr(
        common,
        "run_cdx_common_preflight",
        lambda: {"purpose": "read_only_context_not_secret_clearance"},
    )
    assert common.main(["--preflight-context", "--json"]) == 0
    assert (
        json.loads(capsys.readouterr().out)["purpose"] == "read_only_context_not_secret_clearance"
    )
