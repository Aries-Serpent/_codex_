"""Knowledge synchronization crawler services.

This module provides services to synchronize Agent knowledge bases
with SaaS Knowledge Centers using a "Check and Pull" mechanism.

PS-06 Enhancement: Includes multi-locale sync and content diffing.
"""

from __future__ import annotations

__all__ = [
    "ZendeskKnowledgeSyncService",
    "MultiLocaleSyncManager",
    "LocaleConfig",
    "ContentDiffer",
    "IncrementalSyncDecider",
]

try:
    from src.services.crawler.zendesk_sync import ZendeskKnowledgeSyncService
except ImportError:
    from services.crawler.zendesk_sync import ZendeskKnowledgeSyncService

try:
    from src.services.crawler.multi_locale_sync import MultiLocaleSyncManager, LocaleConfig
except ImportError:
    from services.crawler.multi_locale_sync import MultiLocaleSyncManager, LocaleConfig

try:
    from src.services.crawler.content_diff import ContentDiffer, IncrementalSyncDecider
except ImportError:
    from services.crawler.content_diff import ContentDiffer, IncrementalSyncDecider
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
