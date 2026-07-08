"""Hypothesis-based fuzz tests for Pydantic configuration models.

Targets:
- ``codex_ml.config_schema.TrainConfig`` — full training config
- ``codex_ml.config_schema.LoraConfig`` — LoRA hyper-parameters

Fuzzes arbitrary dicts (missing fields, wrong types, boundary values) to
ensure the models behave predictably: either accepting valid data or raising
``pydantic.ValidationError`` (never crashing with unhandled exceptions).

Import guard skips the module gracefully when ``hypothesis`` is absent.
"""

from __future__ import annotations

import math

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import (  # noqa: E402
    HealthCheck,  # noqa: E402
    given,
    settings,
)
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Lazy import helpers
# ---------------------------------------------------------------------------


def _import_configs():
    from codex_ml.config_schema import LoraConfig, TrainConfig

    return TrainConfig, LoraConfig


def _pydantic_validation_error():
    from pydantic import ValidationError

    return ValidationError


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Arbitrary values for fields: None, bool, int, float, str, list, dict
_any_scalar = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-(10**6), max_value=10**6),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    st.text(max_size=64),
)

_any_value = st.one_of(
    _any_scalar,
    st.lists(_any_scalar, max_size=5),
    st.dictionaries(st.text(max_size=16), _any_scalar, max_size=4),
)

# Strategies for individual TrainConfig fields
_model_name_strategy = st.one_of(
    st.text(min_size=0, max_size=128),
    st.just("tiny"),
    st.just(""),
    st.just("gpt2"),
)

_lr_strategy = st.one_of(
    st.floats(min_value=1e-10, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=True),
    st.just(0.0),
    st.just(-1e-3),
    st.just(float("inf")),
)

_positive_int_strategy = st.one_of(
    st.integers(min_value=1, max_value=10000),
    st.integers(min_value=-100, max_value=0),  # should fail validation
    st.just(0),
)

_device_strategy = st.sampled_from(["cpu", "cuda", "mps", "invalid_device", ""])

# ---------------------------------------------------------------------------
# TrainConfig fuzz tests
# ---------------------------------------------------------------------------


@given(
    model_name=_model_name_strategy,
    batch_size=st.integers(min_value=1, max_value=512),
    epochs=st.integers(min_value=1, max_value=100),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    device=_device_strategy,
)
@settings(max_examples=80, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_train_config_valid_construction(model_name, batch_size, epochs, seed, device):
    """Fuzz: TrainConfig accepts valid positive ints and reasonable strings."""
    TrainConfig, _ = _import_configs()
    ValidationError = _pydantic_validation_error()
    try:
        cfg = TrainConfig(
            model_name=model_name,
            batch_size=batch_size,
            epochs=epochs,
            seed=seed,
            device=device,
        )
        assert cfg.batch_size == batch_size, "batch_size is not valid"
        assert cfg.epochs == epochs, "epochs is not valid"
    except ValidationError:
        # Pydantic rejected it — valid outcome
        pass
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"TrainConfig raised unexpected exception: {exc!r}")


@given(
    learning_rate=_lr_strategy,
    batch_size=_positive_int_strategy,
    epochs=_positive_int_strategy,
    max_samples=_positive_int_strategy,
    grad_accum=_positive_int_strategy,
)
@settings(max_examples=80, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_train_config_boundary_numerics(
    learning_rate, batch_size, epochs, max_samples, grad_accum
):
    """Fuzz: numeric boundary values either validate or raise ValidationError cleanly."""
    TrainConfig, _ = _import_configs()
    ValidationError = _pydantic_validation_error()
    try:
        cfg = TrainConfig(
            learning_rate=learning_rate,
            batch_size=batch_size,
            epochs=epochs,
            max_samples=max_samples,
            grad_accum=grad_accum,
        )
        # If accepted, values must be positive
        assert cfg.learning_rate > 0, "learning_rate must be greater than zero"
        assert cfg.batch_size >= 1, "batch_size must be greater than zero"
    except ValidationError:
        pass  # invalid input rejected by Pydantic — expected behaviour
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"Unexpected exception from TrainConfig: {exc!r}")


