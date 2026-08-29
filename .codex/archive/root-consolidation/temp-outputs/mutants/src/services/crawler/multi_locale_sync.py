"""Multi-Locale Synchronization for Knowledge Crawler.

PS-06 Enhancement: Implements parallel sync for different locales:
- Parallel sync for different locales
- Locale-aware scheduling
- Locale priority configuration

This module extends the Knowledge Crawler Service with
multi-locale support for international knowledge bases.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LocaleConfig:
    """Configuration for a specific locale."""

    locale_code: str  # e.g., "en-us", "ja", "de"
    priority: int = 1  # Higher = synced first
    enabled: bool = True
    sync_interval_hours: int = 24
    last_sync: Optional[datetime] = None
    article_count: int = 0

    def needs_sync(self) -> bool:
        """Check if locale needs synchronization."""
        if not self.enabled:
            return False
        if self.last_sync is None:
            return True

        hours_since_sync = (datetime.now(timezone.utc) - self.last_sync).total_seconds() / 3600
        return hours_since_sync >= self.sync_interval_hours


@dataclass
class LocaleSyncResult:
    """Result of syncing a single locale."""

    locale_code: str
    success: bool
    articles_synced: int = 0
    articles_failed: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "locale_code": self.locale_code,
            "success": self.success,
            "articles_synced": self.articles_synced,
            "articles_failed": self.articles_failed,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MultiLocaleSyncResult:
    """Aggregated result of multi-locale sync."""

    total_locales: int
    successful_locales: int
    failed_locales: int
    total_articles_synced: int
    total_duration_seconds: float
    locale_results: list[LocaleSyncResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_locales": self.total_locales,
            "successful_locales": self.successful_locales,
            "failed_locales": self.failed_locales,
            "total_articles_synced": self.total_articles_synced,
            "total_duration_seconds": self.total_duration_seconds,
            "locale_results": [r.to_dict() for r in self.locale_results],
        }


class MultiLocaleSyncManager:
    """Manager for parallel synchronization across multiple locales.

    Features:
    - Parallel execution using ThreadPoolExecutor
    - Priority-based scheduling
    - Locale-aware sync intervals
    - Aggregated results and logging
    """

    # Common Zendesk locales
    DEFAULT_LOCALES = [
        LocaleConfig("en-us", priority=10),
        LocaleConfig("ja", priority=8),
        LocaleConfig("de", priority=7),
        LocaleConfig("fr", priority=7),
        LocaleConfig("es", priority=6),
        LocaleConfig("pt-br", priority=5),
        LocaleConfig("zh-cn", priority=5),
        LocaleConfig("ko", priority=4),
    ]

    def __init__(
        self,
        max_workers: int = 4,
        locales: Optional[list[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.

        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def add_locale(self, locale: LocaleConfig) -> None:
        """Add a locale to the sync manager."""
        self.locales[locale.locale_code] = locale
        logger.info(f"Added locale: {locale.locale_code} (priority={locale.priority})")

    def remove_locale(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            logger.info(f"Removed locale: {locale_code}")
            return True
        return False

    def get_sync_schedule(self) -> list[dict[str, Any]]:
        """Get the sync schedule for all locales.

        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append(
                {
                    "locale_code": locale.locale_code,
                    "priority": locale.priority,
                    "enabled": locale.enabled,
                    "needs_sync": locale.needs_sync(),
                    "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                    "sync_interval_hours": locale.sync_interval_hours,
                }
            )
        return schedule

    def sync_locale(
        self,
        locale_code: str,
        sync_func: Callable[[str], tuple[int, int]],
    ) -> LocaleSyncResult:
        """Synchronize a single locale.

        Args:
            locale_code: Locale to sync
            sync_func: Function that takes locale_code and returns (synced, failed)

        Returns:
            LocaleSyncResult with sync statistics
        """
        if locale_code not in self.locales:
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                error_message=f"Locale not configured: {locale_code}",
            )

        locale = self.locales[locale_code]
        if not locale.enabled:
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                error_message="Locale is disabled",
            )

        start_time = time.time()

        try:
            logger.info(f"Starting sync for locale: {locale_code}")
            synced, failed = sync_func(locale_code)
            duration = time.time() - start_time

            # Update locale metadata
            locale.last_sync = datetime.now(timezone.utc)
            locale.article_count = synced

            result = LocaleSyncResult(
                locale_code=locale_code,
                success=True,
                articles_synced=synced,
                articles_failed=failed,
                duration_seconds=duration,
            )

            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result

        except (ValueError, TypeError, RuntimeError) as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: <ERROR_TYPE>")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )

    def sync_all_locales(
        self,
        sync_func: Callable[[str], tuple[int, int]],
        only_due: bool = True,
    ) -> MultiLocaleSyncResult:
        """Synchronize all locales in parallel.

        Args:
            sync_func: Function that takes locale_code and returns (synced, failed)
            only_due: If True, only sync locales that need syncing

        Returns:
            MultiLocaleSyncResult with aggregated statistics
        """
        start_time = time.time()

        # Get locales to sync, sorted by priority
        locales_to_sync = sorted(
            [loc for loc in self.locales.values() if loc.enabled],
            key=lambda x: -x.priority,
        )

        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]

        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=0,
                total_articles_synced=0,
                total_duration_seconds=0,
            )

        logger.info(f"Starting parallel sync for {len(locales_to_sync)} locales")

        # Submit all sync tasks
        futures = {}
        for locale in locales_to_sync:
            future = self._executor.submit(
                self.sync_locale,
                locale.locale_code,
                sync_func,
            )
            futures[future] = locale.locale_code

        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=3600)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(
                    LocaleSyncResult(
                        locale_code=locale_code,
                        success=False,
                        error_message=f"Execution error: {e}",
                    )
                )

        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)

        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            failed_locales=failed,
            total_articles_synced=total_synced,
            total_duration_seconds=total_duration,
            locale_results=results,
        )

        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )

        return aggregate

    async def sync_all_locales_async(
        self,
        sync_func: Callable[[str], tuple[int, int]],
        only_due: bool = True,
    ) -> MultiLocaleSyncResult:
        """Async version of sync_all_locales for integration with async code.

        Args:
            sync_func: Function that takes locale_code and returns (synced, failed)
            only_due: If True, only sync locales that need syncing

        Returns:
            MultiLocaleSyncResult with aggregated statistics
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.sync_all_locales(sync_func, only_due),
        )

    def shutdown(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info("MultiLocaleSyncManager shutdown complete")


__all__ = [
    "LocaleConfig",
    "LocaleSyncResult",
    "MultiLocaleSyncManager",
    "MultiLocaleSyncResult",
]
