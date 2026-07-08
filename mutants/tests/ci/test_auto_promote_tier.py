"""
Tests for auto_promote_tier.py — specifically the AUTO_PROMOTE_TIER_ENABLED
guard and the _apply_promotion() write path (W-098 / Priority-3 pre-req).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "ci"))

import auto_promote_tier  # noqa: I001

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_registry(tmp_path: Path, agents: list[dict]) -> Path:
    """Write a minimal AGENT_REGISTRY.yaml to *tmp_path* and return its path."""
    registry_path = tmp_path / "AGENT_REGISTRY.yaml"
    data = {"agents": agents}
    registry_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return registry_path


def _make_agent(agent_id: str, tier: str, status: str = "active") -> dict:
    return {"id": agent_id, "enforcement_tier": tier, "status": status}


# ---------------------------------------------------------------------------
# _load_soft_agents
# ---------------------------------------------------------------------------


class TestLoadSoftAgents:
    def test_returns_empty_when_no_registry(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.yaml"
        with patch.object(auto_promote_tier, "REGISTRY_PATH", missing):
            result = auto_promote_tier._load_soft_agents()
        assert result == [], "Result must not be empty"

    def test_returns_only_soft_active_agents(self, tmp_path: Path) -> None:
        registry = _make_registry(
            tmp_path,
            [
                _make_agent("agent-soft", "SOFT"),
                _make_agent("agent-partial", "PARTIAL"),
                _make_agent("agent-grounded", "GROUNDED"),
                _make_agent("agent-soft-inactive", "SOFT", status="inactive"),
            ],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            result = auto_promote_tier._load_soft_agents()

        ids = [a["id"] for a in result]
        assert ids == ["agent-soft"], "ids is not valid"

    def test_returns_multiple_soft_active_agents(self, tmp_path: Path) -> None:
        registry = _make_registry(
            tmp_path,
            [
                _make_agent("agent-a", "SOFT"),
                _make_agent("agent-b", "SOFT"),
                _make_agent("agent-c", "PARTIAL"),
            ],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            result = auto_promote_tier._load_soft_agents()

        assert len(result) == 2, "Result must not be empty"


# ---------------------------------------------------------------------------
# _apply_promotion — write path
# ---------------------------------------------------------------------------


class TestApplyPromotion:
    def test_promotes_soft_agents_in_registry(self, tmp_path: Path) -> None:
        """Write path updates enforcement_tier SOFT → PARTIAL in AGENT_REGISTRY.yaml."""
        registry = _make_registry(
            tmp_path,
            [
                _make_agent("ci-testing-agent", "SOFT"),
                _make_agent("workflow-ci-fixer", "PARTIAL"),
            ],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            updated = auto_promote_tier._apply_promotion(["ci-testing-agent"])

        assert updated == 1, "updated is not valid"
        data = yaml.safe_load(registry.read_text())
        tiers = {a["id"]: a["enforcement_tier"] for a in data["agents"]}
        assert tiers["ci-testing-agent"] == auto_promote_tier.TARGET_TIER, "Condition must be true"
        assert tiers["workflow-ci-fixer"] == "PARTIAL", "Condition must be true"

    def test_ignores_non_soft_agents(self, tmp_path: Path) -> None:
        """Non-SOFT agents are skipped even if listed in agent_ids."""
        registry = _make_registry(
            tmp_path,
            [
                _make_agent("grounded-agent", "GROUNDED"),
                _make_agent("partial-agent", "PARTIAL"),
            ],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            updated = auto_promote_tier._apply_promotion(["grounded-agent", "partial-agent"])

        assert updated == 0, "updated is not valid"

    def test_returns_zero_when_registry_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.yaml"
        with patch.object(auto_promote_tier, "REGISTRY_PATH", missing):
            updated = auto_promote_tier._apply_promotion(["any-agent"])
        assert updated == 0, "updated is not valid"

    def test_promotes_multiple_agents(self, tmp_path: Path) -> None:
        registry = _make_registry(
            tmp_path,
            [
                _make_agent("agent-a", "SOFT"),
                _make_agent("agent-b", "SOFT"),
                _make_agent("agent-c", "GROUNDED"),
            ],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            updated = auto_promote_tier._apply_promotion(["agent-a", "agent-b"])

        assert updated == 2, "updated is not valid"
        data = yaml.safe_load(registry.read_text())
        tiers = {a["id"]: a["enforcement_tier"] for a in data["agents"]}
        assert tiers["agent-a"] == auto_promote_tier.TARGET_TIER, "Condition must be true"
        assert tiers["agent-b"] == auto_promote_tier.TARGET_TIER, "Condition must be true"
        assert tiers["agent-c"] == "GROUNDED", "Condition must be true"

    def test_preserves_key_order(self, tmp_path: Path) -> None:
        """sort_keys=False preserves original YAML key order after write."""
        registry = _make_registry(
            tmp_path,
            [{"id": "agent-soft", "enforcement_tier": "SOFT", "status": "active"}],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            auto_promote_tier._apply_promotion(["agent-soft"])

        text = registry.read_text()
        # "id:" should appear before "enforcement_tier:" (original order preserved)
        assert text.index("id:") < text.index("enforcement_tier:"), "Condition must be true"


# ---------------------------------------------------------------------------
# AUTO_PROMOTE_TIER_ENABLED guard — run() integration
# ---------------------------------------------------------------------------


class TestAutoPromoteTierGuard:
    def test_guard_disabled_by_default(self) -> None:
        """_AUTO_PROMOTE_ENABLED is False when AUTO_PROMOTE_TIER_ENABLED env var is absent."""
        import importlib

        with patch.dict("os.environ", {}, clear=True):
            # Reload the module so it re-evaluates the module-level constant
            # without the env var set — should default to False.
            reloaded = importlib.reload(auto_promote_tier)

        assert reloaded._AUTO_PROMOTE_ENABLED is False, "_AUTO_PROMOTE_ENABLED is not valid"

    def test_run_dry_run_when_guard_disabled(self, tmp_path: Path, capsys) -> None:
        """run() prints dry-run stubs, does NOT call _apply_promotion when guard=false."""
        registry = _make_registry(
            tmp_path,
            [_make_agent("agent-soft", "SOFT")],
        )
        with (
            patch.object(auto_promote_tier, "REGISTRY_PATH", registry),
            patch.object(auto_promote_tier, "_AUTO_PROMOTE_ENABLED", False),
            patch.object(auto_promote_tier, "_get_violation_count", return_value=0),
            patch.object(auto_promote_tier, "_apply_promotion") as mock_apply,
        ):
            auto_promote_tier.run()

        mock_apply.assert_not_called()

    def test_run_write_path_when_guard_enabled(self, tmp_path: Path) -> None:
        """run() calls _apply_promotion when AUTO_PROMOTE_TIER_ENABLED=true."""
        registry = _make_registry(
            tmp_path,
            [_make_agent("agent-soft", "SOFT")],
        )
        with (
            patch.object(auto_promote_tier, "REGISTRY_PATH", registry),
            patch.object(auto_promote_tier, "_AUTO_PROMOTE_ENABLED", True),
            patch.object(auto_promote_tier, "_get_violation_count", return_value=0),
            patch.object(auto_promote_tier, "_apply_promotion", return_value=1) as mock_apply,
        ):
            count = auto_promote_tier.run()

        mock_apply.assert_called_once_with(["agent-soft"])
        assert count == 1, "Count must be greater than zero"

    def test_run_no_soft_agents_exits_cleanly(self, tmp_path: Path, capsys) -> None:
        """run() returns 0 and prints success message when no SOFT agents."""
        registry = _make_registry(
            tmp_path,
            [_make_agent("grounded-agent", "GROUNDED")],
        )
        with patch.object(auto_promote_tier, "REGISTRY_PATH", registry):
            count = auto_promote_tier.run()

        assert count == 0, "Count must be greater than zero"
        captured = capsys.readouterr()
        assert "No SOFT-tier active agents found" in captured.out, "Condition must be true"

    def test_run_violations_skips_promotion(self, tmp_path: Path, capsys) -> None:
        """Agents with violations are not included in promotable list."""
        registry = _make_registry(
            tmp_path,
            [_make_agent("agent-with-violations", "SOFT")],
        )
        with (
            patch.object(auto_promote_tier, "REGISTRY_PATH", registry),
            patch.object(auto_promote_tier, "_get_violation_count", return_value=5),
            patch.object(auto_promote_tier, "_apply_promotion") as mock_apply,
        ):
            auto_promote_tier.run()

        mock_apply.assert_not_called()


# ---------------------------------------------------------------------------
# Source/target tier constants
# ---------------------------------------------------------------------------


class TestTierConstants:
    def test_source_tier_is_soft(self) -> None:
        assert auto_promote_tier.SOURCE_TIER == "SOFT", "SOURCE_TIER is not valid"

    def test_target_tier_is_partial(self) -> None:
        assert auto_promote_tier.TARGET_TIER == "PARTIAL", "TARGET_TIER is not valid"
