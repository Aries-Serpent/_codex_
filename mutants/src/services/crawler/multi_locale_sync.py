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
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
    
    def to_dict(self) -> Dict[str, Any]:
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
    locale_results: List[LocaleSyncResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
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
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_orig(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_1(
        self,
        max_workers: int = 5,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_2(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = None
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_3(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = None
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_4(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales and self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_5(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = None
    
    def xǁMultiLocaleSyncManagerǁ__init____mutmut_6(
        self,
        max_workers: int = 4,
        locales: Optional[List[LocaleConfig]] = None,
    ):
        """Initialize the multi-locale sync manager.
        
        Args:
            max_workers: Maximum parallel sync threads
            locales: List of locale configurations (defaults to common locales)
        """
        self.max_workers = max_workers
        self.locales = {loc.locale_code: loc for loc in (locales or self.DEFAULT_LOCALES)}
        self._executor = ThreadPoolExecutor(max_workers=None)
    
    xǁMultiLocaleSyncManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁ__init____mutmut_1': xǁMultiLocaleSyncManagerǁ__init____mutmut_1, 
        'xǁMultiLocaleSyncManagerǁ__init____mutmut_2': xǁMultiLocaleSyncManagerǁ__init____mutmut_2, 
        'xǁMultiLocaleSyncManagerǁ__init____mutmut_3': xǁMultiLocaleSyncManagerǁ__init____mutmut_3, 
        'xǁMultiLocaleSyncManagerǁ__init____mutmut_4': xǁMultiLocaleSyncManagerǁ__init____mutmut_4, 
        'xǁMultiLocaleSyncManagerǁ__init____mutmut_5': xǁMultiLocaleSyncManagerǁ__init____mutmut_5, 
        'xǁMultiLocaleSyncManagerǁ__init____mutmut_6': xǁMultiLocaleSyncManagerǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁ__init____mutmut_orig)
    xǁMultiLocaleSyncManagerǁ__init____mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁ__init__'
    
    def xǁMultiLocaleSyncManagerǁadd_locale__mutmut_orig(self, locale: LocaleConfig) -> None:
        """Add a locale to the sync manager."""
        self.locales[locale.locale_code] = locale
        logger.info(f"Added locale: {locale.locale_code} (priority={locale.priority})")
    
    def xǁMultiLocaleSyncManagerǁadd_locale__mutmut_1(self, locale: LocaleConfig) -> None:
        """Add a locale to the sync manager."""
        self.locales[locale.locale_code] = None
        logger.info(f"Added locale: {locale.locale_code} (priority={locale.priority})")
    
    def xǁMultiLocaleSyncManagerǁadd_locale__mutmut_2(self, locale: LocaleConfig) -> None:
        """Add a locale to the sync manager."""
        self.locales[locale.locale_code] = locale
        logger.info(None)
    
    xǁMultiLocaleSyncManagerǁadd_locale__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁadd_locale__mutmut_1': xǁMultiLocaleSyncManagerǁadd_locale__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁadd_locale__mutmut_2': xǁMultiLocaleSyncManagerǁadd_locale__mutmut_2
    }
    
    def add_locale(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁadd_locale__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁadd_locale__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_locale.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁadd_locale__mutmut_orig)
    xǁMultiLocaleSyncManagerǁadd_locale__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁadd_locale'
    
    def xǁMultiLocaleSyncManagerǁremove_locale__mutmut_orig(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            logger.info(f"Removed locale: {locale_code}")
            return True
        return False
    
    def xǁMultiLocaleSyncManagerǁremove_locale__mutmut_1(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code not in self.locales:
            del self.locales[locale_code]
            logger.info(f"Removed locale: {locale_code}")
            return True
        return False
    
    def xǁMultiLocaleSyncManagerǁremove_locale__mutmut_2(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            logger.info(None)
            return True
        return False
    
    def xǁMultiLocaleSyncManagerǁremove_locale__mutmut_3(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            logger.info(f"Removed locale: {locale_code}")
            return False
        return False
    
    def xǁMultiLocaleSyncManagerǁremove_locale__mutmut_4(self, locale_code: str) -> bool:
        """Remove a locale from the sync manager."""
        if locale_code in self.locales:
            del self.locales[locale_code]
            logger.info(f"Removed locale: {locale_code}")
            return True
        return True
    
    xǁMultiLocaleSyncManagerǁremove_locale__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁremove_locale__mutmut_1': xǁMultiLocaleSyncManagerǁremove_locale__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁremove_locale__mutmut_2': xǁMultiLocaleSyncManagerǁremove_locale__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁremove_locale__mutmut_3': xǁMultiLocaleSyncManagerǁremove_locale__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁremove_locale__mutmut_4': xǁMultiLocaleSyncManagerǁremove_locale__mutmut_4
    }
    
    def remove_locale(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁremove_locale__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁremove_locale__mutmut_mutants"), args, kwargs, self)
        return result 
    
    remove_locale.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁremove_locale__mutmut_orig)
    xǁMultiLocaleSyncManagerǁremove_locale__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁremove_locale'
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_orig(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_1(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = None
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_2(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(None, key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_3(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=None):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_4(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_5(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), ):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_6(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: None):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_7(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: +x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_8(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append(None)
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_9(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "XXlocale_codeXX": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_10(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "LOCALE_CODE": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_11(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "XXpriorityXX": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_12(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "PRIORITY": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_13(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "XXenabledXX": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_14(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "ENABLED": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_15(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "XXneeds_syncXX": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_16(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "NEEDS_SYNC": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_17(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "XXlast_syncXX": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_18(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "LAST_SYNC": locale.last_sync.isoformat() if locale.last_sync else None,
                "sync_interval_hours": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_19(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "XXsync_interval_hoursXX": locale.sync_interval_hours,
            })
        return schedule
    
    def xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_20(self) -> List[Dict[str, Any]]:
        """Get the sync schedule for all locales.
        
        Returns:
            List of locale sync schedules sorted by priority
        """
        schedule = []
        for locale in sorted(self.locales.values(), key=lambda x: -x.priority):
            schedule.append({
                "locale_code": locale.locale_code,
                "priority": locale.priority,
                "enabled": locale.enabled,
                "needs_sync": locale.needs_sync(),
                "last_sync": locale.last_sync.isoformat() if locale.last_sync else None,
                "SYNC_INTERVAL_HOURS": locale.sync_interval_hours,
            })
        return schedule
    
    xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_1': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_2': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_3': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_4': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_4, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_5': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_5, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_6': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_6, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_7': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_7, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_8': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_8, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_9': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_9, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_10': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_10, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_11': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_11, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_12': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_12, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_13': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_13, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_14': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_14, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_15': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_15, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_16': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_16, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_17': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_17, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_18': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_18, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_19': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_19, 
        'xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_20': xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_20
    }
    
    def get_sync_schedule(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_sync_schedule.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_orig)
    xǁMultiLocaleSyncManagerǁget_sync_schedule__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁget_sync_schedule'
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_orig(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_1(
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
        if locale_code in self.locales:
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_2(
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
                locale_code=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_3(
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
                success=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_4(
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
                error_message=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_5(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_6(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_7(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_8(
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
                success=True,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_9(
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
        
        locale = None
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_10(
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
        if locale.enabled:
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_11(
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
                locale_code=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_12(
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
                success=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_13(
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
                error_message=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_14(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_15(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_16(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_17(
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
                success=True,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_18(
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
                error_message="XXLocale is disabledXX",
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_19(
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
                error_message="locale is disabled",
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_20(
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
                error_message="LOCALE IS DISABLED",
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_21(
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
        
        start_time = None
        
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_22(
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
            logger.info(None)
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_23(
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
            synced, failed = None
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_24(
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
            synced, failed = sync_func(None)
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_25(
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
            duration = None
            
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_26(
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
            duration = time.time() + start_time
            
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_27(
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
            locale.last_sync = None
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_28(
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
            locale.last_sync = datetime.now(None)
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_29(
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
            locale.article_count = None
            
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_30(
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
            
            result = None
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_31(
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
                locale_code=None,
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_32(
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
                success=None,
                articles_synced=synced,
                articles_failed=failed,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_33(
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
                articles_synced=None,
                articles_failed=failed,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_34(
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
                articles_failed=None,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_35(
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
                duration_seconds=None,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_36(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_37(
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
                articles_synced=synced,
                articles_failed=failed,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_38(
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
                articles_failed=failed,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_39(
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
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_40(
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
                )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_41(
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
                success=False,
                articles_synced=synced,
                articles_failed=failed,
                duration_seconds=duration,
            )
            
            logger.info(
                f"Completed sync for {locale_code}: "
                f"{synced} synced, {failed} failed in {duration:.2f}s"
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_42(
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
                None
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_43(
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
            
        except Exception as e:
            duration = None
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_44(
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
            
        except Exception as e:
            duration = time.time() + start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_45(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(None)
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_46(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=None,
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_47(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=None,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_48(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=None,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_49(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=None,
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_50(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                success=False,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_51(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_52(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_53(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_54(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=True,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    def xǁMultiLocaleSyncManagerǁsync_locale__mutmut_55(
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
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to sync locale {locale_code}: {e}")
            return LocaleSyncResult(
                locale_code=locale_code,
                success=False,
                duration_seconds=duration,
                error_message=str(None),
            )
    
    xǁMultiLocaleSyncManagerǁsync_locale__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_1': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_2': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_3': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_4': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_4, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_5': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_5, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_6': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_6, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_7': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_7, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_8': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_8, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_9': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_9, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_10': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_10, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_11': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_11, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_12': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_12, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_13': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_13, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_14': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_14, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_15': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_15, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_16': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_16, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_17': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_17, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_18': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_18, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_19': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_19, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_20': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_20, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_21': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_21, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_22': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_22, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_23': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_23, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_24': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_24, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_25': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_25, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_26': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_26, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_27': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_27, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_28': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_28, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_29': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_29, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_30': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_30, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_31': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_31, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_32': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_32, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_33': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_33, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_34': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_34, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_35': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_35, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_36': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_36, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_37': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_37, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_38': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_38, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_39': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_39, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_40': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_40, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_41': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_41, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_42': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_42, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_43': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_43, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_44': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_44, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_45': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_45, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_46': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_46, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_47': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_47, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_48': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_48, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_49': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_49, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_50': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_50, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_51': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_51, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_52': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_52, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_53': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_53, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_54': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_54, 
        'xǁMultiLocaleSyncManagerǁsync_locale__mutmut_55': xǁMultiLocaleSyncManagerǁsync_locale__mutmut_55
    }
    
    def sync_locale(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_locale__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_locale__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sync_locale.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁsync_locale__mutmut_orig)
    xǁMultiLocaleSyncManagerǁsync_locale__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁsync_locale'
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_orig(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_1(
        self,
        sync_func: Callable[[str], tuple[int, int]],
        only_due: bool = False,
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_2(
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
        start_time = None
        
        # Get locales to sync, sorted by priority
        locales_to_sync = sorted(
            [loc for loc in self.locales.values() if loc.enabled],
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_3(
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
        locales_to_sync = None
        
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_4(
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
            None,
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_5(
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
            key=None
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_6(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_7(
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_8(
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
            key=lambda x: None
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_9(
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
            key=lambda x: +x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_10(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = None
        
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_11(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if locales_to_sync:
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_12(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info(None)
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_13(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("XXNo locales need syncingXX")
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_14(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("no locales need syncing")
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_15(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("NO LOCALES NEED SYNCING")
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_16(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_17(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_18(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_19(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=0,
                total_articles_synced=None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_20(
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
            key=lambda x: -x.priority
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
                total_duration_seconds=None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_21(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_22(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_23(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_24(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=0,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_25(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_26(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=1,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_27(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=1,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_28(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=1,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_29(
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
            key=lambda x: -x.priority
        )
        
        if only_due:
            locales_to_sync = [loc for loc in locales_to_sync if loc.needs_sync()]
        
        if not locales_to_sync:
            logger.info("No locales need syncing")
            return MultiLocaleSyncResult(
                total_locales=0,
                successful_locales=0,
                failed_locales=0,
                total_articles_synced=1,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_30(
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
            key=lambda x: -x.priority
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
                total_duration_seconds=1,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_31(
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
            key=lambda x: -x.priority
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
        
        logger.info(None)
        
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_32(
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
            key=lambda x: -x.priority
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
        futures = None
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_33(
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
            key=lambda x: -x.priority
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
            future = None
            futures[future] = locale.locale_code
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=3600)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_34(
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
            key=lambda x: -x.priority
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
                None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_35(
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
            key=lambda x: -x.priority
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
                None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_36(
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
            key=lambda x: -x.priority
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
                None,
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_37(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_38(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_39(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_40(
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
            key=lambda x: -x.priority
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
            futures[future] = None
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=3600)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_41(
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
            key=lambda x: -x.priority
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
        results = None
        for future in futures:
            try:
                result = future.result(timeout=3600)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_42(
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
            key=lambda x: -x.priority
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
                result = None  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_43(
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
            key=lambda x: -x.priority
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
                result = future.result(timeout=None)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_44(
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
            key=lambda x: -x.priority
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
                result = future.result(timeout=3601)  # 1 hour timeout per locale
                results.append(result)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_45(
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
            key=lambda x: -x.priority
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
                results.append(None)
            except Exception as e:
                locale_code = futures[future]
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_46(
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
            key=lambda x: -x.priority
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
                locale_code = None
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_47(
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
            key=lambda x: -x.priority
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
                results.append(None)
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_48(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=None,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_49(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=None,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_50(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=None,
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_51(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_52(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_53(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_54(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=True,
                    error_message=f"Execution error: {e}",
                ))
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_55(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = None
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_56(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() + start_time
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_57(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = None
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_58(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(None)
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_59(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(2 for r in results if r.success)
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_60(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = None
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_61(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) + successful
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_62(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = None
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_63(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(None)
        
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_64(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = None
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_65(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=None,
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_66(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=None,
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_67(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            failed_locales=None,
            total_articles_synced=total_synced,
            total_duration_seconds=total_duration,
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_68(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            failed_locales=failed,
            total_articles_synced=None,
            total_duration_seconds=total_duration,
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_69(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
            total_duration_seconds=None,
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_70(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
            locale_results=None,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_71(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_72(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
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
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_73(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            total_articles_synced=total_synced,
            total_duration_seconds=total_duration,
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_74(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
        # Aggregate results
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_synced = sum(r.articles_synced for r in results)
        
        aggregate = MultiLocaleSyncResult(
            total_locales=len(results),
            successful_locales=successful,
            failed_locales=failed,
            total_duration_seconds=total_duration,
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_75(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
            locale_results=results,
        )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_76(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
            )
        
        logger.info(
            f"Multi-locale sync complete: {successful}/{len(results)} locales, "
            f"{total_synced} articles in {total_duration:.2f}s"
        )
        
        return aggregate
    
    def xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_77(
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
            key=lambda x: -x.priority
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
                results.append(LocaleSyncResult(
                    locale_code=locale_code,
                    success=False,
                    error_message=f"Execution error: {e}",
                ))
        
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
            None
        )
        
        return aggregate
    
    xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_1': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_2': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_3': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_4': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_4, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_5': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_5, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_6': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_6, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_7': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_7, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_8': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_8, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_9': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_9, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_10': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_10, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_11': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_11, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_12': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_12, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_13': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_13, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_14': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_14, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_15': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_15, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_16': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_16, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_17': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_17, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_18': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_18, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_19': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_19, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_20': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_20, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_21': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_21, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_22': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_22, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_23': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_23, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_24': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_24, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_25': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_25, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_26': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_26, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_27': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_27, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_28': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_28, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_29': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_29, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_30': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_30, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_31': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_31, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_32': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_32, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_33': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_33, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_34': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_34, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_35': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_35, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_36': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_36, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_37': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_37, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_38': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_38, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_39': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_39, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_40': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_40, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_41': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_41, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_42': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_42, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_43': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_43, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_44': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_44, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_45': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_45, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_46': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_46, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_47': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_47, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_48': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_48, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_49': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_49, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_50': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_50, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_51': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_51, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_52': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_52, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_53': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_53, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_54': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_54, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_55': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_55, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_56': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_56, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_57': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_57, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_58': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_58, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_59': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_59, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_60': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_60, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_61': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_61, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_62': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_62, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_63': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_63, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_64': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_64, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_65': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_65, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_66': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_66, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_67': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_67, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_68': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_68, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_69': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_69, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_70': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_70, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_71': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_71, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_72': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_72, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_73': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_73, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_74': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_74, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_75': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_75, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_76': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_76, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_77': xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_77
    }
    
    def sync_all_locales(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sync_all_locales.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_orig)
    xǁMultiLocaleSyncManagerǁsync_all_locales__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁsync_all_locales'
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_orig(
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
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_1(
        self,
        sync_func: Callable[[str], tuple[int, int]],
        only_due: bool = False,
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
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_2(
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
        loop = None
        return await loop.run_in_executor(
            None,
            lambda: self.sync_all_locales(sync_func, only_due),
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_3(
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
            None,
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_4(
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
            lambda: self.sync_all_locales(sync_func, only_due),
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_5(
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
            )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_6(
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
            lambda: None,
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_7(
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
            lambda: self.sync_all_locales(None, only_due),
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_8(
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
            lambda: self.sync_all_locales(sync_func, None),
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_9(
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
            lambda: self.sync_all_locales(only_due),
        )
    
    async def xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_10(
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
            lambda: self.sync_all_locales(sync_func, ),
        )
    
    xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_1': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_2': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_3': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_4': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_4, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_5': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_5, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_6': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_6, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_7': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_7, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_8': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_8, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_9': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_9, 
        'xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_10': xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_10
    }
    
    def sync_all_locales_async(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_mutants"), args, kwargs, self)
        return result 
    
    sync_all_locales_async.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_orig)
    xǁMultiLocaleSyncManagerǁsync_all_locales_async__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁsync_all_locales_async'
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_orig(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info("MultiLocaleSyncManager shutdown complete")
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_1(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=None)
        logger.info("MultiLocaleSyncManager shutdown complete")
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_2(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=False)
        logger.info("MultiLocaleSyncManager shutdown complete")
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_3(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info(None)
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_4(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info("XXMultiLocaleSyncManager shutdown completeXX")
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_5(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info("multilocalesyncmanager shutdown complete")
    
    def xǁMultiLocaleSyncManagerǁshutdown__mutmut_6(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
        logger.info("MULTILOCALESYNCMANAGER SHUTDOWN COMPLETE")
    
    xǁMultiLocaleSyncManagerǁshutdown__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMultiLocaleSyncManagerǁshutdown__mutmut_1': xǁMultiLocaleSyncManagerǁshutdown__mutmut_1, 
        'xǁMultiLocaleSyncManagerǁshutdown__mutmut_2': xǁMultiLocaleSyncManagerǁshutdown__mutmut_2, 
        'xǁMultiLocaleSyncManagerǁshutdown__mutmut_3': xǁMultiLocaleSyncManagerǁshutdown__mutmut_3, 
        'xǁMultiLocaleSyncManagerǁshutdown__mutmut_4': xǁMultiLocaleSyncManagerǁshutdown__mutmut_4, 
        'xǁMultiLocaleSyncManagerǁshutdown__mutmut_5': xǁMultiLocaleSyncManagerǁshutdown__mutmut_5, 
        'xǁMultiLocaleSyncManagerǁshutdown__mutmut_6': xǁMultiLocaleSyncManagerǁshutdown__mutmut_6
    }
    
    def shutdown(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁshutdown__mutmut_orig"), object.__getattribute__(self, "xǁMultiLocaleSyncManagerǁshutdown__mutmut_mutants"), args, kwargs, self)
        return result 
    
    shutdown.__signature__ = _mutmut_signature(xǁMultiLocaleSyncManagerǁshutdown__mutmut_orig)
    xǁMultiLocaleSyncManagerǁshutdown__mutmut_orig.__name__ = 'xǁMultiLocaleSyncManagerǁshutdown'


__all__ = [
    "LocaleConfig",
    "LocaleSyncResult",
    "MultiLocaleSyncResult",
    "MultiLocaleSyncManager",
]
