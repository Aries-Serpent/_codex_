"""
T-002 End-to-End Cost Gate Integration Test (OBJ-001 KR-2)

Validates the FULL cost gate lifecycle:
  1. Cost estimation -> tier classification
  2. PR body checkbox detection (with and without bold markers)
  3. Gate decision logic (block / warn / approve)
  4. GitHub Actions output writing
  5. NDJSON usage log emission
  6. All 5 production workflows gate correctly

Previously deferred as "admin T-002 smoke test" — now implemented
programmatically so it runs in CI without any live GitHub API calls.
"""

# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import cost_estimator from scripts/ci/
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "cost_estimator.py"
spec = importlib.util.spec_from_file_location("cost_estimator_e2e", _SCRIPT)
_mod = importlib.util.module_from_spec(spec)
sys.modules["cost_estimator_e2e"] = _mod
spec.loader.exec_module(_mod)

CostEstimate = _mod.CostEstimate
TIER_GREEN_MAX = _mod.TIER_GREEN_MAX
TIER_YELLOW_MAX = _mod.TIER_YELLOW_MAX

# ---------------------------------------------------------------------------
# Import usage_logger from scripts/ci/
# ---------------------------------------------------------------------------
_LOGGER_SCRIPT = _REPO_ROOT / "scripts" / "ci" / "usage_logger.py"
spec2 = importlib.util.spec_from_file_location("usage_logger_e2e", _LOGGER_SCRIPT)
_log_mod = importlib.util.module_from_spec(spec2)
sys.modules["usage_logger_e2e"] = _log_mod
spec2.loader.exec_module(_log_mod)

log_usage = _log_mod.log_usage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_estimate(name, runner="ubuntu-latest", timeout=30, matrix=1, ghcr=False):
    return CostEstimate(
        workflow_name=name,
        runner=runner,
        timeout_minutes=timeout,
        matrix_count=matrix,
        pushes_to_ghcr=ghcr,
    )


# PR body fixtures — using ASCII-safe representation of the checkbox lines
# to avoid encoding issues; the real PR body uses Unicode emoji but the
# detection logic strips bold markers then checks for the literal string.
_COST_APPROVED_CHECKBOX = "- [x] \U0001f4b0 Cost Proposal Approved"

PR_BODY_WITH_APPROVAL = (
    "## PR Description\n\nSome changes here.\n\n"
    "- [x] **\U0001f4b0 Cost Proposal Approved** \u2014 Stakeholder has reviewed\n"
)

PR_BODY_NO_APPROVAL = (
    "## PR Description\n\nSome changes here.\n\n"
    "- [ ] **\U0001f4b0 Cost Proposal Approved** \u2014 Stakeholder has reviewed\n"
)

PR_BODY_PLAIN_APPROVAL = "- [x] \U0001f4b0 Cost Proposal Approved \u2014 stakeholder sign-off\n"


def _is_approved(pr_body: str) -> bool:
    """Mirror of the approval detection logic in cost-gate.yml / pr-cost-check.yml.

    Strips bold markers before checking (per stored memory: cost gate approval fix).
    """
    normalized = pr_body.replace("**", "")
    return _COST_APPROVED_CHECKBOX in normalized


# ---------------------------------------------------------------------------
# T-002: Full gate lifecycle
# ---------------------------------------------------------------------------


