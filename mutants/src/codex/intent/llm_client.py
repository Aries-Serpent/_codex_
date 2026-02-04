"""
LLM Client - OpenAI API wrapper with safety guards and provenance.

Provides a safe interface to LLM APIs with:
- Rate limiting
- Token budget management
- Provenance recording
- Error handling and fallbacks

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Token budget enforcement (max 8000)
- Rate limiting between calls
- Provenance recording for all calls
- No private data to external LLM by default
- Temperature set to 0 for determinism
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Constants
CHARS_PER_TOKEN = 4  # Approximate character-to-token ratio for English text
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MODEL = "gpt-4o"
MAX_TOKENS = 8000
DEFAULT_TEMPERATURE = 0.0
RATE_LIMIT_DELAY = 1.0
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
class ProvenanceRecord:
    """Record of an LLM API call for auditing."""
    prompt_hash: str
    prompt: str
    response: str
    model: str
    model_version: str
    timestamp: datetime
    temperature: float
    token_count: dict[str, int]
    latency_ms: float
    snapshot_ref: str
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "prompt_hash": self.prompt_hash,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature,
            "token_count": self.token_count,
            "latency_ms": self.latency_ms,
            "snapshot_ref": self.snapshot_ref,
        }
    
    def save(self, directory: Path) -> Path:
        """Save provenance record to file."""
        filename = f"{self.prompt_hash[:16]}.json"
        path = directory / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


def x__hash_prompt__mutmut_orig(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def x__hash_prompt__mutmut_1(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(None).hexdigest()


def x__hash_prompt__mutmut_2(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(prompt.encode(None)).hexdigest()


def x__hash_prompt__mutmut_3(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(prompt.encode("XXutf-8XX")).hexdigest()


def x__hash_prompt__mutmut_4(prompt: str) -> str:
    """Compute SHA256 hash of prompt."""
    return hashlib.sha256(prompt.encode("UTF-8")).hexdigest()

x__hash_prompt__mutmut_mutants : ClassVar[MutantDict] = {
'x__hash_prompt__mutmut_1': x__hash_prompt__mutmut_1, 
    'x__hash_prompt__mutmut_2': x__hash_prompt__mutmut_2, 
    'x__hash_prompt__mutmut_3': x__hash_prompt__mutmut_3, 
    'x__hash_prompt__mutmut_4': x__hash_prompt__mutmut_4
}

def _hash_prompt(*args, **kwargs):
    result = _mutmut_trampoline(x__hash_prompt__mutmut_orig, x__hash_prompt__mutmut_mutants, args, kwargs)
    return result 

_hash_prompt.__signature__ = _mutmut_signature(x__hash_prompt__mutmut_orig)
x__hash_prompt__mutmut_orig.__name__ = 'x__hash_prompt'


def x__truncate_context__mutmut_orig(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] + "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_1(text: str, max_chars: int = 24001) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] + "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_2(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) < max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] + "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_3(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] - "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_4(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars + 100] + "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_5(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 101] + "\n\n[... truncated for token budget ...]"


def x__truncate_context__mutmut_6(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] + "XX\n\n[... truncated for token budget ...]XX"


def x__truncate_context__mutmut_7(text: str, max_chars: int = 24000) -> str:
    """Truncate text to fit within token budget.
    
    Safeguard: Token budget enforcement.
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate with indicator
    return text[:max_chars - 100] + "\n\n[... TRUNCATED FOR TOKEN BUDGET ...]"

x__truncate_context__mutmut_mutants : ClassVar[MutantDict] = {
'x__truncate_context__mutmut_1': x__truncate_context__mutmut_1, 
    'x__truncate_context__mutmut_2': x__truncate_context__mutmut_2, 
    'x__truncate_context__mutmut_3': x__truncate_context__mutmut_3, 
    'x__truncate_context__mutmut_4': x__truncate_context__mutmut_4, 
    'x__truncate_context__mutmut_5': x__truncate_context__mutmut_5, 
    'x__truncate_context__mutmut_6': x__truncate_context__mutmut_6, 
    'x__truncate_context__mutmut_7': x__truncate_context__mutmut_7
}

def _truncate_context(*args, **kwargs):
    result = _mutmut_trampoline(x__truncate_context__mutmut_orig, x__truncate_context__mutmut_mutants, args, kwargs)
    return result 

_truncate_context.__signature__ = _mutmut_signature(x__truncate_context__mutmut_orig)
x__truncate_context__mutmut_orig.__name__ = 'x__truncate_context'


