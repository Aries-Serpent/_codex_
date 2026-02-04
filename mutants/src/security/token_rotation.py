"""Token Rotation Automation Module.

PS-05 Enhancement: Implements automated token rotation with:
- Auto-rotation on security events
- Rotation scheduling
- Comprehensive audit trail

This module extends the Token Security Neutralization planset with
enterprise-grade token lifecycle management.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

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


class RotationTrigger(Enum):
    """Events that can trigger token rotation."""
    
    SCHEDULED = "scheduled"  # Regular rotation schedule
    EXPIRY = "expiry"  # Token approaching expiration
    SECURITY_EVENT = "security_event"  # Security incident detected
    EXPOSURE = "exposure"  # Token potentially exposed
    MANUAL = "manual"  # Manual rotation request
    POLICY_CHANGE = "policy_change"  # Security policy updated


class TokenState(Enum):
    """Token lifecycle states."""
    
    ACTIVE = "active"
    ROTATING = "rotating"  # In grace period during rotation
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class TokenMetadata:
    """Metadata for a managed token."""
    
    token_id: str
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime] = None
    state: TokenState = TokenState.ACTIVE
    rotation_count: int = 0
    scopes: list[str] = field(default_factory=list)
    provider: str = "github"  # github, gitlab, bitbucket, etc.
    
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now(UTC) > self.expires_at
    
    def days_until_expiry(self) -> int:
        """Days remaining until expiration."""
        delta = self.expires_at - datetime.now(UTC)
        return max(0, delta.days)
    
    def should_rotate(self, policy: RotationPolicy) -> tuple[bool, RotationTrigger | None]:
        """Determine if token should be rotated based on policy."""
        if self.is_expired():
            return True, RotationTrigger.EXPIRY
        
        if self.days_until_expiry() <= policy.rotate_before_expiry_days:
            return True, RotationTrigger.EXPIRY
        
        if self.rotation_count == 0:
            # First rotation after max age
            days_since_creation = (datetime.now(UTC) - self.created_at).days
            if days_since_creation >= policy.max_age_days:
                return True, RotationTrigger.SCHEDULED
        
        return False, None


@dataclass
class RotationPolicy:
    """Policy configuration for token rotation."""
    
    max_age_days: int = 90  # Maximum token age before rotation
    rotate_before_expiry_days: int = 14  # Rotate this many days before expiry
    grace_period_hours: int = 24  # Both tokens valid during rotation
    auto_rotate_on_exposure: bool = True  # Rotate if token detected in logs
    auto_rotate_on_security_event: bool = True  # Rotate on security incidents
    min_rotation_interval_hours: int = 1  # Prevent rotation storms
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize policy to dict."""
        return {
            "max_age_days": self.max_age_days,
            "rotate_before_expiry_days": self.rotate_before_expiry_days,
            "grace_period_hours": self.grace_period_hours,
            "auto_rotate_on_exposure": self.auto_rotate_on_exposure,
            "auto_rotate_on_security_event": self.auto_rotate_on_security_event,
            "min_rotation_interval_hours": self.min_rotation_interval_hours,
        }


@dataclass
class RotationEvent:
    """Record of a rotation event for audit trail."""
    
    event_id: str
    token_id: str
    timestamp: datetime
    trigger: RotationTrigger
    old_token_hash: str  # SHA-256 of old token (not the token itself)
    new_token_hash: str  # SHA-256 of new token
    success: bool
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_jsonl(self) -> str:
        """Serialize to JSONL format for audit log."""
        return json.dumps({
            "event_id": self.event_id,
            "token_id": self.token_id,
            "timestamp": self.timestamp.isoformat(),
            "trigger": self.trigger.value,
            "old_token_hash": self.old_token_hash,
            "new_token_hash": self.new_token_hash,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        })


