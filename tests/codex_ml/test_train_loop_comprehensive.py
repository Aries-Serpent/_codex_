"""Contract tests for training utilities, token datasets, reasoning, and resume."""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta

import numpy as np
import pytest
import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from codex_ml.config import ConfigError, ReasoningConfig
from codex_ml.models.reasoning import ReasoningHarness, ReasoningHead
from codex_ml.train_loop import (
    ReasoningRuntime,
    ToyDataset,
    _attempt_resume,
    _coerce_reasoning_config,
    _now_ts,
    _resolve_device,
    _resolve_dtype,
    _set_seed,
    run_training,
)
from codex_ml.utils.checkpoint import save_checkpoint


@pytest.fixture
def mock_model():
    """Use a real, small model rather than a serialization-unsafe mock."""
    return nn.Sequential(nn.Linear(10, 8), nn.ReLU(), nn.Linear(8, 1))


@pytest.fixture
def mock_optimizer(mock_model):
    return optim.SGD(mock_model.parameters(), lr=0.001, momentum=0.9)


@pytest.fixture
def mock_scheduler(mock_optimizer):
    return optim.lr_scheduler.StepLR(mock_optimizer, step_size=1, gamma=0.1)


@pytest.fixture
def reasoning_config():
    return ReasoningConfig.from_mapping(
        {
            "head": {"hidden_size": 10, "projection_size": 8, "trace_vocab_size": 4},
            "objective": {"max_traces_per_epoch": 3, "log_top_k": 2},
        }
    )


@pytest.fixture
def reasoning_runtime(reasoning_config):
    harness = ReasoningHarness(reasoning_config, ReasoningHead(reasoning_config.head), None)
    return ReasoningRuntime(
        config=reasoning_config,
        harness=harness,
        store_path=None,
        per_epoch_limit=reasoning_config.objective.max_traces_per_epoch,
        top_k=reasoning_config.objective.log_top_k,
        threshold=None,
    )


class TestSetSeed:
    @pytest.mark.unit
    @pytest.mark.parametrize("seed", [1, 42, 100, 999])
    def test_set_seed_with_valid_integer(self, seed):
        assert _set_seed(seed) == seed

    @pytest.mark.unit
    @pytest.mark.parametrize("seed", [None, 0])
    def test_set_seed_default(self, seed):
        from codex_ml import train_loop

        assert _set_seed(seed) == train_loop._DEFAULT_SEED

    @pytest.mark.unit
    @pytest.mark.parametrize("seed", [0, 1, 42, 100, 999])
    def test_set_seed_determinism(self, seed):
        _set_seed(seed)
        first = (random.random(), np.random.rand(5), torch.randn(5))
        _set_seed(seed)
        second = (random.random(), np.random.rand(5), torch.randn(5))
        assert first[0] == second[0]
        np.testing.assert_array_equal(first[1], second[1])
        assert torch.equal(first[2], second[2])


class TestNowTs:
    @pytest.mark.unit
    def test_now_ts_format(self):
        timestamp = _now_ts()
        assert timestamp.endswith("Z")
        assert "T" in timestamp

    @pytest.mark.unit
    def test_now_ts_parseable(self):
        parsed = datetime.fromisoformat(_now_ts().replace("Z", "+00:00"))
        assert parsed.utcoffset() == timedelta(0)

    @pytest.mark.unit
    def test_now_ts_monotonic(self):
        assert _now_ts() <= _now_ts()

    @pytest.mark.unit
    def test_now_ts_contains_date_time(self):
        date, time = _now_ts().removesuffix("Z").split("T")
        assert len(date.split("-")) == 3
        assert len(time.split(":")) == 3


class TestResolveDtype:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("fp32", torch.float32),
            ("float32", torch.float32),
            ("f32", torch.float32),
            ("bf16", torch.bfloat16),
            ("bfloat16", torch.bfloat16),
            ("fp16", torch.float16),
            ("float16", torch.float16),
            ("f16", torch.float16),
            ("FLOAT32", torch.float32),
            ("Float32", torch.float32),
        ],
    )
    def test_resolve_dtype_supported_aliases(self, name, expected):
        assert _resolve_dtype(name) == expected

    @pytest.mark.unit
    @pytest.mark.parametrize("name", [None, "float64", "int32", "int64", "invalid_dtype", ""])
    def test_resolve_dtype_unsupported_returns_none(self, name):
        assert _resolve_dtype(name) is None


