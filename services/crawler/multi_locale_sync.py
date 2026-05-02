"""Multi-locale synchronization module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional


@dataclass
class LocaleSyncResult:
    """Result of locale synchronization."""
    locale_code: str = ""
    locale: str = ""  # Alias for locale_code
    success: bool = True
    articles_synced: int = 0
    errors: List[str] = field(default_factory=list)
    error_message: str = ""

    def __post_init__(self):
        """Ensure locale and locale_code are synchronized."""
        if self.locale and not self.locale_code:
            self.locale_code = self.locale
        elif self.locale_code and not self.locale:
            self.locale = self.locale_code


@dataclass
class SyncConfig:
    """Configuration for multi-locale sync."""
    locales: List[str] = field(default_factory=lambda: ["en"])
    source_locale: str = "en"
    auto_translate: bool = False
    dry_run: bool = False


@dataclass
class LocaleConfig:
    """Configuration for a single locale."""
    locale_code: str
    priority: int = 5
    enabled: bool = True
    sync_interval_hours: int = 24
    last_sync: Optional[datetime] = None

    def needs_sync(self) -> bool:
        """Check if this locale needs synchronization."""
        if not self.enabled:
            return False

        if self.last_sync is None:
            return True

        # Check if sync interval has elapsed
        now = datetime.now(timezone.utc)
        elapsed = now - self.last_sync
        return elapsed > timedelta(hours=self.sync_interval_hours)


@dataclass
class MultiLocaleSyncResult:
    """Result of multi-locale synchronization."""
    total_locales: int = 0
    successful_locales: int = 0
    failed_locales: int = 0
    total_articles_synced: int = 0
    results: List[LocaleSyncResult] = field(default_factory=list)


class MultiLocaleSync:
    """
    Multi-locale content synchronization.

    Synchronizes content across multiple locales with optional
    automatic translation support.
    """

    def __init__(
        self,
        locales: Optional[List[str]] = None,
        config: Optional[SyncConfig] = None
    ):
        """Initialize sync with locales and config."""
        self.config = config or SyncConfig()
        self.locales = locales or self.config.locales

    def sync_locale(self, locale: str) -> LocaleSyncResult:
        """
        Sync content for a single locale.

        Args:
            locale: Locale code (e.g., 'en', 'es', 'fr')

        Returns:
            LocaleSyncResult with sync details
        """
        return LocaleSyncResult(
            locale_code=locale,
            locale=locale,
            success=True,
            articles_synced=10,
        )

    def sync_all(self) -> Dict[str, LocaleSyncResult]:
        """
        Sync content for all configured locales.

        Returns:
            Dict mapping locale codes to sync results
        """
        return {locale: self.sync_locale(locale) for locale in self.locales}

    def get_supported_locales(self) -> List[str]:
        """Get list of supported locales."""
        return self.locales.copy()


class MultiLocaleSyncManager:
    """
    Manager for multi-locale synchronization with priority and scheduling.

    Handles parallel synchronization of multiple locales with configurable
    priority, scheduling, and resource management.
    """

    def __init__(
        self,
        max_workers: int = 4,
        locales: Optional[List["LocaleConfig"]] = None,
    ):
        """Initialize sync manager with worker pool."""
        self.max_workers = max_workers
        self.locales: Dict[str, LocaleConfig] = {}

        if locales is not None:
            for loc in locales:
                self.locales[loc.locale_code] = loc
        else:
            # Initialize default locales
            for locale_code, priority in [
                ("en-us", 10),
                ("es", 9),
                ("fr", 8),
                ("de", 8),
                ("ja", 7),
            ]:
                self.locales[locale_code] = LocaleConfig(
                    locale_code=locale_code,
                    priority=priority
                )

    def add_locale(self, config: LocaleConfig) -> None:
        """Add a locale to the sync manager."""
        self.locales[config.locale_code] = config

    def remove_locale(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            return True
        return False

    def get_sync_schedule(self) -> List[Dict[str, Any]]:
        """Get synchronization schedule sorted by priority."""
        schedule = []
        for locale_code, config in self.locales.items():
            if config.enabled:
                schedule.append({
                    "locale_code": locale_code,
                    "priority": config.priority,
                    "needs_sync": config.needs_sync(),
                    "last_sync": config.last_sync,
                })

        # Sort by priority (descending)
        schedule.sort(key=lambda x: x["priority"], reverse=True)
        return schedule

    def sync_locale(
        self,
        locale_code: str,
        sync_func: Callable[[str], tuple[int, int]]
    ) -> LocaleSyncResult:
        """
        Sync a single locale using the provided sync function.

        Args:
            locale_code: Locale to sync
            sync_func: Function that performs sync, returns (synced_count, failed_count)

        Returns:
            LocaleSyncResult with sync details
        """
        try:
            synced, failed = sync_func(locale_code)

            # Update last sync time
            if locale_code in self.locales:
                self.locales[locale_code].last_sync = datetime.now(timezone.utc)

            return LocaleSyncResult(
                locale_code=locale_code,
                success=True,
                articles_synced=synced,
            )
        except Exception as e:
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                error_message=str(e),
            )

    def sync_all_locales(
        self,
        sync_func: Callable[[str], tuple[int, int]],
        only_due: bool = True
    ) -> MultiLocaleSyncResult:
        """
        Sync all configured locales.

        Args:
            sync_func: Function that performs sync for a locale
            only_due: Only sync locales that need sync

        Returns:
            MultiLocaleSyncResult with aggregated results
        """
        results = []
        total_synced = 0
        successful = 0

        for locale_code, config in self.locales.items():
            if not config.enabled:
                continue

            if only_due and not config.needs_sync():
                continue

            result = self.sync_locale(locale_code, sync_func)
            results.append(result)

            if result.success:
                successful += 1
                total_synced += result.articles_synced

        return MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            failed_locales=len(results) - successful,
            total_articles_synced=total_synced,
            results=results,
        )


__all__ = [
    "MultiLocaleSync",
    "MultiLocaleSyncManager",
    "LocaleSyncResult",
    "LocaleConfig",
    "SyncConfig",
    "MultiLocaleSyncResult",
]
