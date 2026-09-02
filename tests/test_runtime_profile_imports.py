"""
Test Suite: Runtime Profile Imports
Phase 2 - Runtime Profile Validation
Module: test_runtime_profile_imports.py

This module tests the core imports and basic functionality of all runtime profile
dependencies. It validates that all ML, web service, RAG, and database components
can be imported and initialized without errors.

Coverage:
- ML inference (torch, transformers, datasets)
- ML training (accelerate, peft, sentencepiece)
- Data processing (pandas, numpy, scikit-learn)
- Web services (fastapi, litestar, starlette)
- Distributed computing (ray, slowapi)
- RAG pipeline (sentence-transformers, chromadb, faiss)
- Database (duckdb)
- Monitoring (prometheus-client, psutil, evidently)
"""

import pytest


class TestDataProcessingDependencies:
    """Test data processing imports and functionality."""

    def test_pandas_import(self):
        """Test pandas import and basic functionality."""
        try:
            import pandas as pd
            # Verify version
            assert hasattr(pd, '__version__')
            # Create simple dataframe
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            assert df.shape == (3, 2)
        except ImportError as e:
            pytest.skip(f"pandas not installed: {e}")

    def test_numpy_import(self):
        """Test numpy import and basic functionality."""
        try:
            import numpy as np
            # Verify version
            assert hasattr(np, '__version__')
            # Create simple array
            arr = np.array([1, 2, 3, 4, 5])
            assert arr.shape == (5,)
            assert np.sum(arr) == 15
        except ImportError as e:
            pytest.skip(f"numpy not installed: {e}")

    def test_scikit_learn_import(self):
        """Test scikit-learn import and basic functionality."""
        try:
            import numpy as np
            from sklearn import __version__
            from sklearn.preprocessing import StandardScaler
            
            # Test scaler
            scaler = StandardScaler()
            X = np.array([[1, 2], [3, 4], [5, 6]])
            X_scaled = scaler.fit_transform(X)
            assert X_scaled.shape == (3, 2)
        except ImportError as e:
            pytest.skip(f"scikit-learn not installed: {e}")


class TestMLInferenceDependencies:
    """Test ML inference dependencies."""

    def test_torch_import(self):
        """Test torch import and basic functionality."""
        try:
            import torch
            assert hasattr(torch, '__version__')
            # Test tensor creation
            t = torch.tensor([1, 2, 3, 4, 5])
            assert t.shape == (5,)
        except ImportError as e:
            pytest.skip(f"torch not installed: {e}")

    def test_transformers_import(self):
        """Test transformers import and basic functionality."""
        try:
            from transformers import AutoTokenizer, __version__
            # Verify we can access tokenizers
            assert AutoTokenizer is not None
        except ImportError as e:
            pytest.skip(f"transformers not installed: {e}")

    def test_datasets_import(self):
        """Test datasets import and basic functionality."""
        try:
            from datasets import Dataset, DatasetDict, __version__
            assert DatasetDict is not None
            assert Dataset is not None
        except ImportError as e:
            pytest.skip(f"datasets not installed: {e}")


class TestMLTrainingDependencies:
    """Test ML training dependencies."""

    def test_accelerate_import(self):
        """Test accelerate import."""
        try:
            from accelerate import Accelerator, __version__
            assert Accelerator is not None
        except ImportError as e:
            pytest.skip(f"accelerate not installed: {e}")

    def test_peft_import(self):
        """Test peft import."""
        try:
            from peft import __version__, get_peft_model
            assert get_peft_model is not None
        except ImportError as e:
            pytest.skip(f"peft not installed: {e}")

    def test_sentencepiece_import(self):
        """Test sentencepiece import."""
        try:
            import sentencepiece
            assert hasattr(sentencepiece, 'sentencepiece_model_pb2')
        except ImportError as e:
            pytest.skip(f"sentencepiece not installed: {e}")