class TestResolveDevice:
    @pytest.mark.unit
    def test_resolve_device_cpu(self):
        assert _resolve_device("cpu") == torch.device("cpu")

    @pytest.mark.unit
    @pytest.mark.parametrize("available", [False, True])
    def test_resolve_device_auto_selection(self, monkeypatch, available):
        monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
        assert _resolve_device(None) == torch.device("cuda" if available else "cpu")

    @pytest.mark.unit
    @pytest.mark.parametrize("available", [False, True])
    def test_resolve_device_explicit_cuda_is_not_auto_fallback(self, monkeypatch, available):
        monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
        # Resolution describes the requested device; it does not allocate on it.
        assert _resolve_device("cuda") == torch.device("cuda")

    @pytest.mark.unit
    def test_resolve_device_invalid_falls_back(self):
        assert _resolve_device("invalid_device_xyz") == torch.device("cpu")

    @pytest.mark.unit
    @pytest.mark.parametrize("name", ["cpu", "cuda:0", "mps"])
    def test_resolve_device_various(self, name):
        assert _resolve_device(name) == torch.device(name)


class TestCoerceReasoningConfig:
    @pytest.mark.unit
    def test_coerce_from_dict(self):
        result = _coerce_reasoning_config({"enabled": True, "trace_history": 3})
        assert isinstance(result, ReasoningConfig)
        assert result.enabled
        assert result.trace_history == 3

    @pytest.mark.unit
    @pytest.mark.parametrize("enabled", [True, False])
    def test_coerce_from_bool(self, enabled):
        result = _coerce_reasoning_config(enabled)
        assert isinstance(result, ReasoningConfig)
        assert result.enabled is enabled

    @pytest.mark.unit
    def test_coerce_from_none(self):
        assert _coerce_reasoning_config(None) is None

    @pytest.mark.unit
    def test_coerce_from_empty_dict(self):
        assert _coerce_reasoning_config({}) == ReasoningConfig()

    @pytest.mark.unit
    def test_coerce_preserves_config_identity(self, reasoning_config):
        assert _coerce_reasoning_config(reasoning_config) is reasoning_config

    @pytest.mark.unit
    def test_coerce_preserves_nested_content(self):
        result = _coerce_reasoning_config(
            {
                "enabled": True,
                "trace_history": 5,
                "head": {"hidden_size": 10, "projection_size": 8},
                "objective": {"max_traces_per_epoch": 2, "log_top_k": 3},
            }
        )
        assert result.trace_history == 5
        assert result.head.hidden_size == 10
        assert result.head.projection_size == 8
        assert result.objective.max_traces_per_epoch == 2
        assert result.objective.log_top_k == 3

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "payload",
        [
            {"trace_history": 0},
            {"trace_mode": "invalid"},
            {"log_probability_threshold": 0},
            {"objective": {"log_top_k": 0}},
            {"head": {"hidden_size": 0}},
        ],
    )
    def test_coerce_rejects_invalid_values(self, payload):
        with pytest.raises(ConfigError):
            _coerce_reasoning_config(payload)

    @pytest.mark.unit
    @pytest.mark.parametrize("key", ["depth", "max_tokens"])
    def test_coerce_rejects_unknown_top_level_keys(self, key):
        with pytest.raises(TypeError, match=key):
            _coerce_reasoning_config({key: 3})


