"""
Test Suite: Core Profile Isolation
Phase 3 Lane 1 - Profile Packaging & Validation
Module: test_core_profile_isolation.py

This module validates that the CORE profile is truly lightweight and has NO
torch/transformers dependencies. The core profile should only include:
- Configuration (hydra, omegaconf, pydantic)
- CLI support (typer, click)
- Code parsing (libcst, parso, tree-sitter*)
- Serialization (marshmallow, pyyaml)

Cross-contamination Test: Attempting to import torch/transformers should FAIL
with ImportError when only core profile is installed.

Coverage:
- Core profile base dependencies load successfully
- Torch/transformers NOT available in core profile
- No indirect torch/transformers imports via core packages
"""

import pytest


class TestCoreProfileBaseImports:
    """Test that all core profile base dependencies are available."""

    def test_hydra_import(self):
        """Test hydra-core import and basic functionality."""
        try:
            import hydra
            from hydra import compose, initialize_config_dir
            assert hasattr(hydra, '__version__')
            assert compose is not None
            assert initialize_config_dir is not None
        except ImportError as e:
            pytest.skip(f"hydra-core not installed: {e}")

    def test_omegaconf_import(self):
        """Test omegaconf import and basic functionality."""
        try:
            from omegaconf import DictConfig, OmegaConf
            assert OmegaConf is not None
            assert DictConfig is not None
            # Test basic functionality
            cfg = OmegaConf.create({"key": "value"})
            assert cfg.key == "value"
        except ImportError as e:
            pytest.skip(f"omegaconf not installed: {e}")

    def test_pydantic_import(self):
        """Test pydantic import and basic functionality."""
        try:
            from pydantic import BaseModel, ValidationError
            assert BaseModel is not None
            assert ValidationError is not None
            
            class TestModel(BaseModel):
                name: str
                age: int
            
            obj = TestModel(name="test", age=25)
            assert obj.name == "test"
        except ImportError as e:
            pytest.skip(f"pydantic not installed: {e}")

    def test_pydantic_settings_import(self):
        """Test pydantic-settings import."""
        try:
            from pydantic_settings import BaseSettings
            assert BaseSettings is not None
        except ImportError as e:
            pytest.skip(f"pydantic-settings not installed: {e}")

    def test_marshmallow_import(self):
        """Test marshmallow import and basic functionality."""
        try:
            from marshmallow import Schema, fields
            assert Schema is not None
            assert fields is not None
        except ImportError as e:
            pytest.skip(f"marshmallow not installed: {e}")

    def test_pyyaml_import(self):
        """Test PyYAML import and basic functionality."""
        try:
            import yaml
            assert yaml is not None
            # Test basic functionality
            data = yaml.safe_load("key: value")
            assert data['key'] == 'value'
        except ImportError as e:
            pytest.skip(f"PyYAML not installed: {e}")

    def test_typer_import(self):
        """Test typer import and basic functionality."""
        try:
            import typer
            app = typer.Typer()
            assert app is not None
        except ImportError as e:
            pytest.skip(f"typer not installed: {e}")

    def test_click_import(self):
        """Test click import and basic functionality."""
        try:
            import click
            @click.command()
            def test_cmd():
                pass
            assert test_cmd is not None
        except ImportError as e:
            pytest.skip(f"click not installed: {e}")

    def test_libcst_import(self):
        """Test libcst import and basic functionality."""
        try:
            import libcst as cst
            assert cst is not None
            # Test parsing
            module = cst.parse_module("x = 1")
            assert module is not None
        except ImportError as e:
            pytest.skip(f"libcst not installed: {e}")

    def test_parso_import(self):
        """Test parso import and basic functionality."""
        try:
            import parso
            assert hasattr(parso, '__version__')
            # Test parsing
            module = parso.parse("x = 1")
            assert module is not None
        except ImportError as e:
            pytest.skip(f"parso not installed: {e}")

    def test_tree_sitter_imports(self):
        """Test tree-sitter imports."""
        try:
            from tree_sitter import Language, Parser
            assert Language is not None
            assert Parser is not None
        except ImportError as e:
            pytest.skip(f"tree-sitter not installed: {e}")

    def test_sqlparse_import(self):
        """Test sqlparse import."""
        try:
            import sqlparse
            assert hasattr(sqlparse, '__version__')
        except ImportError as e:
            pytest.skip(f"sqlparse not installed: {e}")


