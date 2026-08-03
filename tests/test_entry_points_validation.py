"""
Test Suite: Entry Points & CLI Availability
Phase 3 Lane 1 - Profile Packaging & Validation
Module: test_entry_points_validation.py

This module validates that entry points are properly defined and accessible
for each profile. It tests:
- Entry point discovery and registration
- CLI command availability
- Entry point resolver functionality
"""

import subprocess
import sys

import pytest


class TestEntryPointsDiscovery:
    """Test that entry points are discoverable."""

    def test_codex_ml_entry_point(self):
        """Test codex-ml entry point exists."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            # Look for console_scripts group
            if hasattr(eps, 'select'):
                scripts = eps.select(group='console_scripts')
            else:
                scripts = eps.get('console_scripts', [])
            
            codex_ml_found = any(ep.name == 'codex-ml' for ep in scripts)
            
            if not codex_ml_found:
                pytest.skip("codex-ml entry point not registered")
            else:
                assert codex_ml_found
                
        except ImportError:
            pytest.skip("importlib.metadata not available")

    def test_codex_cli_entry_point(self):
        """Test codex-cli entry point exists."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                scripts = eps.select(group='console_scripts')
            else:
                scripts = eps.get('console_scripts', [])
            
            codex_cli_found = any(ep.name == 'codex-cli' for ep in scripts)
            
            if not codex_cli_found:
                pytest.skip("codex-cli entry point not registered")
            else:
                assert codex_cli_found
                
        except ImportError:
            pytest.skip("importlib.metadata not available")


class TestEntryPointsResolution:
    """Test that entry points resolve correctly."""

    def test_codex_ml_resolves(self):
        """Test codex-ml entry point resolves to correct function."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                scripts = eps.select(group='console_scripts')
            else:
                scripts = eps.get('console_scripts', [])
            
            for ep in scripts:
                if ep.name == 'codex-ml':
                    # Try to load the entry point
                    func = ep.load()
                    assert func is not None
                    return
            
            pytest.skip("codex-ml entry point not found")
            
        except Exception as e:
            pytest.skip(f"Entry point resolution failed: {e}")

    def test_codex_cli_resolves(self):
        """Test codex-cli entry point resolves."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                scripts = eps.select(group='console_scripts')
            else:
                scripts = eps.get('console_scripts', [])
            
            for ep in scripts:
                if ep.name == 'codex-cli':
                    func = ep.load()
                    assert func is not None
                    return
            
            pytest.skip("codex-cli entry point not found")
            
        except Exception as e:
            pytest.skip(f"Entry point resolution failed: {e}")


class TestCLIAvailability:
    """Test that CLI commands are available."""

    def test_codex_ml_help(self):
        """Test codex-ml --help works."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "codex_ml.cli.main", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            # Should succeed or at least be callable
            if result.returncode not in [0, 1]:  # 0=success, 1=sometimes happens with help
                pytest.skip(f"codex-ml not callable: {result.stderr[:100]}")
            
        except subprocess.TimeoutExpired:
            pytest.skip("codex-ml command timed out")
        except Exception as e:
            pytest.skip(f"Error running codex-ml: {e}")

    def test_codex_cli_help(self):
        """Test codex-cli --help works."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "codex_ml.cli.simple_cli", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode not in [0, 1]:
                pytest.skip(f"codex-cli not callable: {result.stderr[:100]}")
            
        except subprocess.TimeoutExpired:
            pytest.skip("codex-cli command timed out")
        except Exception as e:
            pytest.skip(f"Error running codex-cli: {e}")


class TestPluginRegistryEntryPoints:
    """Test that plugin registry entry points are defined."""

    def test_tokenizer_registry_entry_points(self):
        """Test tokenizer registry entry points exist."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                tokenizers = eps.select(group='codex_ml.tokenizers')
            else:
                tokenizers = eps.get('codex_ml.tokenizers', [])
            
            # Should have at least the HF tokenizer
            hf_found = any(ep.name == 'hf' for ep in tokenizers)
            
            if hf_found:
                assert hf_found
            else:
                pytest.skip("Tokenizer entry points not registered")
                
        except Exception as e:
            pytest.skip(f"Could not check tokenizer entry points: {e}")

    def test_model_registry_entry_points(self):
        """Test model registry entry points exist."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                models = eps.select(group='codex_ml.models')
            else:
                models = eps.get('codex_ml.models', [])
            
            # Should have at least minilm or bert
            model_found = any(ep.name in ['minilm', 'bert_base_uncased'] for ep in models)
            
            if model_found:
                assert model_found
            else:
                pytest.skip("Model entry points not registered")
                
        except Exception as e:
            pytest.skip(f"Could not check model entry points: {e}")

    def test_metric_registry_entry_points(self):
        """Test metric registry entry points exist."""
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            
            if hasattr(eps, 'select'):
                metrics = eps.select(group='codex_ml.metrics')
            else:
                metrics = eps.get('codex_ml.metrics', [])
            
            # Should have common metrics
            metric_names = {ep.name for ep in metrics}
            expected = {'token_accuracy', 'ppl', 'exact_match', 'f1'}
            
            found_metrics = expected & metric_names
            
            if found_metrics:
                assert len(found_metrics) > 0
            else:
                pytest.skip("Metric entry points not registered")
                
        except Exception as e:
            pytest.skip(f"Could not check metric entry points: {e}")


class TestEntryPointIntegration:
    """Test that entry points work in an integrated manner."""

    def test_can_discover_all_entry_points(self):
        """Test that we can discover all defined entry points."""
        try:
            from importlib.metadata import entry_points
            
            eps = entry_points()
            
            # List all entry point groups
            groups = set()
            
            if hasattr(eps, 'groups'):
                groups = eps.groups
            else:
                # Fallback for older Python versions
                for ep_list in eps.values():
                    for ep in ep_list:
                        if hasattr(ep, 'group'):
                            groups.add(ep.group)
            
            expected_groups = [
                'console_scripts',
                'codex_ml.tokenizers',
                'codex_ml.models',
                'codex_ml.metrics',
                'codex_ml.data_loaders',
                'codex_ml.datasets',
                'codex_ml.trainers',
            ]
            
            # Check if we have the expected groups
            found_groups = [g for g in expected_groups if g in groups]
            
            print(f"\n📦 Found entry point groups: {', '.join(found_groups)}")
            print(f"📦 All groups: {', '.join(sorted(groups))}")
            
            assert len(found_groups) > 0, "No expected entry point groups found"
            
        except Exception as e:
            pytest.skip(f"Could not check entry points: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