class TestToyDataset:
    @pytest.mark.unit
    def test_toy_dataset_creation(self):
        dataset = ToyDataset(num_samples=100, seq_len=10, vocab_size=32, seed=42)
        assert len(dataset) == 100

    @pytest.mark.unit
    def test_toy_dataset_getitem(self):
        dataset = ToyDataset(num_samples=20, seq_len=10, vocab_size=32, seed=42)
        tokens = dataset[0]
        assert tokens.shape == (10,)
        assert tokens.dtype == torch.long
        assert torch.all((tokens >= 0) & (tokens < 32))

    @pytest.mark.unit
    def test_toy_dataset_batch_indexing(self):
        dataset = ToyDataset(num_samples=20, seq_len=10, vocab_size=32, seed=42)
        for index in range(10):
            assert dataset[index].shape == (10,)
        with pytest.raises(IndexError):
            dataset[len(dataset)]

    @pytest.mark.unit
    @pytest.mark.parametrize("num_samples,seq_len", [(10, 5), (100, 20), (50, 10)])
    def test_toy_dataset_various_sizes(self, num_samples, seq_len):
        dataset = ToyDataset(num_samples=num_samples, seq_len=seq_len, vocab_size=32, seed=42)
        assert len(dataset) == num_samples
        assert dataset[0].shape == (seq_len,)

    @pytest.mark.unit
    @pytest.mark.parametrize("batch_size", [1, 8, 32, 128])
    def test_toy_dataset_dataloader_compatibility(self, batch_size):
        dataset = ToyDataset(num_samples=100, seq_len=10, vocab_size=32, seed=42)
        batches = list(DataLoader(dataset, batch_size=batch_size))
        assert sum(batch.shape[0] for batch in batches) == len(dataset)
        for batch in batches:
            assert batch.ndim == 2
            assert batch.shape[0] <= batch_size
            assert batch.shape[1] == 10
            assert batch.dtype == torch.long

    @pytest.mark.unit
    @pytest.mark.parametrize("seq_len", [1, 5, 10, 50])
    def test_toy_dataset_sequence_lengths(self, seq_len):
        dataset = ToyDataset(num_samples=50, seq_len=seq_len, vocab_size=32, seed=42)
        assert dataset[0].shape == (seq_len,)

    @pytest.mark.unit
    def test_toy_dataset_seed_is_local_and_reproducible(self):
        torch.manual_seed(123)
        before = torch.random.get_rng_state().clone()
        first = ToyDataset(num_samples=20, seq_len=10, vocab_size=32, seed=42)
        assert torch.equal(before, torch.random.get_rng_state())
        second = ToyDataset(num_samples=20, seq_len=10, vocab_size=32, seed=42)
        different = ToyDataset(num_samples=20, seq_len=10, vocab_size=32, seed=43)
        assert all(torch.equal(first[i], second[i]) for i in range(len(first)))
        assert any(not torch.equal(first[i], different[i]) for i in range(len(first)))


class TestReasoningRuntime:
    @pytest.mark.unit
    def test_reasoning_runtime_creation(self, reasoning_runtime, reasoning_config):
        assert reasoning_runtime.config is reasoning_config
        assert reasoning_runtime.harness.config is reasoning_config
        assert reasoning_runtime.store_path is None
        assert reasoning_runtime.per_epoch_limit == 3
        assert reasoning_runtime.top_k == 2
        assert reasoning_runtime.threshold is None
        assert reasoning_runtime.traces_written == 0

    @pytest.mark.unit
    def test_reasoning_runtime_bind_model(self, reasoning_runtime, mock_model):
        reasoning_runtime.bind_model(mock_model)
        assert reasoning_runtime.harness.model is mock_model
        assert mock_model.reasoning_head is reasoning_runtime.harness.head

    @pytest.mark.unit
    def test_reasoning_runtime_requires_dependencies(self):
        with pytest.raises(TypeError, match="required positional arguments"):
            ReasoningRuntime()

    @pytest.mark.unit
    @pytest.mark.parametrize("trace_mode,expected", [("weights", True), ("disabled", False)])
    def test_reasoning_runtime_trace_mode(self, reasoning_runtime, trace_mode, expected):
        reasoning_runtime.config.trace_mode = trace_mode
        assert reasoning_runtime.should_capture() is expected

    @pytest.mark.unit
    @pytest.mark.parametrize("limit", [1, 3, 5, 10])
    def test_reasoning_runtime_per_epoch_limit(self, reasoning_runtime, limit):
        reasoning_runtime.per_epoch_limit = limit
        reasoning_runtime.traces_written = limit - 1
        assert reasoning_runtime.should_capture()
        reasoning_runtime.traces_written = limit
        assert not reasoning_runtime.should_capture()
        reasoning_runtime.on_new_epoch()
        assert reasoning_runtime.traces_written == 0
        assert reasoning_runtime.should_capture()

    @pytest.mark.unit
    @pytest.mark.parametrize("limit", [0, -1])
    def test_reasoning_runtime_unlimited_capture(self, reasoning_runtime, limit):
        reasoning_runtime.per_epoch_limit = limit
        reasoning_runtime.traces_written = 100
        assert reasoning_runtime.should_capture()

    @pytest.mark.unit
    def test_reasoning_runtime_record_trace(self, reasoning_runtime, mock_model, tmp_path):
        reasoning_runtime.store_path = tmp_path / "traces.ndjson"
        reasoning_runtime.per_epoch_limit = 1
        reasoning_runtime.bind_model(mock_model)
        for step in (1, 2):
            reasoning_runtime.record_trace(
                mock_model, epoch=1, step=step, art_dir_path=None, session_id="test-session"
            )
        assert reasoning_runtime.traces_written == 1
        history = reasoning_runtime.harness.history_snapshot()
        assert len(history) == 1
        assert history[0]["epoch"] == 1
        assert history[0]["step"] == 1
        assert history[0]["session_id"] == "test-session"
        stored = [
            json.loads(line) for line in reasoning_runtime.store_path.read_text().splitlines()
        ]
        assert stored == history


