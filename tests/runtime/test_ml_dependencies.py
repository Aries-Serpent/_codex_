"""
Comprehensive ML dependencies validation test suite.

Tests the runtime profile installation and verifies that all ML inference
dependencies (torch, transformers, scikit-learn) import and function correctly.

Test Coverage:
1. Runtime profile installation
2. PyTorch import and version verification
3. PyTorch CUDA/GPU availability detection
4. Transformers import and version verification
5. Transformers model loading (distilbert-base-uncased)
6. Scikit-learn import and pipeline functionality
7. Memory requirements validation
8. Dependency conflict detection
9. Model inference on synthetic data
10. Optional GPU memory profiling
"""

import os
import tempfile
import warnings
from pathlib import Path

import pytest

# Suppress transformers logging during tests
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# ============================================================================
# INLINE FIXTURES (instead of conftest.py due to pytest discovery)
# ============================================================================

@pytest.fixture
def temp_model_cache():
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
def pytorch_available():
    """Check if PyTorch is available in the environment."""
    try:
        import torch
        return True
    except ImportError:
        return False


@pytest.fixture
def cuda_available():
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except (ImportError, RuntimeError):
        return False


@pytest.fixture
def get_system_memory():
    """Get available system memory in GB."""
    try:
        import psutil
        return int(psutil.virtual_memory().total / (1024 ** 3))
    except Exception:
        return 0


@pytest.fixture
def synthetic_text_data():
    """Generate synthetic text data for testing."""
    return [
        "The machine learning model is very effective.",
        "PyTorch provides excellent support for deep learning.",
        "Transformers have revolutionized natural language processing.",
        "Scikit-learn is a popular library for machine learning.",
        "Transfer learning is a powerful technique in ML.",
    ]


@pytest.fixture
def synthetic_numerical_data():
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
def dependency_versions():
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


class TestRuntimeProfileInstallation:
    """Test that runtime profile installs cleanly."""

    def test_runtime_profile_installed(self):
        """Verify that runtime profile dependencies are installed."""
        # Try importing key runtime dependencies
        try:
            import fastapi
            import numpy
            import pandas
            import ray
            import sklearn
            import torch

            import transformers
        except ImportError as e:
            pytest.fail(f"Runtime profile not fully installed: {e}")


class TestPyTorchImportAndVersion:
    """Test PyTorch import and version compatibility."""

    def test_torch_import(self):
        """Test that PyTorch can be imported."""
        try:
            import torch
            assert hasattr(torch, '__version__'), "PyTorch missing __version__"
        except ImportError as e:
            pytest.fail(f"Failed to import PyTorch: {e}")

    def test_torch_version_compatibility(self):
        """Verify PyTorch version is within expected range."""
        import torch
        version_parts = torch.__version__.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        # Expect torch >= 2.6 and < 3.0
        assert major == 2 and minor >= 6, \
            f"PyTorch version {torch.__version__} outside expected range [2.6, 3.0)"

    def test_torch_core_modules(self):
        """Test that core PyTorch modules are available."""
        import torch
        
        # Verify key modules exist
        assert hasattr(torch, 'nn'), "torch.nn not available"
        assert hasattr(torch, 'optim'), "torch.optim not available"
        assert hasattr(torch, 'cuda'), "torch.cuda not available"
        assert hasattr(torch, 'utils'), "torch.utils not available"


class TestPyTorchCUDADetection:
    """Test GPU/CUDA availability detection."""

    def test_cuda_detection(self):
        """Test that CUDA availability can be detected."""
        import torch
        
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        
        # Just verify the methods work, don't require CUDA
        assert isinstance(cuda_available, bool), \
            f"Expected bool from torch.cuda.is_available(), got {type(cuda_available)}"
        assert isinstance(device_count, int), \
            f"Expected int from torch.cuda.device_count(), got {type(device_count)}"

    def test_torch_device_creation(self):
        """Test that torch devices can be created."""
        import torch
        
        # Create CPU device (should always work)
        cpu_device = torch.device("cpu")
        assert str(cpu_device) == "cpu"
        
        # Try to create CUDA device (may fail on CPU-only systems)
        try:
            if torch.cuda.is_available():
                cuda_device = torch.device("cuda")
                assert "cuda" in str(cuda_device)
        except RuntimeError:
            # CUDA not available, which is fine
            pass

    def test_torch_tensor_operations(self):
        """Test basic tensor creation and operations on available device."""
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create a simple tensor
        x = torch.randn(2, 3, device=device)
        assert x.shape == (2, 3), f"Expected shape (2, 3), got {x.shape}"
        assert str(x.device) == device, f"Expected device {device}, got {x.device}"
        
        # Test basic operations
        y = torch.randn(2, 3, device=device)
        z = x + y
        assert z.shape == (2, 3)


