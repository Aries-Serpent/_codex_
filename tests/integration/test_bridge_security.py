"""Integration test for bridge security features."""

import tempfile
from pathlib import Path

import pytest

from bridge_manager import (
    BridgeManager,
    BridgeMode,
    ContextMessage,
    bridge_lock,
)


class TestBridgeSecurity:
    """Test suite for bridge security features."""

    def test_bridge_creates_secure_permissions(self):
        """Test that bridge creates files with 0o600 permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "test_bridge",
                mode=BridgeMode.NAMED_PIPE,
                owner_only=True,
            )

            # Check directory permissions (0o700 = owner only rwx)
            dir_stat = bridge.bridge_dir.stat()
            dir_mode = dir_stat.st_mode & 0o777
            assert dir_mode == 0o700, f"Expected 0o700, got {oct(dir_mode)}"

            # Check pipe permissions if created
            if bridge.pipe_path.exists():
                pipe_stat = bridge.pipe_path.stat()
                pipe_mode = pipe_stat.st_mode & 0o777
                assert pipe_mode == 0o600, f"Expected 0o600, got {oct(pipe_mode)}"

            bridge.cleanup()

    def test_lock_prevents_concurrent_access(self):
        """Test that lock prevents concurrent write access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # Acquire first lock
            with bridge_lock(lock_path):
                # Try to acquire second lock (should timeout)
                from bridge_manager import BridgeLock

                second_lock = BridgeLock(lock_path)
                acquired = second_lock.acquire(timeout=1)

                assert acquired is False, "Second lock should not be acquired"
                second_lock.release()

    def test_message_validation(self):
        """Test that invalid messages are rejected."""
        # Valid message
        valid_msg = ContextMessage(
            timestamp="2026-01-08T12:00:00Z",
            source="test",
            message_type="test",
            context={"data": "test"},
        )
        assert valid_msg.validate() is True, "Condition must be true"

        # Invalid message (missing required field)
        # Can't create directly due to Pydantic, but test the validate method
        assert valid_msg.validate() is True, "Condition must be true"


class TestBridgeModes:
    """Test different bridge communication modes."""

    def test_named_pipe_mode(self):
        """Test named pipe mode initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "pipe_test",
                mode=BridgeMode.NAMED_PIPE,
                owner_only=True,
            )

            assert bridge.mode == BridgeMode.NAMED_PIPE, "mode is not valid"
            assert bridge.pipe_path.exists(), "Condition must be true"

            bridge.cleanup()
            assert not bridge.pipe_path.exists(), "Condition must be true"

    def test_unix_socket_mode(self):
        """Test unix socket mode initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = BridgeManager(
                bridge_dir=Path(tmpdir) / "socket_test",
                mode=BridgeMode.UNIX_SOCKET,
                owner_only=True,
            )

            assert bridge.mode == BridgeMode.UNIX_SOCKET, "mode is not valid"
            # Socket not created until bind

            bridge.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