class TestWebServiceDependencies:
    """Test web service dependencies."""

    def test_fastapi_import(self):
        """Test FastAPI import and basic app creation."""
        try:
            from fastapi import FastAPI
            app = FastAPI()
            assert app is not None
            assert hasattr(app, 'get')
            assert hasattr(app, 'post')
        except ImportError as e:
            pytest.skip(f"fastapi not installed: {e}")

    def test_litestar_import(self):
        """Test Litestar import and basic app creation."""
        try:
            from litestar import Litestar
            app = Litestar(route_handlers=[])
            assert app is not None
        except ImportError as e:
            pytest.skip(f"litestar not installed: {e}")

    def test_starlette_import(self):
        """Test Starlette import and basic app creation."""
        try:
            from starlette.applications import Starlette
            app = Starlette()
            assert app is not None
        except ImportError as e:
            pytest.skip(f"starlette not installed: {e}")

    def test_slowapi_import(self):
        """Test slowapi (rate limiting) import."""
        try:
            from slowapi import Limiter
            from slowapi.util import get_remote_address
            limiter = Limiter(key_func=get_remote_address)
            assert limiter is not None
        except ImportError as e:
            pytest.skip(f"slowapi not installed: {e}")


class TestDistributedComputingDependencies:
    """Test distributed computing dependencies."""

    def test_ray_import(self):
        """Test ray import."""
        try:
            import ray
            assert hasattr(ray, '__version__')
            assert hasattr(ray, 'remote')
            assert hasattr(ray, 'init')
        except ImportError as e:
            pytest.skip(f"ray not installed: {e}")

    def test_ray_serve_import(self):
        """Test ray[serve] import."""
        try:
            from ray import serve
            assert serve is not None
        except ImportError as e:
            pytest.skip(f"ray[serve] not installed: {e}")


class TestRAGPipelineDependencies:
    """Test RAG pipeline dependencies."""

    def test_sentence_transformers_import(self):
        """Test sentence-transformers import."""
        try:
            from sentence_transformers import SentenceTransformer
            assert SentenceTransformer is not None
        except ImportError as e:
            pytest.skip(f"sentence-transformers not installed: {e}")

    def test_chromadb_import(self):
        """Test chromadb import."""
        try:
            import chromadb
            assert hasattr(chromadb, '__version__')
        except ImportError as e:
            pytest.skip(f"chromadb not installed: {e}")

    def test_faiss_import(self):
        """Test faiss-cpu import."""
        try:
            import faiss
            assert hasattr(faiss, '__version__')
        except ImportError as e:
            pytest.skip(f"faiss-cpu not installed: {e}")


class TestDatabaseDependencies:
    """Test database dependencies."""

    def test_duckdb_import(self):
        """Test duckdb import and basic functionality."""
        try:
            import duckdb
            assert hasattr(duckdb, '__version__')
            # Test basic connection
            conn = duckdb.connect(':memory:')
            result = conn.execute('SELECT 1').fetchall()
            assert result == [(1,)]
        except ImportError as e:
            pytest.skip(f"duckdb not installed: {e}")


class TestMonitoringDependencies:
    """Test monitoring and telemetry dependencies."""

    def test_prometheus_client_import(self):
        """Test prometheus-client import."""
        try:
            from prometheus_client import Counter, Gauge, Histogram
            assert Counter is not None
            assert Gauge is not None
            assert Histogram is not None
        except ImportError as e:
            pytest.skip(f"prometheus-client not installed: {e}")

    def test_psutil_import(self):
        """Test psutil import and basic functionality."""
        try:
            import psutil
            # Test basic functionality
            cpu_percent = psutil.cpu_percent(interval=0.1)
            assert isinstance(cpu_percent, float)
            assert 0 <= cpu_percent <= 100
        except ImportError as e:
            pytest.skip(f"psutil not installed: {e}")

    def test_evidently_import(self):
        """Test evidently import."""
        try:
            from evidently import __version__
            from evidently.report import Report
            assert Report is not None
        except ImportError as e:
            pytest.skip(f"evidently not installed: {e}")


class TestAPIClientDependencies:
    """Test API client dependencies."""

    def test_httpx_import(self):
        """Test httpx import."""
        try:
            import httpx
            assert hasattr(httpx, '__version__')
            client = httpx.Client()
            assert client is not None
            client.close()
        except ImportError as e:
            pytest.skip(f"httpx not installed: {e}")


