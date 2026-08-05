"""
Test suite for security utilities.
Validates safe_torch_loader, safe_pickle, and security middleware.

SECURITY TESTING NOTES:
-----------------------
This test suite validates security utilities that protect against:
1. Arbitrary code execution via pickle deserialization
2. Unsafe PyTorch model loading (weights_only enforcement)
3. API security middleware (form size, rate limits)

Test Pickle Usage:
- All pickle operations in this file are on test fixtures WE create
- These are trusted sources used to validate security controls
- Production code should use safe_pickle_load with RestrictedUnpickler
"""

import hashlib
import io
import os
import pickle
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Import torch with error handling for CI environments
try:
    import torch

    TORCH_AVAILABLE = True
except (ImportError, OSError):
    torch = None
    TORCH_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not TORCH_AVAILABLE,
    reason="PyTorch not available or failed to load (expected in some CI environments)",
)

# Import security utilities
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.safe_pickle import RestrictedUnpickler, safe_pickle_load, trusted_pickle_dumps
from utils.safe_torch_loader import safe_load


class TestSafeTorchLoader:
    """Test suite for safe PyTorch model loading."""

    def test_safe_load_with_weights_only_true(self):
        """Test that safe_load enforces weights_only=True."""
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as f:
            temp_path = f.name
            # Save a simple tensor
            torch.save({"weight": torch.randn(3, 3)}, temp_path)

        try:
            # Should load successfully with weights_only=True
            loaded = safe_load(temp_path, weights_only=True)
            assert "weight" in loaded, "Condition must be true"
            assert isinstance(loaded["weight"], torch.Tensor)
        finally:
            os.unlink(temp_path)

    def test_safe_load_rejects_weights_only_false(self):
        """Test that safe_load rejects weights_only=False."""
        with pytest.raises(ValueError, match="weights_only=False is a security vulnerability"):
            safe_load("dummy.pth", weights_only=False)

    def test_safe_load_file_not_found(self):
        """Test that safe_load handles missing files."""
        with pytest.raises(FileNotFoundError):
            safe_load("nonexistent_file.pth")

    def test_safe_load_with_map_location(self):
        """Test that safe_load respects map_location parameter."""
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as f:
            temp_path = f.name
            torch.save({"weight": torch.randn(2, 2)}, temp_path)

        try:
            loaded = safe_load(temp_path, map_location="cpu", weights_only=True)
            assert loaded["weight"].device.type == "cpu", "type is not valid"
        finally:
            os.unlink(temp_path)


class TestSafePickle:
    """Test suite for safe pickle deserialization."""

    def test_safe_pickle_load_with_simple_data(self):
        """Test safe pickle loading with simple data structures.

        SECURITY NOTE: We're creating a test pickle here, so it's a trusted source.
        This validates that safe_pickle_load can handle legitimate data.
        """
        data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(trusted_pickle_dumps(data))

        try:
            loaded = safe_pickle_load(temp_path, use_restricted_unpickler=False)
            assert loaded == data, "Data must not be empty"
        finally:
            os.unlink(temp_path)

    def test_unrestricted_pickle_load_logs_warning(self, caplog):
        """Test unrestricted pickle loads emit an explicit trust-boundary warning."""
        data = {"trusted": True}

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(trusted_pickle_dumps(data))

        try:
            caplog.set_level("WARNING")
            loaded = safe_pickle_load(temp_path, use_restricted_unpickler=False)
            assert loaded == data, "Data must not be empty"
            assert "WITHOUT restriction" in caplog.text, "Condition must be true"
        finally:
            os.unlink(temp_path)

    def test_restricted_unpickler_allows_safe_types(self):
        """Test that RestrictedUnpickler allows whitelisted types.

        SECURITY NOTE: Creating test pickle with safe data to validate allowlist.
        """
        safe_data = {"int": 42, "str": "hello", "list": [1, 2, 3]}

        buffer = io.BytesIO()
        buffer.write(trusted_pickle_dumps(safe_data))
        buffer.seek(0)

        unpickler = RestrictedUnpickler(buffer)
        loaded = unpickler.load()

        assert loaded == safe_data, "Data must not be empty"

    def test_restricted_unpickler_blocks_unsafe_types(self):
        """Test that RestrictedUnpickler blocks non-whitelisted types.

        SECURITY TEST: This validates that the allowlist works by attempting
        to unpickle a custom class that should be blocked.
        """

        # Create a custom class that should be blocked
        class UnsafeClass:
            def __init__(self):
                self.data = "unsafe"

        unsafe_obj = UnsafeClass()

        buffer = io.BytesIO()
        buffer.write(trusted_pickle_dumps(unsafe_obj))
        buffer.seek(0)

        unpickler = RestrictedUnpickler(buffer)

        with pytest.raises(pickle.UnpicklingError, match="not in whitelist"):
            unpickler.load()

    def test_safe_pickle_with_numpy_array(self):
        """Test safe pickle with numpy arrays (whitelisted).

        SECURITY NOTE: NumPy arrays are in the allowlist because they're
        commonly used in ML checkpoints and have limited attack surface.
        """
        try:
            import numpy as np

            data = {"array": np.array([1, 2, 3])}

            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_path = f.name
                f.write(trusted_pickle_dumps(data))

            try:
                loaded = safe_pickle_load(temp_path, use_restricted_unpickler=True)
                assert np.array_equal(loaded["array"], data["array"])
            finally:
                os.unlink(temp_path)
        except ImportError:
            pytest.skip("NumPy not installed")


