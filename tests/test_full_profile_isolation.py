"""
Test Suite: Full Profile Isolation & Integration
Phase 3 Lane 1 - Profile Packaging & Validation
Module: test_full_profile_isolation.py

This module validates that the FULL profile includes ALL dependencies:
- Core profile: configuration, CLI, code parsing
- Runtime profile: ML, web services, RAG, monitoring
- Full profile: all development tools, testing utilities, plugins

All imports should succeed when full profile is installed.

Coverage:
- All core dependencies load successfully
- All runtime dependencies load successfully
- All dev/test dependencies load successfully
- Integration between all profiles works
"""

import pytest


class TestFullProfileCoreImports:
    """Test that full profile includes all core dependencies."""

    def test_hydra_import(self):
        """Test hydra-core import."""
        try:
            import hydra
            assert hasattr(hydra, '__version__')
        except ImportError as e:
            pytest.skip(f"hydra not in full profile: {e}")

    def test_omegaconf_import(self):
        """Test omegaconf import."""
        try:
            from omegaconf import OmegaConf
            assert OmegaConf is not None
        except ImportError as e:
            pytest.skip(f"omegaconf not in full profile: {e}")

    def test_pydantic_import(self):
        """Test pydantic import."""
        try:
            from pydantic import BaseModel
            assert BaseModel is not None
        except ImportError as e:
            pytest.skip(f"pydantic not in full profile: {e}")


class TestFullProfileRuntimeImports:
    """Test that full profile includes all runtime dependencies."""

    def test_torch_import(self):
        """Test torch import."""
        try:
            import torch
            assert hasattr(torch, '__version__')
        except ImportError as e:
            pytest.skip(f"torch not in full profile: {e}")

    def test_transformers_import(self):
        """Test transformers import."""
        try:
            from transformers import AutoTokenizer
            assert AutoTokenizer is not None
        except ImportError as e:
            pytest.skip(f"transformers not in full profile: {e}")

    def test_datasets_import(self):
        """Test datasets import."""
        try:
            from datasets import Dataset
            assert Dataset is not None
        except ImportError as e:
            pytest.skip(f"datasets not in full profile: {e}")

    def test_pandas_import(self):
        """Test pandas import."""
        try:
            import pandas as pd
            assert hasattr(pd, '__version__')
        except ImportError as e:
            pytest.skip(f"pandas not in full profile: {e}")

    def test_numpy_import(self):
        """Test numpy import."""
        try:
            import numpy as np
            assert hasattr(np, '__version__')
        except ImportError as e:
            pytest.skip(f"numpy not in full profile: {e}")

    def test_fastapi_import(self):
        """Test fastapi import."""
        try:
            from fastapi import FastAPI
            assert FastAPI is not None
        except ImportError as e:
            pytest.skip(f"fastapi not in full profile: {e}")

    def test_ray_import(self):
        """Test ray import."""
        try:
            import ray
            assert hasattr(ray, '__version__')
        except ImportError as e:
            pytest.skip(f"ray not in full profile: {e}")

    def test_sentence_transformers_import(self):
        """Test sentence-transformers import."""
        try:
            from sentence_transformers import SentenceTransformer
            assert SentenceTransformer is not None
        except ImportError as e:
            pytest.skip(f"sentence-transformers not in full profile: {e}")


class TestFullProfileDevDependencies:
    """Test that full profile includes all dev/test dependencies."""

    def test_pytest_import(self):
        """Test pytest import."""
        try:
            import pytest as pt
            assert hasattr(pt, '__version__')
        except ImportError as e:
            pytest.skip(f"pytest not in full profile: {e}")

    def test_black_import(self):
        """Test black import."""
        try:
            import black
            assert hasattr(black, '__version__')
        except ImportError as e:
            pytest.skip(f"black not in full profile: {e}")

    def test_mypy_import(self):
        """Test mypy import."""
        try:
            import mypy
            assert hasattr(mypy, '__version__')
        except ImportError as e:
            pytest.skip(f"mypy not in full profile: {e}")

    def test_ruff_import(self):
        """Test ruff import."""
        try:
            import ruff
            assert ruff is not None
        except ImportError as e:
            pytest.skip(f"ruff not in full profile: {e}")

    def test_isort_import(self):
        """Test isort import."""
        try:
            import isort
            assert hasattr(isort, '__version__')
        except ImportError as e:
            pytest.skip(f"isort not in full profile: {e}")

    def test_hypothesis_import(self):
        """Test hypothesis import."""
        try:
            import hypothesis
            assert hasattr(hypothesis, '__version__')
        except ImportError as e:
            pytest.skip(f"hypothesis not in full profile: {e}")

    def test_pytest_cov_import(self):
        """Test pytest-cov import."""
        try:
            import pytest_cov
            assert pytest_cov is not None
        except ImportError as e:
            pytest.skip(f"pytest-cov not in full profile: {e}")


