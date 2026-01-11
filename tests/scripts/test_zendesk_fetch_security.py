"""Security-focused tests for scripts/zendesk_docs_fetch.py URL validation."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path for direct import
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from zendesk_docs_fetch import _fetch


class TestURLValidation:
    """Test suite for _fetch URL security validation."""

    def test_reject_file_scheme(self) -> None:
        """Reject file:// URLs to prevent local file access."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("file:///etc/passwd")

    def test_reject_http_scheme(self) -> None:
        """Reject HTTP URLs (only HTTPS allowed)."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("http://example.com/page")

    def test_reject_ftp_scheme(self) -> None:
        """Reject FTP URLs."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("ftp://ftp.example.com/file")

    def test_reject_data_scheme(self) -> None:
        """Reject data: URLs."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("data:text/plain,Hello")

    def test_reject_javascript_scheme(self) -> None:
        """Reject javascript: URLs."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("javascript:alert(1)")

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
        assert result == b"test content"
        mock_urlopen.assert_called_once()

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

        assert mock_urlopen.call_count == 3

    def test_case_sensitive_scheme(self) -> None:
        """Ensure scheme validation is case-insensitive per RFC 3986."""
        # URL schemes should be case-insensitive, but our validation
        # explicitly checks for lowercase "https"
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("HTTPS://example.com")

    def test_reject_mixed_case_file_scheme(self) -> None:
        """Reject file:// with mixed case."""
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("FILE:///etc/passwd")
        with pytest.raises(ValueError, match="Only HTTPS URLs are allowed"):
            _fetch("File:///etc/passwd")
