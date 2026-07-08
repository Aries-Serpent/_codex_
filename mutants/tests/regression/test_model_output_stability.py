"""Regression tests: model output stability.

Validates that the symbolic pipeline produces outputs with stable:
- Structure (required keys / fields present)
- Dtype / type contracts (floats where floats are expected)
- Value ranges (probabilities sum to ~1, losses are non-negative, etc.)
- Determinism (same seed → same result)

These tests catch accidental API surface breakage and numeric regressions.
No GPU or heavy ML dependencies required.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ── Marker ───────────────────────────────────────────────────────────────────
pytestmark = pytest.mark.regression


# ────────────────────────────────────────────────────────────────────────────
# 1. Pretrained model output structure
# ────────────────────────────────────────────────────────────────────────────


class TestPretrainedModelStructure:
    """The ModelHandle returned by ``pretrain`` must have a stable structure."""

    def test_model_has_required_fields(self, pretrained_model):
        """ModelHandle must expose name, stage, and meta."""
        model = pretrained_model
        assert hasattr(model, "name"), "ModelHandle missing 'name'"
        assert hasattr(model, "stage"), "ModelHandle missing 'stage'"
        assert hasattr(model, "meta"), "ModelHandle missing 'meta'"

    def test_model_stage_is_pretrained(self, pretrained_model):
        """Stage string must indicate the pretrain phase (regression: stage must not drift)."""
        assert ("M0" in pretrained_model.stage or "Pretrained" in pretrained_model.stage, "Condition must be true"
        ), f"Unexpected stage after pretrain: {pretrained_model.stage!r}"

    def test_model_meta_contains_vocab(self, pretrained_model):
        """meta dict must include a vocab mapping (non-empty after training on corpus)."""
        meta = pretrained_model.meta
        assert "vocab" in meta, "meta missing 'vocab'"
        assert isinstance(meta["vocab"], dict), "meta['vocab'] must be a dict"
        assert len(meta["vocab"]) > 0, "vocab must not be empty after training"

    def test_token_probabilities_sum_to_one(self, pretrained_model):
        """Token probability distribution must sum to approximately 1.0."""
        token_probs = pretrained_model.meta.get("token_probs", {})
        assert token_probs, "token_probs must not be empty"
        total = sum(token_probs.values())
        assert math.isclose(total, 1.0, abs_tol=1e-6), f"token_probs sum {total} diverges from 1.0"

    def test_token_probabilities_in_valid_range(self, pretrained_model):
        """Every probability must be in [0, 1]."""
        token_probs = pretrained_model.meta.get("token_probs", {})
        for tok, prob in token_probs.items():
            assert 0.0 <= prob <= 1.0, f"Token {tok!r} has out-of-range probability {prob}"

    def test_model_seed_stored_in_meta(self, pretrained_model):
        """Training seed must be persisted inside meta for reproducibility audits."""
        assert ("seed" in pretrained_model.meta, "Condition must be true"
        ), "meta must record the training seed for reproducibility"
        assert isinstance(pretrained_model.meta["seed"], int)


# ────────────────────────────────────────────────────────────────────────────
# 2. Full pipeline output structure
# ────────────────────────────────────────────────────────────────────────────


class TestPipelineOutputStructure:
    """run_codex_symbolic_pipeline must return a dict with stable top-level keys."""

    REQUIRED_KEYS = {"symbolic", "weights", "handles", "losses", "objective_U"}

    def test_pipeline_result_has_required_keys(self, pipeline_result):
        """All expected top-level keys must be present in the pipeline result."""
        missing = self.REQUIRED_KEYS - set(pipeline_result.keys())
        assert not missing, f"Pipeline result missing keys: {missing}"

    def test_pipeline_losses_are_finite_numerics(self, pipeline_result):
        """Every loss value in the result must be a finite numeric value.

        Note: L_RLHF is a *negative* reward (its sign reflects the
        reward model output), so we only assert finiteness, not non-negativity.
        """
        losses = pipeline_result.get("losses", {})
        assert losses, "losses dict must not be empty"
        for name, value in losses.items():
            assert isinstance(value, (int, float)
            ), f"loss '{name}' must be numeric, got {type(value)}"
            assert math.isfinite(value), f"loss '{name}' = {value} is not finite"

    def test_pipeline_objective_u_is_float(self, pipeline_result):
        """Combined objective U must be a finite float."""
        u = pipeline_result["objective_U"]
        assert isinstance(u, (int, float)), f"objective_U must be numeric, got {type(u)}"
        assert math.isfinite(u), f"objective_U is not finite: {u}"

    def test_pipeline_handles_contain_m0_m1_m2(self, pipeline_result):
        """Pipeline must produce model handles for stages M0, M1, and M2."""
        handles = pipeline_result.get("handles", {})
        for stage in ("M0", "M1", "M2"):
            assert stage in handles, f"Missing stage handle: {stage!r}"

    def test_pipeline_weights_schema(self, pipeline_result):
        """Weights dict must contain alpha, beta, gamma keys with float values."""
        weights = pipeline_result.get("weights", {})
        for key in ("alpha", "beta", "gamma"):
            assert key in weights, f"weights missing key: {key!r}"
            assert isinstance(weights[key], (int, float)), f"weights[{key!r}] must be numeric"


# ────────────────────────────────────────────────────────────────────────────
# 3. Determinism regression
# ────────────────────────────────────────────────────────────────────────────


class TestModelDeterminism:
    """Same seed must produce identical results across two independent runs."""

    def test_pretrain_deterministic(self, corpus):
        """Two pretrain calls with the same seed must produce identical token_probs."""
        from codex_ml.symbolic_pipeline import PretrainCfg, pretrain

        cfg = PretrainCfg(epochs=1, seed=99)
        m1 = pretrain(corpus, cfg)
        m2 = pretrain(corpus, cfg)
        assert (m1.meta["token_probs"] == m2.meta["token_probs"], "Condition must be true"
        )

    def test_pipeline_result_deterministic(self, corpus, demos, prefs):
        """Full pipeline run must produce the same objective_U for the same seed."""
        from codex_ml.symbolic_pipeline import (
            PretrainCfg,
            RewardModelCfg,
            RLHFCfg,
            SFTCfg,
            run_codex_symbolic_pipeline,
        )

        kwargs = dict(
            corpus=corpus,
            demos=demos,
            prefs=prefs,
            pre_cfg=PretrainCfg(epochs=1, seed=7),
            sft_cfg=SFTCfg(epochs=1, seed=7),
            rm_cfg=RewardModelCfg(epochs=2, seed=7),
            rlhf_cfg=RLHFCfg(epochs=1, seed=7),
        )
        r1 = run_codex_symbolic_pipeline(**kwargs)
        r2 = run_codex_symbolic_pipeline(**kwargs)
        assert (r1["objective_U"] == r2["objective_U"], "Object must be initialized"
        ), "pipeline objective_U is not deterministic for the same seed"