class TestAttemptResume:
    @pytest.mark.unit
    def test_attempt_resume_no_checkpoint(
        self, mock_model, mock_optimizer, mock_scheduler, tmp_path
    ):
        assert _attempt_resume(mock_model, mock_optimizer, mock_scheduler, tmp_path) == (1, {})

    @pytest.mark.unit
    def test_attempt_resume_invalid_directory(
        self, mock_model, mock_optimizer, mock_scheduler, tmp_path
    ):
        assert _attempt_resume(
            mock_model, mock_optimizer, mock_scheduler, tmp_path / "nonexistent"
        ) == (1, {})

    @pytest.mark.unit
    def test_attempt_resume_with_checkpoint(
        self, mock_model, mock_optimizer, mock_scheduler, tmp_path
    ):
        # Populate optimizer momentum and scheduler state before saving the real layout.
        mock_model(torch.ones(2, 10)).sum().backward()
        mock_optimizer.step()
        mock_scheduler.step()
        expected_parameters = {
            name: value.clone() for name, value in mock_model.state_dict().items()
        }
        expected_momentum = [
            value["momentum_buffer"].clone() for value in mock_optimizer.state.values()
        ]
        expected_scheduler = mock_scheduler.state_dict().copy()
        checkpoint = tmp_path / "epoch-0005"
        save_checkpoint(
            model=mock_model,
            optimizer=mock_optimizer,
            scheduler=mock_scheduler,
            out_dir=checkpoint,
            metadata={"epoch": 5},
        )
        (tmp_path / "latest.json").write_text(json.dumps({"epoch": 5, "path": checkpoint.name}))
        with torch.no_grad():
            for parameter in mock_model.parameters():
                parameter.zero_()
        mock_optimizer.state.clear()
        mock_optimizer.param_groups[0]["lr"] = 99
        mock_scheduler.last_epoch = 99

        epoch, metadata = _attempt_resume(mock_model, mock_optimizer, mock_scheduler, tmp_path)
        assert epoch == 6
        assert metadata["resumed_from_epoch"] == 5
        assert metadata["latest_checkpoint_path"] == str(checkpoint)
        assert metadata["model_state_loaded"] is True
        assert metadata["optimizer_state_loaded"] is True
        assert metadata["scheduler_state_loaded"] is True
        for name, value in mock_model.state_dict().items():
            assert torch.equal(value, expected_parameters[name])
        actual_momentum = [value["momentum_buffer"] for value in mock_optimizer.state.values()]
        assert len(actual_momentum) == len(expected_momentum)
        assert all(
            torch.equal(actual, expected)
            for actual, expected in zip(actual_momentum, expected_momentum, strict=True)
        )
        assert mock_optimizer.param_groups[0]["lr"] == 0.0001
        assert mock_scheduler.state_dict() == expected_scheduler

    @pytest.mark.unit
    def test_attempt_resume_returns_tuple(self, tmp_path):
        assert _attempt_resume(None, None, None, tmp_path) == (1, {})

    @pytest.mark.unit
    def test_attempt_resume_missing_model_file(self, mock_model, tmp_path):
        (tmp_path / "latest.json").write_text(json.dumps({"epoch": 5, "path": "epoch-0005"}))
        epoch, metadata = _attempt_resume(mock_model, None, None, tmp_path)
        assert epoch == 1
        assert metadata["model_state_loaded"] is False
        assert metadata["missing_checkpoint"] == str(tmp_path / "epoch-0005" / "model.pt")


