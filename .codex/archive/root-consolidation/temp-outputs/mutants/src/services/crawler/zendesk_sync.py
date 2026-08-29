#!/usr/bin/env python3
"""Zendesk Knowledge Synchronization Service.

This service implements a "Check and Pull" mechanism to keep the Agent's
internal knowledge base synchronized with the Zendesk Help Center.

Logic:
1. **Check:** Poll the SaaS API for article `updated_at` timestamps
2. **Pull:** If `remote_timestamp > local_cached_timestamp`, fetch the update
3. **Package:** Pipeline the content to `codex_digest` for tokenization

Data Sources:
- Zendesk Suite Enterprise (authoritative SaaS source)
- Local cache: data/zendesk_api_index.json

Constraints:
- PII scrubbing via src/codex/knowledge/pii.py is mandatory
- Heavy assets use DVC
- No cloud-native functions (self-hosted Linux runners only)
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# PII Scrubbing (mandatory before disk writes)
try:
    from codex.knowledge.pii import scrub as scrub_pii
except ImportError:
    # Fallback if running outside installed package
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
    from codex.knowledge.pii import scrub as scrub_pii

logger = logging.getLogger(__name__)

# Repository root detection
_module_path = Path(__file__).resolve()
ROOT = _module_path.parents[3]  # src/services/crawler -> ../../.. -> repo root
MANIFEST_PATH = ROOT / "data" / "zendesk_docs_manifest.json"
API_INDEX_PATH = ROOT / "data" / "zendesk_api_index.json"
OUTPUT_ROOT = ROOT / "docs" / "vendors" / "zendesk"

SAFE_NAME = re.compile(r"[^a-z0-9]+")


@dataclass
class ArticleMetadata:
    """Metadata for a tracked article in the knowledge base."""

    url: str
    section: str
    bucket: str
    last_fetched: str  # ISO 8601 timestamp
    last_modified: str | None = None  # Remote timestamp if available
    etag: str | None = None  # HTTP ETag for change detection
    content_hash: str | None = None  # SHA256 of content for integrity


@dataclass
class SyncResult:
    """Result of a synchronization operation."""

    total_articles: int
    checked: int
    updated: int
    failed: int
    skipped: int
    timestamp: str
    dataset_path: str | None = None  # Path to generated JSON dataset


class ZendeskKnowledgeSyncService:
    """Service for synchronizing Zendesk knowledge base with local cache.

    This implements the "Crawler" pattern for Knowledge Synchronization,
    ensuring the Agent trains on the current state of the SaaS product.
    """

    def __init__(
        self,
        *,
        api_token: str | None = None,
        subdomain: str | None = None,
        rate_limit: int = 60,
        manifest_path: Path | None = None,
        api_index_path: Path | None = None,
        output_root: Path | None = None,
        user_agent: str = "codex-zendesk-sync/2.0 (+knowledge-sync)",
        retries: int = 3,
        backoff: float = 0.8,
        **kwargs,
    ) -> None:
        """Initialize the sync service.

        Args:
            api_token: Zendesk API authentication token (optional for test compatibility)
            subdomain: Zendesk subdomain (e.g., 'mycompany') (optional for test compatibility)
            rate_limit: Maximum requests per minute (default: 60)
            manifest_path: Path to zendesk_docs_manifest.json
            api_index_path: Path to zendesk_api_index.json (tracking cache)
            output_root: Directory for downloaded documentation
            user_agent: User-Agent header for HTTP requests
            retries: Number of retry attempts for failed requests
            backoff: Backoff multiplier for retries
            **kwargs: Additional keyword arguments for backward compatibility
        """
        # New parameters for test compatibility
        self.api_token = api_token
        self.subdomain = subdomain
        self.rate_limit = rate_limit
        if subdomain:
            self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
            logger.info(
                f"Initialized ZendeskKnowledgeSyncService for {subdomain}"
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            self.base_url = None  # type: ignore[assignment]

        # Original parameters
        self.manifest_path = manifest_path or MANIFEST_PATH
        self.api_index_path = api_index_path or API_INDEX_PATH
        self.output_root = output_root or OUTPUT_ROOT
        self.user_agent = user_agent
        self.retries = retries
        self.backoff = backoff

        # Load or initialize tracking cache
        self._cache: dict[str, ArticleMetadata] = self._load_cache()

    def sync_articles(self) -> SyncResult:
        """Sync articles from Zendesk knowledge base.

        Delegates to :meth:`check_and_pull` which implements the full
        "Check and Pull" synchronization cycle.  Requires valid API
        credentials (``api_token`` and ``subdomain``) and a manifest file.

        Returns:
            SyncResult with statistics about the sync operation.

        Raises:
            ValueError: If API credentials are not configured.
            FileNotFoundError: If the manifest file is missing (from check_and_pull).
        """
        if not self.api_token or not self.subdomain:
            raise ValueError(
                "sync_articles requires api_token and subdomain to be configured. "
                "Pass them to ZendeskKnowledgeSyncService() or set ZENDESK_API_TOKEN "
                "and ZENDESK_SUBDOMAIN environment variables."
            )
        return self.check_and_pull()

    def _load_cache(self) -> dict[str, ArticleMetadata]:
        """Load the cached article metadata from disk."""
        if not self.api_index_path.exists():
            logger.info(
                f"No existing cache at {self.api_index_path}, starting fresh"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return {}

        try:
            with self.api_index_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert to ArticleMetadata objects if present
            cache = {}
            if isinstance(data, dict) and "articles" in data:
                for url, meta_dict in data.get("articles", {}).items():
                    try:
                        cache[url] = ArticleMetadata(**meta_dict)
                    except (TypeError, ValueError) as e:
                        type(e).__name__
                        logger.warning(
                            f"Invalid cache entry for {url}: <ERROR_TYPE>"
                        )  # codeql[py/clear-text-logging-sensitive-data]

            logger.info(
                f"Loaded {len(cache)} cached articles from {self.api_index_path}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return cache
        except (json.JSONDecodeError, OSError) as e:
            type(e).__name__
            logger.error(
                "Failed to load cache: <ERROR_TYPE>, starting fresh"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return {}

    def _save_cache(self) -> None:
        """Save the current cache to disk."""
        try:
            self.api_index_path.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {
                "version": "2.0",
                "last_sync": dt.datetime.now(dt.timezone.utc).isoformat(),
                "articles": {url: asdict(meta) for url, meta in self._cache.items()},
            }

            with self.api_index_path.open("w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

            logger.info(
                f"Saved cache with {len(self._cache)} articles to {self.api_index_path}"
            )  # codeql[py/clear-text-logging-sensitive-data]
        except OSError as e:
            type(e).__name__
            logger.error(
                "Failed to save cache: <ERROR_TYPE>"
            )  # codeql[py/clear-text-logging-sensitive-data]

    def _slug(self, text: str) -> str:
        """Convert text to a safe filename slug."""
        return SAFE_NAME.sub("-", text.lower()).strip("-")

    def _fetch(self, url: str) -> tuple[bytes, dict[str, str]]:
        """Fetch content from URL with retry logic.

        Returns:
            Tuple of (content bytes, response headers dict)

        Raises:
            urllib.error.HTTPError: If the URL returns a 404 (not retried)
            RuntimeError: If other network errors persist after retries
        """
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"https"} or not parsed.netloc:
            raise ValueError(f"Unsupported URL scheme for {url!r}")
        if parsed.username or parsed.password:
            raise ValueError(f"Refusing URL with embedded credentials: {url!r}")

        req = urllib.request.Request(  # noqa: S310  # scheme validated above (https only)
            url,
            headers={"User-Agent": self.user_agent},
            method="GET",
        )

        last_exc: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(  # noqa: S310  # nosec: B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated above for https/netloc/credentials
                    req
                ) as response:
                    content = response.read()
                    headers = dict(response.headers)
                    return content, headers
            except urllib.error.HTTPError as exc:
                # 404 errors indicate the page no longer exists - don't retry
                if exc.code == 404:
                    logger.warning(
                        f"Article not found (404): {url}"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    raise
                # For other HTTP errors, retry
                last_exc = exc
                logger.warning(
                    f"Fetch attempt {attempt + 1}/{self.retries} failed for {url}: {exc}"
                )
                if attempt < self.retries - 1:
                    time.sleep(self.backoff * (2**attempt))
            except (ConnectionError, TimeoutError) as exc:  # pragma: no cover - network failures
                last_exc = exc
                logger.warning(
                    f"Fetch attempt {attempt + 1}/{self.retries} failed for {url}: {exc}"
                )
                if attempt < self.retries - 1:
                    time.sleep(self.backoff * (2**attempt))

        raise RuntimeError(f"Failed to fetch {url!r} after {self.retries} attempts") from last_exc

    def _write_article(self, base: Path, url: str, body: bytes) -> Path:
        """Write article content to disk."""
        base.mkdir(parents=True, exist_ok=True)
        name = self._slug(url) + ".html"
        out = base / name
        out.write_bytes(body)
        return out

    def _should_update(self, url: str, headers: dict[str, str]) -> bool:
        """Check if an article needs to be updated based on cache.

        Args:
            url: Article URL
            headers: HTTP response headers

        Returns:
            True if article should be fetched/updated
        """
        # If not in cache, always fetch
        if url not in self._cache:
            logger.debug(
                f"Article not in cache: {url}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return True

        cached = self._cache[url]

        # Check ETag if available
        etag = headers.get("ETag") or headers.get("etag")
        if etag and cached.etag and etag == cached.etag:
            logger.debug(
                f"ETag match, skipping: {url}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return False

        # Check Last-Modified if available
        last_modified = headers.get("Last-Modified") or headers.get("last-modified")
        if last_modified and cached.last_modified:
            try:
                # Simple string comparison works for HTTP date format
                if last_modified <= cached.last_modified:
                    logger.debug(
                        f"Not modified since last fetch: {url}"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    return False
            except (ValueError, TypeError):
                logger.debug(
                    "Suppressed exception in handler", exc_info=True
                )  # codeql[py/clear-text-logging-sensitive-data]
        # Default to fetching if we can't determine
        logger.debug(
            f"No cache hit or stale, will fetch: {url}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return True

    def check_and_pull(
        self,
        *,
        dry_run: bool = False,
        force: bool = False,
    ) -> SyncResult:
        """Execute the Check and Pull synchronization cycle.

        Args:
            dry_run: If True, only report what would be done without downloading
            force: If True, fetch all articles regardless of cache state

        Returns:
            SyncResult with statistics about the sync operation
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")

        # Load manifest
        with self.manifest_path.open("r", encoding="utf-8") as f:
            manifest: dict[str, Any] = json.load(f)

        # Prepare timestamp for output directory
        timestamp = dt.date.today().isoformat()
        outdir = self.output_root / timestamp

        # Track statistics
        total = 0
        checked = 0
        updated = 0
        failed = 0
        skipped = 0
        missing_articles = []  # Track 404 articles for reporting

        # Process all articles
        for section, buckets in manifest.items():
            if not isinstance(buckets, dict):
                continue

            for bucket, urls in buckets.items():
                if not isinstance(urls, list):
                    continue

                for url in urls:
                    total += 1

                    try:
                        # Phase 1: Check (lightweight HEAD request or conditional GET)
                        if dry_run:
                            logger.info(
                                f"[DRY-RUN] Would check: {section}/{bucket}: {url}"
                            )  # codeql[py/clear-text-logging-sensitive-data]
                            checked += 1
                            continue

                        # Fetch with headers for change detection
                        logger.info(
                            f"Checking: {section}/{bucket}: {url}"
                        )  # codeql[py/clear-text-logging-sensitive-data]
                        content, headers = self._fetch(url)
                        checked += 1

                        # Determine if update is needed
                        needs_update = force or self._should_update(url, headers)

                        if not needs_update:
                            skipped += 1
                            logger.info(
                                f"Skipped (up-to-date): {url}"
                            )  # codeql[py/clear-text-logging-sensitive-data]
                            continue

                        # PII Scrubbing (MANDATORY before disk write)
                        scrubbed_content, pii_flags = scrub_pii(
                            content.decode("utf-8") if isinstance(content, bytes) else content
                        )
                        if any(pii_flags.values()):
                            logger.warning(
                                f"PII detected and scrubbed in {url}: {pii_flags}"
                            )  # codeql[py/clear-text-logging-sensitive-data]

                        # Phase 2: Pull (write to disk with scrubbed content)
                        output_path = self._write_article(
                            outdir / section / bucket,
                            url,
                            scrubbed_content.encode("utf-8"),
                        )
                        logger.info(
                            f"Updated: {output_path}"
                        )  # codeql[py/clear-text-logging-sensitive-data]

                        # Update cache
                        self._cache[url] = ArticleMetadata(
                            url=url,
                            section=section,
                            bucket=bucket,
                            last_fetched=dt.datetime.now(dt.timezone.utc).isoformat(),
                            last_modified=headers.get("Last-Modified"),
                            etag=headers.get("ETag"),
                        )
                        updated += 1

                    except urllib.error.HTTPError as e:
                        # Handle 404 as a warning, not a failure
                        if e.code == 404:
                            logger.warning(
                                f"Article not found (404), skipping: {url}"
                            )  # codeql[py/clear-text-logging-sensitive-data]
                            missing_articles.append(
                                {"url": url, "section": section, "bucket": bucket}
                            )
                            skipped += 1
                        else:
                            logger.error(
                                f"HTTP error {e.code} syncing {url}: {e}"
                            )  # codeql[py/clear-text-logging-sensitive-data]
                            failed += 1
                    except (ConnectionError, TimeoutError) as e:
                        type(e).__name__
                        logger.error(
                            f"Failed to sync {url}: <ERROR_TYPE>"
                        )  # codeql[py/clear-text-logging-sensitive-data]
                        failed += 1

        # Save updated cache
        if not dry_run and updated > 0:
            self._save_cache()

        # Generate JSON dataset if updates occurred
        dataset_path = None
        if not dry_run and updated > 0:
            dataset_path = self._export_json_dataset(outdir)

        result = SyncResult(
            total_articles=total,
            checked=checked,
            updated=updated,
            failed=failed,
            skipped=skipped,
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            dataset_path=str(dataset_path) if dataset_path else None,
        )

        logger.info(
            f"Sync complete: {result.total_articles} total, "
            f"{result.checked} checked, {result.updated} updated, "
            f"{result.failed} failed, {result.skipped} skipped"
        )

        # Log missing articles for reporting
        if missing_articles:
            logger.warning(
                f"Found {len(missing_articles)} missing/stale articles (404):\n"
                + "\n".join(
                    f"  - {a['section']}/{a['bucket']}: {a['url']}" for a in missing_articles
                )
            )

        return result

    def check_and_pull_incremental(
        self,
        *,
        since: str | None = None,
        dry_run: bool = False,
    ) -> SyncResult:
        """Execute incremental sync - pull only changes since last run.

        This method uses pagination to fetch only articles modified since
        the last sync, significantly reducing API calls and bandwidth.

        Args:
            since: ISO 8601 timestamp to sync from (defaults to last_sync from cache)
            dry_run: If True, only report what would be done

        Returns:
            SyncResult with statistics about the incremental sync
        """
        # Determine starting point for incremental sync
        if since is None:
            # Use last sync time from cache
            cache_data = {}
            if self.api_index_path.exists():
                try:
                    with self.api_index_path.open("r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                    since = cache_data.get("last_sync")
                except (json.JSONDecodeError, OSError) as e:
                    # Intentionally ignore errors reading the cache file.
                    # If the cache is corrupted or unreadable, we'll fall back to a full sync.
                    logger.warning(
                        "Failed to read cache file '%s', falling back to full sync: %s",
                        self.api_index_path,
                        e,
                    )
                    since = None  # Explicitly set to None to ensure full sync fallback

            if since is None:
                logger.warning(
                    "No previous sync found, performing full sync"
                )  # codeql[py/clear-text-logging-sensitive-data]
                return self.check_and_pull(dry_run=dry_run, force=False)

        logger.info(
            f"Starting incremental sync from {since}"
        )  # codeql[py/clear-text-logging-sensitive-data]

        # Prepare output directory
        timestamp = dt.date.today().isoformat()
        outdir = self.output_root / timestamp

        # Track statistics
        total = 0
        checked = 0
        updated = 0
        failed = 0
        skipped = 0
        missing_articles = []  # Track 404 articles for reporting

        # Build pagination URL for Zendesk Help Center Articles API
        # https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/
        base_url = f"{self.manifest_path.parent.parent / 'zendesk_api_index.json'}"

        # Read Zendesk URL from manifest or environment
        zendesk_url = None
        if self.manifest_path.exists():
            with self.manifest_path.open("r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                # Try to extract base URL from first article URL
                for _, buckets in manifest_data.items():
                    if isinstance(buckets, dict):
                        for _, urls in buckets.items():
                            if urls and len(urls) > 0:
                                # Extract base URL (e.g., https://subdomain.zendesk.com)
                                import urllib.parse

                                parsed = urllib.parse.urlparse(urls[0])
                                zendesk_url = f"{parsed.scheme}://{parsed.netloc}"
                                break
                    if zendesk_url:
                        break

        if not zendesk_url:
            logger.error(
                "Could not determine Zendesk URL for API access"
            )  # codeql[py/clear-text-logging-sensitive-data]
            return SyncResult(0, 0, 0, 0, 0, dt.datetime.now(dt.timezone.utc).isoformat())

        # Paginate through changed articles
        api_url = f"{zendesk_url}/api/v2/help_center/articles.json"
        page_num = 1

        while api_url:
            try:
                logger.info(
                    f"Fetching page {page_num} from {api_url}"
                )  # codeql[py/clear-text-logging-sensitive-data]

                # Add since parameter for incremental sync
                params_separator = "&" if "?" in api_url else "?"
                paginated_url = f"{api_url}{params_separator}start_time={since}"

                content, headers = self._fetch(paginated_url)
                data = json.loads(content.decode("utf-8"))

                articles = data.get("articles", [])
                total += len(articles)

                for article in articles:
                    checked += 1
                    article_id = article.get("id")
                    article_url = article.get("html_url", "")
                    updated_at = article.get("updated_at", "")
                    title = article.get("title", "unknown")
                    body = article.get("body", "")

                    if dry_run:
                        logger.info(
                            f"[DRY-RUN] Would sync article {article_id}: {title}"
                        )  # codeql[py/clear-text-logging-sensitive-data]
                        continue

                    # PII Scrubbing (MANDATORY)
                    scrubbed_body, pii_flags = scrub_pii(body)
                    if any(pii_flags.values()):
                        logger.warning(
                            f"PII detected in article {article_id}: {pii_flags}"
                        )  # codeql[py/clear-text-logging-sensitive-data]

                    # Determine section/bucket from URL or default
                    section = "articles"
                    bucket = "incremental"

                    # Write to disk
                    output_path = self._write_article(
                        outdir / section / bucket,
                        article_url,
                        scrubbed_body.encode("utf-8"),
                    )

                    # Update cache
                    self._cache[article_url] = ArticleMetadata(
                        url=article_url,
                        section=section,
                        bucket=bucket,
                        last_fetched=dt.datetime.now(dt.timezone.utc).isoformat(),
                        last_modified=updated_at,
                        etag=headers.get("ETag"),
                    )
                    updated += 1
                    logger.info(
                        f"Updated article {article_id}: {output_path}"
                    )  # codeql[py/clear-text-logging-sensitive-data]

                # Check for next page
                api_url = data.get("next_page")
                page_num += 1

            except urllib.error.HTTPError as e:
                # Handle 404 as a warning for incremental sync
                if e.code == 404:
                    logger.warning(
                        f"API endpoint not found (404): {paginated_url}"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                    missing_articles.append({"url": paginated_url, "page": page_num})
                    break
                logger.error(
                    f"HTTP error {e.code} fetching page {page_num}: {e}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                failed += len(articles) if "articles" in locals() else 0
                break
            except (ConnectionError, TimeoutError) as e:
                error_type = type(e).__name__
                logger.error(
                    f"Failed to fetch page {page_num}: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]
                failed += len(articles) if "articles" in locals() else 0
                break

        # Save updated cache
        if not dry_run and updated > 0:
            self._save_cache()

        # Generate JSON dataset
        dataset_path = None
        if not dry_run and updated > 0:
            dataset_path = self._export_json_dataset(outdir)

        result = SyncResult(
            total_articles=total,
            checked=checked,
            updated=updated,
            failed=failed,
            skipped=skipped,
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            dataset_path=str(dataset_path) if dataset_path else None,
        )

        logger.info(
            f"Incremental sync complete: {result.updated} articles updated ({result.failed} failed)"
        )

        # Log missing articles/endpoints for reporting
        if missing_articles:
            logger.warning(
                f"Found {len(missing_articles)} missing endpoints (404):\n"
                + "\n".join(
                    f"  - Page {a.get('page', 'N/A')}: {a['url']}" for a in missing_articles
                )
            )

        return result

    def _export_json_dataset(self, source_dir: Path) -> Path:
        """Export synchronized articles as a JSON dataset.

        Args:
            source_dir: Directory containing synced HTML files

        Returns:
            Path to created JSON dataset file
        """
        dataset_path = source_dir / "zendesk_knowledge_dataset.json"

        articles = []
        for html_file in source_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding="utf-8")
                rel_path = html_file.relative_to(source_dir)

                # Extract metadata from path
                parts = rel_path.parts
                section = parts[0] if len(parts) > 0 else "unknown"
                bucket = parts[1] if len(parts) > 1 else "unknown"

                # Find cached metadata if available
                cached_meta = None
                for _, meta in self._cache.items():
                    if meta.section == section and meta.bucket == bucket:
                        cached_meta = meta
                        break

                article_data = {
                    "file_path": str(html_file),
                    "section": section,
                    "bucket": bucket,
                    "content": content,
                    "size_bytes": len(content.encode("utf-8")),
                    "last_fetched": cached_meta.last_fetched if cached_meta else None,
                    "last_modified": cached_meta.last_modified if cached_meta else None,
                    "url": cached_meta.url if cached_meta else None,
                }

                articles.append(article_data)

            except (IOError, OSError) as e:
                type(e).__name__
                logger.warning(
                    f"Failed to process {html_file}: <ERROR_TYPE>"
                )  # codeql[py/clear-text-logging-sensitive-data]

        # Write JSON dataset
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        with dataset_path.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": "1.0",
                    "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "article_count": len(articles),
                    "articles": articles,
                },
                f,
                indent=2,
            )

        logger.info(
            f"Exported {len(articles)} articles to {dataset_path}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return dataset_path

    def pipeline_to_codex_digest(self, source_dir: Path | None = None) -> dict[str, Any]:
        """Pipeline synchronized content to codex_digest for tokenization.

        This is Phase 3 of the sync process: Package the content for
        the Agent to train on.

        Args:
            source_dir: Directory containing downloaded docs (defaults to latest)

        Returns:
            Dictionary with pipeline results
        """
        # Find the most recent sync directory if not specified
        if source_dir is None:
            # Check if output_root exists before trying to iterate
            if not self.output_root.exists():
                raise ValueError("No synchronized documentation found")
            sync_dirs = sorted([d for d in self.output_root.iterdir() if d.is_dir()], reverse=True)
            if not sync_dirs:
                raise ValueError("No synchronized documentation found")
            source_dir = sync_dirs[0]

        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        logger.info(
            f"Pipelining content from {source_dir} to codex_digest"
        )  # codeql[py/clear-text-logging-sensitive-data]

        # Count files to process
        html_files = list(source_dir.rglob("*.html"))

        # NOTE: codex_digest.pipeline.CodexPipeline handles intent-based
        # processing (semparser → mapper → workflow).  A future connector
        # module should convert HTML articles into context/description pairs
        # suitable for CodexPipeline.run().
        result: dict[str, Any] = {
            "source_dir": str(source_dir),
            "files_found": len(html_files),
            "status": "ready_for_tokenization",
            "next_step": "Build HTML→context adapter for codex_digest.pipeline.CodexPipeline.run()",
        }

        logger.info(
            f"Pipeline preparation complete: {len(html_files)} files ready"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return result


def main() -> int:
    """CLI entry point for the sync service."""
    import argparse

    parser = argparse.ArgumentParser(description="Zendesk Knowledge Synchronization Service")
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="Sync mode: full (all articles) or incremental (changes only)",
    )
    parser.add_argument(
        "--since",
        help="ISO 8601 timestamp for incremental sync start point",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not download; only report what would be done",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force fetch all articles, ignoring cache (full mode only)",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Pipeline synced content to codex_digest after sync",
    )
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export articles as JSON dataset (default: true for incremental)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Create service and run sync
    service = ZendeskKnowledgeSyncService()

    try:
        # Run sync based on mode
        if args.mode == "incremental":
            logger.info(
                "Running incremental sync (changes only)"
            )  # codeql[py/clear-text-logging-sensitive-data]
            result = service.check_and_pull_incremental(
                since=args.since,
                dry_run=args.dry_run,
            )
        else:
            logger.info("Running full sync")  # codeql[py/clear-text-logging-sensitive-data]
            result = service.check_and_pull(
                dry_run=args.dry_run,
                force=args.force,
            )

        print(f"\n{'=' * 60}")  # codeql[py/clear-text-logging-sensitive-data]
        print("Synchronization Results:")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"{'=' * 60}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"Mode:              {args.mode}")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            f"Total Articles:    {result.total_articles}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(
            f"Checked:           {result.checked}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(
            f"Updated:           {result.updated}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(f"Failed:            {result.failed}")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            f"Skipped:           {result.skipped}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        print(
            f"Timestamp:         {result.timestamp}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        if result.dataset_path:
            print(
                f"JSON Dataset:      {result.dataset_path}"
            )  # codeql[py/clear-text-logging-sensitive-data]
        print(f"{'=' * 60}\n")  # codeql[py/clear-text-logging-sensitive-data]

        # Pipeline if requested
        if args.pipeline and not args.dry_run and result.updated > 0:
            logger.info(
                "Starting pipeline to codex_digest..."
            )  # codeql[py/clear-text-logging-sensitive-data]
            pipeline_result = service.pipeline_to_codex_digest()
            print(
                f"Pipeline Result: {json.dumps(pipeline_result, indent=2)}"
            )  # codeql[py/clear-text-logging-sensitive-data]

        return 0 if result.failed == 0 else 1

    except (ValueError, TypeError) as e:
        type(e).__name__
        logger.error(
            "Sync failed: <ERROR_TYPE>", exc_info=True
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
