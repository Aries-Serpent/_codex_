"""
Tests for Bayesian Networks PoC (Phase 4)

Validates the BayesianAssessor API:
- posterior() inference with and without evidence
- adjust_scores() blending with CODEX_BAYESIAN_MODE flag
- from_dict() and from_json() construction
"""

import json
import tempfile

import pytest

from cognitive_brain.analytics.bayesian import (
    BayesianAssessor,
    CPDTable,
    _bayesian_mode_enabled,
)

# ---------------------------------------------------------------------------
# Minimal test network fixture
# ---------------------------------------------------------------------------

NETWORK_DICT = {
    "nodes": [
        {
            "node": "risk_level",
            "parents": [],
            "values": ["low", "medium", "high"],
            "probs": {
                "": {"low": 0.4, "medium": 0.4, "high": 0.2},
            },
        },
        {
            "node": "decision",
            "parents": ["risk_level"],
            "values": ["approve", "reject", "conditional"],
            "probs": {
                "low": {"approve": 0.80, "reject": 0.05, "conditional": 0.15},
                "medium": {"approve": 0.30, "reject": 0.30, "conditional": 0.40},
                "high": {"approve": 0.10, "reject": 0.60, "conditional": 0.30},
            },
        },
    ]
}


@pytest.fixture
def assessor() -> BayesianAssessor:
    return BayesianAssessor.from_dict(NETWORK_DICT)


@pytest.fixture
def network_json_path(tmp_path) -> str:
    path = tmp_path / "test_network.json"
    path.write_text(json.dumps(NETWORK_DICT))
    return str(path)


# ---------------------------------------------------------------------------
# CPDTable
# ---------------------------------------------------------------------------


class TestCPDTable:
    def test_from_dict_root_node(self):
        data = NETWORK_DICT["nodes"][0]
        table = CPDTable.from_dict(data)
        assert table.node == "risk_level", "node is not valid"
        assert table.parents == [], "parents is not valid"
        assert table.values == ["low", "medium", "high"]
        assert table.probs[()] == {"low": 0.4, "medium": 0.4, "high": 0.2}

    def test_from_dict_child_node(self):
        data = NETWORK_DICT["nodes"][1]
        table = CPDTable.from_dict(data)
        assert table.node == "decision", "node is not valid"
        assert table.parents == ["risk_level"], "parents is not valid"
        # Key "low" becomes ("low",) tuple
        assert ("low",) in table.probs
        assert table.probs[("low",)]["approve"] == pytest.approx(0.80)

    def test_from_dict_probability_values_float(self):
        data = NETWORK_DICT["nodes"][0]
        table = CPDTable.from_dict(data)
        for v in table.probs[()].values():
            assert isinstance(v, float)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestBayesianAssessorConstruction:
    def test_from_dict(self, assessor):
        assert "risk_level" in assessor._tables, "Condition must be true"
        assert "decision" in assessor._tables, "Condition must be true"

    def test_from_json(self, network_json_path):
        a = BayesianAssessor.from_json(network_json_path)
        assert "decision" in a._tables, "Condition must be true"

    def test_from_json_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            BayesianAssessor.from_json(os.path.join(tempfile.gettempdir(), "nonexistent_network.json"))


# ---------------------------------------------------------------------------
# Inference — posterior()
# ---------------------------------------------------------------------------


