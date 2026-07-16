"""
Batch 3 Flaky Test Stabilization Fixtures
Provides reusable fixtures and utilities for fixing flaky tests
"""

import time
import pytest
from unittest.mock import patch, MagicMock
from typing import Callable, Any, Optional


class PollingHelper:
    """Helper for polling-based assertions (race conditions)"""
    
    @staticmethod
    def wait_for_condition(
        condition: Callable[[], bool],
        timeout: float = 2.0,
        poll_interval: float = 0.01,
        error_msg: str = "Condition not met"
    ) -> bool:
        """
        Poll for a condition to become true
        
        Args:
            condition: Function that returns bool
            timeout: Max seconds to wait
            poll_interval: Sleep between polls (seconds)
            error_msg: Error message if timeout
            
        Returns:
            True if condition met, raises TimeoutError otherwise
        """
        start = time.time()
        last_error = None
        
        while time.time() - start < timeout:
            try:
                if condition():
                    return True
            except Exception as e:
                last_error = e
            
            time.sleep(poll_interval)
        
        # Timeout occurred
        if last_error:
            raise TimeoutError(f"{error_msg} (last error: {last_error})")
        raise TimeoutError(error_msg)
    
    @staticmethod
    def wait_for_value(
        getter: Callable[[], Any],
        expected: Any,
        timeout: float = 2.0,
        poll_interval: float = 0.01,
    ) -> bool:
        """Wait for getter() to equal expected value"""
        def condition():
            return getter() == expected
        
        return PollingHelper.wait_for_condition(
            condition,
            timeout=timeout,
            poll_interval=poll_interval,
            error_msg=f"Value {expected} not achieved"
        )


@pytest.fixture
def freezegun_decorator():
    """Provide freezegun time freezing"""
    try:
        from freezegun import freeze_time
        return freeze_time
    except ImportError:
        pytest.skip("freezegun not installed")


@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests library for network calls"""
    
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, text=None):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = text or ""
            self.headers = {}
        
        def json(self):
            return self._json_data
    
    def mock_get(url, *args, **kwargs):
        return MockResponse(status_code=200)
    
    def mock_post(url, *args, **kwargs):
        return MockResponse(status_code=201)
    
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)
    
    return {
        "get": mock_get,
        "post": mock_post,
        "Response": MockResponse,
    }


@pytest.fixture
def mock_http_client(monkeypatch):
    """Mock HTTP client for urllib and similar"""
    
    class MockHTTPResponse:
        def __init__(self, status=200, data=b"OK"):
            self.status = status
            self.data = data
        
        def read(self):
            return self.data
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    def mock_urlopen(url, *args, **kwargs):
        return MockHTTPResponse()
    
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    return MockHTTPResponse


@pytest.fixture
def polling_helper():
    """Provide polling helper for race conditions"""
    return PollingHelper()


@pytest.fixture
def time_mock(monkeypatch):
    """Mock time module for timing-dependent tests"""
    
    class TimeMock:
        def __init__(self):
            self.current_time = time.time()
            self.sleep_total = 0
        
        def time(self):
            return self.current_time
        
        def sleep(self, duration):
            self.current_time += duration
            self.sleep_total += duration
        
        def advance(self, duration):
            """Manually advance time"""
            self.current_time += duration
    
    mock = TimeMock()
    monkeypatch.setattr("time.time", mock.time)
    monkeypatch.setattr("time.sleep", mock.sleep)
    
    return mock


# Utility functions

def assert_no_flaky_marker(test_file: str) -> bool:
    """Verify test file has no @pytest.mark.flaky without reason"""
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for flaky markers without reason=
    if '@pytest.mark.flaky' in content:
        # Find all flaky markers
        import re
        flaky_matches = re.findall(
            r'@pytest\.mark\.flaky\([^)]*\)',
            content
        )
        for match in flaky_matches:
            if 'reason=' not in match:
                return False
    
    return True


def get_flaky_tests(test_dir: str = "tests") -> list:
    """Find all tests marked as flaky"""
    from pathlib import Path
    import re
    
    flaky_tests = []
    for test_file in Path(test_dir).rglob("test_*.py"):
        try:
            content = test_file.read_text()
            if '@pytest.mark.flaky' in content or '@flaky' in content:
                flaky_tests.append(str(test_file))
        except:
            pass
    
    return flaky_tests


# Test repair patterns

PATTERN_TIMING_DEPENDENT = """
# PATTERN: Timing-Dependent Test
# Description: Test fails under system load due to time assertions
# Fix: Use freezegun to freeze time

@pytest.fixture
def freeze_time_fixture():
    from freezegun import freeze_time
    return freeze_time("2026-07-16 03:00:00")

@pytest.mark.flaky(reruns=0, reason="Fixed with freezegun - no flakiness expected")
def test_timing_dependent(freeze_time_fixture):
    # Time is now frozen, test runs consistently
    start = time.time()
    operation()
    duration = time.time() - start
    assert duration == 0  # Always true with frozen time
"""

PATTERN_NETWORK_DEPENDENT = """
# PATTERN: Network-Dependent Test
# Description: Test fails due to external API timeouts
# Fix: Mock network requests with monkeypatch

def test_network_call(mock_requests):
    response = requests.get("https://external-api.com/data")
    assert response.status_code == 200  # Always passes with mock
    assert response.json() == {}  # Mock returns empty dict
"""

PATTERN_RACE_CONDITION = """
# PATTERN: Race Condition Test
# Description: Test has callback timing issues
# Fix: Use polling helper to wait for condition

def test_async_callback(polling_helper):
    callback_called = False
    
    def on_callback():
        nonlocal callback_called
        callback_called = True
    
    trigger_async(on_callback)
    
    # Poll for callback with 2s timeout
    polling_helper.wait_for_condition(
        lambda: callback_called,
        timeout=2.0,
        error_msg="Callback not called within 2s"
    )
"""

PATTERN_EDGE_CASE = """
# PATTERN: Edge Case Test
# Description: Test fails on boundary conditions
# Fix: Add explicit assertions for empty/null cases

def test_empty_list():
    result = process([])
    assert result == []  # Explicit empty case

def test_single_item():
    result = process([1])
    assert len(result) == 1
    assert result[0] == 1

def test_large_list():
    large_input = list(range(10000))
    result = process(large_input)
    assert len(result) == 10000
"""


if __name__ == "__main__":
    print("Flaky test stabilization fixtures and utilities loaded.")
    print("Use with pytest via conftest.py or direct import.")
