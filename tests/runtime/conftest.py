"""Pytest fixtures for ML runtime profile validation tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_model_cache() -> Generator[Path, None, None]:
    """Create a temporary directory for model caching during tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cache = os.environ.get("HF_HOME")
        os.environ["HF_HOME"] = tmpdir
        try:
            yield Path(tmpdir)
        finally:
            if old_cache is not None:
                os.environ["HF_HOME"] = old_cache
            elif "HF_HOME" in os.environ:
                del os.environ["HF_HOME"]


@pytest.fixture
def pytorch_available() -> bool:
    """Check if PyTorch is available in the environment."""
    try:
        import torch
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
def get_system_memory() -> int:
    """Get available system memory in GB."""
    try:
        import psutil
        return int(psutil.virtual_memory().total / (1024 ** 3))
    except Exception:
        return 0


@pytest.fixture
def synthetic_text_data() -> list[str]:
    """Generate synthetic text data for testing."""
    return [
        "The machine learning model is very effective.",
        "PyTorch provides excellent support for deep learning.",
        "Transformers have revolutionized natural language processing.",
        "Scikit-learn is a popular library for machine learning.",
        "Transfer learning is a powerful technique in ML.",
    ]


@pytest.fixture
def synthetic_numerical_data() -> tuple[list[list[float]], list[int]]:
    """Generate synthetic numerical data for testing sklearn."""
    # Simple binary classification data
    X = [
        [0.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [0.5, 0.5],
        [1.5, 1.5],
    ]
    y = [0, 1, 1, 1, 0, 1]
    return X, y


@pytest.fixture
def dependency_versions() -> dict[str, str]:
    """Collect version information for all key ML dependencies."""
    versions = {}
    
    # PyTorch
    try:
        import torch
        versions["torch"] = torch.__version__
    except ImportError:
        versions["torch"] = "NOT_INSTALLED"
    
    # Transformers
    try:
        import transformers
        versions["transformers"] = transformers.__version__
    except ImportError:
        versions["transformers"] = "NOT_INSTALLED"
    
    # Scikit-learn
    try:
        import sklearn
        versions["scikit-learn"] = sklearn.__version__
    except ImportError:
        versions["scikit-learn"] = "NOT_INSTALLED"
    
    # NumPy
    try:
        import numpy
        versions["numpy"] = numpy.__version__
    except ImportError:
        versions["numpy"] = "NOT_INSTALLED"
    
    # Pandas
    try:
        import pandas
        versions["pandas"] = pandas.__version__
    except ImportError:
        versions["pandas"] = "NOT_INSTALLED"
    
    # Datasets (HuggingFace)
    try:
        import datasets
        versions["datasets"] = datasets.__version__
    except ImportError:
        versions["datasets"] = "NOT_INSTALLED"
    
    # Sentence-transformers
    try:
        import sentence_transformers
        versions["sentence-transformers"] = sentence_transformers.__version__
    except ImportError:
        versions["sentence-transformers"] = "NOT_INSTALLED"
    
    # Accelerate
    try:
        import accelerate
        versions["accelerate"] = accelerate.__version__
    except ImportError:
        versions["accelerate"] = "NOT_INSTALLED"
    
    # PEFT
    try:
        import peft
        versions["peft"] = peft.__version__
    except ImportError:
        versions["peft"] = "NOT_INSTALLED"
    
    # Ray
    try:
        import ray
        versions["ray"] = ray.__version__
    except ImportError:
        versions["ray"] = "NOT_INSTALLED"
    
    return versions
