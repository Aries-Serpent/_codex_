"""
Pinecone Adapter Module

This module provides functionality for pinecone adapter.

Usage:
    from backends.pinecone_adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Pinecone adapter for MCP backend interface (skeleton + wiring to retries & metrics)
from __future__ import annotations
import importlib
import importlib.util
import logging
import os
import sys
from typing import Any, Iterable, Optional

from .interface import BackendAdapter, VectorItem, BackendResponse

# Reuse Plan A scaffolds (import-safe)
from src.mcp.retries import retry_on_exception  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore
from src.mcp.server.safety_checks import live_tests_enabled  # type: ignore

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


class PineconeAdapter(BackendAdapter):
    """
    Pinecone adapter skeleton.

    - Lazy-imports pinecone SDK so import-time does not fail when package absent.
    - Uses retry_on_exception for transient network calls.
    - Emits minimal metrics via src/mcp/observability/metrics.
    - Guards live calls with live_tests_enabled() safety check.
    """

    def xǁPineconeAdapterǁ__init____mutmut_orig(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_1(self, index_name: Optional[str] = None) -> None:
        self._client = ""
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_2(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = ""
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_3(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = None
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_4(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = True
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_5(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = None
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_6(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name and os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_7(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get(None, "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_8(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", None)
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_9(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_10(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", )
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_11(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("XXPINECONE_INDEX_NAMEXX", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_12(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("pinecone_index_name", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_13(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "XXmcp-indexXX")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_14(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "MCP-INDEX")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_15(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = None
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_16(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get(None, "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_17(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", None)
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_18(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_19(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", )
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_20(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("XXPINECONE_API_KEYXX", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_21(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("pinecone_api_key", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_22(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "XXXX")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_23(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = None
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_24(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get(None, "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_25(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", None)
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_26(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_27(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", )
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_28(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("XXPINECONE_ENVXX", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_29(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("pinecone_env", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_30(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "XXXX")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_31(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = None

    def xǁPineconeAdapterǁ__init____mutmut_32(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(None)

    def xǁPineconeAdapterǁ__init____mutmut_33(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get(None, "3"))

    def xǁPineconeAdapterǁ__init____mutmut_34(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", None))

    def xǁPineconeAdapterǁ__init____mutmut_35(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("3"))

    def xǁPineconeAdapterǁ__init____mutmut_36(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", ))

    def xǁPineconeAdapterǁ__init____mutmut_37(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("XXPINECONE_MAX_RETRIESXX", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_38(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("pinecone_max_retries", "3"))

    def xǁPineconeAdapterǁ__init____mutmut_39(self, index_name: Optional[str] = None) -> None:
        self._client = None
        self._index = None
        self._connected = False
        self._index_name = index_name or os.environ.get("PINECONE_INDEX_NAME", "mcp-index")
        self._api_key = os.environ.get("PINECONE_API_KEY", "")
        self._env = os.environ.get("PINECONE_ENV", "")
        # Config knobs (env overrides)
        self._max_retries = int(os.environ.get("PINECONE_MAX_RETRIES", "XX3XX"))
    
    xǁPineconeAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁ__init____mutmut_1': xǁPineconeAdapterǁ__init____mutmut_1, 
        'xǁPineconeAdapterǁ__init____mutmut_2': xǁPineconeAdapterǁ__init____mutmut_2, 
        'xǁPineconeAdapterǁ__init____mutmut_3': xǁPineconeAdapterǁ__init____mutmut_3, 
        'xǁPineconeAdapterǁ__init____mutmut_4': xǁPineconeAdapterǁ__init____mutmut_4, 
        'xǁPineconeAdapterǁ__init____mutmut_5': xǁPineconeAdapterǁ__init____mutmut_5, 
        'xǁPineconeAdapterǁ__init____mutmut_6': xǁPineconeAdapterǁ__init____mutmut_6, 
        'xǁPineconeAdapterǁ__init____mutmut_7': xǁPineconeAdapterǁ__init____mutmut_7, 
        'xǁPineconeAdapterǁ__init____mutmut_8': xǁPineconeAdapterǁ__init____mutmut_8, 
        'xǁPineconeAdapterǁ__init____mutmut_9': xǁPineconeAdapterǁ__init____mutmut_9, 
        'xǁPineconeAdapterǁ__init____mutmut_10': xǁPineconeAdapterǁ__init____mutmut_10, 
        'xǁPineconeAdapterǁ__init____mutmut_11': xǁPineconeAdapterǁ__init____mutmut_11, 
        'xǁPineconeAdapterǁ__init____mutmut_12': xǁPineconeAdapterǁ__init____mutmut_12, 
        'xǁPineconeAdapterǁ__init____mutmut_13': xǁPineconeAdapterǁ__init____mutmut_13, 
        'xǁPineconeAdapterǁ__init____mutmut_14': xǁPineconeAdapterǁ__init____mutmut_14, 
        'xǁPineconeAdapterǁ__init____mutmut_15': xǁPineconeAdapterǁ__init____mutmut_15, 
        'xǁPineconeAdapterǁ__init____mutmut_16': xǁPineconeAdapterǁ__init____mutmut_16, 
        'xǁPineconeAdapterǁ__init____mutmut_17': xǁPineconeAdapterǁ__init____mutmut_17, 
        'xǁPineconeAdapterǁ__init____mutmut_18': xǁPineconeAdapterǁ__init____mutmut_18, 
        'xǁPineconeAdapterǁ__init____mutmut_19': xǁPineconeAdapterǁ__init____mutmut_19, 
        'xǁPineconeAdapterǁ__init____mutmut_20': xǁPineconeAdapterǁ__init____mutmut_20, 
        'xǁPineconeAdapterǁ__init____mutmut_21': xǁPineconeAdapterǁ__init____mutmut_21, 
        'xǁPineconeAdapterǁ__init____mutmut_22': xǁPineconeAdapterǁ__init____mutmut_22, 
        'xǁPineconeAdapterǁ__init____mutmut_23': xǁPineconeAdapterǁ__init____mutmut_23, 
        'xǁPineconeAdapterǁ__init____mutmut_24': xǁPineconeAdapterǁ__init____mutmut_24, 
        'xǁPineconeAdapterǁ__init____mutmut_25': xǁPineconeAdapterǁ__init____mutmut_25, 
        'xǁPineconeAdapterǁ__init____mutmut_26': xǁPineconeAdapterǁ__init____mutmut_26, 
        'xǁPineconeAdapterǁ__init____mutmut_27': xǁPineconeAdapterǁ__init____mutmut_27, 
        'xǁPineconeAdapterǁ__init____mutmut_28': xǁPineconeAdapterǁ__init____mutmut_28, 
        'xǁPineconeAdapterǁ__init____mutmut_29': xǁPineconeAdapterǁ__init____mutmut_29, 
        'xǁPineconeAdapterǁ__init____mutmut_30': xǁPineconeAdapterǁ__init____mutmut_30, 
        'xǁPineconeAdapterǁ__init____mutmut_31': xǁPineconeAdapterǁ__init____mutmut_31, 
        'xǁPineconeAdapterǁ__init____mutmut_32': xǁPineconeAdapterǁ__init____mutmut_32, 
        'xǁPineconeAdapterǁ__init____mutmut_33': xǁPineconeAdapterǁ__init____mutmut_33, 
        'xǁPineconeAdapterǁ__init____mutmut_34': xǁPineconeAdapterǁ__init____mutmut_34, 
        'xǁPineconeAdapterǁ__init____mutmut_35': xǁPineconeAdapterǁ__init____mutmut_35, 
        'xǁPineconeAdapterǁ__init____mutmut_36': xǁPineconeAdapterǁ__init____mutmut_36, 
        'xǁPineconeAdapterǁ__init____mutmut_37': xǁPineconeAdapterǁ__init____mutmut_37, 
        'xǁPineconeAdapterǁ__init____mutmut_38': xǁPineconeAdapterǁ__init____mutmut_38, 
        'xǁPineconeAdapterǁ__init____mutmut_39': xǁPineconeAdapterǁ__init____mutmut_39
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁPineconeAdapterǁ__init____mutmut_orig)
    xǁPineconeAdapterǁ__init____mutmut_orig.__name__ = 'xǁPineconeAdapterǁ__init__'

    def xǁPineconeAdapterǁ_lazy_import__mutmut_orig(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_1(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "XXpineconeXX" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_2(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "PINECONE" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_3(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" not in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_4(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["XXpineconeXX"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_5(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["PINECONE"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_6(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec(None) is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_7(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("XXpineconeXX") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_8(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("PINECONE") is None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_9(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is not None:
            return None
        return importlib.import_module("pinecone")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_10(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module(None)

    def xǁPineconeAdapterǁ_lazy_import__mutmut_11(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("XXpineconeXX")

    def xǁPineconeAdapterǁ_lazy_import__mutmut_12(self):
        """
        Lazy import helper that returns the pinecone module or None.
        Tests can monkeypatch 'pinecone' in sys.modules to provide a fake impl.
        """
        if "pinecone" in sys.modules:
            return sys.modules["pinecone"]
        if importlib.util.find_spec("pinecone") is None:
            return None
        return importlib.import_module("PINECONE")
    
    xǁPineconeAdapterǁ_lazy_import__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁ_lazy_import__mutmut_1': xǁPineconeAdapterǁ_lazy_import__mutmut_1, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_2': xǁPineconeAdapterǁ_lazy_import__mutmut_2, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_3': xǁPineconeAdapterǁ_lazy_import__mutmut_3, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_4': xǁPineconeAdapterǁ_lazy_import__mutmut_4, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_5': xǁPineconeAdapterǁ_lazy_import__mutmut_5, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_6': xǁPineconeAdapterǁ_lazy_import__mutmut_6, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_7': xǁPineconeAdapterǁ_lazy_import__mutmut_7, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_8': xǁPineconeAdapterǁ_lazy_import__mutmut_8, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_9': xǁPineconeAdapterǁ_lazy_import__mutmut_9, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_10': xǁPineconeAdapterǁ_lazy_import__mutmut_10, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_11': xǁPineconeAdapterǁ_lazy_import__mutmut_11, 
        'xǁPineconeAdapterǁ_lazy_import__mutmut_12': xǁPineconeAdapterǁ_lazy_import__mutmut_12
    }
    
    def _lazy_import(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁ_lazy_import__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁ_lazy_import__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _lazy_import.__signature__ = _mutmut_signature(xǁPineconeAdapterǁ_lazy_import__mutmut_orig)
    xǁPineconeAdapterǁ_lazy_import__mutmut_orig.__name__ = 'xǁPineconeAdapterǁ_lazy_import'

    def xǁPineconeAdapterǁconnect__mutmut_orig(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_1(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key and not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_2(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_3(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_4(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info(None)
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_5(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("XXPinecone credentials not set; adapter remains disconnected.XX")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_6(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_7(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("PINECONE CREDENTIALS NOT SET; ADAPTER REMAINS DISCONNECTED.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_8(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = None
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_9(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = True
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_10(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = None
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_11(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_12(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning(None)
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_13(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("XXpinecone SDK not available; adapter cannot connect.XX")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_14(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone sdk not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_15(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("PINECONE SDK NOT AVAILABLE; ADAPTER CANNOT CONNECT.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_16(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = None
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_17(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = True
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_18(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=None, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_19(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=None)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_20(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_21(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, )
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_22(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = None
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_23(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(None)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_24(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = None
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_25(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = None
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_26(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = False
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_27(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info(None, self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_28(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", None)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_29(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info(self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_30(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_31(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("XXConnected to Pinecone index %sXX", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_32(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("connected to pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_33(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("CONNECTED TO PINECONE INDEX %S", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_34(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(None)
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_35(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception(None, exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_36(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", None)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_37(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception(exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_38(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", )
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_39(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("XXFailed to initialize Pinecone: %sXX", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_40(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("failed to initialize pinecone: %s", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_41(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("FAILED TO INITIALIZE PINECONE: %S", exc)
            self._connected = False

    def xǁPineconeAdapterǁconnect__mutmut_42(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = None

    def xǁPineconeAdapterǁconnect__mutmut_43(self) -> None:
        """Lazily initialize pinecone client & index. No-op if credentials absent."""
        if self._connected:
            return
        if not self._api_key or not self._env:
            logger.info("Pinecone credentials not set; adapter remains disconnected.")
            self._connected = False
            return

        pinecone = self._lazy_import()
        if not pinecone:
            logger.warning("pinecone SDK not available; adapter cannot connect.")
            self._connected = False
            return

        try:
            pinecone.init(api_key=self._api_key, environment=self._env)
            self._index = pinecone.Index(self._index_name)
            self._client = pinecone
            self._connected = True
            logger.info("Connected to Pinecone index %s", self._index_name)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            logger.exception("Failed to initialize Pinecone: %s", exc)
            self._connected = True
    
    xǁPineconeAdapterǁconnect__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁconnect__mutmut_1': xǁPineconeAdapterǁconnect__mutmut_1, 
        'xǁPineconeAdapterǁconnect__mutmut_2': xǁPineconeAdapterǁconnect__mutmut_2, 
        'xǁPineconeAdapterǁconnect__mutmut_3': xǁPineconeAdapterǁconnect__mutmut_3, 
        'xǁPineconeAdapterǁconnect__mutmut_4': xǁPineconeAdapterǁconnect__mutmut_4, 
        'xǁPineconeAdapterǁconnect__mutmut_5': xǁPineconeAdapterǁconnect__mutmut_5, 
        'xǁPineconeAdapterǁconnect__mutmut_6': xǁPineconeAdapterǁconnect__mutmut_6, 
        'xǁPineconeAdapterǁconnect__mutmut_7': xǁPineconeAdapterǁconnect__mutmut_7, 
        'xǁPineconeAdapterǁconnect__mutmut_8': xǁPineconeAdapterǁconnect__mutmut_8, 
        'xǁPineconeAdapterǁconnect__mutmut_9': xǁPineconeAdapterǁconnect__mutmut_9, 
        'xǁPineconeAdapterǁconnect__mutmut_10': xǁPineconeAdapterǁconnect__mutmut_10, 
        'xǁPineconeAdapterǁconnect__mutmut_11': xǁPineconeAdapterǁconnect__mutmut_11, 
        'xǁPineconeAdapterǁconnect__mutmut_12': xǁPineconeAdapterǁconnect__mutmut_12, 
        'xǁPineconeAdapterǁconnect__mutmut_13': xǁPineconeAdapterǁconnect__mutmut_13, 
        'xǁPineconeAdapterǁconnect__mutmut_14': xǁPineconeAdapterǁconnect__mutmut_14, 
        'xǁPineconeAdapterǁconnect__mutmut_15': xǁPineconeAdapterǁconnect__mutmut_15, 
        'xǁPineconeAdapterǁconnect__mutmut_16': xǁPineconeAdapterǁconnect__mutmut_16, 
        'xǁPineconeAdapterǁconnect__mutmut_17': xǁPineconeAdapterǁconnect__mutmut_17, 
        'xǁPineconeAdapterǁconnect__mutmut_18': xǁPineconeAdapterǁconnect__mutmut_18, 
        'xǁPineconeAdapterǁconnect__mutmut_19': xǁPineconeAdapterǁconnect__mutmut_19, 
        'xǁPineconeAdapterǁconnect__mutmut_20': xǁPineconeAdapterǁconnect__mutmut_20, 
        'xǁPineconeAdapterǁconnect__mutmut_21': xǁPineconeAdapterǁconnect__mutmut_21, 
        'xǁPineconeAdapterǁconnect__mutmut_22': xǁPineconeAdapterǁconnect__mutmut_22, 
        'xǁPineconeAdapterǁconnect__mutmut_23': xǁPineconeAdapterǁconnect__mutmut_23, 
        'xǁPineconeAdapterǁconnect__mutmut_24': xǁPineconeAdapterǁconnect__mutmut_24, 
        'xǁPineconeAdapterǁconnect__mutmut_25': xǁPineconeAdapterǁconnect__mutmut_25, 
        'xǁPineconeAdapterǁconnect__mutmut_26': xǁPineconeAdapterǁconnect__mutmut_26, 
        'xǁPineconeAdapterǁconnect__mutmut_27': xǁPineconeAdapterǁconnect__mutmut_27, 
        'xǁPineconeAdapterǁconnect__mutmut_28': xǁPineconeAdapterǁconnect__mutmut_28, 
        'xǁPineconeAdapterǁconnect__mutmut_29': xǁPineconeAdapterǁconnect__mutmut_29, 
        'xǁPineconeAdapterǁconnect__mutmut_30': xǁPineconeAdapterǁconnect__mutmut_30, 
        'xǁPineconeAdapterǁconnect__mutmut_31': xǁPineconeAdapterǁconnect__mutmut_31, 
        'xǁPineconeAdapterǁconnect__mutmut_32': xǁPineconeAdapterǁconnect__mutmut_32, 
        'xǁPineconeAdapterǁconnect__mutmut_33': xǁPineconeAdapterǁconnect__mutmut_33, 
        'xǁPineconeAdapterǁconnect__mutmut_34': xǁPineconeAdapterǁconnect__mutmut_34, 
        'xǁPineconeAdapterǁconnect__mutmut_35': xǁPineconeAdapterǁconnect__mutmut_35, 
        'xǁPineconeAdapterǁconnect__mutmut_36': xǁPineconeAdapterǁconnect__mutmut_36, 
        'xǁPineconeAdapterǁconnect__mutmut_37': xǁPineconeAdapterǁconnect__mutmut_37, 
        'xǁPineconeAdapterǁconnect__mutmut_38': xǁPineconeAdapterǁconnect__mutmut_38, 
        'xǁPineconeAdapterǁconnect__mutmut_39': xǁPineconeAdapterǁconnect__mutmut_39, 
        'xǁPineconeAdapterǁconnect__mutmut_40': xǁPineconeAdapterǁconnect__mutmut_40, 
        'xǁPineconeAdapterǁconnect__mutmut_41': xǁPineconeAdapterǁconnect__mutmut_41, 
        'xǁPineconeAdapterǁconnect__mutmut_42': xǁPineconeAdapterǁconnect__mutmut_42, 
        'xǁPineconeAdapterǁconnect__mutmut_43': xǁPineconeAdapterǁconnect__mutmut_43
    }
    
    def connect(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁconnect__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁconnect__mutmut_mutants"), args, kwargs, self)
        return result 
    
    connect.__signature__ = _mutmut_signature(xǁPineconeAdapterǁconnect__mutmut_orig)
    xǁPineconeAdapterǁconnect__mutmut_orig.__name__ = 'xǁPineconeAdapterǁconnect'

    @retry_on_exception(tries=3)
    def _index_upsert(self, vectors: list, namespace: Optional[str] = None) -> Any:
        """Internal wrapper for index.upsert with retries."""
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.upsert(vectors=vectors, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_query(
        self,
        vector: list[float],
        top_k: int = 5,
        filter: Optional[dict] = None,
        namespace: Optional[str] = None,
    ) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.query(vector=vector, top_k=top_k, filter=filter, namespace=namespace)

    @retry_on_exception(tries=3)
    def _index_delete(self, ids: list[str], namespace: Optional[str] = None) -> Any:
        if not self._index:
            raise RuntimeError("Index not initialized")
        return self._index.delete(ids=ids, namespace=namespace)

    def xǁPineconeAdapterǁupsert_batch__mutmut_orig(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_1(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment(None)
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_2(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("XXpinecone_upsert_totalXX")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_3(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("PINECONE_UPSERT_TOTAL")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_4(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected and self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_5(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_6(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is not None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_7(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected and self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_8(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_9(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is not None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_10(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug(None)
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_11(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("XXPinecone adapter not connected; upsert_batch no-op.XX")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_12(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_13(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("PINECONE ADAPTER NOT CONNECTED; UPSERT_BATCH NO-OP.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_14(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_15(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug(None)
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_16(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("XXENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.XX")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_17(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("enable_live_tests not set; skipping live pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_18(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS NOT SET; SKIPPING LIVE PINECONE UPSERT FOR SAFETY.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_19(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = None
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_20(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append(None)

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_21(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["XXidXX"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_22(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["ID"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_23(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["XXembeddingXX"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_24(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["EMBEDDING"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_25(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get(None, {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_26(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", None)))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_27(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get({})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_28(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", )))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_29(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("XXmetadataXX", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_30(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("METADATA", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_31(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer(None):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_32(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("XXpinecone_upsert_latencyXX"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_33(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("PINECONE_UPSERT_LATENCY"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_34(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=None, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_35(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=None)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_36(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_37(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, )
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_38(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_39(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_40(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_41(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_42(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_43(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_44(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_45(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_46(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_47(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_48(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_49(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_50(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_51(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_52(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_53(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            increment("pinecone_errors_total")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_54(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment(None)
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_55(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("XXpinecone_errors_totalXX")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_56(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("PINECONE_ERRORS_TOTAL")
            logger.exception("Pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_57(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception(None)
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_58(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("XXPinecone upsert failedXX")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_59(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("pinecone upsert failed")
            raise

    def xǁPineconeAdapterǁupsert_batch__mutmut_60(self, namespace: str, items: Iterable[VectorItem]) -> None:
        """
        Upsert a batch of items. Emits metrics and respects safety guard.
        Each item should contain: id, embedding, metadata.
        """
        increment("pinecone_upsert_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter not connected; upsert_batch no-op.")
            return

        # Safety guard: do not call live providers unless explicitly enabled
        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping live Pinecone upsert for safety.")
            return

        vectors = []
        for item in items:
            vectors.append((item["id"], item["embedding"], item.get("metadata", {})))

        try:
            with Timer("pinecone_upsert_latency"):
                self._index_upsert(vectors=vectors, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("PINECONE UPSERT FAILED")
            raise
    
    xǁPineconeAdapterǁupsert_batch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁupsert_batch__mutmut_1': xǁPineconeAdapterǁupsert_batch__mutmut_1, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_2': xǁPineconeAdapterǁupsert_batch__mutmut_2, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_3': xǁPineconeAdapterǁupsert_batch__mutmut_3, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_4': xǁPineconeAdapterǁupsert_batch__mutmut_4, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_5': xǁPineconeAdapterǁupsert_batch__mutmut_5, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_6': xǁPineconeAdapterǁupsert_batch__mutmut_6, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_7': xǁPineconeAdapterǁupsert_batch__mutmut_7, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_8': xǁPineconeAdapterǁupsert_batch__mutmut_8, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_9': xǁPineconeAdapterǁupsert_batch__mutmut_9, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_10': xǁPineconeAdapterǁupsert_batch__mutmut_10, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_11': xǁPineconeAdapterǁupsert_batch__mutmut_11, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_12': xǁPineconeAdapterǁupsert_batch__mutmut_12, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_13': xǁPineconeAdapterǁupsert_batch__mutmut_13, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_14': xǁPineconeAdapterǁupsert_batch__mutmut_14, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_15': xǁPineconeAdapterǁupsert_batch__mutmut_15, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_16': xǁPineconeAdapterǁupsert_batch__mutmut_16, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_17': xǁPineconeAdapterǁupsert_batch__mutmut_17, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_18': xǁPineconeAdapterǁupsert_batch__mutmut_18, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_19': xǁPineconeAdapterǁupsert_batch__mutmut_19, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_20': xǁPineconeAdapterǁupsert_batch__mutmut_20, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_21': xǁPineconeAdapterǁupsert_batch__mutmut_21, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_22': xǁPineconeAdapterǁupsert_batch__mutmut_22, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_23': xǁPineconeAdapterǁupsert_batch__mutmut_23, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_24': xǁPineconeAdapterǁupsert_batch__mutmut_24, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_25': xǁPineconeAdapterǁupsert_batch__mutmut_25, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_26': xǁPineconeAdapterǁupsert_batch__mutmut_26, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_27': xǁPineconeAdapterǁupsert_batch__mutmut_27, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_28': xǁPineconeAdapterǁupsert_batch__mutmut_28, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_29': xǁPineconeAdapterǁupsert_batch__mutmut_29, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_30': xǁPineconeAdapterǁupsert_batch__mutmut_30, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_31': xǁPineconeAdapterǁupsert_batch__mutmut_31, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_32': xǁPineconeAdapterǁupsert_batch__mutmut_32, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_33': xǁPineconeAdapterǁupsert_batch__mutmut_33, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_34': xǁPineconeAdapterǁupsert_batch__mutmut_34, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_35': xǁPineconeAdapterǁupsert_batch__mutmut_35, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_36': xǁPineconeAdapterǁupsert_batch__mutmut_36, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_37': xǁPineconeAdapterǁupsert_batch__mutmut_37, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_38': xǁPineconeAdapterǁupsert_batch__mutmut_38, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_39': xǁPineconeAdapterǁupsert_batch__mutmut_39, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_40': xǁPineconeAdapterǁupsert_batch__mutmut_40, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_41': xǁPineconeAdapterǁupsert_batch__mutmut_41, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_42': xǁPineconeAdapterǁupsert_batch__mutmut_42, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_43': xǁPineconeAdapterǁupsert_batch__mutmut_43, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_44': xǁPineconeAdapterǁupsert_batch__mutmut_44, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_45': xǁPineconeAdapterǁupsert_batch__mutmut_45, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_46': xǁPineconeAdapterǁupsert_batch__mutmut_46, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_47': xǁPineconeAdapterǁupsert_batch__mutmut_47, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_48': xǁPineconeAdapterǁupsert_batch__mutmut_48, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_49': xǁPineconeAdapterǁupsert_batch__mutmut_49, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_50': xǁPineconeAdapterǁupsert_batch__mutmut_50, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_51': xǁPineconeAdapterǁupsert_batch__mutmut_51, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_52': xǁPineconeAdapterǁupsert_batch__mutmut_52, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_53': xǁPineconeAdapterǁupsert_batch__mutmut_53, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_54': xǁPineconeAdapterǁupsert_batch__mutmut_54, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_55': xǁPineconeAdapterǁupsert_batch__mutmut_55, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_56': xǁPineconeAdapterǁupsert_batch__mutmut_56, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_57': xǁPineconeAdapterǁupsert_batch__mutmut_57, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_58': xǁPineconeAdapterǁupsert_batch__mutmut_58, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_59': xǁPineconeAdapterǁupsert_batch__mutmut_59, 
        'xǁPineconeAdapterǁupsert_batch__mutmut_60': xǁPineconeAdapterǁupsert_batch__mutmut_60
    }
    
    def upsert_batch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁupsert_batch__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁupsert_batch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    upsert_batch.__signature__ = _mutmut_signature(xǁPineconeAdapterǁupsert_batch__mutmut_orig)
    xǁPineconeAdapterǁupsert_batch__mutmut_orig.__name__ = 'xǁPineconeAdapterǁupsert_batch'

    def xǁPineconeAdapterǁquery_top_k__mutmut_orig(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_1(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 6,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_2(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment(None)
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_3(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("XXpinecone_query_totalXX")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_4(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("PINECONE_QUERY_TOTAL")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_5(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected and self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_6(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_7(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is not None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_8(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected and self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_9(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_10(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is not None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_11(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug(None)
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_12(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("XXPinecone adapter disconnected; returning empty list.XX")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_13(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_14(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("PINECONE ADAPTER DISCONNECTED; RETURNING EMPTY LIST.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_15(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_16(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug(None)
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_17(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("XXENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).XX")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_18(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("enable_live_tests not set; returning empty list for pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_19(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS NOT SET; RETURNING EMPTY LIST FOR PINECONE QUERY (SAFETY).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_20(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer(None):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_21(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("XXpinecone_query_latencyXX"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_22(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("PINECONE_QUERY_LATENCY"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_23(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = None
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_24(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=None, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_25(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=None, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_26(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=None, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_27(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=None)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_28(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_29(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_30(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_31(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, )
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_32(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_33(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_34(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_35(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_36(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_37(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_38(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_39(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_40(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_41(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_42(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_43(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_44(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_45(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_46(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_47(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_48(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment(None)
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_49(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("XXpinecone_errors_totalXX")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_50(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("PINECONE_ERRORS_TOTAL")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_51(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception(None)
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_52(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("XXPinecone query failedXX")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_53(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_54(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("PINECONE QUERY FAILED")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_55(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = None
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_56(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = None
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_57(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get(None, [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_58(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", None)
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_59(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get([])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_60(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", )
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_61(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("XXmatchesXX", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_62(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("MATCHES", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_63(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = None

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_64(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) and []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_65(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(None, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_66(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, None, []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_67(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", None) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_68(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr("matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_69(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_70(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", ) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_71(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "XXmatchesXX", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_72(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "MATCHES", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_73(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = None
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_74(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                None
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_75(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    None
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_76(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "XXidXX": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_77(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "ID": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_78(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get(None),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_79(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("XXidXX"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_80(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("ID"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_81(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "XXscoreXX": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_82(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "SCORE": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_83(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(None),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_84(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get(None, 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_85(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", None)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_86(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get(0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_87(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", )),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_88(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("XXscoreXX", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_89(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("SCORE", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_90(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 1.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_91(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "XXcontentXX": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_92(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "CONTENT": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_93(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get(None, "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_94(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", None) if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_95(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_96(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", ) if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_97(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get(None, {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_98(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", None).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_99(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get({}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_100(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", ).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_101(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("XXmetadataXX", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_102(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("METADATA", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_103(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("XXcontentXX", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_104(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("CONTENT", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_105(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "XXXX") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_106(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "XXXX",
                        "metadata": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_107(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "XXmetadataXX": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_108(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "METADATA": m.get("metadata", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_109(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get(None, {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_110(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", None),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_111(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get({}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_112(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("metadata", ),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_113(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("XXmetadataXX", {}),
                    }
                )
            )
        return results

    def xǁPineconeAdapterǁquery_top_k__mutmut_114(
        self,
        namespace: str,
        query_embedding: list[float],
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[BackendResponse]:
        increment("pinecone_query_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            logger.debug("Pinecone adapter disconnected; returning empty list.")
            return []

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; returning empty list for Pinecone query (safety).")
            return []

        try:
            with Timer("pinecone_query_latency"):
                resp = self._index_query(vector=query_embedding, top_k=top_k, filter=filters, namespace=namespace)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone query failed")
            return []

        # Normalize matches across possible response shapes
        matches = []
        if isinstance(resp, dict):
            matches = resp.get("matches", [])
        else:
            matches = getattr(resp, "matches", []) or []

        results: list[BackendResponse] = []
        for m in matches:
            results.append(
                BackendResponse(
                    {
                        "id": m.get("id"),
                        "score": float(m.get("score", 0.0)),
                        "content": m.get("metadata", {}).get("content", "") if isinstance(m.get("metadata", {}), dict) else "",
                        "metadata": m.get("METADATA", {}),
                    }
                )
            )
        return results
    
    xǁPineconeAdapterǁquery_top_k__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁquery_top_k__mutmut_1': xǁPineconeAdapterǁquery_top_k__mutmut_1, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_2': xǁPineconeAdapterǁquery_top_k__mutmut_2, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_3': xǁPineconeAdapterǁquery_top_k__mutmut_3, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_4': xǁPineconeAdapterǁquery_top_k__mutmut_4, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_5': xǁPineconeAdapterǁquery_top_k__mutmut_5, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_6': xǁPineconeAdapterǁquery_top_k__mutmut_6, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_7': xǁPineconeAdapterǁquery_top_k__mutmut_7, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_8': xǁPineconeAdapterǁquery_top_k__mutmut_8, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_9': xǁPineconeAdapterǁquery_top_k__mutmut_9, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_10': xǁPineconeAdapterǁquery_top_k__mutmut_10, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_11': xǁPineconeAdapterǁquery_top_k__mutmut_11, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_12': xǁPineconeAdapterǁquery_top_k__mutmut_12, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_13': xǁPineconeAdapterǁquery_top_k__mutmut_13, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_14': xǁPineconeAdapterǁquery_top_k__mutmut_14, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_15': xǁPineconeAdapterǁquery_top_k__mutmut_15, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_16': xǁPineconeAdapterǁquery_top_k__mutmut_16, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_17': xǁPineconeAdapterǁquery_top_k__mutmut_17, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_18': xǁPineconeAdapterǁquery_top_k__mutmut_18, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_19': xǁPineconeAdapterǁquery_top_k__mutmut_19, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_20': xǁPineconeAdapterǁquery_top_k__mutmut_20, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_21': xǁPineconeAdapterǁquery_top_k__mutmut_21, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_22': xǁPineconeAdapterǁquery_top_k__mutmut_22, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_23': xǁPineconeAdapterǁquery_top_k__mutmut_23, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_24': xǁPineconeAdapterǁquery_top_k__mutmut_24, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_25': xǁPineconeAdapterǁquery_top_k__mutmut_25, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_26': xǁPineconeAdapterǁquery_top_k__mutmut_26, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_27': xǁPineconeAdapterǁquery_top_k__mutmut_27, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_28': xǁPineconeAdapterǁquery_top_k__mutmut_28, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_29': xǁPineconeAdapterǁquery_top_k__mutmut_29, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_30': xǁPineconeAdapterǁquery_top_k__mutmut_30, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_31': xǁPineconeAdapterǁquery_top_k__mutmut_31, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_32': xǁPineconeAdapterǁquery_top_k__mutmut_32, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_33': xǁPineconeAdapterǁquery_top_k__mutmut_33, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_34': xǁPineconeAdapterǁquery_top_k__mutmut_34, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_35': xǁPineconeAdapterǁquery_top_k__mutmut_35, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_36': xǁPineconeAdapterǁquery_top_k__mutmut_36, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_37': xǁPineconeAdapterǁquery_top_k__mutmut_37, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_38': xǁPineconeAdapterǁquery_top_k__mutmut_38, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_39': xǁPineconeAdapterǁquery_top_k__mutmut_39, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_40': xǁPineconeAdapterǁquery_top_k__mutmut_40, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_41': xǁPineconeAdapterǁquery_top_k__mutmut_41, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_42': xǁPineconeAdapterǁquery_top_k__mutmut_42, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_43': xǁPineconeAdapterǁquery_top_k__mutmut_43, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_44': xǁPineconeAdapterǁquery_top_k__mutmut_44, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_45': xǁPineconeAdapterǁquery_top_k__mutmut_45, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_46': xǁPineconeAdapterǁquery_top_k__mutmut_46, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_47': xǁPineconeAdapterǁquery_top_k__mutmut_47, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_48': xǁPineconeAdapterǁquery_top_k__mutmut_48, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_49': xǁPineconeAdapterǁquery_top_k__mutmut_49, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_50': xǁPineconeAdapterǁquery_top_k__mutmut_50, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_51': xǁPineconeAdapterǁquery_top_k__mutmut_51, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_52': xǁPineconeAdapterǁquery_top_k__mutmut_52, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_53': xǁPineconeAdapterǁquery_top_k__mutmut_53, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_54': xǁPineconeAdapterǁquery_top_k__mutmut_54, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_55': xǁPineconeAdapterǁquery_top_k__mutmut_55, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_56': xǁPineconeAdapterǁquery_top_k__mutmut_56, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_57': xǁPineconeAdapterǁquery_top_k__mutmut_57, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_58': xǁPineconeAdapterǁquery_top_k__mutmut_58, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_59': xǁPineconeAdapterǁquery_top_k__mutmut_59, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_60': xǁPineconeAdapterǁquery_top_k__mutmut_60, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_61': xǁPineconeAdapterǁquery_top_k__mutmut_61, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_62': xǁPineconeAdapterǁquery_top_k__mutmut_62, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_63': xǁPineconeAdapterǁquery_top_k__mutmut_63, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_64': xǁPineconeAdapterǁquery_top_k__mutmut_64, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_65': xǁPineconeAdapterǁquery_top_k__mutmut_65, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_66': xǁPineconeAdapterǁquery_top_k__mutmut_66, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_67': xǁPineconeAdapterǁquery_top_k__mutmut_67, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_68': xǁPineconeAdapterǁquery_top_k__mutmut_68, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_69': xǁPineconeAdapterǁquery_top_k__mutmut_69, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_70': xǁPineconeAdapterǁquery_top_k__mutmut_70, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_71': xǁPineconeAdapterǁquery_top_k__mutmut_71, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_72': xǁPineconeAdapterǁquery_top_k__mutmut_72, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_73': xǁPineconeAdapterǁquery_top_k__mutmut_73, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_74': xǁPineconeAdapterǁquery_top_k__mutmut_74, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_75': xǁPineconeAdapterǁquery_top_k__mutmut_75, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_76': xǁPineconeAdapterǁquery_top_k__mutmut_76, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_77': xǁPineconeAdapterǁquery_top_k__mutmut_77, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_78': xǁPineconeAdapterǁquery_top_k__mutmut_78, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_79': xǁPineconeAdapterǁquery_top_k__mutmut_79, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_80': xǁPineconeAdapterǁquery_top_k__mutmut_80, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_81': xǁPineconeAdapterǁquery_top_k__mutmut_81, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_82': xǁPineconeAdapterǁquery_top_k__mutmut_82, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_83': xǁPineconeAdapterǁquery_top_k__mutmut_83, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_84': xǁPineconeAdapterǁquery_top_k__mutmut_84, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_85': xǁPineconeAdapterǁquery_top_k__mutmut_85, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_86': xǁPineconeAdapterǁquery_top_k__mutmut_86, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_87': xǁPineconeAdapterǁquery_top_k__mutmut_87, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_88': xǁPineconeAdapterǁquery_top_k__mutmut_88, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_89': xǁPineconeAdapterǁquery_top_k__mutmut_89, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_90': xǁPineconeAdapterǁquery_top_k__mutmut_90, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_91': xǁPineconeAdapterǁquery_top_k__mutmut_91, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_92': xǁPineconeAdapterǁquery_top_k__mutmut_92, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_93': xǁPineconeAdapterǁquery_top_k__mutmut_93, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_94': xǁPineconeAdapterǁquery_top_k__mutmut_94, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_95': xǁPineconeAdapterǁquery_top_k__mutmut_95, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_96': xǁPineconeAdapterǁquery_top_k__mutmut_96, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_97': xǁPineconeAdapterǁquery_top_k__mutmut_97, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_98': xǁPineconeAdapterǁquery_top_k__mutmut_98, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_99': xǁPineconeAdapterǁquery_top_k__mutmut_99, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_100': xǁPineconeAdapterǁquery_top_k__mutmut_100, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_101': xǁPineconeAdapterǁquery_top_k__mutmut_101, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_102': xǁPineconeAdapterǁquery_top_k__mutmut_102, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_103': xǁPineconeAdapterǁquery_top_k__mutmut_103, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_104': xǁPineconeAdapterǁquery_top_k__mutmut_104, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_105': xǁPineconeAdapterǁquery_top_k__mutmut_105, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_106': xǁPineconeAdapterǁquery_top_k__mutmut_106, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_107': xǁPineconeAdapterǁquery_top_k__mutmut_107, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_108': xǁPineconeAdapterǁquery_top_k__mutmut_108, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_109': xǁPineconeAdapterǁquery_top_k__mutmut_109, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_110': xǁPineconeAdapterǁquery_top_k__mutmut_110, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_111': xǁPineconeAdapterǁquery_top_k__mutmut_111, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_112': xǁPineconeAdapterǁquery_top_k__mutmut_112, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_113': xǁPineconeAdapterǁquery_top_k__mutmut_113, 
        'xǁPineconeAdapterǁquery_top_k__mutmut_114': xǁPineconeAdapterǁquery_top_k__mutmut_114
    }
    
    def query_top_k(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁquery_top_k__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁquery_top_k__mutmut_mutants"), args, kwargs, self)
        return result 
    
    query_top_k.__signature__ = _mutmut_signature(xǁPineconeAdapterǁquery_top_k__mutmut_orig)
    xǁPineconeAdapterǁquery_top_k__mutmut_orig.__name__ = 'xǁPineconeAdapterǁquery_top_k'

    def xǁPineconeAdapterǁdelete__mutmut_orig(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_1(self, namespace: str, id: str) -> bool:
        increment(None)
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_2(self, namespace: str, id: str) -> bool:
        increment("XXpinecone_delete_totalXX")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_3(self, namespace: str, id: str) -> bool:
        increment("PINECONE_DELETE_TOTAL")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_4(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected and self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_5(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_6(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is not None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_7(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected and self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_8(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_9(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is not None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_10(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return True

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_11(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_12(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug(None)
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_13(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("XXENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.XX")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_14(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("enable_live_tests not set; skipping pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_15(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS NOT SET; SKIPPING PINECONE DELETE FOR SAFETY.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_16(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return True

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_17(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer(None):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_18(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("XXpinecone_delete_latencyXX"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_19(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("PINECONE_DELETE_LATENCY"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_20(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=None, namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_21(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=None)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_22(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_23(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], )
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_24(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return False
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_25(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_26(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_27(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_28(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_29(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_30(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_31(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_32(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_33(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_34(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_35(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_36(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_37(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_38(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_39(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_40(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_41(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment(None)
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_42(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("XXpinecone_errors_totalXX")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_43(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("PINECONE_ERRORS_TOTAL")
            logger.exception("Pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_44(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception(None)
            return False

    def xǁPineconeAdapterǁdelete__mutmut_45(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("XXPinecone delete failedXX")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_46(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("pinecone delete failed")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_47(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("PINECONE DELETE FAILED")
            return False

    def xǁPineconeAdapterǁdelete__mutmut_48(self, namespace: str, id: str) -> bool:
        increment("pinecone_delete_total")
        if not self._connected or self._index is None:
            self.connect()
        if not self._connected or self._index is None:
            return False

        if not live_tests_enabled():
            logger.debug("ENABLE_LIVE_TESTS not set; skipping Pinecone delete for safety.")
            return False

        try:
            with Timer("pinecone_delete_latency"):
                self._index_delete(ids=[id], namespace=namespace)
            return True
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            increment("pinecone_errors_total")
            logger.exception("Pinecone delete failed")
            return True
    
    xǁPineconeAdapterǁdelete__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁdelete__mutmut_1': xǁPineconeAdapterǁdelete__mutmut_1, 
        'xǁPineconeAdapterǁdelete__mutmut_2': xǁPineconeAdapterǁdelete__mutmut_2, 
        'xǁPineconeAdapterǁdelete__mutmut_3': xǁPineconeAdapterǁdelete__mutmut_3, 
        'xǁPineconeAdapterǁdelete__mutmut_4': xǁPineconeAdapterǁdelete__mutmut_4, 
        'xǁPineconeAdapterǁdelete__mutmut_5': xǁPineconeAdapterǁdelete__mutmut_5, 
        'xǁPineconeAdapterǁdelete__mutmut_6': xǁPineconeAdapterǁdelete__mutmut_6, 
        'xǁPineconeAdapterǁdelete__mutmut_7': xǁPineconeAdapterǁdelete__mutmut_7, 
        'xǁPineconeAdapterǁdelete__mutmut_8': xǁPineconeAdapterǁdelete__mutmut_8, 
        'xǁPineconeAdapterǁdelete__mutmut_9': xǁPineconeAdapterǁdelete__mutmut_9, 
        'xǁPineconeAdapterǁdelete__mutmut_10': xǁPineconeAdapterǁdelete__mutmut_10, 
        'xǁPineconeAdapterǁdelete__mutmut_11': xǁPineconeAdapterǁdelete__mutmut_11, 
        'xǁPineconeAdapterǁdelete__mutmut_12': xǁPineconeAdapterǁdelete__mutmut_12, 
        'xǁPineconeAdapterǁdelete__mutmut_13': xǁPineconeAdapterǁdelete__mutmut_13, 
        'xǁPineconeAdapterǁdelete__mutmut_14': xǁPineconeAdapterǁdelete__mutmut_14, 
        'xǁPineconeAdapterǁdelete__mutmut_15': xǁPineconeAdapterǁdelete__mutmut_15, 
        'xǁPineconeAdapterǁdelete__mutmut_16': xǁPineconeAdapterǁdelete__mutmut_16, 
        'xǁPineconeAdapterǁdelete__mutmut_17': xǁPineconeAdapterǁdelete__mutmut_17, 
        'xǁPineconeAdapterǁdelete__mutmut_18': xǁPineconeAdapterǁdelete__mutmut_18, 
        'xǁPineconeAdapterǁdelete__mutmut_19': xǁPineconeAdapterǁdelete__mutmut_19, 
        'xǁPineconeAdapterǁdelete__mutmut_20': xǁPineconeAdapterǁdelete__mutmut_20, 
        'xǁPineconeAdapterǁdelete__mutmut_21': xǁPineconeAdapterǁdelete__mutmut_21, 
        'xǁPineconeAdapterǁdelete__mutmut_22': xǁPineconeAdapterǁdelete__mutmut_22, 
        'xǁPineconeAdapterǁdelete__mutmut_23': xǁPineconeAdapterǁdelete__mutmut_23, 
        'xǁPineconeAdapterǁdelete__mutmut_24': xǁPineconeAdapterǁdelete__mutmut_24, 
        'xǁPineconeAdapterǁdelete__mutmut_25': xǁPineconeAdapterǁdelete__mutmut_25, 
        'xǁPineconeAdapterǁdelete__mutmut_26': xǁPineconeAdapterǁdelete__mutmut_26, 
        'xǁPineconeAdapterǁdelete__mutmut_27': xǁPineconeAdapterǁdelete__mutmut_27, 
        'xǁPineconeAdapterǁdelete__mutmut_28': xǁPineconeAdapterǁdelete__mutmut_28, 
        'xǁPineconeAdapterǁdelete__mutmut_29': xǁPineconeAdapterǁdelete__mutmut_29, 
        'xǁPineconeAdapterǁdelete__mutmut_30': xǁPineconeAdapterǁdelete__mutmut_30, 
        'xǁPineconeAdapterǁdelete__mutmut_31': xǁPineconeAdapterǁdelete__mutmut_31, 
        'xǁPineconeAdapterǁdelete__mutmut_32': xǁPineconeAdapterǁdelete__mutmut_32, 
        'xǁPineconeAdapterǁdelete__mutmut_33': xǁPineconeAdapterǁdelete__mutmut_33, 
        'xǁPineconeAdapterǁdelete__mutmut_34': xǁPineconeAdapterǁdelete__mutmut_34, 
        'xǁPineconeAdapterǁdelete__mutmut_35': xǁPineconeAdapterǁdelete__mutmut_35, 
        'xǁPineconeAdapterǁdelete__mutmut_36': xǁPineconeAdapterǁdelete__mutmut_36, 
        'xǁPineconeAdapterǁdelete__mutmut_37': xǁPineconeAdapterǁdelete__mutmut_37, 
        'xǁPineconeAdapterǁdelete__mutmut_38': xǁPineconeAdapterǁdelete__mutmut_38, 
        'xǁPineconeAdapterǁdelete__mutmut_39': xǁPineconeAdapterǁdelete__mutmut_39, 
        'xǁPineconeAdapterǁdelete__mutmut_40': xǁPineconeAdapterǁdelete__mutmut_40, 
        'xǁPineconeAdapterǁdelete__mutmut_41': xǁPineconeAdapterǁdelete__mutmut_41, 
        'xǁPineconeAdapterǁdelete__mutmut_42': xǁPineconeAdapterǁdelete__mutmut_42, 
        'xǁPineconeAdapterǁdelete__mutmut_43': xǁPineconeAdapterǁdelete__mutmut_43, 
        'xǁPineconeAdapterǁdelete__mutmut_44': xǁPineconeAdapterǁdelete__mutmut_44, 
        'xǁPineconeAdapterǁdelete__mutmut_45': xǁPineconeAdapterǁdelete__mutmut_45, 
        'xǁPineconeAdapterǁdelete__mutmut_46': xǁPineconeAdapterǁdelete__mutmut_46, 
        'xǁPineconeAdapterǁdelete__mutmut_47': xǁPineconeAdapterǁdelete__mutmut_47, 
        'xǁPineconeAdapterǁdelete__mutmut_48': xǁPineconeAdapterǁdelete__mutmut_48
    }
    
    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁdelete__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁdelete__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete.__signature__ = _mutmut_signature(xǁPineconeAdapterǁdelete__mutmut_orig)
    xǁPineconeAdapterǁdelete__mutmut_orig.__name__ = 'xǁPineconeAdapterǁdelete'

    def xǁPineconeAdapterǁhealth_check__mutmut_orig(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_1(self) -> dict[str, Any]:
        status = None
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_2(self) -> dict[str, Any]:
        status = "XXokXX" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_3(self) -> dict[str, Any]:
        status = "OK" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_4(self) -> dict[str, Any]:
        status = "ok" if self._connected else "XXdisconnectedXX"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_5(self) -> dict[str, Any]:
        status = "ok" if self._connected else "DISCONNECTED"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_6(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = None
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_7(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"XXstatusXX": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_8(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"STATUS": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_9(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "XXadapterXX": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_10(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "ADAPTER": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_11(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "XXpineconeXX", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_12(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "PINECONE", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_13(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "XXindexXX": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_14(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "INDEX": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_15(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client or hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_16(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected or self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_17(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(None, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_18(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, None):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_19(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr("describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_20(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, ):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_21(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "XXdescribe_index_statsXX"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_22(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "DESCRIBE_INDEX_STATS"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_23(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = None
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_24(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = None
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_25(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["XXstatsXX"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_26(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["STATS"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_27(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning(None, exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_28(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=None)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_29(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning(exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_30(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", )
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_31(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("XXException occurredXX", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_32(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_33(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_34(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=False)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_35(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(None, exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_36(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=None)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_37(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning(exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_38(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", )
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_39(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("XXException occurredXX", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_40(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("exception occurred", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_41(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("EXCEPTION OCCURRED", exc_info=True)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_42(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=False)
            logger.debug("Failed to fetch Pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_43(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug(None)
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_44(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("XXFailed to fetch Pinecone index stats during health_checkXX")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_45(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("failed to fetch pinecone index stats during health_check")
        return info

    def xǁPineconeAdapterǁhealth_check__mutmut_46(self) -> dict[str, Any]:
        status = "ok" if self._connected else "disconnected"
        info = {"status": status, "adapter": "pinecone", "index": self._index_name}
        # Optional: get index stats defensively
        try:
            if self._connected and self._client and hasattr(self._index, "describe_index_stats"):
                stats = self._index.describe_index_stats()
                info["stats"] = stats
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            logger.debug("FAILED TO FETCH PINECONE INDEX STATS DURING HEALTH_CHECK")
        return info
    
    xǁPineconeAdapterǁhealth_check__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPineconeAdapterǁhealth_check__mutmut_1': xǁPineconeAdapterǁhealth_check__mutmut_1, 
        'xǁPineconeAdapterǁhealth_check__mutmut_2': xǁPineconeAdapterǁhealth_check__mutmut_2, 
        'xǁPineconeAdapterǁhealth_check__mutmut_3': xǁPineconeAdapterǁhealth_check__mutmut_3, 
        'xǁPineconeAdapterǁhealth_check__mutmut_4': xǁPineconeAdapterǁhealth_check__mutmut_4, 
        'xǁPineconeAdapterǁhealth_check__mutmut_5': xǁPineconeAdapterǁhealth_check__mutmut_5, 
        'xǁPineconeAdapterǁhealth_check__mutmut_6': xǁPineconeAdapterǁhealth_check__mutmut_6, 
        'xǁPineconeAdapterǁhealth_check__mutmut_7': xǁPineconeAdapterǁhealth_check__mutmut_7, 
        'xǁPineconeAdapterǁhealth_check__mutmut_8': xǁPineconeAdapterǁhealth_check__mutmut_8, 
        'xǁPineconeAdapterǁhealth_check__mutmut_9': xǁPineconeAdapterǁhealth_check__mutmut_9, 
        'xǁPineconeAdapterǁhealth_check__mutmut_10': xǁPineconeAdapterǁhealth_check__mutmut_10, 
        'xǁPineconeAdapterǁhealth_check__mutmut_11': xǁPineconeAdapterǁhealth_check__mutmut_11, 
        'xǁPineconeAdapterǁhealth_check__mutmut_12': xǁPineconeAdapterǁhealth_check__mutmut_12, 
        'xǁPineconeAdapterǁhealth_check__mutmut_13': xǁPineconeAdapterǁhealth_check__mutmut_13, 
        'xǁPineconeAdapterǁhealth_check__mutmut_14': xǁPineconeAdapterǁhealth_check__mutmut_14, 
        'xǁPineconeAdapterǁhealth_check__mutmut_15': xǁPineconeAdapterǁhealth_check__mutmut_15, 
        'xǁPineconeAdapterǁhealth_check__mutmut_16': xǁPineconeAdapterǁhealth_check__mutmut_16, 
        'xǁPineconeAdapterǁhealth_check__mutmut_17': xǁPineconeAdapterǁhealth_check__mutmut_17, 
        'xǁPineconeAdapterǁhealth_check__mutmut_18': xǁPineconeAdapterǁhealth_check__mutmut_18, 
        'xǁPineconeAdapterǁhealth_check__mutmut_19': xǁPineconeAdapterǁhealth_check__mutmut_19, 
        'xǁPineconeAdapterǁhealth_check__mutmut_20': xǁPineconeAdapterǁhealth_check__mutmut_20, 
        'xǁPineconeAdapterǁhealth_check__mutmut_21': xǁPineconeAdapterǁhealth_check__mutmut_21, 
        'xǁPineconeAdapterǁhealth_check__mutmut_22': xǁPineconeAdapterǁhealth_check__mutmut_22, 
        'xǁPineconeAdapterǁhealth_check__mutmut_23': xǁPineconeAdapterǁhealth_check__mutmut_23, 
        'xǁPineconeAdapterǁhealth_check__mutmut_24': xǁPineconeAdapterǁhealth_check__mutmut_24, 
        'xǁPineconeAdapterǁhealth_check__mutmut_25': xǁPineconeAdapterǁhealth_check__mutmut_25, 
        'xǁPineconeAdapterǁhealth_check__mutmut_26': xǁPineconeAdapterǁhealth_check__mutmut_26, 
        'xǁPineconeAdapterǁhealth_check__mutmut_27': xǁPineconeAdapterǁhealth_check__mutmut_27, 
        'xǁPineconeAdapterǁhealth_check__mutmut_28': xǁPineconeAdapterǁhealth_check__mutmut_28, 
        'xǁPineconeAdapterǁhealth_check__mutmut_29': xǁPineconeAdapterǁhealth_check__mutmut_29, 
        'xǁPineconeAdapterǁhealth_check__mutmut_30': xǁPineconeAdapterǁhealth_check__mutmut_30, 
        'xǁPineconeAdapterǁhealth_check__mutmut_31': xǁPineconeAdapterǁhealth_check__mutmut_31, 
        'xǁPineconeAdapterǁhealth_check__mutmut_32': xǁPineconeAdapterǁhealth_check__mutmut_32, 
        'xǁPineconeAdapterǁhealth_check__mutmut_33': xǁPineconeAdapterǁhealth_check__mutmut_33, 
        'xǁPineconeAdapterǁhealth_check__mutmut_34': xǁPineconeAdapterǁhealth_check__mutmut_34, 
        'xǁPineconeAdapterǁhealth_check__mutmut_35': xǁPineconeAdapterǁhealth_check__mutmut_35, 
        'xǁPineconeAdapterǁhealth_check__mutmut_36': xǁPineconeAdapterǁhealth_check__mutmut_36, 
        'xǁPineconeAdapterǁhealth_check__mutmut_37': xǁPineconeAdapterǁhealth_check__mutmut_37, 
        'xǁPineconeAdapterǁhealth_check__mutmut_38': xǁPineconeAdapterǁhealth_check__mutmut_38, 
        'xǁPineconeAdapterǁhealth_check__mutmut_39': xǁPineconeAdapterǁhealth_check__mutmut_39, 
        'xǁPineconeAdapterǁhealth_check__mutmut_40': xǁPineconeAdapterǁhealth_check__mutmut_40, 
        'xǁPineconeAdapterǁhealth_check__mutmut_41': xǁPineconeAdapterǁhealth_check__mutmut_41, 
        'xǁPineconeAdapterǁhealth_check__mutmut_42': xǁPineconeAdapterǁhealth_check__mutmut_42, 
        'xǁPineconeAdapterǁhealth_check__mutmut_43': xǁPineconeAdapterǁhealth_check__mutmut_43, 
        'xǁPineconeAdapterǁhealth_check__mutmut_44': xǁPineconeAdapterǁhealth_check__mutmut_44, 
        'xǁPineconeAdapterǁhealth_check__mutmut_45': xǁPineconeAdapterǁhealth_check__mutmut_45, 
        'xǁPineconeAdapterǁhealth_check__mutmut_46': xǁPineconeAdapterǁhealth_check__mutmut_46
    }
    
    def health_check(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPineconeAdapterǁhealth_check__mutmut_orig"), object.__getattribute__(self, "xǁPineconeAdapterǁhealth_check__mutmut_mutants"), args, kwargs, self)
        return result 
    
    health_check.__signature__ = _mutmut_signature(xǁPineconeAdapterǁhealth_check__mutmut_orig)
    xǁPineconeAdapterǁhealth_check__mutmut_orig.__name__ = 'xǁPineconeAdapterǁhealth_check'
