"""
Test subprocess timing - Pattern 3: Event-based Synchronization
Tests require event-based synchronization for subprocess lifecycle.
"""
import subprocess
import threading
import time
import pytest
from pathlib import Path
import tempfile


class TestSubprocessTimingEvent:
    """Test suite for subprocess timing with event synchronization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.start_event = threading.Event()
        self.ready_event = threading.Event()
        self.temp_dir = tempfile.mkdtemp()
        self.proc = None
        self.output = []

    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except:
                self.proc.kill()
        
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.timeout(10)
    def test_subprocess_timing(self):
        """Test subprocess timing with event-based synchronization."""
        
        def run_process():
            """Run subprocess with event signaling."""
            self.start_event.wait(timeout=5)  # Wait for signal to start
            
            script = """
import sys
print('READY', flush=True)
sys.stdout.flush()
import time
time.sleep(0.2)
print('DONE', flush=True)
"""
            self.proc = subprocess.Popen(
                ["python", "-c", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Read output
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    break
                self.output.append(line.strip())
                if "READY" in line:
                    self.ready_event.set()
            
            self.proc.wait(timeout=5)

        # Start process thread
        t = threading.Thread(target=run_process)
        t.start()
        
        # Signal to start
        time.sleep(0.05)
        self.start_event.set()
        
        # Wait for ready signal
        assert self.ready_event.wait(timeout=5)
        
        # Wait for completion
        t.join(timeout=10)
        
        assert "READY" in self.output
        assert "DONE" in self.output
        assert self.proc.returncode == 0