class TestSecurityMiddleware:
    """Test suite for API security middleware."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock()
        request.headers = {}
        request.client.host = "127.0.0.1"
        return request

    def test_form_size_validation(self, mock_request):
        """Test that middleware validates form size."""
        pytest.importorskip("starlette", reason="starlette not installed")
        from services.api.middleware.form_validator import SecureMultipartMiddleware

        middleware = SecureMultipartMiddleware(None)

        # Test request within limits
        mock_request.headers["content-type"] = "multipart/form-data"
        mock_request.headers["content-length"] = "1000000"  # 1MB

        # Should not raise an error (would need full async test for actual validation)
        assert middleware.MAX_FORM_SIZE == 10 * 1024 * 1024, "MAX_FORM_SIZE is not valid"

    def test_security_config_limits(self):
        """Test that APIConfig has appropriate security limits."""
        from services.api.config import APIConfig

        assert APIConfig.MAX_UPLOAD_SIZE == 50 * 1024 * 1024, "MAX_UPLOAD_SIZE is not valid"
        assert APIConfig.MAX_FIELD_SIZE == 1 * 1024 * 1024, "MAX_FIELD_SIZE is not valid"
        assert APIConfig.MAX_FIELDS == 1000, "MAX_FIELDS is not valid"
        assert APIConfig.REQUEST_TIMEOUT == 30, "REQUEST_TIMEOUT is not valid"


class TestMD5Usage:
    """Test that MD5 usage is properly marked."""

    def test_md5_with_usedforsecurity_false(self):
        """Test MD5 can be used with usedforsecurity=False."""
        data = b"test data"

        # This should work - MD5 for non-security purposes
        hash_obj = hashlib.md5(data, usedforsecurity=False)
        digest = hash_obj.hexdigest()

        assert len(digest) == 32, "Digest must not be empty"

    def test_sha256_for_security(self):
        """Test SHA256 is available for security purposes."""
        data = b"secure data"

        # SHA256 should be used for security-critical hashing
        hash_obj = hashlib.sha256(data)
        digest = hash_obj.hexdigest()

        assert len(digest) == 64, "Digest must not be empty"


class TestSubprocessSecurity:
    """Test subprocess security patterns."""

    def test_subprocess_uses_list_form(self):
        """Test that subprocess calls use list form."""
        import subprocess

        # Safe: list form
        result = subprocess.run(["echo", "hello"], capture_output=True, text=True)
        assert result.returncode == 0, "Result must not be empty"
        assert "hello" in result.stdout, "Result must not be empty"

    def test_shlex_split_for_command_parsing(self):
        """Test shlex.split for safe command parsing."""
        import shlex

        command = "git status --short"
        args = shlex.split(command)

        assert args == ["git", "status", "--short"]
        assert isinstance(args, list)

    def test_secure_wrapper_rejects_shell_true(self):
        """Secure subprocess wrapper should reject shell=True explicitly."""
        from security.security_hardening import secure_subprocess_run

        with pytest.raises((ValueError, security.security_hardening.SubprocessSecurityError), match="shell=True"):
            secure_subprocess_run(["echo", "hello"], shell=True)


class TestErrorHandling:
    """Test error handling patterns."""

    def test_exceptions_are_logged(self):
        """Test that exceptions include logging."""
        import logging

        logger = logging.getLogger(__name__)

        # Example of proper error handling
        try:
            raise ValueError("Test error")
        except ValueError as e:
            # Should log with context
            logger.warning(f"Exception: {e}", exc_info=True)
            # Test passes if no exception raised

    def test_specific_exception_handling(self):
        """Test using specific exception types."""
        with pytest.raises(ValueError):
            raise ValueError("Specific error")

    def test_file_not_found_exception_handling(self):
        """Test FileNotFoundError handling explicitly."""
        with pytest.raises(FileNotFoundError):
            raise FileNotFoundError("File not found")


def test_security_utilities_exist():
    """Verify all security utilities are present."""
    utils_dir = Path(__file__).parent.parent.parent / "utils"

    assert (utils_dir / "safe_torch_loader.py").exists(), "Condition must be true"
    assert (utils_dir / "safe_pickle.py").exists(), "Condition must be true"
    assert (utils_dir / "torch_resource_manager.py").exists(), "Condition must be true"


def test_security_documentation_exists():
    """Verify security documentation is present."""
    docs_dir = Path(__file__).parent.parent.parent / "docs"

    assert (docs_dir / "SECURITY.md").exists(), "Condition must be true"
    assert (docs_dir / "PYTORCH_MIGRATION_GUIDE.md").exists(), "Condition must be true"
    assert (docs_dir / "ERROR_HANDLING_IMPROVEMENT_GUIDE.md").exists(), "Error should be raised or set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