class TestBayesianPoC:
    """Core PoC test cases as specified in Phase 4 plan."""

    def test_posterior_basic(self, assessor):
        """posterior() returns a normalised dict for a valid node."""
        p = assessor.posterior(evidence={"risk_level": "high"}, node="decision")
        assert set(p.keys()) == {"approve", "reject", "conditional"}
        assert sum(p.values()) == pytest.approx(1.0), "Value must be initialized"

    def test_posterior_high_risk_reject_dominant(self, assessor):
        """High risk should favour reject per the test network."""
        p = assessor.posterior(evidence={"risk_level": "high"}, node="decision")
        assert p["reject"] > p["approve"], "Value must be greater than zero"
        assert p["reject"] > p["conditional"], "Value must be greater than zero"

    def test_posterior_low_risk_approve_dominant(self, assessor):
        """Low risk should favour approve per the test network."""
        p = assessor.posterior(evidence={"risk_level": "low"}, node="decision")
        assert p["approve"] > p["reject"], "Value must be greater than zero"
        assert p["approve"] > p["conditional"], "Value must be greater than zero"

    def test_posterior_root_node_no_evidence(self, assessor):
        """Root node posterior with no evidence equals prior."""
        p = assessor.posterior(evidence={}, node="risk_level")
        assert p["low"] == pytest.approx(0.4), "Condition must be true"
        assert p["medium"] == pytest.approx(0.4), "Condition must be true"
        assert p["high"] == pytest.approx(0.2), "Condition must be true"

    def test_posterior_sum_to_one(self, assessor):
        """Posterior always sums to 1.0 (normalised)."""
        for risk in ["low", "medium", "high"]:
            p = assessor.posterior(evidence={"risk_level": risk}, node="decision")
            assert sum(p.values()) == pytest.approx(1.0), "Value must be initialized"

    def test_posterior_unknown_node_raises(self, assessor):
        with pytest.raises(KeyError):
            assessor.posterior(evidence={}, node="nonexistent")

    def test_posterior_marginalises_over_unknown_parent(self, assessor):
        """When parent is not in evidence, should marginalise gracefully."""
        p = assessor.posterior(evidence={}, node="decision")
        assert sum(p.values()) == pytest.approx(1.0), "Value must be initialized"


# ---------------------------------------------------------------------------
# adjust_scores()
# ---------------------------------------------------------------------------


class TestAdjustScores:
    """Validate adjust_scores() blending direction and behaviour."""

    def test_adjust_scores_direction(self, assessor, monkeypatch):
        """
        With CODEX_BAYESIAN_MODE=true, high-risk evidence should shift
        reject probability upward compared to the base.
        """
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")

        base = {"approve": 0.5, "reject": 0.2, "conditional": 0.3}
        adjusted = assessor.adjust_scores(
            base_probs=base,
            evidence={"risk_level": "high"},
            target_node="decision",
            alpha=0.5,
        )
        # With high risk, reject posterior=0.60 > base=0.20 → should increase
        assert adjusted["reject"] > base["reject"], "Value must be greater than zero"
        # approve posterior=0.10 < base=0.50 → should decrease
        assert adjusted["approve"] < base["approve"], "Condition must be true"

    def test_adjust_scores_disabled_returns_base(self, assessor, monkeypatch):
        """When CODEX_BAYESIAN_MODE=false, returns base unchanged."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "false")

        base = {"approve": 0.5, "reject": 0.2, "conditional": 0.3}
        adjusted = assessor.adjust_scores(
            base_probs=base,
            evidence={"risk_level": "high"},
        )
        assert adjusted == base, "adjusted is not valid"

    def test_adjust_scores_sums_to_one(self, assessor, monkeypatch):
        """Adjusted probs should remain normalised."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")

        base = {"approve": 0.4, "reject": 0.3, "conditional": 0.3}
        adjusted = assessor.adjust_scores(
            base_probs=base,
            evidence={"risk_level": "medium"},
            target_node="decision",
        )
        assert sum(adjusted.values()) == pytest.approx(1.0), "Value must be initialized"

    def test_adjust_scores_unknown_node_returns_base(self, assessor, monkeypatch):
        """Unknown target_node should return base unchanged."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        base = {"approve": 0.5, "reject": 0.5}
        adjusted = assessor.adjust_scores(base, {}, target_node="nonexistent")
        assert adjusted == base, "adjusted is not valid"

    def test_feature_flag_default_off(self, monkeypatch):
        """CODEX_BAYESIAN_MODE defaults to false."""
        monkeypatch.delenv("CODEX_BAYESIAN_MODE", raising=False)
        assert not _bayesian_mode_enabled(), "Condition must be true"

    def test_feature_flag_enabled(self, monkeypatch):
        """CODEX_BAYESIAN_MODE=true enables Bayesian blending."""
        monkeypatch.setenv("CODEX_BAYESIAN_MODE", "true")
        assert _bayesian_mode_enabled(), "Condition must be true"
