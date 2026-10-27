"""Contract regressions for the actual Phase 7B batch-2 module APIs.

Prior art: tests/tracking/test_mlflow_guard.py, tests/test_peft_hooks.py,
tests/test_dp_config.py, tests/test_rng_checkpoint.py, and
docs/safety/differential_privacy.md. These modules provide guard functions,
quantum state primitives, PEFT helpers, shared security types, differential
privacy configuration, and RNGState -- not the speculative classes formerly
imported here. Optional integrations are tested at their dependency boundaries.
"""

from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from codex_ml.interfaces import peft_hooks
from codex_ml.tracking import mlflow_guard
from codex_ml.training import dp_config, rng_checkpoint
from cognitive_brain.quantum.base import (
    CoherenceDegradationError,
    InvalidQuantumConfigurationError,
    QuantumException,
    QuantumFeature,
    QuantumState,
)
from security._types import SecurityError, sanitize_text


@pytest.fixture
def isolated_guard(monkeypatch, tmp_path):
    """Guard calls may mutate the environment and last-decision singleton."""
    for key in (
        "MLFLOW_TRACKING_URI",
        "CODEX_MLFLOW_URI",
        "MLFLOW_ALLOW_REMOTE",
        "CODEX_ALLOW_REMOTE_TRACKING",
        "CODEX_MLFLOW_ALLOW_REMOTE",
        "MLFLOW_ENABLE_SYSTEM_METRICS",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "true")
    monkeypatch.setenv("CODEX_MLFLOW_LOCAL_DIR", str(tmp_path / "mlruns"))
    monkeypatch.setattr(mlflow_guard, "_LAST_DECISION", None)
    return tmp_path / "mlruns"


class TestMLflowGuard:
    def test_default_local_backend_and_decision(self, isolated_guard):
        decision = mlflow_guard.ensure_file_backend_decision()
        assert decision.effective_uri == isolated_guard.as_uri()
        assert isolated_guard.is_dir()
        assert decision.uri == decision.effective_uri
        assert decision.requested_uri == str(isolated_guard)
        assert decision.fallback_reason is None
        assert decision.allow_remote is False
        assert decision.allow_remote_env == "MLFLOW_ALLOW_REMOTE"
        assert mlflow_guard.last_decision() is decision
        for key in ("MLFLOW_TRACKING_URI", "CODEX_MLFLOW_URI"):
            assert os.environ[key] == decision.uri
        assert os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] == "false"
        assert decision.system_metrics_enabled is False
        with pytest.raises(FrozenInstanceError):
            decision.effective_uri = "https://remote.invalid"

    @pytest.mark.parametrize("uri", ["https://remote.invalid/runs", "sqlite:///runs.db"])
    def test_remote_backend_rejected_by_default(self, isolated_guard, uri):
        decision = mlflow_guard.ensure_file_backend_decision(requested_uri=uri)
        assert decision.requested_uri == uri
        assert decision.uri == isolated_guard.as_uri()
        assert decision.fallback_reason == "non_file_scheme"

    def test_explicit_remote_opt_in(self, isolated_guard):
        uri = "https://remote.invalid/runs"
        decision = mlflow_guard.ensure_file_backend_decision(
            requested_uri=uri, allow_remote=True, allow_remote_flag="yes"
        )
        assert decision.uri == uri
        assert decision.allow_remote is True
        assert decision.allow_remote_flag == "yes"
        assert decision.fallback_reason is None

    @pytest.mark.parametrize("flag", ["1", "true", " YES ", "on"])
    def test_bootstrap_remote_opt_in(self, isolated_guard, monkeypatch, flag):
        monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", flag)
        uri = "https://remote.invalid/runs"
        decision = mlflow_guard.bootstrap_offline_tracking_decision(requested_uri=uri)
        assert decision.uri == uri
        assert decision.allow_remote is True
        assert decision.allow_remote_flag == flag.strip()

    @pytest.mark.parametrize("flag", ["", "0", "false", "off"])
    def test_bootstrap_false_flags_stay_offline(self, isolated_guard, monkeypatch, flag):
        monkeypatch.setenv("MLFLOW_ALLOW_REMOTE", flag)
        uri = mlflow_guard.bootstrap_offline_tracking(requested_uri="https://remote.invalid")
        assert uri == isolated_guard.as_uri()
        assert mlflow_guard.last_decision().allow_remote is False

    @pytest.mark.parametrize("key", mlflow_guard.ADDITIONAL_ALLOW_REMOTE_ENVS)
    def test_legacy_opt_in_flags(self, isolated_guard, monkeypatch, key):
        monkeypatch.setenv(key, "yes")
        uri = mlflow_guard.bootstrap_offline_tracking(requested_uri="https://remote.invalid")
        assert uri == "https://remote.invalid"
        assert os.environ["MLFLOW_ALLOW_REMOTE"] == "yes"

    @pytest.mark.parametrize("explicit", [False, True])
    def test_tracking_uri_precedence(self, isolated_guard, monkeypatch, explicit):
        monkeypatch.setenv("MLFLOW_TRACKING_URI", "tracking")
        monkeypatch.setenv("CODEX_MLFLOW_URI", "codex")
        uri = mlflow_guard.ensure_file_backend(requested_uri="explicit" if explicit else None)
        assert uri == ("explicit" if explicit else "tracking")

    def test_codex_uri_precedes_local_default(self, isolated_guard, monkeypatch):
        monkeypatch.setenv("CODEX_MLFLOW_URI", "codex")
        assert mlflow_guard.ensure_file_backend() == "codex"

    def test_absolute_directory_normalized(self, isolated_guard, tmp_path):
        directory = tmp_path / "nested" / "runs"
        assert mlflow_guard.ensure_file_backend(requested_uri=str(directory)) == directory.as_uri()
        assert directory.is_dir()

    def test_literal_file_uri_preserved(self, isolated_guard, tmp_path):
        literal = f"file:{tmp_path / 'literal'}"
        assert mlflow_guard.ensure_file_backend(requested_uri=literal) == literal
        assert (tmp_path / "literal").is_dir()

    @pytest.mark.parametrize("allow_remote", [False, True])
    def test_nonlocal_file_host(self, isolated_guard, allow_remote):
        uri = "file://remote.invalid/runs"
        decision = mlflow_guard.ensure_file_backend_decision(
            requested_uri=uri, allow_remote=allow_remote
        )
        assert decision.uri == (uri if allow_remote else isolated_guard.as_uri())
        assert decision.fallback_reason == (None if allow_remote else "non_local_host")

    @pytest.mark.parametrize("force", [False, True])
    def test_force_controls_system_metrics_reset(self, isolated_guard, monkeypatch, force):
        monkeypatch.setenv("MLFLOW_ENABLE_SYSTEM_METRICS", "true")
        decision = mlflow_guard.ensure_file_backend_decision(force=force)
        assert decision.system_metrics_enabled is (not force)
        assert os.environ["MLFLOW_ENABLE_SYSTEM_METRICS"] == ("false" if force else "true")


