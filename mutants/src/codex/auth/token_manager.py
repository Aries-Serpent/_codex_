"""
Token Manager for Codex platform.

Handles JWT token generation, validation, rotation, and session management
with focus on security and GitHub integration.

Minimum Python version: 3.9+ (uses built-in generic types)
"""

import json
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Optional, Any, List, Set, Tuple
from enum import Enum

from ..security_utils import sanitize_log_message
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


class TokenType(Enum):
    """Token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    SESSION = "session"


@dataclass
class TokenClaims:
    """JWT token claims."""
    sub: str  # Subject (user ID)
    iat: float  # Issued at
    exp: float  # Expiration
    type: TokenType  # Token type
    scope: Optional[str] = None  # Permissions/scopes
    jti: Optional[str] = None  # Token ID
    iss: str = "codex"  # Issuer
    aud: str = "codex-api"  # Audience
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert claims to dictionary."""
        return {
            'sub': self.sub,
            'iat': self.iat,
            'exp': self.exp,
            'type': self.type.value,
            'scope': self.scope,
            'jti': self.jti,
            'iss': self.iss,
            'aud': self.aud,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenClaims':
        """Create claims from dictionary."""
        return cls(
            sub=data['sub'],
            iat=data['iat'],
            exp=data['exp'],
            type=TokenType(data['type']),
            scope=data.get('scope'),
            jti=data.get('jti'),
            iss=data.get('iss', 'codex'),
            aud=data.get('aud', 'codex-api'),
        )


@dataclass
class SessionInfo:
    """User session information."""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    mfa_verified: bool = False
    
    def is_active(self, timeout: int = 1800) -> bool:
        """Check if session is still active (default 30 minutes)."""
        return (time.time() - self.last_activity) < timeout
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()


class TokenManager:
    """
    Token manager for authentication and session management.
    
    Provides JWT-like token generation and validation without external
    dependencies. In production, consider using PyJWT library.
    """
    
    # Token expiration times (in seconds)
    ACCESS_TOKEN_EXPIRY = 900  # 15 minutes
    REFRESH_TOKEN_EXPIRY = 604800  # 7 days
    SESSION_TOKEN_EXPIRY = 2592000  # 30 days
    
    def xǁTokenManagerǁ__init____mutmut_orig(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_1(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is not None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_2(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                None,
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_3(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                None
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_4(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_5(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_6(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "XXAuto-generating secret key. This is ONLY for development. XX"
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_7(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "auto-generating secret key. this is only for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_8(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "AUTO-GENERATING SECRET KEY. THIS IS ONLY FOR DEVELOPMENT. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_9(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "XXIn production, ALWAYS provide an explicit secret_key.XX",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_10(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "in production, always provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_11(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "IN PRODUCTION, ALWAYS PROVIDE AN EXPLICIT SECRET_KEY.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_12(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = None
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_13(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(None)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_14(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(65)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_15(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = None
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_16(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = None  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = {}  # Use database in production
    
    def xǁTokenManagerǁ__init____mutmut_17(self, secret_key: Optional[str] = None):
        """
        Initialize token manager.
        
        Args:
            secret_key: Secret key for signing tokens. 
                       If None, generates a random key (NOT recommended for production).
                       In production, ALWAYS provide an explicit secret key via 
                       environment variable or secure configuration.
        
        Warning:
            Auto-generated keys are only for development/testing.
            Production deployments MUST provide an explicit secret_key to
            prevent token invalidation across restarts.
        """
        if secret_key is None:
            # Generate random secret for development only
            import warnings
            warnings.warn(
                "Auto-generating secret key. This is ONLY for development. "
                "In production, ALWAYS provide an explicit secret_key.",
                UserWarning
            )
            secret_key = secrets.token_urlsafe(64)
        
        self._secret_key = secret_key
        self._revoked_tokens: Set[str] = set()  # Use Redis in production
        self._sessions: Dict[str, SessionInfo] = None  # Use database in production
    
    xǁTokenManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁ__init____mutmut_1': xǁTokenManagerǁ__init____mutmut_1, 
        'xǁTokenManagerǁ__init____mutmut_2': xǁTokenManagerǁ__init____mutmut_2, 
        'xǁTokenManagerǁ__init____mutmut_3': xǁTokenManagerǁ__init____mutmut_3, 
        'xǁTokenManagerǁ__init____mutmut_4': xǁTokenManagerǁ__init____mutmut_4, 
        'xǁTokenManagerǁ__init____mutmut_5': xǁTokenManagerǁ__init____mutmut_5, 
        'xǁTokenManagerǁ__init____mutmut_6': xǁTokenManagerǁ__init____mutmut_6, 
        'xǁTokenManagerǁ__init____mutmut_7': xǁTokenManagerǁ__init____mutmut_7, 
        'xǁTokenManagerǁ__init____mutmut_8': xǁTokenManagerǁ__init____mutmut_8, 
        'xǁTokenManagerǁ__init____mutmut_9': xǁTokenManagerǁ__init____mutmut_9, 
        'xǁTokenManagerǁ__init____mutmut_10': xǁTokenManagerǁ__init____mutmut_10, 
        'xǁTokenManagerǁ__init____mutmut_11': xǁTokenManagerǁ__init____mutmut_11, 
        'xǁTokenManagerǁ__init____mutmut_12': xǁTokenManagerǁ__init____mutmut_12, 
        'xǁTokenManagerǁ__init____mutmut_13': xǁTokenManagerǁ__init____mutmut_13, 
        'xǁTokenManagerǁ__init____mutmut_14': xǁTokenManagerǁ__init____mutmut_14, 
        'xǁTokenManagerǁ__init____mutmut_15': xǁTokenManagerǁ__init____mutmut_15, 
        'xǁTokenManagerǁ__init____mutmut_16': xǁTokenManagerǁ__init____mutmut_16, 
        'xǁTokenManagerǁ__init____mutmut_17': xǁTokenManagerǁ__init____mutmut_17
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTokenManagerǁ__init____mutmut_orig)
    xǁTokenManagerǁ__init____mutmut_orig.__name__ = 'xǁTokenManagerǁ__init__'
    
    def xǁTokenManagerǁ_encode_token__mutmut_orig(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_1(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = None
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_2(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'XXtypXX': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_3(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'TYP': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_4(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'XXJWTXX',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_5(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'jwt',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_6(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'XXalgXX': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_7(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'ALG': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_8(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'XXHS256XX',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_9(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'hs256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_10(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = None
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_11(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip(None)
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_12(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().lstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_13(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            None
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_14(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(None).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_15(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('XX=XX')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_16(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = None
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_17(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip(None)
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_18(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().lstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_19(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            None
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_20(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(None, default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_21(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=None).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_22(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_23(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), ).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_24(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('XX=XX')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_25(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = None
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_26(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = None
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_27(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            None,
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_28(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            None,
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_29(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            None
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_30(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_31(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_32(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_33(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = None
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_34(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip(None)
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_35(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().lstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_36(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(None).decode().rstrip('=')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_37(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('XX=XX')
        
        # Combine all parts
        token = f"{header_b64}.{payload_b64}.{signature_b64}"
        return token
    
    def xǁTokenManagerǁ_encode_token__mutmut_38(self, claims: TokenClaims) -> str:
        """
        Encode token (simplified JWT).
        
        In production, use PyJWT library for proper JWT support.
        This is a simplified implementation for demonstration.
        
        Args:
            claims: Token claims
        
        Returns:
            Encoded token string
        """
        import base64
        import hmac
        import hashlib
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': 'HS256',
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(claims.to_dict(), default=str).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Combine all parts
        token = None
        return token
    
    xǁTokenManagerǁ_encode_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁ_encode_token__mutmut_1': xǁTokenManagerǁ_encode_token__mutmut_1, 
        'xǁTokenManagerǁ_encode_token__mutmut_2': xǁTokenManagerǁ_encode_token__mutmut_2, 
        'xǁTokenManagerǁ_encode_token__mutmut_3': xǁTokenManagerǁ_encode_token__mutmut_3, 
        'xǁTokenManagerǁ_encode_token__mutmut_4': xǁTokenManagerǁ_encode_token__mutmut_4, 
        'xǁTokenManagerǁ_encode_token__mutmut_5': xǁTokenManagerǁ_encode_token__mutmut_5, 
        'xǁTokenManagerǁ_encode_token__mutmut_6': xǁTokenManagerǁ_encode_token__mutmut_6, 
        'xǁTokenManagerǁ_encode_token__mutmut_7': xǁTokenManagerǁ_encode_token__mutmut_7, 
        'xǁTokenManagerǁ_encode_token__mutmut_8': xǁTokenManagerǁ_encode_token__mutmut_8, 
        'xǁTokenManagerǁ_encode_token__mutmut_9': xǁTokenManagerǁ_encode_token__mutmut_9, 
        'xǁTokenManagerǁ_encode_token__mutmut_10': xǁTokenManagerǁ_encode_token__mutmut_10, 
        'xǁTokenManagerǁ_encode_token__mutmut_11': xǁTokenManagerǁ_encode_token__mutmut_11, 
        'xǁTokenManagerǁ_encode_token__mutmut_12': xǁTokenManagerǁ_encode_token__mutmut_12, 
        'xǁTokenManagerǁ_encode_token__mutmut_13': xǁTokenManagerǁ_encode_token__mutmut_13, 
        'xǁTokenManagerǁ_encode_token__mutmut_14': xǁTokenManagerǁ_encode_token__mutmut_14, 
        'xǁTokenManagerǁ_encode_token__mutmut_15': xǁTokenManagerǁ_encode_token__mutmut_15, 
        'xǁTokenManagerǁ_encode_token__mutmut_16': xǁTokenManagerǁ_encode_token__mutmut_16, 
        'xǁTokenManagerǁ_encode_token__mutmut_17': xǁTokenManagerǁ_encode_token__mutmut_17, 
        'xǁTokenManagerǁ_encode_token__mutmut_18': xǁTokenManagerǁ_encode_token__mutmut_18, 
        'xǁTokenManagerǁ_encode_token__mutmut_19': xǁTokenManagerǁ_encode_token__mutmut_19, 
        'xǁTokenManagerǁ_encode_token__mutmut_20': xǁTokenManagerǁ_encode_token__mutmut_20, 
        'xǁTokenManagerǁ_encode_token__mutmut_21': xǁTokenManagerǁ_encode_token__mutmut_21, 
        'xǁTokenManagerǁ_encode_token__mutmut_22': xǁTokenManagerǁ_encode_token__mutmut_22, 
        'xǁTokenManagerǁ_encode_token__mutmut_23': xǁTokenManagerǁ_encode_token__mutmut_23, 
        'xǁTokenManagerǁ_encode_token__mutmut_24': xǁTokenManagerǁ_encode_token__mutmut_24, 
        'xǁTokenManagerǁ_encode_token__mutmut_25': xǁTokenManagerǁ_encode_token__mutmut_25, 
        'xǁTokenManagerǁ_encode_token__mutmut_26': xǁTokenManagerǁ_encode_token__mutmut_26, 
        'xǁTokenManagerǁ_encode_token__mutmut_27': xǁTokenManagerǁ_encode_token__mutmut_27, 
        'xǁTokenManagerǁ_encode_token__mutmut_28': xǁTokenManagerǁ_encode_token__mutmut_28, 
        'xǁTokenManagerǁ_encode_token__mutmut_29': xǁTokenManagerǁ_encode_token__mutmut_29, 
        'xǁTokenManagerǁ_encode_token__mutmut_30': xǁTokenManagerǁ_encode_token__mutmut_30, 
        'xǁTokenManagerǁ_encode_token__mutmut_31': xǁTokenManagerǁ_encode_token__mutmut_31, 
        'xǁTokenManagerǁ_encode_token__mutmut_32': xǁTokenManagerǁ_encode_token__mutmut_32, 
        'xǁTokenManagerǁ_encode_token__mutmut_33': xǁTokenManagerǁ_encode_token__mutmut_33, 
        'xǁTokenManagerǁ_encode_token__mutmut_34': xǁTokenManagerǁ_encode_token__mutmut_34, 
        'xǁTokenManagerǁ_encode_token__mutmut_35': xǁTokenManagerǁ_encode_token__mutmut_35, 
        'xǁTokenManagerǁ_encode_token__mutmut_36': xǁTokenManagerǁ_encode_token__mutmut_36, 
        'xǁTokenManagerǁ_encode_token__mutmut_37': xǁTokenManagerǁ_encode_token__mutmut_37, 
        'xǁTokenManagerǁ_encode_token__mutmut_38': xǁTokenManagerǁ_encode_token__mutmut_38
    }
    
    def _encode_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁ_encode_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁ_encode_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _encode_token.__signature__ = _mutmut_signature(xǁTokenManagerǁ_encode_token__mutmut_orig)
    xǁTokenManagerǁ_encode_token__mutmut_orig.__name__ = 'xǁTokenManagerǁ_encode_token'
    
    def xǁTokenManagerǁ_decode_token__mutmut_orig(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_1(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = None
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_2(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split(None)
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_3(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('XX.XX')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_4(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) == 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_5(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 4:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_6(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError(None)
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_7(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("XXInvalid token formatXX")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_8(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_9(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("INVALID TOKEN FORMAT")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_10(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = None
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_11(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = None
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_12(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = None
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_13(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                None,
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_14(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                None,
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_15(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                None
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_16(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_17(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_18(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_19(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = None
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_20(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 - '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_21(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' / (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_22(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + 'XX=XX' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_23(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 + len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_24(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (5 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_25(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) / 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_26(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 5)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_27(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = None
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_28(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(None)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_29(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_30(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(None, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_31(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, None):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_32(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_33(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, ):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_34(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError(None)
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_35(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("XXInvalid token signatureXX")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_36(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_37(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("INVALID TOKEN SIGNATURE")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_38(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = None
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_39(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 - '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_40(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' / (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_41(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + 'XX=XX' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_42(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 + len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_43(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (5 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_44(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) / 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_45(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 5)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_46(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = None
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_47(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(None)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_48(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = None
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_49(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(None)
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_50(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = None
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_51(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(None)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_52(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = None
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_53(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(None)
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_54(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(None)}")
            raise ValueError(error_msg)
    
    def xǁTokenManagerǁ_decode_token__mutmut_55(self, token: str) -> TokenClaims:
        """
        Decode and verify token.
        
        Args:
            token: Encoded token string
        
        Returns:
            Decoded token claims
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        import base64
        import hmac
        import hashlib
        
        try:
            # Split token parts
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid token format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_b64_padded = signature_b64 + '=' * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)
            
            if not secrets.compare_digest(expected_signature, actual_signature):
                raise ValueError("Invalid token signature")
            
            # Decode payload
            payload_b64_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64_padded)
            payload = json.loads(payload_bytes.decode())
            
            # Create claims
            claims = TokenClaims.from_dict(payload)
            
            return claims
            
        except Exception as e:
            error_msg = sanitize_log_message(f"Token decode failed: {str(e)}")
            raise ValueError(None)
    
    xǁTokenManagerǁ_decode_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁ_decode_token__mutmut_1': xǁTokenManagerǁ_decode_token__mutmut_1, 
        'xǁTokenManagerǁ_decode_token__mutmut_2': xǁTokenManagerǁ_decode_token__mutmut_2, 
        'xǁTokenManagerǁ_decode_token__mutmut_3': xǁTokenManagerǁ_decode_token__mutmut_3, 
        'xǁTokenManagerǁ_decode_token__mutmut_4': xǁTokenManagerǁ_decode_token__mutmut_4, 
        'xǁTokenManagerǁ_decode_token__mutmut_5': xǁTokenManagerǁ_decode_token__mutmut_5, 
        'xǁTokenManagerǁ_decode_token__mutmut_6': xǁTokenManagerǁ_decode_token__mutmut_6, 
        'xǁTokenManagerǁ_decode_token__mutmut_7': xǁTokenManagerǁ_decode_token__mutmut_7, 
        'xǁTokenManagerǁ_decode_token__mutmut_8': xǁTokenManagerǁ_decode_token__mutmut_8, 
        'xǁTokenManagerǁ_decode_token__mutmut_9': xǁTokenManagerǁ_decode_token__mutmut_9, 
        'xǁTokenManagerǁ_decode_token__mutmut_10': xǁTokenManagerǁ_decode_token__mutmut_10, 
        'xǁTokenManagerǁ_decode_token__mutmut_11': xǁTokenManagerǁ_decode_token__mutmut_11, 
        'xǁTokenManagerǁ_decode_token__mutmut_12': xǁTokenManagerǁ_decode_token__mutmut_12, 
        'xǁTokenManagerǁ_decode_token__mutmut_13': xǁTokenManagerǁ_decode_token__mutmut_13, 
        'xǁTokenManagerǁ_decode_token__mutmut_14': xǁTokenManagerǁ_decode_token__mutmut_14, 
        'xǁTokenManagerǁ_decode_token__mutmut_15': xǁTokenManagerǁ_decode_token__mutmut_15, 
        'xǁTokenManagerǁ_decode_token__mutmut_16': xǁTokenManagerǁ_decode_token__mutmut_16, 
        'xǁTokenManagerǁ_decode_token__mutmut_17': xǁTokenManagerǁ_decode_token__mutmut_17, 
        'xǁTokenManagerǁ_decode_token__mutmut_18': xǁTokenManagerǁ_decode_token__mutmut_18, 
        'xǁTokenManagerǁ_decode_token__mutmut_19': xǁTokenManagerǁ_decode_token__mutmut_19, 
        'xǁTokenManagerǁ_decode_token__mutmut_20': xǁTokenManagerǁ_decode_token__mutmut_20, 
        'xǁTokenManagerǁ_decode_token__mutmut_21': xǁTokenManagerǁ_decode_token__mutmut_21, 
        'xǁTokenManagerǁ_decode_token__mutmut_22': xǁTokenManagerǁ_decode_token__mutmut_22, 
        'xǁTokenManagerǁ_decode_token__mutmut_23': xǁTokenManagerǁ_decode_token__mutmut_23, 
        'xǁTokenManagerǁ_decode_token__mutmut_24': xǁTokenManagerǁ_decode_token__mutmut_24, 
        'xǁTokenManagerǁ_decode_token__mutmut_25': xǁTokenManagerǁ_decode_token__mutmut_25, 
        'xǁTokenManagerǁ_decode_token__mutmut_26': xǁTokenManagerǁ_decode_token__mutmut_26, 
        'xǁTokenManagerǁ_decode_token__mutmut_27': xǁTokenManagerǁ_decode_token__mutmut_27, 
        'xǁTokenManagerǁ_decode_token__mutmut_28': xǁTokenManagerǁ_decode_token__mutmut_28, 
        'xǁTokenManagerǁ_decode_token__mutmut_29': xǁTokenManagerǁ_decode_token__mutmut_29, 
        'xǁTokenManagerǁ_decode_token__mutmut_30': xǁTokenManagerǁ_decode_token__mutmut_30, 
        'xǁTokenManagerǁ_decode_token__mutmut_31': xǁTokenManagerǁ_decode_token__mutmut_31, 
        'xǁTokenManagerǁ_decode_token__mutmut_32': xǁTokenManagerǁ_decode_token__mutmut_32, 
        'xǁTokenManagerǁ_decode_token__mutmut_33': xǁTokenManagerǁ_decode_token__mutmut_33, 
        'xǁTokenManagerǁ_decode_token__mutmut_34': xǁTokenManagerǁ_decode_token__mutmut_34, 
        'xǁTokenManagerǁ_decode_token__mutmut_35': xǁTokenManagerǁ_decode_token__mutmut_35, 
        'xǁTokenManagerǁ_decode_token__mutmut_36': xǁTokenManagerǁ_decode_token__mutmut_36, 
        'xǁTokenManagerǁ_decode_token__mutmut_37': xǁTokenManagerǁ_decode_token__mutmut_37, 
        'xǁTokenManagerǁ_decode_token__mutmut_38': xǁTokenManagerǁ_decode_token__mutmut_38, 
        'xǁTokenManagerǁ_decode_token__mutmut_39': xǁTokenManagerǁ_decode_token__mutmut_39, 
        'xǁTokenManagerǁ_decode_token__mutmut_40': xǁTokenManagerǁ_decode_token__mutmut_40, 
        'xǁTokenManagerǁ_decode_token__mutmut_41': xǁTokenManagerǁ_decode_token__mutmut_41, 
        'xǁTokenManagerǁ_decode_token__mutmut_42': xǁTokenManagerǁ_decode_token__mutmut_42, 
        'xǁTokenManagerǁ_decode_token__mutmut_43': xǁTokenManagerǁ_decode_token__mutmut_43, 
        'xǁTokenManagerǁ_decode_token__mutmut_44': xǁTokenManagerǁ_decode_token__mutmut_44, 
        'xǁTokenManagerǁ_decode_token__mutmut_45': xǁTokenManagerǁ_decode_token__mutmut_45, 
        'xǁTokenManagerǁ_decode_token__mutmut_46': xǁTokenManagerǁ_decode_token__mutmut_46, 
        'xǁTokenManagerǁ_decode_token__mutmut_47': xǁTokenManagerǁ_decode_token__mutmut_47, 
        'xǁTokenManagerǁ_decode_token__mutmut_48': xǁTokenManagerǁ_decode_token__mutmut_48, 
        'xǁTokenManagerǁ_decode_token__mutmut_49': xǁTokenManagerǁ_decode_token__mutmut_49, 
        'xǁTokenManagerǁ_decode_token__mutmut_50': xǁTokenManagerǁ_decode_token__mutmut_50, 
        'xǁTokenManagerǁ_decode_token__mutmut_51': xǁTokenManagerǁ_decode_token__mutmut_51, 
        'xǁTokenManagerǁ_decode_token__mutmut_52': xǁTokenManagerǁ_decode_token__mutmut_52, 
        'xǁTokenManagerǁ_decode_token__mutmut_53': xǁTokenManagerǁ_decode_token__mutmut_53, 
        'xǁTokenManagerǁ_decode_token__mutmut_54': xǁTokenManagerǁ_decode_token__mutmut_54, 
        'xǁTokenManagerǁ_decode_token__mutmut_55': xǁTokenManagerǁ_decode_token__mutmut_55
    }
    
    def _decode_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁ_decode_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁ_decode_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _decode_token.__signature__ = _mutmut_signature(xǁTokenManagerǁ_decode_token__mutmut_orig)
    xǁTokenManagerǁ_decode_token__mutmut_orig.__name__ = 'xǁTokenManagerǁ_decode_token'
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_orig(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_1(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = None
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_2(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = None
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_3(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(None)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_4(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(17)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_5(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = None
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_6(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=None,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_7(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=None,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_8(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=None,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_9(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=None,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_10(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=None,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_11(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=None,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_12(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_13(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_14(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_15(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_16(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_17(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_18(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now - self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_access_token__mutmut_19(self, user_id: str, scope: Optional[str] = None) -> str:
        """
        Generate access token.
        
        Args:
            user_id: User identifier
            scope: Optional permissions scope
        
        Returns:
            Encoded access token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.ACCESS_TOKEN_EXPIRY,
            type=TokenType.ACCESS,
            scope=scope,
            jti=jti,
        )
        
        return self._encode_token(None)
    
    xǁTokenManagerǁgenerate_access_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁgenerate_access_token__mutmut_1': xǁTokenManagerǁgenerate_access_token__mutmut_1, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_2': xǁTokenManagerǁgenerate_access_token__mutmut_2, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_3': xǁTokenManagerǁgenerate_access_token__mutmut_3, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_4': xǁTokenManagerǁgenerate_access_token__mutmut_4, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_5': xǁTokenManagerǁgenerate_access_token__mutmut_5, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_6': xǁTokenManagerǁgenerate_access_token__mutmut_6, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_7': xǁTokenManagerǁgenerate_access_token__mutmut_7, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_8': xǁTokenManagerǁgenerate_access_token__mutmut_8, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_9': xǁTokenManagerǁgenerate_access_token__mutmut_9, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_10': xǁTokenManagerǁgenerate_access_token__mutmut_10, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_11': xǁTokenManagerǁgenerate_access_token__mutmut_11, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_12': xǁTokenManagerǁgenerate_access_token__mutmut_12, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_13': xǁTokenManagerǁgenerate_access_token__mutmut_13, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_14': xǁTokenManagerǁgenerate_access_token__mutmut_14, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_15': xǁTokenManagerǁgenerate_access_token__mutmut_15, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_16': xǁTokenManagerǁgenerate_access_token__mutmut_16, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_17': xǁTokenManagerǁgenerate_access_token__mutmut_17, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_18': xǁTokenManagerǁgenerate_access_token__mutmut_18, 
        'xǁTokenManagerǁgenerate_access_token__mutmut_19': xǁTokenManagerǁgenerate_access_token__mutmut_19
    }
    
    def generate_access_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁgenerate_access_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁgenerate_access_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_access_token.__signature__ = _mutmut_signature(xǁTokenManagerǁgenerate_access_token__mutmut_orig)
    xǁTokenManagerǁgenerate_access_token__mutmut_orig.__name__ = 'xǁTokenManagerǁgenerate_access_token'
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_orig(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_1(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = None
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_2(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = None
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_3(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(None)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_4(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(17)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_5(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = None
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_6(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=None,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_7(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=None,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_8(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=None,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_9(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=None,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_10(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=None,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_11(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_12(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_13(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_14(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_15(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_16(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now - self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(claims)
    
    def xǁTokenManagerǁgenerate_refresh_token__mutmut_17(self, user_id: str) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
        
        Returns:
            Encoded refresh token
        """
        now = time.time()
        jti = secrets.token_urlsafe(16)
        
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.REFRESH_TOKEN_EXPIRY,
            type=TokenType.REFRESH,
            jti=jti,
        )
        
        return self._encode_token(None)
    
    xǁTokenManagerǁgenerate_refresh_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁgenerate_refresh_token__mutmut_1': xǁTokenManagerǁgenerate_refresh_token__mutmut_1, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_2': xǁTokenManagerǁgenerate_refresh_token__mutmut_2, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_3': xǁTokenManagerǁgenerate_refresh_token__mutmut_3, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_4': xǁTokenManagerǁgenerate_refresh_token__mutmut_4, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_5': xǁTokenManagerǁgenerate_refresh_token__mutmut_5, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_6': xǁTokenManagerǁgenerate_refresh_token__mutmut_6, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_7': xǁTokenManagerǁgenerate_refresh_token__mutmut_7, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_8': xǁTokenManagerǁgenerate_refresh_token__mutmut_8, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_9': xǁTokenManagerǁgenerate_refresh_token__mutmut_9, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_10': xǁTokenManagerǁgenerate_refresh_token__mutmut_10, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_11': xǁTokenManagerǁgenerate_refresh_token__mutmut_11, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_12': xǁTokenManagerǁgenerate_refresh_token__mutmut_12, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_13': xǁTokenManagerǁgenerate_refresh_token__mutmut_13, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_14': xǁTokenManagerǁgenerate_refresh_token__mutmut_14, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_15': xǁTokenManagerǁgenerate_refresh_token__mutmut_15, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_16': xǁTokenManagerǁgenerate_refresh_token__mutmut_16, 
        'xǁTokenManagerǁgenerate_refresh_token__mutmut_17': xǁTokenManagerǁgenerate_refresh_token__mutmut_17
    }
    
    def generate_refresh_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁgenerate_refresh_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁgenerate_refresh_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_refresh_token.__signature__ = _mutmut_signature(xǁTokenManagerǁgenerate_refresh_token__mutmut_orig)
    xǁTokenManagerǁgenerate_refresh_token__mutmut_orig.__name__ = 'xǁTokenManagerǁgenerate_refresh_token'
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_orig(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_1(self, user_id: str, mfa_verified: bool = True,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_2(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = None
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_3(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = None
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_4(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(None)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_5(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(33)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_6(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = None
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_7(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=None,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_8(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=None,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_9(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=None,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_10(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=None,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_11(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=None,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_12(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=None,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_13(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=None,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_14(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_15(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_16(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_17(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_18(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_19(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_20(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_21(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = None
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_22(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = None
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_23(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=None,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_24(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=None,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_25(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=None,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_26(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=None,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_27(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=None,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_28(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_29(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_30(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_31(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_32(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_33(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now - self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(claims)
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_34(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = None
        return token, session_id
    
    def xǁTokenManagerǁgenerate_session_token__mutmut_35(self, user_id: str, mfa_verified: bool = False,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate session token and create session.
        
        Args:
            user_id: User identifier
            mfa_verified: Whether MFA was verified
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (session_token, session_id)
        """
        now = time.time()
        session_id = secrets.token_urlsafe(32)
        
        # Create session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )
        
        self._sessions[session_id] = session
        
        # Generate token
        claims = TokenClaims(
            sub=user_id,
            iat=now,
            exp=now + self.SESSION_TOKEN_EXPIRY,
            type=TokenType.SESSION,
            jti=session_id,
        )
        
        token = self._encode_token(None)
        return token, session_id
    
    xǁTokenManagerǁgenerate_session_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁgenerate_session_token__mutmut_1': xǁTokenManagerǁgenerate_session_token__mutmut_1, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_2': xǁTokenManagerǁgenerate_session_token__mutmut_2, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_3': xǁTokenManagerǁgenerate_session_token__mutmut_3, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_4': xǁTokenManagerǁgenerate_session_token__mutmut_4, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_5': xǁTokenManagerǁgenerate_session_token__mutmut_5, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_6': xǁTokenManagerǁgenerate_session_token__mutmut_6, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_7': xǁTokenManagerǁgenerate_session_token__mutmut_7, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_8': xǁTokenManagerǁgenerate_session_token__mutmut_8, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_9': xǁTokenManagerǁgenerate_session_token__mutmut_9, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_10': xǁTokenManagerǁgenerate_session_token__mutmut_10, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_11': xǁTokenManagerǁgenerate_session_token__mutmut_11, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_12': xǁTokenManagerǁgenerate_session_token__mutmut_12, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_13': xǁTokenManagerǁgenerate_session_token__mutmut_13, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_14': xǁTokenManagerǁgenerate_session_token__mutmut_14, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_15': xǁTokenManagerǁgenerate_session_token__mutmut_15, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_16': xǁTokenManagerǁgenerate_session_token__mutmut_16, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_17': xǁTokenManagerǁgenerate_session_token__mutmut_17, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_18': xǁTokenManagerǁgenerate_session_token__mutmut_18, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_19': xǁTokenManagerǁgenerate_session_token__mutmut_19, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_20': xǁTokenManagerǁgenerate_session_token__mutmut_20, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_21': xǁTokenManagerǁgenerate_session_token__mutmut_21, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_22': xǁTokenManagerǁgenerate_session_token__mutmut_22, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_23': xǁTokenManagerǁgenerate_session_token__mutmut_23, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_24': xǁTokenManagerǁgenerate_session_token__mutmut_24, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_25': xǁTokenManagerǁgenerate_session_token__mutmut_25, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_26': xǁTokenManagerǁgenerate_session_token__mutmut_26, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_27': xǁTokenManagerǁgenerate_session_token__mutmut_27, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_28': xǁTokenManagerǁgenerate_session_token__mutmut_28, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_29': xǁTokenManagerǁgenerate_session_token__mutmut_29, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_30': xǁTokenManagerǁgenerate_session_token__mutmut_30, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_31': xǁTokenManagerǁgenerate_session_token__mutmut_31, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_32': xǁTokenManagerǁgenerate_session_token__mutmut_32, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_33': xǁTokenManagerǁgenerate_session_token__mutmut_33, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_34': xǁTokenManagerǁgenerate_session_token__mutmut_34, 
        'xǁTokenManagerǁgenerate_session_token__mutmut_35': xǁTokenManagerǁgenerate_session_token__mutmut_35
    }
    
    def generate_session_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁgenerate_session_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁgenerate_session_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_session_token.__signature__ = _mutmut_signature(xǁTokenManagerǁgenerate_session_token__mutmut_orig)
    xǁTokenManagerǁgenerate_session_token__mutmut_orig.__name__ = 'xǁTokenManagerǁgenerate_session_token'
    
    def xǁTokenManagerǁvalidate_token__mutmut_orig(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_1(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = None
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_2(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(None)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_3(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp <= time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_4(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError(None)
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_5(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("XXToken expiredXX")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_6(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_7(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("TOKEN EXPIRED")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_8(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type or claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_9(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type == expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_10(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(None)
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_11(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti or claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_12(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti not in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_13(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError(None)
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_14(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("XXToken revokedXX")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_15(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_16(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("TOKEN REVOKED")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_17(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION or claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_18(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type != TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_19(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = None
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_20(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(None)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_21(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_22(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError(None)
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_23(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("XXSession not foundXX")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_24(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("session not found")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_25(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("SESSION NOT FOUND")
            if not session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_26(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if session.is_active():
                raise ValueError("Session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_27(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError(None)
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_28(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("XXSession expiredXX")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_29(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("session expired")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    def xǁTokenManagerǁvalidate_token__mutmut_30(self, token: str, expected_type: Optional[TokenType] = None) -> TokenClaims:
        """
        Validate token and return claims.
        
        Args:
            token: Token to validate
            expected_type: Expected token type (optional)
        
        Returns:
            Validated token claims
        
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        # Decode token
        claims = self._decode_token(token)
        
        # Check expiration
        if claims.exp < time.time():
            raise ValueError("Token expired")
        
        # Check type if specified
        if expected_type and claims.type != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type.value}, got {claims.type.value}")
        
        # Check revocation
        if claims.jti and claims.jti in self._revoked_tokens:
            raise ValueError("Token revoked")
        
        # For session tokens, validate session
        if claims.type == TokenType.SESSION and claims.jti:
            session = self._sessions.get(claims.jti)
            if not session:
                raise ValueError("Session not found")
            if not session.is_active():
                raise ValueError("SESSION EXPIRED")
            
            # Update activity
            session.update_activity()
        
        return claims
    
    xǁTokenManagerǁvalidate_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁvalidate_token__mutmut_1': xǁTokenManagerǁvalidate_token__mutmut_1, 
        'xǁTokenManagerǁvalidate_token__mutmut_2': xǁTokenManagerǁvalidate_token__mutmut_2, 
        'xǁTokenManagerǁvalidate_token__mutmut_3': xǁTokenManagerǁvalidate_token__mutmut_3, 
        'xǁTokenManagerǁvalidate_token__mutmut_4': xǁTokenManagerǁvalidate_token__mutmut_4, 
        'xǁTokenManagerǁvalidate_token__mutmut_5': xǁTokenManagerǁvalidate_token__mutmut_5, 
        'xǁTokenManagerǁvalidate_token__mutmut_6': xǁTokenManagerǁvalidate_token__mutmut_6, 
        'xǁTokenManagerǁvalidate_token__mutmut_7': xǁTokenManagerǁvalidate_token__mutmut_7, 
        'xǁTokenManagerǁvalidate_token__mutmut_8': xǁTokenManagerǁvalidate_token__mutmut_8, 
        'xǁTokenManagerǁvalidate_token__mutmut_9': xǁTokenManagerǁvalidate_token__mutmut_9, 
        'xǁTokenManagerǁvalidate_token__mutmut_10': xǁTokenManagerǁvalidate_token__mutmut_10, 
        'xǁTokenManagerǁvalidate_token__mutmut_11': xǁTokenManagerǁvalidate_token__mutmut_11, 
        'xǁTokenManagerǁvalidate_token__mutmut_12': xǁTokenManagerǁvalidate_token__mutmut_12, 
        'xǁTokenManagerǁvalidate_token__mutmut_13': xǁTokenManagerǁvalidate_token__mutmut_13, 
        'xǁTokenManagerǁvalidate_token__mutmut_14': xǁTokenManagerǁvalidate_token__mutmut_14, 
        'xǁTokenManagerǁvalidate_token__mutmut_15': xǁTokenManagerǁvalidate_token__mutmut_15, 
        'xǁTokenManagerǁvalidate_token__mutmut_16': xǁTokenManagerǁvalidate_token__mutmut_16, 
        'xǁTokenManagerǁvalidate_token__mutmut_17': xǁTokenManagerǁvalidate_token__mutmut_17, 
        'xǁTokenManagerǁvalidate_token__mutmut_18': xǁTokenManagerǁvalidate_token__mutmut_18, 
        'xǁTokenManagerǁvalidate_token__mutmut_19': xǁTokenManagerǁvalidate_token__mutmut_19, 
        'xǁTokenManagerǁvalidate_token__mutmut_20': xǁTokenManagerǁvalidate_token__mutmut_20, 
        'xǁTokenManagerǁvalidate_token__mutmut_21': xǁTokenManagerǁvalidate_token__mutmut_21, 
        'xǁTokenManagerǁvalidate_token__mutmut_22': xǁTokenManagerǁvalidate_token__mutmut_22, 
        'xǁTokenManagerǁvalidate_token__mutmut_23': xǁTokenManagerǁvalidate_token__mutmut_23, 
        'xǁTokenManagerǁvalidate_token__mutmut_24': xǁTokenManagerǁvalidate_token__mutmut_24, 
        'xǁTokenManagerǁvalidate_token__mutmut_25': xǁTokenManagerǁvalidate_token__mutmut_25, 
        'xǁTokenManagerǁvalidate_token__mutmut_26': xǁTokenManagerǁvalidate_token__mutmut_26, 
        'xǁTokenManagerǁvalidate_token__mutmut_27': xǁTokenManagerǁvalidate_token__mutmut_27, 
        'xǁTokenManagerǁvalidate_token__mutmut_28': xǁTokenManagerǁvalidate_token__mutmut_28, 
        'xǁTokenManagerǁvalidate_token__mutmut_29': xǁTokenManagerǁvalidate_token__mutmut_29, 
        'xǁTokenManagerǁvalidate_token__mutmut_30': xǁTokenManagerǁvalidate_token__mutmut_30
    }
    
    def validate_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁvalidate_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁvalidate_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_token.__signature__ = _mutmut_signature(xǁTokenManagerǁvalidate_token__mutmut_orig)
    xǁTokenManagerǁvalidate_token__mutmut_orig.__name__ = 'xǁTokenManagerǁvalidate_token'
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_orig(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_1(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = None
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_2(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(None, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_3(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, None)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_4(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_5(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, )
        
        # Generate new access token
        return self.generate_access_token(claims.sub, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_6(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(None, claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_7(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, None)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_8(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.scope)
    
    def xǁTokenManagerǁrefresh_access_token__mutmut_9(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token
        
        Raises:
            ValueError: If refresh token is invalid
        """
        # Validate refresh token
        claims = self.validate_token(refresh_token, TokenType.REFRESH)
        
        # Generate new access token
        return self.generate_access_token(claims.sub, )
    
    xǁTokenManagerǁrefresh_access_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁrefresh_access_token__mutmut_1': xǁTokenManagerǁrefresh_access_token__mutmut_1, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_2': xǁTokenManagerǁrefresh_access_token__mutmut_2, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_3': xǁTokenManagerǁrefresh_access_token__mutmut_3, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_4': xǁTokenManagerǁrefresh_access_token__mutmut_4, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_5': xǁTokenManagerǁrefresh_access_token__mutmut_5, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_6': xǁTokenManagerǁrefresh_access_token__mutmut_6, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_7': xǁTokenManagerǁrefresh_access_token__mutmut_7, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_8': xǁTokenManagerǁrefresh_access_token__mutmut_8, 
        'xǁTokenManagerǁrefresh_access_token__mutmut_9': xǁTokenManagerǁrefresh_access_token__mutmut_9
    }
    
    def refresh_access_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁrefresh_access_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁrefresh_access_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    refresh_access_token.__signature__ = _mutmut_signature(xǁTokenManagerǁrefresh_access_token__mutmut_orig)
    xǁTokenManagerǁrefresh_access_token__mutmut_orig.__name__ = 'xǁTokenManagerǁrefresh_access_token'
    
    def xǁTokenManagerǁrevoke_token__mutmut_orig(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_1(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = None
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_2(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(None)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_3(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(None)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_4(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION or claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_5(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type != TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_6(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti not in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_7(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return False
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_8(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return True
        
        return False
    
    def xǁTokenManagerǁrevoke_token__mutmut_9(self, token: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        
        Returns:
            True if token was revoked
        """
        try:
            claims = self._decode_token(token)
            if claims.jti:
                self._revoked_tokens.add(claims.jti)
                
                # If session token, remove session
                if claims.type == TokenType.SESSION and claims.jti in self._sessions:
                    del self._sessions[claims.jti]
                
                return True
        except ValueError:
            # Invalid or malformed token; nothing to revoke (not an error condition)
            return False
        
        return True
    
    xǁTokenManagerǁrevoke_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁrevoke_token__mutmut_1': xǁTokenManagerǁrevoke_token__mutmut_1, 
        'xǁTokenManagerǁrevoke_token__mutmut_2': xǁTokenManagerǁrevoke_token__mutmut_2, 
        'xǁTokenManagerǁrevoke_token__mutmut_3': xǁTokenManagerǁrevoke_token__mutmut_3, 
        'xǁTokenManagerǁrevoke_token__mutmut_4': xǁTokenManagerǁrevoke_token__mutmut_4, 
        'xǁTokenManagerǁrevoke_token__mutmut_5': xǁTokenManagerǁrevoke_token__mutmut_5, 
        'xǁTokenManagerǁrevoke_token__mutmut_6': xǁTokenManagerǁrevoke_token__mutmut_6, 
        'xǁTokenManagerǁrevoke_token__mutmut_7': xǁTokenManagerǁrevoke_token__mutmut_7, 
        'xǁTokenManagerǁrevoke_token__mutmut_8': xǁTokenManagerǁrevoke_token__mutmut_8, 
        'xǁTokenManagerǁrevoke_token__mutmut_9': xǁTokenManagerǁrevoke_token__mutmut_9
    }
    
    def revoke_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁrevoke_token__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁrevoke_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    revoke_token.__signature__ = _mutmut_signature(xǁTokenManagerǁrevoke_token__mutmut_orig)
    xǁTokenManagerǁrevoke_token__mutmut_orig.__name__ = 'xǁTokenManagerǁrevoke_token'
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_orig(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_1(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = None
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_2(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 1
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_3(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(None):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_4(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id != user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_5(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(None)
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_6(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count = 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_7(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count -= 1
        
        return count
    
    def xǁTokenManagerǁrevoke_all_user_tokens__mutmut_8(self, user_id: str) -> int:
        """
        Revoke all tokens for a user (e.g., on password change).
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        
        # Revoke all sessions for user
        for session_id, session in list(self._sessions.items()):
            if session.user_id == user_id:
                self._revoked_tokens.add(session_id)
                del self._sessions[session_id]
                count += 2
        
        return count
    
    xǁTokenManagerǁrevoke_all_user_tokens__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_1': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_1, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_2': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_2, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_3': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_3, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_4': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_4, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_5': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_5, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_6': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_6, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_7': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_7, 
        'xǁTokenManagerǁrevoke_all_user_tokens__mutmut_8': xǁTokenManagerǁrevoke_all_user_tokens__mutmut_8
    }
    
    def revoke_all_user_tokens(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁrevoke_all_user_tokens__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁrevoke_all_user_tokens__mutmut_mutants"), args, kwargs, self)
        return result 
    
    revoke_all_user_tokens.__signature__ = _mutmut_signature(xǁTokenManagerǁrevoke_all_user_tokens__mutmut_orig)
    xǁTokenManagerǁrevoke_all_user_tokens__mutmut_orig.__name__ = 'xǁTokenManagerǁrevoke_all_user_tokens'
    
    def xǁTokenManagerǁget_session__mutmut_orig(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
        
        Returns:
            SessionInfo if found, None otherwise
        """
        return self._sessions.get(session_id)
    
    def xǁTokenManagerǁget_session__mutmut_1(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information.
        
        Args:
            session_id: Session identifier
        
        Returns:
            SessionInfo if found, None otherwise
        """
        return self._sessions.get(None)
    
    xǁTokenManagerǁget_session__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁget_session__mutmut_1': xǁTokenManagerǁget_session__mutmut_1
    }
    
    def get_session(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁget_session__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁget_session__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_session.__signature__ = _mutmut_signature(xǁTokenManagerǁget_session__mutmut_orig)
    xǁTokenManagerǁget_session__mutmut_orig.__name__ = 'xǁTokenManagerǁget_session'
    
    def xǁTokenManagerǁget_user_sessions__mutmut_orig(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active sessions
        """
        return [
            session for session in self._sessions.values()
            if session.user_id == user_id and session.is_active()
        ]
    
    def xǁTokenManagerǁget_user_sessions__mutmut_1(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active sessions
        """
        return [
            session for session in self._sessions.values()
            if session.user_id == user_id or session.is_active()
        ]
    
    def xǁTokenManagerǁget_user_sessions__mutmut_2(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active sessions
        """
        return [
            session for session in self._sessions.values()
            if session.user_id != user_id and session.is_active()
        ]
    
    xǁTokenManagerǁget_user_sessions__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁget_user_sessions__mutmut_1': xǁTokenManagerǁget_user_sessions__mutmut_1, 
        'xǁTokenManagerǁget_user_sessions__mutmut_2': xǁTokenManagerǁget_user_sessions__mutmut_2
    }
    
    def get_user_sessions(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁget_user_sessions__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁget_user_sessions__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_user_sessions.__signature__ = _mutmut_signature(xǁTokenManagerǁget_user_sessions__mutmut_orig)
    xǁTokenManagerǁget_user_sessions__mutmut_orig.__name__ = 'xǁTokenManagerǁget_user_sessions'
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_orig(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_1(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = None
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_2(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 1
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_3(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(None):
            if not session.is_active():
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_4(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if session.is_active():
                del self._sessions[session_id]
                count += 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_5(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count = 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_6(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count -= 1
        
        return count
    
    def xǁTokenManagerǁcleanup_expired_sessions__mutmut_7(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._sessions.items()):
            if not session.is_active():
                del self._sessions[session_id]
                count += 2
        
        return count
    
    xǁTokenManagerǁcleanup_expired_sessions__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTokenManagerǁcleanup_expired_sessions__mutmut_1': xǁTokenManagerǁcleanup_expired_sessions__mutmut_1, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_2': xǁTokenManagerǁcleanup_expired_sessions__mutmut_2, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_3': xǁTokenManagerǁcleanup_expired_sessions__mutmut_3, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_4': xǁTokenManagerǁcleanup_expired_sessions__mutmut_4, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_5': xǁTokenManagerǁcleanup_expired_sessions__mutmut_5, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_6': xǁTokenManagerǁcleanup_expired_sessions__mutmut_6, 
        'xǁTokenManagerǁcleanup_expired_sessions__mutmut_7': xǁTokenManagerǁcleanup_expired_sessions__mutmut_7
    }
    
    def cleanup_expired_sessions(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTokenManagerǁcleanup_expired_sessions__mutmut_orig"), object.__getattribute__(self, "xǁTokenManagerǁcleanup_expired_sessions__mutmut_mutants"), args, kwargs, self)
        return result 
    
    cleanup_expired_sessions.__signature__ = _mutmut_signature(xǁTokenManagerǁcleanup_expired_sessions__mutmut_orig)
    xǁTokenManagerǁcleanup_expired_sessions__mutmut_orig.__name__ = 'xǁTokenManagerǁcleanup_expired_sessions'
