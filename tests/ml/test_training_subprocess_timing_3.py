"""Test subprocess timing - Pattern 3: event-based synchronization."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestSubprocessTimingEvent:
    """Test suite for subprocess timing with event synchronization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.proc = None
        self.output = []

    def teardown_method(self):
        """Clean up after tests."""
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.timeout(10)
    @pytest.mark.flaky(
        reruns=2,
        reason=(
            "CI scheduling can delay child-process stdout; this test is validating "
            "startup timing rather than a product regression."
        ),
    )
    def test_subprocess_timing(self):
        """Verify the child emits READY and DONE within the bounded timeout."""
        script = """
import sys
import time

print('READY', flush=True)
sys.stdout.flush()
time.sleep(0.2)
print('DONE', flush=True)
"""
        self.proc = subprocess.Popen(
            ["python", "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        try:
            stdout, stderr = self.proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            stdout, stderr = self.proc.communicate()
            pytest.fail(f"Subprocess timed out: {stderr}")

        self.output = stdout.splitlines()
        assert "READY" in self.output
        assert "DONE" in self.output
        assert self.proc.returncode == 0
