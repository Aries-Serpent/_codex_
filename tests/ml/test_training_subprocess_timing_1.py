"""
Test subprocess timing - Pattern 1: Barrier Synchronization
Tests require robust subprocess timing synchronization using threading.Barrier
"""
import subprocess
import threading
import time
import pytest
from pathlib import Path
import tempfile


class TestSubprocessTimingBarrier:
    """Test suite for subprocess timing with barrier synchronization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.barrier = threading.Barrier(2)
        self.temp_dir = tempfile.mkdtemp()
        self.results = []

    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.timeout(10)
    def test_subprocess_timing(self):
        """Test subprocess timing with barrier synchronization."""
        # Without barrier, this test can be flaky due to timing issues
        # between subprocess startup and signal delivery
        
        def subprocess_worker():
            """Worker that runs in subprocess."""
            import sys
            sys.stdout.write("ready\n")
            sys.stdout.flush()
            time.sleep(0.5)  # Simulate work
            sys.stdout.write("done\n")
            sys.stdout.flush()

        def main_worker():
            """Main thread worker."""
            time.sleep(0.1)  # Give subprocess time to start

        # Use barrier to synchronize
        def run_subprocess():
            self.barrier.wait(timeout=5)
            proc = subprocess.Popen(
                ["python", "-c", "import time; print('ready'); time.sleep(0.5); print('done')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.results.append(proc)
            return proc

        def run_main():
            self.barrier.wait(timeout=5)
            time.sleep(0.1)

        # Run synchronized
        t1 = threading.Thread(target=run_subprocess)
        t2 = threading.Thread(target=run_main)
        
        t1.start()
        t2.start()
        
        t1.join(timeout=10)
        t2.join(timeout=10)

        assert len(self.results) > 0
        proc = self.results[0]
        stdout, stderr = proc.communicate(timeout=5)
        
        assert "ready" in stdout
        assert "done" in stdout
        assert proc.returncode == 0