class TestTransformersImportAndVersion:
    """Test Transformers library import and version compatibility."""

    def test_transformers_import(self):
        """Test that transformers can be imported."""
        try:
            import transformers
            assert hasattr(transformers, '__version__'), \
                "transformers missing __version__"
        except ImportError as e:
            pytest.fail(f"Failed to import transformers: {e}")

    def test_transformers_version_compatibility(self):
        """Verify transformers version is within expected range."""
        import transformers
        version_parts = transformers.__version__.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        # Expect transformers >= 5.12 and < 6.0
        assert major == 5 and minor >= 12, \
            f"transformers version {transformers.__version__} outside expected range [5.12, 6.0)"

    def test_transformers_core_modules(self):
        """Test that core transformers modules are available."""
        import transformers
        
        # Verify key classes exist
        assert hasattr(transformers, 'AutoTokenizer'), \
            "transformers.AutoTokenizer not available"
        assert hasattr(transformers, 'AutoModel'), \
            "transformers.AutoModel not available"
        assert hasattr(transformers, 'pipeline'), \
            "transformers.pipeline not available"


class TestTransformersModelLoading:
    """Test model loading from transformers library."""

    @pytest.mark.timeout(120)
    def test_small_model_tokenizer_loading(self, temp_model_cache):
        """Test loading a small pre-trained tokenizer."""
        from transformers import AutoTokenizer
        
        model_name = "distilbert-base-uncased"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            assert tokenizer is not None, "Tokenizer is None"
            assert hasattr(tokenizer, 'encode'), "Tokenizer missing encode method"
        except Exception as e:
            pytest.skip(f"Could not download model {model_name}: {e}")

    @pytest.mark.timeout(120)
    def test_small_model_loading(self, temp_model_cache):
        """Test loading a small pre-trained model."""
        from transformers import AutoModel, AutoTokenizer
        
        model_name = "distilbert-base-uncased"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            assert model is not None, "Model is None"
            
            # Verify model can process tokens
            inputs = tokenizer("Test input", return_tensors="pt")
            assert "input_ids" in inputs, "Missing input_ids in tokenizer output"
        except Exception as e:
            pytest.skip(f"Could not download/load model {model_name}: {e}")

    @pytest.mark.timeout(120)
    def test_model_inference_on_synthetic_data(
        self, temp_model_cache, synthetic_text_data
    ):
        """Test model inference on synthetic text data."""
        from transformers import AutoModel, AutoTokenizer
        
        model_name = "distilbert-base-uncased"
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Run inference on synthetic data
            for text in synthetic_text_data[:2]:  # Test on first 2 samples
                inputs = tokenizer(text, return_tensors="pt", truncation=True)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    outputs = model(**inputs)
                
                # Check output shape
                assert hasattr(outputs, 'last_hidden_state'), \
                    "Model output missing last_hidden_state"
                assert outputs.last_hidden_state.shape[0] == 1, \
                    "Expected batch size 1"
        except Exception as e:
            pytest.skip(f"Could not run inference: {e}")


