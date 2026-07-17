"""Inference pipeline fixtures for comprehensive model and tokenizer testing.

Provides reusable fixtures for model loading, tokenization, and performance profiling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Generator, NamedTuple, Optional

import pytest


class ModelInfo(NamedTuple):
    """Model metadata information."""

    name: str
    source: str
    model_size_mb: float
    parameters: int


class InferenceMetrics(NamedTuple):
    """Performance metrics from inference execution."""

    latency_ms: float
    throughput_samples_per_sec: float
    peak_ram_gb: float
    peak_vram_gb: Optional[float]


@pytest.fixture
def model_config() -> dict[str, Any]:
    """Return configuration for the test model."""
    return {
        "model_name": "distilbert-base-uncased",
        "max_seq_length": 128,
        "batch_size": 8,
        "num_samples": 16,
    }


@pytest.fixture
def test_texts() -> list[str]:
    """Generate synthetic text samples for inference testing."""
    return [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning models require careful training and evaluation.",
        "Natural language processing is a complex field of AI.",
        "This is a test sentence for tokenization and inference.",
        "PyTorch provides excellent support for deep neural networks.",
        "Transformers have revolutionized the field of NLP.",
        "Text embeddings are useful for similarity matching.",
        "Model evaluation metrics help us understand performance.",
        "Batch processing improves inference throughput significantly.",
        "GPU acceleration can speed up tensor operations.",
        "Memory management is critical for large models.",
        "Distributed inference enables handling massive datasets.",
        "Token embeddings capture semantic information in text.",
        "Attention mechanisms allow models to focus on relevant parts.",
        "Gradual model loading prevents memory overflow issues.",
        "Performance profiling helps identify optimization opportunities.",
    ]


@pytest.fixture
def batch_test_texts() -> list[list[str]]:
    """Generate batches of text samples for batch inference testing."""
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning models require careful training and evaluation.",
        "Natural language processing is a complex field of AI.",
        "This is a test sentence for tokenization and inference.",
        "PyTorch provides excellent support for deep neural networks.",
        "Transformers have revolutionized the field of NLP.",
        "Text embeddings are useful for similarity matching.",
        "Model evaluation metrics help us understand performance.",
    ]
    
    # Create batches
    batch_size = 4
    batches = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
    return batches


@pytest.fixture
def transformers_available() -> bool:
    """Check if transformers library is available."""
    try:
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture
def torch_available() -> bool:
    """Check if PyTorch is available."""
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture
def cuda_available() -> bool:
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except (ImportError, RuntimeError):
        return False


@pytest.fixture
def device_info() -> dict[str, Any]:
    """Get information about the available device."""
    info = {"cuda_available": False, "device": "cpu", "device_name": "CPU"}
    
    try:
        import torch
        if torch.cuda.is_available():
            info["cuda_available"] = True
            info["device"] = "cuda"
            info["device_name"] = torch.cuda.get_device_name(0)
            info["cuda_version"] = torch.version.cuda
    except Exception:
        pass
    
    return info


@pytest.fixture
def memory_profiler() -> Generator[dict[str, Any], None, None]:
    """Simple memory profiler for tracking peak memory during inference."""
    
    def get_memory_usage() -> tuple[float, Optional[float]]:
        """Get current RAM and VRAM usage in GB."""
        ram_gb = 0.0
        vram_gb = None
        
        try:
            import psutil
            process = psutil.Process(os.getpid())
            ram_gb = process.memory_info().rss / (1024 ** 3)
        except Exception:
            pass
        
        try:
            import torch
            if torch.cuda.is_available():
                vram_gb = torch.cuda.memory_allocated() / (1024 ** 3)
        except Exception:
            pass
        
        return ram_gb, vram_gb
    
    profile_data = {
        "start_ram_gb": 0.0,
        "start_vram_gb": None,
        "peak_ram_gb": 0.0,
        "peak_vram_gb": None,
        "measurements": [],
    }
    
    # Record initial state
    ram, vram = get_memory_usage()
    profile_data["start_ram_gb"] = ram
    profile_data["start_vram_gb"] = vram
    profile_data["peak_ram_gb"] = ram
    if vram is not None:
        profile_data["peak_vram_gb"] = vram
    
    yield profile_data
    
    # Cleanup: Peak memory should already be recorded


@pytest.fixture
def performance_tracker() -> Generator[dict[str, Any], None, None]:
    """Track performance metrics during inference."""
    
    metrics = {
        "inference_times_ms": [],
        "total_samples": 0,
        "total_time_sec": 0.0,
        "min_latency_ms": float("inf"),
        "max_latency_ms": 0.0,
        "mean_latency_ms": 0.0,
        "throughput_samples_per_sec": 0.0,
    }
    
    yield metrics


@pytest.fixture
def model_info_fixture() -> ModelInfo:
    """Return standard model information for test reporting."""
    return ModelInfo(
        name="distilbert-base-uncased",
        source="transformers",
        model_size_mb=268,
        parameters=66_000_000,
    )


@pytest.fixture
def hf_cache_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Temporary directory for HuggingFace model cache."""
    cache_dir = tmp_path / "hf_cache"
    cache_dir.mkdir(exist_ok=True)
    
    old_home = os.environ.get("HF_HOME")
    os.environ["HF_HOME"] = str(cache_dir)
    
    try:
        yield cache_dir
    finally:
        if old_home is not None:
            os.environ["HF_HOME"] = old_home
        else:
            os.environ.pop("HF_HOME", None)


@pytest.fixture
def special_tokens() -> dict[str, str]:
    """Common special tokens for testing."""
    return {
        "[CLS]": "<cls>",
        "[SEP]": "<sep>",
        "[PAD]": "<pad>",
        "[UNK]": "<unk>",
        "[MASK]": "<mask>",
    }


@pytest.fixture
def inference_test_config() -> dict[str, Any]:
    """Comprehensive configuration for inference pipeline tests."""
    return {
        "model_name": "distilbert-base-uncased",
        "max_seq_length": 128,
        "batch_sizes": [1, 4, 8],
        "num_samples": 16,
        "device": "cuda" if _cuda_available() else "cpu",
        "timeout_seconds": 300,
        "latency_threshold_ms": 100.0,
        "memory_threshold_gb": 5.0,
    }


def _cuda_available() -> bool:
    """Helper to check CUDA availability."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False