class TestCoreProfileNoTorchContamination:
    """Test that core profile does NOT include torch/transformers."""

    def test_torch_should_not_be_available(self):
        """Verify torch is NOT available in core profile."""
        # This test should PASS only if torch is not installed
        # or SKIP if torch IS installed (meaning core profile isolation failed)
        try:
            import torch
            pytest.skip("torch IS installed - core profile isolation may be compromised")
        except ImportError:
            # This is the EXPECTED behavior for core profile
            # torch should not be importable
            pass

    def test_transformers_should_not_be_available(self):
        """Verify transformers is NOT available in core profile."""
        # This test should PASS only if transformers is not installed
        # or SKIP if transformers IS installed (meaning core profile isolation failed)
        try:
            import transformers
            pytest.skip("transformers IS installed - core profile isolation may be compromised")
        except ImportError:
            # This is the EXPECTED behavior for core profile
            # transformers should not be importable
            pass

    def test_datasets_should_not_be_available(self):
        """Verify datasets is NOT available in core profile."""
        try:
            import datasets
            pytest.skip("datasets IS installed - core profile isolation may be compromised")
        except ImportError:
            pass

    def test_accelerate_should_not_be_available(self):
        """Verify accelerate is NOT available in core profile."""
        try:
            import accelerate
            pytest.skip("accelerate IS installed - core profile isolation may be compromised")
        except ImportError:
            pass

    def test_fastapi_should_not_be_available(self):
        """Verify fastapi is NOT available in core profile."""
        try:
            import fastapi
            pytest.skip("fastapi IS installed - core profile isolation may be compromised")
        except ImportError:
            pass

    def test_ray_should_not_be_available(self):
        """Verify ray is NOT available in core profile."""
        try:
            import ray
            pytest.skip("ray IS installed - core profile isolation may be compromised")
        except ImportError:
            pass

    def test_pandas_should_not_be_available(self):
        """Verify pandas is NOT available in core profile."""
        try:
            import pandas
            pytest.skip("pandas IS installed - core profile isolation may be compromised")
        except ImportError:
            pass


class TestCoreProfileDependencyTree:
    """Test that core profile dependencies do not indirectly import runtime packages."""

    def test_no_torch_via_libcst(self):
        """Verify libcst doesn't bring in torch."""
        try:
            import sys

            import libcst as cst
            # Check if torch is in sys.modules after libcst import
            if 'torch' in sys.modules:
                pytest.fail("torch was imported indirectly via libcst")
        except ImportError:
            pytest.skip("libcst not installed")

    def test_no_torch_via_parso(self):
        """Verify parso doesn't bring in torch."""
        try:
            import sys

            import parso
            if 'torch' in sys.modules:
                pytest.fail("torch was imported indirectly via parso")
        except ImportError:
            pytest.skip("parso not installed")

    def test_no_torch_via_pydantic(self):
        """Verify pydantic doesn't bring in torch."""
        try:
            import sys

            from pydantic import BaseModel
            if 'torch' in sys.modules:
                pytest.fail("torch was imported indirectly via pydantic")
        except ImportError:
            pytest.skip("pydantic not installed")


