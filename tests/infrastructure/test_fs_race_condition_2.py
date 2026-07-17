"""
Test filesystem race conditions - Pattern 2: Thread-safe atomic operations with GUIDs
Tests require robust file operations with unique resource naming and proper locking.
Fix: Replaced fcntl.flock() with threading.Lock() for cross-platform compatibility
"""
import tempfile
import threading
import time
import uuid
from pathlib import Path

import pytest


class TestFSRaceConditionLocking:
    """Test suite for filesystem race conditions with file locking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_temp = Path(tempfile.gettempdir())
        self.test_dirs = []
        self.results = []
        self.lock = threading.Lock()
        self.file_locks = {}  # File-specific locks for atomic operations

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
        """Create a GUID-based temp directory."""
        guid = str(uuid.uuid4())
        temp_dir = self.base_temp / f"test_{guid}"
        temp_dir.mkdir(parents=True, exist_ok=False)
        self.test_dirs.append(temp_dir)
        return temp_dir

    def get_file_lock(self, file_path):
        """Get or create a threading.Lock for a specific file."""
        if file_path not in self.file_locks:
            self.file_locks[file_path] = threading.Lock()
        return self.file_locks[file_path]

    @pytest.mark.timeout(10)
    def test_race_condition(self):
        """Test filesystem race condition with thread-safe operations."""
        
        # Shared resource with GUID naming
        work_dir = self.create_guid_temp_dir()
        counter_file = work_dir / "counter.txt"
        counter_file.write_text("0")
        
        file_lock = self.get_file_lock(str(counter_file))
        
        def worker(worker_id):
            """Worker that increments shared counter safely."""
            try:
                for _ in range(10):
                    # Use threading.Lock for atomic operations (cross-platform)
                    with file_lock:
                        # Read current value
                        current = int(counter_file.read_text().strip() or "0")
                        # Increment
                        new_value = current + 1
                        # Atomic write (write to temp file then rename)
                        temp_file = counter_file.parent / f"{counter_file.name}.tmp"
                        temp_file.write_text(str(new_value))
                        # Atomic rename
                        temp_file.replace(counter_file)
                    
                    time.sleep(0.001)  # Minimal delay to allow interleaving
                
                with self.lock:
                    self.results.append((worker_id, "success"))
                    
            except Exception as e:
                with self.lock:
                    self.results.append((worker_id, "failed", str(e)))

        # Run multiple workers
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            t.start()
            threads.append(t)

        # Wait for all threads
        for t in threads:
            t.join(timeout=10)

        # Verify results - all workers succeeded
        assert len(self.results) == 5, f"Expected 5 results, got {len(self.results)}"
        for result in self.results:
            assert result[1] == "success", f"Worker {result[0]} failed: {result}"

        # Verify final counter value (5 workers × 10 increments = 50)
        final_count = int(counter_file.read_text().strip())
        assert final_count == 50, f"Expected 50, got {final_count}"