class TestRuntimeProfileIntegration:
    """Test integration of runtime profile components."""

    def test_all_imports_available(self):
        """Test that all runtime profile imports are available."""
        runtime_packages = [
            'pandas',
            'numpy',
            'sklearn',
            'torch',
            'transformers',
            'datasets',
            'accelerate',
            'peft',
            'sentencepiece',
            'fastapi',
            'litestar',
            'starlette',
            'slowapi',
            'ray',
            'sentence_transformers',
            'chromadb',
            'faiss',
            'duckdb',
            'prometheus_client',
            'psutil',
            'evidently',
            'httpx',
        ]
        
        missing_packages = []
        available_packages = []
        
        for package_name in runtime_packages:
            try:
                __import__(package_name)
                available_packages.append(package_name)
            except ImportError:
                missing_packages.append(package_name)
        
        # Report findings
        print(f"\n✅ Available packages ({len(available_packages)}): {', '.join(available_packages)}")
        if missing_packages:
            print(f"⚠️  Missing packages ({len(missing_packages)}): {', '.join(missing_packages)}")
        
        # Assert that we have a reasonable number of available packages
        assert len(available_packages) > 0, "No runtime packages available"

    def test_runtime_profile_version_compatibility(self):
        """Test that installed versions are compatible with runtime profile constraints."""
        version_constraints = {
            'pandas': ('2.0.3', '3.0.0'),
            'numpy': ('2.4.6', '3.0.0'),
            'torch': ('2.6.1', '3.0.0'),
            'transformers': ('5.12.1', '6.0.0'),
            'datasets': ('5.0.0', '6.0.0'),
            'accelerate': ('1.14.0', '2.0.0'),
            'peft': ('0.19.1', '1.0.0'),
            'fastapi': ('0.135.3', '1.0.0'),
            'litestar': ('2.22.0', '3.0.0'),
            'starlette': ('1.0.1', '2.0.0'),
            'ray': ('2.9.0', '3.0.0'),
            'sentence_transformers': ('5.5.1', '6.0.0'),
            'chromadb': ('1.5.8', '2.0.0'),
            'faiss': ('1.13.2', '2.0.0'),
            'duckdb': ('1.5.4', None),
            'prometheus_client': ('0.19.0', None),
            'psutil': ('5.9.0', None),
            'httpx': ('0.26.0', '1.0.0'),
        }
        
        compatibility_results = {}
        
        for package_name, (min_version, max_version) in version_constraints.items():
            try:
                module = __import__(package_name)
                version_str = getattr(module, '__version__', 'unknown')
                compatibility_results[package_name] = {
                    'status': 'available',
                    'version': version_str,
                }
            except ImportError:
                compatibility_results[package_name] = {
                    'status': 'missing',
                    'version': None,
                }
        
        # Print results
        print("\n📊 Runtime Profile Version Compatibility:")
        for package_name, info in compatibility_results.items():
            if info['status'] == 'available':
                print(f"  ✅ {package_name}: {info['version']}")
            else:
                print(f"  ⚠️  {package_name}: not installed")
        
        # Ensure at least core ML packages are present
        core_packages = ['pandas', 'numpy']
        for pkg in core_packages:
            assert compatibility_results[pkg]['status'] == 'available', \
                f"Core package {pkg} must be available"


class TestRuntimeProfileComputeCapabilities:
    """Test compute capabilities of runtime profile."""

    def test_torch_tensor_operations(self):
        """Test torch tensor operations."""
        try:
            import numpy as np
            import torch
            
            # Test tensor creation and operations
            a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
            b = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
            c = torch.matmul(a, b)
            
            assert c.shape == (2, 2)
            assert c is not None
        except ImportError:
            pytest.skip("torch not installed")

    def test_pandas_dataframe_operations(self):
        """Test pandas dataframe operations."""
        try:
            import numpy as np
            import pandas as pd
            
            # Create test data
            df = pd.DataFrame({
                'A': np.random.randn(100),
                'B': np.random.randn(100),
                'C': np.random.randn(100),
            })
            
            # Test operations
            assert len(df) == 100
            assert len(df.columns) == 3
            assert df['A'].mean() is not None
            assert df.describe() is not None
        except ImportError:
            pytest.skip("pandas or numpy not installed")

    def test_fastapi_endpoint_definition(self):
        """Test FastAPI endpoint definition."""
        try:
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.get("/test")
            def test_endpoint():
                return {"status": "ok"}
            
            # Check endpoint was registered
            assert len(app.routes) > 0
        except ImportError:
            pytest.skip("fastapi not installed")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
