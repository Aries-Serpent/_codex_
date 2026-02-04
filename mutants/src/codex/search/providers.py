"""Pluggable search providers used by codex.

This module supplies a minimal plugin architecture with a registry that can
combine multiple search backends. It is intentionally lightweight so that new
providers can be added without altering existing code. The implementation
follows the repurpose/enhance/fallback strategy: each provider gracefully
handles errors and returns an empty list on failure.
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

import abc
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from tools.security import net
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


class SearchProvider(abc.ABC):
    """Abstract base class for search providers."""

    @abc.abstractmethod
    def search(self, query: str) -> list[dict[str, Any]]:
        """Search for *query* and return a list of results."""


@dataclass
class InternalRepoSearch(SearchProvider):
    """Ripgrep-backed search inside the repository.

    Parameters
    ----------
    root:
        Directory to search. Defaults to the current working directory.
    """

    root: Path = Path.cwd()

    def search(self, query: str) -> list[dict[str, Any]]:
        try:
            completed = subprocess.run(
                ["rg", "--json", query, str(self.root)],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return []

        results: list[dict[str, Any]] = []
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                logger.debug("Exception caught, continuing", exc_info=True)
                continue
            if event.get("type") == "match":
                data = event.get("data", {})
                path = data.get("path", {}).get("text")
                line_text = data.get("lines", {}).get("text", "").rstrip("\n")
                if path:
                    results.append({"path": path, "line": line_text})
        return results


@dataclass
class ExternalWebSearch(SearchProvider):
    """Best-effort web search provider using DuckDuckGo.

    Network failures are caught and surfaced as an empty result set, allowing
    the rest of the system to continue operating.
    """

    def search(self, query: str) -> list[dict[str, Any]]:
        import urllib.error
        import urllib.parse

        url = (
            "https://duckduckgo.com/?q="
            + urllib.parse.quote(query)
            + "&format=json&no_redirect=1&no_html=1"
        )
        try:
            payload = net.safe_fetch(url, timeout=10)
            data = json.loads(payload.decode("utf-8"))
        except (urllib.error.URLError, ValueError, OSError):
            logger.debug("Exception caught, returning", exc_info=True)
            return []

        results: list[dict[str, Any]] = []
        for topic in data.get("RelatedTopics", []):
            if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                results.append({"text": topic["Text"], "url": topic["FirstURL"]})
        return results


class SearchRegistry:
    """Registry aggregating search providers."""

    def xǁSearchRegistryǁ__init____mutmut_orig(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = [InternalRepoSearch(root=root or Path.cwd())]
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def xǁSearchRegistryǁ__init____mutmut_1(self, enable_external: bool = True, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = [InternalRepoSearch(root=root or Path.cwd())]
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def xǁSearchRegistryǁ__init____mutmut_2(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = None
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def xǁSearchRegistryǁ__init____mutmut_3(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = [InternalRepoSearch(root=None)]
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def xǁSearchRegistryǁ__init____mutmut_4(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = [InternalRepoSearch(root=root and Path.cwd())]
        if enable_external:
            self.providers.append(ExternalWebSearch())

    def xǁSearchRegistryǁ__init____mutmut_5(self, enable_external: bool = False, root: Optional[Path] = None):
        self.providers: list[SearchProvider] = [InternalRepoSearch(root=root or Path.cwd())]
        if enable_external:
            self.providers.append(None)
    
    xǁSearchRegistryǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSearchRegistryǁ__init____mutmut_1': xǁSearchRegistryǁ__init____mutmut_1, 
        'xǁSearchRegistryǁ__init____mutmut_2': xǁSearchRegistryǁ__init____mutmut_2, 
        'xǁSearchRegistryǁ__init____mutmut_3': xǁSearchRegistryǁ__init____mutmut_3, 
        'xǁSearchRegistryǁ__init____mutmut_4': xǁSearchRegistryǁ__init____mutmut_4, 
        'xǁSearchRegistryǁ__init____mutmut_5': xǁSearchRegistryǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSearchRegistryǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSearchRegistryǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSearchRegistryǁ__init____mutmut_orig)
    xǁSearchRegistryǁ__init____mutmut_orig.__name__ = 'xǁSearchRegistryǁ__init__'

    def xǁSearchRegistryǁsearch__mutmut_orig(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_1(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = None
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_2(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(None)
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_3(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(None))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_4(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning(None, exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_5(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=None)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_6(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning(exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_7(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", )
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_8(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("XXException occurredXX", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_9(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_10(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("EXCEPTION OCCURRED", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_11(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=False)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_12(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning(None, exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_13(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=None)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_14(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning(exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_15(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", )
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_16(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("XXException occurredXX", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_17(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_18(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("EXCEPTION OCCURRED", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_19(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=False)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                continue
        return results

    def xǁSearchRegistryǁsearch__mutmut_20(self, query: str) -> list[dict[str, Any]]:
        """Search all providers and concatenate their results."""

        results: list[dict[str, Any]] = []
        for provider in self.providers:
            try:
                results.extend(provider.search(query))
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Each provider is responsible for handling its own errors. If
                # an unexpected exception bubbles up we swallow it here so that
                # other providers still run.
                break
        return results
    
    xǁSearchRegistryǁsearch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSearchRegistryǁsearch__mutmut_1': xǁSearchRegistryǁsearch__mutmut_1, 
        'xǁSearchRegistryǁsearch__mutmut_2': xǁSearchRegistryǁsearch__mutmut_2, 
        'xǁSearchRegistryǁsearch__mutmut_3': xǁSearchRegistryǁsearch__mutmut_3, 
        'xǁSearchRegistryǁsearch__mutmut_4': xǁSearchRegistryǁsearch__mutmut_4, 
        'xǁSearchRegistryǁsearch__mutmut_5': xǁSearchRegistryǁsearch__mutmut_5, 
        'xǁSearchRegistryǁsearch__mutmut_6': xǁSearchRegistryǁsearch__mutmut_6, 
        'xǁSearchRegistryǁsearch__mutmut_7': xǁSearchRegistryǁsearch__mutmut_7, 
        'xǁSearchRegistryǁsearch__mutmut_8': xǁSearchRegistryǁsearch__mutmut_8, 
        'xǁSearchRegistryǁsearch__mutmut_9': xǁSearchRegistryǁsearch__mutmut_9, 
        'xǁSearchRegistryǁsearch__mutmut_10': xǁSearchRegistryǁsearch__mutmut_10, 
        'xǁSearchRegistryǁsearch__mutmut_11': xǁSearchRegistryǁsearch__mutmut_11, 
        'xǁSearchRegistryǁsearch__mutmut_12': xǁSearchRegistryǁsearch__mutmut_12, 
        'xǁSearchRegistryǁsearch__mutmut_13': xǁSearchRegistryǁsearch__mutmut_13, 
        'xǁSearchRegistryǁsearch__mutmut_14': xǁSearchRegistryǁsearch__mutmut_14, 
        'xǁSearchRegistryǁsearch__mutmut_15': xǁSearchRegistryǁsearch__mutmut_15, 
        'xǁSearchRegistryǁsearch__mutmut_16': xǁSearchRegistryǁsearch__mutmut_16, 
        'xǁSearchRegistryǁsearch__mutmut_17': xǁSearchRegistryǁsearch__mutmut_17, 
        'xǁSearchRegistryǁsearch__mutmut_18': xǁSearchRegistryǁsearch__mutmut_18, 
        'xǁSearchRegistryǁsearch__mutmut_19': xǁSearchRegistryǁsearch__mutmut_19, 
        'xǁSearchRegistryǁsearch__mutmut_20': xǁSearchRegistryǁsearch__mutmut_20
    }
    
    def search(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSearchRegistryǁsearch__mutmut_orig"), object.__getattribute__(self, "xǁSearchRegistryǁsearch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    search.__signature__ = _mutmut_signature(xǁSearchRegistryǁsearch__mutmut_orig)
    xǁSearchRegistryǁsearch__mutmut_orig.__name__ = 'xǁSearchRegistryǁsearch'
