"""
Tests for Phase 3 — Ingress Gateway
(src/codex/autonomy/ingress.py)
"""

from __future__ import annotations

from codex.autonomy.ingress import (
    IngressDecision,
    IngressEvent,
    IngressGateway,
    IngressResult,
)
from codex.autonomy.registry import AutonomyMode, AutonomyRegistry


def _reg(**kwargs) -> AutonomyRegistry:
    defaults = dict(
        autonomy_mode=AutonomyMode.SAFE_AUTO,
        kill_switch=False,
        dry_run=False,
        allowed_surfaces=[],
        approval_required_classes=[],
    )
    defaults.update(kwargs)
    return AutonomyRegistry(**defaults)


def _gw(**reg_kwargs) -> IngressGateway:
    return IngressGateway(registry=_reg(**reg_kwargs))


def _event(**kwargs) -> IngressEvent:
    defaults = dict(
        event_type="issue_comment",
        actor="mbaetiong",
        source_surface="AUT-007",
    )
    defaults.update(kwargs)
    return IngressEvent(**defaults)


class TestIngressEvent:
    def test_control_class_auto_derived(self):
        evt = IngressEvent(event_type="issue_comment", actor="mbaetiong")
        assert evt.control_class == "ADVISORY_WRITE", "control_class is not valid"

    def test_control_class_override(self):
        evt = IngressEvent(
            event_type="issue_comment",
            actor="mbaetiong",
            control_class="READ_ONLY",
        )
        assert evt.control_class == "READ_ONLY", "control_class is not valid"

    def test_nonce_extracted_from_payload(self):
        evt = IngressEvent(
            event_type="push",
            actor="mbaetiong",
            payload={"nonce": "xyz123"},
        )
        assert evt.nonce == "xyz123", "nonce is not valid"

    def test_schedule_derives_read_only(self):
        evt = IngressEvent(event_type="schedule", actor="mbaetiong")
        assert evt.control_class == "READ_ONLY", "control_class is not valid"


class TestIngressGateway:
    def test_kill_switch_denies(self):
        gw = _gw(kill_switch=True)
        d = gw.evaluate(_event())
        assert not d.allowed, "Condition must be true"
        assert "kill_switch" in d.reason, "Condition must be true"

    def test_mode_off_denies(self):
        gw = _gw(autonomy_mode=AutonomyMode.OFF)
        d = gw.evaluate(_event())
        assert not d.allowed, "Condition must be true"
        assert "OFF" in d.reason, "Condition must be true"

    def test_unknown_actor_denied(self):
        gw = _gw()
        d = gw.evaluate(_event(actor="evil-bot"))
        assert not d.allowed, "Condition must be true"
        assert "allowlist" in d.reason, "Condition must be true"

    def test_known_actor_allowed(self):
        gw = _gw()
        d = gw.evaluate(_event(actor="mbaetiong"))
        assert d.allowed, "Condition must be true"

    def test_replay_nonce_denied(self):
        gw = _gw()
        evt = _event(nonce="replay-nonce-abc")
        gw.evaluate(evt)  # first pass — registers nonce
        d = gw.evaluate(evt)  # second pass — should be denied
        assert not d.allowed, "Condition must be true"
        assert "replay" in d.reason, "Condition must be true"

    def test_distinct_nonces_allowed(self):
        gw = _gw()
        d1 = gw.evaluate(_event(nonce="nonce-1"))
        d2 = gw.evaluate(_event(nonce="nonce-2"))
        assert d1.allowed, "Condition must be true"
        assert d2.allowed, "Condition must be true"

    def test_missing_event_type_denied(self):
        gw = _gw()
        evt = IngressEvent(event_type="", actor="mbaetiong")
        d = gw.evaluate(evt)
        assert not d.allowed, "Condition must be true"
        assert "schema" in d.reason, "Condition must be true"

    def test_dry_run_returns_dry_run_result(self):
        gw = _gw(dry_run=True)
        d = gw.evaluate(_event())
        assert d.is_dry_run, "Condition must be true"
        assert d.allowed, "Condition must be true"

    def test_custom_allowed_actors(self):
        gw = IngressGateway(
            registry=_reg(),
            allowed_actors=frozenset({"custom-bot"}),
        )
        d = gw.evaluate(_event(actor="custom-bot"))
        assert d.allowed, "Condition must be true"

    def test_env_actor_allowlist(self, monkeypatch):
        monkeypatch.setenv("CODEX_ALLOWED_ACTORS", "alice,bob")
        gw = IngressGateway(registry=_reg())
        assert "alice" in gw._allowed_actors, "Condition must be true"
        assert "bob" in gw._allowed_actors, "Condition must be true"

    def test_policy_version_propagated(self):
        gw = _gw()
        d = gw.evaluate(_event())
        assert d.policy_version == "blueprint-v1", "policy_version is not valid"


class TestIngressDecision:
    def test_allowed_property_allow(self):
        d = IngressDecision(
            result=IngressResult.ALLOW,
            reason="ok",
            event=_event(),
        )
        assert d.allowed, "Condition must be true"
        assert not d.is_dry_run, "Condition must be true"

    def test_allowed_property_dry_run(self):
        d = IngressDecision(
            result=IngressResult.DRY_RUN,
            reason="dry",
            event=_event(),
        )
        assert d.allowed, "Condition must be true"
        assert d.is_dry_run, "Condition must be true"

    def test_denied_not_allowed(self):
        d = IngressDecision(
            result=IngressResult.DENY,
            reason="nope",
            event=_event(),
        )
        assert not d.allowed, "Condition must be true"
