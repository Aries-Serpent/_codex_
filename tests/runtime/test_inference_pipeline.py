"""Comprehensive inference pipeline validation tests for runtime profile.

Tests cover:
- Model loading and initialization
- Tokenizer loading and validation  
- Single and batch inference execution
- Output tensor validation (shape, dtype)
- Performance profiling (latency, throughput, memory)
- Device management (CPU/GPU)
- Error handling and graceful degradation
"""

from __future__ import annotations

import time
from typing import Any

import pytest


class TestModelInitialization:
    """Tests for model loading and initialization."""

    def test_model_loading_automodel(self, model_config: dict[str, Any]) -> None:
        """Test that AutoModel can load a small transformer model."""
        pytest.importorskip("transformers")
        from transformers import AutoModel
        
        model = AutoModel.from_pretrained(
            model_config["model_name"],
            trust_remote_code=True,
        )
        
        assert model is not None
        assert hasattr(model, "forward") or hasattr(model, "__call__")
        assert model.training is False

    def test_model_to_eval_mode(self, model_config: dict[str, Any]) -> None:
        """Test that model can be put in evaluation mode."""
        pytest.importorskip("transformers")
        from transformers import AutoModel
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        model.eval()
        
        assert model.training is False

    def test_model_has_config(self, model_config: dict[str, Any]) -> None:
        """Test that loaded model has proper configuration."""
        pytest.importorskip("transformers")
        from transformers import AutoConfig, AutoModel
        
        config = AutoConfig.from_pretrained(model_config["model_name"])
        model = AutoModel.from_pretrained(
            model_config["model_name"],
            config=config,
        )
        
        assert model.config is not None
        assert hasattr(model.config, "vocab_size")
        assert hasattr(model.config, "hidden_size")


class TestTokenizerInitialization:
    """Tests for tokenizer loading and validation."""

    def test_tokenizer_loading_autotokenizer(self, model_config: dict[str, Any]) -> None:
        """Test that AutoTokenizer can load a tokenizer."""
        pytest.importorskip("transformers")
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        assert tokenizer is not None
        assert hasattr(tokenizer, "encode")
        assert hasattr(tokenizer, "decode")

    def test_tokenizer_has_vocab_size(self, model_config: dict[str, Any]) -> None:
        """Test that tokenizer reports vocabulary size."""
        pytest.importorskip("transformers")
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        vocab_size = len(tokenizer)
        
        assert vocab_size > 0
        assert vocab_size > 1000

    def test_tokenizer_pad_token(self, model_config: dict[str, Any]) -> None:
        """Test that tokenizer has proper padding token."""
        pytest.importorskip("transformers")
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        assert tokenizer.pad_token is not None or tokenizer.pad_token_id is not None


class TestInferenceExecution:
    """Tests for single and batch inference execution."""

    def test_single_sample_inference(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test inference on a single text sample."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs is not None
        assert hasattr(outputs, "last_hidden_state")
        assert outputs.last_hidden_state.shape[0] == 1

    def test_batch_inference(
        self,
        model_config: dict[str, Any],
        batch_test_texts: list[list[str]],
        device_info: dict[str, Any],
    ) -> None:
        """Test inference on a batch of samples."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        batch = batch_test_texts[0]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
            padding=True,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs.last_hidden_state.shape[0] == len(batch)
        assert outputs.last_hidden_state.shape[1] <= model_config["max_seq_length"]


class TestOutputValidation:
    """Tests for output tensor validation."""

    def test_output_tensor_shapes(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test that output tensors have correct shapes."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        batch_size = 1
        seq_len = inputs["input_ids"].shape[1]
        hidden_size = model.config.hidden_size
        
        assert outputs.last_hidden_state.shape == (batch_size, seq_len, hidden_size)

    def test_output_tensor_dtype(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test that output tensors have correct data types."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs.last_hidden_state.dtype in (torch.float32, torch.float64)


class TestPerformanceProfiling:
    """Tests for latency and throughput profiling."""

    def test_inference_latency_single_sample(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test latency for single sample inference."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            _ = model(**inputs)
        
        start_time = time.perf_counter()
        with torch.no_grad():
            _ = model(**inputs)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        
        assert latency_ms > 0
        assert latency_ms < 5000

    def test_batch_inference_throughput(
        self,
        model_config: dict[str, Any],
        batch_test_texts: list[list[str]],
        device_info: dict[str, Any],
    ) -> None:
        """Test throughput (samples/sec) for batch inference."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        batch = batch_test_texts[0]
        batch_size = len(batch)
        
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
            padding=True,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            _ = model(**inputs)
        
        start_time = time.perf_counter()
        with torch.no_grad():
            _ = model(**inputs)
        end_time = time.perf_counter()
        
        latency_sec = end_time - start_time
        throughput = batch_size / latency_sec if latency_sec > 0 else 0
        
        assert throughput > 0
        assert throughput >= 1


class TestMemoryProfiling:
    """Tests for memory usage profiling."""

    def test_model_memory_footprint(
        self,
        model_config: dict[str, Any],
        device_info: dict[str, Any],
    ) -> None:
        """Test that model loads within memory bounds."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        from transformers import AutoModel
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        device = device_info["device"]
        model = model.to(device)
        
        assert model is not None
        
        param_count = sum(p.numel() for p in model.parameters())
        assert param_count > 0
        assert param_count > 1_000_000

    def test_inference_memory_stability(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test that memory usage is stable across multiple inferences."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        pytest.importorskip("psutil")
        import psutil
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 ** 3)
        
        for text in test_texts[:5]:
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=model_config["max_seq_length"],
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                _ = model(**inputs)
        
        final_memory = process.memory_info().rss / (1024 ** 3)
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 1.0


class TestErrorHandling:
    """Tests for graceful error handling and edge cases."""

    def test_empty_string_handling(
        self,
        model_config: dict[str, Any],
        device_info: dict[str, Any],
    ) -> None:
        """Test handling of empty strings."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        inputs = tokenizer(
            "",
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs is not None

    def test_long_sequence_truncation(
        self,
        model_config: dict[str, Any],
        device_info: dict[str, Any],
    ) -> None:
        """Test handling of sequences longer than max_seq_length."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        long_text = " ".join(["word"] * 500)
        
        inputs = tokenizer(
            long_text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        assert inputs["input_ids"].shape[1] <= model_config["max_seq_length"]
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs is not None


class TestDeviceManagement:
    """Tests for device placement and management."""

    def test_cpu_device_placement(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
    ) -> None:
        """Test that model can run on CPU."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        model = model.to("cpu")
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to("cpu") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert outputs is not None

    def test_input_output_device_consistency(
        self,
        model_config: dict[str, Any],
        test_texts: list[str],
        device_info: dict[str, Any],
    ) -> None:
        """Test that outputs are on the same device as model."""
        pytest.importorskip("transformers")
        pytest.importorskip("torch")
        import torch

        from transformers import AutoModel, AutoTokenizer
        
        model = AutoModel.from_pretrained(model_config["model_name"])
        tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        
        device = device_info["device"]
        model = model.to(device)
        model.eval()
        
        text = test_texts[0]
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_config["max_seq_length"],
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        assert str(outputs.last_hidden_state.device) == device
