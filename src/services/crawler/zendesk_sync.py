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


class ZendeskKnowledgeSyncService:
    """Service for synchronizing Zendesk knowledge base with local cache.
    
    This implements the "Crawler" pattern for Knowledge Synchronization,
    ensuring the Agent trains on the current state of the SaaS product.
    """

    def __init__(
        self,
        *,
        manifest_path: Path | None = None,
        api_index_path: Path | None = None,
        output_root: Path | None = None,
        user_agent: str = "codex-zendesk-sync/2.0 (+knowledge-sync)",
        retries: int = 3,
        backoff: float = 0.8,
    ) -> None:
        """Initialize the sync service.
        
        Args:
            manifest_path: Path to zendesk_docs_manifest.json
            api_index_path: Path to zendesk_api_index.json (tracking cache)
            output_root: Directory for downloaded documentation
            user_agent: User-Agent header for HTTP requests
            retries: Number of retry attempts for failed requests
            backoff: Backoff multiplier for retries
        """
        self.manifest_path = manifest_path or MANIFEST_PATH
        self.api_index_path = api_index_path or API_INDEX_PATH
        self.output_root = output_root or OUTPUT_ROOT
        self.user_agent = user_agent
        self.retries = retries
        self.backoff = backoff
        
        # Load or initialize tracking cache
        self._cache: dict[str, ArticleMetadata] = self._load_cache()
        
    def _load_cache(self) -> dict[str, ArticleMetadata]:
        """Load the cached article metadata from disk."""
        if not self.api_index_path.exists():
            logger.info(f"No existing cache at {self.api_index_path}, starting fresh")
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
                        logger.warning(f"Invalid cache entry for {url}: {e}")
            
            logger.info(f"Loaded {len(cache)} cached articles from {self.api_index_path}")
            return cache
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load cache: {e}, starting fresh")
            return {}
    
    def _save_cache(self) -> None:
        """Save the current cache to disk."""
        try:
            self.api_index_path.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                "version": "2.0",
                "last_sync": dt.datetime.now(dt.timezone.utc).isoformat(),
                "articles": {
                    url: asdict(meta) for url, meta in self._cache.items()
                }
            }
            
            with self.api_index_path.open("w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Saved cache with {len(self._cache)} articles to {self.api_index_path}")
        except OSError as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _slug(self, text: str) -> str:
        """Convert text to a safe filename slug."""
        return SAFE_NAME.sub("-", text.lower()).strip("-")
    
    def _fetch(self, url: str) -> tuple[bytes, dict[str, str]]:
        """Fetch content from URL with retry logic.
        
        Returns:
            Tuple of (content bytes, response headers dict)
        """
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"https"}:
            raise ValueError(f"Unsupported URL scheme for {url!r}")
        
        req = urllib.request.Request(  # noqa: S310 - curated domains
            url,
            headers={"User-Agent": self.user_agent},
            method="GET",
        )
        
        last_exc: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req) as response:  # noqa: S310 - curated domains
                    content = response.read()
                    headers = dict(response.headers)
                    return content, headers
            except Exception as exc:  # pragma: no cover - network failures
                last_exc = exc
                logger.warning(f"Fetch attempt {attempt + 1}/{self.retries} failed for {url}: {exc}")
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
            logger.debug(f"Article not in cache: {url}")
            return True
        
        cached = self._cache[url]
        
        # Check ETag if available
        etag = headers.get("ETag") or headers.get("etag")
        if etag and cached.etag and etag == cached.etag:
            logger.debug(f"ETag match, skipping: {url}")
            return False
        
        # Check Last-Modified if available
        last_modified = headers.get("Last-Modified") or headers.get("last-modified")
        if last_modified and cached.last_modified:
            try:
                # Simple string comparison works for HTTP date format
                if last_modified <= cached.last_modified:
                    logger.debug(f"Not modified since last fetch: {url}")
                    return False
            except (ValueError, TypeError):
                pass  # If comparison fails, fetch to be safe
        
        # Default to fetching if we can't determine
        logger.debug(f"No cache hit or stale, will fetch: {url}")
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
                            logger.info(f"[DRY-RUN] Would check: {section}/{bucket}: {url}")
                            checked += 1
                            continue
                        
                        # Fetch with headers for change detection
                        logger.info(f"Checking: {section}/{bucket}: {url}")
                        content, headers = self._fetch(url)
                        checked += 1
                        
                        # Determine if update is needed
                        needs_update = force or self._should_update(url, headers)
                        
                        if not needs_update:
                            skipped += 1
                            logger.info(f"Skipped (up-to-date): {url}")
                            continue
                        
                        # PII Scrubbing (MANDATORY before disk write)
                        scrubbed_content, pii_flags = scrub_pii(content.decode('utf-8') if isinstance(content, bytes) else content)
                        if any(pii_flags.values()):
                            logger.warning(f"PII detected and scrubbed in {url}: {pii_flags}")
                        
                        # Phase 2: Pull (write to disk with scrubbed content)
                        output_path = self._write_article(
                            outdir / section / bucket,
                            url,
                            scrubbed_content.encode('utf-8')
                        )
                        logger.info(f"Updated: {output_path}")
                        
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
                        
                    except Exception as e:
                        logger.error(f"Failed to sync {url}: {e}")
                        failed += 1
        
        # Save updated cache
        if not dry_run and updated > 0:
            self._save_cache()
        
        result = SyncResult(
            total_articles=total,
            checked=checked,
            updated=updated,
            failed=failed,
            skipped=skipped,
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
        )
        
        logger.info(
            f"Sync complete: {result.total_articles} total, "
            f"{result.checked} checked, {result.updated} updated, "
            f"{result.failed} failed, {result.skipped} skipped"
        )
        
        return result
    
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
            sync_dirs = sorted(
                [d for d in self.output_root.iterdir() if d.is_dir()],
                reverse=True
            )
            if not sync_dirs:
                raise ValueError("No synchronized documentation found")
            source_dir = sync_dirs[0]
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        logger.info(f"Pipelining content from {source_dir} to codex_digest")
        
        # Count files to process
        html_files = list(source_dir.rglob("*.html"))
        
        # TODO: Integrate with codex_digest pipeline
        # For now, return metadata about what would be processed
        result = {
            "source_dir": str(source_dir),
            "files_found": len(html_files),
            "status": "ready_for_tokenization",
            "next_step": "Integrate with codex_digest.pipeline.process()",
        }
        
        logger.info(f"Pipeline preparation complete: {len(html_files)} files ready")
        return result


def main() -> int:
    """CLI entry point for the sync service."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Zendesk Knowledge Synchronization Service"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not download; only report what would be done",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force fetch all articles, ignoring cache",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Pipeline synced content to codex_digest after sync",
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
        result = service.check_and_pull(
            dry_run=args.dry_run,
            force=args.force,
        )
        
        print(f"\n{'='*60}")
        print("Synchronization Results:")
        print(f"{'='*60}")
        print(f"Total Articles:    {result.total_articles}")
        print(f"Checked:           {result.checked}")
        print(f"Updated:           {result.updated}")
        print(f"Failed:            {result.failed}")
        print(f"Skipped:           {result.skipped}")
        print(f"Timestamp:         {result.timestamp}")
        print(f"{'='*60}\n")
        
        # Pipeline if requested
        if args.pipeline and not args.dry_run and result.updated > 0:
            logger.info("Starting pipeline to codex_digest...")
            pipeline_result = service.pipeline_to_codex_digest()
            print(f"Pipeline Result: {json.dumps(pipeline_result, indent=2)}")
        
        return 0 if result.failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
