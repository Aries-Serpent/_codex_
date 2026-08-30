"""
Tests for Phase 4 — Prompt Registry
(src/codex/autonomy/prompt_registry.py)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from codex.autonomy.prompt_registry import (
    PromptMetadata,
    PromptRegistry,
    PromptRegistryError,
)
from codex.autonomy.registry import AutonomyMode, ControlClass


def _write_registry(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "prompts" / "registry.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


_VALID_YAML = """
schema_version: "1.0.0"
prompts:
  - prompt_id: test-read-only
    path: .codex/prompts/test.md
    type: system
    risk_class: READ_ONLY
    consumers:
      - AUT-001
    owner: mbaetiong
    version: "2026-05-04"
    approved_for_modes:
      - OBSERVE
      - DRY_RUN
      - SAFE_AUTO
    description: "Test read-only prompt"

  - prompt_id: test-advisory
    path: .codex/prompts/advisory.md
    type: task
    risk_class: ADVISORY_WRITE
    consumers:
      - AUT-007
    owner: mbaetiong
    version: "2026-05-04"
    approved_for_modes:
      - ASSISTED
      - SAFE_AUTO
    description: "Test advisory prompt"
"""


class TestPromptMetadata:
    def test_risk_property_parses_control_class(self):
        m = PromptMetadata(
            prompt_id="x",
            path="p",
            type="system",
            risk_class="READ_ONLY",
        )
        assert m.risk == ControlClass.READ_ONLY, "risk is not valid"

    def test_risk_property_fallback_on_invalid(self):
        m = PromptMetadata(
            prompt_id="x",
            path="p",
            type="system",
            risk_class="BOGUS",
        )
        assert m.risk == ControlClass.ADVISORY_WRITE, "risk is not valid"

    def test_is_approved_for(self):
        m = PromptMetadata(
            prompt_id="x",
            path="p",
            type="system",
            risk_class="READ_ONLY",
            approved_for_modes=["OBSERVE", "DRY_RUN"],
        )
        assert m.is_approved_for(AutonomyMode.OBSERVE), "Condition must be true"
        assert m.is_approved_for(AutonomyMode.DRY_RUN), "Condition must be true"
        assert not m.is_approved_for(AutonomyMode.SAFE_AUTO), "Condition must be true"


class TestPromptRegistryLoad:
    def test_load_valid_yaml(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        assert len(reg.all_prompts()) == 2, "Collection must not be empty"
        assert reg.get("test-read-only") is not None, "Value must be initialized"

    def test_load_missing_file(self, monkeypatch):
        monkeypatch.setenv("CODEX_PROMPT_REGISTRY", "/nonexistent.yaml")
        reg = PromptRegistry.load()
        assert reg.all_prompts() == [], "Condition must be true"

    def test_get_returns_none_for_unknown(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        assert reg.get("no-such-id") is None, "Condition must be true"

    def test_by_surface(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        surface_prompts = reg.by_surface("AUT-007")
        assert any(p.prompt_id == "test-advisory" for p in surface_prompts), "prompt_id is not valid"
        assert not any(p.prompt_id == "test-read-only" for p in surface_prompts), "prompt_id is not valid"

    def test_by_risk_class(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        read_only = reg.by_risk_class(ControlClass.READ_ONLY)
        assert len(read_only) == 1, "Read_only must not be empty"
        assert read_only[0].prompt_id == "test-read-only", "prompt_id is not valid"


class TestValidation:
    def test_validate_all_passes_clean_registry(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        errors = reg.validate_all()
        assert errors == [], "Error should be raised or set"

    def test_validate_all_catches_bad_risk_class(self, tmp_path):
        yaml = (
            _VALID_YAML
            + "\n  - prompt_id: bad\n    path: x\n    type: task\n    risk_class: INVALID\n"
        )
        path = _write_registry(tmp_path, yaml)
        reg = PromptRegistry.load(path=path)
        errors = reg.validate_all()
        assert any("invalid risk_class" in e for e in errors), "Error should be raised or set"

    def test_validate_all_catches_bad_mode(self, tmp_path):
        yaml = (
            _VALID_YAML + "\n  - prompt_id: badmode\n    path: x\n    type: task\n"
            "    risk_class: READ_ONLY\n    approved_for_modes:\n      - BANANA\n"
        )
        path = _write_registry(tmp_path, yaml)
        reg = PromptRegistry.load(path=path)
        errors = reg.validate_all()
        assert any("BANANA" in e for e in errors), "Error should be raised or set"

    def test_validate_for_mode_passes_approved(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        meta = reg.get("test-read-only")
        reg.validate_for_mode(meta, AutonomyMode.OBSERVE)  # should not raise

    def test_validate_for_mode_raises_unapproved(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        meta = reg.get("test-read-only")
        with pytest.raises(PromptRegistryError, match="not approved"):
            reg.validate_for_mode(meta, AutonomyMode.ELEVATED_AUTO)

    def test_validate_for_mode_by_id(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        reg.validate_for_mode("test-advisory", AutonomyMode.SAFE_AUTO)

    def test_validate_for_mode_unknown_id_raises(self, tmp_path):
        path = _write_registry(tmp_path, _VALID_YAML)
        reg = PromptRegistry.load(path=path)
        with pytest.raises(PromptRegistryError, match="Unknown prompt_id"):
            reg.validate_for_mode("no-such", AutonomyMode.SAFE_AUTO)