class TestRunTrainingIntegration:
    @pytest.mark.integration
    def test_run_training_basic(self, mock_model, tmp_path):
        before = [parameter.detach().clone() for parameter in mock_model.parameters()]
        result = run_training(
            model=mock_model,
            epochs=2,
            steps_per_epoch=2,
            grad_accum=2,
            batch_size=2,
            learning_rate=0.001,
            device="cpu",
            seed=42,
            checkpoint_dir=str(tmp_path / "checkpoints"),
            art_dir=tmp_path / "artifacts",
        )
        assert result["start_epoch"] == 1
        assert result["final_epoch"] == 2
        assert result["total_steps"] == 4
        assert result["optimizer_steps"] == 2
        assert any(
            not torch.equal(old, new)
            for old, new in zip(before, mock_model.parameters(), strict=True)
        )
        latest = json.loads((tmp_path / "checkpoints" / "latest.json").read_text())
        assert latest["epoch"] == 2
        assert (tmp_path / "checkpoints" / latest["path"] / "model.pt").is_file()

    @pytest.mark.integration
    def test_run_training_with_seed_determinism(self, tmp_path):
        states = []
        for index in range(2):
            _set_seed(42)
            model = nn.Linear(10, 1)
            result = run_training(
                model=model,
                epochs=1,
                steps_per_epoch=2,
                seed=42,
                device="cpu",
                art_dir=tmp_path / str(index),
                return_state=True,
            )
            assert result["model"] is model
            metrics = [
                json.loads(line)
                for line in (tmp_path / str(index) / "metrics.ndjson").read_text().splitlines()
            ]
            losses = [
                record["value"]
                for record in metrics
                if record.get("metric_name") == "training.loss"
            ]
            states.append(
                (
                    {name: value.clone() for name, value in model.state_dict().items()},
                    losses,
                    result["optimizer_steps"],
                )
            )
        assert states[0][2] == states[1][2] == 2
        assert len(states[0][1]) == len(states[1][1]) == 1
        assert all(isinstance(loss, float) for loss in states[0][1])
        assert states[0][1] == states[1][1]
        for name in states[0][0]:
            assert torch.equal(states[0][0][name], states[1][0][name])

    @pytest.mark.integration
    def test_run_training_creates_output_dir(self, mock_model, tmp_path):
        art_dir = tmp_path / "new" / "artifacts"
        assert not art_dir.exists()
        result = run_training(
            model=mock_model, epochs=1, steps_per_epoch=1, device="cpu", art_dir=art_dir
        )
        assert result["final_epoch"] == 1
        assert art_dir.is_dir()
        assert (art_dir / "metrics.ndjson").is_file()


class TestEdgeCases:
    @pytest.mark.unit
    def test_toy_dataset_zero_samples(self):
        dataset = ToyDataset(num_samples=0, seq_len=10, vocab_size=32, seed=42)
        assert len(dataset) == 0
        assert list(DataLoader(dataset, batch_size=2)) == []
        with pytest.raises(IndexError):
            dataset[0]

    @pytest.mark.unit
    def test_toy_dataset_zero_sequence_length(self):
        dataset = ToyDataset(num_samples=100, seq_len=0, vocab_size=32, seed=42)
        assert len(dataset) == 100
        assert dataset[0].shape == (0,)
        assert next(iter(DataLoader(dataset, batch_size=2))).shape == (2, 0)

    @pytest.mark.unit
    def test_set_seed_negative_value(self):
        with pytest.raises(ValueError, match="Seed must be between"):
            _set_seed(-1)

    @pytest.mark.unit
    def test_coerce_reasoning_config_invalid_type(self):
        with pytest.raises(ConfigError, match="mapping or boolean"):
            _coerce_reasoning_config(12345)

    @pytest.mark.unit
    def test_attempt_resume_with_corrupted_manifest(self, mock_model, tmp_path):
        (tmp_path / "latest.json").write_text("corrupted data")
        epoch, metadata = _attempt_resume(mock_model, None, None, tmp_path)
        assert epoch == 1
        assert metadata["resume_error"].startswith("latest.json parse failure:")