class TestQuantumState:
    @pytest.mark.parametrize("feature", list(QuantumFeature))
    def test_features_and_serialization(self, feature):
        state = QuantumState(feature=feature)
        assert str(feature) == feature.value
        assert state.is_coherent()
        assert state.to_dict() == {
            "feature": feature.value,
            "coherence": 1.0,
            "metadata": {},
        }
        assert json.loads(json.dumps(state.to_dict())) == state.to_dict()
        assert repr(state) == f"QuantumState(feature={feature.value}, coherence=1.000)"

    def test_metadata_is_independent(self):
        first = QuantumState(QuantumFeature.ENTANGLEMENT)
        second = QuantumState(QuantumFeature.ENTANGLEMENT)
        first.metadata["agent"] = "first"
        assert second.metadata == {}

    @pytest.mark.parametrize("coherence", [0.0, 0.3, 1.0])
    def test_coherence_boundaries(self, coherence):
        state = QuantumState(QuantumFeature.SUPERPOSITION, coherence=coherence)
        assert state.is_coherent() is (coherence >= 0.3)
        assert state.is_coherent(threshold=coherence)
        state.update_coherence(1.0 - coherence)
        assert state.coherence == 1.0 - coherence

    @pytest.mark.parametrize("value", [-0.01, 1.01, float("nan")])
    def test_invalid_initial_coherence(self, value):
        with pytest.raises(ValueError, match="Coherence must be between"):
            QuantumState(QuantumFeature.UNCERTAINTY, coherence=value)

    @pytest.mark.parametrize("value", [-1.0, 2.0, float("nan")])
    def test_invalid_update_preserves_state(self, value):
        state = QuantumState(QuantumFeature.WAVE_COLLAPSE, coherence=0.5)
        with pytest.raises(ValueError, match="Coherence must be between"):
            state.update_coherence(value)
        assert state.coherence == 0.5

    def test_quantum_error_contract(self):
        error = CoherenceDegradationError(0.1, 0.3, "superposition")
        assert isinstance(error, QuantumException)
        assert (error.current, error.threshold, error.feature) == (0.1, 0.3, "superposition")
        assert str(error) == "Coherence degradation detected in superposition: 0.100 < 0.300"
        assert issubclass(InvalidQuantumConfigurationError, QuantumException)


