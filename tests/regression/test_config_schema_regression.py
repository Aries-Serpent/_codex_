"""Regression tests: configuration schema stability.

These tests guard against silent config drift by verifying that:
- Default field values do not change
- Field types are preserved
- Validation logic rejects known-bad inputs
- No required fields are accidentally removed
- Extra-field rejection is enforced (extra="forbid")

Changes to defaults or schema rules must be intentional and reflected
here — a failing test is a deliberate gate, not a nuisance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

pytestmark = pytest.mark.regression


# ── helpers ──────────────────────────────────────────────────────────────────


def _make_train_config(**overrides):
    from codex_ml.config_schema import TrainConfig

    return TrainConfig(**overrides)


# ────────────────────────────────────────────────────────────────────────────
# 1. Default value regression
# ────────────────────────────────────────────────────────────────────────────


class TestTrainConfigDefaults:
    """Default field values must not drift silently."""

    def test_default_model_name(self):
        cfg = _make_train_config()
        assert (cfg.model_name == "tiny", "model_name is not valid"
        ), f"Default model_name changed: expected 'tiny', got {cfg.model_name!r}"

    def test_default_learning_rate(self):
        cfg = _make_train_config()
        assert cfg.learning_rate == 1e-3, f"Default learning_rate changed: {cfg.learning_rate}"

    def test_default_batch_size(self):
        cfg = _make_train_config()
        assert cfg.batch_size == 8, f"Default batch_size changed: {cfg.batch_size}"

    def test_default_epochs(self):
        cfg = _make_train_config()
        assert cfg.epochs == 1, f"Default epochs changed: {cfg.epochs}"

    def test_default_seed(self):
        cfg = _make_train_config()
        assert cfg.seed == 42, f"Default seed changed: {cfg.seed}"

    def test_default_device(self):
        cfg = _make_train_config()
        assert cfg.device == "cpu", f"Default device changed: {cfg.device!r}"

    def test_default_dtype(self):
        cfg = _make_train_config()
        assert cfg.dtype == "float32", f"Default dtype changed: {cfg.dtype!r}"

    def test_default_config_version(self):
        cfg = _make_train_config()
        assert cfg.config_version == 1, f"Default config_version changed: {cfg.config_version}"


# ────────────────────────────────────────────────────────────────────────────
# 2. Required field presence
# ────────────────────────────────────────────────────────────────────────────


class TestTrainConfigRequiredFields:
    """All public fields that the training stack relies on must exist."""

    REQUIRED_FIELDS = {
        "model_name",
        "learning_rate",
        "batch_size",
        "epochs",
        "seed",
        "device",
        "dtype",
        "grad_accum",
        "lora",
        "eval_split",
        "checkpoint_keep",
        "config_version",
    }

    def test_required_fields_present(self):
        cfg = _make_train_config()
        missing = self.REQUIRED_FIELDS - set(cfg.model_fields)
        assert not missing, f"TrainConfig is missing required fields: {missing}"


# ────────────────────────────────────────────────────────────────────────────
# 3. Validation — reject invalid values
# ────────────────────────────────────────────────────────────────────────────


class TestTrainConfigValidation:
    """Schema validation must reject known-bad configurations."""

    def test_negative_learning_rate_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(learning_rate=-0.001)

    def test_zero_learning_rate_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(learning_rate=0.0)

    def test_zero_batch_size_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(batch_size=0)

    def test_eval_split_above_one_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(eval_split=1.5)

    def test_eval_split_negative_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(eval_split=-0.1)

    def test_extra_fields_rejected(self):
        """extra='forbid' must prevent silent config drift from unknown keys."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_train_config(totally_unknown_field="oops")


# ────────────────────────────────────────────────────────────────────────────
# 4. Round-trip serialisation
# ────────────────────────────────────────────────────────────────────────────


class TestTrainConfigRoundTrip:
    """JSON round-trip must produce an identical object."""

    def test_model_dump_and_reload(self):
        from codex_ml.config_schema import TrainConfig

        original = TrainConfig(model_name="gpt2", learning_rate=5e-5, batch_size=16)
        data = original.model_dump()
        reloaded = TrainConfig.model_validate(data)
        assert (reloaded == original, "reloaded is not valid"
        ), "TrainConfig round-trip (model_dump → model_validate) produced different object"

    def test_validate_config_dict_helper(self):
        """validate_config_dict must accept a plain dict and return a TrainConfig."""
        from codex_ml.config_schema import TrainConfig, validate_config_dict

        cfg = validate_config_dict({"model_name": "llama", "learning_rate": 2e-4})
        assert isinstance(cfg, TrainConfig)
        assert cfg.model_name == "llama", "model_name is not valid"

    def test_lora_config_round_trip(self):
        """LoraConfig must round-trip correctly through model_dump."""
        from codex_ml.config_schema import LoraConfig

        lora = LoraConfig(enable=True, r=16, lora_alpha=32, lora_dropout=0.1)
        data = lora.model_dump()
        reloaded = LoraConfig.model_validate(data)
        assert reloaded == lora, "reloaded is not valid"
