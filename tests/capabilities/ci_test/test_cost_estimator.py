"""
Unit tests for scripts/ci/cost_estimator.py

OBJ-001 T-001 — verifies KR-1: correct GREEN/YELLOW/RED classification
for all 5 cost-gated workflows and edge cases.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ── Import cost_estimator from scripts/ci/ ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "cost_estimator.py"

spec = importlib.util.spec_from_file_location("cost_estimator", _SCRIPT)
_mod = importlib.util.module_from_spec(spec)
sys.modules["cost_estimator"] = _mod  # register before exec so dataclass __module__ resolves
spec.loader.exec_module(_mod)

CostEstimate = _mod.CostEstimate
RUNNER_MULTIPLIERS = _mod.RUNNER_MULTIPLIERS


# ── Helper ────────────────────────────────────────────────────────────────────


def make(runner="ubuntu-latest", timeout=30, matrix=1, ghcr=False, name="Test Workflow"):
    return CostEstimate(
        workflow_name=name,
        runner=runner,
        timeout_minutes=timeout,
        matrix_count=matrix,
        pushes_to_ghcr=ghcr,
    )


# ── Tier classification ───────────────────────────────────────────────────────


class TestTierClassification:
    """GREEN / YELLOW / RED tier boundary tests (KR-1)."""

    # GREEN: < 30 effective min, no GHCR
    @pytest.mark.parametrize(
        "timeout,matrix",
        [
            (5, 1),  # 5 eff-min
            (29, 1),  # 29 eff-min — just under GREEN ceiling
            (10, 2),  # 20 eff-min
        ],
    )
    def test_green_tier(self, timeout, matrix):
        e = make(timeout=timeout, matrix=matrix)
        assert e.tier == "GREEN", "tier is not valid"
        assert e.tier_emoji == "✅", "tier_emoji is not valid"
        assert e.exit_code == 0, "exit_code is not valid"

    # Exactly at GREEN ceiling
    def test_green_boundary_exactly_30(self):
        e = make(timeout=30, matrix=1)
        # 30 eff-min = YELLOW (>= TIER_GREEN_MAX of 30)
        assert e.tier == "YELLOW", "tier is not valid"

    # YELLOW: 30–90 effective min, no GHCR
    @pytest.mark.parametrize(
        "timeout,matrix",
        [
            (30, 1),  # 30 eff-min — at YELLOW floor
            (45, 1),  # 45 eff-min
            (90, 1),  # 90 eff-min — at YELLOW ceiling
        ],
    )
    def test_yellow_tier(self, timeout, matrix):
        e = make(timeout=timeout, matrix=matrix)
        assert e.tier == "YELLOW", "tier is not valid"
        assert e.exit_code == 1, "exit_code is not valid"

    # RED: > 90 effective min
    @pytest.mark.parametrize(
        "timeout,matrix",
        [
            (91, 1),  # just over YELLOW ceiling
            (60, 2),  # 120 eff-min
            (60, 3),  # 180 eff-min
            (30, 4),  # 120 eff-min
        ],
    )
    def test_red_tier_high_minutes(self, timeout, matrix):
        e = make(timeout=timeout, matrix=matrix)
        assert e.tier == "RED", "tier is not valid"
        assert e.exit_code == 2, "exit_code is not valid"

    # RED: any GHCR push, regardless of minutes
    @pytest.mark.parametrize(
        "timeout,matrix",
        [
            (5, 1),  # would be GREEN without GHCR
            (20, 1),  # would be GREEN without GHCR
            (30, 1),  # would be YELLOW without GHCR
            (120, 3),  # already RED + GHCR
        ],
    )
    def test_red_tier_ghcr_push(self, timeout, matrix):
        e = make(timeout=timeout, matrix=matrix, ghcr=True)
        assert e.tier == "RED", "tier is not valid"

    # GREEN never triggers when GHCR push is set
    def test_no_green_when_ghcr(self):
        e = make(timeout=1, matrix=1, ghcr=True)
        assert e.tier == "RED", "tier is not valid"


# ── Runner multiplier ─────────────────────────────────────────────────────────


class TestRunnerMultiplier:
    """Effective minutes = timeout × multiplier × matrix (KR-1)."""

    def test_ubuntu_latest_multiplier_1x(self):
        e = make(runner="ubuntu-latest", timeout=30)
        assert e.multiplier == 1.0, "multiplier is not valid"
        assert e.effective_minutes == pytest.approx(30.0), "effective_minutes is not valid"

    def test_ubuntu_latest_m_multiplier_2x(self):
        e = make(runner="ubuntu-latest-m", timeout=30)
        assert e.multiplier == 2.0, "multiplier is not valid"
        assert e.effective_minutes == pytest.approx(60.0), "effective_minutes is not valid"

    def test_macos_multiplier_10x(self):
        e = make(runner="macos-latest", timeout=10)
        assert e.multiplier == 10.0, "multiplier is not valid"
        assert e.effective_minutes == pytest.approx(100.0), "effective_minutes is not valid"
        assert e.tier == "RED", "tier is not valid"

    def test_windows_multiplier_2x(self):
        e = make(runner="windows-latest", timeout=20)
        assert e.multiplier == 2.0, "multiplier is not valid"
        assert e.effective_minutes == pytest.approx(40.0), "effective_minutes is not valid"

    def test_self_hosted_zero_cost(self):
        e = make(runner="self-hosted", timeout=120, matrix=5)
        assert e.multiplier == 0.0, "multiplier is not valid"
        assert e.effective_minutes == pytest.approx(0.0), "effective_minutes is not valid"
        assert e.tier == "GREEN", "tier is not valid"

    def test_unknown_runner_defaults_to_1x(self):
        e = make(runner="some-custom-runner", timeout=30)
        assert e.multiplier == 1.0, "multiplier is not valid"


# ── Five covered workflows (KR-1 explicit verification) ──────────────────────


class TestCoveredWorkflows:
    """Verify the correct tier for each of the 5 cost-gated workflows."""

    def test_build_preview_image(self):
        """ubuntu-latest-m × 30 min × 2 matrix + GHCR push = RED."""
        e = make(
            runner="ubuntu-latest-m",
            timeout=30,
            matrix=2,
            ghcr=True,
            name="Build & Push Preview Image",
        )
        assert e.tier == "RED", "tier is not valid"
        assert e.effective_minutes == pytest.approx(120.0), "effective_minutes is not valid"

    def test_data_quality_suite(self):
        """3 jobs × 60 min = 180 eff-min = RED."""
        e = make(
            runner="ubuntu-latest",
            timeout=60,
            matrix=3,
            name="Art_Data Quality & Determinism Suite",
        )
        assert e.tier == "RED", "tier is not valid"
        assert e.effective_minutes == pytest.approx(180.0), "effective_minutes is not valid"

    def test_scheduled_archival(self):
        """3 jobs × 60 min = 180 eff-min = RED."""
        e = make(
            runner="ubuntu-latest",
            timeout=60,
            matrix=3,
            name="Scheduled Archival",
        )
        assert e.tier == "RED", "tier is not valid"
        assert e.effective_minutes == pytest.approx(180.0), "effective_minutes is not valid"

    def test_rust_swarm_ci(self):
        """3 jobs × 60 min = 180 eff-min = RED."""
        e = make(
            runner="ubuntu-latest",
            timeout=60,
            matrix=3,
            name="Rust Swarm CI",
        )
        assert e.tier == "RED", "tier is not valid"
        assert e.effective_minutes == pytest.approx(180.0), "effective_minutes is not valid"

    def test_embedding_index_rebuild(self):
        """1 job × 15 min = 15 eff-min = GREEN (but scheduled concern)."""
        e = make(
            runner="ubuntu-latest",
            timeout=15,
            matrix=1,
            name="Embedding Index Rebuild",
        )
        # 15 min < 30 GREEN threshold — correct tier is GREEN
        assert e.tier == "GREEN", "tier is not valid"
        assert e.effective_minutes == pytest.approx(15.0), "effective_minutes is not valid"


# ── Proposal markdown ─────────────────────────────────────────────────────────


class TestProposalMarkdown:
    """Proposal output contains required fields (KR-2)."""

    def test_green_proposal_contains_auto_approved(self):
        e = make(timeout=10)
        md = e.proposal_markdown
        assert "Auto-approved" in md, "Condition must be true"
        assert "GREEN" in md, "Condition must be true"

    def test_yellow_proposal_contains_warning(self):
        e = make(timeout=60)
        md = e.proposal_markdown
        assert "Warning" in md or "YELLOW" in md, "Condition must be true"

    def test_red_proposal_contains_checkbox_instruction(self):
        e = make(timeout=120, matrix=2)
        md = e.proposal_markdown
        assert "💰 Cost Proposal Approved" in md, "Condition must be true"
        assert "BLOCKED" in md, "Condition must be true"

    def test_proposal_contains_effective_minutes(self):
        e = make(timeout=45, matrix=2)
        md = e.proposal_markdown
        assert "90" in md, "Condition must be true"

    def test_to_dict_serializable(self):
        import json

        e = make(runner="ubuntu-latest-m", timeout=30, matrix=2, ghcr=True)
        d = e.to_dict()
        # Must be JSON-serializable
        dumped = json.dumps(d)
        parsed = json.loads(dumped)
        assert parsed["tier"] == "RED", "Condition must be true"
        assert parsed["effective_minutes"] == pytest.approx(120.0), "Condition must be true"
        assert parsed["multiplier"] == 2.0, "Condition must be true"


# ── Exit codes ────────────────────────────────────────────────────────────────


class TestExitCodes:
    def test_green_exit_0(self):
        assert make(timeout=10).exit_code == 0, "exit_code is not valid"

    def test_yellow_exit_1(self):
        assert make(timeout=60).exit_code == 1, "exit_code is not valid"

    def test_red_exit_2(self):
        assert make(timeout=200).exit_code == 2, "exit_code is not valid"


# ── Reason string ─────────────────────────────────────────────────────────────


class TestReasonString:
    def test_ghcr_in_reason_when_push(self):
        e = make(ghcr=True, timeout=5)
        assert "GHCR" in e.reason, "Condition must be true"

    def test_runner_in_reason_when_non_standard(self):
        e = make(runner="ubuntu-latest-m", timeout=60)
        assert "ubuntu-latest-m" in e.reason, "Condition must be true"

    def test_matrix_in_reason(self):
        e = make(matrix=4, timeout=30)
        assert "Matrix" in e.reason or "matrix" in e.reason.lower() or "4" in e.reason

    def test_low_cost_reason_clean(self):
        e = make(timeout=5)
        # Should not mention GHCR or non-standard runner
        assert "GHCR" not in e.reason, "Condition must be true"
        assert "ubuntu-latest-m" not in e.reason, "Condition must be true"