@pytest.fixture
def peft_backend(monkeypatch):
    config = Mock(name="LoraConfig")
    wrap = Mock(name="get_peft_model")
    model_type = SimpleNamespace(from_pretrained=Mock())
    monkeypatch.setattr(peft_hooks, "LoraConfig", config)
    monkeypatch.setattr(peft_hooks, "get_peft_model", wrap)
    monkeypatch.setattr(peft_hooks, "TaskType", SimpleNamespace(CAUSAL_LM="causal"))
    monkeypatch.setattr(peft_hooks, "PeftModel", model_type)
    return config, wrap, model_type


class TestPEFTHelpers:
    @pytest.mark.parametrize("missing", ["LoraConfig", "get_peft_model", "TaskType"])
    def test_missing_dependency_is_actionable(self, peft_backend, monkeypatch, missing):
        monkeypatch.setattr(peft_hooks, missing, None)
        with pytest.raises(peft_hooks.PeftUnavailable, match="peft is not installed"):
            peft_hooks.build_peft_config()

    @pytest.mark.parametrize("custom", [False, True])
    def test_lora_config_forwarding(self, peft_backend, custom):
        constructor, _, _ = peft_backend
        kwargs = {"r": 4, "alpha": 16, "dropout": 0.25} if custom else {}
        result = peft_hooks.build_peft_config(**kwargs)
        assert result is constructor.return_value
        constructor.assert_called_once_with(
            task_type="causal",
            r=4 if custom else 8,
            lora_alpha=16 if custom else 32,
            lora_dropout=0.25 if custom else 0.1,
            inference_mode=False,
        )

    def test_unknown_task_not_silently_accepted(self, peft_backend):
        with pytest.raises(AttributeError, match="NOT_A_TASK"):
            peft_hooks.build_peft_config(task="NOT_A_TASK")
        peft_backend[0].assert_not_called()

    def test_enable_wraps_and_reports_parameters(self, peft_backend):
        _, wrap, _ = peft_backend
        model, config = object(), object()
        result = peft_hooks.enable_peft(model, config, adapter_name="domain")
        wrap.assert_called_once_with(model, config, adapter_name="domain")
        assert result is wrap.return_value
        result.print_trainable_parameters.assert_called_once_with()

    def test_optional_diagnostic_io_failure_does_not_lose_adapter(self, peft_backend):
        wrap = peft_backend[1]
        wrap.return_value.print_trainable_parameters.side_effect = OSError("diagnostic")
        assert peft_hooks.enable_peft(object(), object()) is wrap.return_value

    def test_adapter_creation_errors_propagate(self, peft_backend):
        peft_backend[1].side_effect = ValueError("incompatible adapter")
        with pytest.raises(ValueError, match="incompatible adapter"):
            peft_hooks.enable_peft(object(), object())

    def test_load_inference_adapter(self, peft_backend):
        model = object()
        loader = peft_backend[2].from_pretrained
        assert peft_hooks.load_adapter_for_inference(model, "adapter") is loader.return_value
        loader.assert_called_once_with(model, "adapter")

    def test_missing_inference_loader(self, peft_backend, monkeypatch):
        monkeypatch.setattr(peft_hooks, "PeftModel", None)
        with pytest.raises(peft_hooks.PeftUnavailable, match="peft.PeftModel unavailable"):
            peft_hooks.load_adapter_for_inference(object(), "adapter")


class TestSharedSecurityTypes:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("", ""),
            ("ordinary text", "ordinary text"),
            ("FOO and Barf", "[REDACTED] and [REDACTED]"),
            ("bazinga dang", "[REDACTED] [REDACTED]"),
            ("foofoo", "[REDACTED][REDACTED]"),
            ("café foo 日本語", "café [REDACTED] 日本語"),
        ],
    )
    def test_sanitization(self, text, expected):
        assert sanitize_text(text) == expected
        assert sanitize_text(expected) == expected

    def test_shared_validation_exception(self):
        error = SecurityError("invalid input")
        assert isinstance(error, ValueError)
        assert str(error) == "invalid input"


