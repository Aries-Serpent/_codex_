"""
Test filesystem race conditions - Pattern 1: GUID-based temp directories
Tests require atomic file operations with unique naming using GUIDs.
"""
import tempfile
import threading
import time
import pytest
import os
import uuid
from pathlib import Path


class TestFSRaceCondition:
    """Test suite for filesystem race conditions with GUID temp dirs."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_temp = Path(tempfile.gettempdir())
        self.test_dirs = []
        self.results = []
        self.lock = threading.Lock()

    def teardown_method(self):
        """Clean up after tests."""
        import shutil
        for test_dir in self.test_dirs:
            if test_dir.exists():
                try:
                    shutil.rmtree(test_dir)
                except:
                    pass

    def create_guid_temp_dir(self):
        """Create a GUID-based temp directory to avoid race conditions."""
        guid = str(uuid.uuid4())
        temp_dir = self.base_temp / f"test_{guid}"
        temp_dir.mkdir(parents=True, exist_ok=False)  # Fail if exists
        self.test_dirs.append(temp_dir)
        return temp_dir

    @pytest.mark.timeout(10)
    def test_race_condition(self):
        """Test filesystem race condition with multiple threads."""
        
        def worker(worker_id):
            """Worker that creates and manipulates files."""
            try:
                # Each worker gets a unique GUID-based dir
                work_dir = self.create_guid_temp_dir()
                
                # Create files with barrier
                for i in range(5):
                    file_path = work_dir / f"file_{i}.txt"
                    # Atomic write
                    file_path.write_text(f"worker_{worker_id}_file_{i}")
                    time.sleep(0.01)  # Small delay
                
                # Verify all files exist
                files = list(work_dir.glob("file_*.txt"))
                assert len(files) == 5
                
                with self.lock:
                    self.results.append((worker_id, "success", len(files)))
                    
            except Exception as e:
                with self.lock:
                    self.results.append((worker_id, "failed", str(e)))

        # Run multiple workers
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            t.start()
            threads.append(t)

        # Wait for all threads
        for t in threads:
            t.join(timeout=10)

        # Verify results
        assert len(self.results) == 3
        for worker_id, status, data in self.results:
            assert status == "success", f"Worker {worker_id} failed: {data}"
            assert data == 5  # All files created

        # Verify no directory conflicts (each had unique GUID)
        assert len(self.test_dirs) == 3