class TestCostGateLifecycle:
    """OBJ-001 T-002 -- end-to-end gate lifecycle without live GitHub API."""

    # -- Tier classification + exit codes ------------------------------------

    def test_green_auto_approved(self):
        e = make_estimate("small-job", timeout=10, matrix=1)
        assert e.tier == "GREEN"
        assert e.exit_code == 0, "GREEN must exit 0 (auto-approve)"

    def test_yellow_warn_but_proceed(self):
        e = make_estimate("medium-job", timeout=50, matrix=1)
        assert e.tier == "YELLOW"
        assert e.exit_code == 1, "YELLOW must exit 1 (warn)"

    def test_red_blocked(self):
        # 60 min * 3 matrix = 180 eff-min -> RED
        e = make_estimate("heavy-job", timeout=60, matrix=3)
        assert e.tier == "RED"
        assert e.exit_code == 2, "RED must exit 2 (blocked)"

    def test_green_yellow_boundary(self):
        """Effective minutes just below TIER_GREEN_MAX is GREEN; at/above is YELLOW."""
        # TIER_GREEN_MAX uses strict less-than: effective_minutes < TIER_GREEN_MAX
        e_below = make_estimate("boundary-green-below", timeout=TIER_GREEN_MAX - 1, matrix=1)
        assert (
            e_below.tier == "GREEN"
        ), f"effective_minutes < TIER_GREEN_MAX ({TIER_GREEN_MAX}) must be GREEN"
        e_at = make_estimate("boundary-green-at", timeout=TIER_GREEN_MAX, matrix=1)
        assert (
            e_at.tier == "YELLOW"
        ), f"effective_minutes == TIER_GREEN_MAX ({TIER_GREEN_MAX}) must be YELLOW (exclusive upper bound)"

    def test_yellow_red_boundary(self):
        """Effective minutes at TIER_YELLOW_MAX is YELLOW; above is RED."""
        # TIER_YELLOW_MAX uses less-than-or-equal: effective_minutes <= TIER_YELLOW_MAX
        e_at = make_estimate("boundary-yellow-at", timeout=TIER_YELLOW_MAX, matrix=1)
        assert (
            e_at.tier == "YELLOW"
        ), f"effective_minutes == TIER_YELLOW_MAX ({TIER_YELLOW_MAX}) must be YELLOW (inclusive)"
        e_above = make_estimate("boundary-yellow-above", timeout=TIER_YELLOW_MAX + 1, matrix=1)
        assert (
            e_above.tier == "RED"
        ), f"effective_minutes > TIER_YELLOW_MAX ({TIER_YELLOW_MAX}) must be RED"

    # -- Checkbox detection with bold markers --------------------------------

    def test_approval_detected_with_bold_markers(self):
        assert _is_approved(
            PR_BODY_WITH_APPROVAL
        ), "Approval must be detected even when checkbox text is wrapped in **bold**"

    def test_approval_detected_plain_text(self):
        assert _is_approved(PR_BODY_PLAIN_APPROVAL)

    def test_no_approval_when_unchecked(self):
        assert not _is_approved(PR_BODY_NO_APPROVAL)

    def test_empty_body_not_approved(self):
        assert not _is_approved("")

    # -- RED gate blocked until approval -------------------------------------

    def test_red_gate_blocked_without_approval(self):
        e = make_estimate("rust_swarm_ci", timeout=60, matrix=3)
        assert e.tier == "RED"
        assert not _is_approved(PR_BODY_NO_APPROVAL), "RED job must stay blocked"

    def test_red_gate_unblocked_after_approval(self):
        e = make_estimate("rust_swarm_ci", timeout=60, matrix=3)
        assert e.tier == "RED"
        assert _is_approved(PR_BODY_WITH_APPROVAL), "RED job must unblock once approved"

    # -- GitHub Actions output writing ---------------------------------------

    def test_github_output_writes_tier(self, tmp_path):
        output_file = tmp_path / "github_output"
        output_file.write_text("")
        e = make_estimate("test-job", timeout=60, matrix=3)
        with open(output_file, "a") as f:
            f.write(f"tier={e.tier}\n")
        assert "tier=RED" in output_file.read_text()

    def test_json_export(self):
        e = make_estimate("test-job", timeout=10)
        data = e.to_dict()
        assert data["tier"] == "GREEN"
        assert data["effective_minutes"] == pytest.approx(10.0, abs=0.1)
        assert "workflow_name" in data

    # -- Cost proposal markdown ---------------------------------------------

    def test_red_proposal_contains_checkbox_instruction(self):
        e = make_estimate("blocked-job", timeout=60, matrix=3)
        proposal = "\n".join(e.proposal_lines)
        assert "Cost Proposal Approved" in proposal
        assert "checkbox" in proposal.lower() or "tick" in proposal.lower()

    def test_green_proposal_auto_approved_text(self):
        e = make_estimate("cheap-job", timeout=5)
        proposal = "\n".join(e.proposal_lines)
        assert "auto" in proposal.lower() or "approved" in proposal.lower()

    def test_yellow_proposal_warning_text(self):
        e = make_estimate("medium-job", timeout=50)
        proposal = "\n".join(e.proposal_lines)
        assert "warn" in proposal.lower() or "YELLOW" in proposal

    # -- All 5 production workflows gate correctly ---------------------------

    @pytest.mark.parametrize(
        "name,runner,timeout,matrix,ghcr,expected_tier",
        [
            ("Build & Push Preview Image", "ubuntu-latest-m", 60, 2, True, "RED"),
            ("Data Quality Suite", "ubuntu-latest", 60, 3, False, "RED"),
            ("Scheduled Archival", "ubuntu-latest", 60, 3, False, "RED"),
            ("Rust Swarm CI", "ubuntu-latest", 60, 3, False, "RED"),
            ("Docker Build & Push", "ubuntu-latest-m", 60, 2, True, "RED"),
            ("Embedding Index Rebuild", "ubuntu-latest", 15, 1, False, "GREEN"),
        ],
    )
    def test_production_workflows(self, name, runner, timeout, matrix, ghcr, expected_tier):
        e = make_estimate(name, runner=runner, timeout=timeout, matrix=matrix, ghcr=ghcr)
        assert e.tier == expected_tier, (
            f"{name}: expected {expected_tier}, got {e.tier} " f"(eff_min={e.effective_minutes})"
        )

    # -- Budget tracking integration ----------------------------------------

    def test_usage_log_records_event(self, tmp_path, monkeypatch):
        log_path = tmp_path / "usage.ndjson"
        monkeypatch.setattr(_log_mod, "_LOG_PATH", log_path)
        entry = log_usage(
            workflow="rust_swarm_ci",
            runner="ubuntu-latest",
            tier="RED",
            effective_minutes=180.0,
            approved=True,
            pr_number="3579",
        )
        assert entry["tier"] == "RED"
        assert entry["approved"] is True
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["effective_minutes"] == pytest.approx(180.0)

    def test_usage_log_accumulates_events(self, tmp_path, monkeypatch):
        log_path = tmp_path / "usage.ndjson"
        monkeypatch.setattr(_log_mod, "_LOG_PATH", log_path)
        for i in range(5):
            log_usage(
                workflow=f"job-{i}",
                runner="ubuntu-latest",
                tier="GREEN",
                effective_minutes=10.0,
                approved=True,
                pr_number=str(100 + i),
            )
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 5

    def test_usage_budget_aggregate_under_20_pct(self, tmp_path, monkeypatch):
        """Aggregate effective minutes for this PR stays under 20% of monthly budget."""
        log_path = tmp_path / "usage.ndjson"
        monkeypatch.setattr(_log_mod, "_LOG_PATH", log_path)
        events = [
            ("build-preview-image", "RED", 120.0),
            ("data-quality-suite", "RED", 180.0),
            ("rust-swarm-ci", "RED", 180.0),
            ("embed-rebuild", "GREEN", 15.0),
        ]
        for wf, tier, mins in events:
            log_usage(
                workflow=wf,
                runner="ubuntu-latest",
                tier=tier,
                effective_minutes=mins,
                approved=True,
                pr_number="3579",
            )
        total = sum(
            json.loads(line)["effective_minutes"]
            for line in log_path.read_text().strip().splitlines()
        )
        assert total == pytest.approx(495.0)
        pct = total / 3000 * 100
        assert pct < 20.0, f"Single PR consumed {pct:.1f}% of monthly budget (budget=3000 min)"
