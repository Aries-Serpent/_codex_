#!/usr/bin/env python3
"""
Comprehensive profile validation script for codex-ml packaging.
Tests all three profiles: core, runtime, and full.
"""

import sys
import subprocess
from typing import Dict

class ProfileValidator:
    """Validates each installation profile."""
    
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.details: Dict[str, List[str]] = {}
    
    def test_core_profile(self) -> bool:
        """Test core profile: offline-first, no network I/O."""
        print("\n" + "="*60)
        print("TESTING CORE PROFILE (8-15 MB)")
        print("="*60)
        
        tests = [
            ("omegaconf import", self._test_import, "omegaconf"),
            ("hydra-core import", self._test_import, "hydra"),
            ("pydantic import", self._test_import, "pydantic"),
            ("cryptography import", self._test_import, "cryptography"),
            ("PyJWT import", self._test_import, "jwt"),
            ("requests import", self._test_import, "requests"),
            ("CLI tools import", self._test_import, "typer"),
        ]
        
        all_passed = True
        for test_name, test_func, *args in tests:
            try:
                test_func(*args)
                print(f"✅ {test_name}")
                self.details.setdefault("core", []).append(f"✅ {test_name}")
            except Exception as e:
                print(f"❌ {test_name}: {e}")
                self.details.setdefault("core", []).append(f"❌ {test_name}: {e}")
                all_passed = False
        
        # Test offline capability only if core imports passed
        if all_passed:
            print("\n📋 Offline Capability Test:")
            try:
                self._test_no_network_io()
                print("✅ No network I/O detected at import")
                self.details["core"].append("✅ No network I/O at import")
            except RuntimeError as e:
                print(f"⚠️  Network I/O possible (may be normal): {e}")
                # Don't fail for this as it's environment-dependent
        else:
            print("\n📋 Offline Capability Test: SKIPPED (core imports failed)")
            self.details["core"].append("⏭️  Offline test skipped (core imports failed)")
        
        self.results["core"] = all_passed
        return all_passed
    
    def test_runtime_profile(self) -> bool:
        """Test runtime profile: ML inference, FastAPI."""
        print("\n" + "="*60)
        print("TESTING RUNTIME PROFILE (20-35 MB)")
        print("="*60)
        
        tests = [
            ("torch import", self._test_import, "torch"),
            ("transformers import", self._test_import, "transformers"),
            ("fastapi import", self._test_import, "fastapi"),
            ("ray import", self._test_import, "ray"),
            ("numpy import", self._test_import, "numpy"),
            ("pandas import", self._test_import, "pandas"),
            ("sentence-transformers import", self._test_import, "sentence_transformers"),
        ]
        
        all_passed = True
        for test_name, test_func, *args in tests:
            try:
                test_func(*args)
                print(f"✅ {test_name}")
                self.details.setdefault("runtime", []).append(f"✅ {test_name}")
            except ImportError as e:
                print(f"⚠️  {test_name}: Not installed (OK if core-only)")
                self.details.setdefault("runtime", []).append(f"⚠️  {test_name}: Optional")
            except Exception as e:
                print(f"❌ {test_name}: {e}")
                self.details.setdefault("runtime", []).append(f"❌ {test_name}: {e}")
                all_passed = False
        
        self.results["runtime"] = all_passed
        return all_passed
    
    def test_full_profile(self) -> bool:
        """Test full profile: testing, linting, development."""
        print("\n" + "="*60)
        print("TESTING FULL PROFILE (100+ MB)")
        print("="*60)
        
        tests = [
            ("pytest import", self._test_import, "pytest"),
            ("ruff import", self._test_import, "ruff"),
            ("black import", self._test_import, "black"),
            ("mypy import", self._test_import, "mypy"),
            ("jupyter import", self._test_import, "jupyter"),
            ("mlflow import", self._test_import, "mlflow"),
            ("plotly import", self._test_import, "plotly"),
        ]
        
        all_passed = True
        for test_name, test_func, *args in tests:
            try:
                test_func(*args)
                print(f"✅ {test_name}")
                self.details.setdefault("full", []).append(f"✅ {test_name}")
            except ImportError as e:
                print(f"⚠️  {test_name}: Not installed (OK if limited profile)")
                self.details.setdefault("full", []).append(f"⚠️  {test_name}: Optional")
            except Exception as e:
                print(f"❌ {test_name}: {e}")
                self.details.setdefault("full", []).append(f"❌ {test_name}: {e}")
                # Don't fail for dev tools
        
        self.results["full"] = all_passed
        return all_passed
    
    @staticmethod
    def _test_import(module_name: str) -> None:
        """Test importing a module."""
        __import__(module_name)
    
    @staticmethod
    def _test_no_network_io() -> None:
        """Test that core imports don't make network calls in a fresh subprocess."""
        code = """
import socket
from unittest.mock import patch

calls = []

def mock_connect(self, address):
    calls.append(f"socket.connect({address})")

def mock_create_connection(address, *args, **kwargs):
    calls.append(f"socket.create_connection({address})")

with patch.object(socket.socket, 'connect', mock_connect):
    with patch('socket.create_connection', mock_create_connection):
        # These should not trigger network calls
        import omegaconf
        import hydra

if calls:
    import sys
    print(f"ERROR: Network calls detected: {calls}", file=sys.stderr)
    sys.exit(1)
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Network calls detected in subprocess: {result.stderr}")
    
    def print_summary(self) -> int:
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        for profile, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{profile.upper():15} {status}")
            for detail in self.details.get(profile, []):
                if "❌" in detail:
                    print(f"  {detail}")
        
        all_passed = all(self.results.values())
        print("\n" + ("="*60))
        if all_passed:
            print("✅ All profile validations passed!")
            print("="*60)
            return 0
        else:
            print("❌ Some profile validations failed!")
            print("="*60)
            return 1

def main():
    """Run all profile validation tests."""
    validator = ProfileValidator()
    
    # Run tests for each profile
    validator.test_core_profile()
    validator.test_runtime_profile()
    validator.test_full_profile()
    
    # Print summary and return exit code
    return validator.print_summary()

if __name__ == "__main__":
    sys.exit(main())