class CodexLLMClient:
    """LLM client with safety guards and provenance tracking.
    
    Provides a safe interface to OpenAI API with:
    - Rate limiting between calls
    - Token budget management
    - Provenance recording for all calls
    - Conservative inference mode
    
    Example:
        >>> client = CodexLLMClient(provenance_dir=Path("llm_provenance"))
        >>> result = client.infer_intent(context)
        >>> print(f"Goal: {result['goal']}")
    """
    
    def xǁCodexLLMClientǁ__init____mutmut_orig(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_1(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "XXXX",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_2(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = False,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_3(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = None
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_4(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = None
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_5(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = None
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_6(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = None
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_7(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = None
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_8(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 1.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_9(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = ""
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_10(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = None
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_11(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get(None)
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_12(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("XXOPENAI_API_KEYXX")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_13(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("openai_api_key")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_14(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = None
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_15(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=None)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_16(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info(None, model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_17(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", None)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_18(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info(model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_19(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", )
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_20(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("XXInitialized OpenAI client with model: %sXX", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_21(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("initialized openai client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_22(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("INITIALIZED OPENAI CLIENT WITH MODEL: %S", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_23(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning(None)
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_24(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("XXOPENAI_API_KEY not set, LLM features disabledXX")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_25(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("openai_api_key not set, llm features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_26(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY NOT SET, LLM FEATURES DISABLED")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_27(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(None)
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_28(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(None, exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_29(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=None)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_30(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(exc_info=True)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_31(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", )
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_32(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=False)
                logger.warning("openai package not installed, LLM features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_33(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning(None)
    
    def xǁCodexLLMClientǁ__init____mutmut_34(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("XXopenai package not installed, LLM features disabledXX")
    
    def xǁCodexLLMClientǁ__init____mutmut_35(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("openai package not installed, llm features disabled")
    
    def xǁCodexLLMClientǁ__init____mutmut_36(
        self,
        model: str = DEFAULT_MODEL,
        provenance_dir: Optional[Path] = None,
        snapshot_ref: str = "",
        allow_external_llm: bool = True,
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model to use
            provenance_dir: Directory for storing provenance records
            snapshot_ref: Reference to the current snapshot
            allow_external_llm: Whether to allow external API calls
        """
        self.model = model
        self.provenance_dir = provenance_dir
        self.snapshot_ref = snapshot_ref
        self.allow_external_llm = allow_external_llm
        self._last_call_time = 0.0
        self._client = None
        
        # Initialize OpenAI client if available
        if allow_external_llm:
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._client = OpenAI(api_key=api_key)
                    logger.info("Initialized OpenAI client with model: %s", model)
                else:
                    logger.warning("OPENAI_API_KEY not set, LLM features disabled")
            except ImportError as e:
                logger.debug(f"ImportError: {e}")
                logger.warning(f"ImportError: {e}", exc_info=True)
                logger.warning("OPENAI PACKAGE NOT INSTALLED, LLM FEATURES DISABLED")
    
    xǁCodexLLMClientǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexLLMClientǁ__init____mutmut_1': xǁCodexLLMClientǁ__init____mutmut_1, 
        'xǁCodexLLMClientǁ__init____mutmut_2': xǁCodexLLMClientǁ__init____mutmut_2, 
        'xǁCodexLLMClientǁ__init____mutmut_3': xǁCodexLLMClientǁ__init____mutmut_3, 
        'xǁCodexLLMClientǁ__init____mutmut_4': xǁCodexLLMClientǁ__init____mutmut_4, 
        'xǁCodexLLMClientǁ__init____mutmut_5': xǁCodexLLMClientǁ__init____mutmut_5, 
        'xǁCodexLLMClientǁ__init____mutmut_6': xǁCodexLLMClientǁ__init____mutmut_6, 
        'xǁCodexLLMClientǁ__init____mutmut_7': xǁCodexLLMClientǁ__init____mutmut_7, 
        'xǁCodexLLMClientǁ__init____mutmut_8': xǁCodexLLMClientǁ__init____mutmut_8, 
        'xǁCodexLLMClientǁ__init____mutmut_9': xǁCodexLLMClientǁ__init____mutmut_9, 
        'xǁCodexLLMClientǁ__init____mutmut_10': xǁCodexLLMClientǁ__init____mutmut_10, 
        'xǁCodexLLMClientǁ__init____mutmut_11': xǁCodexLLMClientǁ__init____mutmut_11, 
        'xǁCodexLLMClientǁ__init____mutmut_12': xǁCodexLLMClientǁ__init____mutmut_12, 
        'xǁCodexLLMClientǁ__init____mutmut_13': xǁCodexLLMClientǁ__init____mutmut_13, 
        'xǁCodexLLMClientǁ__init____mutmut_14': xǁCodexLLMClientǁ__init____mutmut_14, 
        'xǁCodexLLMClientǁ__init____mutmut_15': xǁCodexLLMClientǁ__init____mutmut_15, 
        'xǁCodexLLMClientǁ__init____mutmut_16': xǁCodexLLMClientǁ__init____mutmut_16, 
        'xǁCodexLLMClientǁ__init____mutmut_17': xǁCodexLLMClientǁ__init____mutmut_17, 
        'xǁCodexLLMClientǁ__init____mutmut_18': xǁCodexLLMClientǁ__init____mutmut_18, 
        'xǁCodexLLMClientǁ__init____mutmut_19': xǁCodexLLMClientǁ__init____mutmut_19, 
        'xǁCodexLLMClientǁ__init____mutmut_20': xǁCodexLLMClientǁ__init____mutmut_20, 
        'xǁCodexLLMClientǁ__init____mutmut_21': xǁCodexLLMClientǁ__init____mutmut_21, 
        'xǁCodexLLMClientǁ__init____mutmut_22': xǁCodexLLMClientǁ__init____mutmut_22, 
        'xǁCodexLLMClientǁ__init____mutmut_23': xǁCodexLLMClientǁ__init____mutmut_23, 
        'xǁCodexLLMClientǁ__init____mutmut_24': xǁCodexLLMClientǁ__init____mutmut_24, 
        'xǁCodexLLMClientǁ__init____mutmut_25': xǁCodexLLMClientǁ__init____mutmut_25, 
        'xǁCodexLLMClientǁ__init____mutmut_26': xǁCodexLLMClientǁ__init____mutmut_26, 
        'xǁCodexLLMClientǁ__init____mutmut_27': xǁCodexLLMClientǁ__init____mutmut_27, 
        'xǁCodexLLMClientǁ__init____mutmut_28': xǁCodexLLMClientǁ__init____mutmut_28, 
        'xǁCodexLLMClientǁ__init____mutmut_29': xǁCodexLLMClientǁ__init____mutmut_29, 
        'xǁCodexLLMClientǁ__init____mutmut_30': xǁCodexLLMClientǁ__init____mutmut_30, 
        'xǁCodexLLMClientǁ__init____mutmut_31': xǁCodexLLMClientǁ__init____mutmut_31, 
        'xǁCodexLLMClientǁ__init____mutmut_32': xǁCodexLLMClientǁ__init____mutmut_32, 
        'xǁCodexLLMClientǁ__init____mutmut_33': xǁCodexLLMClientǁ__init____mutmut_33, 
        'xǁCodexLLMClientǁ__init____mutmut_34': xǁCodexLLMClientǁ__init____mutmut_34, 
        'xǁCodexLLMClientǁ__init____mutmut_35': xǁCodexLLMClientǁ__init____mutmut_35, 
        'xǁCodexLLMClientǁ__init____mutmut_36': xǁCodexLLMClientǁ__init____mutmut_36
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexLLMClientǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCodexLLMClientǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCodexLLMClientǁ__init____mutmut_orig)
    xǁCodexLLMClientǁ__init____mutmut_orig.__name__ = 'xǁCodexLLMClientǁ__init__'
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_orig(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_1(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = None
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_2(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(None)
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_3(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get(None, RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_4(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", None))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_5(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get(RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_6(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", ))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_7(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("XXCODEX_LLM_RATE_LIMIT_DELAYXX", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_8(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("codex_llm_rate_limit_delay", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_9(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = None
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_10(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() + self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_11(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed <= delay:
            time.sleep(delay - elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_12(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(None)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_13(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay + elapsed)
        self._last_call_time = time.time()
    
    def xǁCodexLLMClientǁ_rate_limit__mutmut_14(self) -> None:
        """Enforce rate limiting between calls.
        
        Safeguard: Rate limiting.
        """
        delay = float(os.environ.get("CODEX_LLM_RATE_LIMIT_DELAY", RATE_LIMIT_DELAY))
        elapsed = time.time() - self._last_call_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_time = None
    
    xǁCodexLLMClientǁ_rate_limit__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexLLMClientǁ_rate_limit__mutmut_1': xǁCodexLLMClientǁ_rate_limit__mutmut_1, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_2': xǁCodexLLMClientǁ_rate_limit__mutmut_2, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_3': xǁCodexLLMClientǁ_rate_limit__mutmut_3, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_4': xǁCodexLLMClientǁ_rate_limit__mutmut_4, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_5': xǁCodexLLMClientǁ_rate_limit__mutmut_5, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_6': xǁCodexLLMClientǁ_rate_limit__mutmut_6, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_7': xǁCodexLLMClientǁ_rate_limit__mutmut_7, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_8': xǁCodexLLMClientǁ_rate_limit__mutmut_8, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_9': xǁCodexLLMClientǁ_rate_limit__mutmut_9, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_10': xǁCodexLLMClientǁ_rate_limit__mutmut_10, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_11': xǁCodexLLMClientǁ_rate_limit__mutmut_11, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_12': xǁCodexLLMClientǁ_rate_limit__mutmut_12, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_13': xǁCodexLLMClientǁ_rate_limit__mutmut_13, 
        'xǁCodexLLMClientǁ_rate_limit__mutmut_14': xǁCodexLLMClientǁ_rate_limit__mutmut_14
    }
    
    def _rate_limit(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexLLMClientǁ_rate_limit__mutmut_orig"), object.__getattribute__(self, "xǁCodexLLMClientǁ_rate_limit__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _rate_limit.__signature__ = _mutmut_signature(xǁCodexLLMClientǁ_rate_limit__mutmut_orig)
    xǁCodexLLMClientǁ_rate_limit__mutmut_orig.__name__ = 'xǁCodexLLMClientǁ_rate_limit'
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_orig(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_1(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = None
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_2(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(None, indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_3(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=None)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_4(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_5(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), )
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_6(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get(None, {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_7(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", None), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_8(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get({}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_9(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", ), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_10(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("XXstatic_summaryXX", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_11(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("STATIC_SUMMARY", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_12(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=3)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_13(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = None
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_14(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(None)
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_15(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = "XX, XX".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_16(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get(None, [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_17(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", None)[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_18(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get([])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_19(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", )[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_20(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("XXimportsXX", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_21(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("IMPORTS", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_22(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:51])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_23(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = None
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_24(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(None)
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_25(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get(None, ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_26(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", None))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_27(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get(""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_28(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_29(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("XXsource_excerptXX", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_30(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("SOURCE_EXCERPT", ""))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_31(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", "XXXX"))
        
        prompt = f"""## System Prompt
You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Input Context
### Static Analysis Summary
```json
{static_summary}
```

### Imports
{imports}

### Source Code (excerpt)
```python
{source_excerpt}
```

## Output Requirements
Respond with valid JSON matching this schema:
- goal: string (one-sentence purpose)
- actors: list of strings (who/what interacts)
- inputs: list of objects with name, type, required
- outputs: list of objects with name, type
- constraints: list of strings
- side_effects: list of strings
- confidence: float (0.0-1.0)
- assumptions: list of strings (if any)

Return ONLY valid JSON, no explanation or markdown."""
        
        return prompt
    
    def xǁCodexLLMClientǁ_build_intent_prompt__mutmut_32(self, context: dict[str, Any]) -> str:
        """Build intent inference prompt.
        
        Safeguard: Constrained prompt with safety instructions.
        """
        static_summary = json.dumps(context.get("static_summary", {}), indent=2)
        imports = ", ".join(context.get("imports", [])[:50])
        source_excerpt = _truncate_context(context.get("source_excerpt", ""))
        
        prompt = None
        
        return prompt
    
    xǁCodexLLMClientǁ_build_intent_prompt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_1': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_1, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_2': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_2, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_3': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_3, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_4': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_4, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_5': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_5, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_6': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_6, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_7': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_7, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_8': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_8, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_9': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_9, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_10': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_10, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_11': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_11, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_12': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_12, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_13': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_13, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_14': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_14, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_15': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_15, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_16': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_16, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_17': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_17, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_18': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_18, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_19': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_19, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_20': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_20, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_21': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_21, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_22': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_22, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_23': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_23, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_24': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_24, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_25': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_25, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_26': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_26, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_27': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_27, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_28': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_28, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_29': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_29, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_30': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_30, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_31': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_31, 
        'xǁCodexLLMClientǁ_build_intent_prompt__mutmut_32': xǁCodexLLMClientǁ_build_intent_prompt__mutmut_32
    }
    
    def _build_intent_prompt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexLLMClientǁ_build_intent_prompt__mutmut_orig"), object.__getattribute__(self, "xǁCodexLLMClientǁ_build_intent_prompt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _build_intent_prompt.__signature__ = _mutmut_signature(xǁCodexLLMClientǁ_build_intent_prompt__mutmut_orig)
    xǁCodexLLMClientǁ_build_intent_prompt__mutmut_orig.__name__ = 'xǁCodexLLMClientǁ_build_intent_prompt'
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_orig(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_1(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client and not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_2(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_3(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_4(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning(None)
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_5(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("XXLLM client not availableXX")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_6(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("llm client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_7(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM CLIENT NOT AVAILABLE")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_8(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = None
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_9(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(None)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_10(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = None
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_11(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(None)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_12(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) >= MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_13(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS / CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_14(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning(None)
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_15(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("XXPrompt exceeds token budget, truncatingXX")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_16(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_17(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("PROMPT EXCEEDS TOKEN BUDGET, TRUNCATING")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_18(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = None
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_19(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(None, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_20(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, None)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_21(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_22(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, )
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_23(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS / 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_24(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 4)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_25(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = None
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_26(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = None
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_27(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=None,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_28(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=None,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_29(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=None,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_30(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=None,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_31(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_32(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_33(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_34(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_35(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"XXroleXX": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_36(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"ROLE": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_37(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "XXsystemXX", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_38(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "SYSTEM", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_39(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "XXcontentXX": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_40(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "CONTENT": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_41(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "XXYou are a code analysis assistant.XX"},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_42(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "you are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_43(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "YOU ARE A CODE ANALYSIS ASSISTANT."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_44(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"XXroleXX": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_45(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"ROLE": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_46(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "XXuserXX", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_47(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "USER", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_48(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "XXcontentXX": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_49(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "CONTENT": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_50(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1001,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_51(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = None
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_52(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) / 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_53(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() + start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_54(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1001
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_55(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = None
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_56(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content and ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_57(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[1].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_58(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or "XXXX"
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_59(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = None
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_60(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=None,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_61(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=None,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_62(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=None,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_63(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=None,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_64(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=None,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_65(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=None,
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_66(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=None,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_67(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count=None,
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_68(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=None,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_69(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=None,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_70(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_71(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_72(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_73(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_74(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_75(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_76(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_77(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_78(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_79(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_80(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(None, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_81(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, None) else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_82(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr("model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_83(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, ) else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_84(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "XXmodelXX") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_85(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "MODEL") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_86(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(None),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_87(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "XXpromptXX": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_88(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "PROMPT": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_89(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 1,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_90(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "XXcompletionXX": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_91(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "COMPLETION": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_92(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 1,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_93(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=None, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_94(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=None)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_95(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_96(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, )
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_97(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=False, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_98(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=False)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_99(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = None
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_100(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(None)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_101(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info(None, provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_102(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", None)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_103(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info(provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_104(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", )
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_105(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("XXSaved provenance record: %sXX", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_106(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_107(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("SAVED PROVENANCE RECORD: %S", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_108(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = None
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_109(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith(None):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_110(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("XX```XX"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_111(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = None
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_112(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split(None)
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_113(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("XX\nXX")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_114(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = None
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_115(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(None)
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_116(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "XX\nXX".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_117(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[2:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_118(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:+1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_119(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-2])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_120(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = None
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_121(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(None)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_122(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = None
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_123(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["XXprovenance_refXX"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_124(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["PROVENANCE_REF"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_125(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:17]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_126(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(None, e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_127(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", None)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_128(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_129(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", )
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_130(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("XXFailed to parse LLM response as JSON: %sXX", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_131(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("failed to parse llm response as json: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_132(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("FAILED TO PARSE LLM RESPONSE AS JSON: %S", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_133(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(None)
            logger.error("LLM call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_134(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(None, e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_135(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", None)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_136(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_137(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM call failed: %s", )
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_138(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("XXLLM call failed: %sXX", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_139(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("llm call failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁinfer_intent__mutmut_140(self, context: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Infer intent using LLM.
        
        Args:
            context: Analysis context including static report and source
            
        Returns:
            Dictionary with inferred intent or None if unavailable
        """
        if not self._client or not self.allow_external_llm:
            logger.warning("LLM client not available")
            return None
        
        # Build prompt
        prompt = self._build_intent_prompt(context)
        prompt_hash = _hash_prompt(prompt)
        
        # Check token budget using module-level constant
        if len(prompt) > MAX_TOKENS * CHARS_PER_TOKEN:
            logger.warning("Prompt exceeds token budget, truncating")
            prompt = _truncate_context(prompt, MAX_TOKENS * 3)
        
        # Rate limit
        self._rate_limit()
        
        try:
            start_time = time.time()
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=1000,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            response_text = response.choices[0].message.content or ""
            
            # Record provenance
            record = ProvenanceRecord(
                prompt_hash=prompt_hash,
                prompt=prompt,
                response=response_text,
                model=self.model,
                model_version=response.model if hasattr(response, "model") else self.model,
                timestamp=datetime.now(timezone.utc),
                temperature=DEFAULT_TEMPERATURE,
                token_count={
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                },
                latency_ms=latency_ms,
                snapshot_ref=self.snapshot_ref,
            )
            
            if self.provenance_dir:
                self.provenance_dir.mkdir(parents=True, exist_ok=True)
                provenance_path = record.save(self.provenance_dir)
                logger.info("Saved provenance record: %s", provenance_path)
            
            # Parse response
            try:
                # Clean up response (remove markdown code blocks if present)
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                
                result = json.loads(clean_response)
                result["provenance_ref"] = prompt_hash[:16]
                return result
                
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response as JSON: %s", e)
                return None
                
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("LLM CALL FAILED: %S", e)
            return None
    
    xǁCodexLLMClientǁinfer_intent__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexLLMClientǁinfer_intent__mutmut_1': xǁCodexLLMClientǁinfer_intent__mutmut_1, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_2': xǁCodexLLMClientǁinfer_intent__mutmut_2, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_3': xǁCodexLLMClientǁinfer_intent__mutmut_3, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_4': xǁCodexLLMClientǁinfer_intent__mutmut_4, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_5': xǁCodexLLMClientǁinfer_intent__mutmut_5, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_6': xǁCodexLLMClientǁinfer_intent__mutmut_6, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_7': xǁCodexLLMClientǁinfer_intent__mutmut_7, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_8': xǁCodexLLMClientǁinfer_intent__mutmut_8, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_9': xǁCodexLLMClientǁinfer_intent__mutmut_9, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_10': xǁCodexLLMClientǁinfer_intent__mutmut_10, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_11': xǁCodexLLMClientǁinfer_intent__mutmut_11, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_12': xǁCodexLLMClientǁinfer_intent__mutmut_12, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_13': xǁCodexLLMClientǁinfer_intent__mutmut_13, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_14': xǁCodexLLMClientǁinfer_intent__mutmut_14, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_15': xǁCodexLLMClientǁinfer_intent__mutmut_15, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_16': xǁCodexLLMClientǁinfer_intent__mutmut_16, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_17': xǁCodexLLMClientǁinfer_intent__mutmut_17, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_18': xǁCodexLLMClientǁinfer_intent__mutmut_18, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_19': xǁCodexLLMClientǁinfer_intent__mutmut_19, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_20': xǁCodexLLMClientǁinfer_intent__mutmut_20, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_21': xǁCodexLLMClientǁinfer_intent__mutmut_21, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_22': xǁCodexLLMClientǁinfer_intent__mutmut_22, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_23': xǁCodexLLMClientǁinfer_intent__mutmut_23, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_24': xǁCodexLLMClientǁinfer_intent__mutmut_24, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_25': xǁCodexLLMClientǁinfer_intent__mutmut_25, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_26': xǁCodexLLMClientǁinfer_intent__mutmut_26, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_27': xǁCodexLLMClientǁinfer_intent__mutmut_27, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_28': xǁCodexLLMClientǁinfer_intent__mutmut_28, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_29': xǁCodexLLMClientǁinfer_intent__mutmut_29, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_30': xǁCodexLLMClientǁinfer_intent__mutmut_30, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_31': xǁCodexLLMClientǁinfer_intent__mutmut_31, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_32': xǁCodexLLMClientǁinfer_intent__mutmut_32, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_33': xǁCodexLLMClientǁinfer_intent__mutmut_33, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_34': xǁCodexLLMClientǁinfer_intent__mutmut_34, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_35': xǁCodexLLMClientǁinfer_intent__mutmut_35, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_36': xǁCodexLLMClientǁinfer_intent__mutmut_36, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_37': xǁCodexLLMClientǁinfer_intent__mutmut_37, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_38': xǁCodexLLMClientǁinfer_intent__mutmut_38, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_39': xǁCodexLLMClientǁinfer_intent__mutmut_39, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_40': xǁCodexLLMClientǁinfer_intent__mutmut_40, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_41': xǁCodexLLMClientǁinfer_intent__mutmut_41, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_42': xǁCodexLLMClientǁinfer_intent__mutmut_42, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_43': xǁCodexLLMClientǁinfer_intent__mutmut_43, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_44': xǁCodexLLMClientǁinfer_intent__mutmut_44, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_45': xǁCodexLLMClientǁinfer_intent__mutmut_45, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_46': xǁCodexLLMClientǁinfer_intent__mutmut_46, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_47': xǁCodexLLMClientǁinfer_intent__mutmut_47, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_48': xǁCodexLLMClientǁinfer_intent__mutmut_48, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_49': xǁCodexLLMClientǁinfer_intent__mutmut_49, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_50': xǁCodexLLMClientǁinfer_intent__mutmut_50, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_51': xǁCodexLLMClientǁinfer_intent__mutmut_51, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_52': xǁCodexLLMClientǁinfer_intent__mutmut_52, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_53': xǁCodexLLMClientǁinfer_intent__mutmut_53, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_54': xǁCodexLLMClientǁinfer_intent__mutmut_54, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_55': xǁCodexLLMClientǁinfer_intent__mutmut_55, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_56': xǁCodexLLMClientǁinfer_intent__mutmut_56, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_57': xǁCodexLLMClientǁinfer_intent__mutmut_57, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_58': xǁCodexLLMClientǁinfer_intent__mutmut_58, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_59': xǁCodexLLMClientǁinfer_intent__mutmut_59, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_60': xǁCodexLLMClientǁinfer_intent__mutmut_60, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_61': xǁCodexLLMClientǁinfer_intent__mutmut_61, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_62': xǁCodexLLMClientǁinfer_intent__mutmut_62, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_63': xǁCodexLLMClientǁinfer_intent__mutmut_63, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_64': xǁCodexLLMClientǁinfer_intent__mutmut_64, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_65': xǁCodexLLMClientǁinfer_intent__mutmut_65, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_66': xǁCodexLLMClientǁinfer_intent__mutmut_66, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_67': xǁCodexLLMClientǁinfer_intent__mutmut_67, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_68': xǁCodexLLMClientǁinfer_intent__mutmut_68, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_69': xǁCodexLLMClientǁinfer_intent__mutmut_69, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_70': xǁCodexLLMClientǁinfer_intent__mutmut_70, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_71': xǁCodexLLMClientǁinfer_intent__mutmut_71, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_72': xǁCodexLLMClientǁinfer_intent__mutmut_72, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_73': xǁCodexLLMClientǁinfer_intent__mutmut_73, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_74': xǁCodexLLMClientǁinfer_intent__mutmut_74, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_75': xǁCodexLLMClientǁinfer_intent__mutmut_75, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_76': xǁCodexLLMClientǁinfer_intent__mutmut_76, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_77': xǁCodexLLMClientǁinfer_intent__mutmut_77, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_78': xǁCodexLLMClientǁinfer_intent__mutmut_78, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_79': xǁCodexLLMClientǁinfer_intent__mutmut_79, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_80': xǁCodexLLMClientǁinfer_intent__mutmut_80, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_81': xǁCodexLLMClientǁinfer_intent__mutmut_81, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_82': xǁCodexLLMClientǁinfer_intent__mutmut_82, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_83': xǁCodexLLMClientǁinfer_intent__mutmut_83, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_84': xǁCodexLLMClientǁinfer_intent__mutmut_84, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_85': xǁCodexLLMClientǁinfer_intent__mutmut_85, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_86': xǁCodexLLMClientǁinfer_intent__mutmut_86, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_87': xǁCodexLLMClientǁinfer_intent__mutmut_87, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_88': xǁCodexLLMClientǁinfer_intent__mutmut_88, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_89': xǁCodexLLMClientǁinfer_intent__mutmut_89, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_90': xǁCodexLLMClientǁinfer_intent__mutmut_90, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_91': xǁCodexLLMClientǁinfer_intent__mutmut_91, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_92': xǁCodexLLMClientǁinfer_intent__mutmut_92, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_93': xǁCodexLLMClientǁinfer_intent__mutmut_93, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_94': xǁCodexLLMClientǁinfer_intent__mutmut_94, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_95': xǁCodexLLMClientǁinfer_intent__mutmut_95, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_96': xǁCodexLLMClientǁinfer_intent__mutmut_96, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_97': xǁCodexLLMClientǁinfer_intent__mutmut_97, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_98': xǁCodexLLMClientǁinfer_intent__mutmut_98, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_99': xǁCodexLLMClientǁinfer_intent__mutmut_99, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_100': xǁCodexLLMClientǁinfer_intent__mutmut_100, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_101': xǁCodexLLMClientǁinfer_intent__mutmut_101, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_102': xǁCodexLLMClientǁinfer_intent__mutmut_102, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_103': xǁCodexLLMClientǁinfer_intent__mutmut_103, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_104': xǁCodexLLMClientǁinfer_intent__mutmut_104, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_105': xǁCodexLLMClientǁinfer_intent__mutmut_105, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_106': xǁCodexLLMClientǁinfer_intent__mutmut_106, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_107': xǁCodexLLMClientǁinfer_intent__mutmut_107, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_108': xǁCodexLLMClientǁinfer_intent__mutmut_108, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_109': xǁCodexLLMClientǁinfer_intent__mutmut_109, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_110': xǁCodexLLMClientǁinfer_intent__mutmut_110, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_111': xǁCodexLLMClientǁinfer_intent__mutmut_111, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_112': xǁCodexLLMClientǁinfer_intent__mutmut_112, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_113': xǁCodexLLMClientǁinfer_intent__mutmut_113, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_114': xǁCodexLLMClientǁinfer_intent__mutmut_114, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_115': xǁCodexLLMClientǁinfer_intent__mutmut_115, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_116': xǁCodexLLMClientǁinfer_intent__mutmut_116, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_117': xǁCodexLLMClientǁinfer_intent__mutmut_117, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_118': xǁCodexLLMClientǁinfer_intent__mutmut_118, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_119': xǁCodexLLMClientǁinfer_intent__mutmut_119, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_120': xǁCodexLLMClientǁinfer_intent__mutmut_120, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_121': xǁCodexLLMClientǁinfer_intent__mutmut_121, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_122': xǁCodexLLMClientǁinfer_intent__mutmut_122, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_123': xǁCodexLLMClientǁinfer_intent__mutmut_123, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_124': xǁCodexLLMClientǁinfer_intent__mutmut_124, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_125': xǁCodexLLMClientǁinfer_intent__mutmut_125, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_126': xǁCodexLLMClientǁinfer_intent__mutmut_126, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_127': xǁCodexLLMClientǁinfer_intent__mutmut_127, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_128': xǁCodexLLMClientǁinfer_intent__mutmut_128, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_129': xǁCodexLLMClientǁinfer_intent__mutmut_129, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_130': xǁCodexLLMClientǁinfer_intent__mutmut_130, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_131': xǁCodexLLMClientǁinfer_intent__mutmut_131, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_132': xǁCodexLLMClientǁinfer_intent__mutmut_132, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_133': xǁCodexLLMClientǁinfer_intent__mutmut_133, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_134': xǁCodexLLMClientǁinfer_intent__mutmut_134, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_135': xǁCodexLLMClientǁinfer_intent__mutmut_135, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_136': xǁCodexLLMClientǁinfer_intent__mutmut_136, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_137': xǁCodexLLMClientǁinfer_intent__mutmut_137, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_138': xǁCodexLLMClientǁinfer_intent__mutmut_138, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_139': xǁCodexLLMClientǁinfer_intent__mutmut_139, 
        'xǁCodexLLMClientǁinfer_intent__mutmut_140': xǁCodexLLMClientǁinfer_intent__mutmut_140
    }
    
    def infer_intent(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexLLMClientǁinfer_intent__mutmut_orig"), object.__getattribute__(self, "xǁCodexLLMClientǁinfer_intent__mutmut_mutants"), args, kwargs, self)
        return result 
    
    infer_intent.__signature__ = _mutmut_signature(xǁCodexLLMClientǁinfer_intent__mutmut_orig)
    xǁCodexLLMClientǁinfer_intent__mutmut_orig.__name__ = 'xǁCodexLLMClientǁinfer_intent'
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_orig(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_1(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client and not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_2(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_3(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_4(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = None
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_5(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(None, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_6(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, None)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_7(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_8(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, )}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_9(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8001)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_10(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = None
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_11(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=None,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_12(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=None,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_13(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=None,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_14(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=None,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_15(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_16(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_17(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_18(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_19(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"XXroleXX": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_20(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"ROLE": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_21(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "XXuserXX", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_22(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "USER", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_23(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "XXcontentXX": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_24(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "CONTENT": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_25(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=201,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_26(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[1].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_27(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(None)
            logger.error("Summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_28(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(None, e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_29(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", None)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_30(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_31(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("Summarization failed: %s", )
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_32(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("XXSummarization failed: %sXX", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_33(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("summarization failed: %s", e)
            return None
    
    def xǁCodexLLMClientǁsummarize_code__mutmut_34(self, source: str) -> Optional[str]:
        """Generate a brief summary of code.
        
        Args:
            source: Source code to summarize
            
        Returns:
            Summary string or None
        """
        if not self._client or not self.allow_external_llm:
            return None
        
        prompt = f"""Summarize this Python code in one paragraph:

```python
{_truncate_context(source, 8000)}
```

Be concise and factual. Do not invent functionality not present in the code."""
        
        self._rate_limit()
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=200,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error("SUMMARIZATION FAILED: %S", e)
            return None
    
    xǁCodexLLMClientǁsummarize_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexLLMClientǁsummarize_code__mutmut_1': xǁCodexLLMClientǁsummarize_code__mutmut_1, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_2': xǁCodexLLMClientǁsummarize_code__mutmut_2, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_3': xǁCodexLLMClientǁsummarize_code__mutmut_3, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_4': xǁCodexLLMClientǁsummarize_code__mutmut_4, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_5': xǁCodexLLMClientǁsummarize_code__mutmut_5, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_6': xǁCodexLLMClientǁsummarize_code__mutmut_6, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_7': xǁCodexLLMClientǁsummarize_code__mutmut_7, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_8': xǁCodexLLMClientǁsummarize_code__mutmut_8, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_9': xǁCodexLLMClientǁsummarize_code__mutmut_9, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_10': xǁCodexLLMClientǁsummarize_code__mutmut_10, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_11': xǁCodexLLMClientǁsummarize_code__mutmut_11, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_12': xǁCodexLLMClientǁsummarize_code__mutmut_12, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_13': xǁCodexLLMClientǁsummarize_code__mutmut_13, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_14': xǁCodexLLMClientǁsummarize_code__mutmut_14, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_15': xǁCodexLLMClientǁsummarize_code__mutmut_15, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_16': xǁCodexLLMClientǁsummarize_code__mutmut_16, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_17': xǁCodexLLMClientǁsummarize_code__mutmut_17, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_18': xǁCodexLLMClientǁsummarize_code__mutmut_18, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_19': xǁCodexLLMClientǁsummarize_code__mutmut_19, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_20': xǁCodexLLMClientǁsummarize_code__mutmut_20, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_21': xǁCodexLLMClientǁsummarize_code__mutmut_21, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_22': xǁCodexLLMClientǁsummarize_code__mutmut_22, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_23': xǁCodexLLMClientǁsummarize_code__mutmut_23, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_24': xǁCodexLLMClientǁsummarize_code__mutmut_24, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_25': xǁCodexLLMClientǁsummarize_code__mutmut_25, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_26': xǁCodexLLMClientǁsummarize_code__mutmut_26, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_27': xǁCodexLLMClientǁsummarize_code__mutmut_27, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_28': xǁCodexLLMClientǁsummarize_code__mutmut_28, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_29': xǁCodexLLMClientǁsummarize_code__mutmut_29, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_30': xǁCodexLLMClientǁsummarize_code__mutmut_30, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_31': xǁCodexLLMClientǁsummarize_code__mutmut_31, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_32': xǁCodexLLMClientǁsummarize_code__mutmut_32, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_33': xǁCodexLLMClientǁsummarize_code__mutmut_33, 
        'xǁCodexLLMClientǁsummarize_code__mutmut_34': xǁCodexLLMClientǁsummarize_code__mutmut_34
    }
    
    def summarize_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexLLMClientǁsummarize_code__mutmut_orig"), object.__getattribute__(self, "xǁCodexLLMClientǁsummarize_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    summarize_code.__signature__ = _mutmut_signature(xǁCodexLLMClientǁsummarize_code__mutmut_orig)
    xǁCodexLLMClientǁsummarize_code__mutmut_orig.__name__ = 'xǁCodexLLMClientǁsummarize_code'