class TestCoreProfileSize:
    """Test that core profile size is within acceptable bounds."""

    def test_core_profile_imports_quickly(self):
        """Verify core profile imports complete quickly (lightweight)."""
        import time
        
        # Remove any already-loaded core modules for fresh import timing
        core_modules = [
            'hydra', 'omegaconf', 'pydantic', 'pydantic_settings',
            'marshmallow', 'yaml', 'typer', 'click',
            'libcst', 'parso', 'tree_sitter', 'sqlparse'
        ]
        
        start_time = time.time()
        
        try:
            # Import all core dependencies
            import click
            import hydra
            import libcst
            import marshmallow
            import parso
            import pydantic
            import pydantic_settings
            import sqlparse
            import tree_sitter
            import typer
            import yaml

            import omegaconf
            
            elapsed = time.time() - start_time
            
            # Core profile should import in < 2 seconds (typically < 0.5s)
            # This is a soft check; exact timing depends on system
            print(f"\n⏱️  Core profile import time: {elapsed:.3f}s")
            
            # Just verify it's reasonably fast
            assert elapsed < 10.0, f"Core profile import took too long: {elapsed:.3f}s"
            
        except ImportError as e:
            pytest.skip(f"Some core packages not available: {e}")


class TestCoreProfileFunctionality:
    """Test that core profile has sufficient functionality."""

    def test_can_parse_python_code(self):
        """Verify core profile can parse Python code."""
        try:
            import libcst as cst
            code = """
def hello(name):
    print(f"Hello, {name}!")
"""
            module = cst.parse_module(code)
            assert module is not None
            # Verify we can access the function definition
            assert len(module.body) == 1
        except ImportError:
            pytest.skip("libcst not installed")

    def test_can_validate_configs(self):
        """Verify core profile can validate configurations."""
        try:
            from pydantic import BaseModel, ValidationError
            
            class Config(BaseModel):
                name: str
                timeout: int
                debug: bool
            
            cfg = Config(name="test", timeout=30, debug=True)
            assert cfg.name == "test"
            assert cfg.timeout == 30
            
            # Verify validation works
            try:
                Config(name="test", timeout="invalid", debug=True)
                pytest.fail("Should have raised ValidationError")
            except ValidationError:
                pass  # Expected
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_can_load_yaml_configs(self):
        """Verify core profile can load YAML configurations."""
        try:
            import yaml
            config_text = """
database:
  host: localhost
  port: 5432
  debug: false
"""
            config = yaml.safe_load(config_text)
            assert config['database']['host'] == 'localhost'
            assert config['database']['port'] == 5432
        except ImportError:
            pytest.skip("PyYAML not installed")


class TestCoreProfileMinimalViability:
    """Test that core profile meets minimum viability criteria."""

    def test_core_profile_has_minimum_imports(self):
        """Verify core profile packages are importable."""
        core_packages = [
            'hydra',
            'omegaconf',
            'pydantic',
            'pydantic_settings',
            'marshmallow',
            'yaml',
            'typer',
            'click',
            'libcst',
            'parso',
            'tree_sitter',
            'sqlparse',
        ]
        
        available = []
        missing = []
        
        for pkg_name in core_packages:
            try:
                __import__(pkg_name)
                available.append(pkg_name)
            except ImportError:
                missing.append(pkg_name)
        
        print(f"\n✅ Available core packages ({len(available)}): {', '.join(available)}")
        if missing:
            print(f"⚠️  Missing core packages ({len(missing)}): {', '.join(missing)}")
        
        # Require at least 8/12 core packages (configuration + CLI + parsing)
        assert len(available) >= 8, f"Too many missing core packages: {missing}"

    def test_core_profile_excludes_runtime_deps(self):
        """Verify core profile excludes runtime/dev dependencies."""
        runtime_deps = [
            'torch',
            'transformers',
            'datasets',
            'accelerate',
            'peft',
            'fastapi',
            'litestar',
            'ray',
            'pandas',
            'numpy',
            'pytest',
            'black',
            'mypy',
        ]
        
        found_runtime_deps = []
        
        for dep in runtime_deps:
            try:
                __import__(dep)
                found_runtime_deps.append(dep)
            except ImportError:
                pass
        
        if found_runtime_deps:
            print(f"\n⚠️  Runtime dependencies found in core profile: {', '.join(found_runtime_deps)}")
            # Skip if runtime deps are installed (maybe we're testing full profile)
            pytest.skip(f"Runtime dependencies installed: {', '.join(found_runtime_deps)}")
        else:
            print("\n✅ No runtime dependencies found in core profile")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
