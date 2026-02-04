"""
OpenAI Client Configuration for _codex_ Autonomous Agents
Leverages Aries-Serpent organization custom models (32 models)

Author: mbaetiong
Generated: 2025-12-17
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Literal

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)

# Model cost tiers
CostTier = Literal["low", "medium", "high", "very-high"]
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
class ModelConfig:
    """Configuration for an OpenAI model."""

    context_length: int
    reasoning: bool = False
    cost_tier: CostTier = "medium"
    input_cost_per_1k: float = 0.01
    output_cost_per_1k: float = 0.03


# Available models in GITHUB_CODEX organization
AVAILABLE_MODELS: dict[str, ModelConfig] = {
    # Reasoning models (o-series)
    "o1-preview": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="high",
        input_cost_per_1k=0.015,
        output_cost_per_1k=0.06,
    ),
    "o1-mini": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="medium",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.012,
    ),
    "o3-mini": ModelConfig(
        128000,
        reasoning=True,
        cost_tier="medium",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.012,
    ),
    # GPT-4 Turbo models
    "gpt-4-turbo": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03
    ),
    "gpt-4-turbo-preview": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.01, output_cost_per_1k=0.03
    ),
    # GPT-4 models
    "gpt-4": ModelConfig(
        8192, cost_tier="high", input_cost_per_1k=0.03, output_cost_per_1k=0.06
    ),
    "gpt-4-32k": ModelConfig(
        32768, cost_tier="very-high", input_cost_per_1k=0.06, output_cost_per_1k=0.12
    ),
    # GPT-4o models
    "gpt-4o": ModelConfig(
        128000, cost_tier="medium", input_cost_per_1k=0.005, output_cost_per_1k=0.015
    ),
    "gpt-4o-mini": ModelConfig(
        128000, cost_tier="low", input_cost_per_1k=0.00015, output_cost_per_1k=0.0006
    ),
    # GPT-3.5 models
    "gpt-3.5-turbo": ModelConfig(
        16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015
    ),
    "gpt-3.5-turbo-16k": ModelConfig(
        16385, cost_tier="low", input_cost_per_1k=0.0005, output_cost_per_1k=0.0015
    ),
}


@dataclass
class ExecutionResult:
    """Result of an agent task execution."""

    success: bool
    model: str
    response: str | None = None
    error: str | None = None
    usage: dict[str, int] | None = None
    duration_ms: int = 0
    estimated_cost: float = 0.0


@dataclass
class AuditLogEntry:
    """Audit log entry for API usage tracking."""

    timestamp: str
    task_id: str
    model: str
    tokens_used: int
    duration_ms: int
    estimated_cost: float
    success: bool


# Safeguard: Validate API key format
# Supports: sk-<32+ alphanumeric chars> and sk-<project>-<alphanumeric chars> formats
API_KEY_PATTERN = re.compile(r"^sk-[a-zA-Z0-9-]{32,}$")
MAX_API_KEY_LENGTH = 256
MAX_AUDIT_LOG_SIZE = 1000


def x__validate_api_key__mutmut_orig(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_1(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key and not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_2(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_3(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_4(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return True
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_5(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) >= MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_6(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return True
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(api_key))


def x__validate_api_key__mutmut_7(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(None)


def x__validate_api_key__mutmut_8(api_key: str | None) -> bool:
    """Validate API key format (safeguard).

    Supports standard OpenAI API key formats:
    - sk-<32+ alphanumeric chars>
    - sk-<project>-<alphanumeric chars> (project-scoped keys)

    Args:
        api_key: The API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    # Bounds check (safeguard)
    if len(api_key) > MAX_API_KEY_LENGTH:
        return False
    # Pattern validation (safeguard)
    return bool(API_KEY_PATTERN.match(None))

