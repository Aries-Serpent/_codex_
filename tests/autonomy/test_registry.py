"""
Tests for Phase 1 — Autonomy State Registry
(src/codex/autonomy/registry.py)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from codex.autonomy.registry import (
    AutonomyMode,
    AutonomyPolicyError,
    AutonomyRegistry,
    ControlClass,
    MutationClass,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _write_registry(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "autonomy_registry.yaml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ── AutonomyMode ──────────────────────────────────────────────────────────────


class TestAutonomyMode:
    def test_level_ordering(self):
        levels = [m.level for m in AutonomyMode]
        assert levels == sorted(levels), "modes must be ordered least→most permissive"

    def test_allows_at_least(self):
        assert AutonomyMode.SAFE_AUTO.allows_at_least(AutonomyMode.OBSERVE)
        assert not AutonomyMode.OBSERVE.allows_at_least(AutonomyMode.SAFE_AUTO)
        assert AutonomyMode.ELEVATED_AUTO.allows_at_least(AutonomyMode.ELEVATED_AUTO)

    def test_off_is_most_restrictive(self):
        assert AutonomyMode.OFF.level == 0

    def test_elevated_auto_is_most_permissive(self):
        assert AutonomyMode.ELEVATED_AUTO.level == max(m.level for m in AutonomyMode)


# ── ControlClass / MutationClass alias ────────────────────────────────────────


class TestControlClass:
    def test_mutation_class_alias(self):
        assert MutationClass is ControlClass

    def test_all_classes_exist(self):
        expected = {
            "READ_ONLY",
            "PROMPT_ONLY",
            "ADVISORY_WRITE",
            "REPO_STATE_WRITE",
            "INFRA_WRITE",
            "REMOTE_EXEC",
            "EXTERNAL_BRIDGE",
        }
        assert {c.value for c in ControlClass} == expected


# ── AutonomyRegistry.load ─────────────────────────────────────────────────────


class TestAutonomyRegistryLoad:
    def test_load_defaults_when_file_missing(self, monkeypatch):
        monkeypatch.setenv("CODEX_AUTONOMY_REGISTRY", "/nonexistent/path.yaml")
        reg = AutonomyRegistry.load()
        assert reg.autonomy_mode == AutonomyMode.SAFE_AUTO
        assert not reg.kill_switch

    def test_load_from_valid_yaml(self, tmp_path):
        path = _write_registry(
            tmp_path,
            """
            schema_version: "1.0.0"
            autonomy_mode: "DRY_RUN"
            kill_switch: false
            dry_run: true
            max_iterations: 10
            budget_seconds: 600
            allowed_surfaces:
              - AUT-007
            allowed_runners:
              - ubuntu-latest
            approval_required_classes:
              - INFRA_WRITE
            """,
        )
        reg = AutonomyRegistry.load(path=path)
        assert reg.autonomy_mode == AutonomyMode.DRY_RUN
        assert reg.dry_run is True
        assert reg.max_iterations == 10
        assert "AUT-007" in reg.allowed_surfaces
        assert "INFRA_WRITE" in reg.approval_required_classes

    def test_load_unknown_mode_defaults_to_safe_auto(self, tmp_path):
        path = _write_registry(tmp_path, "autonomy_mode: BANANA\n")
        reg = AutonomyRegistry.load(path=path)
        assert reg.autonomy_mode == AutonomyMode.SAFE_AUTO

    def test_load_empty_yaml_uses_defaults(self, tmp_path):
        path = tmp_path / "empty.yaml"
        path.write_text("", encoding="utf-8")
        reg = AutonomyRegistry.load(path=path)
        assert reg.autonomy_mode == AutonomyMode.SAFE_AUTO


# ── AutonomyRegistry.is_permitted ─────────────────────────────────────────────


class TestIsPermitted:
    def _reg(self, **kwargs) -> AutonomyRegistry:
        defaults = dict(
            autonomy_mode=AutonomyMode.SAFE_AUTO,
            kill_switch=False,
            dry_run=False,
            allowed_surfaces=["AUT-007"],
            approval_required_classes=[],
        )
        defaults.update(kwargs)
        return AutonomyRegistry(**defaults)

    def test_kill_switch_denies_all(self):
        reg = self._reg(kill_switch=True)
        allowed, reason = reg.is_permitted("AUT-007", ControlClass.READ_ONLY)
        assert not allowed
        assert "kill_switch" in reason

    def test_surface_not_in_allowlist(self):
        reg = self._reg(allowed_surfaces=["AUT-001"])
        allowed, reason = reg.is_permitted("AUT-007", ControlClass.READ_ONLY)
        assert not allowed
        assert "allowed_surfaces" in reason

    def test_mode_floor_denied(self):
        # OBSERVE mode cannot do INFRA_WRITE
        reg = self._reg(autonomy_mode=AutonomyMode.OBSERVE, allowed_surfaces=[])
        allowed, reason = reg.is_permitted("AUT-007", ControlClass.INFRA_WRITE)
        assert not allowed
        assert "INFRA_WRITE" in reason or "ELEVATED_AUTO" in reason

    def test_approval_required_class_denied(self):
        reg = self._reg(approval_required_classes=["ADVISORY_WRITE"])
        allowed, reason = reg.is_permitted("AUT-007", ControlClass.ADVISORY_WRITE)
        assert not allowed
        assert "approval" in reason.lower()

    def test_read_only_allowed_in_observe(self):
        reg = self._reg(autonomy_mode=AutonomyMode.OBSERVE, allowed_surfaces=[])
        allowed, _ = reg.is_permitted("any", ControlClass.READ_ONLY)
        assert allowed

    def test_dry_run_returns_allowed_with_note(self):
        reg = self._reg(dry_run=True, allowed_surfaces=[])
        allowed, reason = reg.is_permitted("AUT-007", ControlClass.ADVISORY_WRITE)
        assert allowed
        assert "dry_run" in reason

    def test_invalid_control_class_denied(self):
        reg = self._reg(allowed_surfaces=[])
        allowed, _ = reg.is_permitted("AUT-007", "INVALID_CLASS")
        assert not allowed

    def test_assert_permitted_raises_on_deny(self):
        reg = self._reg(kill_switch=True)
        with pytest.raises(AutonomyPolicyError):
            reg.assert_permitted("AUT-007", ControlClass.READ_ONLY)

    def test_assert_permitted_passes_on_allow(self):
        reg = self._reg(allowed_surfaces=[])
        # Should not raise
        reg.assert_permitted("AUT-007", ControlClass.READ_ONLY)

    def test_empty_surface_allowlist_allows_all(self):
        reg = self._reg(allowed_surfaces=[])
        allowed, _ = reg.is_permitted("any-surface", ControlClass.READ_ONLY)
        assert allowed


# ── effective_mode / is_off ───────────────────────────────────────────────────


class TestEffectiveMode:
    def test_effective_mode_off_when_kill_switch(self):
        reg = AutonomyRegistry(kill_switch=True, autonomy_mode=AutonomyMode.SAFE_AUTO)
        assert reg.effective_mode == AutonomyMode.OFF
        assert reg.is_off

    def test_effective_mode_passes_through_normally(self):
        reg = AutonomyRegistry(kill_switch=False, autonomy_mode=AutonomyMode.DRY_RUN)
        assert reg.effective_mode == AutonomyMode.DRY_RUN
        assert not reg.is_off
