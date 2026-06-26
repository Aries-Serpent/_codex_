"""
Test Policy Mapping

Test module for policy mapping.
"""

from pathlib import Path

from codex_audit.policy import RA_RULES, build_policy_mapping, write_policy_mapping


def test_policy_mapping_includes_tracks_and_capabilities(tmp_path: Path) -> None:
    mapping = build_policy_mapping()

    assert set(RA_RULES.keys()) == {"RA-1", "RA-2", "RA-3", "RA-4", "RA-5"}
    assert mapping["capabilities"], "Capabilities should not be empty"
    assert mapping["tracks"], "Tracks should not be empty"

    track_labels = {t["track"] for t in mapping["tracks"]}
    assert track_labels == {"A", "B", "C", "D", "E", "F"}

    target = tmp_path / "policy_map.json"
    written = write_policy_mapping(target, mapping)
    assert target.exists(), "Condition must be true"
    assert written["ra_rules"] == RA_RULES, "Condition must be true"


def test_policy_capabilities_have_ra_links() -> None:
    mapping = build_policy_mapping()
    for cap in mapping["capabilities"]:
        assert cap["ra_rules"], f"Capability {cap['name']} should link to RA rules"
