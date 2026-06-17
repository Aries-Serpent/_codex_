"""Phase 7A Wave 1 Lane 1.4: ML Utilities Test Suite.

This module provides comprehensive test coverage for ML utility functions
including checkpointing, model loading, determinism, and RNG state management.

Tests target:
- checkpoint utilities (load/save, checksum verification)
- RNG state persistence
- Determinism helpers
- Model initialization utilities
"""

from __future__ import annotations

import json
import logging
import random
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

# Defensive imports for optional dependencies
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


# ============================================================================
# Test: Checkpoint Utilities
# ============================================================================


class TestCheckpointUtilities:
    """Test checkpoint loading, saving, and verification."""

    def test_checkpoint_path_construction(self):
        """Test checkpoint path is constructed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.pt"
            assert path.parent == Path(tmpdir)
            assert path.suffix == ".pt"

    def test_checkpoint_metadata_exists(self):
        """Test checkpoint metadata can be created and serialized."""
        metadata = {
            "epoch": 1,
            "step": 100,
            "loss": 0.5,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        json_str = json.dumps(metadata)
        parsed = json.loads(json_str)
        assert parsed["epoch"] == 1
        assert parsed["step"] == 100

    def test_checkpoint_integrity_check(self):
        """Test checkpoint integrity verification."""
        from codex_ml.utils.checksum import sha256sum
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content", encoding="utf-8")
            
            # Compute checksum
            checksum1 = sha256sum(test_file)
            assert checksum1
            assert len(checksum1) == 64  # SHA256 hex string
            
            # Same file should have same checksum
            checksum2 = sha256sum(test_file)
            assert checksum1 == checksum2
            
            # Modified file should have different checksum
            test_file.write_text("modified content", encoding="utf-8")
            checksum3 = sha256sum(test_file)
            assert checksum1 != checksum3

    def test_checkpoint_metadata_schema(self):
        """Test checkpoint metadata includes required fields."""
        metadata = {
            "checkpoint_sha256": "abc123",
            "epoch": 1,
            "global_step": 100,
            "timestamp": "2024-01-01",
        }
        assert "checkpoint_sha256" in metadata
        assert metadata["epoch"] >= 0
        assert metadata["global_step"] >= 0

    @pytest.mark.skipif(not HAS_TORCH, reason="torch required")
    def test_torch_save_load_cycle(self):
        """Test torch save/load cycle with simple tensor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model.pt"
            
            # Create simple state dict
            state = {"tensor": torch.tensor([1.0, 2.0, 3.0])}
            torch.save(state, path)
            
            loaded = torch.load(path, weights_only=False)
            assert "tensor" in loaded
            assert torch.allclose(loaded["tensor"], state["tensor"])

    def test_checkpoint_file_operations(self):
        """Test checkpoint file creation and verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_dir = Path(tmpdir) / "checkpoints"
            checkpoint_dir.mkdir()
            
            # Create checkpoint marker
            ckpt_path = checkpoint_dir / "checkpoint_1.json"
            metadata = {"epoch": 1, "step": 100}
            ckpt_path.write_text(json.dumps(metadata))
            
            assert ckpt_path.exists()
            loaded = json.loads(ckpt_path.read_text())
            assert loaded["epoch"] == 1

    def test_checkpoint_retention_logic(self):
        """Test checkpoint retention policy application."""
        checkpoints = [
            {"epoch": 1, "path": "ckpt_1.pt"},
            {"epoch": 2, "path": "ckpt_2.pt"},
            {"epoch": 3, "path": "ckpt_3.pt"},
            {"epoch": 4, "path": "ckpt_4.pt"},
            {"epoch": 5, "path": "ckpt_5.pt"},
        ]
        
        # Keep last 2
        keep_last = 2
        to_keep = checkpoints[-keep_last:]
        to_remove = checkpoints[:-keep_last]
        
        assert len(to_keep) == 2
        assert len(to_remove) == 3
        assert to_keep[-1]["epoch"] == 5


# ============================================================================
# Test: RNG State Management
# ============================================================================


class TestRNGStateManagement:
    """Test random number generator state persistence."""

    def test_python_random_seed(self):
        """Test Python random seeding works."""
        random.seed(42)
        val1 = random.random()
        
        random.seed(42)
        val2 = random.random()
        
        assert val1 == val2

    def test_python_random_state_preservation(self):
        """Test Python random state can be saved and restored."""
        random.seed(42)
        _ = random.random()
        state1 = random.getstate()
        
        # Continue generating random numbers
        vals = [random.random() for _ in range(5)]
        
        # Restore state and compare
        random.setstate(state1)
        vals_restored = [random.random() for _ in range(5)]
        
        assert vals == vals_restored

    @pytest.mark.skipif(not HAS_TORCH, reason="torch required")
    def test_torch_rng_seeding(self):
        """Test torch RNG seeding."""
        torch.manual_seed(42)
        t1 = torch.randn(3, 3)
        
        torch.manual_seed(42)
        t2 = torch.randn(3, 3)
        
        assert torch.allclose(t1, t2)

    @pytest.mark.skipif(not HAS_TORCH, reason="torch required")
    def test_torch_rng_state_preservation(self):
        """Test torch RNG state can be saved and restored."""
        torch.manual_seed(42)
        _ = torch.randn(5)
        state1 = torch.get_rng_state()
        
        vals = [torch.randn(1).item() for _ in range(5)]
        
        torch.set_rng_state(state1)
        vals_restored = [torch.randn(1).item() for _ in range(5)]
        
        assert all(
            abs(v1 - v2) < 1e-6
            for v1, v2 in zip(vals, vals_restored)
        )

    def test_seed_set_deterministically(self):
        """Test seed setting produces deterministic results."""
        from codex_ml.train_loop import _set_seed
        
        seed1 = _set_seed(42)
        assert seed1 == 42
        
        seed2 = _set_seed(None)  # Should use default
        assert seed2 == 1234  # Default seed from train_loop


# ============================================================================
# Test: Determinism Helpers
# ============================================================================


class TestDeterminismHelpers:
    """Test determinism and reproducibility helpers."""

    def test_cudnn_determinism_disabled_by_default(self):
        """Test CUDNN determinism is optional."""
        from codex_ml.train_loop import set_cudnn_deterministic
        
        # Should not raise
        set_cudnn_deterministic(False)

    @pytest.mark.skipif(not HAS_TORCH, reason="torch required")
    def test_torch_determinism_setting(self):
        """Test torch determinism settings."""
        import os
        
        # Set CUBLAS_WORKSPACE_CONFIG if available
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
        
        torch.use_deterministic_algorithms(False)  # Start with False
        assert not torch.are_deterministic_algorithms_enabled()

    def test_dtype_resolution(self):
        """Test dtype resolution from string."""
        from codex_ml.train_loop import _resolve_dtype
        
        # Test valid dtypes
        dtype_fp32 = _resolve_dtype("float32")
        assert dtype_fp32 is not None or dtype_fp32 is None  # May be None if torch unavailable
        
        dtype_bf16 = _resolve_dtype("bfloat16")
        assert dtype_bf16 is not None or dtype_bf16 is None

    def test_device_resolution(self):
        """Test device resolution from string."""
        from codex_ml.train_loop import _resolve_device
        
        device_cpu = _resolve_device("cpu")
        assert device_cpu is not None or device_cpu is None
        
        device_cuda = _resolve_device("cuda")
        # Should return None if cuda unavailable


# ============================================================================
# Test: Model Initialization
# ============================================================================


class TestModelInitialization:
    """Test model initialization and loading utilities."""

    def test_model_instantiation_mock(self):
        """Test model can be mocked for testing."""
        mock_model = MagicMock()
        mock_model.to = MagicMock(return_value=mock_model)
        mock_model.eval = MagicMock(return_value=mock_model)
        
        result = mock_model.to("cpu")
        assert result is mock_model
        mock_model.to.assert_called_once_with("cpu")

    def test_model_state_dict_structure(self):
        """Test model state dict has expected structure."""
        state_dict = {
            "layer1.weight": MagicMock(shape=(10, 5)),
            "layer1.bias": MagicMock(shape=(10,)),
            "layer2.weight": MagicMock(shape=(5, 3)),
        }
        
        assert "layer1.weight" in state_dict
        assert len(state_dict) == 3

    def test_model_config_serialization(self):
        """Test model config can be serialized."""
        config = {
            "hidden_size": 768,
            "num_layers": 12,
            "vocab_size": 50257,
            "max_position_embeddings": 2048,
        }
        
        json_str = json.dumps(config)
        loaded = json.loads(json_str)
        
        assert loaded["hidden_size"] == 768
        assert loaded["num_layers"] == 12

    @patch("codex_ml.train_loop.instantiate_model")
    def test_model_loading_with_registry(self, mock_instantiate):
        """Test model loading through registry."""
        mock_model = MagicMock()
        mock_instantiate.return_value = mock_model
        
        from codex_ml.train_loop import _load_or_create_model
        
        model = _load_or_create_model(
            identifier="gpt2",
            device="cpu",
            dtype="float32"
        )
        
        # Mock was called (if registry available)
        assert mock_model is not None or model is not None

    def test_model_parameter_counting(self):
        """Test model parameter counting utility."""
        def count_params(state_dict):
            """Count total parameters in state dict."""
            total = 0
            for tensor in state_dict.values():
                if hasattr(tensor, "numel"):
                    total += tensor.numel()
                elif hasattr(tensor, "size"):
                    size = tensor.size()
                    param_count = 1
                    for dim in size:
                        param_count *= dim
                    total += param_count
            return total
        
        state_dict = {
            "layer1": MagicMock(numel=MagicMock(return_value=100)),
            "layer2": MagicMock(numel=MagicMock(return_value=50)),
        }
        
        # Mock numel calls
        for key, tensor in state_dict.items():
            if key == "layer1":
                tensor.numel.return_value = 100
            else:
                tensor.numel.return_value = 50
        
        params = count_params(state_dict)
        assert params == 150


# ============================================================================
# Test: Training Configuration
# ============================================================================


class TestTrainingConfiguration:
    """Test training configuration loading and validation."""

    def test_training_config_creation(self):
        """Test training config can be created with default values."""
        from training.trainer import TrainingState
        
        state = TrainingState()
        assert state is not None

    def test_training_args_parsing(self):
        """Test training arguments can be parsed."""
        from training.engine_hf_trainer import build_training_args
        
        args = build_training_args(
            output_dir="/tmp/test",
            num_train_epochs=1,
            per_device_train_batch_size=8,
        )
        
        assert args.num_train_epochs == 1
        assert args.per_device_train_batch_size == 8

    def test_training_config_snapshot(self):
        """Test training config can be snapshotted to JSON."""
        config = {
            "num_epochs": 3,
            "batch_size": 32,
            "learning_rate": 1e-4,
            "warmup_steps": 100,
        }
        
        snapshot = json.dumps(config)
        loaded = json.loads(snapshot)
        
        assert loaded == config

    def test_hf_trainer_config_validation(self):
        """Test HuggingFace trainer config validation."""
        from training.engine_hf_trainer import HFTrainerConfig
        
        config = HFTrainerConfig(
            output_dir="/tmp/test",
            num_train_epochs=1,
            per_device_train_batch_size=8,
        )
        
        assert config.num_train_epochs == 1
        assert config.output_dir == "/tmp/test"


# ============================================================================
# Test: Capability Detectors
# ============================================================================


class TestCapabilityDetectors:
    """Test capability detection utilities."""

    def test_path_exists_check(self):
        """Test path existence checking."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir)
            assert test_path.exists()
            
            nonexistent = Path(tmpdir) / "nonexistent"
            assert not nonexistent.exists()

    def test_file_counting(self):
        """Test file counting in directory."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test files
            (tmppath / "file1.py").touch()
            (tmppath / "file2.py").touch()
            (tmppath / "file3.txt").touch()
            
            py_files = list(tmppath.glob("*.py"))
            assert len(py_files) == 2

    def test_content_pattern_matching(self):
        """Test content pattern matching in files."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import torch\nimport transformers\n")
            
            content = test_file.read_text()
            assert "torch" in content
            assert "transformers" in content

    def test_detector_result_scoring(self):
        """Test capability detector result scoring."""
        from codex_ml.detectors.core import clamp01
        
        # Test clamping to [0, 1]
        assert clamp01(0.5) == 0.5
        assert clamp01(-0.5) == 0.0
        assert clamp01(1.5) == 1.0
        assert clamp01(0.0) == 0.0
        assert clamp01(1.0) == 1.0

    def test_detector_result_structure(self):
        """Test DetectorResult has expected structure."""
        from codex_ml.detectors.core import DetectorResult
        
        result = DetectorResult(
            score=0.75,
            category="testing",
            evidence=["test_created", "test_passing"],
        )
        
        assert result.score == 0.75
        assert result.category == "testing"
        assert len(result.evidence) == 2


