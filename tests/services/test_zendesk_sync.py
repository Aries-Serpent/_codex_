"""
Comprehensive tests for Zendesk Knowledge Synchronization Service (PS-06).

Tests cover:
- Service initialization and configuration
- State management and caching
- Drift detection logic
- Incremental vs full sync modes
- PII scrubbing integration
- Error handling and retry logic
- JSON dataset generation
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest

from src.services.crawler.zendesk_sync import (
    ArticleMetadata,
    SyncResult,
    ZendeskKnowledgeSyncService,
)


class TestArticleMetadata:
    """Test suite for ArticleMetadata dataclass."""

    def test_article_metadata_creation(self):
        """Test creating ArticleMetadata with required fields."""
        meta = ArticleMetadata(
            url="https://example.zendesk.com/hc/article-1",
            section="getting-started",
            bucket="tutorials",
            last_fetched="2026-01-09T12:00:00+00:00",
        )

        assert meta.url == "https://example.zendesk.com/hc/article-1", "url is not valid"
        assert meta.section == "getting-started", "section is not valid"
        assert meta.bucket == "tutorials", "bucket is not valid"
        assert meta.last_fetched == "2026-01-09T12:00:00+00:00", "last_fetched is not valid"
        assert meta.last_modified is None, "last_modified is not valid"
        assert meta.etag is None, "etag is not valid"
        assert meta.content_hash is None, "Content must not be empty"

    def test_article_metadata_with_optional_fields(self):
        """Test ArticleMetadata with all optional fields."""
        meta = ArticleMetadata(
            url="https://example.zendesk.com/hc/article-1",
            section="api",
            bucket="reference",
            last_fetched="2026-01-09T12:00:00+00:00",
            last_modified="Wed, 08 Jan 2026 10:00:00 GMT",
            etag='"abc123"',
            content_hash="sha256:deadbeef",
        )

        assert meta.last_modified == "Wed, 08 Jan 2026 10:00:00 GMT"
        assert meta.etag == '"abc123"', "etag is not valid"
        assert meta.content_hash == "sha256:deadbeef", "Content must not be empty"


class TestSyncResult:
    """Test suite for SyncResult dataclass."""

    def test_sync_result_creation(self):
        """Test creating SyncResult with statistics."""
        result = SyncResult(
            total_articles=100,
            checked=95,
            updated=10,
            failed=5,
            skipped=85,
            timestamp="2026-01-09T12:00:00+00:00",
        )

        assert result.total_articles == 100, "Result must not be empty"
        assert result.checked == 95, "Result must not be empty"
        assert result.updated == 10, "Result must not be empty"
        assert result.failed == 5, "Result must not be empty"
        assert result.skipped == 85, "Result must not be empty"
        assert result.timestamp == "2026-01-09T12:00:00+00:00", "Result must not be empty"
        assert result.dataset_path is None, "Result must not be empty"

    def test_sync_result_with_dataset_path(self):
        """Test SyncResult with dataset path."""
        result = SyncResult(
            total_articles=50,
            checked=50,
            updated=25,
            failed=0,
            skipped=25,
            timestamp="2026-01-09T12:00:00+00:00",
            dataset_path=os.path.join(tempfile.gettempdir(), "dataset.json"),
        )

        assert result.dataset_path == os.path.join(tempfile.gettempdir(), "dataset.json"), "Result must not be empty"


class TestZendeskKnowledgeSyncService:
    """Test suite for ZendeskKnowledgeSyncService."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_manifest(self, temp_dir):
        """Create a mock manifest file."""
        manifest_path = temp_dir / "manifest.json"
        manifest_data = {
            "getting-started": {
                "tutorials": [
                    "https://example.zendesk.com/hc/tutorial-1",
                    "https://example.zendesk.com/hc/tutorial-2",
                ]
            },
            "api": {"reference": ["https://example.zendesk.com/hc/api-ref-1"]},
        }
        manifest_path.write_text(json.dumps(manifest_data))
        return manifest_path

    @pytest.fixture
    def service(self, temp_dir, mock_manifest):
        """Create a ZendeskKnowledgeSyncService instance for testing."""
        return ZendeskKnowledgeSyncService(
            manifest_path=mock_manifest,
            api_index_path=temp_dir / "api_index.json",
            output_root=temp_dir / "output",
            retries=2,
            backoff=0.1,
        )

    def test_service_initialization(self, service, temp_dir, mock_manifest):
        """Test service initialization with custom paths."""
        assert service.manifest_path == mock_manifest, "manifest_path is not valid"
        assert service.api_index_path == temp_dir / "api_index.json", "api_index_path is not valid"
        assert service.output_root == temp_dir / "output", "output_root is not valid"
        assert service.retries == 2, "retries is not valid"
        assert service.backoff == 0.1, "backoff is not valid"
        assert service._cache == {}, "_cache is not valid"

    def test_load_cache_empty(self, service):
        """Test loading cache when no cache file exists."""
        cache = service._load_cache()
        assert cache == {}, "cache is not valid"

    def test_load_cache_with_data(self, temp_dir):
        """Test loading cache with existing data."""
        cache_path = temp_dir / "cache.json"
        cache_data = {
            "version": "2.0",
            "last_sync": "2026-01-08T10:00:00+00:00",
            "articles": {
                "https://example.zendesk.com/hc/article-1": {
                    "url": "https://example.zendesk.com/hc/article-1",
                    "section": "getting-started",
                    "bucket": "tutorials",
                    "last_fetched": "2026-01-08T10:00:00+00:00",
                    "last_modified": "Wed, 07 Jan 2026 10:00:00 GMT",
                    "etag": '"abc123"',
                    "content_hash": None,
                }
            },
        }
        cache_path.write_text(json.dumps(cache_data))

        service = ZendeskKnowledgeSyncService(
            api_index_path=cache_path, output_root=temp_dir / "output"
        )

        assert len(service._cache) == 1, "Collection must not be empty"
        assert "https://example.zendesk.com/hc/article-1" in service._cache, "Condition must be true"
        meta = service._cache["https://example.zendesk.com/hc/article-1"]
        assert meta.section == "getting-started", "section is not valid"
        assert meta.etag == '"abc123"', "etag is not valid"

    def test_load_cache_corrupted(self, temp_dir):
        """Test loading cache with corrupted JSON."""
        cache_path = temp_dir / "cache.json"
        cache_path.write_text("{ invalid json")

        service = ZendeskKnowledgeSyncService(
            api_index_path=cache_path, output_root=temp_dir / "output"
        )

        # Should fall back to empty cache
        assert service._cache == {}, "_cache is not valid"

    def test_save_cache(self, service, temp_dir):
        """Test saving cache to disk."""
        service._cache["https://example.zendesk.com/hc/article-1"] = ArticleMetadata(
            url="https://example.zendesk.com/hc/article-1",
            section="api",
            bucket="reference",
            last_fetched="2026-01-09T12:00:00+00:00",
            etag='"xyz789"',
        )

        service._save_cache()

        assert service.api_index_path.exists(), "Condition must be true"
        cache_data = json.loads(service.api_index_path.read_text())

        assert cache_data["version"] == "2.0", "Data must not be empty"
        assert "last_sync" in cache_data, "Data must not be empty"
        assert len(cache_data["articles"]) == 1, "Collection must not be empty"
        assert "https://example.zendesk.com/hc/article-1" in cache_data["articles"], "Data must not be empty"

    def test_slug_generation(self, service):
        """Test URL to filename slug conversion."""
        assert service._slug("Hello World!") == "hello-world", "Condition must be true"
        assert service._slug("API/Reference/v2") == "api-reference-v2", "Condition must be true"
        assert service._slug("  spaces  ") == "spaces", "Condition must be true"
        assert service._slug("UPPERCASE") == "uppercase", "Condition must be true"

    @patch("urllib.request.urlopen")
    def test_fetch_success(self, mock_urlopen, service):
        """Test successful URL fetching."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>content</html>"
        mock_response.headers = {
            "ETag": '"abc123"',
            "Last-Modified": "Wed, 08 Jan 2026 10:00:00 GMT",
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        content, headers = service._fetch("https://example.zendesk.com/hc/article-1")

        assert content == b"<html>content</html>", "Content must not be empty"
        assert headers["ETag"] == '"abc123"', "Condition must be true"
        assert headers["Last-Modified"] == "Wed, 08 Jan 2026 10:00:00 GMT"

    @patch("urllib.request.urlopen")
    def test_fetch_with_retry(self, mock_urlopen, service):
        """Test URL fetching with retry on failure."""
        # First attempt fails, second succeeds
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>content</html>"
        mock_response.headers = {}

        # Create a proper context manager for the second call
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_response
        mock_context.__exit__.return_value = None

        mock_urlopen.side_effect = [URLError("Network error"), mock_context]

        content, _headers = service._fetch("https://example.zendesk.com/hc/article-1")

        assert content == b"<html>content</html>", "Content must not be empty"
        assert mock_urlopen.call_count == 2, "Count must be greater than zero"

    @patch("urllib.request.urlopen")
    def test_fetch_failure_after_retries(self, mock_urlopen, service):
        """Test URL fetching fails after all retries."""
        mock_urlopen.side_effect = URLError("Persistent network error")

        with pytest.raises(RuntimeError, match="Failed to fetch"):
            service._fetch("https://example.zendesk.com/hc/article-1")

        assert mock_urlopen.call_count == service.retries, "Count must be greater than zero"

    def test_fetch_invalid_scheme(self, service):
        """Test fetching URL with invalid scheme."""
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            service._fetch("http://example.com")  # Only https allowed

    def test_write_article(self, service, temp_dir):
        """Test writing article content to disk."""
        base = temp_dir / "output"
        url = "https://example.zendesk.com/hc/my-article"
        body = b"<html><body>Article content</body></html>"

        output_path = service._write_article(base, url, body)

        assert output_path.exists(), "Condition must be true"
        assert output_path.read_bytes() == body, "Condition must be true"
        assert output_path.name.endswith(".html"), "Condition must be true"

    def test_should_update_not_in_cache(self, service):
        """Test should_update returns True when article not in cache."""
        assert service._should_update("https://example.zendesk.com/hc/new-article", {}) is True

    def test_should_update_etag_match(self, service):
        """Test should_update returns False when ETag matches."""
        url = "https://example.zendesk.com/hc/article-1"
        service._cache[url] = ArticleMetadata(
            url=url,
            section="api",
            bucket="reference",
            last_fetched="2026-01-08T10:00:00+00:00",
            etag='"abc123"',
        )

        headers = {"ETag": '"abc123"'}
        assert service._should_update(url, headers) is False

    def test_should_update_etag_mismatch(self, service):
        """Test should_update returns True when ETag differs."""
        url = "https://example.zendesk.com/hc/article-1"
        service._cache[url] = ArticleMetadata(
            url=url,
            section="api",
            bucket="reference",
            last_fetched="2026-01-08T10:00:00+00:00",
            etag='"abc123"',
        )

        headers = {"ETag": '"xyz789"'}
        assert service._should_update(url, headers) is True

    def test_should_update_last_modified_not_changed(self, service):
        """Test should_update returns False when Last-Modified unchanged."""
        url = "https://example.zendesk.com/hc/article-1"
        service._cache[url] = ArticleMetadata(
            url=url,
            section="api",
            bucket="reference",
            last_fetched="2026-01-08T10:00:00+00:00",
            last_modified="Wed, 07 Jan 2026 10:00:00 GMT",
        )

        headers = {"Last-Modified": "Wed, 07 Jan 2026 10:00:00 GMT"}
        assert service._should_update(url, headers) is False

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch.object(ZendeskKnowledgeSyncService, "_fetch")
    def test_check_and_pull_dry_run(self, mock_fetch, mock_scrub, service, mock_manifest):
        """Test check_and_pull in dry-run mode."""
        result = service.check_and_pull(dry_run=True)

        assert result.total_articles == 3, "Result must not be empty"
        assert result.checked == 3, "Result must not be empty"
        assert result.updated == 0, "Result must not be empty"
        assert result.failed == 0, "Result must not be empty"
        assert mock_fetch.call_count == 0, "Count must be greater than zero"

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch.object(ZendeskKnowledgeSyncService, "_fetch")
    def test_check_and_pull_full_sync(self, mock_fetch, mock_scrub, service, mock_manifest):
        """Test full check_and_pull sync."""
        mock_fetch.return_value = (b"<html>content</html>", {"ETag": '"abc123"'})
        mock_scrub.return_value = ("<html>scrubbed</html>", {})

        result = service.check_and_pull(dry_run=False, force=False)

        assert result.total_articles == 3, "Result must not be empty"
        assert result.checked == 3, "Result must not be empty"
        assert result.updated == 3, "Result must not be empty"
        assert result.failed == 0, "Result must not be empty"
        assert len(service._cache) == 3, "Collection must not be empty"

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch.object(ZendeskKnowledgeSyncService, "_fetch")
    def test_check_and_pull_with_pii_detection(
        self, mock_fetch, mock_scrub, service, mock_manifest
    ):
        """Test check_and_pull detects and logs PII."""
        mock_fetch.return_value = (b"<html>email@example.com</html>", {})
        mock_scrub.return_value = ("<html>[REDACTED]</html>", {"email": True})

        result = service.check_and_pull(dry_run=False)

        assert result.updated == 3, "Result must not be empty"
        # Verify scrubbing was called
        assert mock_scrub.call_count == 3, "Count must be greater than zero"

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch.object(ZendeskKnowledgeSyncService, "_fetch")
    def test_check_and_pull_with_failures(self, mock_fetch, mock_scrub, service, mock_manifest):
        """Test check_and_pull handles failures gracefully."""
        mock_fetch.side_effect = [
            (b"<html>content1</html>", {}),
            RuntimeError("Network error"),
            (b"<html>content3</html>", {}),
        ]
        mock_scrub.return_value = ("<html>scrubbed</html>", {})

        result = service.check_and_pull(dry_run=False)

        assert result.total_articles == 3, "Result must not be empty"
        assert result.updated == 2, "Result must not be empty"
        assert result.failed == 1, "Result must not be empty"

    def test_check_and_pull_missing_manifest(self, temp_dir):
        """Test check_and_pull raises error when manifest missing."""
        service = ZendeskKnowledgeSyncService(
            manifest_path=temp_dir / "nonexistent.json", output_root=temp_dir / "output"
        )

        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            service.check_and_pull()

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch.object(ZendeskKnowledgeSyncService, "_fetch")
    def test_incremental_sync_no_previous_sync(
        self, mock_fetch, mock_scrub, service, mock_manifest
    ):
        """Test incremental sync falls back to full sync when no cache exists."""
        mock_fetch.return_value = (b"<html>content</html>", {})
        mock_scrub.return_value = ("<html>scrubbed</html>", {})

        result = service.check_and_pull_incremental(dry_run=False)

        # Should perform full sync
        assert result.total_articles == 3, "Result must not be empty"
        assert result.updated == 3, "Result must not be empty"

    def test_export_json_dataset(self, service, temp_dir):
        """Test JSON dataset generation."""
        # Create some test HTML files
        source_dir = temp_dir / "output" / "2026-01-09"
        section_dir = source_dir / "api" / "reference"
        section_dir.mkdir(parents=True, exist_ok=True)

        (section_dir / "article-1.html").write_text("<html>Article 1</html>")
        (section_dir / "article-2.html").write_text("<html>Article 2</html>")

        dataset_path = service._export_json_dataset(source_dir)

        assert dataset_path.exists(), "Data must not be empty"
        dataset = json.loads(dataset_path.read_text())

        assert dataset["version"] == "1.0", "Data must not be empty"
        assert dataset["article_count"] == 2, "Data must not be empty"
        assert len(dataset["articles"]) == 2, "Collection must not be empty"
        assert all("content" in article for article in dataset["articles"]), "Data must not be empty"
        assert all("section" in article for article in dataset["articles"]), "Data must not be empty"

    def test_pipeline_to_codex_digest(self, service, temp_dir):
        """Test pipeline preparation to codex_digest."""
        # Create test directory with HTML files
        source_dir = temp_dir / "output" / "2026-01-09"
        section_dir = source_dir / "api" / "reference"
        section_dir.mkdir(parents=True, exist_ok=True)

        (section_dir / "article-1.html").write_text("<html>Article 1</html>")
        (section_dir / "article-2.html").write_text("<html>Article 2</html>")

        result = service.pipeline_to_codex_digest(source_dir)

        assert result["files_found"] == 2, "Result must not be empty"
        assert result["status"] == "ready_for_tokenization", "Result must not be empty"
        assert "source_dir" in result, "Result must not be empty"

    def test_pipeline_no_source_dir(self, service):
        """Test pipeline raises error when no sync directory exists."""
        with pytest.raises(ValueError, match="No synchronized documentation found"):
            service.pipeline_to_codex_digest()


class TestServiceIntegration:
    """Integration tests for the full sync workflow."""

    @pytest.fixture
    def integration_service(self, tmp_path):
        """Create service with temporary paths for integration testing."""
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {"tutorials": {"basics": ["https://example.zendesk.com/hc/tutorial-1"]}}
        manifest_path.write_text(json.dumps(manifest_data))

        return ZendeskKnowledgeSyncService(
            manifest_path=manifest_path,
            api_index_path=tmp_path / "cache.json",
            output_root=tmp_path / "output",
        )

    @patch("src.services.crawler.zendesk_sync.scrub_pii")
    @patch("urllib.request.urlopen")
    def test_full_workflow_integration(self, mock_urlopen, mock_scrub, integration_service):
        """Test complete workflow from fetch to cache update."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>Tutorial content</html>"
        mock_response.headers = {
            "ETag": '"integration-test"',
            "Last-Modified": "Wed, 08 Jan 2026 10:00:00 GMT",
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Mock PII scrubbing
        mock_scrub.return_value = ("<html>Tutorial content</html>", {})

        # Run sync
        result = integration_service.check_and_pull(dry_run=False)

        # Verify results
        assert result.total_articles == 1, "Result must not be empty"
        assert result.updated == 1, "Result must not be empty"
        assert result.failed == 0, "Result must not be empty"

        # Verify cache was updated
        assert len(integration_service._cache) == 1, "Collection must not be empty"
        cached_meta = list(integration_service._cache.values())[0]
        assert cached_meta.etag == '"integration-test"', "etag is not valid"

        # Verify cache was saved to disk
        assert integration_service.api_index_path.exists(), "Condition must be true"

        # Verify output files were created
        output_files = list(integration_service.output_root.rglob("*.html"))
        assert len(output_files) == 1, "Output_files must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