class TestDifferentialPrivacyConfig:
    def test_disabled_defaults_and_serialization(self):
        config = dp_config.DifferentialPrivacyConfig()
        assert config.as_dict() == {
            "enabled": False,
            "epsilon": 1.0,
            "delta": 1e-5,
            "max_grad_norm": 1.0,
            "noise_multiplier": 1.0,
            "secure_rng": False,
        }
        assert json.loads(json.dumps(config.as_dict())) == config.as_dict()

    def test_disabled_model_is_identity_without_opacus(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "opacus", None)
        parts = object(), object(), object()
        result = dp_config.make_private_model(*parts, dp_config.DifferentialPrivacyConfig())
        assert all(actual is expected for actual, expected in zip(result[:3], parts))
        assert result[3] is None

    def test_enabled_requires_opacus(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "opacus", None)
        with pytest.raises(ImportError, match="Opacus is required for differential privacy"):
            dp_config.DifferentialPrivacyConfig(enabled=True)

    def test_enabled_wraps_exact_components_and_parameters(self, monkeypatch):
        constructor = Mock(name="PrivacyEngine")
        private_parts = object(), object(), object()
        constructor.return_value.make_private.return_value = private_parts
        monkeypatch.setitem(sys.modules, "opacus", SimpleNamespace(PrivacyEngine=constructor))
        config = dp_config.DifferentialPrivacyConfig(
            enabled=True,
            epsilon=2,
            delta=1e-6,
            max_grad_norm=0.5,
            noise_multiplier=1.2,
            secure_rng=True,
        )
        parts = object(), object(), object()
        result = dp_config.make_private_model(*parts, config)
        assert result[:3] == private_parts
        assert result[3] is constructor.return_value
        constructor.assert_called_once_with(secure_rng=True)
        constructor.return_value.make_private.assert_called_once_with(
            module=parts[0],
            optimizer=parts[1],
            data_loader=parts[2],
            noise_multiplier=1.2,
            max_grad_norm=0.5,
        )
        assert config.as_dict()["epsilon"] == 2.0
        assert config.as_dict()["delta"] == 1e-6

    def test_privacy_engine_failure_propagates(self, monkeypatch):
        engine = Mock()
        engine.make_private.side_effect = ValueError("unsupported layer")
        monkeypatch.setitem(
            sys.modules, "opacus", SimpleNamespace(PrivacyEngine=Mock(return_value=engine))
        )
        config = dp_config.DifferentialPrivacyConfig(enabled=True)
        with pytest.raises(ValueError, match="unsupported layer"):
            dp_config.make_private_model(object(), object(), object(), config)


@pytest.fixture
def preserve_rng():
    state = rng_checkpoint.RNGState()
    state.capture()
    yield
    state.restore()


class TestRNGState:
    @pytest.mark.parametrize("seed", [0, 42, 2**31 - 1])
    def test_capture_restore_and_seed_reproducibility(self, preserve_rng, seed):
        rng_checkpoint.set_seed(seed)
        state = rng_checkpoint.RNGState()
        state.capture()
        expected = [random.random() for _ in range(4)]
        state.restore()
        assert [random.random() for _ in range(4)] == expected
        rng_checkpoint.set_seed(seed)
        assert [random.random() for _ in range(4)] == expected

    def test_save_load_restores_rng(self, preserve_rng, tmp_path):
        state = rng_checkpoint.RNGState()
        state.capture()
        path = tmp_path / "nested" / "rng.json"
        assert state.save_to_file(path) == path
        assert isinstance(json.loads(path.read_text()), dict)
        expected = random.random()
        loaded = rng_checkpoint.RNGState.load_from_file(path)
        loaded.restore()
        assert random.random() == expected

    @pytest.mark.parametrize("payload", ["[]", "null", "42"])
    def test_load_rejects_non_object_json(self, tmp_path, payload):
        path = tmp_path / "invalid.json"
        path.write_text(payload)
        with pytest.raises(ValueError, match="RNG state file must contain a JSON object"):
            rng_checkpoint.RNGState.load_from_file(path)

    def test_load_rejects_corrupt_json(self, tmp_path):
        path = tmp_path / "corrupt.json"
        path.write_text("{")
        with pytest.raises(json.JSONDecodeError):
            rng_checkpoint.RNGState.load_from_file(path)

    def test_missing_file_is_not_ignored(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rng_checkpoint.RNGState.load_from_file(tmp_path / "missing")

    def test_empty_state_restore_is_noop(self):
        before = random.getstate()
        rng_checkpoint.RNGState().restore()
        assert random.getstate() == before

    @pytest.mark.parametrize("name", ["checkpoint", "checkpoint.pt", "archive.tar.gz"])
    def test_sidecar_path(self, name):
        path = Path("checkpoints") / name
        assert rng_checkpoint.RNGState.path_for_checkpoint(path) == path.with_name(
            name + ".rng.json"
        )
