"""
Production Authentication Middleware for Codex platform.

Provides FastAPI/Starlette middleware for authentication and authorization.
Supports JWT, API key, and OAuth authentication methods.

Usage:
    from codex.auth.middleware import AuthMiddleware, require_auth
    
    app = FastAPI()
    app.add_middleware(AuthMiddleware, token_manager=token_manager)
    
    @app.get("/protected")
    @require_auth(scopes=["read"])
    async def protected_endpoint(request: Request):
        return {"user": request.state.user}
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Callable, Dict, List, Optional, Set, Any

from .token_manager import TokenManager, TokenClaims
from ..security_utils import sanitize_log_message


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


class AuthMethod(Enum):
    """Supported authentication methods."""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH = "oauth"
    NONE = "none"


@dataclass
class AuthConfig:
    """Authentication middleware configuration."""
    enabled: bool = True
    default_method: AuthMethod = AuthMethod.JWT
    api_key_header: str = "X-API-Key"
    bearer_header: str = "Authorization"
    allowed_methods: Set[AuthMethod] = field(default_factory=lambda: {AuthMethod.JWT, AuthMethod.API_KEY})
    exempt_paths: Set[str] = field(default_factory=lambda: {"/health", "/ready", "/metrics"})
    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds


@dataclass
class AuthResult:
    """Authentication result."""
    authenticated: bool
    method: AuthMethod
    user_id: Optional[str] = None
    claims: Optional[TokenClaims] = None
    scopes: Set[str] = field(default_factory=set)
    error: Optional[str] = None


class APIKeyValidator:
    """API key validation with secure HMAC-SHA256 hashing."""
    
    def xǁAPIKeyValidatorǁ__init____mutmut_orig(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_1(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = None  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_2(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = None
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_3(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = None
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_4(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get(None)
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_5(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("XXAUTH_SECRET_KEYXX")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_6(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("auth_secret_key")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_7(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_8(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get(None) != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_9(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("XXCODEX_ENVXX") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_10(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("codex_env") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_11(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") == "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_12(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "XXproductionXX":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_13(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "PRODUCTION":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_14(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        None
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_15(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "XXAUTH_SECRET_KEY not set. Using development fallback. XX"
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_16(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "auth_secret_key not set. using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_17(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY NOT SET. USING DEVELOPMENT FALLBACK. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_18(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "XXSet AUTH_SECRET_KEY environment variable in production.XX"
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_19(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "set auth_secret_key environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_20(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "SET AUTH_SECRET_KEY ENVIRONMENT VARIABLE IN PRODUCTION."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_21(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = None
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_22(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "XXcodex-dev-secret-key-change-in-productionXX"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_23(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "CODEX-DEV-SECRET-KEY-CHANGE-IN-PRODUCTION"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_24(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        None
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_25(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "XXAUTH_SECRET_KEY environment variable must be set in production. XX"
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_26(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "auth_secret_key environment variable must be set in production. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_27(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY ENVIRONMENT VARIABLE MUST BE SET IN PRODUCTION. "
                        "Generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_28(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "XXGenerate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'XX"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_29(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "generate a secure random key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                    )
    
    def xǁAPIKeyValidatorǁ__init____mutmut_30(self, secret_key: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            secret_key: Secret key for HMAC hashing. If not provided, reads from environment.
        
        Raises:
            ValueError: If AUTH_SECRET_KEY is not set in production environment.
        """
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> key_info
        
        # Get secret key from parameter, environment, or raise error in production
        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = os.environ.get("AUTH_SECRET_KEY")
            if not self._secret_key:
                # Allow development with warning
                if os.environ.get("CODEX_ENV") != "production":
                    logger.warning(
                        "AUTH_SECRET_KEY not set. Using development fallback. "
                        "Set AUTH_SECRET_KEY environment variable in production."
                    )
                    self._secret_key = "codex-dev-secret-key-change-in-production"
                else:
                    raise ValueError(
                        "AUTH_SECRET_KEY environment variable must be set in production. "
                        "GENERATE A SECURE RANDOM KEY: PYTHON -C 'IMPORT SECRETS; PRINT(SECRETS.TOKEN_URLSAFE(32))'"
                    )
    
    xǁAPIKeyValidatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁ__init____mutmut_1': xǁAPIKeyValidatorǁ__init____mutmut_1, 
        'xǁAPIKeyValidatorǁ__init____mutmut_2': xǁAPIKeyValidatorǁ__init____mutmut_2, 
        'xǁAPIKeyValidatorǁ__init____mutmut_3': xǁAPIKeyValidatorǁ__init____mutmut_3, 
        'xǁAPIKeyValidatorǁ__init____mutmut_4': xǁAPIKeyValidatorǁ__init____mutmut_4, 
        'xǁAPIKeyValidatorǁ__init____mutmut_5': xǁAPIKeyValidatorǁ__init____mutmut_5, 
        'xǁAPIKeyValidatorǁ__init____mutmut_6': xǁAPIKeyValidatorǁ__init____mutmut_6, 
        'xǁAPIKeyValidatorǁ__init____mutmut_7': xǁAPIKeyValidatorǁ__init____mutmut_7, 
        'xǁAPIKeyValidatorǁ__init____mutmut_8': xǁAPIKeyValidatorǁ__init____mutmut_8, 
        'xǁAPIKeyValidatorǁ__init____mutmut_9': xǁAPIKeyValidatorǁ__init____mutmut_9, 
        'xǁAPIKeyValidatorǁ__init____mutmut_10': xǁAPIKeyValidatorǁ__init____mutmut_10, 
        'xǁAPIKeyValidatorǁ__init____mutmut_11': xǁAPIKeyValidatorǁ__init____mutmut_11, 
        'xǁAPIKeyValidatorǁ__init____mutmut_12': xǁAPIKeyValidatorǁ__init____mutmut_12, 
        'xǁAPIKeyValidatorǁ__init____mutmut_13': xǁAPIKeyValidatorǁ__init____mutmut_13, 
        'xǁAPIKeyValidatorǁ__init____mutmut_14': xǁAPIKeyValidatorǁ__init____mutmut_14, 
        'xǁAPIKeyValidatorǁ__init____mutmut_15': xǁAPIKeyValidatorǁ__init____mutmut_15, 
        'xǁAPIKeyValidatorǁ__init____mutmut_16': xǁAPIKeyValidatorǁ__init____mutmut_16, 
        'xǁAPIKeyValidatorǁ__init____mutmut_17': xǁAPIKeyValidatorǁ__init____mutmut_17, 
        'xǁAPIKeyValidatorǁ__init____mutmut_18': xǁAPIKeyValidatorǁ__init____mutmut_18, 
        'xǁAPIKeyValidatorǁ__init____mutmut_19': xǁAPIKeyValidatorǁ__init____mutmut_19, 
        'xǁAPIKeyValidatorǁ__init____mutmut_20': xǁAPIKeyValidatorǁ__init____mutmut_20, 
        'xǁAPIKeyValidatorǁ__init____mutmut_21': xǁAPIKeyValidatorǁ__init____mutmut_21, 
        'xǁAPIKeyValidatorǁ__init____mutmut_22': xǁAPIKeyValidatorǁ__init____mutmut_22, 
        'xǁAPIKeyValidatorǁ__init____mutmut_23': xǁAPIKeyValidatorǁ__init____mutmut_23, 
        'xǁAPIKeyValidatorǁ__init____mutmut_24': xǁAPIKeyValidatorǁ__init____mutmut_24, 
        'xǁAPIKeyValidatorǁ__init____mutmut_25': xǁAPIKeyValidatorǁ__init____mutmut_25, 
        'xǁAPIKeyValidatorǁ__init____mutmut_26': xǁAPIKeyValidatorǁ__init____mutmut_26, 
        'xǁAPIKeyValidatorǁ__init____mutmut_27': xǁAPIKeyValidatorǁ__init____mutmut_27, 
        'xǁAPIKeyValidatorǁ__init____mutmut_28': xǁAPIKeyValidatorǁ__init____mutmut_28, 
        'xǁAPIKeyValidatorǁ__init____mutmut_29': xǁAPIKeyValidatorǁ__init____mutmut_29, 
        'xǁAPIKeyValidatorǁ__init____mutmut_30': xǁAPIKeyValidatorǁ__init____mutmut_30
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁ__init____mutmut_orig)
    xǁAPIKeyValidatorǁ__init____mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁ__init__'
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_orig(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_1(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = None
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_2(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            None,
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_3(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            None,
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_4(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            None,
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_5(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            self._secret_key.encode(),
            None,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_6(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_7(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_8(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_9(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            self._secret_key.encode(),
            )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_10(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "XXsha256XX",
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_11(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "SHA256",
            api_key.encode(),
            self._secret_key.encode(),
            100_000,
        )
        return derived_key.hex()
    
    def xǁAPIKeyValidatorǁ_compute_hmac__mutmut_12(self, api_key: str) -> str:
        """
        Compute a computationally expensive hash of an API key.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            PBKDF2-HMAC-SHA256 hash as hexadecimal string
        """
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode(),
            self._secret_key.encode(),
            100001,
        )
        return derived_key.hex()
    
    xǁAPIKeyValidatorǁ_compute_hmac__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_1': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_1, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_2': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_2, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_3': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_3, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_4': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_4, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_5': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_5, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_6': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_6, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_7': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_7, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_8': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_8, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_9': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_9, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_10': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_10, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_11': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_11, 
        'xǁAPIKeyValidatorǁ_compute_hmac__mutmut_12': xǁAPIKeyValidatorǁ_compute_hmac__mutmut_12
    }
    
    def _compute_hmac(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁ_compute_hmac__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁ_compute_hmac__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _compute_hmac.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁ_compute_hmac__mutmut_orig)
    xǁAPIKeyValidatorǁ_compute_hmac__mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁ_compute_hmac'
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_orig(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_1(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "XXdefaultXX") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_2(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "DEFAULT") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_3(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = None
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_4(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "XXuser_idXX": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_5(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "USER_ID": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_6(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "XXscopesXX": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_7(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "SCOPES": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_8(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(None),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_9(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes and []),
            "name": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_10(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "XXnameXX": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_11(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "NAME": name,
            "created_at": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_12(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "XXcreated_atXX": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_13(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "CREATED_AT": time.time(),
            "last_used": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_14(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "XXlast_usedXX": None,
        }
    
    def xǁAPIKeyValidatorǁregister_key__mutmut_15(self, key_hash: str, user_id: str, scopes: Optional[List[str]] = None,
                    name: str = "default") -> None:
        """
        Register an API key.
        
        Args:
            key_hash: Hashed API key (use hash_api_key() method to generate)
            user_id: Associated user ID
            scopes: Allowed scopes for this key
            name: Key name for identification
        """
        self._keys[key_hash] = {
            "user_id": user_id,
            "scopes": set(scopes or []),
            "name": name,
            "created_at": time.time(),
            "LAST_USED": None,
        }
    
    xǁAPIKeyValidatorǁregister_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁregister_key__mutmut_1': xǁAPIKeyValidatorǁregister_key__mutmut_1, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_2': xǁAPIKeyValidatorǁregister_key__mutmut_2, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_3': xǁAPIKeyValidatorǁregister_key__mutmut_3, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_4': xǁAPIKeyValidatorǁregister_key__mutmut_4, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_5': xǁAPIKeyValidatorǁregister_key__mutmut_5, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_6': xǁAPIKeyValidatorǁregister_key__mutmut_6, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_7': xǁAPIKeyValidatorǁregister_key__mutmut_7, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_8': xǁAPIKeyValidatorǁregister_key__mutmut_8, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_9': xǁAPIKeyValidatorǁregister_key__mutmut_9, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_10': xǁAPIKeyValidatorǁregister_key__mutmut_10, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_11': xǁAPIKeyValidatorǁregister_key__mutmut_11, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_12': xǁAPIKeyValidatorǁregister_key__mutmut_12, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_13': xǁAPIKeyValidatorǁregister_key__mutmut_13, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_14': xǁAPIKeyValidatorǁregister_key__mutmut_14, 
        'xǁAPIKeyValidatorǁregister_key__mutmut_15': xǁAPIKeyValidatorǁregister_key__mutmut_15
    }
    
    def register_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁregister_key__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁregister_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    register_key.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁregister_key__mutmut_orig)
    xǁAPIKeyValidatorǁregister_key__mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁregister_key'
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_orig(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_1(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = None
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_2(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(None)
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_3(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash not in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_4(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash in self._keys:
            key_info = None
            key_info["last_used"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_5(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["last_used"] = None
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_6(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["XXlast_usedXX"] = time.time()
            return key_info
        
        return None
    
    def xǁAPIKeyValidatorǁvalidate_key__mutmut_7(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key using secure HMAC-SHA256 hashing.
        
        Args:
            api_key: The API key to validate
        
        Returns:
            Key info dict if valid, None otherwise
        """
        key_hash = self._compute_hmac(api_key)
        
        if key_hash in self._keys:
            key_info = self._keys[key_hash]
            key_info["LAST_USED"] = time.time()
            return key_info
        
        return None
    
    xǁAPIKeyValidatorǁvalidate_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁvalidate_key__mutmut_1': xǁAPIKeyValidatorǁvalidate_key__mutmut_1, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_2': xǁAPIKeyValidatorǁvalidate_key__mutmut_2, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_3': xǁAPIKeyValidatorǁvalidate_key__mutmut_3, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_4': xǁAPIKeyValidatorǁvalidate_key__mutmut_4, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_5': xǁAPIKeyValidatorǁvalidate_key__mutmut_5, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_6': xǁAPIKeyValidatorǁvalidate_key__mutmut_6, 
        'xǁAPIKeyValidatorǁvalidate_key__mutmut_7': xǁAPIKeyValidatorǁvalidate_key__mutmut_7
    }
    
    def validate_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁvalidate_key__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁvalidate_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate_key.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁvalidate_key__mutmut_orig)
    xǁAPIKeyValidatorǁvalidate_key__mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁvalidate_key'
    
    def xǁAPIKeyValidatorǁhash_api_key__mutmut_orig(self, api_key: str) -> str:
        """
        Hash an API key using HMAC-SHA256.
        
        Use this method when registering API keys to get the secure hash.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            HMAC-SHA256 hash of the API key
        """
        return self._compute_hmac(api_key)
    
    def xǁAPIKeyValidatorǁhash_api_key__mutmut_1(self, api_key: str) -> str:
        """
        Hash an API key using HMAC-SHA256.
        
        Use this method when registering API keys to get the secure hash.
        
        Args:
            api_key: The API key to hash
        
        Returns:
            HMAC-SHA256 hash of the API key
        """
        return self._compute_hmac(None)
    
    xǁAPIKeyValidatorǁhash_api_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁhash_api_key__mutmut_1': xǁAPIKeyValidatorǁhash_api_key__mutmut_1
    }
    
    def hash_api_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁhash_api_key__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁhash_api_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    hash_api_key.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁhash_api_key__mutmut_orig)
    xǁAPIKeyValidatorǁhash_api_key__mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁhash_api_key'
    
    def xǁAPIKeyValidatorǁrevoke_key__mutmut_orig(self, key_hash: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_hash: Hash of the key to revoke
        
        Returns:
            True if key was revoked
        """
        if key_hash in self._keys:
            del self._keys[key_hash]
            return True
        return False
    
    def xǁAPIKeyValidatorǁrevoke_key__mutmut_1(self, key_hash: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_hash: Hash of the key to revoke
        
        Returns:
            True if key was revoked
        """
        if key_hash not in self._keys:
            del self._keys[key_hash]
            return True
        return False
    
    def xǁAPIKeyValidatorǁrevoke_key__mutmut_2(self, key_hash: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_hash: Hash of the key to revoke
        
        Returns:
            True if key was revoked
        """
        if key_hash in self._keys:
            del self._keys[key_hash]
            return False
        return False
    
    def xǁAPIKeyValidatorǁrevoke_key__mutmut_3(self, key_hash: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_hash: Hash of the key to revoke
        
        Returns:
            True if key was revoked
        """
        if key_hash in self._keys:
            del self._keys[key_hash]
            return True
        return True
    
    xǁAPIKeyValidatorǁrevoke_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyValidatorǁrevoke_key__mutmut_1': xǁAPIKeyValidatorǁrevoke_key__mutmut_1, 
        'xǁAPIKeyValidatorǁrevoke_key__mutmut_2': xǁAPIKeyValidatorǁrevoke_key__mutmut_2, 
        'xǁAPIKeyValidatorǁrevoke_key__mutmut_3': xǁAPIKeyValidatorǁrevoke_key__mutmut_3
    }
    
    def revoke_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyValidatorǁrevoke_key__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyValidatorǁrevoke_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    revoke_key.__signature__ = _mutmut_signature(xǁAPIKeyValidatorǁrevoke_key__mutmut_orig)
    xǁAPIKeyValidatorǁrevoke_key__mutmut_orig.__name__ = 'xǁAPIKeyValidatorǁrevoke_key'


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def xǁRateLimiterǁ__init____mutmut_orig(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds
        self._counters: Dict[str, List[float]] = {}
    
    def xǁRateLimiterǁ__init____mutmut_1(self, requests_per_window: int = 101, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds
        self._counters: Dict[str, List[float]] = {}
    
    def xǁRateLimiterǁ__init____mutmut_2(self, requests_per_window: int = 100, window_seconds: int = 61):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds
        self._counters: Dict[str, List[float]] = {}
    
    def xǁRateLimiterǁ__init____mutmut_3(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = None
        self._window_seconds = window_seconds
        self._counters: Dict[str, List[float]] = {}
    
    def xǁRateLimiterǁ__init____mutmut_4(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = None
        self._counters: Dict[str, List[float]] = {}
    
    def xǁRateLimiterǁ__init____mutmut_5(self, requests_per_window: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self._requests_per_window = requests_per_window
        self._window_seconds = window_seconds
        self._counters: Dict[str, List[float]] = None
    
    xǁRateLimiterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimiterǁ__init____mutmut_1': xǁRateLimiterǁ__init____mutmut_1, 
        'xǁRateLimiterǁ__init____mutmut_2': xǁRateLimiterǁ__init____mutmut_2, 
        'xǁRateLimiterǁ__init____mutmut_3': xǁRateLimiterǁ__init____mutmut_3, 
        'xǁRateLimiterǁ__init____mutmut_4': xǁRateLimiterǁ__init____mutmut_4, 
        'xǁRateLimiterǁ__init____mutmut_5': xǁRateLimiterǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimiterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRateLimiterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRateLimiterǁ__init____mutmut_orig)
    xǁRateLimiterǁ__init____mutmut_orig.__name__ = 'xǁRateLimiterǁ__init__'
    
    def xǁRateLimiterǁis_allowed__mutmut_orig(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_1(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = None
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_2(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = None
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_3(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now + self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_4(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_5(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = None
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_6(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = None
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_7(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t >= window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_8(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) > self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_9(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return True
        
        # Record request
        self._counters[key].append(now)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_10(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(None)
        return True
    
    def xǁRateLimiterǁis_allowed__mutmut_11(self, key: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., user ID or IP)
        
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            self._counters[key] = []
        
        # Remove old entries
        self._counters[key] = [t for t in self._counters[key] if t > window_start]
        
        # Check limit
        if len(self._counters[key]) >= self._requests_per_window:
            return False
        
        # Record request
        self._counters[key].append(now)
        return False
    
    xǁRateLimiterǁis_allowed__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimiterǁis_allowed__mutmut_1': xǁRateLimiterǁis_allowed__mutmut_1, 
        'xǁRateLimiterǁis_allowed__mutmut_2': xǁRateLimiterǁis_allowed__mutmut_2, 
        'xǁRateLimiterǁis_allowed__mutmut_3': xǁRateLimiterǁis_allowed__mutmut_3, 
        'xǁRateLimiterǁis_allowed__mutmut_4': xǁRateLimiterǁis_allowed__mutmut_4, 
        'xǁRateLimiterǁis_allowed__mutmut_5': xǁRateLimiterǁis_allowed__mutmut_5, 
        'xǁRateLimiterǁis_allowed__mutmut_6': xǁRateLimiterǁis_allowed__mutmut_6, 
        'xǁRateLimiterǁis_allowed__mutmut_7': xǁRateLimiterǁis_allowed__mutmut_7, 
        'xǁRateLimiterǁis_allowed__mutmut_8': xǁRateLimiterǁis_allowed__mutmut_8, 
        'xǁRateLimiterǁis_allowed__mutmut_9': xǁRateLimiterǁis_allowed__mutmut_9, 
        'xǁRateLimiterǁis_allowed__mutmut_10': xǁRateLimiterǁis_allowed__mutmut_10, 
        'xǁRateLimiterǁis_allowed__mutmut_11': xǁRateLimiterǁis_allowed__mutmut_11
    }
    
    def is_allowed(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimiterǁis_allowed__mutmut_orig"), object.__getattribute__(self, "xǁRateLimiterǁis_allowed__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_allowed.__signature__ = _mutmut_signature(xǁRateLimiterǁis_allowed__mutmut_orig)
    xǁRateLimiterǁis_allowed__mutmut_orig.__name__ = 'xǁRateLimiterǁis_allowed'
    
    def xǁRateLimiterǁget_remaining__mutmut_orig(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_1(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = None
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_2(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = None
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_3(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now + self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_4(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_5(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = None
        return max(0, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_6(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(None, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_7(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, None)
    
    def xǁRateLimiterǁget_remaining__mutmut_8(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_9(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, )
    
    def xǁRateLimiterǁget_remaining__mutmut_10(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(1, self._requests_per_window - current_count)
    
    def xǁRateLimiterǁget_remaining__mutmut_11(self, key: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self._window_seconds
        
        if key not in self._counters:
            return self._requests_per_window
        
        # Count requests in window
        current_count = len([t for t in self._counters[key] if t > window_start])
        return max(0, self._requests_per_window + current_count)
    
    xǁRateLimiterǁget_remaining__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimiterǁget_remaining__mutmut_1': xǁRateLimiterǁget_remaining__mutmut_1, 
        'xǁRateLimiterǁget_remaining__mutmut_2': xǁRateLimiterǁget_remaining__mutmut_2, 
        'xǁRateLimiterǁget_remaining__mutmut_3': xǁRateLimiterǁget_remaining__mutmut_3, 
        'xǁRateLimiterǁget_remaining__mutmut_4': xǁRateLimiterǁget_remaining__mutmut_4, 
        'xǁRateLimiterǁget_remaining__mutmut_5': xǁRateLimiterǁget_remaining__mutmut_5, 
        'xǁRateLimiterǁget_remaining__mutmut_6': xǁRateLimiterǁget_remaining__mutmut_6, 
        'xǁRateLimiterǁget_remaining__mutmut_7': xǁRateLimiterǁget_remaining__mutmut_7, 
        'xǁRateLimiterǁget_remaining__mutmut_8': xǁRateLimiterǁget_remaining__mutmut_8, 
        'xǁRateLimiterǁget_remaining__mutmut_9': xǁRateLimiterǁget_remaining__mutmut_9, 
        'xǁRateLimiterǁget_remaining__mutmut_10': xǁRateLimiterǁget_remaining__mutmut_10, 
        'xǁRateLimiterǁget_remaining__mutmut_11': xǁRateLimiterǁget_remaining__mutmut_11
    }
    
    def get_remaining(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimiterǁget_remaining__mutmut_orig"), object.__getattribute__(self, "xǁRateLimiterǁget_remaining__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_remaining.__signature__ = _mutmut_signature(xǁRateLimiterǁget_remaining__mutmut_orig)
    xǁRateLimiterǁget_remaining__mutmut_orig.__name__ = 'xǁRateLimiterǁget_remaining'
    
    def xǁRateLimiterǁcleanup__mutmut_orig(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_1(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = None
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_2(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = None
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_3(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now + self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_4(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = None
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_5(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 1
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_6(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(None):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_7(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = None
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_8(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t >= window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_9(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if self._counters[key]:
                del self._counters[key]
                cleaned += 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_10(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned = 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_11(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned -= 1
        
        return cleaned
    
    def xǁRateLimiterǁcleanup__mutmut_12(self) -> int:
        """
        Clean up old entries.
        
        Returns:
            Number of keys cleaned up
        """
        now = time.time()
        window_start = now - self._window_seconds
        cleaned = 0
        
        for key in list(self._counters.keys()):
            self._counters[key] = [t for t in self._counters[key] if t > window_start]
            if not self._counters[key]:
                del self._counters[key]
                cleaned += 2
        
        return cleaned
    
    xǁRateLimiterǁcleanup__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimiterǁcleanup__mutmut_1': xǁRateLimiterǁcleanup__mutmut_1, 
        'xǁRateLimiterǁcleanup__mutmut_2': xǁRateLimiterǁcleanup__mutmut_2, 
        'xǁRateLimiterǁcleanup__mutmut_3': xǁRateLimiterǁcleanup__mutmut_3, 
        'xǁRateLimiterǁcleanup__mutmut_4': xǁRateLimiterǁcleanup__mutmut_4, 
        'xǁRateLimiterǁcleanup__mutmut_5': xǁRateLimiterǁcleanup__mutmut_5, 
        'xǁRateLimiterǁcleanup__mutmut_6': xǁRateLimiterǁcleanup__mutmut_6, 
        'xǁRateLimiterǁcleanup__mutmut_7': xǁRateLimiterǁcleanup__mutmut_7, 
        'xǁRateLimiterǁcleanup__mutmut_8': xǁRateLimiterǁcleanup__mutmut_8, 
        'xǁRateLimiterǁcleanup__mutmut_9': xǁRateLimiterǁcleanup__mutmut_9, 
        'xǁRateLimiterǁcleanup__mutmut_10': xǁRateLimiterǁcleanup__mutmut_10, 
        'xǁRateLimiterǁcleanup__mutmut_11': xǁRateLimiterǁcleanup__mutmut_11, 
        'xǁRateLimiterǁcleanup__mutmut_12': xǁRateLimiterǁcleanup__mutmut_12
    }
    
    def cleanup(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimiterǁcleanup__mutmut_orig"), object.__getattribute__(self, "xǁRateLimiterǁcleanup__mutmut_mutants"), args, kwargs, self)
        return result 
    
    cleanup.__signature__ = _mutmut_signature(xǁRateLimiterǁcleanup__mutmut_orig)
    xǁRateLimiterǁcleanup__mutmut_orig.__name__ = 'xǁRateLimiterǁcleanup'


class AuthMiddleware:
    """
    Production authentication middleware.
    
    Integrates with FastAPI/Starlette to provide request authentication.
    Supports JWT tokens, API keys, and OAuth tokens.
    
    Example:
        app = FastAPI()
        token_manager = TokenManager(secret_key="your-secret")
        app.add_middleware(AuthMiddleware, token_manager=token_manager)
    """
    
    def xǁAuthMiddlewareǁ__init____mutmut_orig(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_1(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = None
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_2(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = None
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_3(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = None
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_4(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config and AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_5(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = None
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_6(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator and APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_7(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = None
    
    def xǁAuthMiddlewareǁ__init____mutmut_8(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            None,
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_9(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            None
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_10(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_window
        )
    
    def xǁAuthMiddlewareǁ__init____mutmut_11(self, app, token_manager: TokenManager, config: Optional[AuthConfig] = None,
                 api_key_validator: Optional[APIKeyValidator] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: ASGI application
            token_manager: Token manager for JWT validation
            config: Authentication configuration
            api_key_validator: Optional API key validator
        """
        self.app = app
        self.token_manager = token_manager
        self.config = config or AuthConfig()
        self.api_key_validator = api_key_validator or APIKeyValidator()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            )
    
    xǁAuthMiddlewareǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ__init____mutmut_1': xǁAuthMiddlewareǁ__init____mutmut_1, 
        'xǁAuthMiddlewareǁ__init____mutmut_2': xǁAuthMiddlewareǁ__init____mutmut_2, 
        'xǁAuthMiddlewareǁ__init____mutmut_3': xǁAuthMiddlewareǁ__init____mutmut_3, 
        'xǁAuthMiddlewareǁ__init____mutmut_4': xǁAuthMiddlewareǁ__init____mutmut_4, 
        'xǁAuthMiddlewareǁ__init____mutmut_5': xǁAuthMiddlewareǁ__init____mutmut_5, 
        'xǁAuthMiddlewareǁ__init____mutmut_6': xǁAuthMiddlewareǁ__init____mutmut_6, 
        'xǁAuthMiddlewareǁ__init____mutmut_7': xǁAuthMiddlewareǁ__init____mutmut_7, 
        'xǁAuthMiddlewareǁ__init____mutmut_8': xǁAuthMiddlewareǁ__init____mutmut_8, 
        'xǁAuthMiddlewareǁ__init____mutmut_9': xǁAuthMiddlewareǁ__init____mutmut_9, 
        'xǁAuthMiddlewareǁ__init____mutmut_10': xǁAuthMiddlewareǁ__init____mutmut_10, 
        'xǁAuthMiddlewareǁ__init____mutmut_11': xǁAuthMiddlewareǁ__init____mutmut_11
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ__init____mutmut_orig)
    xǁAuthMiddlewareǁ__init____mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ__init__'
    
    async def xǁAuthMiddlewareǁ__call____mutmut_orig(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_1(self, scope, receive, send):
        """ASGI interface."""
        if scope["XXtypeXX"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_2(self, scope, receive, send):
        """ASGI interface."""
        if scope["TYPE"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_3(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] == "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_4(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "XXhttpXX":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_5(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "HTTP":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_6(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(None, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_7(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, None, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_8(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, None)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_9(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_10(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_11(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, )
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_12(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = None
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_13(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get(None, "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_14(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", None)
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_15(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_16(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", )
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_17(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("XXpathXX", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_18(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("PATH", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_19(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "XXXX")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_20(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path not in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_21(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(None, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_22(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, None, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_23(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, None)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_24(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_25(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_26(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, )
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_27(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_28(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(None, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_29(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, None, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_30(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, None)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_31(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_32(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_33(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, )
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_34(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = None
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_35(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(None)
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_36(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get(None, []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_37(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", None))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_38(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get([]))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_39(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", ))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_40(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("XXheadersXX", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_41(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("HEADERS", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_42(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = None
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_43(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(None)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_44(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = None
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_45(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["XXauthXX"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_46(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["AUTH"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_47(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_48(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(None, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_49(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, None)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_50(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_51(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, )
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_52(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = None
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_53(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id and scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_54(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get(None, ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_55(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", None)[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_56(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get(["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_57(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", )[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_58(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("XXclientXX", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_59(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("CLIENT", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_60(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["XXunknownXX"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_61(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["UNKNOWN"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_62(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[1]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_63(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_64(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(None):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_65(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(None)
            return
        
        # Continue to app
        await self.app(scope, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_66(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(None, receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_67(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, None, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_68(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, None)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_69(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(receive, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_70(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, send)
    
    async def xǁAuthMiddlewareǁ__call____mutmut_71(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path is exempt
        path = scope.get("path", "")
        if path in self.config.exempt_paths:
            await self.app(scope, receive, send)
            return
        
        if not self.config.enabled:
            await self.app(scope, receive, send)
            return
        
        # Extract headers
        headers = dict(scope.get("headers", []))
        
        # Authenticate request
        auth_result = self._authenticate(headers)
        
        # Store auth result in scope
        scope["auth"] = auth_result
        
        if not auth_result.authenticated:
            # Return 401 Unauthorized
            await self._send_unauthorized(send, auth_result.error)
            return
        
        # Check rate limit
        rate_key = auth_result.user_id or scope.get("client", ["unknown"])[0]
        if not self.rate_limiter.is_allowed(rate_key):
            await self._send_rate_limited(send)
            return
        
        # Continue to app
        await self.app(scope, receive, )
    
    xǁAuthMiddlewareǁ__call____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ__call____mutmut_1': xǁAuthMiddlewareǁ__call____mutmut_1, 
        'xǁAuthMiddlewareǁ__call____mutmut_2': xǁAuthMiddlewareǁ__call____mutmut_2, 
        'xǁAuthMiddlewareǁ__call____mutmut_3': xǁAuthMiddlewareǁ__call____mutmut_3, 
        'xǁAuthMiddlewareǁ__call____mutmut_4': xǁAuthMiddlewareǁ__call____mutmut_4, 
        'xǁAuthMiddlewareǁ__call____mutmut_5': xǁAuthMiddlewareǁ__call____mutmut_5, 
        'xǁAuthMiddlewareǁ__call____mutmut_6': xǁAuthMiddlewareǁ__call____mutmut_6, 
        'xǁAuthMiddlewareǁ__call____mutmut_7': xǁAuthMiddlewareǁ__call____mutmut_7, 
        'xǁAuthMiddlewareǁ__call____mutmut_8': xǁAuthMiddlewareǁ__call____mutmut_8, 
        'xǁAuthMiddlewareǁ__call____mutmut_9': xǁAuthMiddlewareǁ__call____mutmut_9, 
        'xǁAuthMiddlewareǁ__call____mutmut_10': xǁAuthMiddlewareǁ__call____mutmut_10, 
        'xǁAuthMiddlewareǁ__call____mutmut_11': xǁAuthMiddlewareǁ__call____mutmut_11, 
        'xǁAuthMiddlewareǁ__call____mutmut_12': xǁAuthMiddlewareǁ__call____mutmut_12, 
        'xǁAuthMiddlewareǁ__call____mutmut_13': xǁAuthMiddlewareǁ__call____mutmut_13, 
        'xǁAuthMiddlewareǁ__call____mutmut_14': xǁAuthMiddlewareǁ__call____mutmut_14, 
        'xǁAuthMiddlewareǁ__call____mutmut_15': xǁAuthMiddlewareǁ__call____mutmut_15, 
        'xǁAuthMiddlewareǁ__call____mutmut_16': xǁAuthMiddlewareǁ__call____mutmut_16, 
        'xǁAuthMiddlewareǁ__call____mutmut_17': xǁAuthMiddlewareǁ__call____mutmut_17, 
        'xǁAuthMiddlewareǁ__call____mutmut_18': xǁAuthMiddlewareǁ__call____mutmut_18, 
        'xǁAuthMiddlewareǁ__call____mutmut_19': xǁAuthMiddlewareǁ__call____mutmut_19, 
        'xǁAuthMiddlewareǁ__call____mutmut_20': xǁAuthMiddlewareǁ__call____mutmut_20, 
        'xǁAuthMiddlewareǁ__call____mutmut_21': xǁAuthMiddlewareǁ__call____mutmut_21, 
        'xǁAuthMiddlewareǁ__call____mutmut_22': xǁAuthMiddlewareǁ__call____mutmut_22, 
        'xǁAuthMiddlewareǁ__call____mutmut_23': xǁAuthMiddlewareǁ__call____mutmut_23, 
        'xǁAuthMiddlewareǁ__call____mutmut_24': xǁAuthMiddlewareǁ__call____mutmut_24, 
        'xǁAuthMiddlewareǁ__call____mutmut_25': xǁAuthMiddlewareǁ__call____mutmut_25, 
        'xǁAuthMiddlewareǁ__call____mutmut_26': xǁAuthMiddlewareǁ__call____mutmut_26, 
        'xǁAuthMiddlewareǁ__call____mutmut_27': xǁAuthMiddlewareǁ__call____mutmut_27, 
        'xǁAuthMiddlewareǁ__call____mutmut_28': xǁAuthMiddlewareǁ__call____mutmut_28, 
        'xǁAuthMiddlewareǁ__call____mutmut_29': xǁAuthMiddlewareǁ__call____mutmut_29, 
        'xǁAuthMiddlewareǁ__call____mutmut_30': xǁAuthMiddlewareǁ__call____mutmut_30, 
        'xǁAuthMiddlewareǁ__call____mutmut_31': xǁAuthMiddlewareǁ__call____mutmut_31, 
        'xǁAuthMiddlewareǁ__call____mutmut_32': xǁAuthMiddlewareǁ__call____mutmut_32, 
        'xǁAuthMiddlewareǁ__call____mutmut_33': xǁAuthMiddlewareǁ__call____mutmut_33, 
        'xǁAuthMiddlewareǁ__call____mutmut_34': xǁAuthMiddlewareǁ__call____mutmut_34, 
        'xǁAuthMiddlewareǁ__call____mutmut_35': xǁAuthMiddlewareǁ__call____mutmut_35, 
        'xǁAuthMiddlewareǁ__call____mutmut_36': xǁAuthMiddlewareǁ__call____mutmut_36, 
        'xǁAuthMiddlewareǁ__call____mutmut_37': xǁAuthMiddlewareǁ__call____mutmut_37, 
        'xǁAuthMiddlewareǁ__call____mutmut_38': xǁAuthMiddlewareǁ__call____mutmut_38, 
        'xǁAuthMiddlewareǁ__call____mutmut_39': xǁAuthMiddlewareǁ__call____mutmut_39, 
        'xǁAuthMiddlewareǁ__call____mutmut_40': xǁAuthMiddlewareǁ__call____mutmut_40, 
        'xǁAuthMiddlewareǁ__call____mutmut_41': xǁAuthMiddlewareǁ__call____mutmut_41, 
        'xǁAuthMiddlewareǁ__call____mutmut_42': xǁAuthMiddlewareǁ__call____mutmut_42, 
        'xǁAuthMiddlewareǁ__call____mutmut_43': xǁAuthMiddlewareǁ__call____mutmut_43, 
        'xǁAuthMiddlewareǁ__call____mutmut_44': xǁAuthMiddlewareǁ__call____mutmut_44, 
        'xǁAuthMiddlewareǁ__call____mutmut_45': xǁAuthMiddlewareǁ__call____mutmut_45, 
        'xǁAuthMiddlewareǁ__call____mutmut_46': xǁAuthMiddlewareǁ__call____mutmut_46, 
        'xǁAuthMiddlewareǁ__call____mutmut_47': xǁAuthMiddlewareǁ__call____mutmut_47, 
        'xǁAuthMiddlewareǁ__call____mutmut_48': xǁAuthMiddlewareǁ__call____mutmut_48, 
        'xǁAuthMiddlewareǁ__call____mutmut_49': xǁAuthMiddlewareǁ__call____mutmut_49, 
        'xǁAuthMiddlewareǁ__call____mutmut_50': xǁAuthMiddlewareǁ__call____mutmut_50, 
        'xǁAuthMiddlewareǁ__call____mutmut_51': xǁAuthMiddlewareǁ__call____mutmut_51, 
        'xǁAuthMiddlewareǁ__call____mutmut_52': xǁAuthMiddlewareǁ__call____mutmut_52, 
        'xǁAuthMiddlewareǁ__call____mutmut_53': xǁAuthMiddlewareǁ__call____mutmut_53, 
        'xǁAuthMiddlewareǁ__call____mutmut_54': xǁAuthMiddlewareǁ__call____mutmut_54, 
        'xǁAuthMiddlewareǁ__call____mutmut_55': xǁAuthMiddlewareǁ__call____mutmut_55, 
        'xǁAuthMiddlewareǁ__call____mutmut_56': xǁAuthMiddlewareǁ__call____mutmut_56, 
        'xǁAuthMiddlewareǁ__call____mutmut_57': xǁAuthMiddlewareǁ__call____mutmut_57, 
        'xǁAuthMiddlewareǁ__call____mutmut_58': xǁAuthMiddlewareǁ__call____mutmut_58, 
        'xǁAuthMiddlewareǁ__call____mutmut_59': xǁAuthMiddlewareǁ__call____mutmut_59, 
        'xǁAuthMiddlewareǁ__call____mutmut_60': xǁAuthMiddlewareǁ__call____mutmut_60, 
        'xǁAuthMiddlewareǁ__call____mutmut_61': xǁAuthMiddlewareǁ__call____mutmut_61, 
        'xǁAuthMiddlewareǁ__call____mutmut_62': xǁAuthMiddlewareǁ__call____mutmut_62, 
        'xǁAuthMiddlewareǁ__call____mutmut_63': xǁAuthMiddlewareǁ__call____mutmut_63, 
        'xǁAuthMiddlewareǁ__call____mutmut_64': xǁAuthMiddlewareǁ__call____mutmut_64, 
        'xǁAuthMiddlewareǁ__call____mutmut_65': xǁAuthMiddlewareǁ__call____mutmut_65, 
        'xǁAuthMiddlewareǁ__call____mutmut_66': xǁAuthMiddlewareǁ__call____mutmut_66, 
        'xǁAuthMiddlewareǁ__call____mutmut_67': xǁAuthMiddlewareǁ__call____mutmut_67, 
        'xǁAuthMiddlewareǁ__call____mutmut_68': xǁAuthMiddlewareǁ__call____mutmut_68, 
        'xǁAuthMiddlewareǁ__call____mutmut_69': xǁAuthMiddlewareǁ__call____mutmut_69, 
        'xǁAuthMiddlewareǁ__call____mutmut_70': xǁAuthMiddlewareǁ__call____mutmut_70, 
        'xǁAuthMiddlewareǁ__call____mutmut_71': xǁAuthMiddlewareǁ__call____mutmut_71
    }
    
    def __call__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ__call____mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ__call____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __call__.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ__call____mutmut_orig)
    xǁAuthMiddlewareǁ__call____mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ__call__'
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_orig(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_1(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = None
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_2(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(None, b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_3(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", None).decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_4(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_5(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", ).decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_6(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"XXauthorizationXX", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_7(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"AUTHORIZATION", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_8(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"XXXX").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_9(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith(None):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_10(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("XXBearer XX"):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_11(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_12(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("BEARER "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_13(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(None)
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_14(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[8:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_15(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = None
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_16(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.upper().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_17(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = None
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_18(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(None, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_19(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, None).decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_20(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_21(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, ).decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_22(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"XXXX").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_23(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(None)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_24(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=None,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_25(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=None,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_26(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error=None
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_27(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_28(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_29(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_30(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=True,
            method=AuthMethod.NONE,
            error="No authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_31(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="XXNo authentication credentials providedXX"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_32(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="no authentication credentials provided"
        )
    
    def xǁAuthMiddlewareǁ_authenticate__mutmut_33(self, headers: Dict[bytes, bytes]) -> AuthResult:
        """
        Authenticate request from headers.
        
        Args:
            headers: Request headers
        
        Returns:
            AuthResult with authentication status
        """
        # Try Bearer token (JWT)
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            return self._authenticate_jwt(auth_header[7:])
        
        # Try API key
        api_key_header = self.config.api_key_header.lower().encode()
        api_key = headers.get(api_key_header, b"").decode()
        if api_key:
            return self._authenticate_api_key(api_key)
        
        # No authentication provided
        return AuthResult(
            authenticated=False,
            method=AuthMethod.NONE,
            error="NO AUTHENTICATION CREDENTIALS PROVIDED"
        )
    
    xǁAuthMiddlewareǁ_authenticate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ_authenticate__mutmut_1': xǁAuthMiddlewareǁ_authenticate__mutmut_1, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_2': xǁAuthMiddlewareǁ_authenticate__mutmut_2, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_3': xǁAuthMiddlewareǁ_authenticate__mutmut_3, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_4': xǁAuthMiddlewareǁ_authenticate__mutmut_4, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_5': xǁAuthMiddlewareǁ_authenticate__mutmut_5, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_6': xǁAuthMiddlewareǁ_authenticate__mutmut_6, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_7': xǁAuthMiddlewareǁ_authenticate__mutmut_7, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_8': xǁAuthMiddlewareǁ_authenticate__mutmut_8, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_9': xǁAuthMiddlewareǁ_authenticate__mutmut_9, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_10': xǁAuthMiddlewareǁ_authenticate__mutmut_10, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_11': xǁAuthMiddlewareǁ_authenticate__mutmut_11, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_12': xǁAuthMiddlewareǁ_authenticate__mutmut_12, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_13': xǁAuthMiddlewareǁ_authenticate__mutmut_13, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_14': xǁAuthMiddlewareǁ_authenticate__mutmut_14, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_15': xǁAuthMiddlewareǁ_authenticate__mutmut_15, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_16': xǁAuthMiddlewareǁ_authenticate__mutmut_16, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_17': xǁAuthMiddlewareǁ_authenticate__mutmut_17, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_18': xǁAuthMiddlewareǁ_authenticate__mutmut_18, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_19': xǁAuthMiddlewareǁ_authenticate__mutmut_19, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_20': xǁAuthMiddlewareǁ_authenticate__mutmut_20, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_21': xǁAuthMiddlewareǁ_authenticate__mutmut_21, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_22': xǁAuthMiddlewareǁ_authenticate__mutmut_22, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_23': xǁAuthMiddlewareǁ_authenticate__mutmut_23, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_24': xǁAuthMiddlewareǁ_authenticate__mutmut_24, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_25': xǁAuthMiddlewareǁ_authenticate__mutmut_25, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_26': xǁAuthMiddlewareǁ_authenticate__mutmut_26, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_27': xǁAuthMiddlewareǁ_authenticate__mutmut_27, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_28': xǁAuthMiddlewareǁ_authenticate__mutmut_28, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_29': xǁAuthMiddlewareǁ_authenticate__mutmut_29, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_30': xǁAuthMiddlewareǁ_authenticate__mutmut_30, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_31': xǁAuthMiddlewareǁ_authenticate__mutmut_31, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_32': xǁAuthMiddlewareǁ_authenticate__mutmut_32, 
        'xǁAuthMiddlewareǁ_authenticate__mutmut_33': xǁAuthMiddlewareǁ_authenticate__mutmut_33
    }
    
    def _authenticate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate__mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _authenticate.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ_authenticate__mutmut_orig)
    xǁAuthMiddlewareǁ_authenticate__mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ_authenticate'
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_orig(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_1(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = None
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_2(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(None)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_3(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = None
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_4(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(None)
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_5(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=None,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_6(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=None,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_7(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=None,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_8(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=None,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_9(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=None,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_10(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_11(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_12(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_13(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_14(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_15(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_16(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = None
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_17(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(None)
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_18(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(None))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_19(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(None)
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_20(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=None,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_21(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=None,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_22(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                error=None
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_23(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_24(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                error=f"Invalid token: {error_msg}"
            )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_25(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=False,
                method=AuthMethod.JWT,
                )
    
    def xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_26(self, token: str) -> AuthResult:
        """Authenticate using JWT token."""
        try:
            claims = self.token_manager.validate_token(token)
            scopes = set(claims.scope.split() if claims.scope else [])
            
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                user_id=claims.sub,
                claims=claims,
                scopes=scopes,
            )
        except ValueError as e:
            error_msg = sanitize_log_message(str(e))
            logger.warning(f"JWT authentication failed: {error_msg}")
            return AuthResult(
                authenticated=True,
                method=AuthMethod.JWT,
                error=f"Invalid token: {error_msg}"
            )
    
    xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_1': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_1, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_2': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_2, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_3': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_3, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_4': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_4, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_5': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_5, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_6': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_6, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_7': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_7, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_8': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_8, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_9': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_9, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_10': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_10, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_11': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_11, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_12': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_12, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_13': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_13, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_14': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_14, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_15': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_15, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_16': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_16, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_17': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_17, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_18': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_18, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_19': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_19, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_20': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_20, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_21': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_21, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_22': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_22, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_23': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_23, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_24': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_24, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_25': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_25, 
        'xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_26': xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_26
    }
    
    def _authenticate_jwt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _authenticate_jwt.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_orig)
    xǁAuthMiddlewareǁ_authenticate_jwt__mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ_authenticate_jwt'
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_orig(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_1(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = None
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_2(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(None)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_3(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=None,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_4(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=None,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_5(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=None,
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_6(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=None,
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_7(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_8(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_9(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_10(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_11(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=False,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_12(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["XXuser_idXX"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_13(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["USER_ID"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_14(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["XXscopesXX"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_15(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["SCOPES"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_16(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning(None)
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_17(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("XXAPI key authentication failed: Invalid keyXX")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_18(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("api key authentication failed: invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_19(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API KEY AUTHENTICATION FAILED: INVALID KEY")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_20(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=None,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_21(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=None,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_22(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error=None
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_23(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_24(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_25(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_26(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=True,
            method=AuthMethod.API_KEY,
            error="Invalid API key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_27(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="XXInvalid API keyXX"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_28(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="invalid api key"
        )
    
    def xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_29(self, api_key: str) -> AuthResult:
        """Authenticate using API key."""
        key_info = self.api_key_validator.validate_key(api_key)
        
        if key_info:
            return AuthResult(
                authenticated=True,
                method=AuthMethod.API_KEY,
                user_id=key_info["user_id"],
                scopes=key_info["scopes"],
            )
        
        logger.warning("API key authentication failed: Invalid key")
        return AuthResult(
            authenticated=False,
            method=AuthMethod.API_KEY,
            error="INVALID API KEY"
        )
    
    xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_1': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_1, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_2': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_2, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_3': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_3, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_4': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_4, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_5': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_5, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_6': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_6, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_7': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_7, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_8': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_8, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_9': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_9, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_10': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_10, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_11': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_11, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_12': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_12, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_13': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_13, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_14': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_14, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_15': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_15, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_16': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_16, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_17': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_17, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_18': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_18, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_19': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_19, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_20': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_20, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_21': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_21, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_22': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_22, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_23': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_23, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_24': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_24, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_25': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_25, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_26': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_26, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_27': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_27, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_28': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_28, 
        'xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_29': xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_29
    }
    
    def _authenticate_api_key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _authenticate_api_key.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_orig)
    xǁAuthMiddlewareǁ_authenticate_api_key__mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ_authenticate_api_key'
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_orig(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_1(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = None
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_2(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps(None).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_3(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "XXerrorXX": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_4(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "ERROR": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_5(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "XXUnauthorizedXX",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_6(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_7(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "UNAUTHORIZED",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_8(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "XXdetailXX": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_9(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "DETAIL": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_10(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error and "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_11(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "XXAuthentication requiredXX"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_12(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_13(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "AUTHENTICATION REQUIRED"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_14(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send(None)
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_15(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "XXtypeXX": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_16(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "TYPE": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_17(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "XXhttp.response.startXX",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_18(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "HTTP.RESPONSE.START",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_19(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "XXstatusXX": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_20(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "STATUS": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_21(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 402,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_22(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "XXheadersXX": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_23(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "HEADERS": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_24(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"XXcontent-typeXX", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_25(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"CONTENT-TYPE", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_26(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"XXapplication/jsonXX"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_27(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"APPLICATION/JSON"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_28(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"XXwww-authenticateXX", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_29(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"WWW-AUTHENTICATE", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_30(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"XXBearerXX"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_31(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_32(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"BEARER"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_33(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send(None)
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_34(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "XXtypeXX": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_35(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "TYPE": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_36(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "XXhttp.response.bodyXX",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_37(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "HTTP.RESPONSE.BODY",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_38(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "XXbodyXX": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_unauthorized__mutmut_39(self, send, error: Optional[str] = None):
        """Send 401 Unauthorized response."""
        import json
        
        body = json.dumps({
            "error": "Unauthorized",
            "detail": error or "Authentication required"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({
            "type": "http.response.body",
            "BODY": body,
        })
    
    xǁAuthMiddlewareǁ_send_unauthorized__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_1': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_1, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_2': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_2, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_3': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_3, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_4': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_4, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_5': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_5, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_6': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_6, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_7': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_7, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_8': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_8, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_9': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_9, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_10': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_10, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_11': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_11, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_12': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_12, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_13': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_13, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_14': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_14, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_15': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_15, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_16': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_16, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_17': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_17, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_18': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_18, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_19': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_19, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_20': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_20, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_21': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_21, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_22': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_22, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_23': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_23, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_24': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_24, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_25': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_25, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_26': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_26, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_27': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_27, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_28': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_28, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_29': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_29, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_30': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_30, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_31': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_31, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_32': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_32, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_33': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_33, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_34': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_34, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_35': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_35, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_36': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_36, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_37': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_37, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_38': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_38, 
        'xǁAuthMiddlewareǁ_send_unauthorized__mutmut_39': xǁAuthMiddlewareǁ_send_unauthorized__mutmut_39
    }
    
    def _send_unauthorized(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ_send_unauthorized__mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ_send_unauthorized__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _send_unauthorized.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ_send_unauthorized__mutmut_orig)
    xǁAuthMiddlewareǁ_send_unauthorized__mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ_send_unauthorized'
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_orig(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_1(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = None
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_2(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps(None).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_3(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "XXerrorXX": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_4(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "ERROR": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_5(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "XXToo Many RequestsXX",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_6(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "too many requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_7(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "TOO MANY REQUESTS",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_8(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "XXdetailXX": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_9(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "DETAIL": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_10(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "XXRate limit exceeded. Please try again later.XX"
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_11(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "rate limit exceeded. please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_12(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "RATE LIMIT EXCEEDED. PLEASE TRY AGAIN LATER."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_13(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send(None)
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_14(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "XXtypeXX": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_15(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "TYPE": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_16(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "XXhttp.response.startXX",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_17(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "HTTP.RESPONSE.START",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_18(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "XXstatusXX": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_19(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "STATUS": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_20(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 430,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_21(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "XXheadersXX": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_22(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "HEADERS": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_23(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"XXcontent-typeXX", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_24(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"CONTENT-TYPE", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_25(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"XXapplication/jsonXX"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_26(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"APPLICATION/JSON"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_27(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"XXretry-afterXX", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_28(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"RETRY-AFTER", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_29(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(None).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_30(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send(None)
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_31(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "XXtypeXX": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_32(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "TYPE": "http.response.body",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_33(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "XXhttp.response.bodyXX",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_34(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "HTTP.RESPONSE.BODY",
            "body": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_35(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "XXbodyXX": body,
        })
    
    async def xǁAuthMiddlewareǁ_send_rate_limited__mutmut_36(self, send):
        """Send 429 Too Many Requests response."""
        import json
        
        body = json.dumps({
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later."
        }).encode()
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(self.config.rate_limit_window).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "BODY": body,
        })
    
    xǁAuthMiddlewareǁ_send_rate_limited__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_1': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_1, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_2': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_2, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_3': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_3, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_4': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_4, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_5': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_5, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_6': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_6, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_7': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_7, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_8': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_8, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_9': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_9, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_10': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_10, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_11': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_11, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_12': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_12, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_13': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_13, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_14': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_14, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_15': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_15, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_16': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_16, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_17': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_17, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_18': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_18, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_19': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_19, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_20': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_20, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_21': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_21, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_22': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_22, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_23': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_23, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_24': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_24, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_25': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_25, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_26': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_26, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_27': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_27, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_28': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_28, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_29': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_29, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_30': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_30, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_31': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_31, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_32': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_32, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_33': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_33, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_34': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_34, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_35': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_35, 
        'xǁAuthMiddlewareǁ_send_rate_limited__mutmut_36': xǁAuthMiddlewareǁ_send_rate_limited__mutmut_36
    }
    
    def _send_rate_limited(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAuthMiddlewareǁ_send_rate_limited__mutmut_orig"), object.__getattribute__(self, "xǁAuthMiddlewareǁ_send_rate_limited__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _send_rate_limited.__signature__ = _mutmut_signature(xǁAuthMiddlewareǁ_send_rate_limited__mutmut_orig)
    xǁAuthMiddlewareǁ_send_rate_limited__mutmut_orig.__name__ = 'xǁAuthMiddlewareǁ_send_rate_limited'


def x_require_auth__mutmut_orig(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = set(methods or list(AuthMethod))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_1(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = None
    allowed_methods = set(methods or list(AuthMethod))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_2(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(None)
    allowed_methods = set(methods or list(AuthMethod))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_3(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes and [])
    allowed_methods = set(methods or list(AuthMethod))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_4(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = None
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_5(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = set(None)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_6(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = set(methods and list(AuthMethod))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def x_require_auth__mutmut_7(scopes: Optional[List[str]] = None, methods: Optional[List[AuthMethod]] = None):
    """
    Decorator to require authentication on endpoint.
    
    Args:
        scopes: Required scopes (any of these grants access)
        methods: Allowed authentication methods
    
    Usage:
        @require_auth(scopes=["read", "write"])
        async def protected_endpoint(request: Request):
            return {"user": request.state.user}
    """
    required_scopes = set(scopes or [])
    allowed_methods = set(methods or list(None))
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Get auth result from request scope
            auth_result = getattr(request.scope.get("auth"), None, None)
            
            if not auth_result or not auth_result.authenticated:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if auth_result.method not in allowed_methods:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authentication method")
            
            # Check scopes if required
            if required_scopes and not (required_scopes & auth_result.scopes):
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Add user info to request state
            request.state.user_id = auth_result.user_id
            request.state.scopes = auth_result.scopes
            request.state.auth_method = auth_result.method
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator

x_require_auth__mutmut_mutants : ClassVar[MutantDict] = {
'x_require_auth__mutmut_1': x_require_auth__mutmut_1, 
    'x_require_auth__mutmut_2': x_require_auth__mutmut_2, 
    'x_require_auth__mutmut_3': x_require_auth__mutmut_3, 
    'x_require_auth__mutmut_4': x_require_auth__mutmut_4, 
    'x_require_auth__mutmut_5': x_require_auth__mutmut_5, 
    'x_require_auth__mutmut_6': x_require_auth__mutmut_6, 
    'x_require_auth__mutmut_7': x_require_auth__mutmut_7
}

def require_auth(*args, **kwargs):
    result = _mutmut_trampoline(x_require_auth__mutmut_orig, x_require_auth__mutmut_mutants, args, kwargs)
    return result 

require_auth.__signature__ = _mutmut_signature(x_require_auth__mutmut_orig)
x_require_auth__mutmut_orig.__name__ = 'x_require_auth'


def x_get_current_user__mutmut_orig(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get("auth")
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def x_get_current_user__mutmut_1(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = None
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def x_get_current_user__mutmut_2(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get(None)
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def x_get_current_user__mutmut_3(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get("XXauthXX")
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def x_get_current_user__mutmut_4(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get("AUTH")
    if auth_result and auth_result.authenticated:
        return auth_result.user_id
    return None


def x_get_current_user__mutmut_5(request) -> Optional[str]:
    """
    Get current authenticated user from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        User ID if authenticated, None otherwise
    """
    auth_result = request.scope.get("auth")
    if auth_result or auth_result.authenticated:
        return auth_result.user_id
    return None

x_get_current_user__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_current_user__mutmut_1': x_get_current_user__mutmut_1, 
    'x_get_current_user__mutmut_2': x_get_current_user__mutmut_2, 
    'x_get_current_user__mutmut_3': x_get_current_user__mutmut_3, 
    'x_get_current_user__mutmut_4': x_get_current_user__mutmut_4, 
    'x_get_current_user__mutmut_5': x_get_current_user__mutmut_5
}

def get_current_user(*args, **kwargs):
    result = _mutmut_trampoline(x_get_current_user__mutmut_orig, x_get_current_user__mutmut_mutants, args, kwargs)
    return result 

get_current_user.__signature__ = _mutmut_signature(x_get_current_user__mutmut_orig)
x_get_current_user__mutmut_orig.__name__ = 'x_get_current_user'


def x_get_current_scopes__mutmut_orig(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = request.scope.get("auth")
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()


def x_get_current_scopes__mutmut_1(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = None
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()


def x_get_current_scopes__mutmut_2(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = request.scope.get(None)
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()


def x_get_current_scopes__mutmut_3(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = request.scope.get("XXauthXX")
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()


def x_get_current_scopes__mutmut_4(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = request.scope.get("AUTH")
    if auth_result and auth_result.authenticated:
        return auth_result.scopes
    return set()


def x_get_current_scopes__mutmut_5(request) -> Set[str]:
    """
    Get current user's scopes from request.
    
    Args:
        request: FastAPI/Starlette request object
    
    Returns:
        Set of scopes
    """
    auth_result = request.scope.get("auth")
    if auth_result or auth_result.authenticated:
        return auth_result.scopes
    return set()

x_get_current_scopes__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_current_scopes__mutmut_1': x_get_current_scopes__mutmut_1, 
    'x_get_current_scopes__mutmut_2': x_get_current_scopes__mutmut_2, 
    'x_get_current_scopes__mutmut_3': x_get_current_scopes__mutmut_3, 
    'x_get_current_scopes__mutmut_4': x_get_current_scopes__mutmut_4, 
    'x_get_current_scopes__mutmut_5': x_get_current_scopes__mutmut_5
}

def get_current_scopes(*args, **kwargs):
    result = _mutmut_trampoline(x_get_current_scopes__mutmut_orig, x_get_current_scopes__mutmut_mutants, args, kwargs)
    return result 

get_current_scopes.__signature__ = _mutmut_signature(x_get_current_scopes__mutmut_orig)
x_get_current_scopes__mutmut_orig.__name__ = 'x_get_current_scopes'