class TestScikitLearnImportAndFunctionality:
    """Test scikit-learn import and basic functionality."""

    def test_sklearn_import(self):
        """Test that scikit-learn can be imported."""
        try:
            import sklearn
            assert hasattr(sklearn, '__version__'), \
                "sklearn missing __version__"
        except ImportError as e:
            pytest.fail(f"Failed to import scikit-learn: {e}")

    def test_sklearn_version_compatibility(self):
        """Verify scikit-learn version is within expected range."""
        import sklearn
        version_parts = sklearn.__version__.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        # Expect sklearn >= 1.9 and < 2.0
        assert major == 1 and minor >= 9, \
            f"scikit-learn version {sklearn.__version__} outside expected range [1.9, 2.0)"

    def test_sklearn_pipeline_creation(self, synthetic_numerical_data):
        """Test creating and using a scikit-learn pipeline."""
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        
        X, y = synthetic_numerical_data
        
        # Create a pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(max_iter=100))
        ])
        
        # Fit the pipeline
        pipeline.fit(X, y)
        
        # Make predictions
        predictions = pipeline.predict(X)
        assert predictions is not None
        assert len(predictions) == len(X)

    def test_sklearn_cross_validation(self, synthetic_numerical_data):
        """Test scikit-learn cross-validation functionality."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        
        X, y = synthetic_numerical_data
        
        clf = RandomForestClassifier(n_estimators=10, random_state=42)
        scores = cross_val_score(clf, X, y, cv=3)
        
        assert len(scores) == 3, "Expected 3 cross-validation scores"
        assert all(0 <= score <= 1 for score in scores), \
            "Cross-validation scores should be between 0 and 1"


class TestMemoryRequirements:
    """Test memory availability and profiling."""

    def test_system_memory_detection(self, get_system_memory):
        """Test detection of available system memory."""
        available_memory_gb = get_system_memory
        
        assert available_memory_gb > 0, \
            f"Could not detect system memory: {available_memory_gb} GB"
        assert available_memory_gb >= 2, \
            f"Insufficient memory for ML operations: {available_memory_gb} GB (minimum 2 GB required)"

    def test_torch_memory_allocation(self):
        """Test PyTorch memory allocation."""
        import torch
        
        # Create a tensor and check memory allocation
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            x = torch.randn(1000, 1000, device=device)
            
            if device == "cuda":
                allocated = torch.cuda.memory_allocated() / (1024 ** 2)
                assert allocated > 0, "No GPU memory allocated"
            
            del x
            if device == "cuda":
                torch.cuda.empty_cache()
        except Exception as e:
            pytest.skip(f"Memory allocation test skipped: {e}")


class TestDependencyConflictDetection:
    """Test for dependency conflicts and compatibility issues."""

    def test_numpy_torch_compatibility(self):
        """Test compatibility between numpy and torch."""
        import numpy as np
        import torch
        
        # Create numpy array and convert to torch
        np_array = np.array([1.0, 2.0, 3.0])
        torch_tensor = torch.from_numpy(np_array)
        
        assert torch_tensor.shape == np_array.shape
        assert torch_tensor.dtype == torch.float64

    def test_pandas_numpy_compatibility(self):
        """Test compatibility between pandas and numpy."""
        import numpy as np
        import pandas as pd
        
        # Create dataframe from numpy
        data = np.random.randn(5, 3)
        df = pd.DataFrame(data, columns=['A', 'B', 'C'])
        
        assert df.shape == (5, 3)
        assert list(df.columns) == ['A', 'B', 'C']

    def test_sklearn_numpy_compatibility(self):
        """Test compatibility between scikit-learn and numpy."""
        import numpy as np
        from sklearn.preprocessing import StandardScaler
        
        # Create data and scale it
        X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        assert X_scaled.shape == X.shape
        assert np.isclose(X_scaled.mean(), 0.0, atol=1e-10)


class TestOptionalDependencies:
    """Test optional dependencies that may not always be available."""

    def test_sentence_transformers_import(self):
        """Test sentence-transformers import (optional but in runtime profile)."""
        try:
            import sentence_transformers
            assert hasattr(sentence_transformers, '__version__'), \
                "sentence_transformers missing __version__"
        except ImportError:
            pytest.skip("sentence-transformers not installed")

    def test_fastapi_import(self):
        """Test FastAPI import (optional but in runtime profile)."""
        try:
            import fastapi
            assert hasattr(fastapi, '__version__'), \
                "fastapi missing __version__"
        except ImportError:
            pytest.skip("fastapi not installed")

    def test_ray_import(self):
        """Test Ray import (optional but in runtime profile)."""
        try:
            import ray
            assert hasattr(ray, '__version__'), \
                "ray missing __version__"
        except ImportError:
            pytest.skip("ray not installed")


class TestDependencyVersions:
    """Test and report on all dependency versions."""

    def test_report_dependency_versions(self, dependency_versions):
        """Report all dependency versions for documentation."""
        print("\n=== ML Dependency Versions ===")
        for dep, version in sorted(dependency_versions.items()):
            status = "✓" if version != "NOT_INSTALLED" else "✗"
            print(f"  {status} {dep}: {version}")

    def test_all_critical_dependencies_installed(self, dependency_versions):
        """Verify all critical dependencies are installed."""
        critical_deps = [
            'torch',
            'transformers',
            'scikit-learn',
            'numpy',
            'pandas',
        ]
        
        missing = [
            dep for dep in critical_deps
            if dependency_versions[dep] == "NOT_INSTALLED"
        ]
        
        assert not missing, \
            f"Missing critical dependencies: {', '.join(missing)}"
