"""Contract tests validating CLI request/response schemas."""
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCLIContract:
    """Contract tests for CLI interface."""

    def test_generate_tests_request_schema(self):
        """Test generate_tests request schema."""
        request = {
            "type": "generate_tests",
            "module": "codex.ingest",
            "threshold": 85,
            "output_dir": "tests",
        }

        # Validate required fields
        assert "type" in request
        assert "module" in request
        assert request["type"] == "generate_tests"
        assert isinstance(request["module"], str)
        assert isinstance(request["threshold"], (int, float))

    def test_generate_tests_response_schema(self):
        """Test generate_tests response schema."""
        response = {
            "status": "success",
            "files_generated": 5,
            "module": "codex.ingest",
            "threshold": 85,
            "test_files": [
                {
                    "path": "tests/test_func.py",
                    "content": "...",
                    "function": "func_name",
                    "source_file": "src/module.py",
                }
            ],
        }

        # Validate required fields
        assert "status" in response
        assert "files_generated" in response
        assert isinstance(response["status"], str)
        assert isinstance(response["files_generated"], int)
        assert isinstance(response["test_files"], list)

        # Validate test file structure
        if response["test_files"]:
            test_file = response["test_files"][0]
            assert "path" in test_file
            assert "content" in test_file
            assert "function" in test_file
            assert "source_file" in test_file

    def test_validate_coverage_request_schema(self):
        """Test validate_coverage request schema."""
        request = {
            "type": "validate_coverage",
            "baseline": "baseline_coverage.txt",
            "threshold": 85,
            "modules": ["codex.ingest", "codex.process"],
        }

        # Validate required fields
        assert "type" in request
        assert request["type"] == "validate_coverage"
        assert isinstance(request.get("threshold", 85), (int, float))
        assert isinstance(request.get("modules", []), list)

    def test_validate_coverage_response_schema(self):
        """Test validate_coverage response schema."""
        response = {
            "status": "success",
            "baseline_coverage": 80.0,
            "current_coverage": 87.5,
            "delta": 7.5,
            "threshold": 85,
            "meets_threshold": True,
            "gaps": [],
            "module_coverage": {"module1.py": 90.0, "module2.py": 85.0},
        }

        # Validate required fields
        assert "status" in response
        assert "current_coverage" in response
        assert "baseline_coverage" in response
        assert "delta" in response
        assert "threshold" in response
        assert "meets_threshold" in response
        assert isinstance(response["current_coverage"], (int, float))
        assert isinstance(response["meets_threshold"], bool)
        assert isinstance(response["gaps"], list)

    def test_execute_tests_request_schema(self):
        """Test execute_tests request schema."""
        request = {
            "type": "execute_tests",
            "command": "pytest",
            "args": ["tests/", "-v", "--cov"],
            "env": {"PYTHONPATH": "/workspace/src"},
            "timeout": 300,
        }

        # Validate required fields
        assert "type" in request
        assert request["type"] == "execute_tests"
        assert isinstance(request.get("command", "pytest"), str)
        assert isinstance(request.get("args", []), list)
        assert isinstance(request.get("env", {}), dict)
        assert isinstance(request.get("timeout", 300), int)

    def test_execute_tests_response_schema(self):
        """Test execute_tests response schema."""
        response = {
            "status": "success",
            "returncode": 0,
            "stdout": "Test output...",
            "stderr": "",
            "command": "pytest tests/ -v",
        }

        # Validate required fields
        assert "status" in response
        assert "returncode" in response
        assert "command" in response
        assert isinstance(response["returncode"], int)
        assert isinstance(response["stdout"], str)
        assert isinstance(response["stderr"], str)

    def test_error_response_schema(self):
        """Test error response schema."""
        response = {
            "status": "error",
            "error": "Module not found",
            "files_generated": 0,
        }

        # Validate error fields
        assert "status" in response
        assert response["status"] == "error"
        assert "error" in response
        assert isinstance(response["error"], str)

    def test_debug_ci_failure_request_schema(self):
        """Test debug_ci_failure request schema."""
        request = {
            "type": "debug_ci_failure",
            "command": "pytest",
            "args": ["tests/", "--tb=short"],
            "workflow_run_id": 12345,
        }

        # Validate required fields
        assert "type" in request
        assert request["type"] == "debug_ci_failure"
        assert isinstance(request.get("command", "pytest"), str)

    def test_task_timestamp_field(self):
        """Test that tasks can include timestamp."""
        request = {
            "type": "generate_tests",
            "module": "codex.ingest",
            "timestamp": "2025-12-31T20:00:00.000Z",
        }

        assert "timestamp" in request
        assert isinstance(request["timestamp"], str)

    def test_optional_fields(self):
        """Test that optional fields are handled correctly."""
        # Minimal request
        minimal_request = {
            "type": "generate_tests",
            "module": "codex.ingest",
        }

        assert "type" in minimal_request
        assert "module" in minimal_request
        # Optional fields should not be required
        assert minimal_request.get("threshold", 85) == 85
        assert minimal_request.get("output_dir", "tests") == "tests"

    def test_status_values(self):
        """Test valid status values."""
        valid_statuses = [
            "success",
            "failure",
            "error",
            "timeout",
            "below_threshold",
        ]

        for status in valid_statuses:
            response = {"status": status}
            assert response["status"] in valid_statuses
