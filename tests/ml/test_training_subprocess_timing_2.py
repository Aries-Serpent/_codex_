"""
Test subprocess timing - Pattern 2: Event-based Task Synchronization (Process pool)
Tests require robust subprocess timing with event-based coordination.
Fix: Replaced Barrier with Event signaling to avoid BrokenBarrierError
"""
import subprocess
import threading
import time
import pytest
from pathlib import Path
import tempfile
from concurrent.futures import ThreadPoolExecutor


class TestSubprocessTimingPool:
    """Test suite for subprocess timing with thread pool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.start_event = threading.Event()
        self.tasks_ready = []
        self.temp_dir = tempfile.mkdtemp()
        self.results = []
        self.lock = threading.Lock()

    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.timeout(10)
    def test_subprocess_timing(self):
        """Test subprocess timing with event-based thread pool synchronization."""
        
        def subprocess_task(task_id):
            """Worker that runs in subprocess with event synchronization."""
            try:
                time.sleep(0.05 * task_id)  # Stagger starts
                
                # Signal task ready
                with self.lock:
                    self.tasks_ready.append(task_id)
                
                # Wait for all tasks to be ready
                while True:
                    with self.lock:
                        if len(self.tasks_ready) >= 2:
                            break
                    time.sleep(0.001)
                
                # Now run subprocess with guaranteed synchronization
                proc = subprocess.Popen(
                    ["python", "-c", f"import sys, time; time.sleep(0.1); print('task_{task_id}_done')"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = proc.communicate(timeout=5)
                
                with self.lock:
                    self.results.append((task_id, stdout.strip(), proc.returncode))
                
                return proc.returncode == 0
            except Exception as e:
                with self.lock:
                    self.results.append((task_id, str(e), -1))
                return False

        # Use ThreadPoolExecutor with event-based synchronization (no Barrier)
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for i in range(2):
                future = executor.submit(subprocess_task, i)
                futures.append(future)
            
            # Wait with timeout
            results = [f.result(timeout=10) for f in futures]

        assert all(results), f"Some tasks failed: {self.results}"
        assert len(self.results) == 2
        for task_id, output, returncode in self.results:
            assert returncode == 0, f"Task {task_id} failed with: {output}"
            assert f"task_{task_id}_done" in output