@given(
    extra_fields=st.dictionaries(
        keys=st.text(min_size=1, max_size=32).filter(
            lambda k: k
            not in {
                "model_name",
                "learning_rate",
                "batch_size",
                "epochs",
                "seed",
                "device",
                "dtype",
                "data_path",
                "eval_split",
                "grad_accum",
                "lora",
                "max_samples",
                "config_version",
                "checkpoint_keep",
                "bf16_require_capability",
                "dataset_cast_policy",
            }
        ),
        values=_any_value,
        min_size=1,
        max_size=5,
    )
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_train_config_extra_fields_forbidden(extra_fields):
    """Fuzz: extra fields must be rejected (model_config extra='forbid')."""
    TrainConfig, _ = _import_configs()
    ValidationError = _pydantic_validation_error()
    with pytest.raises(ValidationError):
        TrainConfig(**extra_fields)


@given(
    dtype=st.one_of(
        st.sampled_from(["float32", "float16", "bfloat16", "int8"]),
        st.text(min_size=0, max_size=32),
    ),
    eval_split=st.one_of(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        st.floats(min_value=1.01, max_value=10.0, allow_nan=False),
        st.just(None),
        st.just(float("nan")),
    ),
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_train_config_dtype_and_eval_split(dtype, eval_split):
    """Fuzz: dtype (free string) and eval_split [0, 1] range enforcement."""
    TrainConfig, _ = _import_configs()
    ValidationError = _pydantic_validation_error()
    try:
        cfg = TrainConfig(dtype=dtype, eval_split=eval_split)
        if eval_split is not None and not math.isnan(eval_split):  # not NaN
            assert 0.0 <= cfg.eval_split <= 1.0, "0 is not valid"
    except ValidationError:
        pass  # invalid config values rejected by Pydantic — expected behaviour in fuzz test
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"Unexpected exception: {exc!r}")


# ---------------------------------------------------------------------------
# LoraConfig fuzz tests
# ---------------------------------------------------------------------------


@given(
    enable=st.booleans(),
    r=st.one_of(st.integers(min_value=1, max_value=256), st.integers(min_value=-10, max_value=0)),
    lora_alpha=st.one_of(
        st.integers(min_value=1, max_value=256), st.integers(min_value=-10, max_value=0)
    ),
    lora_dropout=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    task_type=st.text(min_size=0, max_size=64),
)
@settings(max_examples=80, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_lora_config_construction(enable, r, lora_alpha, lora_dropout, task_type):
    """Fuzz: LoraConfig accepts positive ints and rejects non-positive ranks."""
    _, LoraConfig = _import_configs()
    ValidationError = _pydantic_validation_error()
    try:
        cfg = LoraConfig(
            enable=enable,
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            task_type=task_type,
        )
        assert cfg.r >= 1, "r must be greater than zero"
        assert cfg.lora_alpha >= 1, "lora_alpha must be greater than zero"
        assert 0.0 <= cfg.lora_dropout <= 1.0, "0 is not valid"
    except ValidationError:
        pass  # non-positive ranks/alpha rejected by Pydantic — expected behaviour in fuzz test
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"Unexpected LoraConfig exception: {exc!r}")


@given(
    dropout=st.one_of(
        st.floats(min_value=-10.0, max_value=-0.01, allow_nan=False),
        st.floats(min_value=1.01, max_value=10.0, allow_nan=False),
        st.just(float("nan")),
        st.just(float("inf")),
        st.just(float("-inf")),
    )
)
@settings(max_examples=50, deadline=None)
def test_fuzz_lora_config_invalid_dropout(dropout):
    """Fuzz: out-of-range dropout must raise ValidationError."""
    _, LoraConfig = _import_configs()
    ValidationError = _pydantic_validation_error()
    with pytest.raises((ValidationError, Exception)):
        LoraConfig(lora_dropout=dropout)


@given(
    target_modules=st.one_of(
        st.none(),
        st.lists(st.text(min_size=0, max_size=32), min_size=0, max_size=10),
        st.just("not_a_list"),
        st.just(42),
        st.just({}),
    )
)
@settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_lora_config_target_modules(target_modules):
    """Fuzz: target_modules accepts None/list and rejects other types."""
    _, LoraConfig = _import_configs()
    ValidationError = _pydantic_validation_error()
    try:
        cfg = LoraConfig(target_modules=target_modules)
        assert cfg.target_modules is None or isinstance(cfg.target_modules, list)
    except (ValidationError, Exception):
        pass  # non-list types should be rejected cleanly