class TokenRotationManager:
    """Manages automated token rotation lifecycle.
    
    Features:
    - Scheduled rotation based on policy
    - Security event-triggered rotation
    - Grace period for seamless transitions
    - Comprehensive audit logging
    """
    
    def xǁTokenRotationManagerǁ__init____mutmut_orig(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_1(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = None
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_2(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy and RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_3(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = None
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_4(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path and Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_5(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(None)
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_6(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path("XX.codex/evidence/token_rotation.jsonlXX")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_7(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".CODEX/EVIDENCE/TOKEN_ROTATION.JSONL")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_8(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = None
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_9(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator and self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_10(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = None
        self._rotation_locks: dict[str, datetime] = {}
    
    def xǁTokenRotationManagerǁ__init____mutmut_11(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.
        
        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = None
    
    xǁTokenRotationManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁ__init____mutmut_1': xǁTokenRotationManagerǁ__init____mutmut_1, 
        'xǁTokenRotationManagerǁ__init____mutmut_2': xǁTokenRotationManagerǁ__init____mutmut_2, 
        'xǁTokenRotationManagerǁ__init____mutmut_3': xǁTokenRotationManagerǁ__init____mutmut_3, 
        'xǁTokenRotationManagerǁ__init____mutmut_4': xǁTokenRotationManagerǁ__init____mutmut_4, 
        'xǁTokenRotationManagerǁ__init____mutmut_5': xǁTokenRotationManagerǁ__init____mutmut_5, 
        'xǁTokenRotationManagerǁ__init____mutmut_6': xǁTokenRotationManagerǁ__init____mutmut_6, 
        'xǁTokenRotationManagerǁ__init____mutmut_7': xǁTokenRotationManagerǁ__init____mutmut_7, 
        'xǁTokenRotationManagerǁ__init____mutmut_8': xǁTokenRotationManagerǁ__init____mutmut_8, 
        'xǁTokenRotationManagerǁ__init____mutmut_9': xǁTokenRotationManagerǁ__init____mutmut_9, 
        'xǁTokenRotationManagerǁ__init____mutmut_10': xǁTokenRotationManagerǁ__init____mutmut_10, 
        'xǁTokenRotationManagerǁ__init____mutmut_11': xǁTokenRotationManagerǁ__init____mutmut_11
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁ__init____mutmut_orig)
    xǁTokenRotationManagerǁ__init____mutmut_orig.__name__ = 'xǁTokenRotationManagerǁ__init__'
    
    @staticmethod
    def _default_token_generator() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Create SHA-256 hash of token for audit (never store raw tokens)."""
        return hashlib.sha256(token.encode()).hexdigest()[:16]
    
    def xǁTokenRotationManagerǁregister_token__mutmut_orig(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_1(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "XXgithubXX",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_2(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "GITHUB",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_3(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = None
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_4(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=None,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_5(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=None,
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_6(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=None,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_7(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=None,
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_8(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=None,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_9(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_10(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_11(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_12(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_13(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_14(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(None),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_15(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes and [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_16(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = None
        
        logger.info(
            f"Registered token {token_id} with expiry {expires_at.isoformat()}"
        )
        return metadata
    
    def xǁTokenRotationManagerǁregister_token__mutmut_17(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.
        
        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)
            
        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata
        
        logger.info(
            None
        )
        return metadata
    
    xǁTokenRotationManagerǁregister_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁregister_token__mutmut_1': xǁTokenRotationManagerǁregister_token__mutmut_1, 
        'xǁTokenRotationManagerǁregister_token__mutmut_2': xǁTokenRotationManagerǁregister_token__mutmut_2, 
        'xǁTokenRotationManagerǁregister_token__mutmut_3': xǁTokenRotationManagerǁregister_token__mutmut_3, 
        'xǁTokenRotationManagerǁregister_token__mutmut_4': xǁTokenRotationManagerǁregister_token__mutmut_4, 
        'xǁTokenRotationManagerǁregister_token__mutmut_5': xǁTokenRotationManagerǁregister_token__mutmut_5, 
        'xǁTokenRotationManagerǁregister_token__mutmut_6': xǁTokenRotationManagerǁregister_token__mutmut_6, 
        'xǁTokenRotationManagerǁregister_token__mutmut_7': xǁTokenRotationManagerǁregister_token__mutmut_7, 
        'xǁTokenRotationManagerǁregister_token__mutmut_8': xǁTokenRotationManagerǁregister_token__mutmut_8, 
        'xǁTokenRotationManagerǁregister_token__mutmut_9': xǁTokenRotationManagerǁregister_token__mutmut_9, 
        'xǁTokenRotationManagerǁregister_token__mutmut_10': xǁTokenRotationManagerǁregister_token__mutmut_10, 
        'xǁTokenRotationManagerǁregister_token__mutmut_11': xǁTokenRotationManagerǁregister_token__mutmut_11, 
        'xǁTokenRotationManagerǁregister_token__mutmut_12': xǁTokenRotationManagerǁregister_token__mutmut_12, 
        'xǁTokenRotationManagerǁregister_token__mutmut_13': xǁTokenRotationManagerǁregister_token__mutmut_13, 
        'xǁTokenRotationManagerǁregister_token__mutmut_14': xǁTokenRotationManagerǁregister_token__mutmut_14, 
        'xǁTokenRotationManagerǁregister_token__mutmut_15': xǁTokenRotationManagerǁregister_token__mutmut_15, 
        'xǁTokenRotationManagerǁregister_token__mutmut_16': xǁTokenRotationManagerǁregister_token__mutmut_16, 
        'xǁTokenRotationManagerǁregister_token__mutmut_17': xǁTokenRotationManagerǁregister_token__mutmut_17
    }
    
    def register_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁregister_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁregister_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_token.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁregister_token__mutmut_orig)
    xǁTokenRotationManagerǁregister_token__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁregister_token'
    
    def xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_orig(self, token_id: str) -> tuple[bool, RotationTrigger | None]:
        """Check if a token needs rotation.
        
        Args:
            token_id: Token to check
            
        Returns:
            Tuple of (needs_rotation, trigger_reason)
        """
        if token_id not in self.tokens:
            return False, None
        
        return self.tokens[token_id].should_rotate(self.policy)
    
    def xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_1(self, token_id: str) -> tuple[bool, RotationTrigger | None]:
        """Check if a token needs rotation.
        
        Args:
            token_id: Token to check
            
        Returns:
            Tuple of (needs_rotation, trigger_reason)
        """
        if token_id in self.tokens:
            return False, None
        
        return self.tokens[token_id].should_rotate(self.policy)
    
    def xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_2(self, token_id: str) -> tuple[bool, RotationTrigger | None]:
        """Check if a token needs rotation.
        
        Args:
            token_id: Token to check
            
        Returns:
            Tuple of (needs_rotation, trigger_reason)
        """
        if token_id not in self.tokens:
            return True, None
        
        return self.tokens[token_id].should_rotate(self.policy)
    
    def xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_3(self, token_id: str) -> tuple[bool, RotationTrigger | None]:
        """Check if a token needs rotation.
        
        Args:
            token_id: Token to check
            
        Returns:
            Tuple of (needs_rotation, trigger_reason)
        """
        if token_id not in self.tokens:
            return False, None
        
        return self.tokens[token_id].should_rotate(None)
    
    xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_1': xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_1, 
        'xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_2': xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_2, 
        'xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_3': xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_3
    }
    
    def check_rotation_needed(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_mutants"), args, kwargs, self)
        return result 
    
    check_rotation_needed.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_orig)
    xǁTokenRotationManagerǁcheck_rotation_needed__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁcheck_rotation_needed'
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_orig(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_1(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id not in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_2(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = None
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_3(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = None
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_4(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=None)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_5(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) + lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_6(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(None) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_7(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time <= min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_8(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=None,
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_9(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=None,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_10(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=None,
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_11(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=None,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_12(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=None,
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_13(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash=None,
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_14(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=None,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_15(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message=None,
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_16(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=None,
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_17(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_18(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_19(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_20(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_21(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_22(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_23(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_24(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_25(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_26(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(None),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_27(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(9),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_28(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(None),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_29(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(None),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_30(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="XXXX",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_31(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=True,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_32(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="XXRotation throttled - minimum interval not metXX",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_33(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_34(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="ROTATION THROTTLED - MINIMUM INTERVAL NOT MET",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_35(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata and {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_36(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = None
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_37(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token and self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_38(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = None
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_39(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=None,
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_40(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=None,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_41(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=None,
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_42(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=None,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_43(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=None,
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_44(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=None,
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_45(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=None,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_46(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=None,
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_47(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_48(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_49(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_50(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_51(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_52(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_53(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_54(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_55(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(None),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_56(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(9),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_57(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(None),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_58(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(None),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_59(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(None),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_60(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=False,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_61(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata and {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_62(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id not in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_63(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count = 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_64(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count -= 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_65(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 2
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_66(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = None
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_67(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = None
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_68(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(None)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_69(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(None)
        
        logger.info(
            f"Rotated token {token_id}: trigger={trigger.value}, "
            f"event_id={event.event_id}"
        )
        
        return event
    
    def xǁTokenRotationManagerǁrotate_token__mutmut_70(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.
        
        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit
            
        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )
        
        # Generate new token if not provided
        new_token = new_token or self.token_generator()
        
        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )
        
        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING
        
        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)
        
        # Log audit event
        self._write_audit_log(event)
        
        logger.info(
            None
        )
        
        return event
    
    xǁTokenRotationManagerǁrotate_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁrotate_token__mutmut_1': xǁTokenRotationManagerǁrotate_token__mutmut_1, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_2': xǁTokenRotationManagerǁrotate_token__mutmut_2, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_3': xǁTokenRotationManagerǁrotate_token__mutmut_3, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_4': xǁTokenRotationManagerǁrotate_token__mutmut_4, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_5': xǁTokenRotationManagerǁrotate_token__mutmut_5, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_6': xǁTokenRotationManagerǁrotate_token__mutmut_6, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_7': xǁTokenRotationManagerǁrotate_token__mutmut_7, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_8': xǁTokenRotationManagerǁrotate_token__mutmut_8, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_9': xǁTokenRotationManagerǁrotate_token__mutmut_9, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_10': xǁTokenRotationManagerǁrotate_token__mutmut_10, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_11': xǁTokenRotationManagerǁrotate_token__mutmut_11, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_12': xǁTokenRotationManagerǁrotate_token__mutmut_12, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_13': xǁTokenRotationManagerǁrotate_token__mutmut_13, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_14': xǁTokenRotationManagerǁrotate_token__mutmut_14, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_15': xǁTokenRotationManagerǁrotate_token__mutmut_15, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_16': xǁTokenRotationManagerǁrotate_token__mutmut_16, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_17': xǁTokenRotationManagerǁrotate_token__mutmut_17, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_18': xǁTokenRotationManagerǁrotate_token__mutmut_18, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_19': xǁTokenRotationManagerǁrotate_token__mutmut_19, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_20': xǁTokenRotationManagerǁrotate_token__mutmut_20, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_21': xǁTokenRotationManagerǁrotate_token__mutmut_21, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_22': xǁTokenRotationManagerǁrotate_token__mutmut_22, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_23': xǁTokenRotationManagerǁrotate_token__mutmut_23, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_24': xǁTokenRotationManagerǁrotate_token__mutmut_24, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_25': xǁTokenRotationManagerǁrotate_token__mutmut_25, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_26': xǁTokenRotationManagerǁrotate_token__mutmut_26, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_27': xǁTokenRotationManagerǁrotate_token__mutmut_27, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_28': xǁTokenRotationManagerǁrotate_token__mutmut_28, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_29': xǁTokenRotationManagerǁrotate_token__mutmut_29, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_30': xǁTokenRotationManagerǁrotate_token__mutmut_30, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_31': xǁTokenRotationManagerǁrotate_token__mutmut_31, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_32': xǁTokenRotationManagerǁrotate_token__mutmut_32, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_33': xǁTokenRotationManagerǁrotate_token__mutmut_33, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_34': xǁTokenRotationManagerǁrotate_token__mutmut_34, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_35': xǁTokenRotationManagerǁrotate_token__mutmut_35, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_36': xǁTokenRotationManagerǁrotate_token__mutmut_36, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_37': xǁTokenRotationManagerǁrotate_token__mutmut_37, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_38': xǁTokenRotationManagerǁrotate_token__mutmut_38, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_39': xǁTokenRotationManagerǁrotate_token__mutmut_39, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_40': xǁTokenRotationManagerǁrotate_token__mutmut_40, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_41': xǁTokenRotationManagerǁrotate_token__mutmut_41, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_42': xǁTokenRotationManagerǁrotate_token__mutmut_42, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_43': xǁTokenRotationManagerǁrotate_token__mutmut_43, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_44': xǁTokenRotationManagerǁrotate_token__mutmut_44, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_45': xǁTokenRotationManagerǁrotate_token__mutmut_45, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_46': xǁTokenRotationManagerǁrotate_token__mutmut_46, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_47': xǁTokenRotationManagerǁrotate_token__mutmut_47, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_48': xǁTokenRotationManagerǁrotate_token__mutmut_48, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_49': xǁTokenRotationManagerǁrotate_token__mutmut_49, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_50': xǁTokenRotationManagerǁrotate_token__mutmut_50, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_51': xǁTokenRotationManagerǁrotate_token__mutmut_51, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_52': xǁTokenRotationManagerǁrotate_token__mutmut_52, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_53': xǁTokenRotationManagerǁrotate_token__mutmut_53, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_54': xǁTokenRotationManagerǁrotate_token__mutmut_54, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_55': xǁTokenRotationManagerǁrotate_token__mutmut_55, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_56': xǁTokenRotationManagerǁrotate_token__mutmut_56, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_57': xǁTokenRotationManagerǁrotate_token__mutmut_57, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_58': xǁTokenRotationManagerǁrotate_token__mutmut_58, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_59': xǁTokenRotationManagerǁrotate_token__mutmut_59, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_60': xǁTokenRotationManagerǁrotate_token__mutmut_60, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_61': xǁTokenRotationManagerǁrotate_token__mutmut_61, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_62': xǁTokenRotationManagerǁrotate_token__mutmut_62, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_63': xǁTokenRotationManagerǁrotate_token__mutmut_63, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_64': xǁTokenRotationManagerǁrotate_token__mutmut_64, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_65': xǁTokenRotationManagerǁrotate_token__mutmut_65, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_66': xǁTokenRotationManagerǁrotate_token__mutmut_66, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_67': xǁTokenRotationManagerǁrotate_token__mutmut_67, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_68': xǁTokenRotationManagerǁrotate_token__mutmut_68, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_69': xǁTokenRotationManagerǁrotate_token__mutmut_69, 
        'xǁTokenRotationManagerǁrotate_token__mutmut_70': xǁTokenRotationManagerǁrotate_token__mutmut_70
    }
    
    def rotate_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁrotate_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁrotate_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    rotate_token.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁrotate_token__mutmut_orig)
    xǁTokenRotationManagerǁrotate_token__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁrotate_token'
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_orig(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_1(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = None
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_2(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" or not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_3(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type != "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_4(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "XXexposureXX" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_5(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "EXPOSURE" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_6(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_7(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning(None)
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_8(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("XXToken exposure detected but auto-rotation disabledXX")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_9(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_10(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("TOKEN EXPOSURE DETECTED BUT AUTO-ROTATION DISABLED")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_11(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") or not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_12(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type not in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_13(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("XXbreachXX", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_14(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("BREACH", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_15(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "XXcompromiseXX") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_16(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "COMPROMISE") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_17(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_18(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning(None)
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_19(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("XXSecurity event detected but auto-rotation disabledXX")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_20(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_21(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("SECURITY EVENT DETECTED BUT AUTO-ROTATION DISABLED")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_22(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = None
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_23(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids and list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_24(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(None)
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_25(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id not in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_26(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = None
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_27(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=None,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_28(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=None,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_29(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token=None,  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_30(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata=None,
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_31(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_32(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_33(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_34(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_35(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="XX<redacted>XX",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_36(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<REDACTED>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_37(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "XXsecurity_event_typeXX": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_38(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "SECURITY_EVENT_TYPE": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_39(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata and {}),
                    },
                )
                events.append(event)
        
        return events
    
    def xǁTokenRotationManagerǁhandle_security_event__mutmut_40(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.
        
        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context
            
        Returns:
            List of rotation events performed
        """
        events = []
        
        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events
        
        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events
        
        token_ids = affected_token_ids or list(self.tokens.keys())
        
        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(None)
        
        return events
    
    xǁTokenRotationManagerǁhandle_security_event__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁhandle_security_event__mutmut_1': xǁTokenRotationManagerǁhandle_security_event__mutmut_1, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_2': xǁTokenRotationManagerǁhandle_security_event__mutmut_2, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_3': xǁTokenRotationManagerǁhandle_security_event__mutmut_3, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_4': xǁTokenRotationManagerǁhandle_security_event__mutmut_4, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_5': xǁTokenRotationManagerǁhandle_security_event__mutmut_5, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_6': xǁTokenRotationManagerǁhandle_security_event__mutmut_6, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_7': xǁTokenRotationManagerǁhandle_security_event__mutmut_7, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_8': xǁTokenRotationManagerǁhandle_security_event__mutmut_8, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_9': xǁTokenRotationManagerǁhandle_security_event__mutmut_9, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_10': xǁTokenRotationManagerǁhandle_security_event__mutmut_10, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_11': xǁTokenRotationManagerǁhandle_security_event__mutmut_11, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_12': xǁTokenRotationManagerǁhandle_security_event__mutmut_12, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_13': xǁTokenRotationManagerǁhandle_security_event__mutmut_13, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_14': xǁTokenRotationManagerǁhandle_security_event__mutmut_14, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_15': xǁTokenRotationManagerǁhandle_security_event__mutmut_15, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_16': xǁTokenRotationManagerǁhandle_security_event__mutmut_16, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_17': xǁTokenRotationManagerǁhandle_security_event__mutmut_17, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_18': xǁTokenRotationManagerǁhandle_security_event__mutmut_18, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_19': xǁTokenRotationManagerǁhandle_security_event__mutmut_19, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_20': xǁTokenRotationManagerǁhandle_security_event__mutmut_20, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_21': xǁTokenRotationManagerǁhandle_security_event__mutmut_21, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_22': xǁTokenRotationManagerǁhandle_security_event__mutmut_22, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_23': xǁTokenRotationManagerǁhandle_security_event__mutmut_23, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_24': xǁTokenRotationManagerǁhandle_security_event__mutmut_24, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_25': xǁTokenRotationManagerǁhandle_security_event__mutmut_25, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_26': xǁTokenRotationManagerǁhandle_security_event__mutmut_26, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_27': xǁTokenRotationManagerǁhandle_security_event__mutmut_27, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_28': xǁTokenRotationManagerǁhandle_security_event__mutmut_28, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_29': xǁTokenRotationManagerǁhandle_security_event__mutmut_29, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_30': xǁTokenRotationManagerǁhandle_security_event__mutmut_30, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_31': xǁTokenRotationManagerǁhandle_security_event__mutmut_31, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_32': xǁTokenRotationManagerǁhandle_security_event__mutmut_32, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_33': xǁTokenRotationManagerǁhandle_security_event__mutmut_33, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_34': xǁTokenRotationManagerǁhandle_security_event__mutmut_34, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_35': xǁTokenRotationManagerǁhandle_security_event__mutmut_35, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_36': xǁTokenRotationManagerǁhandle_security_event__mutmut_36, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_37': xǁTokenRotationManagerǁhandle_security_event__mutmut_37, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_38': xǁTokenRotationManagerǁhandle_security_event__mutmut_38, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_39': xǁTokenRotationManagerǁhandle_security_event__mutmut_39, 
        'xǁTokenRotationManagerǁhandle_security_event__mutmut_40': xǁTokenRotationManagerǁhandle_security_event__mutmut_40
    }
    
    def handle_security_event(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁhandle_security_event__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁhandle_security_event__mutmut_mutants"), args, kwargs, self)
        return result 
    
    handle_security_event.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁhandle_security_event__mutmut_orig)
    xǁTokenRotationManagerǁhandle_security_event__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁhandle_security_event'
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_orig(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_1(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = None
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_2(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = None
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_3(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(None)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_4(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append(None)
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_5(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "XXtoken_idXX": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_6(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "TOKEN_ID": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_7(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "XXdays_until_expiryXX": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_8(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "DAYS_UNTIL_EXPIRY": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_9(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "XXrotation_neededXX": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_10(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "ROTATION_NEEDED": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_11(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "XXtriggerXX": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_12(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "TRIGGER": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_13(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "XXstateXX": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_14(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "STATE": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_15(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "XXrotation_countXX": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_16(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "ROTATION_COUNT": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_17(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(None, key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_18(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=None)
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_19(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(key=lambda x: x["days_until_expiry"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_20(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, )
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_21(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: None)
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_22(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["XXdays_until_expiryXX"])
    
    def xǁTokenRotationManagerǁget_rotation_schedule__mutmut_23(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.
        
        Returns:
            List of upcoming rotation schedules
        """
        schedule = []
        
        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)
            
            schedule.append({
                "token_id": token_id,
                "days_until_expiry": meta.days_until_expiry(),
                "rotation_needed": needs_rotation,
                "trigger": trigger.value if trigger else None,
                "state": meta.state.value,
                "rotation_count": meta.rotation_count,
            })
        
        return sorted(schedule, key=lambda x: x["DAYS_UNTIL_EXPIRY"])
    
    xǁTokenRotationManagerǁget_rotation_schedule__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_1': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_1, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_2': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_2, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_3': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_3, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_4': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_4, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_5': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_5, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_6': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_6, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_7': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_7, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_8': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_8, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_9': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_9, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_10': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_10, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_11': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_11, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_12': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_12, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_13': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_13, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_14': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_14, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_15': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_15, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_16': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_16, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_17': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_17, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_18': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_18, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_19': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_19, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_20': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_20, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_21': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_21, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_22': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_22, 
        'xǁTokenRotationManagerǁget_rotation_schedule__mutmut_23': xǁTokenRotationManagerǁget_rotation_schedule__mutmut_23
    }
    
    def get_rotation_schedule(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁget_rotation_schedule__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁget_rotation_schedule__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_rotation_schedule.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁget_rotation_schedule__mutmut_orig)
    xǁTokenRotationManagerǁget_rotation_schedule__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁget_rotation_schedule'
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_orig(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_1(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=None, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_2(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=None)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_3(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_4(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, )
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_5(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=False, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_6(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=False)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_7(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open(None) as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_8(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("XXaXX") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_9(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("A") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_10(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(None)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_11(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() - "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_12(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "XX\nXX")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def xǁTokenRotationManagerǁ_write_audit_log__mutmut_13(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except Exception as e:
            logger.error(None)
    
    xǁTokenRotationManagerǁ_write_audit_log__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenRotationManagerǁ_write_audit_log__mutmut_1': xǁTokenRotationManagerǁ_write_audit_log__mutmut_1, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_2': xǁTokenRotationManagerǁ_write_audit_log__mutmut_2, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_3': xǁTokenRotationManagerǁ_write_audit_log__mutmut_3, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_4': xǁTokenRotationManagerǁ_write_audit_log__mutmut_4, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_5': xǁTokenRotationManagerǁ_write_audit_log__mutmut_5, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_6': xǁTokenRotationManagerǁ_write_audit_log__mutmut_6, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_7': xǁTokenRotationManagerǁ_write_audit_log__mutmut_7, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_8': xǁTokenRotationManagerǁ_write_audit_log__mutmut_8, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_9': xǁTokenRotationManagerǁ_write_audit_log__mutmut_9, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_10': xǁTokenRotationManagerǁ_write_audit_log__mutmut_10, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_11': xǁTokenRotationManagerǁ_write_audit_log__mutmut_11, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_12': xǁTokenRotationManagerǁ_write_audit_log__mutmut_12, 
        'xǁTokenRotationManagerǁ_write_audit_log__mutmut_13': xǁTokenRotationManagerǁ_write_audit_log__mutmut_13
    }
    
    def _write_audit_log(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenRotationManagerǁ_write_audit_log__mutmut_orig"), object.__getattribute__(self, "xǁTokenRotationManagerǁ_write_audit_log__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _write_audit_log.__signature__ = _mutmut_signature(xǁTokenRotationManagerǁ_write_audit_log__mutmut_orig)
    xǁTokenRotationManagerǁ_write_audit_log__mutmut_orig.__name__ = 'xǁTokenRotationManagerǁ_write_audit_log'


def x_check_token_rotation_needed__mutmut_orig(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_1(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 91,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_2(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 15,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_3(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = None
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_4(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(None)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_5(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now >= expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_6(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return False, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_7(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "XXToken expiredXX"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_8(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_9(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "TOKEN EXPIRED"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_10(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = None
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_11(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at + now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_12(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry < rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_13(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return False, f"Token expires in {days_until_expiry} days"
    
    return False, None


def x_check_token_rotation_needed__mutmut_14(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.
    
    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate
        
    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)
    
    if now > expires_at:
        return True, "Token expired"
    
    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"
    
    return True, None

x_check_token_rotation_needed__mutmut_mutants : ClassVar[MutantDict] = {
'x_check_token_rotation_needed__mutmut_1': x_check_token_rotation_needed__mutmut_1, 
    'x_check_token_rotation_needed__mutmut_2': x_check_token_rotation_needed__mutmut_2, 
    'x_check_token_rotation_needed__mutmut_3': x_check_token_rotation_needed__mutmut_3, 
    'x_check_token_rotation_needed__mutmut_4': x_check_token_rotation_needed__mutmut_4, 
    'x_check_token_rotation_needed__mutmut_5': x_check_token_rotation_needed__mutmut_5, 
    'x_check_token_rotation_needed__mutmut_6': x_check_token_rotation_needed__mutmut_6, 
    'x_check_token_rotation_needed__mutmut_7': x_check_token_rotation_needed__mutmut_7, 
    'x_check_token_rotation_needed__mutmut_8': x_check_token_rotation_needed__mutmut_8, 
    'x_check_token_rotation_needed__mutmut_9': x_check_token_rotation_needed__mutmut_9, 
    'x_check_token_rotation_needed__mutmut_10': x_check_token_rotation_needed__mutmut_10, 
    'x_check_token_rotation_needed__mutmut_11': x_check_token_rotation_needed__mutmut_11, 
    'x_check_token_rotation_needed__mutmut_12': x_check_token_rotation_needed__mutmut_12, 
    'x_check_token_rotation_needed__mutmut_13': x_check_token_rotation_needed__mutmut_13, 
    'x_check_token_rotation_needed__mutmut_14': x_check_token_rotation_needed__mutmut_14
}

def check_token_rotation_needed(*args, **kwargs):
    result = _mutmut_trampoline(x_check_token_rotation_needed__mutmut_orig, x_check_token_rotation_needed__mutmut_mutants, args, kwargs)
    return result 

check_token_rotation_needed.__signature__ = _mutmut_signature(x_check_token_rotation_needed__mutmut_orig)
x_check_token_rotation_needed__mutmut_orig.__name__ = 'x_check_token_rotation_needed'


__all__ = [
    "TokenRotationManager",
    "RotationPolicy",
    "RotationEvent",
    "RotationTrigger",
    "TokenMetadata",
    "TokenState",
    "check_token_rotation_needed",
]