x__validate_api_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_api_key__mutmut_1': x__validate_api_key__mutmut_1, 
    'x__validate_api_key__mutmut_2': x__validate_api_key__mutmut_2, 
    'x__validate_api_key__mutmut_3': x__validate_api_key__mutmut_3, 
    'x__validate_api_key__mutmut_4': x__validate_api_key__mutmut_4, 
    'x__validate_api_key__mutmut_5': x__validate_api_key__mutmut_5, 
    'x__validate_api_key__mutmut_6': x__validate_api_key__mutmut_6, 
    'x__validate_api_key__mutmut_7': x__validate_api_key__mutmut_7, 
    'x__validate_api_key__mutmut_8': x__validate_api_key__mutmut_8
}

def _validate_api_key(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_api_key__mutmut_orig, x__validate_api_key__mutmut_mutants, args, kwargs)
    return result 

_validate_api_key.__signature__ = _mutmut_signature(x__validate_api_key__mutmut_orig)
x__validate_api_key__mutmut_orig.__name__ = 'x__validate_api_key'


class CodexOpenAIClient:
    """
    OpenAI client for _codex_ autonomous agents.

    Features:
    - Intelligent model selection based on task requirements
    - Cost estimation and tracking
    - Audit logging for compliance
    - Rate limiting support

    Safeguards:
    - Input validation on API key and parameters
    - Bounds checking on audit log size
    - Defensive error handling
    """

    def xǁCodexOpenAIClientǁ__init____mutmut_orig(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_1(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = None

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_2(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") and os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_3(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv(None) or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_4(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("XXOPENAI_API_KEYXX") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_5(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("openai_api_key") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_6(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv(None)

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_7(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("XXGITHUB_CODEXXX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_8(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("github_codex")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_9(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_10(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                None
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_11(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "XXOPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode.XX"
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_12(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "openai_api_key or github_codex not found. agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_13(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY OR GITHUB_CODEX NOT FOUND. AGENT WILL OPERATE IN DRY-RUN MODE."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_14(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = None
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_15(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = False
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_16(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = None

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_17(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = True

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_18(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = None
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_19(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = None

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_20(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = None
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_21(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 1
        self._tokens_this_minute = 0
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_22(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = None
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_23(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 1
        self._minute_start = time.time()

    def xǁCodexOpenAIClientǁ__init____mutmut_24(self) -> None:
        """Initialize the OpenAI client."""
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_CODEX")

        # Safeguard: Validate API key presence (but not format for flexibility)
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY or GITHUB_CODEX not found. Agent will operate in dry-run mode."
            )
            self._dry_run = True
        else:
            self._dry_run = False

        self.models = AVAILABLE_MODELS
        self.audit_log: list[AuditLogEntry] = []

        # Rate limiting state
        self._requests_this_minute = 0
        self._tokens_this_minute = 0
        self._minute_start = None
    
    xǁCodexOpenAIClientǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁ__init____mutmut_1': xǁCodexOpenAIClientǁ__init____mutmut_1, 
        'xǁCodexOpenAIClientǁ__init____mutmut_2': xǁCodexOpenAIClientǁ__init____mutmut_2, 
        'xǁCodexOpenAIClientǁ__init____mutmut_3': xǁCodexOpenAIClientǁ__init____mutmut_3, 
        'xǁCodexOpenAIClientǁ__init____mutmut_4': xǁCodexOpenAIClientǁ__init____mutmut_4, 
        'xǁCodexOpenAIClientǁ__init____mutmut_5': xǁCodexOpenAIClientǁ__init____mutmut_5, 
        'xǁCodexOpenAIClientǁ__init____mutmut_6': xǁCodexOpenAIClientǁ__init____mutmut_6, 
        'xǁCodexOpenAIClientǁ__init____mutmut_7': xǁCodexOpenAIClientǁ__init____mutmut_7, 
        'xǁCodexOpenAIClientǁ__init____mutmut_8': xǁCodexOpenAIClientǁ__init____mutmut_8, 
        'xǁCodexOpenAIClientǁ__init____mutmut_9': xǁCodexOpenAIClientǁ__init____mutmut_9, 
        'xǁCodexOpenAIClientǁ__init____mutmut_10': xǁCodexOpenAIClientǁ__init____mutmut_10, 
        'xǁCodexOpenAIClientǁ__init____mutmut_11': xǁCodexOpenAIClientǁ__init____mutmut_11, 
        'xǁCodexOpenAIClientǁ__init____mutmut_12': xǁCodexOpenAIClientǁ__init____mutmut_12, 
        'xǁCodexOpenAIClientǁ__init____mutmut_13': xǁCodexOpenAIClientǁ__init____mutmut_13, 
        'xǁCodexOpenAIClientǁ__init____mutmut_14': xǁCodexOpenAIClientǁ__init____mutmut_14, 
        'xǁCodexOpenAIClientǁ__init____mutmut_15': xǁCodexOpenAIClientǁ__init____mutmut_15, 
        'xǁCodexOpenAIClientǁ__init____mutmut_16': xǁCodexOpenAIClientǁ__init____mutmut_16, 
        'xǁCodexOpenAIClientǁ__init____mutmut_17': xǁCodexOpenAIClientǁ__init____mutmut_17, 
        'xǁCodexOpenAIClientǁ__init____mutmut_18': xǁCodexOpenAIClientǁ__init____mutmut_18, 
        'xǁCodexOpenAIClientǁ__init____mutmut_19': xǁCodexOpenAIClientǁ__init____mutmut_19, 
        'xǁCodexOpenAIClientǁ__init____mutmut_20': xǁCodexOpenAIClientǁ__init____mutmut_20, 
        'xǁCodexOpenAIClientǁ__init____mutmut_21': xǁCodexOpenAIClientǁ__init____mutmut_21, 
        'xǁCodexOpenAIClientǁ__init____mutmut_22': xǁCodexOpenAIClientǁ__init____mutmut_22, 
        'xǁCodexOpenAIClientǁ__init____mutmut_23': xǁCodexOpenAIClientǁ__init____mutmut_23, 
        'xǁCodexOpenAIClientǁ__init____mutmut_24': xǁCodexOpenAIClientǁ__init____mutmut_24
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁ__init____mutmut_orig)
    xǁCodexOpenAIClientǁ__init____mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁ__init__'

    def xǁCodexOpenAIClientǁselect_model__mutmut_orig(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_1(
        self,
        *,
        requires_reasoning: bool = True,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_2(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "XXmediumXX",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_3(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "MEDIUM",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_4(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4097,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_5(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str) or preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_6(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model or isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_7(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model not in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_8(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = None
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_9(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["XXlowXX", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_10(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["LOW", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_11(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "XXmediumXX", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_12(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "MEDIUM", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_13(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "XXhighXX", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_14(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "HIGH", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_15(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "XXvery-highXX"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_16(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "VERY-HIGH"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_17(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = None

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_18(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(None)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_19(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.rindex(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_20(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = None

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_21(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index or (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_22(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context or cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_23(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length > min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_24(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(None) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_25(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.rindex(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_26(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) < max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_27(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning and config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_28(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_29(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_30(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "XXgpt-4o-miniXX"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_31(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "GPT-4O-MINI"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_32(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=None)

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_33(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: None)

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_34(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(None))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_35(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.rindex(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_36(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[2].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_37(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = None
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_38(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[2].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_39(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[1][0]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_40(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][1]

        return candidates[0][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_41(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[1][0]

    def xǁCodexOpenAIClientǁselect_model__mutmut_42(
        self,
        *,
        requires_reasoning: bool = False,
        max_cost: CostTier = "medium",
        min_context: int = 4096,
        preferred_model: str | None = None,
    ) -> str:
        """
        Intelligently select the optimal model based on task requirements.

        Args:
            requires_reasoning: Whether the task requires chain-of-thought reasoning
            max_cost: Maximum acceptable cost tier
            min_context: Minimum required context window
            preferred_model: Explicitly preferred model (bypasses auto-selection)

        Returns:
            Selected model name
        """
        # Use preferred model if specified and valid (safeguard: validate input)
        if (
            preferred_model
            and isinstance(preferred_model, str)
            and preferred_model in self.models
        ):
            return preferred_model

        cost_order = ["low", "medium", "high", "very-high"]
        max_cost_index = cost_order.index(max_cost)

        # Filter models by requirements
        candidates = [
            (name, config)
            for name, config in self.models.items()
            if config.context_length >= min_context
            and cost_order.index(config.cost_tier) <= max_cost_index
            and (not requires_reasoning or config.reasoning)
        ]

        if not candidates:
            # Fallback to gpt-4o-mini (most cost-effective)
            return "gpt-4o-mini"

        # Sort by cost efficiency (lower cost tier first)
        candidates.sort(key=lambda x: cost_order.index(x[1].cost_tier))

        # Prefer reasoning models if required
        if requires_reasoning:
            reasoning_candidates = [c for c in candidates if c[1].reasoning]
            if reasoning_candidates:
                return reasoning_candidates[0][0]

        return candidates[0][1]
    
    xǁCodexOpenAIClientǁselect_model__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁselect_model__mutmut_1': xǁCodexOpenAIClientǁselect_model__mutmut_1, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_2': xǁCodexOpenAIClientǁselect_model__mutmut_2, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_3': xǁCodexOpenAIClientǁselect_model__mutmut_3, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_4': xǁCodexOpenAIClientǁselect_model__mutmut_4, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_5': xǁCodexOpenAIClientǁselect_model__mutmut_5, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_6': xǁCodexOpenAIClientǁselect_model__mutmut_6, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_7': xǁCodexOpenAIClientǁselect_model__mutmut_7, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_8': xǁCodexOpenAIClientǁselect_model__mutmut_8, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_9': xǁCodexOpenAIClientǁselect_model__mutmut_9, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_10': xǁCodexOpenAIClientǁselect_model__mutmut_10, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_11': xǁCodexOpenAIClientǁselect_model__mutmut_11, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_12': xǁCodexOpenAIClientǁselect_model__mutmut_12, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_13': xǁCodexOpenAIClientǁselect_model__mutmut_13, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_14': xǁCodexOpenAIClientǁselect_model__mutmut_14, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_15': xǁCodexOpenAIClientǁselect_model__mutmut_15, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_16': xǁCodexOpenAIClientǁselect_model__mutmut_16, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_17': xǁCodexOpenAIClientǁselect_model__mutmut_17, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_18': xǁCodexOpenAIClientǁselect_model__mutmut_18, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_19': xǁCodexOpenAIClientǁselect_model__mutmut_19, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_20': xǁCodexOpenAIClientǁselect_model__mutmut_20, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_21': xǁCodexOpenAIClientǁselect_model__mutmut_21, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_22': xǁCodexOpenAIClientǁselect_model__mutmut_22, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_23': xǁCodexOpenAIClientǁselect_model__mutmut_23, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_24': xǁCodexOpenAIClientǁselect_model__mutmut_24, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_25': xǁCodexOpenAIClientǁselect_model__mutmut_25, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_26': xǁCodexOpenAIClientǁselect_model__mutmut_26, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_27': xǁCodexOpenAIClientǁselect_model__mutmut_27, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_28': xǁCodexOpenAIClientǁselect_model__mutmut_28, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_29': xǁCodexOpenAIClientǁselect_model__mutmut_29, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_30': xǁCodexOpenAIClientǁselect_model__mutmut_30, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_31': xǁCodexOpenAIClientǁselect_model__mutmut_31, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_32': xǁCodexOpenAIClientǁselect_model__mutmut_32, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_33': xǁCodexOpenAIClientǁselect_model__mutmut_33, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_34': xǁCodexOpenAIClientǁselect_model__mutmut_34, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_35': xǁCodexOpenAIClientǁselect_model__mutmut_35, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_36': xǁCodexOpenAIClientǁselect_model__mutmut_36, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_37': xǁCodexOpenAIClientǁselect_model__mutmut_37, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_38': xǁCodexOpenAIClientǁselect_model__mutmut_38, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_39': xǁCodexOpenAIClientǁselect_model__mutmut_39, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_40': xǁCodexOpenAIClientǁselect_model__mutmut_40, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_41': xǁCodexOpenAIClientǁselect_model__mutmut_41, 
        'xǁCodexOpenAIClientǁselect_model__mutmut_42': xǁCodexOpenAIClientǁselect_model__mutmut_42
    }
    
    def select_model(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁselect_model__mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁselect_model__mutmut_mutants"), args, kwargs, self)
        return result 
    
    select_model.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁselect_model__mutmut_orig)
    xǁCodexOpenAIClientǁselect_model__mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁselect_model'

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_orig(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_1(self, task_type: str = "XXgeneralXX") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_2(self, task_type: str = "GENERAL") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_3(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv(None, "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_4(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", None)}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_5(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_6(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", )}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_7(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("XXREPO_CONTEXTXX", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_8(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("repo_context", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_9(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "XX_codex_XX")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_10(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_CODEX_")}
- Organization: {os.getenv("ORG_CONTEXT", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_11(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv(None, "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_12(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", None)}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_13(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_14(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", )}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_15(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("XXORG_CONTEXTXX", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_16(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("org_context", "Aries-Serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_17(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "XXAries-SerpentXX")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_18(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "aries-serpent")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""

    def xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_19(self, task_type: str = "general") -> str:
        """Build the system prompt with _codex_ context."""
        return f"""You are an autonomous AI agent operating within the Aries-Serpent/_codex_ repository.

Your capabilities:
- Full access to 32 OpenAI custom models via GITHUB_CODEX API key
- Autonomous decision-making within defined safety boundaries
- Code generation, analysis, and modification
- GitHub API integration (issues, PRs, workflows)
- Multi-agent coordination and task decomposition

Current context:
- Repository: {os.getenv("REPO_CONTEXT", "_codex_")}
- Organization: {os.getenv("ORG_CONTEXT", "ARIES-SERPENT")}
- Task Type: {task_type}

Physics-optimized principles:
- 🛤️ Path: Optimize for least resistance
- 🔄 Fields: Propagate changes efficiently
- 👁️ Patterns: Recognize and apply successful patterns
- 🔀 Redundancy: Build fallback mechanisms
- ⚖️ Balance: Trade off speed vs. accuracy appropriately

Execute the user's request autonomously, following _codex_ patterns and best practices."""
    
    xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_1': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_1, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_2': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_2, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_3': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_3, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_4': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_4, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_5': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_5, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_6': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_6, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_7': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_7, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_8': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_8, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_9': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_9, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_10': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_10, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_11': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_11, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_12': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_12, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_13': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_13, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_14': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_14, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_15': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_15, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_16': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_16, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_17': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_17, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_18': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_18, 
        'xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_19': xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_19
    }
    
    def build_system_prompt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    build_system_prompt.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_orig)
    xǁCodexOpenAIClientǁbuild_system_prompt__mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁbuild_system_prompt'

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_orig(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_1(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = None
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_2(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(None)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_3(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_4(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 1.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_5(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = None
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_6(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get(None, 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_7(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", None)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_8(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get(0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_9(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", )
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_10(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("XXprompt_tokensXX", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_11(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("PROMPT_TOKENS", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_12(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 1)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_13(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = None

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_14(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get(None, 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_15(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", None)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_16(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get(0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_17(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", )

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_18(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("XXcompletion_tokensXX", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_19(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("COMPLETION_TOKENS", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_20(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 1)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_21(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = None
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_22(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) / config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_23(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens * 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_24(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1001) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_25(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = None

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_26(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) / config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_27(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens * 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_28(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1001) * config.output_cost_per_1k

        return round(input_cost + output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_29(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(None, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_30(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, None)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_31(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_32(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, )

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_33(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost - output_cost, 6)

    def xǁCodexOpenAIClientǁestimate_cost__mutmut_34(self, model: str, usage: dict[str, int]) -> float:
        """Estimate the cost of an API call."""
        config = self.models.get(model)
        if not config:
            return 0.0

        # Safeguard: Validate usage dict
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        input_cost = (prompt_tokens / 1000) * config.input_cost_per_1k
        output_cost = (completion_tokens / 1000) * config.output_cost_per_1k

        return round(input_cost + output_cost, 7)
    
    xǁCodexOpenAIClientǁestimate_cost__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁestimate_cost__mutmut_1': xǁCodexOpenAIClientǁestimate_cost__mutmut_1, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_2': xǁCodexOpenAIClientǁestimate_cost__mutmut_2, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_3': xǁCodexOpenAIClientǁestimate_cost__mutmut_3, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_4': xǁCodexOpenAIClientǁestimate_cost__mutmut_4, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_5': xǁCodexOpenAIClientǁestimate_cost__mutmut_5, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_6': xǁCodexOpenAIClientǁestimate_cost__mutmut_6, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_7': xǁCodexOpenAIClientǁestimate_cost__mutmut_7, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_8': xǁCodexOpenAIClientǁestimate_cost__mutmut_8, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_9': xǁCodexOpenAIClientǁestimate_cost__mutmut_9, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_10': xǁCodexOpenAIClientǁestimate_cost__mutmut_10, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_11': xǁCodexOpenAIClientǁestimate_cost__mutmut_11, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_12': xǁCodexOpenAIClientǁestimate_cost__mutmut_12, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_13': xǁCodexOpenAIClientǁestimate_cost__mutmut_13, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_14': xǁCodexOpenAIClientǁestimate_cost__mutmut_14, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_15': xǁCodexOpenAIClientǁestimate_cost__mutmut_15, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_16': xǁCodexOpenAIClientǁestimate_cost__mutmut_16, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_17': xǁCodexOpenAIClientǁestimate_cost__mutmut_17, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_18': xǁCodexOpenAIClientǁestimate_cost__mutmut_18, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_19': xǁCodexOpenAIClientǁestimate_cost__mutmut_19, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_20': xǁCodexOpenAIClientǁestimate_cost__mutmut_20, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_21': xǁCodexOpenAIClientǁestimate_cost__mutmut_21, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_22': xǁCodexOpenAIClientǁestimate_cost__mutmut_22, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_23': xǁCodexOpenAIClientǁestimate_cost__mutmut_23, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_24': xǁCodexOpenAIClientǁestimate_cost__mutmut_24, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_25': xǁCodexOpenAIClientǁestimate_cost__mutmut_25, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_26': xǁCodexOpenAIClientǁestimate_cost__mutmut_26, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_27': xǁCodexOpenAIClientǁestimate_cost__mutmut_27, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_28': xǁCodexOpenAIClientǁestimate_cost__mutmut_28, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_29': xǁCodexOpenAIClientǁestimate_cost__mutmut_29, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_30': xǁCodexOpenAIClientǁestimate_cost__mutmut_30, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_31': xǁCodexOpenAIClientǁestimate_cost__mutmut_31, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_32': xǁCodexOpenAIClientǁestimate_cost__mutmut_32, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_33': xǁCodexOpenAIClientǁestimate_cost__mutmut_33, 
        'xǁCodexOpenAIClientǁestimate_cost__mutmut_34': xǁCodexOpenAIClientǁestimate_cost__mutmut_34
    }
    
    def estimate_cost(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁestimate_cost__mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁestimate_cost__mutmut_mutants"), args, kwargs, self)
        return result 
    
    estimate_cost.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁestimate_cost__mutmut_orig)
    xǁCodexOpenAIClientǁestimate_cost__mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁestimate_cost'

    def xǁCodexOpenAIClientǁlog_execution__mutmut_orig(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_1(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = None

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_2(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=None,
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_3(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=None,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_4(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=None,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_5(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=None,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_6(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=None,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_7(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=None,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_8(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=None,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_9(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_10(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_11(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_12(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_13(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_14(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_15(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_16(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(None).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_17(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(None)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_18(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) >= MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[-MAX_AUDIT_LOG_SIZE:]

    def xǁCodexOpenAIClientǁlog_execution__mutmut_19(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = None

    def xǁCodexOpenAIClientǁlog_execution__mutmut_20(
        self,
        *,
        task_id: str,
        model: str,
        tokens_used: int,
        duration_ms: int,
        estimated_cost: float,
        success: bool,
    ) -> None:
        """Log an execution for audit purposes."""
        from datetime import datetime, timezone

        entry = AuditLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            success=success,
        )

        self.audit_log.append(entry)

        # Keep only last MAX_AUDIT_LOG_SIZE entries in memory (safeguard: bounds check)
        if len(self.audit_log) > MAX_AUDIT_LOG_SIZE:
            self.audit_log = self.audit_log[+MAX_AUDIT_LOG_SIZE:]
    
    xǁCodexOpenAIClientǁlog_execution__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁlog_execution__mutmut_1': xǁCodexOpenAIClientǁlog_execution__mutmut_1, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_2': xǁCodexOpenAIClientǁlog_execution__mutmut_2, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_3': xǁCodexOpenAIClientǁlog_execution__mutmut_3, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_4': xǁCodexOpenAIClientǁlog_execution__mutmut_4, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_5': xǁCodexOpenAIClientǁlog_execution__mutmut_5, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_6': xǁCodexOpenAIClientǁlog_execution__mutmut_6, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_7': xǁCodexOpenAIClientǁlog_execution__mutmut_7, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_8': xǁCodexOpenAIClientǁlog_execution__mutmut_8, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_9': xǁCodexOpenAIClientǁlog_execution__mutmut_9, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_10': xǁCodexOpenAIClientǁlog_execution__mutmut_10, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_11': xǁCodexOpenAIClientǁlog_execution__mutmut_11, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_12': xǁCodexOpenAIClientǁlog_execution__mutmut_12, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_13': xǁCodexOpenAIClientǁlog_execution__mutmut_13, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_14': xǁCodexOpenAIClientǁlog_execution__mutmut_14, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_15': xǁCodexOpenAIClientǁlog_execution__mutmut_15, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_16': xǁCodexOpenAIClientǁlog_execution__mutmut_16, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_17': xǁCodexOpenAIClientǁlog_execution__mutmut_17, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_18': xǁCodexOpenAIClientǁlog_execution__mutmut_18, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_19': xǁCodexOpenAIClientǁlog_execution__mutmut_19, 
        'xǁCodexOpenAIClientǁlog_execution__mutmut_20': xǁCodexOpenAIClientǁlog_execution__mutmut_20
    }
    
    def log_execution(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁlog_execution__mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁlog_execution__mutmut_mutants"), args, kwargs, self)
        return result 
    
    log_execution.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁlog_execution__mutmut_orig)
    xǁCodexOpenAIClientǁlog_execution__mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁlog_execution'

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_orig(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_1(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_2(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"XXtotal_requestsXX": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_3(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"TOTAL_REQUESTS": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_4(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 1, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_5(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "XXtotal_tokensXX": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_6(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "TOTAL_TOKENS": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_7(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 1, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_8(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "XXtotal_costXX": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_9(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "TOTAL_COST": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_10(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 1.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_11(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "XXtotal_requestsXX": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_12(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "TOTAL_REQUESTS": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_13(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "XXsuccessful_requestsXX": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_14(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "SUCCESSFUL_REQUESTS": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_15(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(None),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_16(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(2 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_17(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "XXtotal_tokensXX": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_18(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "TOTAL_TOKENS": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_19(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(None),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_20(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "XXtotal_costXX": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_21(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "TOTAL_COST": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_22(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(None),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_23(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "XXmodels_usedXX": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_24(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "MODELS_USED": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_25(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(None),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_26(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(None)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_27(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "XXavg_duration_msXX": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_28(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "AVG_DURATION_MS": sum(e.duration_ms for e in self.audit_log)
            // len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_29(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log) / len(self.audit_log),
        }

    def xǁCodexOpenAIClientǁget_usage_summary__mutmut_30(self) -> dict[str, Any]:
        """Get a summary of API usage from the audit log."""
        if not self.audit_log:
            return {"total_requests": 0, "total_tokens": 0, "total_cost": 0.0}

        return {
            "total_requests": len(self.audit_log),
            "successful_requests": sum(1 for e in self.audit_log if e.success),
            "total_tokens": sum(e.tokens_used for e in self.audit_log),
            "total_cost": sum(e.estimated_cost for e in self.audit_log),
            "models_used": list(set(e.model for e in self.audit_log)),
            "avg_duration_ms": sum(None)
            // len(self.audit_log),
        }
    
    xǁCodexOpenAIClientǁget_usage_summary__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCodexOpenAIClientǁget_usage_summary__mutmut_1': xǁCodexOpenAIClientǁget_usage_summary__mutmut_1, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_2': xǁCodexOpenAIClientǁget_usage_summary__mutmut_2, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_3': xǁCodexOpenAIClientǁget_usage_summary__mutmut_3, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_4': xǁCodexOpenAIClientǁget_usage_summary__mutmut_4, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_5': xǁCodexOpenAIClientǁget_usage_summary__mutmut_5, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_6': xǁCodexOpenAIClientǁget_usage_summary__mutmut_6, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_7': xǁCodexOpenAIClientǁget_usage_summary__mutmut_7, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_8': xǁCodexOpenAIClientǁget_usage_summary__mutmut_8, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_9': xǁCodexOpenAIClientǁget_usage_summary__mutmut_9, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_10': xǁCodexOpenAIClientǁget_usage_summary__mutmut_10, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_11': xǁCodexOpenAIClientǁget_usage_summary__mutmut_11, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_12': xǁCodexOpenAIClientǁget_usage_summary__mutmut_12, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_13': xǁCodexOpenAIClientǁget_usage_summary__mutmut_13, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_14': xǁCodexOpenAIClientǁget_usage_summary__mutmut_14, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_15': xǁCodexOpenAIClientǁget_usage_summary__mutmut_15, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_16': xǁCodexOpenAIClientǁget_usage_summary__mutmut_16, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_17': xǁCodexOpenAIClientǁget_usage_summary__mutmut_17, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_18': xǁCodexOpenAIClientǁget_usage_summary__mutmut_18, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_19': xǁCodexOpenAIClientǁget_usage_summary__mutmut_19, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_20': xǁCodexOpenAIClientǁget_usage_summary__mutmut_20, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_21': xǁCodexOpenAIClientǁget_usage_summary__mutmut_21, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_22': xǁCodexOpenAIClientǁget_usage_summary__mutmut_22, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_23': xǁCodexOpenAIClientǁget_usage_summary__mutmut_23, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_24': xǁCodexOpenAIClientǁget_usage_summary__mutmut_24, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_25': xǁCodexOpenAIClientǁget_usage_summary__mutmut_25, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_26': xǁCodexOpenAIClientǁget_usage_summary__mutmut_26, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_27': xǁCodexOpenAIClientǁget_usage_summary__mutmut_27, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_28': xǁCodexOpenAIClientǁget_usage_summary__mutmut_28, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_29': xǁCodexOpenAIClientǁget_usage_summary__mutmut_29, 
        'xǁCodexOpenAIClientǁget_usage_summary__mutmut_30': xǁCodexOpenAIClientǁget_usage_summary__mutmut_30
    }
    
    def get_usage_summary(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCodexOpenAIClientǁget_usage_summary__mutmut_orig"), object.__getattribute__(self, "xǁCodexOpenAIClientǁget_usage_summary__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_usage_summary.__signature__ = _mutmut_signature(xǁCodexOpenAIClientǁget_usage_summary__mutmut_orig)
    xǁCodexOpenAIClientǁget_usage_summary__mutmut_orig.__name__ = 'xǁCodexOpenAIClientǁget_usage_summary'


__all__ = [
    "AVAILABLE_MODELS",
    "AuditLogEntry",
    "CodexOpenAIClient",
    "CostTier",
    "ExecutionResult",
    "ModelConfig",
]
