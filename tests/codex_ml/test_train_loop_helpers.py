"""
Gap-filling tests for codex_ml.train_loop helper functions.

Tests cover:
- Utility functions for data normalization and snapshots
- Device and dtype resolution
- Model loading and instantiation
- Device capability checks
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestNormaliseSnapshot:
    """Tests for _normalise_snapshot function."""

    def test_normalise_snapshot_dict(self):
        """Test normalizing a simple dictionary."""
        from codex_ml.train_loop import _normalise_snapshot

        data = {"key": "value", "num": 42}
        result = _normalise_snapshot(data)
        assert result == {"key": "value", "num": 42}

    def test_normalise_snapshot_nested_dict(self):
        """Test normalizing nested dictionaries."""
        from codex_ml.train_loop import _normalise_snapshot

        data = {"outer": {"inner": "value"}, "list": [1, 2, 3]}
        result = _normalise_snapshot(data)
        assert result == {"outer": {"inner": "value"}, "list": [1, 2, 3]}

    def test_normalise_snapshot_dataclass(self):
        """Test normalizing a dataclass."""
        from dataclasses import dataclass

        from codex_ml.train_loop import _normalise_snapshot

        @dataclass
        class SampleData:
            name: str
            value: int

        obj = SampleData(name="test", value=123)
        result = _normalise_snapshot(obj)
        assert isinstance(result, dict)
        assert result["name"] == "test", "Result must not be empty"
        assert result["value"] == 123, "Result must not be empty"

    def test_normalise_snapshot_list(self):
        """Test normalizing lists."""
        from codex_ml.train_loop import _normalise_snapshot

        data = [1, "two", {"three": 3}, [4, 5]]
        result = _normalise_snapshot(data)
        assert result == [1, "two", {"three": 3}, [4, 5]]

    def test_normalise_snapshot_tuple(self):
        """Test normalizing tuples."""
        from codex_ml.train_loop import _normalise_snapshot

        data = (1, "two", {"three": 3})
        result = _normalise_snapshot(data)
        assert isinstance(result, list)
        assert result == [1, "two", {"three": 3}]

    def test_normalise_snapshot_set(self):
        """Test normalizing sets."""
        from codex_ml.train_loop import _normalise_snapshot

        data = {1, 2, 3}
        result = _normalise_snapshot(data)
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_normalise_snapshot_primitive(self):
        """Test normalizing primitive types."""
        from codex_ml.train_loop import _normalise_snapshot

        assert _normalise_snapshot("string") == "string", "_n is not valid"
        assert _normalise_snapshot(42) == 42, "_n is not valid"
        assert _normalise_snapshot(3.14) == 3.14, "_n is not valid"
        assert _normalise_snapshot(True) is True, "_n is not valid"
        assert _normalise_snapshot(None) is None, "_n is not valid"


class TestSnapshotPayload:
    """Tests for _snapshot_payload function."""

    def test_snapshot_payload_none(self):
        """Test snapshot_payload with None input."""
        from codex_ml.train_loop import _snapshot_payload

        result = _snapshot_payload(None)
        assert result is None, "Result must not be empty"

    def test_snapshot_payload_dict(self):
        """Test snapshot_payload with dict."""
        from codex_ml.train_loop import _snapshot_payload

        data = {"key": "value"}
        result = _snapshot_payload(data)
        assert result == {"key": "value"}, "Result must not be empty"

    def test_snapshot_payload_non_mapping(self):
        """Test snapshot_payload with non-mapping data."""
        from codex_ml.train_loop import _snapshot_payload

        result = _snapshot_payload([1, 2, 3])
        assert result is None, "Result must not be empty"

    def test_snapshot_payload_empty_dict(self):
        """Test snapshot_payload with empty dict."""
        from codex_ml.train_loop import _snapshot_payload

        result = _snapshot_payload({})
        assert result == {}, "Result must not be empty"


class TestApplyMetadataToState:
    """Tests for _apply_metadata_to_state function."""

    def test_apply_metadata_to_state_with_metadata(self):
        """Test applying metadata to state."""
        from codex_ml.train_loop import _apply_metadata_to_state

        state = {"loss": 0.5}
        metadata = {"rollout_ring": "test"}
        _apply_metadata_to_state(state, metadata)
        assert state["metadata"] == {"rollout_ring": "test"}, "Data must not be empty"

    def test_apply_metadata_to_state_none_metadata(self):
        """Test applying None metadata to state."""
        from codex_ml.train_loop import _apply_metadata_to_state

        state = {"loss": 0.5}
        _apply_metadata_to_state(state, None)
        assert state["metadata"] == {}, "Data must not be empty"

    def test_apply_metadata_to_state_missing_rollout_ring(self):
        """Test that warning is logged when rollout_ring is missing."""
        from codex_ml.train_loop import _apply_metadata_to_state

        state = {"loss": 0.5}
        metadata = {"other": "value"}
        with patch("codex_ml.train_loop.logger") as mock_logger:
            _apply_metadata_to_state(state, metadata)
            # Verify warning was called
            mock_logger.warning.assert_called()


class TestWriteJsonReport:
    """Tests for _write_json_report function."""

    def test_write_json_report_creates_file(self):
        """Test writing JSON report creates file."""
        from codex_ml.train_loop import _write_json_report

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            payload = {"key": "value", "count": 42}
            _write_json_report(output_dir, "test.json", payload)

            report_file = output_dir / "test.json"
            assert report_file.exists(), "rep is not valid"

            content = json.loads(report_file.read_text())
            assert content == payload, "Content must not be empty"

    def test_write_json_report_none_output_dir(self):
        """Test write_json_report with None output_dir."""
        from codex_ml.train_loop import _write_json_report

        # Should not raise
        _write_json_report(None, "test.json", {"key": "value"})

    def test_write_json_report_empty_payload(self):
        """Test write_json_report with empty payload."""
        from codex_ml.train_loop import _write_json_report

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_json_report(output_dir, "test.json", {})

            # Should not create file for empty payload
            report_file = output_dir / "test.json"
            assert not report_file.exists(), "Condition must be true"

    def test_write_json_report_creates_directory(self):
        """Test write_json_report creates output directory if missing."""
        from codex_ml.train_loop import _write_json_report

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "dir"
            payload = {"key": "value"}
            _write_json_report(output_dir, "test.json", payload)

            report_file = output_dir / "test.json"
            assert report_file.exists(), "rep is not valid"


class TestResolveDtype:
    """Tests for _resolve_dtype function."""

    def test_resolve_dtype_none(self):
        """Test resolve_dtype with None."""
        from codex_ml.train_loop import _resolve_dtype

        result = _resolve_dtype(None)
        assert result is None, "Result must not be empty"

    def test_resolve_dtype_fp32(self):
        """Test resolve_dtype with fp32."""
        from codex_ml.train_loop import _resolve_dtype

        try:
            import torch

            result = _resolve_dtype("fp32")
            assert result == torch.float32, "Result must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_resolve_dtype_float32(self):
        """Test resolve_dtype with float32."""
        from codex_ml.train_loop import _resolve_dtype

        try:
            import torch

            result = _resolve_dtype("float32")
            assert result == torch.float32, "Result must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_resolve_dtype_f32(self):
        """Test resolve_dtype with f32."""
        from codex_ml.train_loop import _resolve_dtype

        try:
            import torch

            result = _resolve_dtype("f32")
            assert result == torch.float32, "Result must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_resolve_dtype_fp16(self):
        """Test resolve_dtype with fp16."""
        from codex_ml.train_loop import _resolve_dtype

        try:
            import torch

            result = _resolve_dtype("fp16")
            assert result == torch.float16, "Result must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_resolve_dtype_case_insensitive(self):
        """Test resolve_dtype is case insensitive."""
        from codex_ml.train_loop import _resolve_dtype

        try:
            import torch

            result = _resolve_dtype("FP32")
            assert result == torch.float32, "Result must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_resolve_dtype_invalid(self):
        """Test resolve_dtype with invalid dtype."""
        from codex_ml.train_loop import _resolve_dtype

        result = _resolve_dtype("invalid_dtype")
        assert result is None, "Result must not be empty"


class TestResolveDevice:
    """Tests for _resolve_device function."""

    def test_resolve_device_none(self):
        """Test resolve_device with None."""
        from codex_ml.train_loop import _resolve_device

        result = _resolve_device(None)
        # Should return a device object (CPU or CUDA if available)
        assert result is not None, "result must be initialized"

    def test_resolve_device_cpu(self):
        """Test resolve_device with cpu."""
        from codex_ml.train_loop import _resolve_device

        result = _resolve_device("cpu")
        assert str(result) == "cpu", "Result must not be empty"

    def test_resolve_device_invalid(self):
        """Test resolve_device with invalid device."""
        from codex_ml.train_loop import _resolve_device

        # Should return CPU as fallback
        result = _resolve_device("invalid_device_xyz")
        assert str(result) == "cpu", "Result must not be empty"


class TestLoadOrCreateModel:
    """Tests for _load_or_create_model function."""

    def test_load_or_create_model_provided_model(self):
        """Test when model is already provided."""
        from codex_ml.train_loop import _load_or_create_model

        provided_model = MagicMock()
        model, created = _load_or_create_model(provided_model, None, {})

        assert model is provided_model, "model is not valid"
        assert created is False, "created is not valid"

    def test_load_or_create_model_no_model_no_name(self):
        """Test when no model and no model_name provided."""
        from codex_ml.train_loop import _load_or_create_model

        model, created = _load_or_create_model(None, None, {})

        assert model is None, "model is not valid"
        assert created is False, "created is not valid"

    def test_load_or_create_model_with_instantiate(self):
        """Test model instantiation when function is available."""
        from codex_ml.train_loop import _load_or_create_model

        with patch("codex_ml.train_loop.instantiate_model") as mock_instantiate:
            mock_model = MagicMock()
            mock_instantiate.return_value = mock_model

            model, created = _load_or_create_model(None, "test_model", {"param": "value"})

            assert model is mock_model, "model is not valid"
            assert created is True, "created is not valid"
            mock_instantiate.assert_called_once_with("test_model", {"param": "value"})


class TestAssertBf16Capability:
    """Tests for _assert_bf16_capability function."""

    def test_assert_bf16_capability_not_required(self):
        """Test when bf16 is not required."""
        from codex_ml.train_loop import _assert_bf16_capability

        # Should not raise
        _assert_bf16_capability("bf16", None, require=False)

    def test_assert_bf16_capability_not_requested(self):
        """Test when bf16 is not requested."""
        from codex_ml.train_loop import _assert_bf16_capability

        # Should not raise
        _assert_bf16_capability("fp32", None, require=True)

    def test_assert_bf16_capability_torch_not_installed(self):
        """Test bf16 requirement when torch is not available."""
        from codex_ml.train_loop import _assert_bf16_capability

        with patch.dict("sys.modules", {"torch": None}):
            with pytest.raises(RuntimeError, match="bf16 required but PyTorch"):
                _assert_bf16_capability("bf16", None, require=True)


class TestToyDataset:
    """Tests for ToyDataset class."""

    def test_toy_dataset_creation(self):
        """Test creating a ToyDataset."""
        from codex_ml.train_loop import ToyDataset

        try:
            import torch

            dataset = ToyDataset(num_samples=10, seq_len=20, vocab_size=100, seed=42)
            assert len(dataset) == 10, "Dataset must not be empty"

            # Get an item
            item = dataset[0]
            assert item.shape == (20,)
            assert item.dtype == torch.long, "Item must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_toy_dataset_length(self):
        """Test ToyDataset length."""
        from codex_ml.train_loop import ToyDataset

        try:
            import torch

            dataset = ToyDataset(num_samples=5, seq_len=15, vocab_size=50, seed=42)
            assert len(dataset) == 5, "Dataset must not be empty"
        except ImportError:
            pytest.skip("torch not installed")

    def test_toy_dataset_deterministic_seed(self):
        """Test ToyDataset produces same data with same seed."""
        from codex_ml.train_loop import ToyDataset

        try:
            import torch

            dataset1 = ToyDataset(num_samples=3, seq_len=10, vocab_size=50, seed=42)
            dataset2 = ToyDataset(num_samples=3, seq_len=10, vocab_size=50, seed=42)

            # Both should produce identical data
            for i in range(len(dataset1)):
                assert torch.equal(dataset1[i], dataset2[i])
        except ImportError:
            pytest.skip("torch not installed")


class TestReasoningRuntime:
    """Tests for ReasoningRuntime class."""

    def test_reasoning_runtime_should_capture_enabled(self):
        """Test should_capture with enabled tracing."""
        from codex_ml.config import ReasoningConfig
        from codex_ml.train_loop import ReasoningRuntime

        config = ReasoningConfig(enabled=True)
        runtime = ReasoningRuntime(
            config=config,
            harness=MagicMock(),
            store_path=None,
            per_epoch_limit=10,
            top_k=5,
            threshold=0.5,
        )

        assert runtime.should_capture() is True, "Condition must be true"

    def test_reasoning_runtime_should_capture_zero_limit(self):
        """Test should_capture with zero limit (unlimited)."""
        from codex_ml.config import ReasoningConfig
        from codex_ml.train_loop import ReasoningRuntime

        config = ReasoningConfig(enabled=True)
        runtime = ReasoningRuntime(
            config=config,
            harness=MagicMock(),
            store_path=None,
            per_epoch_limit=0,
            top_k=5,
            threshold=0.5,
        )

        assert runtime.should_capture() is True, "Condition must be true"

    def test_reasoning_runtime_should_capture_exceeded_limit(self):
        """Test should_capture when limit is exceeded."""
        from codex_ml.config import ReasoningConfig
        from codex_ml.train_loop import ReasoningRuntime

        config = ReasoningConfig(enabled=True)
        runtime = ReasoningRuntime(
            config=config,
            harness=MagicMock(),
            store_path=None,
            per_epoch_limit=2,
            top_k=5,
            threshold=0.5,
            traces_written=3,
        )

        assert runtime.should_capture() is False, "Condition must be true"

    def test_reasoning_runtime_on_new_epoch(self):
        """Test on_new_epoch resets counter."""
        from codex_ml.config import ReasoningConfig
        from codex_ml.train_loop import ReasoningRuntime

        config = ReasoningConfig(enabled=True)
        runtime = ReasoningRuntime(
            config=config,
            harness=MagicMock(),
            store_path=None,
            per_epoch_limit=5,
            top_k=5,
            threshold=0.5,
            traces_written=10,
        )

        runtime.on_new_epoch()
        assert runtime.traces_written == 0, "traces_written is not valid"

    def test_reasoning_runtime_bind_model(self):
        """Test bind_model attaches to harness."""
        from codex_ml.config import ReasoningConfig
        from codex_ml.train_loop import ReasoningRuntime

        mock_harness = MagicMock()
        config = ReasoningConfig(enabled=True)
        runtime = ReasoningRuntime(
            config=config,
            harness=mock_harness,
            store_path=None,
            per_epoch_limit=5,
            top_k=5,
            threshold=0.5,
        )

        mock_model = MagicMock()
        runtime.bind_model(mock_model)

        mock_harness.attach.assert_called_once_with(mock_model)