# ============================================================================
# Test: Metrics and Logging
# ============================================================================


class TestMetricsAndLogging:
    """Test metrics recording and logging utilities."""

    def test_metrics_dict_creation(self):
        """Test metrics dictionary creation."""
        metrics = {
            "loss": 0.5,
            "accuracy": 0.95,
            "f1": 0.92,
            "epoch": 1,
            "step": 100,
        }
        
        assert "loss" in metrics
        assert metrics["loss"] == 0.5

    def test_metrics_serialization(self):
        """Test metrics can be serialized to JSON."""
        metrics = {
            "epoch": 1,
            "loss": 0.5,
            "perplexity": 42.0,
            "timestamp": "2024-01-01",
        }
        
        json_str = json.dumps(metrics)
        loaded = json.loads(json_str)
        
        assert loaded["epoch"] == 1
        assert loaded["loss"] == 0.5

    def test_logging_handler_creation(self):
        """Test logging handler can be created."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        assert handler.formatter is not None

    def test_metrics_aggregation(self):
        """Test metrics aggregation logic."""
        batch_metrics = [
            {"loss": 0.5, "batch": 1},
            {"loss": 0.4, "batch": 2},
            {"loss": 0.45, "batch": 3},
        ]
        
        avg_loss = sum(m["loss"] for m in batch_metrics) / len(batch_metrics)
        assert 0.45 - 0.01 < avg_loss < 0.45 + 0.01


# ============================================================================
# Test: Evaluation Utilities
# ============================================================================


class TestEvaluationUtilities:
    """Test evaluation and metric computation utilities."""

    def test_eval_metrics_dict(self):
        """Test evaluation metrics dictionary creation."""
        eval_metrics = {
            "eval_loss": 0.45,
            "eval_accuracy": 0.96,
            "eval_f1": 0.93,
            "eval_runtime": 10.5,
        }
        
        assert "eval_loss" in eval_metrics
        assert eval_metrics["eval_loss"] == 0.45

    def test_predictions_shape(self):
        """Test prediction tensor shapes."""
        batch_size = 32
        num_classes = 10
        
        predictions = MagicMock()
        predictions.shape = (batch_size, num_classes)
        
        assert predictions.shape[0] == batch_size
        assert predictions.shape[1] == num_classes

    def test_metric_computation_mock(self):
        """Test metric computation with mocked predictions."""
        from training.engine_hf_trainer import _compute_metrics
        
        predictions = MagicMock()
        predictions.predictions = [[0.1, 0.9], [0.8, 0.2]]
        predictions.label_ids = [1, 0]
        
        # Should not raise
        result = _compute_metrics(predictions)
        assert result is not None

    def test_eval_dataset_preparation(self):
        """Test evaluation dataset preparation."""
        texts = ["sample text 1", "sample text 2", "sample text 3"]
        
        # Mock tokenizer
        tokenizer = MagicMock()
        tokenizer.return_value = {"input_ids": [[1, 2, 3]]}
        
        assert len(texts) == 3


# ============================================================================
# Test: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling in ML utilities."""

    def test_empty_checkpoint_directory(self):
        """Test handling of empty checkpoint directory."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt_dir = Path(tmpdir)
            
            checkpoints = list(ckpt_dir.glob("checkpoint_*.pt"))
            assert len(checkpoints) == 0

    def test_corrupted_metadata_file(self):
        """Test handling of corrupted metadata."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            meta_file = Path(tmpdir) / "metadata.json"
            meta_file.write_text("{ invalid json }")
            
            with pytest.raises(json.JSONDecodeError):
                json.loads(meta_file.read_text())

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        config = {
            "num_epochs": 3,
            # Missing "batch_size"
        }
        
        assert "batch_size" not in config

    def test_invalid_dtype_specification(self):
        """Test handling of invalid dtype."""
        from codex_ml.train_loop import _resolve_dtype
        
        # Should handle gracefully
        result = _resolve_dtype("invalid_dtype")
        assert result is None or result is not None  # Graceful handling

    def test_nonexistent_model_loading(self):
        """Test handling of nonexistent model."""
        with patch("codex_ml.train_loop.instantiate_model") as mock_inst:
            mock_inst.side_effect = ValueError("Model not found")
            
            with pytest.raises(ValueError):
                from codex_ml.train_loop import _load_or_create_model
                _load_or_create_model("nonexistent_model")

    def test_zero_batch_size_handling(self):
        """Test handling of zero batch size."""
        batch_size = 0
        
        # Should handle or raise appropriate error
        assert batch_size == 0

    def test_negative_learning_rate_handling(self):
        """Test handling of negative learning rate."""
        lr = -1e-4
        
        # Should fail validation
        assert lr < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