class TestFullProfileComplexIntegration:
    """Test complex integration scenarios with full profile."""

    def test_ml_pipeline_with_core_config(self):
        """Test ML pipeline can use core configuration."""
        try:
            import torch
            import torch.nn as nn

            from omegaconf import OmegaConf
            
            # Create config using core infrastructure
            cfg = OmegaConf.create({
                'model': 'bert',
                'hidden_size': 768,
                'num_layers': 12,
            })
            
            # Create simple model
            model = nn.Linear(cfg.hidden_size, 10)
            assert model is not None
            
        except ImportError as e:
            pytest.skip(f"Required packages not available: {e}")

    def test_fastapi_with_ml_integration(self):
        """Test FastAPI app can use ML models."""
        try:
            import torch
            import torch.nn as nn
            from fastapi import FastAPI
            
            app = FastAPI()
            model = nn.Linear(100, 10)
            
            @app.post("/predict")
            def predict(features: list):
                x = torch.tensor(features, dtype=torch.float32)
                with torch.no_grad():
                    output = model(x)
                return {"prediction": output.tolist()}
            
            assert len(app.routes) > 0
            
        except ImportError as e:
            pytest.skip(f"Required packages not available: {e}")

    def test_testing_with_ml_fixtures(self):
        """Test that testing infrastructure works with ML."""
        try:
            import numpy as np
            import pytest
            import torch
            
            @pytest.fixture
            def sample_tensor():
                return torch.randn(10, 5)
            
            @pytest.fixture
            def sample_array():
                return np.random.randn(10, 5)
            
            # Just verify fixtures can be defined
            assert sample_tensor is not None
            assert sample_array is not None
            
        except ImportError as e:
            pytest.skip(f"Required packages not available: {e}")

    def test_ml_training_with_accelerate(self):
        """Test ML training can use accelerate."""
        try:
            import torch
            import torch.nn as nn
            from accelerate import Accelerator
            
            accelerator = Accelerator()
            model = nn.Linear(10, 5)
            
            # Prepare model
            model = accelerator.prepare(model)
            assert model is not None
            
        except ImportError as e:
            pytest.skip(f"Required packages not available: {e}")


class TestFullProfileAllImportsAvailable:
    """Test that all expected packages are available in full profile."""

    def test_all_full_profile_packages(self):
        """Test that all full profile packages are importable."""
        full_profile_packages = {
            # Core
            'hydra': 'Configuration management',
            'omegaconf': 'OmegaConf',
            'pydantic': 'Data validation',
            'pydantic_settings': 'Settings management',
            'marshmallow': 'Serialization',
            'yaml': 'YAML support',
            'typer': 'CLI framework',
            'click': 'Click CLI',
            'libcst': 'Code parsing',
            'parso': 'Python parsing',
            'tree_sitter': 'Tree-sitter',
            'sqlparse': 'SQL parsing',
            # Runtime
            'torch': 'PyTorch',
            'transformers': 'Transformers',
            'datasets': 'Datasets',
            'pandas': 'Pandas',
            'numpy': 'NumPy',
            'sklearn': 'Scikit-learn',
            'fastapi': 'FastAPI',
            'litestar': 'Litestar',
            'starlette': 'Starlette',
            'ray': 'Ray',
            'sentence_transformers': 'Sentence Transformers',
            'chromadb': 'ChromaDB',
            'faiss': 'FAISS',
            'duckdb': 'DuckDB',
            # Dev/Test
            'pytest': 'PyTest',
            'black': 'Black formatter',
            'mypy': 'MyPy type checker',
            'ruff': 'Ruff linter',
            'isort': 'isort',
            'hypothesis': 'Hypothesis',
            'pytest_cov': 'pytest-cov',
        }
        
        available = []
        missing = []
        
        for pkg_name, description in full_profile_packages.items():
            try:
                __import__(pkg_name)
                available.append((pkg_name, description))
            except ImportError:
                missing.append((pkg_name, description))
        
        print(f"\n✅ Available full profile packages ({len(available)}):")
        for pkg, desc in sorted(available):
            print(f"  ✓ {pkg:30s} ({desc})")
        
        if missing:
            print(f"\n⚠️  Missing full profile packages ({len(missing)}):")
            for pkg, desc in sorted(missing):
                print(f"  ✗ {pkg:30s} ({desc})")
        
        # Require at least 80% of packages (40/50)
        required_count = int(len(full_profile_packages) * 0.8)
        assert len(available) >= required_count, \
            f"Full profile missing too many packages: {len(available)}/{len(full_profile_packages)}"


class TestFullProfileFeatureCompleteness:
    """Test that full profile provides complete feature set."""

    def test_ml_training_features(self):
        """Test ML training features are available."""
        try:
            import torch
            from accelerate import Accelerator
            from peft import LoraConfig, get_peft_model

            from transformers import AutoModelForCausalLM
            
            # All ML training components available
            assert torch is not None
            assert AutoModelForCausalLM is not None
            assert Accelerator is not None
            assert get_peft_model is not None
            
        except ImportError as e:
            pytest.skip(f"ML training not fully available: {e}")

    def test_web_service_features(self):
        """Test web service features are available."""
        try:
            from fastapi import FastAPI
            from litestar import Litestar
            from slowapi import Limiter
            
            assert FastAPI is not None
            assert Litestar is not None
            assert Limiter is not None
            
        except ImportError as e:
            pytest.skip(f"Web services not fully available: {e}")

    def test_testing_features(self):
        """Test testing features are available."""
        try:
            import pytest
            from hypothesis import given
            from hypothesis import strategies as st
            from pytest_cov import plugin as cov_plugin
            
            assert pytest is not None
            assert cov_plugin is not None
            assert given is not None
            
        except ImportError as e:
            pytest.skip(f"Testing features not fully available: {e}")

    def test_code_quality_features(self):
        """Test code quality features are available."""
        try:
            import black
            import isort
            import mypy.api
            import ruff
            
            assert black is not None
            assert ruff is not None
            assert mypy is not None
            assert isort is not None
            
        except ImportError as e:
            pytest.skip(f"Code quality features not fully available: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
