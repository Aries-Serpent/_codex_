"""Security-focused tests for scripts/zendesk_docs_fetch.py URL validation."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from zendesk_docs_fetch import _fetch


class TestURLValidation:
    """Test suite for _fetch URL security validation."""

    @pytest.mark.parametrize(
        "url,description",
        [
            ("file:///etc/passwd", "file scheme lowercase"),
            ("FILE:///etc/passwd", "file scheme uppercase"),
            ("File:///etc/passwd", "file scheme mixed case"),
            ("http://example.com/page", "http scheme"),
            ("ftp://ftp.example.com/file", "ftp scheme"),
            ("data:text/plain,Hello", "data scheme"),
            ("javascript:alert(1)", "javascript scheme"),
        ],
    )
    def test_reject_non_https_schemes(self, url: str, description: str) -> None:
        """Reject any non-HTTPS URL schemes."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch(url)

    def test_reject_missing_hostname(self) -> None:
        """Reject URLs without valid hostname."""
        with pytest.raises(ValueError, match="must have a valid hostname"):
            _fetch("https://")

    def test_reject_empty_url(self) -> None:
        """Reject empty URLs."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("")

    @patch("urllib.request.urlopen")
    def test_accept_valid_https(self, mock_urlopen: Mock) -> None:
        """Accept valid HTTPS URLs."""
        mock_response = Mock()
        mock_response.read.return_value = b"test content"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = _fetch("https://developer.zendesk.com/api-reference/")
        assert result == b"test content", "Result must not be empty"
        mock_urlopen.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_accept_https_case_insensitive(self, mock_urlopen: Mock) -> None:
        """Accept HTTPS URLs with mixed case schemes (RFC 3986 compliance)."""
        mock_response = Mock()
        mock_response.read.return_value = b"test content"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        # RFC 3986: schemes are case-insensitive
        result = _fetch("HTTPS://example.com/page")
        assert result == b"test content", "Result must not be empty"

    @patch("urllib.request.urlopen")
    def test_retry_on_failure(self, mock_urlopen: Mock) -> None:
        """Test retry logic on network failures."""
        mock_urlopen.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            Exception("Network error"),
        ]

        with pytest.raises(RuntimeError, match="Failed to fetch"):
            _fetch("https://example.com/page", retries=3, backoff=0.1)

        assert mock_urlopen.call_count == 3, "Count must be greater than zero"
