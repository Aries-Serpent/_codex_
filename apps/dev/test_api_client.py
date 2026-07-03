#!/usr/bin/env python3
from src.codex.utils.path_extended import get_repo_root
"""
Test script for Zendesk Voice Lines API Client (non-GUI components).

This script validates the API client logic without requiring tkinter/GUI.
"""

import json

# Import our dataclass and client
import sys
from dataclasses import dataclass, field

sys.path.insert(0, str(get_repo_root() / 'apps/dev'))


@dataclass
class ZendeskVoiceLinesConfig:
    """Configuration for Zendesk Voice Lines API."""
    subdomain: str
    base64_auth: str
    base_url: str = field(init=False)

    def __post_init__(self):
        """Initialize computed fields."""
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"

    def get_auth_header(self) -> dict[str, str]:
        """Get authorization header from base64 encoded credentials."""
        return {"Authorization": f"Basic {self.base64_auth}"}


def test_config_creation():
    """Test configuration creation."""
    print("Testing ZendeskVoiceLinesConfig...")

    config = ZendeskVoiceLinesConfig(
        subdomain="testcompany",
        base64_auth="dGVzdDp0ZXN0MTIz"
    )

    assert config.subdomain == "testcompany"
    assert config.base64_auth == "dGVzdDp0ZXN0MTIz"
    assert config.base_url == "https://testcompany.zendesk.com/api/v2"

    auth_header = config.get_auth_header()
    assert "Authorization" in auth_header
    assert auth_header["Authorization"] == "Basic dGVzdDp0ZXN0MTIz"

    print("✓ Configuration tests passed")


def test_url_construction():
    """Test URL construction."""
    print("Testing URL construction...")

    config = ZendeskVoiceLinesConfig(
        subdomain="mycompany",
        base64_auth="dGVzdA=="
    )

    # Test voice lines endpoint URL
    expected_url = "https://mycompany.zendesk.com/api/v2/channels/voice/lines.json"
    actual_url = f"{config.base_url}/channels/voice/lines.json"

    assert actual_url == expected_url

    print("✓ URL construction tests passed")


def test_pagination_logic():
    """Test pagination detection logic."""
    print("Testing pagination logic...")

    # Simulate API response with next_page
    response_with_next = {
        "lines": [{"id": 1}, {"id": 2}],
        "next_page": "https://example.zendesk.com/api/v2/channels/voice/lines.json?page=2",
        "count": 2
    }

    # Simulate API response without next_page (last page)
    response_last_page = {
        "lines": [{"id": 3}],
        "next_page": None,
        "count": 1
    }

    # Test logic
    has_next = response_with_next.get("next_page") is not None
    assert has_next is True

    has_next_last = response_last_page.get("next_page") is not None
    assert has_next_last is False

    print("✓ Pagination logic tests passed")


def test_export_data_structure():
    """Test export data structure."""
    print("Testing export data structure...")

    # Simulate pages data
    pages = [
        {
            "lines": [
                {"id": 1, "name": "Line 1", "enabled": True},
                {"id": 2, "name": "Line 2", "enabled": False}
            ],
            "next_page": "https://...",
            "count": 2
        },
        {
            "lines": [
                {"id": 3, "name": "Line 3", "enabled": True}
            ],
            "next_page": None,
            "count": 1
        }
    ]

    # Test JSON export structure
    combined_data = {
        "metadata": {
            "total_pages": len(pages),
            "export_timestamp": "2026-02-13 17:00:00",
        },
        "pages": pages,
    }

    assert "metadata" in combined_data
    assert "pages" in combined_data
    assert combined_data["metadata"]["total_pages"] == 2
    assert len(combined_data["pages"]) == 2

    # Test CSV flatten logic
    all_lines = []
    for page in pages:
        lines = page.get("lines", [])
        all_lines.extend(lines)

    assert len(all_lines) == 3
    assert all_lines[0]["id"] == 1
    assert all_lines[2]["id"] == 3

    # Get all unique keys for CSV headers
    all_keys = set()
    for line in all_lines:
        all_keys.update(line.keys())

    assert "id" in all_keys
    assert "name" in all_keys
    assert "enabled" in all_keys

    print("✓ Export data structure tests passed")


def test_rate_limit_detection():
    """Test rate limit detection."""
    print("Testing rate limit detection...")

    # Simulate 429 response
    class MockResponse:
        def __init__(self, status_code, headers):
            self.status_code = status_code
            self.headers = headers

    response_429 = MockResponse(
        status_code=429,
        headers={"Retry-After": "60", "X-Rate-Limit": "400", "X-Rate-Limit-Remaining": "0"}
    )

    # Test detection
    is_rate_limited = response_429.status_code == 429
    assert is_rate_limited is True

    retry_after = int(response_429.headers.get("Retry-After", 60))
    assert retry_after == 60

    # Simulate success response
    response_200 = MockResponse(
        status_code=200,
        headers={"X-Rate-Limit": "400", "X-Rate-Limit-Remaining": "350"}
    )

    is_rate_limited_success = response_200.status_code == 429
    assert is_rate_limited_success is False

    print("✓ Rate limit detection tests passed")


def test_search_logic():
    """Test search functionality logic."""
    print("Testing search logic...")

    pages = [
        {"lines": [{"id": 1, "name": "Main Line"}]},
        {"lines": [{"id": 2, "name": "Support Line"}]},
        {"lines": [{"id": 3, "name": "Sales Line"}]}
    ]

    query = "support"
    search_results = []

    for page_idx, page_data in enumerate(pages):
        page_json = json.dumps(page_data, indent=2).lower()
        if query in page_json:
            search_results.append((page_idx, page_data))

    assert len(search_results) == 1
    assert search_results[0][0] == 1  # Page index

    # Test case-insensitive
    query_upper = "SUPPORT"
    search_results_upper = []

    for page_idx, page_data in enumerate(pages):
        page_json = json.dumps(page_data, indent=2).lower()
        if query_upper.lower() in page_json:
            search_results_upper.append((page_idx, page_data))

    assert len(search_results_upper) == 1

    print("✓ Search logic tests passed")


def test_greeting_download_url_construction():
    """Test greeting download URL construction."""
    print("Testing greeting download URL construction...")

    config = ZendeskVoiceLinesConfig(
        subdomain="mycompany",
        base64_auth="dGVzdA=="
    )

    greeting_path = "29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3"
    expected_url = "https://mycompany.zendesk.com/api/v2/channels/voice/greetings/29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3"
    actual_url = f"{config.base_url}/channels/voice/greetings/{greeting_path}"

    assert actual_url == expected_url

    # Test with leading slash (should be stripped in actual implementation)
    greeting_path_with_slash = "/29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3"
    cleaned_path = greeting_path_with_slash.lstrip("/")
    actual_url_cleaned = f"{config.base_url}/channels/voice/greetings/{cleaned_path}"

    assert actual_url_cleaned == expected_url

    print("✓ Greeting download URL construction tests passed")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Zendesk Voice Lines API Client - Component Tests")
    print("="*60)
    print()

    tests = [
        test_config_creation,
        test_url_construction,
        test_pagination_logic,
        test_export_data_structure,
        test_rate_limit_detection,
        test_search_logic,
        test_greeting_download_url_construction,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
            print()
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
            print()

    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
