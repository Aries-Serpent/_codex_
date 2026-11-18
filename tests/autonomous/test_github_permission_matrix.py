"""Tests for the 360-degree GitHub write-permission azimuth plan."""

from scripts.autonomous.credential_probe import safe_contents_write_probe
from scripts.autonomous.github_permission_matrix import (
    WRITE_PERMISSION_PROBES,
    azimuth_write_plan,
)

EXPECTED_PERMISSION_FAMILIES = {
    "contents",
    "pull_requests",
    "issues",
    "actions",
    "checks",
    "statuses",
    "releases",
    "deployments",
    "discussions",
    "variables",
    "secrets",
    "webhooks",
    "security_events",
    "administration",
}


def test_azimuth_covers_all_write_permission_families() -> None:
    assert {probe.permission_family for probe in WRITE_PERMISSION_PROBES} == (
        EXPECTED_PERMISSION_FAMILIES
    )


def test_every_write_probe_has_adversarial_preflight_and_rollback() -> None:
    for probe in WRITE_PERMISSION_PROBES:
        assert probe.preflight
        assert probe.live_probe
        assert probe.rollback
        assert probe.execution == "dry_run_only"
        assert probe.risk in {"low", "medium", "high", "critical"}


def test_high_risk_probes_are_blocked_until_specific_controls_exist() -> None:
    for probe in WRITE_PERMISSION_PROBES:
        if probe.risk in {"high", "critical"}:
            assert probe.blocked_by, probe.capability


def test_safe_contents_write_has_no_visible_ref_change(monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.autonomous.credential_probe.request_json",
        lambda *args, **kwargs: {"status": 201, "payload": {"sha": "deadbeef"}},
    )

    result = safe_contents_write_probe("dummy-token")

    assert result["write_verified"] is True
    assert result["visible_ref_changed"] is False
    assert result["blob_sha"] == "deadbeef"
    assert result["marker_in_report"] is False


def test_azimuth_plan_disables_live_writes_by_default() -> None:
    plan = azimuth_write_plan()

    assert plan["live_write_enabled"] is False
    assert plan["execution_default"] == "dry_run_only"
    assert plan["probe_count"] == len(WRITE_PERMISSION_PROBES)
    assert "claim permission from repository role metadata alone" in plan["forbidden_fallbacks"]
